-- Budget Engine: Unified Cost Tracking
-- Migration: 003_budget_engine.sql
-- Created: 2026-03-16
--
-- Adds provider registry, cost snapshots, fixed cost entries,
-- extends budget_events, and creates unified monthly view.

BEGIN;

-- ============================================================
-- cost_providers — registry of all cost sources
-- ============================================================
CREATE TABLE IF NOT EXISTS cost_providers (
    id              TEXT PRIMARY KEY,
    display_name    TEXT NOT NULL,
    provider_type   TEXT NOT NULL
                    CHECK (provider_type IN ('api_variable', 'api_subscription', 'fixed_subscription')),
    monthly_fixed   REAL DEFAULT 0,
    pricing_config  JSONB NOT NULL DEFAULT '{}',
    enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    last_polled_at  TIMESTAMPTZ
);

-- ============================================================
-- cost_snapshots — provider-reported totals for reconciliation
-- ============================================================
CREATE TABLE IF NOT EXISTS cost_snapshots (
    id              SERIAL PRIMARY KEY,
    provider        TEXT NOT NULL REFERENCES cost_providers(id),
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    reported_total  REAL NOT NULL,
    computed_total  REAL,
    delta           REAL,
    raw_response    JSONB,
    polled_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cost_snapshots_provider ON cost_snapshots (provider);
CREATE INDEX IF NOT EXISTS idx_cost_snapshots_polled   ON cost_snapshots (polled_at);

-- ============================================================
-- fixed_cost_entries — monthly recurring costs
-- ============================================================
CREATE TABLE IF NOT EXISTS fixed_cost_entries (
    id              SERIAL PRIMARY KEY,
    provider        TEXT NOT NULL REFERENCES cost_providers(id),
    month           DATE NOT NULL,
    amount_usd      REAL NOT NULL,
    description     TEXT,
    UNIQUE(provider, month)
);

CREATE INDEX IF NOT EXISTS idx_fixed_cost_month ON fixed_cost_entries (month);

-- ============================================================
-- Extend budget_events with provider, category, source columns
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'budget_events' AND column_name = 'provider'
    ) THEN
        ALTER TABLE budget_events ADD COLUMN provider TEXT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'budget_events' AND column_name = 'category'
    ) THEN
        ALTER TABLE budget_events ADD COLUMN category TEXT DEFAULT 'api_calls'
            CHECK (category IN ('api_calls', 'compute', 'data_services', 'subscriptions'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'budget_events' AND column_name = 'source'
    ) THEN
        ALTER TABLE budget_events ADD COLUMN source TEXT DEFAULT 'session'
            CHECK (source IN ('session', 'eval_run', 'provider_poll', 'manual'));
    END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_budget_events_provider ON budget_events (provider);
CREATE INDEX IF NOT EXISTS idx_budget_events_category ON budget_events (category);
CREATE INDEX IF NOT EXISTS idx_budget_events_source   ON budget_events (source);

-- ============================================================
-- v_monthly_total_cost — unified monthly totals
-- variable (budget_events) + fixed (fixed_cost_entries)
-- ============================================================
CREATE OR REPLACE VIEW v_monthly_total_cost AS
WITH variable AS (
    SELECT
        DATE_TRUNC('month', timestamp)::date AS month,
        COALESCE(SUM(cost_usd), 0)           AS variable_usd
    FROM budget_events
    GROUP BY DATE_TRUNC('month', timestamp)
),
fixed AS (
    SELECT
        month,
        COALESCE(SUM(amount_usd), 0) AS fixed_usd
    FROM fixed_cost_entries
    GROUP BY month
),
all_months AS (
    SELECT month FROM variable
    UNION
    SELECT month FROM fixed
)
SELECT
    am.month,
    COALESCE(v.variable_usd, 0)                        AS variable_usd,
    COALESCE(f.fixed_usd, 0)                            AS fixed_usd,
    COALESCE(v.variable_usd, 0) + COALESCE(f.fixed_usd, 0) AS total_usd
FROM all_months am
LEFT JOIN variable v ON v.month = am.month
LEFT JOIN fixed f    ON f.month = am.month
ORDER BY am.month DESC;

-- ============================================================
-- v_provider_monthly_spend — per-provider monthly breakdown
-- ============================================================
CREATE OR REPLACE VIEW v_provider_monthly_spend AS
WITH variable AS (
    SELECT
        DATE_TRUNC('month', timestamp)::date AS month,
        provider,
        SUM(cost_usd) AS cost_usd
    FROM budget_events
    WHERE provider IS NOT NULL
    GROUP BY DATE_TRUNC('month', timestamp), provider
),
fixed AS (
    SELECT
        month,
        provider,
        SUM(amount_usd) AS cost_usd
    FROM fixed_cost_entries
    GROUP BY month, provider
)
SELECT month, provider, SUM(cost_usd) AS cost_usd
FROM (
    SELECT * FROM variable
    UNION ALL
    SELECT * FROM fixed
) combined
GROUP BY month, provider
ORDER BY month DESC, cost_usd DESC;

-- ============================================================
-- Seed data: register all 6 providers
-- ============================================================
INSERT INTO cost_providers (id, display_name, provider_type, monthly_fixed, pricing_config) VALUES
    ('anthropic',       'Anthropic',        'api_variable',       0,      '{"api_endpoint": "/v1/organizations/{org}/usage"}'),
    ('openai',          'OpenAI',           'api_variable',       0,      '{"note": "No usage API — cost calculated from token counts"}'),
    ('openrouter',      'OpenRouter',       'api_variable',       0,      '{"api_endpoint": "/api/v1/auth/key"}'),
    ('firecrawl',       'Firecrawl',        'api_subscription',   50,     '{"api_endpoint": "/v2/team/credit-usage", "plan": "standard"}'),
    ('claude_code_max', 'Claude Code Max',  'fixed_subscription', 400,    '{"plan": "max_2", "accounts": 2, "per_account": 200}'),
    ('hetzner',         'Hetzner VPS',      'fixed_subscription', 5.50,   '{"instance": "CPX21", "region": "eu-central"}')
ON CONFLICT (id) DO UPDATE SET
    display_name   = EXCLUDED.display_name,
    provider_type  = EXCLUDED.provider_type,
    monthly_fixed  = EXCLUDED.monthly_fixed,
    pricing_config = EXCLUDED.pricing_config;

-- ============================================================
-- Backfill: March 2026 fixed costs
-- ============================================================
INSERT INTO fixed_cost_entries (provider, month, amount_usd, description) VALUES
    ('claude_code_max', '2026-03-01', 400,   '2x Claude Code Max ($200/account)'),
    ('hetzner',         '2026-03-01', 5.50,  'Hetzner CPX21 VPS'),
    ('firecrawl',       '2026-03-01', 50,    'Firecrawl standard plan')
ON CONFLICT (provider, month) DO NOTHING;

-- ============================================================
-- Backfill: tag existing budget_events with provider based on model
-- ============================================================
UPDATE budget_events SET provider = 'anthropic'
WHERE provider IS NULL AND model LIKE 'claude%';

UPDATE budget_events SET provider = 'openai'
WHERE provider IS NULL AND (model LIKE 'gpt%' OR model LIKE 'o1%' OR model LIKE 'o3%');

UPDATE budget_events SET provider = 'openrouter'
WHERE provider IS NULL AND (model LIKE 'deepseek%' OR model LIKE 'google%');

COMMIT;
