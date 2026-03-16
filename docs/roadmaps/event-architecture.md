# Event-Driven Architecture: From Polling to Reactive

**Status:** Proposed
**Author:** Oddur Sigurdsson
**Date:** 2026-03-16
**Estimated effort:** 14-19 hours

---

## Problem

The daemon (`orchestrator/src/daemon.ts`) runs as a polling loop: sleep for N minutes, wake up, check state, maybe launch sessions, sleep again. The default interval is 30 minutes (`pollIntervalMs: 30 * 60 * 1000`). This means:

- A critic that verdicts REVISE has to wait up to 30 minutes before the writer follow-up launches (follow-ups are queued in memory but only drained at the top of `cycle()`).
- Budget alerts are detected only when a cycle runs, not when overspend actually occurs.
- New features (knowledge graph updates, claim verification, literature monitoring) would inherit this same latency.
- External dispatches from OpenClaw agents sit in `externalQueue` until the next cycle drains them.

The platform needs to react to events in seconds, not minutes.

---

## Design

### Event Types

All meaningful state changes in the platform become typed domain events:

```typescript
type DomainEvent =
  | { type: 'session.completed'; projectName: string; agentType: string; quality: number; result: SessionResult }
  | { type: 'session.failed'; projectName: string; error: string }
  | { type: 'claim.added'; claimId: string; project: string; claimType: string }
  | { type: 'claim.contradicted'; claimId: string; contradictedBy: string }
  | { type: 'experiment.completed'; specId: string; result: ExperimentResult }
  | { type: 'literature.alert'; alertId: string; priority: string; project: string }
  | { type: 'paper.edited'; project: string; sections: string[] }
  | { type: 'verification.failed'; project: string; claimId: string; reason: string }
  | { type: 'critic.verdict'; project: string; verdict: string }
  | { type: 'budget.threshold'; level: string; spent: number; limit: number }
  | { type: 'forum.proposal'; postId: string; proposalType: string }
  | { type: 'governance.passed'; proposalId: string }
  | { type: 'prediction.resolved'; predictionId: string; outcome: boolean }
  | { type: 'planner.brief_ready'; briefId: string; project: string }
  | { type: 'heartbeat.due'; agentId: string }
```

### Event Handlers (Reactions)

Each event type maps to one or more handler functions. Handlers are idempotent and safe to replay.

| Event | Handlers |
|-------|----------|
| `session.completed` | `evaluate_quality`, `plan_next`, `update_knowledge_graph` |
| `session.failed` | `assess_retry`, `notify`, `update_failure_count` |
| `claim.added` | `verify_evidence`, `check_literature_match` |
| `claim.contradicted` | `notify_planner`, `post_to_forum` |
| `experiment.completed` | `analyze_results`, `update_beliefs`, `suggest_followup` |
| `literature.alert` | `assess_impact`, `notify_agents`, `update_knowledge_graph` |
| `paper.edited` | `run_verification`, `check_consistency` |
| `verification.failed` | `notify_writer`, `update_revision_priority` |
| `critic.verdict` | `chain_next_agent` (REVISE -> writer, ACCEPT -> editor) |
| `budget.threshold` | `replan`, `notify_human` |
| `forum.proposal` | `check_quorum`, `notify_voters` |
| `governance.passed` | `apply_decision` |
| `prediction.resolved` | `update_calibration` |
| `planner.brief_ready` | `launch_session` |
| `heartbeat.due` | `run_heartbeat_session` |

---

## Implementation: PostgreSQL LISTEN/NOTIFY

The platform already uses PostgreSQL (schema at `orchestrator/sql/001_initial_schema.sql`). PG's built-in pub/sub avoids adding Redis, RabbitMQ, or any new dependency. Events are persisted in a table (audit trail) and broadcast via `pg_notify` (real-time dispatch).

### SQL Migration

