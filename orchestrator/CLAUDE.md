# orchestrator

Backend engine for the Deepwork research platform. Express REST API, WebSocket server, and autonomous daemon that runs Claude Code research sessions.

## Stack
TypeScript, Express, WebSocket (ws), PostgreSQL (pg), ESM modules.

## Running

```bash
npm run build   # tsc → dist/
npm start       # node dist/index.js
```

Requires `.env` at repo root with `DATABASE_URL`, `API_PORT`, `DEEPWORK_API_KEY`, and API keys for Anthropic/OpenAI/OpenRouter.

VPS service: `deepwork-daemon.service` on port 3001.

## Architecture

### Entry point
`src/index.ts` — creates the daemon, starts the API server.

### API (`src/api.ts`)
Express server exposing REST endpoints + WebSocket. All endpoints require `X-Api-Key` header matching `DEEPWORK_API_KEY` (except health check).

Route modules are in `src/routes/`:
| Module | Endpoints |
|--------|-----------|
| `knowledge.ts` | `/api/knowledge/*` — claims, evidence, graph |
| `events.ts` | `/api/events/*` — event log, dead letters |
| `planner.ts` | `/api/planner/*` — research planning |
| `verification.ts` | `/api/verification/*` — claim verification |
| `paper.ts` | `/api/paper/*` — paper build status |

The main `api.ts` file also handles inline routes for projects, sessions, budget, health, eval, decisions, quality, digest, and activity.

### Daemon (`src/daemon.ts`)
Autonomous loop that:
1. Polls for work (pending sessions, triggers, rituals)
2. Runs Claude Code sessions via `session-runner.ts`
3. Tracks budget via `budget-tracker.ts`
4. Emits events via `event-bus.ts`

### Key services
- `session-runner.ts` — spawns Claude Code in project worktrees
- `research-planner.ts` — AI-driven research planning
- `knowledge-graph.ts` — entity/claim/evidence graph with embeddings
- `verification.ts` — automated claim verification
- `event-bus.ts` — pub/sub event system with PostgreSQL persistence
- `eval-manager.ts` — benchmark evaluation job runner
- `budget-tracker.ts` — spending limits and cost tracking

### Database
PostgreSQL. Schema migrations in `sql/` (001–009), applied manually. Tables use `authjs_` prefix for auth, no prefix for platform data.

Key tables: `projects`, `sessions`, `eval_results`, `eval_runs`, `budget_logs`, `activity_log`, plus collective/knowledge/governance tables in later migrations.

### WebSocket
Broadcasts events to connected clients on channels (`eval-progress`, `logs`, `budget`, `health`). The forge dashboard subscribes to these for real-time updates.

## Adding a new endpoint

1. Create route module in `src/routes/<name>.ts`:
   ```ts
   import { Router } from 'express';
   import type { Pool } from 'pg';

   export function myRoutes(pool: Pool): Router {
     const r = Router();
     r.get('/my-thing', async (req, res) => { ... });
     return r;
   }
   ```
2. Import and mount in `src/api.ts`:
   ```ts
   app.use('/api', myRoutes(pool));
   ```
3. Add corresponding hook in `forge/src/hooks/` and export from index.
4. Rebuild and restart: `npm run build && sudo systemctl restart deepwork-daemon`

## Deploy

```bash
# On VPS after pushing:
cd ~/deepwork && npm run build --workspace=orchestrator
sudo systemctl restart deepwork-daemon
```
