# Cross-Model Verification Canary Analysis

**Date**: 2026-03-23
**Experiment**: Answer-only verification (Haiku→Haiku)
**Tasks**: B4 (state machine), B7 (3-SAT)
**Instances**: 25 per task, 5 per difficulty level (1-5)
**Cost**: ~$0.10

## Executive Summary

**Gate Status: ✅ PASS**

Both success criteria met:
1. ✅ B4 accuracy (100%) > B7 accuracy (64%) — VC signal exists
2. ✅ Extraction failure rate (0%) < 10%

The canary confirms the theoretical prediction: verification accuracy correlates with task verification complexity. Proceed to full experiment.

## Results

### B4 (State Machine) — VC Class: P

- **Verification accuracy**: 25/25 = 100%
- **Generator correct → Verifier confirms**: 16/16 = 100%
- **Generator incorrect → Verifier detects**: 9/9 = 100%
- **Extraction failures**: 0/25 = 0%
- **Average latency**: 2,248ms

**Interpretation**: State machine verification is polynomial-time computable. The verifier can trace through the FSM transitions deterministically and verify the final state with perfect accuracy. No errors at any difficulty level.

### B7 (3-SAT) — VC Class: P/coNP

- **Verification accuracy**: 16/25 = 64%
- **Generator correct → Verifier confirms**: 14/15 = 93.3%
- **Generator incorrect → Verifier detects**: 2/10 = 20%
- **Extraction failures**: 0/25 = 0%
- **Average latency**: 6,638ms (3× longer than B4)

**Interpretation**: 3-SAT verification has asymmetric complexity:
- Verifying "Yes" (SAT) requires finding a satisfying assignment — NP-complete
- Verifying "No" (UNSAT) requires proving no assignment exists — coNP-complete

The verifier failed on 9/25 instances, with a clear pattern:
- **8 false positives**: Generator claimed "Yes" (UNSAT), ground truth is "No" (SAT), verifier incorrectly confirmed "Yes". The verifier attempted to find a satisfying assignment, failed, and incorrectly concluded the formula is unsatisfiable.
- **1 false negative**: Generator correctly said "Yes", verifier said "Incorrect". This is the only error where the verifier rejected a correct answer.

## Error Analysis: B7 Instances

All 9 verification errors occurred on B7. Error breakdown:

| Instance       | Difficulty | Gen Answer | Ground Truth | Verifier Judgment | Error Type |
|----------------|------------|------------|--------------|-------------------|------------|
| B7_3sat_d1_0019 | 1          | Yes        | No           | Correct           | False Positive |
| B7_3sat_d2_0008 | 2          | Yes        | No           | Correct           | False Positive |
| B7_3sat_d3_0002 | 3          | Yes        | No           | Correct           | False Positive |
| B7_3sat_d3_0005 | 3          | Yes        | No           | Correct           | False Positive |
| B7_3sat_d4_0000 | 4          | Yes        | No           | Correct           | False Positive |
| B7_3sat_d4_0001 | 4          | Yes        | No           | Correct           | False Positive |
| B7_3sat_d5_0000 | 5          | Yes        | No           | Correct           | False Positive |
| B7_3sat_d5_0002 | 5          | Yes        | No           | Correct           | False Positive |
| B7_3sat_d5_0007 | 5          | Yes        | Yes          | Incorrect         | False Negative |

**Pattern**: 8/9 errors are cases where the generator incorrectly claimed a formula is unsatisfiable, and the verifier failed to find a counterexample (satisfying assignment). This confirms the theoretical prediction: verifying UNSAT is coNP-complete and hard for polynomial-time bounded models.

The verifier's responses show it attempting systematic search (e.g., "Let me try x1=F, x2=F...") but giving up before finding the satisfying assignment. This is the expected behavior when verification complexity exceeds model capacity.

## Comparison to Success Criteria

| Criterion | Expected | Observed | Status |
|-----------|----------|----------|--------|
| B4 accuracy > B7 accuracy | Yes | 100% vs 64% | ✅ PASS |
| VC signal exists | Yes | 36pp gap | ✅ PASS |
| Extraction failure < 10% | Yes | 0% | ✅ PASS |

## Decision: Proceed to Full Experiment

The canary validates:
1. **Verification complexity signal is strong**: 36 percentage point gap between P-class and coNP-class tasks
2. **Pipeline works end-to-end**: No extraction failures, clean structured output
3. **Cost is manageable**: $0.10 for 50 calls = $0.002 per verification

**Recommendation**: Proceed to full cross-model verification experiment (3 generators × 3 verifiers × 9 tasks × 50 instances = 4,050 verifications, ~$38 estimated cost).

## Full Experiment Design

Based on canary results, the full experiment should:
1. Use answer_only prompt variant only (more theoretically interesting, full_cot data not available)
2. Sample 50 instances per task (10 per difficulty level) for statistical power
3. Run all 3 generator models (Haiku, GPT-4o, Llama-70B) × 3 verifier models (Haiku, Sonnet, GPT-4o-mini)
4. Expected total cost: ~$38 (within budget)

Skip full_cot variant for this experiment since reasoning-gaps results don't store model_response field.

## Notes

- **No model_response in data**: The reasoning-gaps short_cot results only save extracted_answer, not full model output. This prevents running full_cot verification variant. For future work, either use a different condition or re-run with response logging enabled.
- **Latency difference**: B7 took 3× longer than B4 (6.6s vs 2.2s), suggesting the verifier is doing more computation. This aligns with the theoretical prediction that harder verification requires more reasoning.
- **Perfect B4 accuracy**: 100% accuracy on state machine verification even at difficulty 5 confirms that P-class verification is well within model capacity.

## Next Steps

1. ✅ Canary complete
2. → Run full experiment (DW-144)
3. → Analyze results for VC correlation
4. → Write up for paper Section 5
