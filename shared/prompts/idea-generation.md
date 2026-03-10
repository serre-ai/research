# Idea Generation Prompt

## Objective

Brainstorm and evaluate potential research directions, producing a ranked list of structured ideas ready for brief-writing. Ideas should be novel, feasible within our constraints, and complementary to the existing project portfolio.

## Input

- **Current portfolio**: List of active and completed projects (from orchestrator)
- **Recent literature**: Key findings from literature surveys conducted so far
- **Target venues**: Which conferences/journals are we targeting?
- **Constraints**: Budget, timeline, compute, and expertise boundaries
- **Optional focus area**: A specific subfield or phenomenon to explore

## Process

### Step 1: Divergent Generation
Generate 15-20 raw ideas without filtering. Draw from:
- Gaps identified in literature reviews
- Combinations of techniques from different subfields
- Scaling up/down existing results to new regimes
- Transferring methods from adjacent fields
- Challenging widely-held assumptions
- Negative results that deserve explanation
- Practical problems that lack theoretical understanding
- Theoretical results that lack empirical validation

### Step 2: Initial Filter
Discard ideas that:
- Have already been done (check recent literature carefully)
- Are clearly infeasible within our constraints
- Have no plausible path to a compelling paper
- Duplicate an active project in the portfolio

### Step 3: Structured Evaluation
For each surviving idea (aim for 5-10), produce:

```markdown
## Idea [N]: [Title]

### One-Sentence Summary
[What is the core claim or contribution?]

### Hypothesis
[Testable, falsifiable statement. Format: "We hypothesize that X because Y, which predicts Z."]

### Novelty Assessment
- **What's new**: [What hasn't been done before?]
- **Closest prior work**: [Most similar existing paper and how this differs]
- **Novelty level**: Incremental / Moderate / Significant / Paradigm-shifting

### Feasibility
- **Technical risk**: Low / Medium / High — [Why?]
- **Resource requirements**: [Estimated compute, data, API costs]
- **Timeline**: [Weeks to minimum viable paper]
- **Key dependency**: [What must go right for this to work?]

### Venue Fit
- **Best venue**: [Which conference/journal and why]
- **Review angle**: [How would reviewers likely perceive this?]
- **Expected score range**: [Borderline / Competitive / Strong]

### Portfolio Complementarity
- **Overlap with existing projects**: [None / Some / High — specifics]
- **Skill reuse**: [Which capabilities from other projects transfer?]
- **Strategic value**: [Does this open new research directions? Build reputation in a new area?]

### Sketch of Approach
[3-5 bullet points outlining how the research would proceed]

### Risk Mitigation
[What's the fallback if the main hypothesis fails?]
```

### Step 4: Ranking
Rank the ideas by a weighted score:
- Novelty (30%): How new and surprising is the contribution?
- Feasibility (25%): Can we actually do this well?
- Impact (25%): Would the community care?
- Strategic fit (20%): Does it complement our portfolio and goals?

## Output

Save to `notes/idea-generation-<date>.md` in the relevant project or in a general `notes/` directory.

For the top 3 ideas, note whether they should become new projects (create a BRIEF.md) or be folded into an existing project.

## Quality Criteria

- At least 5 fully structured ideas
- Each idea has a testable hypothesis (not just a topic)
- Novelty assessment references specific prior work
- Feasibility estimates are honest, not optimistic
- At least one high-risk/high-reward idea and one safe/incremental idea
- No idea duplicates an existing project in the portfolio
