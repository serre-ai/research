# Experiment Design Prompt

## Objective

Design a rigorous experiment to test a specific hypothesis. The output is a complete experimental plan that can be executed without further design decisions — every choice is made and justified upfront.

## Input

- **Hypothesis**: The specific, testable claim from BRIEF.md
- **Available resources**: Compute budget, API access, datasets, time
- **Prior results**: Any preliminary experiments or literature benchmarks to build on
- **Constraints**: Maximum cost, timeline, ethical restrictions

## Design Process

### Step 1: Operationalize the Hypothesis
Convert the hypothesis into measurable predictions:
- **Independent variable(s)**: What are you manipulating? (e.g., problem complexity, model size, prompt strategy)
- **Dependent variable(s)**: What are you measuring? (e.g., accuracy, failure rate, response time)
- **Control variables**: What must be held constant? (e.g., temperature, random seed, prompt format)
- **Prediction**: "If H is true, we expect [metric] to [increase/decrease/remain stable] as [variable] changes, with effect size approximately [X]."

### Step 2: Choose Experimental Components

#### Models
For each model, specify:
- Name and version (pin exact version — models change)
- Access method (API, local weights, specific checkpoint)
- Why this model is included (represents a family, scale point, or architectural variant)
- Include at least 3 models spanning different families or scales

#### Datasets / Benchmarks
For each dataset:
- Source and version
- Size (number of instances for train/val/test)
- Known properties (difficulty distribution, domain, biases)
- Preprocessing steps
- Why this dataset tests the hypothesis

#### Baselines
For each baseline:
- Description of the method
- Why it's a fair comparison
- Source (prior paper, our implementation, library)
- Expected performance (from literature or preliminary runs)

#### Metrics
- **Primary metric**: The single metric that determines if the hypothesis is supported. Define precisely including edge cases.
- **Secondary metrics**: Additional measurements that enrich the analysis.
- **Statistical tests**: Which tests will be used to assess significance (e.g., paired bootstrap, Wilcoxon signed-rank, permutation test)?
- **Effect size measure**: Cohen's d, relative improvement, etc.
- **Significance threshold**: alpha = 0.05 unless justified otherwise.

### Step 3: Design the Protocol

```markdown
## Experimental Protocol

### Setup
- [Environment: Python version, key libraries, hardware]
- [Random seeds: list specific seeds for reproducibility]
- [API configuration: temperature, max_tokens, system prompt]

### Procedure
1. [Data preparation: exact steps to prepare inputs]
2. [Execution: how each model is run on each input]
3. [Collection: how outputs are captured and stored]
4. [Scoring: how raw outputs are converted to metrics]
5. [Aggregation: how per-instance metrics become summary statistics]
6. [Analysis: statistical tests and visualization]

### Ablations
For each ablation:
- What component is removed or changed?
- What does this test?
- Expected outcome if the component matters / doesn't matter

### Controls
- [Sanity checks: trivial cases where the answer is known]
- [Ceiling performance: human or oracle baseline]
- [Floor performance: random or majority baseline]
```

### Step 4: Plan for Failure Modes

- **If the hypothesis is confirmed**: What additional analysis strengthens the claim?
- **If the hypothesis is refuted**: What follow-up experiments narrow down why?
- **If results are ambiguous**: What would disambiguate? More data? Different metrics?
- **If compute budget is exceeded mid-experiment**: Priority ordering of which runs to complete first.

### Step 5: Cost Estimation

| Component | Quantity | Unit Cost | Total Cost |
|-----------|----------|-----------|------------|
| [Model A API calls] | [N] | [$X/1K tokens] | [$Y] |
| [Model B API calls] | [N] | [$X/1K tokens] | [$Y] |
| [GPU compute] | [N hours] | [$X/hour] | [$Y] |
| **Total** | | | **$Z** |

Verify total is within project budget from `status.yaml` and platform budget from `config.yaml`.

## Output Format

```markdown
# Experiment Plan: [Experiment Name]

## Hypothesis
[Formal statement]

## Prediction
[Measurable prediction]

## Setup
[Models, datasets, baselines, metrics — fully specified]

## Protocol
[Step-by-step execution plan]

## Ablations
[List of ablation experiments]

## Expected Results
[What results would confirm/refute/be ambiguous]

## Analysis Plan
[Statistical tests, visualizations, failure case analysis]

## Cost Estimate
[Budget table]

## Timeline
[Day-by-day or week-by-week execution plan]
```

Save to `experiments/<experiment-name>/README.md` in the project directory using the experiment template from `shared/templates/experiment/README.md`.

## Quality Criteria

- Every design choice is justified (not arbitrary)
- The experiment can distinguish between the hypothesis being true and false
- Baselines are appropriate and fair
- Statistical analysis is pre-registered (chosen before seeing results)
- Cost is estimated and within budget
- A different agent could execute this plan without making additional design decisions
