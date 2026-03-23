#!/usr/bin/env python3
"""Create Linear issues for the infrastructure audit findings."""

from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Optional

API_KEY = os.environ["LINEAR_API_KEY"]
TEAM_ID = "77e7bcae-30d7-4257-b043-6f0b004abc65"
PROJECT_ID = "a10d081e-bfbd-4c54-abd3-39b956d3c657"  # platform-infra
TODO_STATE = "834253df-cd32-4f85-bae7-55054f473c4b"
BACKLOG_STATE = "311c91d4-9830-4b87-8132-f26e6bb1f8ad"

# Labels
SECURITY = "5c237501-f541-4e21-94b8-e0bf8934e982"
INFRA = "23c3bd19-9ea8-4847-93ae-393820a056a6"
DAEMON = "a7557f2e-2373-469d-955e-1749165273fb"
TECH_DEBT = "e6379707-90c1-42a4-a653-bae8520abaab"
BUG = "1f417acd-5f38-49dc-ba5f-f417338e3b87"
EXPERIMENT = "2478e058-1cac-44f1-b0f3-559f4237bbc9"
IMPROVEMENT = "ad444d04-d5a5-4bd4-ab81-5b35b2705b21"

# Priority: 0=none, 1=urgent, 2=high, 3=medium, 4=low


