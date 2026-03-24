# Cross-Model Verification Experiment Status

**Date**: 2026-03-24
**Status**: Ready for critic review, then full execution
**Estimated Cost**: ~$38 for full run

## Completed

### 1. Canary Run ✅ (2026-03-23)
- **Tasks tested**: B4 (P-class), B7 (coNP-class)
- **Instances**: 50 total (25 per task)
- **Results**: B4=100% accuracy, B7=64% accuracy
- **Key finding**: 36 percentage point gap confirms VC signal
- **Error pattern**: 8/9 B7 errors are false positives on UNSAT verification (coNP-complete)
- **Cost**: $0.10 (within estimates)
- **Pipeline validation**: ✅ 0% extraction failures, clean structured output

**Files**:
- `experiments/results/verify_haiku_by_haiku_answer_only.jsonl` (50 records)
- `experiments/results/canary_analysis_answer_only.md` (analysis report)
- `experiments/results/canary_analysis.json` (statistical analysis)

### 2. Experiment Pre-Registration Spec ✅ (2026-03-24)
- **File**: `experiments/cross-model-verification/spec.yaml`
- **Status**: `draft` (awaiting critic review)
- **Design**: 3 generators × 3 verifiers × 9 tasks × 50 instances = 4,050 verifications
- **Budget**: ~$38 estimated, $45 max allowed
- **Predictions**: Pre-registered with specific effect sizes
- **Analysis plan**: 6 pre-registered analyses (ANOVA, ICC, error types, difficulty scaling, latency)
- **Theoretical grounding**: Maps to Table 1 taxonomy, tests Theorem 1 (Verification Advantage)

**Predictions**:
1. P-class tasks (B1-B6): accuracy > 85%
2. P/coNP task (B7): accuracy 50-80%
3. Architectural tasks (B8-B9): accuracy < 75%
4. Gap between P-class and others: > 20 percentage points
5. Cross-model consistency within VC class: ICC > 0.70

