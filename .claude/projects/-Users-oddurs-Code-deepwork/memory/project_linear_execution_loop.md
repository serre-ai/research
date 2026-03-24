---
name: linear_execution_loop_implementation
description: Linear-driven autonomous execution loop — agent work done but needs rebasing onto daemon's current main
type: project
---

## Linear Execution Loop — Implementation Status (2026-03-22)

Three agents built the feature in worktree branches but couldn't merge due to daemon actively pushing commits to main. The code exists and is correct but needs rebasing.

### Agent Branches (preserved in worktrees)
- `worktree-agent-ace8e0f3` (commit `242f999`): Linear client — `getBlockingIssues()`, `isBlocked()`, `getIssueByIdentifier()`, structured `issueToBrief()` supplementary
- `worktree-agent-a543af98` (commit `7549db2`): Planner + daemon — `shouldRetry()`, `markRetried()`, dependency filtering in `linearDrivenBriefs()`, quality gate (<40 retries), critic chaining for Paper/Research labels, `storePendingCriticReview()`
- `worktree-agent-a1a076f9` (commit `49fffbb`): API — `POST /api/sessions/run-issue` endpoint

### What Needs Doing
1. Read current `main` versions of `linear.ts`, `daemon.ts`, `research-planner.ts`, `api.ts`
2. Apply each agent's features against the current base (don't cherry-pick — manual apply is safer given structural changes from daemon's graceful shutdown commit)
3. Build and verify: `npm run build --workspace=orchestrator`

### Design Decisions (user-confirmed)
- Dependencies: Linear's "blocked by" relations
- Quality gate: auto-retry once if score < 40/100, then flag for human
- Critic scope: Paper + Research labels only
- Manual trigger: `POST /api/sessions/run-issue { identifier: "DW-141" }`

### Scope Note
User wants this focused on **infra/engineering tasks**, not paper work. Paper research (proofs, experiments, writing) is better as interactive sessions. The loop is highest value for: Darkreach launch (DW-128-135), CI fixes, bibliography cleanup, experiment execution (running pre-built scripts).

**Why:** Research decisions need human judgment (e.g., the Theorem 2c refinement, SC→cross-model pivot). Infrastructure tasks have clear pass/fail criteria that the quality gate can actually enforce.

### Full Plan
See `/Users/oddurs/.claude/plans/whimsical-riding-dove.md` for the complete design with code snippets and flow diagrams.