def query(gql: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": gql, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": API_KEY,
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data["data"]


def create_issue(
    title: str,
    description: str,
    priority: int,
    labels: list[str],
    state_id: str = TODO_STATE,
    parent_id: str | None = None,
) -> dict:
    mutation = """
    mutation CreateIssue($input: IssueCreateInput!) {
        issueCreate(input: $input) {
            success
            issue { id identifier title url }
        }
    }
    """
    input_data = {
        "teamId": TEAM_ID,
        "projectId": PROJECT_ID,
        "title": title,
        "description": description,
        "priority": priority,
        "labelIds": labels,
        "stateId": state_id,
    }
    if parent_id:
        input_data["parentId"] = parent_id

    result = query(mutation, {"input": input_data})
    issue = result["issueCreate"]["issue"]
    print(f"  ✓ {issue['identifier']}: {issue['title']}")
    print(f"    {issue['url']}")
    time.sleep(0.2)  # rate limit
    return issue


# ─── Parent Issue ───────────────────────────────────────────────────────

PARENT_DESC = """\
## Infrastructure Audit: Pipeline & Orchestration Code Review

Comprehensive code review of the orchestrator, experiment pipelines, and deployment infrastructure. Identified **25+ issues** across three severity tiers, grouped into 10 actionable work items below.

### Audit Scope
- **Orchestrator** — daemon engine, session runner, budget tracker, event bus, API layer, knowledge graph
- **Experiment pipelines** — reasoning-gaps eval suite, verification-complexity scripts, analysis pipeline
- **Deployment** — systemd services, CI/CD workflow, nginx config, startup validation

### Summary by Severity
| Severity | Count | Theme |
|----------|-------|-------|
| 🔴 Critical | 6 | Credential exposure, crash resilience, data loss, budget race |
| 🟠 High | 9 | Missing retries, swallowed errors, race conditions, weak health checks |
| 🟡 Medium | 10 | Security hardening, deployment fragility, reproducibility |

### Root Cause of Pipeline Failures
The most likely causes of failed experiment runs:
1. **No retry logic on API calls** — a single 429 or 500 kills the entire run
2. **Non-atomic writes** — crash during JSONL append corrupts output files
3. **Checkpoint race conditions** — multi-process writes interleave
4. **No cost cap enforcement** — runs exceed budget silently

All sub-issues are filed under `platform-infra` with appropriate labels and priorities.
"""

print("Creating parent issue...")
parent = create_issue(
    title="Infrastructure audit: pipeline & orchestration code review",
    description=PARENT_DESC,
    priority=1,
    labels=[INFRA],
)
parent_id = parent["id"]
print()

# ─── Sub-issues ─────────────────────────────────────────────────────────

issues = [
    # 1. CRITICAL — Credential Exposure
    {
        "title": "Rotate exposed credentials and move to env vars",
        "priority": 1,
        "labels": [SECURITY],
        "state": TODO_STATE,
        "description": """\
## Problem
Production credentials are hardcoded in source files:

- **Linear API key** in `scripts/expand-linear-roadmap.py:15` and `scripts/setup-linear.py:14`
- **PostgreSQL password** in `projects/reasoning-gaps/benchmarks/ingest_results.py:30-31` and `export_results.py:30-32`

These are committed to the repo working directory. Anyone with access can authenticate.

## Action Items
- [ ] Move all hardcoded credentials to environment variables
- [ ] Update scripts to read from `os.environ` with clear error on missing key
- [ ] Rotate the Linear API key (current one is exposed)
- [ ] Rotate the DB password on VPS
- [ ] Audit for any other hardcoded secrets (`grep -r "lin_api_\\|password\\|sk-ant-" --include="*.py" --include="*.ts"`)
""",
    },
    # 2. CRITICAL — Daemon Crash Resilience
    {
        "title": "Add graceful shutdown and crash resilience to daemon",
        "priority": 1,
        "labels": [DAEMON, BUG],
        "state": TODO_STATE,
        "description": """\
## Problem
The daemon has no graceful shutdown and leaks resources on crash:

1. **No SIGTERM handler** (`daemon.ts`) — `systemctl stop` kills active sessions without cleanup
2. **DB pool never closed** (`index.ts:63-72`) — `pool.end()` never called on shutdown
3. **No pool error listener** (`api.ts:1431`) — unhandled pool errors crash the process silently
4. **Active sessions only in memory** (`daemon.ts:112`) — daemon crash = orphaned sessions, no recovery

## Action Items
- [ ] Add `process.on('SIGTERM')` and `process.on('SIGINT')` handlers
- [ ] Drain active sessions before exit (wait up to `TimeoutStopSec`)
- [ ] Add `pool.on('error')` listener with logging
- [ ] Call `pool.end()` in shutdown sequence
- [ ] Persist active session state to DB so crashed sessions can be detected on restart
- [ ] Log shutdown sequence clearly for debugging

## Files
- `orchestrator/src/index.ts`
- `orchestrator/src/daemon.ts`
- `orchestrator/src/api.ts`
""",
    },
    # 3. HIGH — Experiment Pipeline Retry & Atomic Writes
    {
        "title": "Add retry logic and atomic writes to experiment pipelines",
        "priority": 2,
        "labels": [EXPERIMENT, BUG],
        "state": TODO_STATE,
        "description": """\
## Problem — Most Likely Cause of Pipeline Failures
Experiment scripts have no retry logic and non-atomic writes:

### No Retry on API Calls
- `cross_model_verification.py:376` — `client.query()` with no retry; rate limit = entire experiment fails
- `self_consistency.py:409` — same pattern; transient 429/500 errors crash the batch
- `batch_evaluate.py:62-115` — `asyncio.gather(return_exceptions=True)` silently swallows errors

### Non-Atomic Writes
- `cross_model_verification.py:352-429` — JSONL append without atomic write; crash mid-write corrupts file
- `self_consistency.py:407-430` — same pattern; no `fsync()` after write
- `export_results.py:157-162` — JSON written directly; partial write on failure
- `run_evaluation.py:549-584` — atomic write attempt catches only `OSError`, not `ValueError` from `json.dump()`

### Checkpoint Race Condition
- `checkpoint.py:50-78` — in-memory cache updated after file write; two processes can interleave JSONL lines

## Action Items
- [ ] Add retry decorator with exponential backoff + jitter for all API calls (3 retries, 429/500/timeout)
- [ ] Use temp-file-then-rename pattern for all JSON/JSONL writes
- [ ] Add `os.fsync()` before rename for critical output files
- [ ] Fix checkpoint to use file locking properly (or switch to SQLite)
- [ ] Fix `run_evaluation.py` atomic write to catch all exceptions on `json.dump()`
- [ ] Add resume capability to verification-complexity scripts (currently missing)

## Files
- `projects/reasoning-gaps/benchmarks/batch_evaluate.py`
- `projects/reasoning-gaps/benchmarks/checkpoint.py`
- `projects/reasoning-gaps/benchmarks/run_evaluation.py`
- `projects/verification-complexity/experiments/cross_model_verification.py`
- `projects/verification-complexity/experiments/self_consistency.py`
- `projects/reasoning-gaps/benchmarks/export_results.py`
""",
    },
    # 4. HIGH — Budget Enforcement
    {
        "title": "Fix budget enforcement: transactional checks and cost caps",
        "priority": 2,
        "labels": [DAEMON, INFRA],
        "state": TODO_STATE,
        "description": """\
## Problem
Budget enforcement has multiple gaps:

1. **Non-transactional budget check** (`daemon.ts:306-312`) — two concurrent dispatches can both pass the check and overspend
2. **No per-run cost caps** in experiment scripts (`run_evaluation.py:614-711`) — batch can exceed daily $40 budget with no mid-run monitoring
3. **Floating-point arithmetic** (`pricing.ts:56-66`) — monetary values use IEEE 754 floats; rounding errors accumulate over thousands of transactions
4. **Hardcoded fallback cost** (`budget-tracker.ts:417`) — `$455.50` fixed cost assumed when DB unavailable; will drift
5. **JSONL parsing crash** (`budget-tracker.ts:491-495`) — one malformed line in budget JSONL crashes the entire budget status computation

## Action Items
- [ ] Implement optimistic locking or budget reservation before session launch
- [ ] Add cost estimate validation before batch runs start (compare to remaining budget)
- [ ] Add mid-run cost monitoring with abort threshold
- [ ] Use integer cents or `decimal.js` for cost calculations
- [ ] Move fixed costs to config file, not hardcoded
- [ ] Add try/catch around JSONL line parsing (skip malformed lines with warning)

## Files
- `orchestrator/src/daemon.ts`
- `orchestrator/src/pricing.ts`
- `orchestrator/src/budget-tracker.ts`
- `projects/reasoning-gaps/benchmarks/run_evaluation.py`
""",
    },
    # 5. HIGH — EventBus Reliability
    {
        "title": "Fix EventBus error handling and connection recovery",
        "priority": 2,
        "labels": [DAEMON, BUG],
        "state": TODO_STATE,
        "description": """\
## Problem
The EventBus has multiple reliability issues:

1. **Swallowed errors** (`event-bus.ts:221`) — `.catch(() => {})` silently ignores DB update failures after successful handler execution. Event processed in memory but not marked in DB → re-processed on restart.
2. **No circuit breaker on dead letter retry** (`event-bus.ts:228-240`) — `retryAllDeadLetters()` hammers failing handlers infinitely without backoff
3. **Heartbeat reconnect loop** (`event-bus.ts:85-92`) — if `reconnect()` fails, timer keeps running → log spam, stale client
4. **Unbounded message queue** (`event-bus.ts:41-42`) — no limit on concurrent handlers; slow handlers + fast events = memory growth

## Action Items
- [ ] Replace `.catch(() => {})` with proper error logging and retry
- [ ] Add circuit breaker: track consecutive failures per dead letter, stop after N attempts
- [ ] Fix heartbeat: disable timer during reconnect, re-enable on success
- [ ] Add bounded concurrency (semaphore) for event handlers
- [ ] Add `reconnectAttempts` counter with exponential backoff

## Files
- `orchestrator/src/event-bus.ts`
""",
    },
    # 6. HIGH — Health Check & Startup Validation
    {
        "title": "Implement real health checks and startup validation",
        "priority": 2,
        "labels": [INFRA],
        "state": TODO_STATE,
        "description": """\
## Problem
Health checks are superficial and startup has no validation:

1. **Health check returns 200 even when DB is down** (`api.ts:630-672`) — reports `"database": "unavailable"` but still HTTP 200. CI deploys succeed with broken API.
2. **No DB connection test on startup** (`index.ts:69-72`) — pool created but never tested; daemon reports "started" but crashes on first query
3. **No env var validation** (`index.ts:44-66`) — `--interval 0` = busy loop, `--max-sessions -1` = unlimited sessions
4. **CI rollback fragile** (`ci.yml:161-205`) — previous commit stored in `/tmp` (ephemeral); lost on reboot
5. **Systemd doesn't require PostgreSQL** (`deepwork-daemon.service:4`) — `After=` but not `Requires=`; daemon races DB startup

## Action Items
- [ ] Health check: return 503 if database is unreachable
- [ ] Add `/api/ready` readiness probe (checks DB, event bus, git availability)
- [ ] Validate DB connection on startup with `SELECT 1`; exit(1) on failure
- [ ] Validate env vars have sane ranges (interval ≥ 1min, sessions ≥ 1)
- [ ] Store rollback commit in persistent location, not `/tmp`
- [ ] Add `Requires=postgresql.service` to systemd unit
- [ ] Add startup validation script that checks all dependencies

## Files
- `orchestrator/src/api.ts`
- `orchestrator/src/index.ts`
- `orchestrator/deploy/deepwork-daemon.service`
- `.github/workflows/ci.yml`
""",
    },
    # 7. HIGH — Race Conditions
    {
        "title": "Fix race conditions in knowledge graph and session tracking",
        "priority": 2,
        "labels": [DAEMON, BUG],
        "state": TODO_STATE,
        "description": """\
## Problem
Several race conditions exist:

1. **Knowledge graph duplicate claims** (`knowledge-graph.ts:87-109`) — embedding computation + dedup check happens outside a transaction. Two simultaneous identical claims both pass dedup and get inserted.
2. **Session tracking without mutex** (`daemon.ts:112, 475, 502, 513, 550`) — `activeSessions` Map modified during iteration; concurrent session completion + new dispatch = undefined behavior
3. **Stale session detection** (`daemon.ts:838-849`) — uses wall-clock only, never checks if underlying process is alive. Crashed process → session stays "active" until next cycle (up to 30 min).
4. **Chain depth not validated in processSessionSignals** (`daemon.ts:299-302`) — validated in `queueSession()` but not when chaining internally.

## Action Items
- [ ] Wrap knowledge graph dedup + insert in a DB transaction
- [ ] Add UNIQUE constraint on normalized statement + project
- [ ] Use a lock or queue pattern for activeSessions mutations
- [ ] Add process health check (heartbeat or PID check) for stale detection
- [ ] Centralize chain depth validation to a single function called from both paths

## Files
- `orchestrator/src/knowledge-graph.ts`
- `orchestrator/src/daemon.ts`
""",
    },
    # 8. MEDIUM — API Security Hardening
    {
        "title": "Harden API security: auth, CORS, rate limiting, path traversal",
        "priority": 3,
        "labels": [SECURITY, INFRA],
        "state": BACKLOG_STATE,
        "description": """\
## Problem
Several API security gaps:

1. **WebSocket auth via query string** (`api.ts:687-691`) — API key visible in server logs, browser history
2. **CORS defaults to `*`** (`api.ts:1444`) — wildcard if `CORS_ORIGIN` env var not set
3. **No rate limiting on auth failures** (`api.ts:61-78`) — brute-force possible despite nginx global rate limit
4. **Path traversal in eval-manager** (`eval-manager.ts:194`) — `task`/`condition` not validated; could escape results directory with `../`
5. **No query timeouts** — all `pool.query()` calls across API lack explicit timeouts; hung query blocks event loop

## Action Items
- [ ] Move WebSocket auth to `Authorization` header or `Sec-WebSocket-Protocol`
- [ ] Set `CORS_ORIGIN` explicitly in production .env; remove wildcard default
- [ ] Add per-IP rate limiting on failed auth attempts
- [ ] Validate `task` and `condition` match `^[a-zA-Z0-9_-]+$`
- [ ] Add `statement_timeout` to pool config or per-query

## Files
- `orchestrator/src/api.ts`
- `orchestrator/src/eval-manager.ts`
- All route files in `orchestrator/src/routes/`
""",
    },
    # 9. MEDIUM — Deployment Pipeline Hardening
    {
        "title": "Harden deployment: migrations, systemd, nginx, monitoring",
        "priority": 3,
        "labels": [INFRA, TECH_DEBT],
        "state": BACKLOG_STATE,
        "description": """\
## Problem
Deployment has several fragility points:

1. **No automatic DB migrations** — 11 SQL files in `orchestrator/sql/` applied manually; new code can deploy against stale schema
2. **Missing site-next systemd service file** — docs reference it but no file exists; operator must create manually
3. **Nginx has no upstream health checks** (`deploy/nginx.conf:11-14`) — no `max_fails`/`fail_timeout`; slow failures if backend is down
4. **No structured logging** — inconsistent error messages across daemon, API, and routes; no request ID tracing
5. **Missing `.env` validation in systemd** — service starts with empty env if file missing
6. **No external API call timeouts** (`cost-poller.ts:80, 122, 161`) — `fetch()` without `AbortController`; provider API hang blocks entire cycle

## Action Items
- [ ] Add migration runner to daemon startup (track applied versions in `schema_migrations` table)
- [ ] Create and document `deepwork-site.service` for Next.js
- [ ] Add `max_fails=3 fail_timeout=30s` to nginx upstream
- [ ] Add `AbortController` timeout to all external `fetch()` calls in cost-poller
- [ ] Add structured JSON logging with request IDs
- [ ] Validate `.env` existence and required keys in systemd `ExecStartPre`

## Files
- `orchestrator/sql/` (all migration files)
- `orchestrator/deploy/deepwork-daemon.service`
- `orchestrator/deploy/nginx.conf`
- `orchestrator/src/cost-poller.ts`
- `.github/workflows/ci.yml`
""",
    },
    # 10. MEDIUM — Experiment Reproducibility & Error Handling
    {
        "title": "Improve experiment reproducibility and error handling",
        "priority": 3,
        "labels": [EXPERIMENT, TECH_DEBT],
        "state": BACKLOG_STATE,
        "description": """\
## Problem
Experiment scripts have reproducibility and error handling gaps:

1. **No random seeds** (`self_consistency.py`, `run_experiment.py`) — results not reproducible across runs
2. **Fragile answer extraction** (`answer_extraction.py:81-97`) — regex can over-strip markdown; corrupts legitimate answers
3. **Fragile verification judgment parsing** (`cross_model_verification.py:149-182`) — hardcoded word boundary regex; edge cases fail silently
4. **`logging.basicConfig(force=True)`** (`evaluate.py:402`) — resets all loggers when imported as library
5. **Missing JSON error handling** (`analyze.py:184-193`) — one corrupt result file blocks entire analysis
6. **No CLI argument validation** (`run_evaluation.py` args) — no check that model names exist before starting evaluation
7. **Generic error suppression** (`tool_executor.py:166-196`) — catches `Exception`; masks real bugs. `"success": "false"` as string, not bool.

## Action Items
- [ ] Add `random.seed()` and `numpy.random.seed()` to all experiment scripts
- [ ] Add `--seed` CLI argument with default
- [ ] Add try/catch around JSON loading in analysis scripts (skip corrupt files with warning)
- [ ] Fix `tool_executor.py` success field to be bool, not string
- [ ] Validate model names against known list before starting batch
- [ ] Use `logging.getLogger(__name__)` instead of `basicConfig(force=True)`
- [ ] Add unit tests for answer extraction edge cases

## Files
- `projects/reasoning-gaps/benchmarks/evaluate.py`
- `projects/reasoning-gaps/benchmarks/analyze.py`
- `projects/reasoning-gaps/benchmarks/answer_extraction.py`
- `projects/reasoning-gaps/benchmarks/tool_executor.py`
- `projects/reasoning-gaps/benchmarks/run_evaluation.py`
- `projects/verification-complexity/experiments/cross_model_verification.py`
- `projects/verification-complexity/experiments/self_consistency.py`
""",
    },
]

print(f"Creating {len(issues)} sub-issues...\n")

created = []
for issue_data in issues:
    result = create_issue(
        title=issue_data["title"],
        description=issue_data["description"],
        priority=issue_data["priority"],
        labels=issue_data["labels"],
        state_id=issue_data.get("state", TODO_STATE),
        parent_id=parent_id,
    )
    created.append(result)
    print()

print("=" * 60)
print(f"Created {len(created) + 1} issues total (1 parent + {len(created)} sub-issues)")
print(f"\nParent: {parent['identifier']} — {parent['url']}")
print("\nSub-issues:")
for c in created:
    print(f"  {c['identifier']}: {c['title']}")
