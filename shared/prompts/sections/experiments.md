# Experiments Section Guide

## Purpose
Test every prediction from the framework. The reader should finish this section
knowing which predictions held, which failed, and what the numbers actually are.

## Structure

### Setup (1 paragraph)
Cover all logistics in one dense paragraph: models tested, dataset/benchmark
details, conditions (e.g., direct vs. CoT), sample sizes, evaluation metrics,
and compute budget. Point to the appendix for full details. The reader needs
enough to assess validity but not enough to be bored.

### Results by Prediction
Organize results around the predictions from the framework section, NOT around
individual experiments or tables. For each prediction:

1. **Restate the prediction** in one sentence.
2. **Show the result** with the specific number and confidence interval.
3. **Interpret** — does this confirm or refute the prediction? Why?

This structure makes the paper's argument legible. The reader follows a thread:
theory predicts X, experiment shows Y, interpretation connects them.

### Surprising Results
If any prediction failed or a result was unexpected, give it extra space.
Explain what you expected, what happened, and your best hypothesis for why.
Honest surprises are more interesting than clean confirmations.

### Synthesis (1-2 paragraphs)
Summarize: of N predictions, how many confirmed? What's the overall picture?
Which findings are strongest (tightest CIs, largest effects)? Which are weakest?

## Rules

- **State each prediction BEFORE showing results.** Never present a number
  before the reader knows what to expect.
- **Never enumerate every number from a table.** Highlight the 2-3 most
  interesting cells. The table exists for completeness; the prose exists for
  narrative.
- **Every figure/table reference must include the takeaway.** Write
  "Table 2 shows B4 achieves 100% accuracy (P-class), confirming Theorem 1"
  — never "Results are in Table 2."
- **Include confidence intervals** for all quantitative claims.
- **Target ~30% of main text** (per paper-style.yaml) — this is the largest
  section.

## Figure and Table Guidance
- Use bar charts for discrete comparisons (tasks, models, conditions).
- Use heatmaps for model-by-task grids.
- Caption every figure to be self-contained (readable without main text).
- Bold the best result in each table column.
- See `paper-style.yaml` for palette and formatting details.

## Common Mistakes
- Organizing by experiment ("Experiment 1, Experiment 2") instead of by
  prediction — loses the narrative thread.
- Saying "as shown in Table 3" without stating what Table 3 shows.
- Reporting numbers without CIs or significance tests.
- Spending a paragraph on a result that simply confirms the obvious.
- Burying a surprising negative result in a subordinate clause.