```sql
-- 002_domain_events.sql

BEGIN;

-- Persistent event log
CREATE TABLE domain_events (
    id          BIGSERIAL PRIMARY KEY,
    type        TEXT NOT NULL,
    payload     JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    processed   BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_domain_events_type ON domain_events (type);
CREATE INDEX idx_domain_events_created ON domain_events (created_at);
CREATE INDEX idx_domain_events_unprocessed ON domain_events (processed) WHERE NOT processed;

-- Trigger: notify on insert
CREATE OR REPLACE FUNCTION notify_event() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('deepwork_events', json_build_object(
        'id', NEW.id,
        'type', NEW.type,
        'payload', NEW.payload
    )::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER event_notify AFTER INSERT ON domain_events
    FOR EACH ROW EXECUTE FUNCTION notify_event();

-- Dead-letter table for failed handler executions
CREATE TABLE domain_events_dead_letter (
    id              BIGSERIAL PRIMARY KEY,
    event_id        BIGINT NOT NULL REFERENCES domain_events(id),
    handler_name    TEXT NOT NULL,
    error           TEXT NOT NULL,
    attempts        INTEGER DEFAULT 1,
    last_attempt_at TIMESTAMPTZ DEFAULT NOW(),
    resolved        BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_dead_letter_unresolved ON domain_events_dead_letter (resolved) WHERE NOT resolved;

COMMIT;
```

### New File: `orchestrator/src/event-bus.ts`

The EventBus class owns the connection between domain events and PostgreSQL.

```typescript
// Responsibilities:
// - emit(event): INSERT into domain_events (triggers pg_notify automatically)
// - on(type, handler): register a handler function for an event type
// - start(): LISTEN on 'deepwork_events' channel, dispatch incoming events to registered handlers
// - stop(): UNLISTEN, close dedicated PG connection
// - Retry failed handlers up to 3 times, then write to dead-letter table

import pg from "pg";

interface EventHandler {
  name: string;
  fn: (event: { id: number; type: string; payload: Record<string, unknown> }) => Promise<void>;
}

export class EventBus {
  private pool: pg.Pool;
  private listenClient: pg.PoolClient | null = null;
  private handlers: Map<string, EventHandler[]> = new Map();
  private running = false;

  constructor(pool: pg.Pool) {
    this.pool = pool;
  }

  on(type: string, name: string, fn: EventHandler["fn"]): void {
    const list = this.handlers.get(type) ?? [];
    list.push({ name, fn });
    this.handlers.set(type, list);
  }

  async emit(type: string, payload: Record<string, unknown>): Promise<number> {
    const result = await this.pool.query(
      "INSERT INTO domain_events (type, payload) VALUES ($1, $2) RETURNING id",
      [type, JSON.stringify(payload)]
    );
    return result.rows[0].id;
  }

  async start(): Promise<void> {
    this.listenClient = await this.pool.connect();
    await this.listenClient.query("LISTEN deepwork_events");
    this.running = true;

    this.listenClient.on("notification", async (msg) => {
      if (!msg.payload) return;
      const event = JSON.parse(msg.payload);
      await this.dispatch(event);
    });
  }

  async stop(): Promise<void> {
    this.running = false;
    if (this.listenClient) {
      await this.listenClient.query("UNLISTEN deepwork_events");
      this.listenClient.release();
      this.listenClient = null;
    }
  }

  private async dispatch(event: { id: number; type: string; payload: Record<string, unknown> }): Promise<void> {
    const handlers = this.handlers.get(event.type) ?? [];
    for (const handler of handlers) {
      let attempts = 0;
      const maxAttempts = 3;
      while (attempts < maxAttempts) {
        try {
          await handler.fn(event);
          break;
        } catch (err) {
          attempts++;
          if (attempts >= maxAttempts) {
            // Dead-letter
            await this.pool.query(
              "INSERT INTO domain_events_dead_letter (event_id, handler_name, error, attempts) VALUES ($1, $2, $3, $4)",
              [event.id, handler.name, err instanceof Error ? err.message : String(err), attempts]
            );
          }
        }
      }
    }
    // Mark processed
    await this.pool.query("UPDATE domain_events SET processed = TRUE WHERE id = $1", [event.id]);
  }
}
```

