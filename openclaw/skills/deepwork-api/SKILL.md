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

### Health
- `GET /api/health` — Platform health check

### Quality
- `GET /api/quality` — Quality scores across projects

## Script
Use `scripts/api-client.sh` for convenient access. Example:
```bash
./scripts/api-client.sh GET /api/projects
./scripts/api-client.sh GET /api/budget
./scripts/api-client.sh GET /api/sessions
```
