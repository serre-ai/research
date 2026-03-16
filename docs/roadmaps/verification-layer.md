# Verification Layer — Claims-to-Evidence Traceability

**Status:** Planned
**Priority:** High — directly impacts paper quality and submission confidence
**Estimated effort:** 12-16 hours
**Dependencies:** Eval results in PostgreSQL (complete), LaTeX paper source, analysis pipeline

## Motivation

Every factual claim in the paper must be traceable to supporting evidence. Currently, claims are written by the writer agent and reviewed by the critic, but there is no automated system to verify that:

- Numerical claims match the underlying data
- Figures and tables are internally consistent
- The abstract matches the body
- Claims are not stale after data changes

A single wrong number in a NeurIPS submission is a desk reject. This system catches those errors before they reach a reviewer.

## Architecture

The verification layer sits between the paper source and the eval data, operating as a post-processing step after every writer or editor session.

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  LaTeX       │────>│  ClaimVerifier   │<────│  eval_results   │
│  paper/*.tex │     │                  │     │  (PostgreSQL)   │
└─────────────┘     │  1. Extract      │     └─────────────────┘
                    │  2. Link         │     ┌─────────────────┐
                    │  3. Verify       │<────│  figures/tables  │
                    │  4. Report       │     │  (analysis/)    │
                    └────────┬─────────┘     └─────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Verification    │
                    │  Report (JSON)   │
                    └──────────────────┘
```

### Data flow

1. **Extract**: Parse LaTeX source, identify sentences containing numerical claims, statistical results, or quantitative comparisons
2. **Link**: For each claim, search eval_results, analysis outputs, figures, and tables for supporting evidence
3. **Verify**: Compare extracted claim values against evidence values; flag mismatches, staleness, or missing evidence
4. **Report**: Produce a structured report consumed by the critic agent, the API, and the dashboard

## Schema Additions

New migration file: `orchestrator/sql/005_verification.sql`

```sql
BEGIN;

-- ============================================================
-- Paper Claims — extracted factual assertions from LaTeX
-- ============================================================
CREATE TABLE paper_claims (
    id              SERIAL PRIMARY KEY,
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    paper_section   TEXT NOT NULL,           -- e.g. 'abstract', 'section_3.2', 'table_2_caption'
    claim_text      TEXT NOT NULL,           -- raw sentence containing the claim
    claim_type      TEXT NOT NULL
                    CHECK (claim_type IN (
                        'accuracy',          -- "Model X achieves 87% on task Y"
                        'comparison',        -- "CoT improves by 34% over direct"
                        'count',             -- "We evaluate 9 models across 9 tasks"
                        'statistical',       -- "p < 0.001, effect size d = 0.72"
                        'qualitative',       -- "Depth-bounded tasks show the largest CoT benefit"
                        'citation'           -- "Smith et al. (2025) found..."
                    )),
    extracted_values JSONB NOT NULL DEFAULT '{}',
        -- Structured representation of the claim's quantitative content:
        -- { "metric": "cot_lift", "value": 0.271, "models": ["all"],
        --   "tasks": ["B2", "B3"], "conditions": ["short_cot", "direct"],
        --   "comparison_type": "difference" }
    source_file     TEXT NOT NULL,           -- LaTeX file path relative to project root
    source_line     INTEGER,                 -- line number in source file
    hash            TEXT NOT NULL,           -- SHA-256 of claim_text for change detection
    status          TEXT NOT NULL DEFAULT 'unverified'
                    CHECK (status IN ('verified', 'stale', 'unverified', 'contradicted', 'no_evidence')),
    last_verified   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_paper_claims_project   ON paper_claims (project);
CREATE INDEX idx_paper_claims_section   ON paper_claims (project, paper_section);
CREATE INDEX idx_paper_claims_status    ON paper_claims (status);
CREATE INDEX idx_paper_claims_type      ON paper_claims (claim_type);
CREATE INDEX idx_paper_claims_hash      ON paper_claims (hash);


-- ============================================================
-- Claim Evidence — links between claims and their support
-- ============================================================
CREATE TABLE claim_evidence (
    id              SERIAL PRIMARY KEY,
    claim_id        INTEGER NOT NULL REFERENCES paper_claims(id) ON DELETE CASCADE,
    evidence_type   TEXT NOT NULL
                    CHECK (evidence_type IN (
                        'data_query',        -- SQL query against eval_results
                        'statistical_test',  -- reference to a specific test result
                        'figure',            -- figure file path
                        'table',             -- LaTeX table reference
                        'proof',             -- formal proof section
                        'citation',          -- bibliography entry
                        'computed'           -- value derived from analysis pipeline
                    )),
    evidence_ref    TEXT NOT NULL,           -- query string, file path, or BibTeX key
    evidence_value  JSONB DEFAULT '{}',     -- the actual value from evidence
        -- { "computed_value": 0.268, "ci_lower": 0.241, "ci_upper": 0.295,
        --   "n": 121614, "query_timestamp": "2026-03-14T..." }
    match_status    TEXT NOT NULL DEFAULT 'pending'
                    CHECK (match_status IN (
                        'exact_match',       -- claim value matches evidence exactly
                        'within_ci',         -- claim value falls within confidence interval
                        'rounded_match',     -- claim matches after rounding
                        'mismatch',          -- claim does not match evidence
                        'pending'            -- not yet checked
                    )),
    deviation       REAL,                   -- absolute difference between claim and evidence
    verified_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_claim_evidence_claim    ON claim_evidence (claim_id);
CREATE INDEX idx_claim_evidence_type     ON claim_evidence (evidence_type);
CREATE INDEX idx_claim_evidence_status   ON claim_evidence (match_status);


-- ============================================================
-- Verification Runs — audit trail of verification executions
-- ============================================================
CREATE TABLE verification_runs (
    id              SERIAL PRIMARY KEY,
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    trigger         TEXT NOT NULL
                    CHECK (trigger IN ('auto', 'manual', 'pre_submit')),
    claims_total    INTEGER NOT NULL DEFAULT 0,
    claims_verified INTEGER NOT NULL DEFAULT 0,
    claims_stale    INTEGER NOT NULL DEFAULT 0,
    claims_missing  INTEGER NOT NULL DEFAULT 0,
    claims_contradicted INTEGER NOT NULL DEFAULT 0,
    inconsistencies JSONB NOT NULL DEFAULT '[]',
        -- [{ "type": "figure_table_mismatch", "description": "...",
        --    "locations": ["figure_3", "table_2"], "severity": "high" }]
    report_path     TEXT,                   -- path to full JSON report
    duration_ms     REAL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_verification_runs_project ON verification_runs (project);
CREATE INDEX idx_verification_runs_created ON verification_runs (created_at);


-- ============================================================
-- Convenience view: current verification status per project
-- ============================================================
CREATE VIEW v_verification_status AS
SELECT
    pc.project,
    COUNT(*) AS total_claims,
    COUNT(*) FILTER (WHERE pc.status = 'verified') AS verified,
    COUNT(*) FILTER (WHERE pc.status = 'stale') AS stale,
    COUNT(*) FILTER (WHERE pc.status = 'contradicted') AS contradicted,
    COUNT(*) FILTER (WHERE pc.status = 'no_evidence') AS no_evidence,
    COUNT(*) FILTER (WHERE pc.status = 'unverified') AS unverified,
    ROUND(
        (COUNT(*) FILTER (WHERE pc.status = 'verified'))::numeric /
        NULLIF(COUNT(*), 0), 3
    ) AS verified_ratio,
    MAX(vr.created_at) AS last_run
FROM paper_claims pc
LEFT JOIN verification_runs vr ON vr.project = pc.project
GROUP BY pc.project;

COMMIT;
```

## New Files

### `orchestrator/src/verification.ts` — ClaimVerifier class

Core module containing all verification logic. Follows existing patterns in the codebase (ESM, async/await, pg pool).

```typescript
import { readFile, readdir, stat } from "node:fs/promises";
import { join, relative } from "node:path";
import { createHash } from "node:crypto";
import type pg from "pg";

// ============================================================
// Types
// ============================================================

export interface ExtractedClaim {
  section: string;
  text: string;
  type: "accuracy" | "comparison" | "count" | "statistical" | "qualitative" | "citation";
  values: Record<string, unknown>;
  sourceFile: string;
  sourceLine: number;
  hash: string;
}

export interface EvidenceLink {
  claimId: number;
  evidenceType: "data_query" | "statistical_test" | "figure" | "table" | "proof" | "citation" | "computed";
  evidenceRef: string;
  evidenceValue: Record<string, unknown>;
  matchStatus: "exact_match" | "within_ci" | "rounded_match" | "mismatch" | "pending";
  deviation: number | null;
}

export interface VerificationReport {
  project: string;
  timestamp: string;
  claimsTotal: number;
  claimsVerified: number;
  claimsStale: number;
  claimsMissing: number;
  claimsContradicted: number;
  inconsistencies: Inconsistency[];
  claims: ClaimReport[];
}

export interface Inconsistency {
  type: "figure_table_mismatch" | "abstract_body_mismatch" | "count_mismatch" | "stale_reference";
  description: string;
  locations: string[];
  severity: "high" | "medium" | "low";
}

export interface ClaimReport {
  claim: ExtractedClaim;
  evidence: EvidenceLink[];
  status: string;
}

// ============================================================
// ClaimVerifier
// ============================================================

export class ClaimVerifier {
  constructor(
    private pool: pg.Pool,
    private rootDir: string
  ) {}

  /**
   * Extract all factual claims from a LaTeX paper.
   *
   * Strategy: Two-pass approach.
   *   Pass 1 (regex): Identify candidate sentences containing numbers,
   *     percentages, comparisons, model names, or statistical notation.
   *   Pass 2 (LLM): Send candidates to Claude for structured extraction,
   *     producing typed claims with extracted values.
   *
   * Returns structured claims ready for evidence linking.
   */
  async extractClaims(latexDir: string): Promise<ExtractedClaim[]> { /* ... */ }

  /**
   * Find supporting evidence for a single claim.
   *
   * Searches multiple evidence sources depending on claim type:
   *   - accuracy/comparison → SQL queries against eval_results, checkpoints
   *   - count → SQL COUNT queries, file system checks
   *   - statistical → analysis pipeline output files (CI tables, test results)
   *   - qualitative → aggregate queries confirming directional claims
   *   - citation → BibTeX file lookup
   */
  async linkEvidence(claim: ExtractedClaim, project: string): Promise<EvidenceLink[]> { /* ... */ }

  /**
   * Run full verification pipeline for a project.
   *
   * 1. Extract all claims from paper LaTeX
   * 2. Link each claim to evidence
   * 3. Verify each evidence link (compute match status, deviation)
   * 4. Run cross-reference consistency checks
   * 5. Persist results to paper_claims, claim_evidence tables
   * 6. Write verification report to disk
   * 7. Return structured report
   */
  async verifyAll(project: string): Promise<VerificationReport> { /* ... */ }

  /**
   * Cross-reference all numbers across the paper.
   *
   * Checks:
   *   - Abstract numbers match body text numbers
   *   - Table values match figure values for same data
   *   - Model count in "we evaluate N models" matches actual model list
   *   - Task count matches actual task list
   *   - Numbers in discussion/conclusion match results section
   */
  async checkConsistency(project: string): Promise<Inconsistency[]> { /* ... */ }
}
```

**Key implementation details:**

1. **Regex pre-filter**: Scan LaTeX for lines containing `\d+\.?\d*%`, `\d+\.\d{2,}`, `p\s*[<>=]`, `n\s*=`, model name patterns (e.g., `claude`, `gpt`, `gemini`). This reduces LLM calls by filtering out non-claim sentences.

2. **LLM claim extraction**: Send filtered sentences with surrounding context (section header, nearby table/figure references) to Claude Haiku for fast, cheap structured extraction. Expected cost: ~$0.02 per paper pass.

3. **Evidence queries**: Generate SQL queries dynamically based on claim type. For example, a claim "CoT improves accuracy by 27.1% on depth-bounded tasks" generates:
   ```sql
   SELECT
     AVG(CASE WHEN condition = 'short_cot' THEN correct::int END) -
     AVG(CASE WHEN condition = 'direct' THEN correct::int END) AS cot_lift
   FROM eval_results
   WHERE task IN ('B2_parity_chain', 'B3_dependency_resolution')
   ```

4. **Staleness detection**: Compare `paper_claims.hash` against current LaTeX content. If the claim text changed, mark as `stale` and re-verify. If the underlying data changed (new eval runs), mark all claims referencing that data as `stale`.

5. **Tolerance matching**: Use configurable tolerance for numerical comparisons. Default: exact match for integers, 0.001 absolute tolerance for decimals, 0.5% relative tolerance for percentages. Claims matching within the confidence interval of the evidence get `within_ci` status.

### `orchestrator/src/routes/verification.ts` — API routes

```typescript
import { Router, type Request, type Response } from "express";
import type pg from "pg";
import { ClaimVerifier } from "../verification.js";

