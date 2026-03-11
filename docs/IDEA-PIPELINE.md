# Research Idea Pipeline

This document defines how research ideas are generated, evaluated, prioritized, and graduated into active projects. The pipeline is the lifeblood of the research platform — a healthy pipeline ensures there is always a strong project ready to start when a slot opens.

## Sources of Ideas

### 1. Literature Gaps
The most reliable source of publishable research ideas. Every literature review conducted for an active project should generate 2-3 idea candidates. When reading a paper, always ask:
- What did they not do that would be interesting?
- What assumption did they make that could be relaxed?
- What would happen if their method were applied to a different domain?
- What empirical question did they leave unanswered?

### 2. Cross-Project Discoveries
As the portfolio grows, connections between projects emerge. A theoretical framework from one project might apply to the empirical setting of another. A benchmark built for one study might reveal unexpected patterns. Cross-pollination ideas are often the most novel because they combine expertise areas that are rarely combined.

### 3. Conference Proceedings and Workshops
Review accepted paper lists from NeurIPS, ICML, ICLR, ACL within 2 weeks of publication. Look for:
- Trends: what topics had 5+ papers? That area is active and publishable.
- Outliers: what single paper introduced a new direction? Early follow-up work has high impact.
- Workshop papers: what ideas were too preliminary for the main conference but show promise?

### 4. Trending Topics and Community Discussion
Monitor:
- arXiv daily listings in cs.LG, cs.CL, cs.AI, stat.ML
- Twitter/X ML research community (key accounts, trending threads)
- r/MachineLearning on Reddit
- Key research group blogs (Google DeepMind, Anthropic, OpenAI, Meta FAIR, Microsoft Research)

### 5. Failure Analysis
When a project is abandoned or receives poor reviews, the failure itself is data. Ask:
- What did we learn that is not yet published?
- Can the negative result be framed as a contribution?
- Does the failure suggest a different question that would be more tractable?

### 6. Operator Interest and Strategic Direction
The platform operator provides high-level direction on which research areas to prioritize. These preferences filter and weight the pipeline but do not exclusively determine it. Research impact sometimes comes from unexpected directions.

## Idea Capture Format

Every idea is captured as a structured one-pager before entering the backlog. The format is defined in the backlog YAML schema, but should initially be drafted as a brief document.

### Required Fields

```yaml
name: "<slug>"                          # Unique identifier, lowercase-hyphenated
title: "<Descriptive paper title>"
area: "<Research area>"                 # e.g., "LLM Capabilities", "AI Safety"
type: theory | empirical | survey | tool
venue_targets:
  - "<Primary venue>"
  - "<Backup venue>"
estimated_months: <number>
brief_description: |
  <2-3 sentence description of the proposed research>
key_hypotheses:
  - "<Hypothesis 1>"
  - "<Hypothesis 2>"
novelty_score: <1-5>                    # 1=incremental, 5=paradigm-shifting
feasibility_score: <1-5>               # 1=very hard, 5=straightforward execution
impact_score: <1-5>                    # 1=niche interest, 5=field-wide impact
portfolio_fit: "<How it complements existing projects>"
status: idea | scoping | ready
```

### Optional Fields (added during scoping)
```yaml
related_work:                          # Key papers identified
  - "<citation>"
required_resources:                    # API costs, compute, datasets
  estimated_cost_usd: <number>
  api_access_needed: [list]
  compute_requirements: "<description>"
risks:
  - "<Risk 1>"
  - "<Risk 2>"
scoping_notes: |
  <Notes from initial investigation>
```

## Evaluation Criteria

Each idea is evaluated on four dimensions, scored 1-5:

### Novelty (weight: 0.30)
- **1**: Minor extension of existing work; many similar papers exist
- **2**: Reasonable extension with some new angle; a few similar papers
- **3**: Clear novel contribution; no directly comparable published work
- **4**: Highly original; combines areas or questions not previously connected
- **5**: Potentially field-defining; introduces a new research direction

### Feasibility (weight: 0.25)
- **1**: Requires breakthroughs beyond current capability; may not be achievable
- **2**: Technically challenging; significant risk of failure; requires scarce resources
- **3**: Achievable with sustained effort; standard methods apply with non-trivial adaptation
- **4**: Clearly executable; main challenge is thoroughness, not feasibility
- **5**: Straightforward execution; could be completed quickly with existing tools

Feasibility specifically considers what an AI research agent can accomplish: API-based model evaluations, literature synthesis, mathematical reasoning, code writing, and LaTeX paper production. Ideas requiring large-scale training runs, wet-lab experiments, or proprietary data score lower.

### Impact (weight: 0.25)
- **1**: Very niche; interesting to fewer than 50 researchers
- **2**: Niche but solid; a small community would cite this
- **3**: Broadly relevant within a subfield; likely to get 20+ citations in 2 years
- **4**: Relevant across multiple subfields; likely to influence research directions
- **5**: Field-wide significance; changes how people think about a fundamental question

