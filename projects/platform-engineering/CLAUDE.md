# Platform Engineering — Agent Instructions

You are an engineer agent working on the Forge platform itself.

## Your Task
You have been dispatched to address a specific backlog ticket. Your job:

1. Read the backlog to find your assigned ticket (check `GET /api/backlog?status=in_progress`)
2. Understand the issue thoroughly before making changes
3. Make targeted, minimal changes to fix the issue
4. Run `npm run build --workspace=orchestrator` to verify typecheck passes
5. Commit with conventional commit format: `fix(platform): description` or `feat(platform): description`
6. Push and create a PR to `main`

## Rules
- One ticket per session — do not scope-creep
- Always verify typecheck passes before committing
- Do not modify research project files
- Do not change agent personality files (SOUL.md)
- Do not modify gateway.json (that requires human review)
- Prefer fixing the root cause over working around it
- If the ticket is unclear or too risky, commit a comment explaining why and mark it `wont_fix`

## Code Style
- TypeScript, ESM modules
- `node:` prefix for Node.js built-ins
- Async/await, minimal dependencies
- Follow existing patterns in the codebase
