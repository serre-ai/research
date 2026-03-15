# eval-monitor

Evaluation pipeline monitoring and result analysis skill.

## Usage
Used by Kit to monitor eval runs, parse results, and generate formatted comparison tables.

## Functions

### Check Pipeline Status
Query the Deepwork API for active and completed eval runs:
```bash
./scripts/parse-results.sh status
```

### Parse Results
Fetch and parse eval results for a specific project:
```bash
./scripts/parse-results.sh results reasoning-gaps
```

### Compare Models
Generate a cross-model comparison table for a benchmark task:
```bash
./scripts/parse-results.sh compare reasoning-gaps B1
```

## Analysis Outputs
- Per-model accuracy with bootstrap 95% CIs
- CoT lift (CoT accuracy - Direct accuracy) per model per task
- Cross-condition comparisons (direct vs CoT vs budget_cot)
- Anomaly flags: results outside expected ranges, failed runs, cost overruns

## Result Format
Results are formatted as Slack-compatible tables using fixed-width characters for alignment.