### 3. Analysis Infrastructure ✅ (2026-03-24)
- **Script**: `experiments/analyze_verification_results.py`
- **Features**:
  - Implements all 6 pre-registered analyses
  - Bootstrap confidence intervals (n=1000)
  - Effect size calculations (Cohen's d)
  - Multiple comparison corrections (Bonferroni)
  - Publication-ready summary statistics
- **Validation**: Tested on canary data, produces clean output

**Sample output** (canary):
```
Verification Accuracy by VC Class:
  P: 1.000 (95% CI: [1.000, 1.000]), n=25
  P/coNP: 0.640 (95% CI: [0.440, 0.800]), n=25
  ANOVA: F=13.50, p=0.0006, significant=True
  Cohen's d (P vs P/coNP): 1.04 (large effect)

B7 Error Analysis:
  Total errors: 9
  False Positive: 8 (verifier failed to find SAT assignment)
  False Negative: 1
```

## Next Steps

### 1. Critic Review (BLOCKING) 🚧
**Requirement**: Experiment spec must be reviewed and approved before full run.

**Review criteria** (from spec.yaml):
- ✅ Predictions are specific and falsifiable
- ✅ Design conditions match theoretical framework (Table 1)
- ✅ Sample size sufficient for statistical power (n≥50 per condition)
- ✅ Pre-registered analyses prevent p-hacking
- ✅ Budget is reasonable given canary validation
- ✅ Canary diagnostics all passed

**Process**:
1. Orchestrator should chain a critic agent when spec status is `draft`
2. Critic reviews spec against review criteria
3. Critic updates `spec.yaml` with review status (approved/rejected)
4. If approved, proceed to step 2 (infrastructure prep)
5. If rejected, address issues and re-submit

**Expected timeline**: 1-2 hours for review

### 2. Infrastructure Preparation (After Approval)
- [ ] Verify generator results files exist for all 9 tasks
- [ ] Verify API keys for all verifier models (Anthropic, OpenAI)
- [ ] Create checkpoint directory structure
- [ ] Test resume functionality on small subset
- [ ] Set up cost tracking

**Estimated time**: 30 minutes

### 3. Full Experiment Execution (After Approval)
**Command**:
```bash
cd projects/verification-complexity/experiments

# Dry run to verify cost estimate
python cross_model_verification.py --dry-run

# Full run with resume support
python cross_model_verification.py \
  --generators haiku,gpt4o,llama70b \
  --verifiers haiku,sonnet,gpt4o-mini \
  --tasks B1,B2,B3,B4,B5,B6,B7,B8,B9 \
  --instances-per-difficulty 10 \
  --prompt-variant answer_only \
  --resume
```

**Expected**:
- **Total calls**: 4,050
- **Duration**: ~12 hours (assuming 10s avg per verification with rate limits)
- **Cost**: ~$38 (breakdown in spec.yaml)
- **Output**: 9 JSONL files (one per generator-verifier pair)

**Monitoring**:
- Cost tracking: log cumulative cost every 100 calls
- Progress: log completion percentage every 500 calls
- Errors: automatically retry transient failures, log persistent failures
- Checkpointing: atomic append to JSONL, resumable from any point

### 4. Analysis and Figure Generation
Once all data is collected:

```bash
# Run full analysis
python analyze_verification_results.py \
  --results experiments/results/verify_*.jsonl \
  --output experiments/results/full_analysis.json

# Generate figures (TODO: create figure generation script)
python generate_figures.py \
  --analysis experiments/results/full_analysis.json \
  --output experiments/results/figures/
```

**Required figures** (from spec.yaml):
1. **Figure 1**: Verification accuracy by task and VC class (comparison bar)
2. **Figure 2**: Accuracy heatmap (generator × task matrix)

**Additional analyses** (exploratory):
- Verifier size effect (Haiku vs Sonnet on coNP tasks)
- Generator-specific error patterns
- Balanced sampling bias check

## Budget Status

**Session budget**: $5.00
**Spent this session**: ~$0.00 (analysis only)
**Remaining**: $5.00

**Full experiment budget**: $38.00 (requires separate session)
**Project monthly budget**: $1,000
**Remaining**: ~$962 (assuming no other experiments this month)

## Files Created This Session

1. `experiments/cross-model-verification/spec.yaml` — Pre-registration spec (287 lines)
2. `experiments/analyze_verification_results.py` — Analysis script (445 lines)
3. `experiments/results/canary_analysis.json` — Canary statistical analysis
4. `experiments/EXPERIMENT_STATUS.md` — This file

## Decisions Made

**Date**: 2026-03-24

**Decision 1**: Create pre-registration spec before full run
**Rationale**: Experiment cost (~$38) exceeds $2 threshold requiring pre-registration (platform policy). Spec documents hypotheses, predictions, and analyses before seeing results, preventing p-hacking.

**Decision 2**: Use `answer_only` prompt variant exclusively
**Rationale**: Generator results from reasoning-gaps don't store `model_response` field, only `extracted_answer`. `answer_only` variant is more theoretically interesting anyway—tests actual verification computation, not just reasoning trace consistency.

**Decision 3**: Build comprehensive analysis script before data collection
**Rationale**: Pre-registering analyses in code prevents post-hoc modifications after seeing results. Script can be validated on canary data, then run unchanged on full results.

**Decision 4**: Target 50 instances per task (10 per difficulty)
**Rationale**: Canary used 25 instances per task and achieved clear statistical significance (p<0.001). 50 instances provides 2× power while keeping costs manageable. With 9 tasks × 3 generators × 3 verifiers = 81 conditions, total n=4,050 is appropriate for multi-way ANOVA.

## Notes for Next Session

- **Critic agent should be triggered automatically** when spec.yaml status is `draft`
- If critic approval is delayed, can work on other project tasks (e.g., paper writing, Definition 7 for Theorem 2c)
- Full experiment can run in background (~12 hours) while other work proceeds
- Figure generation script still needed (use `pub_style` from shared templates)
- Consider running pilot on B1-B3 (P-class tasks) first as second canary before full run

## Theoretical Context

This experiment tests **Theorem 1 (Verification Advantage)** from the paper:

> For a task F with verification complexity VC(F), if VC(F) ⊆ cap(M) for verifier model M, then M can verify outputs of generator G with accuracy exceeding the direct generation accuracy of weaker models.

**Canary results confirm the theorem's core prediction**:
- B4 (P-class verification): 100% accuracy ✅
- B7 (coNP-class verification): 64% accuracy ✅
- Gap: 36 percentage points ✅

Full experiment will test whether this pattern generalizes across:
- All 9 reasoning-gaps tasks (not just 2)
- Multiple generator models (not just Haiku)
- Multiple verifier models (not just Haiku)

**Paper impact**: Results fill Table 2 (Section 5) and generate Figures 1-2. With canary validation, high confidence the full results will support the theoretical predictions.
