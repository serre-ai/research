# deepwork-api

Core skill for interacting with the Deepwork platform API.

## Usage
All agents use this skill to query project status, budget, eval results, and recent activity from the Deepwork API running at `localhost:3001`.

## Authentication
Requests require the `X-Api-Key` header with the value from `DEEPWORK_API_KEY` environment variable.

## Endpoints

### Projects
- `GET /api/projects` — List all projects with status
- `GET /api/projects/:id` — Get project details
- `PATCH /api/projects/:id/status` — Update project status.yaml (fields: phase, current_focus, current_activity, confidence, notes, status)

### Budget
- `GET /api/budget` — Current budget status (daily/monthly spend, limits)
- `GET /api/budget/history` — Spending history

### Evaluations
- `GET /api/evals` — List eval runs with status
- `GET /api/evals/:id` — Get eval run details and results
- `GET /api/evals/results?project=:name` — Get results for a project

### Sessions
- `GET /api/sessions` — List recent daemon sessions
- `GET /api/sessions/:id` — Get session details and output
- `POST /api/sessions/dispatch` — Dispatch a new daemon session (see session-dispatch skill)
- `GET /api/sessions/dispatch/queue` — View dispatch queue and recent dispatches

### Health
- `GET /api/health` — Platform health check
- `GET /api/daemon/health` — Full daemon state (sessions, dispatch queue, failures, quality)

### Quality
- `GET /api/quality` — Quality scores across projects

### Backlog
- `GET /api/backlog` — List engineering backlog tickets
- `POST /api/backlog` — Create a backlog ticket
- `PATCH /api/backlog/:id` — Update a ticket
- `GET /api/backlog/:id` — Get a single ticket

### Memory / Digests
- `GET /api/memory/digest` — List available digest dates
- `GET /api/memory/digest/latest` — Get the most recent daily digest
- `GET /api/memory/digest/:date` — Get digest for a specific date
- `POST /api/memory/digest` — Save a daily digest

## Script
Use `scripts/api-client.sh` for convenient access. Example:
```bash
./scripts/api-client.sh GET /api/projects
./scripts/api-client.sh GET /api/budget
./scripts/api-client.sh GET /api/sessions
./scripts/api-client.sh GET /api/daemon/health
./scripts/api-client.sh GET /api/backlog
./scripts/api-client.sh GET /api/memory/digest/latest
./scripts/api-client.sh POST /api/sessions/dispatch '{"project":"reasoning-gaps","agent_type":"writer","priority":"high","reason":"test","triggered_by":"sol"}'
```
