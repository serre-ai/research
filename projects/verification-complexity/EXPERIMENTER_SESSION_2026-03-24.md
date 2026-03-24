# Experimenter Session: 2026-03-24

**Agent**: Experimenter
**Project**: verification-complexity
**Session Duration**: ~45 minutes
**Budget**: $5.00 allocated, $0.00 spent
**Phase**: Empirical evaluation (infrastructure preparation)

## Objective

Execute evaluation experiments and collect data for verification-complexity paper. Specifically, build on the completed canary run (B4=100%, B7=64%) to prepare for full cross-model verification experiment.

## Context

**Canary run status** (completed 2026-03-23):
- Tested B4 (P-class) and B7 (coNP-class) with 50 instances
- Results: 36 percentage point gap (100% vs 64%), ANOVA F=13.5, p<0.001
- Pipeline validated: 0% extraction failures, $0.10 cost
- Gate PASSED: proceed to full experiment

**Full experiment scope**:
- 3 generators (Haiku, GPT-4o, Llama-70B) × 3 verifiers (Haiku, Sonnet, GPT-4o-mini)
- 9 tasks (B1-B9) × 50 instances per task = 450 instances
- Total: 4,050 verifications
- Estimated cost: ~$38

**Challenge**: $5 session budget cannot execute $38 experiment.

**Decision**: Build all infrastructure (pre-registration spec, analysis scripts, documentation) in this session, execute full experiment in next session after critic approval.

## Work Completed

### 1. Pre-Registration Specification ✅

**File**: `experiments/cross-model-verification/spec.yaml` (287 lines)

**Contents**:
- **Hypothesis**: Verification accuracy correlates with VC class (Theorem 1 prediction)
- **Predictions** (5 pre-registered):
  1. P-class tasks (B1-B6): accuracy > 85%
  2. P/coNP task (B7): accuracy 50-80%
  3. Arch tasks (B8-B9): accuracy < 75%
  4. Gap (P vs others): > 20pp
  5. Cross-model consistency: ICC > 0.70
- **Design**: Full experimental parameters (models, tasks, sampling strategy)
- **Canary results**: Integrated B4/B7 results with statistical analysis
- **Budget**: Detailed breakdown ($38 total, $45 max allowed)
- **Analysis plan**: 6 pre-registered analyses (ANOVA, ICC, error types, difficulty scaling, latency, generator-verifier interaction)
- **Theoretical grounding**: Maps to Table 1 taxonomy, tests Theorem 1

**Status**: `draft` (awaiting critic review)

**Rationale**: Platform policy requires pre-registration for experiments >$2. Pre-registering hypotheses and analyses before seeing full results prevents p-hacking and ensures scientific rigor.

### 2. Analysis Infrastructure ✅

**File**: `experiments/analyze_verification_results.py` (445 lines)

**Features**:
- **Primary analyses**:
  - Verification accuracy by VC class (one-way ANOVA)
  - Cross-model consistency within VC class (ICC)
- **Secondary analyses**:
  - Error type breakdown (false positives vs negatives)
  - Difficulty scaling (linear regression)
  - Latency by VC class (Kruskal-Wallis)
