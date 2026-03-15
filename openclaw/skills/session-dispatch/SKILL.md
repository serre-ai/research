# session-dispatch

Dispatch daemon sessions via the Deepwork API. Gives OpenClaw agents the ability to trigger Claude Code sessions on specific projects.

## Usage
Used by Sol (strategic dispatch) and Vera (auto-dispatch after review verdicts).

## Endpoints

### Dispatch a session
```bash
./scripts/dispatch.sh <project> <agent_type> <priority> <reason> <triggered_by>
```
- `project`: Project name (e.g., `reasoning-gaps`, `platform-engineering`)
- `agent_type`: One of `researcher`, `writer`, `editor`, `critic`, `experimenter`, `engineer`
- `priority`: `low`, `normal`, `high`, `critical`
- `reason`: Why this session is being dispatched
- `triggered_by`: Agent name dispatching (e.g., `sol`, `vera`)

### View dispatch queue
```bash
./scripts/dispatch.sh --queue
```

## Rate Limits
- Max 5 dispatches per hour per agent
- Max 10 dispatches per day total
- Chain depth limit: 3 (prevents infinite loops)
- Budget must not be exceeded
- Cannot dispatch to a project with an active session

## Examples
```bash
# Sol dispatches a writer session for reasoning-gaps
./scripts/dispatch.sh reasoning-gaps writer high "Morning priority: paper revision needed" sol

# Vera auto-dispatches after REVISE verdict
./scripts/dispatch.sh reasoning-gaps writer high "REVISE verdict — addressing Section 4 feedback" vera

# View current queue
./scripts/dispatch.sh --queue
```