### New File: `orchestrator/src/event-handlers.ts`

All handler registrations live here. Each handler is a pure function that receives the event and performs a side effect. Handlers are grouped by domain.

```typescript
// Structure:
export function registerAllHandlers(bus: EventBus, daemon: Daemon): void {
  // Session lifecycle
  bus.on("session.completed", "evaluate_quality", async (e) => { ... });
  bus.on("session.completed", "plan_next", async (e) => { ... });
  bus.on("session.failed", "assess_retry", async (e) => { ... });
  bus.on("session.failed", "notify_failure", async (e) => { ... });

  // Critic chaining (replaces processSessionSignals in daemon.ts)
  bus.on("critic.verdict", "chain_next_agent", async (e) => { ... });

  // Budget
  bus.on("budget.threshold", "replan_sessions", async (e) => { ... });
  bus.on("budget.threshold", "notify_human", async (e) => { ... });

  // Knowledge graph (future)
  bus.on("claim.added", "verify_evidence", async (e) => { ... });
  bus.on("claim.contradicted", "notify_planner", async (e) => { ... });

  // Literature monitoring (future)
  bus.on("literature.alert", "assess_impact", async (e) => { ... });

  // Governance (future)
  bus.on("forum.proposal", "check_quorum", async (e) => { ... });
  bus.on("governance.passed", "apply_decision", async (e) => { ... });

  // Planning
  bus.on("planner.brief_ready", "launch_session", async (e) => { ... });
  bus.on("heartbeat.due", "run_heartbeat", async (e) => { ... });
}
```

---

## Migration Strategy: Hybrid Approach

The daemon does not need to be rewritten all at once. The polling loop and event bus coexist.

### Phase 1: Foundation (hours 1-5)

1. Run SQL migration to create `domain_events` table and trigger.
2. Implement `EventBus` class with `emit`, `on`, `start`, `stop`.
3. Wire EventBus into `Daemon` constructor (alongside existing `dbPool`).
4. Start EventBus in `Daemon.start()`, stop in `Daemon.shutdown()`.

At this point: events can be emitted and handled, but nothing emits them yet. The polling loop continues unchanged.

### Phase 2: Emit Events From Existing Code (hours 5-9)

Add `eventBus.emit(...)` calls at key points in existing code without changing any logic:

- `daemon.ts` `runSession()` after session completes -> emit `session.completed`
- `daemon.ts` `runSession()` on failure -> emit `session.failed`
- `daemon.ts` `processSessionSignals()` when critic verdict detected -> emit `critic.verdict`
- `budget-tracker.ts` when threshold crossed -> emit `budget.threshold`

At this point: events are being logged (audit trail) and broadcast, but the daemon still uses its existing logic to react. Handlers can optionally be registered for logging/monitoring.

### Phase 3: Migrate Reactions to Event Handlers (hours 9-13)

Replace inline reaction logic with event handlers:

1. **Session chaining** (`processSessionSignals` in `daemon.ts`): Move the REVISE->writer and ACCEPT->editor logic into a `critic.verdict` handler. Remove from `processSessionSignals`.

2. **Budget alerts**: Move the budget-exceeded notification from `cycle()` into a `budget.threshold` handler. The `BudgetTracker` emits the event when it detects a threshold crossing, and the handler sends the Slack notification.

3. **Follow-up queue**: External dispatches and follow-ups become event-driven. Instead of `followUpQueue.push(...)`, emit `planner.brief_ready`. A handler calls `daemon.queueSession(...)`.

### Phase 4: New Features Use Events From Day 1 (hours 13-17)

- Knowledge graph updates on `claim.added` and `experiment.completed`
- Claim verification pipeline on `claim.added`
- Literature alert processing on `literature.alert`
- Forum proposal workflow on `forum.proposal` and `governance.passed`

### Phase 5: Reduce Polling to Fallback (hour 17+)

Once all reactions are event-driven:
- Increase poll interval to 30 minutes (from current 30 min, so no change initially)
- The polling cycle becomes a consistency check: scan for any events that were missed (e.g., PG connection dropped)
- Eventually the poll interval can stretch to 60 minutes or longer -- it is just a safety net