### Portfolio Fit (weight: 0.20)
- **1**: Completely unrelated to existing projects; no synergy
- **2**: Tangentially related; minor overlap in methods or domain
- **3**: Complements existing projects; shares literature or tools
- **4**: Strong synergy; builds directly on another project's findings or artifacts
- **5**: Essential complement; fills a critical gap in the portfolio (e.g., adds a missing project type)

## Prioritization Framework

### Composite Score
```
score = (novelty * 0.30) + (feasibility * 0.25) + (impact * 0.25) + (portfolio_fit * 0.20)
```

Maximum score: 5.0. Minimum for consideration: 2.5.

### Prioritization Tiers

| Tier | Score Range | Action |
|------|-----------|--------|
| **A (Launch)** | 4.0 - 5.0 | Start as soon as a project slot opens |
| **B (Ready)** | 3.0 - 3.9 | Scope further; launch if no A-tier ideas are available |
| **C (Hold)** | 2.5 - 2.9 | Keep in backlog; revisit monthly |
| **D (Retire)** | Below 2.5 | Remove from active backlog |

### Tie-Breaking Rules
When two ideas have similar composite scores:
1. Prefer the idea with a nearer venue deadline (urgency)
2. Prefer the idea with higher feasibility (probability of completion)
3. Prefer the idea that diversifies the portfolio type mix
4. Prefer the idea with higher novelty (upside potential)

## From Idea to Project: Graduation Criteria

An idea graduates from the backlog to an active project when ALL of the following are met:

1. **Composite score >= 3.5** (B+ tier or higher)
2. **Venue deadline alignment**: A suitable venue has a submission deadline 2-5 months away
3. **Resource availability**: Budget headroom exists; no more than 5 active projects running
4. **Scoping complete**: At minimum, 10 relevant papers identified, key hypothesis refined, and methodology sketched
5. **No portfolio conflict**: Does not duplicate an active project's contribution area
6. **Operator approval**: For the first 6 months, all project launches require explicit operator confirmation. After 6 months, the agent may auto-launch B+ tier ideas if resource constraints are met.

### Graduation Process
1. Move status from `idea` or `scoping` to `ready` in the backlog
2. Create project directory: `projects/<name>/`
3. Write `BRIEF.md` from the idea capture document (expanded)
4. Create `status.yaml` with initial state
5. Write project-specific `CLAUDE.md` with research standards and key decisions
6. Create branch: `research/<name>`
7. Update `docs/ideas/backlog.yaml` to mark the idea as `graduated`
8. Log the launch decision in `status.yaml`

## Idea Backlog Management

### Storage
All ideas are stored in `docs/ideas/backlog.yaml`. This is the single source of truth for the idea pipeline.

### Backlog Health Targets
- **Minimum 10 ideas** in the backlog at all times
- **At least 3 ideas** scored B-tier or above (ready for launch)
- **At least 4 different research areas** represented
- **At least 3 different project types** represented (theory, empirical, survey, tool)

### Monthly Idea Generation

On the first of each month, as part of the portfolio review, the agent conducts an idea generation session:

1. **Review recent literature**: Scan the past month's arXiv submissions in cs.LG, cs.CL, cs.AI for trends and gaps
2. **Review active projects**: What questions have emerged from ongoing work?
3. **Review killed/completed projects**: What follow-up directions exist?
4. **Brainstorm 5-10 new ideas**: Using extended thinking, generate research directions that are:
   - Timely (address a current gap or trend)
   - Feasible (executable by an AI research agent)
   - Novel (not a straightforward replication of existing work)
   - Diverse (span different areas and types)
5. **Score and add to backlog**: Evaluate each idea and add those scoring 2.5+ to `backlog.yaml`
6. **Re-score existing ideas**: Adjust scores based on new information (new related work published, resource changes, portfolio shifts)

### Idea Retirement

Remove an idea from the active backlog when:
- **6 months without action**: If an idea has sat at `idea` status for 6 months with no movement toward scoping, it is likely not compelling enough. Archive it.
- **Superseded**: A published paper (by anyone) covers the same ground. If the published work is incomplete, the idea may be modified rather than retired.
- **Consistently low scores**: If an idea has been re-scored 3+ times and never reaches B-tier, retire it.
- **Resource mismatch**: If the idea requires resources that are permanently unavailable (e.g., requires training large models and budget will never support that), retire it.

Retired ideas move to `docs/ideas/archive.yaml` with a retirement reason. They can be resurrected if circumstances change.

## Pipeline Metrics

Track monthly:
- **Ideas generated**: Number of new ideas added to the backlog
- **Ideas graduated**: Number of ideas that became active projects
- **Ideas retired**: Number of ideas removed from the backlog
- **Backlog depth**: Total ideas in backlog, by tier
- **Time-to-graduation**: Average time from idea capture to project launch
- **Graduation success rate**: Of graduated ideas, what percentage reach submission?
- **Idea source distribution**: Where are the best ideas coming from? (literature gaps, cross-project, trending topics, etc.)

These metrics inform whether the pipeline is healthy or whether idea generation needs to be accelerated.
