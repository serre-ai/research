# Scaling Strategy

This document covers the economics and capacity planning for the Serre AI research platform: how much projects cost, how many can run concurrently, and how to grow from 1 project to 6+.

Related documents:
- [Research Operations](OPERATIONS.md) -- project lifecycle, sessions, monitoring
- [Infrastructure and Deployment](INFRASTRUCTURE.md) -- server setup, daemons, API keys

---

## Table of Contents

1. [Resource Model](#resource-model)
2. [Budget Allocation by Phase](#budget-allocation-by-phase)
3. [Concurrent Project Capacity](#concurrent-project-capacity)
4. [Budget Scaling Tiers](#budget-scaling-tiers)
5. [Phased Ramp-Up Plan](#phased-ramp-up-plan)
6. [Rate Limit Management](#rate-limit-management)
7. [Session Scheduling Strategies](#session-scheduling-strategies)
8. [Worktree Resource Model](#worktree-resource-model)
9. [GPU Compute Budgeting](#gpu-compute-budgeting)
10. [Cost Per Paper Estimate](#cost-per-paper-estimate)
11. [When to Add Infrastructure](#when-to-add-infrastructure)
12. [Efficiency Metrics](#efficiency-metrics)

---

## Resource Model

Every project consumes three types of resources: API tokens, compute time, and human attention. The dominant cost is API tokens.

### API Token Consumption by Activity

| Activity | Tokens/Session (est.) | Sessions/Day | Daily Cost (est.) |
|----------|-----------------------|-------------|-------------------|
| Literature search and reading | 100K-200K | 2-3 | $3-5 |
| Note-taking and synthesis | 50K-100K | 1-2 | $1-2 |
| Framework/theory development | 150K-300K | 1-2 | $3-5 |
| Paper writing (drafting) | 200K-400K | 2-3 | $8-12 |
| Paper revision | 150K-300K | 2-3 | $6-10 |
| Experiment design and coding | 100K-200K | 1-2 | $3-5 |
| API-based model evaluation | 50K-100K + eval costs | 1-2 | $5-8 |
| Review and self-critique | 100K-200K | 1 | $2-4 |

**Note:** These estimates assume a mix of Claude Opus (for critical reasoning) and Claude Sonnet (for routine tasks). With Claude Code Max accounts, many of these costs are absorbed by the subscription. Direct API costs apply only when using the Claude Agent SDK outside of Max sessions.

### Cost Structure

The platform has two distinct cost channels:

1. **Claude Code Max subscriptions** -- Fixed monthly cost, unlimited usage within sessions. Currently 2 accounts.
2. **API key usage** -- Pay-per-token for Claude Agent SDK programmatic sessions, Firecrawl, and any other APIs.

For most research work done through Claude Code Max sessions, the marginal API cost is zero. The estimates above apply when using direct API calls (e.g., automated evaluation pipelines, batch processing).

---

## Budget Allocation by Phase

### Per-Project Monthly Cost by Phase

| Phase | API Costs | Compute Costs | Services | Total/Month |
|-------|-----------|---------------|----------|-------------|
| Research (literature review) | $60-100 | $0 | $20-30 (Firecrawl) | $80-130 |
| Research (framework) | $80-120 | $0 | $10-15 | $90-135 |
| Drafting | $150-250 | $0 | $5-10 | $155-260 |
| Revision | $120-200 | $0 | $5 | $125-205 |
| Experiments (API-only) | $100-180 | $0 | $10 | $110-190 |
| Experiments (GPU) | $50-80 | $50-200 | $10 | $110-280 |
| Final/Camera-ready | $30-60 | $0 | $0 | $30-60 |

### Monthly Budget Allocation Template

For a $1,000/month budget with 2 active projects:

| Category | Allocation | Notes |
|----------|-----------|-------|
| Project 1 (primary) | $400-500 | Higher allocation for project closer to deadline |
| Project 2 (secondary) | $250-350 | Lower allocation for earlier-phase project |
| Firecrawl / web services | $50-75 | Shared across all projects |
| GPU compute reserve | $50-100 | Only used during experiment phases |
| Buffer (contingency) | $50-100 | Absorbs spikes, covers unexpected costs |
| **Total** | **$1,000** | |

---

## Concurrent Project Capacity

### Capacity Formula

```
Max concurrent projects = floor(Monthly budget / Avg cost per project per month)
```

Where:
- Average cost per project per month varies by phase mix
- A project in research phase costs ~$100/month
- A project in drafting phase costs ~$200/month
- A project in experiment+drafting phase costs ~$250/month
- Weighted average across a typical phase mix: ~$150-200/month

### Capacity by Budget

| Monthly Budget | Max Projects (conservative) | Max Projects (aggressive) | Recommended |
|----------------|---------------------------|--------------------------|-------------|
| $1,000 | 3 | 5 | 2-3 |
| $2,000 | 6 | 10 | 4-6 |
| $3,000 | 10 | 15 | 6-8 |

**Conservative** assumes all projects are in active drafting/experiment phases. **Aggressive** assumes most are in lighter research or revision phases. **Recommended** accounts for budget spikes, GPU compute needs, and maintaining quality.

### Constraint: Claude Code Max Accounts

With 2 Max accounts, the practical concurrency limit is 2 simultaneous interactive sessions. This does not limit the total number of projects -- it limits how many can receive attention at the same moment.

The orchestrator works around this by cycling sessions:

```
Time 0:00  - Session A (reasoning-gaps) on Account 1
             Session B (scaling-laws) on Account 2
Time 0:45  - Session A ends, Session C (alignment-tax) starts on Account 1
             Session B continues
Time 1:00  - Session B ends, Session D (reasoning-gaps again) on Account 2
```

With 30-60 minute sessions and 2 accounts, each project can receive 2-4 sessions per day, which is sufficient for steady progress.

---

## Budget Scaling Tiers

### Tier 1: $1,000/month (Current)

**What you get:**
- 2-3 active projects
- 1 project in heavy drafting/experiments, 1-2 in lighter research phases
- ~$50/month for Firecrawl
- ~$50-100/month GPU compute reserve
- 2 Claude Code Max accounts for interactive sessions

**Typical portfolio:**
| Project | Phase | Monthly Cost |
|---------|-------|-------------|
| reasoning-gaps | research/drafting | $400 |
| (new project) | research | $150 |
| Buffer + services | -- | $450 |

**Constraints:**
- Cannot run GPU experiments on more than 1 project simultaneously
- Limited to ~4-6 total sessions per day across all projects
- New projects must wait for budget headroom

### Tier 2: $2,000/month

**What you get:**
- 4-6 active projects
- 2 projects in heavy phases, 2-4 in lighter phases
- ~$75/month for Firecrawl (heavier usage)
- ~$200/month GPU compute reserve
- Consider adding a 3rd Claude Code Max account

**Typical portfolio:**
| Project | Phase | Monthly Cost |
|---------|-------|-------------|
| Project A | drafting | $300 |
| Project B | experiments | $350 |
| Project C | research | $150 |
| Project D | research | $150 |
| Project E | revision | $200 |
| Buffer + services | -- | $850 |

**Unlocks:**
- Can run 2 GPU experiment batches per month
- Can maintain a steady pipeline of projects at different phases
- Enough headroom for deadline sprints

### Tier 3: $3,000/month

**What you get:**
- 6-8 active projects
- Full pipeline: 2-3 in research, 2-3 in drafting, 1-2 in revision/final
- ~$100/month for web services
- ~$300-400/month GPU compute reserve
- 3-4 Claude Code Max accounts recommended
- Consider a dedicated VPS for the orchestrator (~$40/month)

**Typical portfolio:**
| Project | Phase | Monthly Cost |
|---------|-------|-------------|
| Project A | final | $100 |
| Project B | revision | $200 |
| Project C | drafting | $300 |
| Project D | drafting | $300 |
| Project E | experiments | $350 |
| Project F | research | $150 |
| Project G | research | $150 |
| Project H | research | $100 |
| Buffer + services + infra | -- | $1,350 |

**Unlocks:**
- True paper pipeline: always have something near submission
- Can explore riskier ideas (higher project failure rate is acceptable)
- Enough GPU budget for serious experimental work
- Dedicated infrastructure for reliability

---

## Phased Ramp-Up Plan

### Month 1: Foundation (2 projects, $1,000 budget)

**Goals:**
- Validate the platform workflow end-to-end
- Get one project (reasoning-gaps) through research into drafting
- Start scoping a second project

**Actions:**
- Run reasoning-gaps through literature review and framework development
- Identify and scope 1-2 candidate second projects
- Start second project in research phase
- Tune session scheduling (how long, how often)
- Establish the PR review cadence

**Budget allocation:**
| Item | Amount |
|------|--------|
| reasoning-gaps | $500 |
| Second project | $200 |
| Services + buffer | $300 |

### Month 2: Expansion (3-4 projects, $1,000-1,500 budget)

**Goals:**
- reasoning-gaps reaches drafting or experiments
- Second project is in active research
- Start 1-2 additional projects
- Consider budget increase if justified

**Actions:**
- Begin paper drafting for reasoning-gaps
- If experiments needed, provision first GPU instance
- Start 1-2 new projects from idea pipeline
- Evaluate whether $1,000 is sufficient or increase to $1,500

**Budget allocation:**
| Item | Amount |
|------|--------|
| reasoning-gaps (drafting) | $400 |
| Project 2 (research) | $200 |
| Project 3 (research) | $150 |
| Project 4 (scoping) | $50 |
| Services + buffer | $200-700 |

### Month 3: Steady State (4-6 projects, $1,500-2,000 budget)

**Goals:**
- reasoning-gaps in revision or submitted
- 2-3 projects in active research/drafting
- Healthy idea pipeline with 2-3 scoped candidates
- Proven session scheduling and budget allocation

**Actions:**
- Submit reasoning-gaps (if ready) or enter revision
- Promote research-phase projects to drafting as they mature
- Add new projects as budget allows
- Upgrade to $2,000 budget if running 5+ projects

### Month 4-6: Pipeline (5-8 projects, $2,000-3,000 budget)

**Goals:**
- Always have 1-2 projects near submission
- Continuous pipeline: new projects entering research as others submit
- 1-2 papers submitted or in final preparation
- Established rhythm of weekly PR reviews and monthly portfolio assessment

---

## Rate Limit Management

### The Problem

When multiple sessions are active simultaneously, they compete for API rate limits. With 2 Max accounts, this is manageable. At 4+ accounts or heavy programmatic API usage, rate limits become a real constraint.

### Strategies

#### 1. Stagger Session Start Times

Instead of starting all sessions at the same time, space them out:

```
Account 1: Session starts at :00, :30
Account 2: Session starts at :15, :45
```

This naturally distributes API load across time.

#### 2. Round-Robin Scheduling

The orchestrator assigns sessions to accounts in round-robin fashion, ensuring no single account is overloaded:

```
Cycle 1: Account 1 -> reasoning-gaps, Account 2 -> scaling-laws
Cycle 2: Account 1 -> alignment-tax, Account 2 -> reasoning-gaps
```

#### 3. Phase-Aware Scheduling

Schedule lighter phases during high-contention periods and heavier phases during quiet periods:

- **Morning:** Research/literature sessions (lighter API usage)
- **Afternoon:** Drafting sessions (heavier, but only 1-2 at a time)
- **Night:** Batch experiment sessions (dedicated API access)

#### 4. Model Selection

Use cheaper, faster models for tasks that don't need top reasoning:

| Task | Model | Cost Ratio |
|------|-------|-----------|
| Literature search queries | Claude 4 Sonnet | 1x |
| Note summarization | Claude 4 Sonnet | 1x |
| Framework reasoning | Claude 4 Opus | 5x |
| Paper writing | Claude 4 Opus | 5x |
| Formatting, cleanup | Claude 4 Sonnet | 1x |

This reduces both cost and rate limit pressure.

### Rate Limit Monitoring

Track request rates and back off proactively:

```
If requests/minute > 80% of rate limit:
  - Delay next session start by 5 minutes
  - Log a warning in orchestrator output

If requests/minute > 95% of rate limit:
  - Pause all sessions except highest priority
  - Alert for human review
```

---

## Session Scheduling Strategies

### Strategy 1: Time-Slicing

Each project gets a fixed time window, rotating through projects in order.

```
09:00-09:45  reasoning-gaps
09:45-10:30  scaling-laws
10:30-11:15  alignment-tax
11:15-12:00  reasoning-gaps (again)
...
```

**Pros:** Fair, predictable, easy to implement
**Cons:** Doesn't account for project urgency or phase intensity

### Strategy 2: Phase-Based Priority

Projects in later phases (closer to submission) get more sessions.

| Phase | Priority Weight | Sessions/Day (with 2 accounts) |
|-------|----------------|-------------------------------|
| Final | 5x | 4-6 |
| Revision | 4x | 3-5 |
| Drafting | 3x | 2-4 |
| Research | 2x | 1-3 |
| Scoping | 1x | 0-1 |

**Pros:** Focuses resources where they matter most (near deadlines)
**Cons:** Can starve early-phase projects

### Strategy 3: Hybrid (Recommended)

Combine time-slicing with priority weighting:

1. **Base allocation:** Every active project gets at least 1 session per day
2. **Priority bonus:** Projects in later phases or approaching deadlines get additional sessions
3. **Burst mode:** When a project hits a milestone (e.g., completing literature review), it gets a burst of sessions to capitalize on momentum
4. **Cool-down:** After a session, wait at least 15 minutes before the next session for the same project (allows status file updates to propagate)

**Implementation in the scheduling loop:**

```
For each cycle:
  1. List all active projects
  2. Score each: base_priority(phase) + deadline_bonus + momentum_bonus
  3. Sort by score descending
  4. Start sessions for top N (where N = available accounts)
  5. Wait for sessions to complete
  6. Record session metrics
  7. Sleep for cool-down interval
```

---

## Worktree Resource Model

### Disk Usage per Project

| Phase | Typical Disk Usage | Growth Rate |
|-------|-------------------|-------------|
| Research | 100-150 MB | +5 MB/week (notes, references) |
| Drafting | 150-300 MB | +20 MB/week (LaTeX, figures) |
| Experiments | 200-500 MB | +50 MB/week (results, data) |
| Revision | 200-400 MB | +5 MB/week (minor changes) |
| Final | 200-400 MB | Stable |

### Git Performance with N Worktrees

Git worktrees share the same object store (`.git/`), so the performance impact of adding worktrees is minimal for typical operations:

| Worktrees | `git status` | `git log` | `git worktree list` | Notes |
|-----------|-------------|-----------|---------------------|-------|
| 1-3 | <100ms | <100ms | <50ms | No noticeable impact |
| 4-8 | <100ms | <100ms | <100ms | Negligible impact |
| 10-15 | <200ms | <100ms | <200ms | Slight overhead |
| 20+ | <500ms | <200ms | <500ms | Consider cleanup |

The main concern is disk space, not git performance. The shared object store means that common files are not duplicated -- only changed files in each worktree consume additional space.

### Cleanup Policy

```
Active project:     Keep worktree alive during sessions, remove between sessions
Paused project:     Remove worktree, recreate when resumed
Completed project:  Remove worktree, merge branch to main, archive
```

---

## GPU Compute Budgeting

### Cost per Experiment Type

| Experiment | GPU | Duration | Cost |
|-----------|-----|----------|------|
| Evaluate 1 open-source model (7B) on benchmark | A10G (24GB) | 1-2 hours | $1-2 |
| Evaluate 1 open-source model (70B) on benchmark | A100 (80GB) | 2-4 hours | $3-5 |
| Evaluate 5 models (mixed sizes) on full benchmark | A100 (80GB) | 8-16 hours | $10-20 |
| Fine-tune a small model (7B) for probing | A100 (80GB) | 4-8 hours | $5-10 |
| Full experimental suite for a paper | Mixed | 20-40 hours | $25-50 |

### Amortized GPU Cost per Paper

| Paper Type | Experiments Needed | GPU Budget |
|-----------|-------------------|-----------|
| Theory-focused (minimal experiments) | 1-2 small batches | $10-30 |
| Empirical (API-only models) | 0 GPU batches | $0 |
| Empirical (open-source models) | 3-5 batches | $30-80 |
| Heavy experimental | 5-10 batches | $80-200 |

### GPU Budget Rules

1. **Reserve, don't pre-spend:** Allocate GPU budget in `budget.yaml` but only spend when experiments are ready
2. **Start small:** Run pilot experiments on cheaper GPUs (A10G) before scaling to A100
3. **Batch experiments:** Combine multiple model evaluations into a single session to amortize instance startup time
4. **Terminate immediately:** GPU instances billing is per-second or per-minute -- don't leave instances running
5. **Use spot instances:** vast.ai spot instances can be 50-70% cheaper than on-demand

---

## Cost Per Paper Estimate

### Total Lifecycle Cost: Idea to Submission

| Phase | Duration | Monthly Cost | Phase Total |
|-------|----------|-------------|-------------|
| Scoping | 0.5 weeks | -- | $20-40 |
| Research (literature) | 2-3 weeks | $80-130 | $120-200 |
| Research (framework) | 1-2 weeks | $90-135 | $90-135 |
| Drafting | 2-3 weeks | $155-260 | $200-400 |
| Experiments (if needed) | 1-3 weeks | $110-280 | $110-280 |
| Revision | 1-2 weeks | $125-205 | $125-205 |
| Final | 0.5 weeks | $30-60 | $15-30 |
| **Total** | **8-14 weeks** | | **$680-1,290** |

### Summary by Paper Type

| Paper Type | Timeline | Total Cost |
|-----------|----------|-----------|
| Theory paper (no experiments) | 8-10 weeks | $500-800 |
| Theory + light experiments | 10-12 weeks | $700-1,000 |
| Empirical (API-only) | 10-12 weeks | $800-1,100 |
| Empirical (GPU experiments) | 12-14 weeks | $900-1,300 |
| Heavy experimental | 14-16 weeks | $1,100-1,500 |

### Cost per Page

A typical NeurIPS paper is 8-10 pages (main body) plus appendix.

| Metric | Value |
|--------|-------|
| Cost per main-body page | $80-130 |
| Cost per appendix page | $20-40 (lower since it's supplementary) |
| Total cost per page (averaged) | $50-90 |

---

## When to Add Infrastructure

### Thresholds for Server Upgrade

| Trigger | Current State | Action |
|---------|--------------|--------|
| Disk usage >70% on worktree partition | 50 GB disk | Upgrade to 100 GB or add volume |
| >4 concurrent projects need daily sessions | 2 Max accounts | Add 3rd Max account |
| Orchestrator CPU consistently >80% | 2-core VPS | Upgrade to 4-core |
| Session scheduling backed up (projects waiting >24h) | 2 accounts | Add account or extend session hours |
| GPU experiments blocking project progress | On-demand provisioning | Pre-provision a reserved instance |
| Budget >80% for 3 consecutive months | $1K budget | Increase to $2K |

### Infrastructure Cost at Each Tier

| Tier | VPS | Max Accounts | GPU Reserve | Services | Total Fixed |
|------|-----|-------------|-------------|----------|-------------|
| Starter ($1K) | $0 (local) | 2 x $100 = $200 | On-demand | $50 | $250/mo fixed |
| Growth ($2K) | $30/mo | 3 x $100 = $300 | On-demand | $75 | $405/mo fixed |
| Scale ($3K) | $50/mo | 4 x $100 = $400 | $100 reserve | $100 | $650/mo fixed |

**Note:** Claude Code Max pricing is illustrative. Actual subscription costs depend on the current plan pricing.

### Decision Framework

Ask these questions quarterly:

1. **Are projects waiting for sessions?** If yes, add a Max account.
2. **Are experiments blocked on GPU availability?** If yes, increase GPU budget or pre-provision.
3. **Is the orchestrator dropping sessions or running slowly?** If yes, upgrade the VPS.
4. **Are we consistently spending >80% of budget?** If yes, either increase budget or reduce project count.
5. **Are we consistently spending <50% of budget?** If yes, either add projects or reduce budget.

---

## Efficiency Metrics

Track these metrics to understand whether the platform is operating well.

### Tokens per Useful Output

| Output | Tokens Used (est.) | Tokens per Page |
|--------|-------------------|-----------------|
| Literature survey (10 pages of notes) | 500K-1M | 50K-100K |
| Paper section (2 pages) | 200K-500K | 100K-250K |
| Experiment code (500 lines) | 100K-200K | 200-400 tokens/line |
| Review cycle (1 round) | 200K-400K | N/A |

**Target efficiency:** <200K tokens per page of final paper content. If significantly higher, the agent may be thrashing or the instructions may be ambiguous.

### Cost per Unit of Output

| Output | Target Cost | Warning Threshold |
|--------|------------|------------------|
| 1 page of paper text | $80-130 | >$200 |
| 1 literature survey note | $5-10 | >$20 |
| 1 experiment run (API-based) | $2-5 | >$10 |
| 1 figure | $10-20 | >$40 |
| 1 review-revise cycle | $40-80 | >$150 |

### Project Health Metrics

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Cost per week | $50-150 | >$200 | >$300 |
| Commits per week | 20-40 | <10 or >80 | <5 or >100 |
| Phase duration | On schedule per BRIEF.md | >50% over timeline | >100% over timeline |
| Confidence score trend | Increasing | Flat for >2 weeks | Decreasing |
| Decision log entries per week | 2-5 | 0 (not logging) | >15 (indecisive) |
| PRs merged per week | 1-2 | 0 for >2 weeks | N/A |

### Monthly Efficiency Report Template

```
Month: YYYY-MM
Budget: $X spent / $Y allocated (Z%)

Per-Project Summary:
| Project | Phase | Cost | Commits | PRs | Confidence | Status |
|---------|-------|------|---------|-----|------------|--------|
| ...     | ...   | ...  | ...     | ... | ...        | ...    |

Aggregate Metrics:
- Total tokens consumed: X
- Cost per page of paper output: $Y
- Projects advanced to next phase: N
- Papers submitted: N
- GPU hours used: X ($Y)

Observations:
- [What went well]
- [What needs improvement]
- [Adjustments for next month]
```

---

## Projection: Annual Research Output

At steady state, the platform can be expected to produce:

| Budget Tier | Projects/Year | Papers Submitted | Papers Accepted (est. 30%) |
|-------------|--------------|-----------------|---------------------------|
| $1,000/mo ($12K/yr) | 6-8 | 4-6 | 1-2 |
| $2,000/mo ($24K/yr) | 12-16 | 8-12 | 2-4 |
| $3,000/mo ($36K/yr) | 18-24 | 12-16 | 4-5 |

These projections assume:
- ~2 month average time from project start to submission
- ~25% of projects are abandoned (idea doesn't work out)
- ~30% acceptance rate at top venues (NeurIPS, ICML, ICLR, etc.)
- Steady-state operation with a healthy project pipeline

The cost per accepted paper at a top venue works out to roughly **$6,000-8,000** -- less than a single graduate student month at most institutions.
