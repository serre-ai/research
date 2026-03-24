# Evidence Summary: Claude Haiku 4.5 B1 Direct Accuracy

**Date**: 2026-03-24
**Claim**: Claude Haiku 4.5 achieves 0.5860 accuracy on B1_masked_majority under direct condition (n=500)
**Status**: VERIFIED ✓

## Primary Evidence

### Source File
- **Path**: `/home/deepwork/deepwork/projects/reasoning-gaps/benchmarks/results/claude-haiku-4-5-20251001_B1_masked_majority_direct.json`
- **Size**: 320,346 bytes
- **Last Modified**: 2026-03-16 14:12:57
- **Format**: JSON evaluation results with full instance-level data

### Evaluation Summary
```json
{
  "model": "claude-haiku-4-5-20251001",
  "task": "B1_masked_majority",
  "condition": "direct",
  "accuracy": 0.586,
  "total_instances": 500
}
```

### Key Metrics
- **Overall Accuracy**: 0.586 (58.60%)
- **Instances Evaluated**: 500
- **Correct Predictions**: 293
- **Incorrect Predictions**: 207
- **Average Latency**: 1,745.59 ms

### Performance Breakdown by Difficulty
| Difficulty | Accuracy | Correct/Total |
|-----------|----------|---------------|
| Level 1 | 0.85 (85.00%) | 85/100 |
| Level 2 | 0.61 (61.00%) | 61/100 |
| Level 3 | 0.41 (41.00%) | 41/100 |
| Level 4 | 0.52 (52.00%) | 52/100 |
| Level 5 | 0.54 (54.00%) | 54/100 |

## Verification

### Independent Computation
```python
# Counted from results array
correct_count = sum(1 for r in data['results'] if r['correct'])
total_count = len(data['results'])
computed_accuracy = correct_count / total_count  # = 293/500 = 0.586
```

**Result**: ✓ Computed accuracy (0.586) matches summary accuracy exactly.

### Cross-Reference with Analysis Pipeline
The result file was processed by the analysis pipeline as confirmed in:
- `/home/deepwork/deepwork/projects/reasoning-gaps/benchmarks/analysis_output/summary.md`
- Analysis includes this evaluation in the 209,438 total instances
- B1 task (Type 1: Sensitivity) direct condition average: 0.610 across all models

## Sample Instances

### Correct Predictions (examples)
1. `B1_masked_majority_d1_0000`: predicted=1, truth=1, difficulty=1
2. `B1_masked_majority_d1_0001`: predicted=0, truth=0, difficulty=1
3. `B1_masked_majority_d1_0002`: predicted=0, truth=0, difficulty=1

### Incorrect Predictions (examples)
1. `B1_masked_majority_d1_0018`: predicted=**, truth=0, difficulty=1 (extraction failure)
2. `B1_masked_majority_d1_0029`: predicted=The, truth=0, difficulty=1 (extraction failure)
3. `B1_masked_majority_d1_0035`: predicted=1, truth=0, difficulty=1

## Evaluation Context

### Task: B1_masked_majority
- **Type**: Type 1 (Sensitivity Gap)
- **Description**: Compute majority vote over visible (unmasked) bits in binary string
- **Complexity Class**: TC⁰-complete (constant-depth threshold circuits)
- **Difficulty Scaling**: String length and mask ratio varied across difficulty levels

### Condition: direct
- **Prompt Style**: Direct question with no reasoning scaffolding
- **Example**: "Consider the binary string: 0010111?1?\\nThe '?' characters are masked and should be ignored.\\nAmong the visible (unmasked) bits, is the majority 0 or 1?\\nAnswer with just '0' or '1'."
- **Expected Answer Format**: Single character ('0' or '1')

### Model: claude-haiku-4-5-20251001
- **Family**: Anthropic Claude
- **Size**: Small (Haiku tier)
- **Version**: 4.5 (20251001 release)
- **API**: Anthropic API

## Related Results

### Other Conditions for Same Model/Task
- **Short CoT**: Available in `claude-haiku-4-5-20251001_B1_masked_majority_short_cot.json`
- **Budget CoT**: Available in `claude-haiku-4-5-20251001_B1_masked_majority_budget_cot.json`

### Aggregate Metrics
From `analysis_output/summary.md`:
- Type 1 (Sensitivity) direct condition average across all models: 0.610
- Haiku's 0.586 is slightly below the cross-model average
- Type 1 CoT lift (short_cot): +0.133 average across models

## Confidence Assessment

**Evidence Quality**: STRONG
- Primary source data file exists and is intact
- File contains complete instance-level results (500 instances)
- Summary statistics independently verified by computation
- File metadata confirms evaluation date (2026-03-16)
- Result integrated into broader analysis pipeline
- Consistent with evaluation protocol documented in benchmark design

**Claim Accuracy**: EXACT MATCH
- Claimed accuracy: 0.5860
- Verified accuracy: 0.586
- Match precision: 3 decimal places (0.0000 difference)

## Conclusion

The claim is **fully supported** by primary evaluation data. The result file provides:
1. Direct evidence of 0.586 accuracy
2. Complete instance-level results (n=500)
3. Breakdown by difficulty level
4. Metadata confirming evaluation date and model
5. Integration into published analysis pipeline

No discrepancies or anomalies detected. Evidence chain is complete from raw evaluation to aggregated analysis.
