# Experiment: [Experiment Name]

**Date**: [YYYY-MM-DD]
**Project**: [project-name]
**Status**: [planned | running | complete | abandoned]
**Hypothesis**: [Which hypothesis from BRIEF.md does this test? e.g., H1, H2]

---

## Hypothesis

[Restate the specific hypothesis being tested in this experiment. Be precise about what outcome would confirm or refute it.]

## Setup

### Models
- [Model 1: name, version, size, access method (API / local)]
- [Model 2: ...]

### Datasets
- [Dataset 1: name, size, source, preprocessing applied]
- [Dataset 2: ...]

### Baselines
- [Baseline 1: description and why it's an appropriate comparison]
- [Baseline 2: ...]

### Metrics
- **Primary**: [Metric name — what it measures and why it's the right metric]
- **Secondary**: [Additional metrics for richer analysis]

### Hyperparameters
| Parameter | Value | Justification |
|-----------|-------|---------------|
| [param]   | [val] | [why]         |

### Compute Budget
- Estimated cost: $[X]
- Estimated runtime: [X hours/days]

## Procedure

1. [Step 1: Concrete action, e.g., "Generate benchmark instances with N=100,500,1000"]
2. [Step 2: e.g., "Run each model on all instances with temperature=0"]
3. [Step 3: e.g., "Compute accuracy, collect failure cases"]
4. [Step 4: e.g., "Statistical analysis: bootstrap confidence intervals, paired t-test vs baseline"]

## Expected Results

[What do you expect to see if the hypothesis is correct? What would refutation look like? Be specific about expected effect sizes and patterns.]

## Actual Results

[Fill in after running. Include key numbers, tables, or references to figures.]

### Summary Statistics
| Model | Metric 1 | Metric 2 | 95% CI |
|-------|----------|----------|--------|
| [...]  | [...]     | [...]     | [...]   |

### Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

## Analysis

[Interpretation of results. Did they confirm or refute the hypothesis? What patterns emerged? What's surprising? What are the limitations of this experiment?]

### Failure Cases
[Describe representative failure cases and what they reveal.]

### Confounds and Limitations
[What could explain the results other than the hypothesis? What would a stronger experiment look like?]

## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Run script | `scripts/[name].py` | Main experiment script |
| Raw data | `data/[name]/` | Unprocessed outputs |
| Results | `results/[name].json` | Aggregated metrics |
| Figures | `figures/[name].pdf` | Visualization of results |
| Log | `logs/[name].log` | Execution log |

## Decision Log

[Any decisions made during this experiment that affect interpretation.]

- [Date]: [Decision and rationale]