export function verificationRoutes(pool: pg.Pool, rootDir: string): Router {
  const router = Router();
  const verifier = new ClaimVerifier(pool, rootDir);

  // GET /api/projects/:id/verification
  // Returns the latest verification report for a project.
  // Query params: ?refresh=true to trigger a new verification run.
  router.get("/projects/:id/verification", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/projects/:id/claims
  // List all claims for a project with their current status.
  // Query params: ?status=stale&type=accuracy&section=abstract
  router.get("/projects/:id/claims", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/projects/:id/claims/:claimId/evidence
  // Get all evidence links for a specific claim.
  router.get("/projects/:id/claims/:claimId/evidence", async (req: Request, res: Response) => {
    /* ... */
  });

  // POST /api/projects/:id/verify
  // Trigger a new verification run. Body: { trigger: "manual" | "pre_submit" }
  router.post("/projects/:id/verify", async (req: Request, res: Response) => {
    /* ... */
  });

  return router;
}
```

### OpenClaw skill: `verify`

Add to the agent skill set so any agent (especially critic and editor) can invoke verification.

**Skill definition** (in `.claude/agents/` persona files):

```
/verify <project> [--section <section>] [--claim-type <type>]
  Run verification checks on the paper. Returns a summary of claim statuses,
  flagging any stale, missing, or contradicted claims. Use before finalizing
  any section that contains numerical results.
```

**Implementation**: The skill calls `POST /api/projects/:id/verify` and formats the response for agent consumption, highlighting actionable items (contradictions, missing evidence, stale claims).

## Integration with Existing Systems

### Session runner hook

In `orchestrator/src/session-runner.ts`, add a post-session hook:

```typescript
// After writer or editor session completes successfully:
if (["writer", "editor"].includes(config.agentType)) {
  const verifier = new ClaimVerifier(pool, rootDir);
  const report = await verifier.verifyAll(config.projectName);

  if (report.claimsContradicted > 0 || report.inconsistencies.length > 0) {
    // Log to activity feed
    await logger.log("verification_alert", {
      project: config.projectName,
      contradictions: report.claimsContradicted,
      inconsistencies: report.inconsistencies.length,
    });
    // Notify via Slack if configured
    await notifier.send(`Verification alert: ${report.claimsContradicted} contradictions found`);
  }
}
```

### Critic agent integration

The critic agent (`.claude/agents/critic.md`) should read the verification report as part of its review:

```
Before reviewing any section, check /verify output. Prioritize:
1. Contradicted claims (status: contradicted) — these are errors
2. Missing evidence (status: no_evidence) — these need data or should be removed
3. Stale claims (status: stale) — these need re-verification
4. Inconsistencies — cross-reference mismatches between sections
```

### Knowledge graph updates

Verification results feed into claim confidence scores. A claim that has been verified against multiple evidence sources with exact matches gets higher confidence than one with a single `within_ci` match. This confidence propagates to the section and paper level, giving the strategist agent a quality signal.

### Dashboard display

The Astro dashboard at `site/` should show:
- Verification status badge per project (green/yellow/red)
- Claim count breakdown by status
- List of actionable issues sorted by severity
- History of verification runs with trend

## Task Breakdown

| # | Task | Est. hours | Dependencies |
|---|------|-----------|--------------|
| 1 | Schema migration (`005_verification.sql`) | 0.5 | None |
| 2 | Claim extraction — regex pre-filter | 1.5 | None |
| 3 | Claim extraction — LLM structured extraction | 2.0 | Task 2 |
| 4 | Evidence linking — SQL query generation | 2.0 | Task 1 |
| 5 | Evidence linking — figure/table matching | 1.5 | Task 4 |
| 6 | Consistency checker — cross-reference all numbers | 2.5 | Tasks 3, 5 |
| 7 | Verification report format and persistence | 1.0 | Task 6 |
| 8 | API routes (`routes/verification.ts`) | 1.5 | Task 7 |
| 9 | OpenClaw `verify` skill | 1.0 | Task 8 |
| 10 | Session runner post-hook integration | 1.0 | Task 7 |
| 11 | Critic agent prompt updates | 0.5 | Task 9 |
| **Total** | | **~15 hours** | |

### Suggested implementation order

**Phase 1 — Core extraction and linking (Tasks 1-5, ~7.5 hours)**
Get claims out of LaTeX and connect them to data. This alone catches most numerical errors.

**Phase 2 — Consistency and reporting (Tasks 6-8, ~5 hours)**
Cross-reference checks and API exposure. Enables dashboard integration.

**Phase 3 — Agent integration (Tasks 9-11, ~2.5 hours)**
Wire into the agent workflow so verification runs automatically and agents can invoke it.

## Success Criteria

1. **Every numerical claim has a traceable evidence link.** Target: 100% of accuracy, comparison, count, and statistical claims linked to at least one evidence source.

2. **Stale claims are flagged automatically.** When eval data changes (new model runs, corrected results), all claims referencing that data are marked stale within the next verification run.

3. **Inconsistencies between sections are caught before submission.** Specifically:
   - Abstract says "N models" but body lists a different count: caught
   - Figure 3 shows accuracy X but Table 2 shows accuracy Y for the same cell: caught
   - Discussion claims "largest effect" but a different task actually has the largest effect: caught

4. **Verification cost is negligible.** Target: under $0.10 per full verification run (Haiku for extraction, SQL for evidence, no Opus calls needed).

5. **Latency is acceptable.** Full verification completes in under 60 seconds for a 20-page paper with ~50 claims.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM extraction misses claims | Unverified numbers in paper | Regex pre-filter catches all numbers; LLM only structures them. Manual review of extraction quality on first run. |
| Evidence linking produces false matches | Claims marked "verified" when evidence is unrelated | Require explicit model/task/condition match in evidence queries; human spot-check on first run. |
| Verification becomes stale itself | False confidence in old verification runs | Auto-run after every writer/editor session; staleness window of 1 hour. |
| Over-reliance on verification | Agents stop thinking critically about numbers | Verification is a safety net, not a replacement for the critic's judgment. Critic agent prompt emphasizes this. |

## Open Questions

1. **Should verification block paper edits?** Current design: no, verification is advisory. Future option: require all claims to be verified before merging to paper branch.

2. **How to handle qualitative claims?** Claims like "depth-bounded tasks show the largest benefit" require directional verification (is the claim about the right ranking?). Current plan: LLM evaluates whether the data supports the directional claim.

3. **Citation verification scope?** Should the system verify that cited papers actually support the claims made about them? This requires reading the cited papers (expensive). Current plan: out of scope for v1, flag for human review.
