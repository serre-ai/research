# Git Workflow for DeepWork

## Context

Single engineer (Oddur) + autonomous daemon agents + Claude Code sessions. Multiple research projects sharing an orchestrator, dashboard, and infrastructure. The standard gitflow model doesn't fit — there's no team to review PRs, no staging environment, and cross-cutting changes (orchestrator, CI, dashboard) affect all projects.

## Principles

1. **`main` is always the source of truth.** No long-lived feature branches. Main should always build and pass tests.
2. **Work directly on `main`** for all cross-cutting changes (orchestrator, dashboard, CI, shared templates).
3. **Short-lived branches only** for isolated, parallel work — agent worktree branches that live for minutes, not days.
4. **Commit often, push after every commit.** Small commits with conventional messages. The commit history IS the project log.
5. **No PRs for solo work.** PRs are only for daemon-generated sessions that need review before merge.

## Branch Model

```
main (always deployable)
  └── worktree-agent-* (ephemeral, auto-created by daemon/agents, deleted after merge)
```

That's it. No `develop`, no `research/*`, no `feature/*`. The old `research/<project>` branches created divergence hell because cross-cutting changes couldn't be shared.

## How Different Work Types Flow

### Research paper work (paper text, experiments, analysis)
- Work directly on `main`
- Commit scope: `paper(reasoning-gaps): add error correlation to Discussion`
- No branch needed — paper changes don't break builds

### Infrastructure changes (orchestrator, dashboard, CI)
- Work directly on `main`
- Commit scope: `feat(orchestrator): add experiment pre-registration protocol`
- Run `npm run build --workspace=orchestrator && npm run test --workspace=forge` before pushing

### Agent team sprints (parallel worktrees)
- Each agent gets a worktree branch: `worktree-agent-<hash>`
- Agent makes changes, commits, returns
- Main session merges immediately and deletes the branch
- Never let agent branches persist overnight

### Daemon sessions (autonomous)
- Daemon creates worktrees on `main` (not on research branches)
- Sessions commit to worktree, push, create PR
- Human reviews PR and merges (or daemon auto-merges if quality score > threshold)

## Commit Convention

```
type(scope): description

Types: paper, research, feat, fix, chore, docs, data, test
Scopes: reasoning-gaps, verification-complexity, self-improvement-limits,
        orchestrator, forge, ci, shared
```

Examples:
```
paper(reasoning-gaps): reframe Type 6 predictions
research(verification-complexity): between-model error correlation analysis
feat(orchestrator): add experiment pre-registration protocol
fix(forge): re-subscribe to WS channels on reconnect
chore(ci): remove stale openclaw job
```

## What NOT to Do

- **Don't create long-lived branches.** If a branch lives more than a day, merge it or delete it.
- **Don't work on research branches.** All work goes on `main`. The `research/*` naming was a mistake — it created parallel universes that couldn't share infrastructure changes.
- **Don't let agent worktree branches accumulate.** Clean them up in the same session.
- **Don't use PRs for your own work.** Just push to main. PRs are for daemon sessions that need review.
- **Don't amend published commits.** Create new commits instead.

## Deployment

Main is always deployable. After pushing to main:
```bash
ssh deepwork-vps "cd ~/deepwork && git pull && npm run build --workspace=orchestrator && npm run build --workspace=forge"
ssh deepwork-vps-root "systemctl restart deepwork-daemon && systemctl restart deepwork-site"
```

The CI workflow runs on push to main and auto-deploys if all checks pass.

## Multi-Project Isolation

Projects are isolated by directory, not by branch:
```
projects/reasoning-gaps/      — paper, experiments, data, notes
projects/verification-complexity/  — paper, experiments, data, notes
projects/self-improvement-limits/  — paper, experiments, data, notes
```

Each project has its own `BRIEF.md`, `status.yaml`, `CLAUDE.md`. The daemon reads `status.yaml` to decide what work to do. No branch switching needed.

## VPS Sync

The VPS tracks `main`. After pushing:
```bash
ssh deepwork-vps "cd ~/deepwork && git pull origin main"
```

If the VPS has local changes (from daemon sessions), they should be on worktree branches that get PRed back to main. The main checkout on the VPS should always be clean and on `main`.