---

## API and Dashboard Integration

### New API Endpoint

```
GET /api/events/recent?limit=50&type=session.completed
```

Returns the last N events from `domain_events`, optionally filtered by type. Simple SELECT query.

### WebSocket Broadcast

The existing API (`orchestrator/src/api.ts`) already has WebSocket support. Add a new message type:

```typescript
// In event-bus.ts, after dispatching handlers:
wss.clients.forEach(client => {
  client.send(JSON.stringify({ type: "event", data: event }));
});
```

The dashboard gets real-time event stream without polling.

### Event Log Dashboard Page

A new page on the Astro site showing:
- Live event feed (via WebSocket)
- Event type filter
- Dead-letter queue status
- Handler execution times

---

## Task Breakdown

| # | Task | Estimate | Dependencies |
|---|------|----------|--------------|
| 1 | SQL migration: `domain_events` table + trigger + dead-letter table | 1 hour | None |
| 2 | `EventBus` class: emit, on, start, stop, retry, dead-letter | 3-4 hours | #1 |
| 3 | Event handler registry (`event-handlers.ts`) with initial handlers | 2-3 hours | #2 |
| 4 | Wire EventBus into Daemon constructor and lifecycle | 1 hour | #2 |
| 5 | Emit events from existing code (session lifecycle, budget) | 2 hours | #4 |
| 6 | Migrate session chaining (`processSessionSignals`) to event handlers | 2 hours | #3, #5 |
| 7 | Migrate budget alerts to event handlers | 1 hour | #3, #5 |
| 8 | API endpoint: `GET /api/events/recent` | 1 hour | #1 |
| 9 | WebSocket broadcast of events to dashboard | 1 hour | #2, #8 |
| 10 | Dead-letter queue monitoring + retry API | 1-2 hours | #2 |
| **Total** | | **14-19 hours** | |

---

## Files Changed

| File | Change |
|------|--------|
| `orchestrator/sql/002_domain_events.sql` | New migration |
| `orchestrator/src/event-bus.ts` | New: EventBus class |
| `orchestrator/src/event-handlers.ts` | New: handler registrations |
| `orchestrator/src/daemon.ts` | Add EventBus as member, emit events, eventually remove inline reactions |
| `orchestrator/src/budget-tracker.ts` | Emit `budget.threshold` events |
| `orchestrator/src/session-manager.ts` | Emit `session.completed` / `session.failed` events |
| `orchestrator/src/api.ts` | Add `/api/events/recent` endpoint, WebSocket event broadcast |
| `orchestrator/src/routes/` | New route file for events API |

---

## Success Criteria

1. **Latency**: The system reacts to events within 5 seconds of occurrence, not at the next 30-minute poll cycle.
2. **Idempotency**: All event handlers are safe to replay. Running the same event through a handler twice produces the same result.
3. **Audit trail**: Every domain event is persisted in `domain_events` with timestamp, type, and full payload. The event log provides a complete history of platform activity.
4. **Observability**: The dashboard shows a real-time event stream via WebSocket. Dead-letter entries are visible and can be retried.
5. **Zero regression**: The polling loop continues to function as a fallback. Existing session chaining, budget alerts, and dispatch queue work identically during the migration.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| PG LISTEN connection drops silently | Heartbeat ping every 30s on the listen connection; reconnect on failure. Polling loop catches anything missed. |
| Handler throws and blocks other handlers for same event | Each handler runs independently with its own try/catch and retry loop. One handler's failure does not affect others. |
| Event storms (e.g., bulk experiment completion) | Rate-limit handler execution per event type. Batch-process where possible. |
| Migration breaks existing session chaining | Hybrid approach: old logic remains active during Phase 2. Only removed in Phase 3 after event handlers are proven. |
| `domain_events` table grows indefinitely | Partition by month. Archive/delete events older than 90 days. Add `PARTITION BY RANGE (created_at)` in the migration. |
