# Research Operations Playbook

This is the operating manual for the Serre AI research platform. It covers everything from how a single research session works to how the portfolio of projects is managed across months.

Related documents:
- [Infrastructure and Deployment](INFRASTRUCTURE.md) -- server setup, daemons, API keys
- [Scaling Strategy](SCALING.md) -- budget allocation, concurrent project capacity, growth plan

---

## Table of Contents

1. [Project Lifecycle](#project-lifecycle)
2. [Session Lifecycle](#session-lifecycle)
3. [Daily Operations](#daily-operations)
4. [Weekly Cadence](#weekly-cadence)
5. [Monthly Cadence](#monthly-cadence)
6. [Monitoring and the Dashboard](#monitoring-and-the-dashboard)
7. [Failure Modes and Recovery](#failure-modes-and-recovery)
8. [The Human Role](#the-human-role)
9. [Decision Protocol](#decision-protocol)

---

## Project Lifecycle

Every research project moves through a defined lifecycle. Each phase has entry criteria (what must be true before starting the phase) and exit criteria (what must be true before moving on).

### Phase Overview

```
Ideation --> Scoping --> Research --> Drafting --> Revision --> Final --> Submission --> Post-Publication
```

### Phase Definitions

#### 1. Ideation

**What happens:** An idea surfaces -- from reading a paper, spotting a gap, or pure curiosity. Ideas are captured in `docs/ideas/` as lightweight markdown files.

**Entry criteria:** None. Anyone (human or agent) can drop an idea file.

**Exit criteria:**
- The idea has a one-paragraph description of the core claim or question
- An initial feasibility assessment exists (is this tractable? is there a venue?)
- A human has read the idea and flagged it as "worth scoping"

**Artifacts:** `docs/ideas/<name>.md`

#### 2. Scoping

**What happens:** The idea is shaped into a concrete project. A `BRIEF.md` is written specifying research goals, hypotheses, methodology, target venue, and timeline.

**Entry criteria:**
- An idea file exists with a feasibility assessment
- Human approval to invest scoping effort

**Exit criteria:**
- `projects/<name>/BRIEF.md` is complete with: title, venue, research area, goals, hypotheses, methodology, timeline
- `projects/<name>/status.yaml` is initialized (phase: `research`, status: `active`)
- `projects/<name>/CLAUDE.md` contains project-specific agent instructions
- A git branch `research/<name>` exists
- An initial commit has been made: `research(<name>): initialize project`

**Artifacts:** Full project directory under `projects/<name>/`

**How to create:** Use the `/new-project` command, which scaffolds the directory structure, creates `BRIEF.md`, `status.yaml`, and `CLAUDE.md`, sets up the branch, and commits.

#### 3. Research

**What happens:** Literature review, framework development, and benchmark/experiment design. This is where the intellectual core of the project takes shape.

**Entry criteria:**
- Project directory is initialized with `BRIEF.md`, `status.yaml`, `CLAUDE.md`
- Research branch exists and worktree can be created

**Exit criteria (ALL must be true to move to Drafting):**
- Literature review is complete: at minimum 15-20 key references identified and summarized in `notes/`
- The core theoretical framework or methodology is defined and documented
- If empirical: benchmark tasks or experiments are designed (not necessarily run)
- If theoretical: main claims/theorems are stated (not necessarily proven)
- `status.yaml` reflects: `literature_review: complete`, core framework status updated
- A milestone PR has been created and merged summarizing research findings
- Confidence score in `status.yaml` is >= 0.6

**Typical duration:** 2-4 weeks

**Key activities:**
- Web search for papers (Firecrawl API, WebSearch)
- Reading and annotating papers
- Writing structured notes in `projects/<name>/notes/`
- Defining formal frameworks
- Designing benchmarks or experiments
- Logging decisions about scope, direction, methodology

#### 4. Drafting

**What happens:** The paper is written. Research notes are transformed into a structured LaTeX document.

**Entry criteria:**
- All Research phase exit criteria are met
- Paper directory exists: `projects/<name>/paper/`
- A decision has been logged about paper structure (number of sections, what goes where)

**Exit criteria (ALL must be true to move to Revision):**
- A complete first draft exists in `projects/<name>/paper/`
- All sections have substantive content (not just placeholders)
- If empirical: experimental results are included with tables/figures
- If theoretical: proofs or proof sketches are present
- Abstract is written
- Related work section covers key references from the research phase
- `status.yaml` reflects: `paper_writing: draft_complete`
- A milestone PR with the full draft has been created

**Typical duration:** 2-3 weeks

**Key activities:**
- Writing LaTeX (NeurIPS, ICML, etc. format as appropriate)
- Running experiments and integrating results
- Creating figures and tables
- Writing proofs or formalizations
- Drafting abstract and introduction

#### 5. Revision

**What happens:** The draft is critically reviewed and improved. The reviewer agent evaluates the paper, and the writer agent addresses feedback.

**Entry criteria:**
- Complete first draft exists
- At least one review cycle has been initiated (reviewer agent has read the draft)

**Exit criteria (ALL must be true to move to Final):**
- At least 2 full review-revise cycles have been completed
- The reviewer agent rates the paper as "Accept" or "Accept with minor revisions"
- All major weaknesses from reviews have been addressed
- Experiments have been validated or strengthened based on reviewer feedback
- `status.yaml` reflects: `paper_writing: revision_complete`, review scores logged
- A milestone PR with the revised paper has been created

**Typical duration:** 1-2 weeks

**Key activities:**
- Running the reviewer agent (`/.claude/agents/reviewer.md`)
- Addressing weaknesses and questions
- Strengthening experiments (additional baselines, ablations)
- Polishing writing, tightening arguments
- Verifying all claims are supported

#### 6. Final

**What happens:** Camera-ready preparation. Formatting, final proofreading, supplementary materials.

**Entry criteria:**
- Revision phase exit criteria met
- Venue submission deadline is known and > 48 hours away

**Exit criteria:**
- Paper meets venue formatting requirements (page limits, margins, font)
- All figures are high-resolution and properly captioned
- References are complete and correctly formatted
- Supplementary material is organized if applicable
- `status.yaml` phase updated to `final`
- Paper branch `paper/<name>/v1` is created with the final version

**Typical duration:** 2-3 days

#### 7. Submission

**What happens:** The paper is submitted to the target venue.

**Entry criteria:**
- Final-phase paper exists on `paper/<name>/v1` branch
- Human has reviewed the final version
- Submission portal account is set up

**Exit criteria:**
- Paper is submitted (confirmation number recorded)
- `status.yaml` updated with submission date and confirmation
- All project branches are merged to `main`
- A tagged release is created: `v1.0-submitted`

**The human role is critical here:** The human handles the actual submission portal, enters author information, selects tracks/topics, and confirms submission.

#### 8. Post-Publication

**What happens:** Reviews come back. The project enters either a revision cycle (if revise-and-resubmit) or is archived.

**Activities:**
- Parse reviewer feedback and log in `status.yaml`
- If revise-and-resubmit: return to Revision phase with reviewer comments as input
- If accepted: prepare camera-ready, celebrate
- If rejected: assess whether to revise and resubmit elsewhere, or archive
- Archive artifacts to `projects/<name>/archive/`

---

## Session Lifecycle

A session is a single Claude agent working on a project in an isolated git worktree. Sessions are the atomic unit of work.

### How a Session Starts

1. **Orchestrator receives a start command** -- either `forge start <project>` from the CLI or the scheduling loop picks a project.
2. **ProjectManager reads `status.yaml`** to determine the project's current phase, focus, and next steps.
3. **GitEngine creates a worktree** at `.worktrees/<project>/` on the project's branch (`research/<project>`). If the branch exists, it checks it out; if not, it creates it from `main`.
4. **SessionManager builds an agent prompt** combining the project's `BRIEF.md`, `CLAUDE.md`, `status.yaml` state, and workflow instructions.
5. **The Claude agent session starts** (currently via Claude Code CLI; future: Claude Agent SDK programmatic sessions).

### What Happens During a Session

The agent works autonomously:
- Reads project files to orient itself
- Performs research, writing, or revision depending on the phase
- Makes decisions and logs them in `status.yaml`
- Makes frequent conventional commits: `type(project-name): description`
- Pushes to remote after every commit
- Creates milestone PRs when reaching significant checkpoints
- Updates `status.yaml` with progress

### How a Session Ends

Sessions end in one of three ways:

1. **Natural completion** -- The agent finishes its current task set and the session completes.
2. **Orchestrator stops the session** -- `SessionManager.stopProject()` is called, which:
   - Commits any pending changes: `chore(<project>): save session state`
   - Pushes to remote
   - Cleans up the worktree via `GitEngine.cleanupProjectWorktree()`
   - Removes the session from the active sessions map
3. **Timeout/Error** -- The session hits a time limit or crashes. The worktree persists and can be resumed.

### Session Isolation

Each session operates in its own git worktree, providing full isolation:

```
deepwork/
  .worktrees/
    reasoning-gaps/     # worktree on research/reasoning-gaps branch
    scaling-laws/       # worktree on research/scaling-laws branch
  projects/             # project metadata (on main branch)
```

This means multiple agents can work on different projects simultaneously without interfering with each other. Each worktree has its own working directory, index, and checked-out branch.

---

## Daily Operations

A typical day in the Forge platform looks like this:

### Morning (automatic or human-initiated)

1. **Orchestrator scheduling loop runs** (when daemon mode is active)
   - Reads all project `status.yaml` files
   - Identifies which projects are active and what their next steps are
   - Prioritizes based on deadlines, phase, and resource availability
   - Starts sessions for top-priority projects

2. **If running manually:** Human starts sessions with `forge start <project>`

### Throughout the Day

3. **Agent sessions work autonomously**
   - Commits accumulate on project branches
   - `status.yaml` files are updated as milestones are hit
   - Milestone PRs are created when phases complete or significant findings emerge

4. **Dashboard shows real-time state**
   - Run the CLI dashboard (`deepwork` or `npx tsx cli/src/index.tsx`) to see:
     - Project statuses and phases
     - Budget utilization
     - Recent commits across all projects
     - Resource allocation

### Evening / End of Day

5. **Review accumulated PRs** (human task)
   - Check GitHub for new milestone PRs
   - Review diffs, especially for research direction changes
   - Merge approved PRs to `main`
   - Leave comments on PRs that need agent attention

6. **Check budget** via the dashboard
   - Verify API spend is on track
   - If approaching alert threshold (80%), consider pausing lower-priority projects

### Continuous

7. **Agents commit and push frequently**
   - Every meaningful change gets a commit
   - Every commit is pushed to remote
   - This provides continuous backup and visibility

---

## Weekly Cadence

### Monday: Portfolio Review

- **Review all project `status.yaml` files** -- Are projects progressing? Any stalled?
- **Check the milestone PR backlog** -- Merge what's ready, comment on what needs work
- **Budget checkpoint** -- Is spend on track for the week? (Target: ~25% of monthly budget per week)
- **Prioritize the week** -- Which projects need sessions? Any deadlines approaching?

### Wednesday: Mid-Week Check

- **Dashboard scan** -- Quick look at project phases and recent commits
- **Address any blocked projects** -- If an agent logged a decision that needs human input (rare, given autonomous policy), resolve it
- **Check for new ideas** -- Review `docs/ideas/` for anything worth scoping

### Friday: Week-End Wrap

- **Ensure all sessions have committed and pushed** -- No orphaned work in worktrees
- **Merge any pending milestone PRs** that are ready
- **Update budget tracking** -- Record actual spend in `budget.yaml` if not automated
- **Brief retrospective** -- What went well? Any failure modes encountered?

### Weekly Metrics to Track

| Metric | Target | Warning Sign |
|--------|--------|-------------|
| Commits per project | 20-40/week | <10 (stalled) or >80 (thrashing) |
| PRs created | 1-2 per active project | 0 (no milestones) |
| Budget utilization | 20-30% of monthly | >35% (overspending) or <10% (underutilizing) |
| Phase progression | Visible progress | Same phase for >2 weeks without commits |
| Decision log growth | 2-5 per project/week | 0 (not logging) or >15 (indecisive) |

---

## Monthly Cadence

### First Week: Monthly Review

1. **Project health assessment** for every active project:
   - Is the project on track for its venue deadline?
   - Is the confidence score trending up?
   - Are there unresolved issues lingering?

2. **Budget reconciliation:**
   - Compare actual spend to planned allocation
   - Update `budget.yaml` history
   - Adjust allocations for next month if needed

3. **Idea pipeline review:**
   - Review `docs/ideas/` for new candidates
   - Decide which ideas to scope into projects
   - Archive ideas that are no longer interesting

### Mid-Month: Capacity Planning

4. **Evaluate concurrent project load:**
   - Are we running at capacity? Under-utilizing?
   - Refer to [Scaling Strategy](SCALING.md) for capacity formulas

5. **Infrastructure check:**
   - Disk usage on worktrees
   - API rate limit headroom
   - Any infrastructure upgrades needed?

### End of Month: Reporting

6. **Monthly summary:**
   - Papers submitted or progressed
   - Key findings across projects
   - Budget spent vs. allocated
   - Lessons learned, process improvements

### Monthly Health Dashboard

| Project | Phase | Weeks in Phase | Confidence | Budget Used | Deadline |
|---------|-------|---------------|------------|-------------|----------|
| reasoning-gaps | research | 1 | 0.5 | $45 | NeurIPS 2026 |
| *(example)* | drafting | 2 | 0.7 | $120 | ICML 2027 |

---

## Monitoring and the Dashboard

### Running the Dashboard

```bash
# From the repo root
cd cli && npx tsx src/index.tsx

# Or if built
deepwork
```

The dashboard shows:
- **Header:** Budget utilization, Max account count, active project count
- **Projects:** Each project with status, phase, branch, and decision counts
- **Budget:** Spending breakdown by category with a visual progress bar
- **Recent Activity:** Last 5 commits across all branches
- **Resources:** Claude Code Max count, decision policy mode, reasoning level, connected APIs

### What to Watch

| Signal | What It Means | Action |
|--------|--------------|--------|
| Project phase hasn't changed in 2+ weeks | Stalled or stuck in a loop | Check `status.yaml` for blockers; review recent commits for thrashing |
| Budget bar turning yellow (>50%) | Mid-month, halfway through budget | Normal if halfway through month; alarming if early |
| Budget bar turning red (>80%) | Approaching budget limit | Pause non-critical projects; check for runaway API usage |
| 0 commits in last 24h on an active project | Session may not be running | Verify orchestrator is running; check for errors |
| Many pending decisions | Agent is uncertain about direction | Review decisions and provide guidance, or verify autonomous policy is active |
| Confidence dropping | Research hitting dead ends | Review the project brief; consider pivoting or archiving |

### Checking Project State Directly

```bash
# View a project's status
cat projects/reasoning-gaps/status.yaml

# View recent commits on a project branch
git log --oneline research/reasoning-gaps -10

# See what's changed since main
git diff main...research/reasoning-gaps --stat

# List all worktrees
git worktree list

# List open PRs
gh pr list --state open
```

---

## Failure Modes and Recovery

### Session Stall

**Symptoms:** No new commits for hours on an active project. `status.yaml` unchanged.

**Causes:**
- Agent hit an error and stopped
- Agent is in a long web search or computation
- Worktree is in a broken git state

**Recovery:**
1. Check if the session process is still running
2. If dead: restart with `forge start <project>` -- the worktree will be recreated
3. If alive but stuck: stop the session, review the worktree for partial work, restart
4. If worktree has uncommitted changes: manually commit from `.worktrees/<project>/`, then restart

### Agent Loop

**Symptoms:** Commits are happening but content is repetitive. The agent is rewriting the same section, going back and forth on a decision, or producing low-quality output in volume.

**Causes:**
- Ambiguous instructions in `CLAUDE.md` or `BRIEF.md`
- A hard research problem with no clear path forward
- Status file not being updated, so agent re-reads stale state

**Recovery:**
1. Stop the session
2. Review recent commits: `git log --oneline research/<project> -20`
3. Read the agent's recent work to understand where it's looping
4. Update `status.yaml` with clearer `next_steps` or `current_focus`
5. Optionally update `CLAUDE.md` with more specific instructions
6. Restart the session

### Budget Exhaustion

**Symptoms:** Budget bar at 100% or spending exceeds `monthly_limit_usd`.

**Causes:**
- A project in experiment phase consuming heavy API calls
- Runaway web searches
- More concurrent projects than budget supports

**Recovery:**
1. Pause all non-critical projects immediately (set `status: paused` in `status.yaml`)
2. Review spending breakdown in `budget.yaml` to identify the culprit
3. Wait for the next billing cycle, or increase the budget if justified
4. When resuming: prioritize projects closest to submission deadlines
5. See [Scaling Strategy](SCALING.md) for budget allocation guidance

### Git Conflicts

**Symptoms:** Push fails on a project branch. Worktree setup fails because the branch is already checked out.

**Causes:**
- Two sessions tried to work on the same branch simultaneously
- A worktree wasn't cleaned up properly after a session
- Manual edits on `main` conflicted with a project branch

**Recovery:**
1. **Branch already checked out:** Clean up stale worktrees with `git worktree prune`, then retry
2. **Push conflicts:** Pull from remote first, resolve conflicts, commit, push
3. **Stale worktree:** `git worktree remove .worktrees/<project> --force`
4. **Merge conflict with main:** Let the agent handle it in the next session, or resolve manually

```bash
# Clean up stale worktrees
git worktree prune

# Force-remove a stuck worktree
git worktree remove .worktrees/<project> --force

# List all worktrees to see what's active
git worktree list
```

### Corrupt status.yaml

**Symptoms:** Dashboard shows errors. Orchestrator can't read project status. Agent behaves erratically.

**Causes:**
- Concurrent writes from multiple processes
- Partial write (agent crashed mid-update)
- YAML syntax error introduced by agent

**Recovery:**
1. Check git history for the last good version: `git log --oneline projects/<name>/status.yaml`
2. Restore from git: `git checkout HEAD~1 -- projects/<name>/status.yaml`
3. Manually fix YAML syntax if the issue is minor
4. Commit the fix: `fix(<name>): restore status.yaml from last good state`

### Worktree Disk Exhaustion

**Symptoms:** Disk full errors. New worktrees can't be created.

**Causes:**
- Too many worktrees accumulated without cleanup
- Large files (datasets, model checkpoints) committed to worktrees

**Recovery:**
1. List worktrees: `git worktree list`
2. Remove worktrees for completed or paused projects: `git worktree remove .worktrees/<project>`
3. Run `git worktree prune` to clean up stale references
4. Check for large files: `du -sh .worktrees/*`
5. See [Infrastructure](INFRASTRUCTURE.md) for disk planning guidance

---

## The Human Role

The Forge platform is designed for maximum agent autonomy, but humans play critical roles.

### Always Human

These activities cannot and should not be delegated to agents:

- **Greenlighting new projects** -- Deciding which ideas from `docs/ideas/` become funded projects
- **Conference submissions** -- Filling out submission portals, entering author info, selecting tracks
- **Presenting at conferences** -- Talks, posters, Q&A
- **Responding to reviewer feedback** -- Deciding whether to revise-and-resubmit or target a new venue
- **Budget decisions** -- Increasing or decreasing the monthly budget
- **Infrastructure changes** -- Provisioning servers, updating API keys

### Regularly Human (Weekly)

These activities benefit from human oversight:

- **Reviewing milestone PRs** -- Reading the diff, checking research quality, merging to `main`
- **Dashboard monitoring** -- Quick scan for warning signs (see Monitoring section)
- **Budget tracking** -- Ensuring spend is on pace

### Occasionally Human (Monthly)

- **Project health assessment** -- Are projects worth continuing?
- **Idea pipeline curation** -- Adding new ideas, archiving stale ones
- **Capacity planning** -- Should we add or remove projects?

### Rarely Human

These are handled by agents unless something goes wrong:

- Research direction decisions (agents decide autonomously, log in `status.yaml`)
- Writing and revision
- Literature review
- Experiment design and execution
- Git workflow (commits, branches, PRs)

---

## Decision Protocol

The platform operates with fully autonomous decision-making, as configured in `config.yaml`:

```yaml
decision_policy:
  mode: autonomous
  reasoning: extended_thinking
  log_all: true
```

### How Decisions Are Made

1. **Critical decisions** (research direction, methodology, theoretical claims, paper scope):
   - Use extended thinking (highest reasoning level)
   - Make the decision immediately -- no human escalation
   - Log in `decisions_made` in `status.yaml` with date, decision, and rationale

2. **Routine decisions** (formatting, organization, naming, section ordering):
   - Decide without logging
   - Proceed immediately

### Decision Log Format in status.yaml

```yaml
decisions_made:
  - date: 2026-03-07
    decision: "Target NeurIPS 2026 as venue"
    rationale: "Strong fit for work bridging theory and empirical LLM evaluation"
  - date: 2026-03-09
    decision: "Focus literature review on TC0/NC1 expressiveness bounds"
    rationale: "Most direct connection to transformer architecture limitations"
```

### When Decisions Go Wrong

If a decision leads to a dead end (experiment doesn't work, theoretical approach is flawed), the agent should:

1. Log the failed approach as a decision: `"Abandoned X approach because Y"`
2. Use extended thinking to evaluate alternatives
3. Choose the best alternative and proceed
4. Update `current_focus` and `next_steps` in `status.yaml`

There is no backtracking to ask a human. The agent pivots and continues.

---

## Cross-Reference Index

| Topic | Document |
|-------|----------|
| Server setup, daemons, API keys | [Infrastructure](INFRASTRUCTURE.md) |
| Budget allocation, concurrent capacity | [Scaling Strategy](SCALING.md) |
| Project configuration | `config.yaml` in repo root |
| Budget tracking | `budget.yaml` in repo root |
| Agent definitions | `.claude/agents/` (researcher, writer, reviewer) |
| CLI commands | `.claude/commands/` (new-project, research, write-paper) |
| Project-specific instructions | `projects/<name>/CLAUDE.md` |
| Repository conventions | `CLAUDE.md` in repo root |
