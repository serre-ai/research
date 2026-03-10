# Experiments Directory

This directory contains all code for empirical evaluation, analysis, and visualization of the ReasonGap benchmark suite.

## Structure

```
experiments/
├── analysis/          # Statistical analysis scripts
│   ├── primary.py     # 6 primary analyses from empirical plan
│   ├── secondary.py   # 3 secondary analyses
│   ├── robustness.py  # Robustness checks
│   └── stats_utils.py # Statistical test utilities
├── visualizations/    # Plotting and figure generation
│   ├── figures.py     # Main figures (4 figures for paper)
│   ├── tables.py      # Results tables (2 main tables)
│   └── viz_utils.py   # Plotting utilities and themes
├── data/              # Generated benchmark instances (gitignored)
│   ├── b1_*.json
│   ├── b2_*.json
│   └── ...
├── results/           # Evaluation results (gitignored)
│   ├── raw/           # Raw model responses
│   ├── processed/     # Processed accuracy scores
│   └── figures/       # Generated figures and tables
└── run_full_analysis.py  # Main pipeline script
```

## Usage

### Generate Benchmark Data

```bash
cd ../benchmarks
python generate.py --all --output ../experiments/data/
```

### Run Evaluations

```bash
cd ../benchmarks
# Example: evaluate GPT-4o on B1 with direct condition
python evaluate.py \
  --benchmark ../experiments/data/b1_majority.json \
  --model openai:gpt-4o \
  --condition direct \
  --output ../experiments/results/raw/b1_gpt4o_direct.json
```

### Run Full Analysis Pipeline

```bash
cd experiments
python run_full_analysis.py --results-dir results/raw/ --output-dir results/processed/
```

This will:
1. Aggregate all evaluation results
2. Run 6 primary analyses + 3 secondary analyses + robustness checks
3. Generate all figures and tables
4. Save results to `results/processed/`

### Generate Specific Figures

```bash
cd experiments
python -m visualizations.figures --analysis primary --figure 1 --output results/figures/
```

## Dependencies

```bash
pip install numpy scipy pandas matplotlib seaborn statsmodels scikit-learn
```

## Analysis Plan

See `../notes/08-empirical-analysis-plan.md` for complete specification of all analyses, statistical tests, and visualization requirements.
