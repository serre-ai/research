# Supplementary Materials: On the Reasoning Gaps of Large Language Models

## Overview

This package contains the complete evaluation code and task generators for
reproducing the experiments in "On the Reasoning Gaps of Large Language Models:
A Formal Characterization."

## Directory Structure

```
supplementary/
├── README.md              — This file
├── LICENSE                — MIT license
├── quickstart.ipynb       — Interactive notebook walkthrough
├── generate.py            — Task instance generator (all benchmarks)
├── analyze.py             — Analysis pipeline entry point (tables, figures)
├── requirements.txt       — Python package dependencies
├── code/
│   ├── evaluate.py        — Core single-instance evaluation pipeline
│   ├── run_evaluation.py  — Batch runner (orchestrates full evaluation matrix)
│   ├── tool_executor.py   — Sandboxed Python execution for the tool_use condition
│   └── analysis/          — Analysis pipeline (tables, figures, statistics)
│       ├── __init__.py
│       ├── loader.py      — Result loading, model/task metadata, display names
│       ├── tables.py      — LaTeX table generation (main accuracy, CoT lift, etc.)
│       ├── plots.py       — Figure generation (accuracy curves, heatmaps, etc.)
│       ├── statistics.py  — Bootstrap CIs and McNemar's test
│       ├── stats.py       — Auto-generated LaTeX \newcommand macros for the paper
│       └── pub_style.py   — Publication-quality matplotlib style settings
├── tasks/                 — Benchmark task generators (B1–B9)
│   ├── __init__.py        — Task registry (imports all B1–B9 modules)
│   ├── b1_majority.py     — B1: Masked Majority (Type 1: Sensitivity)
│   ├── b2_boolean_eval.py — B2: Nested Boolean Evaluation (Type 2: Depth)
│   ├── b3_permutation.py  — B3: Iterated Permutation Composition (Type 3: Serial)
│   ├── b4_state_machine.py— B4: State Machine Tracking (Type 3: Serial)
│   ├── b5_graph_reach.py  — B5: Graph Reachability (Type 2/4: Depth/Algorithmic)
│   ├── b6_lis.py          — B6: Longest Increasing Subsequence (Type 4: Algorithmic)
│   ├── b7_3sat.py         — B7: 3-SAT (Type 5: Intractability)
│   ├── b8_reversal.py     — B8: Reversal Inference (Type 6: Architectural)
│   └── b9_negation.py     — B9: Negation Sensitivity (Type 6: Architectural)
└── configs/
    └── models.txt         — Complete list of 12 models with display names
```

## Evaluation Conditions

Each benchmark instance is evaluated under four conditions:

1. **Direct** — No chain-of-thought; the model must answer immediately.
2. **Short CoT** — "Think step by step" prompt prefix (unconstrained).
3. **Budget CoT** — Dynamic word budget computed per instance based on task complexity.
4. **Tool Use** (tool-augmented) — Model writes and executes Python code via a sandboxed interpreter.

## Reproducing Experiments

### Prerequisites

- Python 3.10+
- API keys for: Anthropic (`ANTHROPIC_API_KEY`), OpenAI (`OPENAI_API_KEY`),
  and/or OpenRouter (`OPENROUTER_API_KEY`)
- Python packages: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`

### Generate benchmark data

```bash
python generate.py --all
```

This creates JSON files in `data/` with 500 instances per task (100 per
difficulty level, 5 difficulty levels).

### Run a single evaluation

```bash
python code/evaluate.py \
    --benchmark data/b1_B1_masked_majority.json \
    --model openai:gpt-4o \
    --condition direct \
    --output results/gpt4o_b1_direct.json
```

### Run the full evaluation matrix

```bash
python code/run_evaluation.py --all
```

This evaluates all 12 models x 9 tasks x 4 conditions with checkpoint/resume
support. Estimated runtime: 48-72 hours depending on API rate limits.

### Run the analysis pipeline

After evaluation, generate tables and figures:

```bash
python analyze.py --results-dir results/ --output-dir analysis_output/
```

## Task-to-Gap-Type Mapping

| Task | Gap Type | Complexity Class |
|------|----------|-----------------|
| B1: Masked Majority | Type 1: Sensitivity | TC^0 |
| B2: Nested Boolean | Type 2: Depth | NC^1 |
| B3: Iterated Permutation Composition | Type 3: Serial | L (Logspace) |
| B4: State Machine | Type 3: Serial | L (Logspace) |
| B5: Graph Reachability | Type 2/4: Depth/Algorithmic | NL |
| B6: LIS | Type 4: Algorithmic | P |
| B7: 3-SAT | Type 5: Intractability | NP-complete |
| B8: Reversal Inference | Type 6: Architectural | Total facts |
| B9: Negation Sensitivity | Type 6: Architectural | Compositional |

## Data Format

Raw results are not included due to size (176,477 instances). Each result
file is JSON with structure:

```json
{
  "summary": {
    "task": "B1_masked_majority",
    "model": "gpt-4o",
    "condition": "direct",
    "total_instances": 500,
    "correct": 312,
    "accuracy": 0.624
  },
  "results": [
    {
      "instance_id": "B1_d1_001",
      "task": "B1_masked_majority",
      "difficulty": 1,
      "condition": "direct",
      "model": "gpt-4o",
      "extracted_answer": "1",
      "ground_truth": "1",
      "correct": true,
      "latency_ms": 423.1
    }
  ]
}
```

## Data Availability

The full evaluation results (176,477 instances across 12 models, 9 tasks, and
4 conditions) will be released upon publication. A anonymized dataset archive
will be hosted on a public repository with a persistent DOI.

To regenerate benchmark instances locally:

```bash
python generate.py --all --n-instances 500
```

To run a minimal evaluation on a single task and model:

```bash
python code/evaluate.py \
    --benchmark data/b1_B1_masked_majority.json \
    --model anthropic:claude-haiku-4-5-20251001 \
    --condition direct \
    --output results/test_run.json
```