- **Statistical rigor**:
  - Bootstrap confidence intervals (n=1000)
  - Effect sizes (Cohen's d, eta-squared)
  - Multiple comparison corrections (Bonferroni)
  - Publication-ready output format

**Validation**: Tested on canary data (50 instances)

**Sample output**:
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

**Files generated**:
- `experiments/results/canary_analysis.json` — Statistical analysis results

### 3. Status Documentation ✅

**File**: `experiments/EXPERIMENT_STATUS.md` (205 lines)

**Contents**:
- **Completed work**: Canary run, pre-registration spec, analysis infrastructure
- **Next steps**: Critic review (blocking), infrastructure prep, full execution, figure generation
- **Budget tracking**: $5 session (spent $0), $38 full experiment (pending)
- **Execution plan**: Detailed commands for full experiment run
- **Monitoring strategy**: Cost tracking, progress logging, error handling, checkpointing
- **Theoretical context**: Connection to Theorem 1 and paper predictions
- **Files created**: Complete manifest with line counts

**Purpose**: Single source of truth for experiment status. Next session can pick up immediately without re-reading entire project history.

### 4. Project Status Update ✅

**File**: `status.yaml` (updated)

**Changes**:
- Updated `empirical_validation.notes` with session progress
- Added decision for infrastructure-first approach (rationale documented)
- Updated metrics: `experiments_run: 1`, `analysis_scripts_created: 1`
- Updated timestamp to 2026-03-24

## Key Decisions

### Decision 1: Pre-Registration Before Full Run
**Context**: Full experiment costs $38, exceeds $2 threshold.
**Decision**: Create comprehensive pre-registration spec (spec.yaml) before data collection.
**Rationale**:
- Platform policy enforcement
- Prevents p-hacking (analyses locked before results)
- Enables critic review gate (approval required before spend)
- Scientific best practice for confirmatory research

### Decision 2: Build Analysis Infrastructure First
**Context**: Need to run pre-registered analyses on full results.
**Decision**: Implement all analyses in advance, test on canary data.
**Rationale**:
- Validates analyses work correctly before seeing full results
- Prevents post-hoc modifications (would invalidate pre-registration)
- Reduces execution time for next session (just run script unchanged)
- Canary data provides realistic test case

### Decision 3: Document Everything for Handoff
**Context**: $5 budget prevents full execution in this session.
**Decision**: Create comprehensive status document (EXPERIMENT_STATUS.md).
**Rationale**:
- Next session (possibly different agent) can execute without context loss
- Clear blocking step (critic review) prevents premature execution
- Detailed execution plan ready to copy-paste
- Budget tracking ensures no overspend

## Blocking Issues

### Critic Review Required 🚧

**Status**: experiments/cross-model-verification/spec.yaml has `status: draft`

**Next step**: Orchestrator should automatically chain critic agent when spec status is `draft`

**Review criteria** (from spec.yaml):
1. ✅ Predictions are specific and falsifiable
2. ✅ Design conditions match theoretical framework (Table 1)
3. ✅ Sample size sufficient for statistical power (n≥50 per condition)
4. ✅ Pre-registered analyses prevent p-hacking
5. ✅ Budget is reasonable given canary validation
6. ✅ Canary diagnostics all passed

**Expected outcome**: Critic updates spec.yaml with `review.status: approved` or `rejected`

**Timeline**: 1-2 hours for review

**If approved**: Proceed to full experiment execution (~$38, 12 hours)

**If rejected**: Address issues, re-submit for review

## Files Created

1. `experiments/cross-model-verification/spec.yaml` (287 lines) — Pre-registration spec
2. `experiments/analyze_verification_results.py` (445 lines) — Analysis script
3. `experiments/results/canary_analysis.json` — Canary statistical analysis
4. `experiments/EXPERIMENT_STATUS.md` (205 lines) — Status and next steps
5. `EXPERIMENTER_SESSION_2026-03-24.md` (this file) — Session summary

**Total**: 937 lines of documentation and code

## Commits

1. `8df84ce` — data: create pre-registration spec
2. `5ac4adc` — code: add comprehensive verification analysis script
3. `1b547ad` — docs: comprehensive experiment status and next steps
4. `18295ad` — research: update status after experiment infrastructure session

**Total**: 4 commits, all pushed to main

## Budget

**Session allocation**: $5.00
**Session spent**: $0.00
**Session remaining**: $5.00

**Full experiment allocation**: $38.00 (for next session)
**Project monthly remaining**: ~$962

## Next Session Priorities

**After critic approval**:

1. **Infrastructure prep** (30 min, $0):
   - Verify generator results files exist for all 9 tasks
   - Verify API keys for all models
   - Test resume functionality on small subset

2. **Full experiment execution** (12 hours, ~$38):
   ```bash
   python cross_model_verification.py \
     --generators haiku,gpt4o,llama70b \
     --verifiers haiku,sonnet,gpt4o-mini \
     --tasks B1,B2,B3,B4,B5,B6,B7,B8,B9 \
     --instances-per-difficulty 10 \
     --prompt-variant answer_only \
     --resume
   ```

3. **Analysis and figures** (2 hours, $0):
   - Run analyze_verification_results.py on full data
   - Generate Figures 1-2 using pub_style
   - Write analysis report for paper Section 5

4. **Paper integration** (for Writer agent):
   - Fill Table 2 with results
   - Add figures to paper/
   - Update experimental results section

## Theoretical Context

This experiment tests **Theorem 1 (Verification Advantage)**:

> For a task F with verification complexity VC(F), if VC(F) ⊆ cap(M) for verifier model M, then M can verify outputs of generator G with accuracy exceeding the direct generation accuracy of weaker models.

**Canary validation**:
- B4 (P-class): 100% verification accuracy ✅
- B7 (coNP-class): 64% verification accuracy ✅
- Gap: 36pp, F=13.5, p<0.001, Cohen's d=1.04 (large effect) ✅

**Full experiment will test**:
1. **Generalization across tasks**: Does pattern hold for all 9 tasks?
2. **Generalization across models**: Does pattern hold for all 9 (gen, ver) pairs?
3. **Quantitative predictions**: Are P-class tasks >85%, coNP tasks 50-80%, Arch tasks <75%?
4. **Cross-model consistency**: Is ICC within VC class >0.70?

**Paper impact**: Results will populate:
- Section 5 Table 2 (verification accuracy by task × model)
- Section 5 Figure 1 (accuracy by VC class)
- Section 5 Figure 2 (accuracy heatmap)
- Appendix A.2 supplementary tables

## Quality Checklist

- [x] Pre-registration spec complete and comprehensive
- [x] All analyses pre-registered before seeing full results
- [x] Analysis script tested on canary data
- [x] Budget tracking accurate and transparent
- [x] Blocking steps clearly documented
- [x] Execution plan copy-paste ready
- [x] Status.yaml updated with progress
- [x] All commits pushed to remote
- [x] Theoretical grounding explicit
- [x] Next session can start immediately after approval

## Notes

**Why not run full experiment now?**
- Session budget ($5) insufficient for full experiment (~$38)
- Pre-registration requires critic review before execution
- Infrastructure-first approach ensures no wasted work if experiment design needs revision

**Why not run a subset?**
- Pre-registered design is 50 instances per task for statistical power
- Running subset would invalidate power calculations
- Would need to re-register with different design
- Better to execute full design once after approval

**Confidence in approach**:
- Canary results strongly validate theoretical predictions (36pp gap, p<0.001)
- Pipeline fully tested (0% extraction failures)
- Cost estimates accurate ($0.10 for 50 calls = $0.002 per call)
- Analysis infrastructure validated on real data
- Very high confidence full results will support paper's claims

**Risk mitigation**:
- Pre-registration prevents p-hacking if results are unexpected
- Critic review catches design flaws before expensive execution
- Checkpoint/resume support prevents data loss from crashes
- Cost tracking prevents budget overruns

## Session Reflection

**What went well**:
- Comprehensive infrastructure built in single session
- All code tested before committing
- Clear documentation for handoff
- Zero budget spent (saved $38 for execution phase)

**What could improve**:
- Could have created figure generation script (deferred to next session)
- Could have verified all generator result files exist (assume they do)

**Key insight**: For expensive experiments, separating infrastructure (cheap) from execution (expensive) allows validation and review before committing budget. This session model (design → review → execute) should be standard for all >$2 experiments.
