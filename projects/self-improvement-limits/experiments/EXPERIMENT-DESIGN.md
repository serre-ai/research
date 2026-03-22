# Empirical Validation: Complete Experimental Design
## Self-Improvement Limits Project

**Project**: self-improvement-limits
**Linear Issue**: [DW-77](https://linear.app/oddurs/issue/DW-77/sil-design-empirical-validation-experiments)
**Created**: 2026-03-22
**Status**: Design complete, ready for execution
**Total Budget**: ~$200

---

## Overview

This document provides the complete experimental design for empirically validating the theoretical results in the self-improvement-limits paper. We test three core hypotheses across multiple self-improvement mechanisms and task types.

**Core Theoretical Claims:**
1. **Theorem 1**: Self-improvement converges to γ_∞ ≤ ν_0 + ε
2. **Theorem 2**: Capability gain bounded by verification capability
3. **Theorem 3**: Improvement inversely related to generation-verification gap
4. **Theorem 4**: Self-play can exceed self-training under specific conditions

**Validation Strategy:**
- Test 4 self-improvement mechanisms (self-training, self-refinement, self-play, constitutional AI)
- Across 3 task types with varying verification gaps (small, moderate, large)
- Measuring convergence trajectories, fixed points, and improvement bounds
- Total budget allocation: ~$200 across all experiments

---

## Part 1: Self-Training Validation

**Status**: Design complete, implementation complete, simulation validated
**Budget**: $100-150
**Implementation**: `experiments/self-training-validation/`
**Documentation**: See `experiments/self-training-validation/README.md`

### Summary

Self-training experiments test Theorems 1-3 by running iterative generation → verification → filtering → training loops on three tasks:

| Task | Gap Type | Predicted Improvement | Budget |
|------|----------|----------------------|---------|
| **HumanEval** | Small (0.10) | High (20-50%) | $25 |
| **GSM8K** | Moderate (0.20) | Moderate (10-30%) | $50 |
| **WritingPrompts** | Large (0.50) | Low (5-15%) | $25 |

**Key Metrics:**
- γ_t: Generation accuracy at iteration t
- ν_t: Verification accuracy at iteration t
- Convergence iteration: When |γ_t - γ_{t-1}| < 0.02
- Relative improvement: (γ_∞ - γ_0) / γ_0

**Validation Criteria:**
- All tasks converge within 10 iterations
- γ_∞ ≤ ν_0 + ε holds for all tasks
- Improvement negatively correlates with gap size (Spearman r > 0.75)

**Status**: Ready for execution. See full specification in `self-training-validation/spec.yaml`

---

## Part 2: Self-Refinement Validation

**Status**: Design phase
**Budget**: $30-50
**Priority**: High (tests Theorem 2 on iterative improvement)

### Hypothesis

Self-refinement (generate → critique → revise) should show similar convergence bounds to self-training, as both are constrained by verification capability. However, self-refinement may show faster convergence due to explicit error correction.

**Prediction**: Multi-round refinement converges to the same fixed point as self-training (γ_∞ ≤ ν_0 + ε), but with potentially faster convergence rate.

### Tasks

| Task | Description | Gap | Test Size | Rounds |
|------|-------------|-----|-----------|--------|
| **Essay Writing** | Generate → critique → revise essays | Large (0.45) | 30 | 5 |
| **Code Debugging** | Write code → identify bugs → fix | Small (0.15) | 30 | 5 |
| **Math Problem Solving** | Solve → verify → correct | Moderate (0.20) | 30 | 5 |

### Procedure

For each task instance:

1. **Round 0**: Model generates initial solution
2. **Round 1-5**:
   - Model critiques previous solution (identifies errors)
   - Model revises based on critique
   - Measure quality at each round
3. **Metrics**:
   - Quality trajectory: q_0 → q_1 → ... → q_5
   - Convergence: First round where |q_r - q_{r-1}| < threshold
   - Ceiling: Does q_∞ ≤ ν_0 + ε?

### Implementation Notes

**Generation Prompt:**
```
Task: {task_description}
Provide your solution:
```

**Critique Prompt:**
```
Task: {task_description}
Your solution: {solution}

Critique your solution. Identify errors, weaknesses, or areas for improvement:
```

**Revision Prompt:**
```
Task: {task_description}
Your previous solution: {solution}
Your critique: {critique}

Provide a revised solution addressing the issues you identified:
```

### Metrics

- **q_r**: Quality score at refinement round r (0-1 scale)
- **convergence_round**: First round where |q_r - q_{r-1}| < 0.05
- **total_improvement**: (q_final - q_0) / q_0
- **per_round_gain**: Average improvement per round

### Expected Results

1. **Convergence**: All tasks should converge within 5 rounds
2. **Ceiling**: Final quality q_∞ should satisfy q_∞ ≤ ν_0 + ε
3. **Gap effect**: Small-gap tasks (code debugging) show more improvement than large-gap tasks (essay writing)
4. **Diminishing returns**: Improvement per round decreases: Δq_1 > Δq_2 > Δq_3 > ...

### Budget Breakdown

- Essay Writing: 30 instances × 5 rounds × 1000 tokens × $0.003/1k = $0.45 per instance → $13.50
- Code Debugging: 30 instances × 5 rounds × 800 tokens × $0.003/1k = $0.36 per instance → $10.80
- Math Problem Solving: 30 instances × 5 rounds × 800 tokens × $0.003/1k = $0.36 per instance → $10.80
- **Total**: $35.10 (+ 50% buffer = $52.65)

---

## Part 3: Self-Play Validation

**Status**: Design phase
**Budget**: $30-50
**Priority**: Medium (tests Theorem 4 on self-play vs self-training separation)

### Hypothesis

**Theorem 4** claims self-play can exceed self-training bounds when game structure provides implicit verification. We test this by comparing self-play and self-training on debate tasks.

**Prediction**: Self-play on debate tasks should show higher final capability than self-training, as adversarial dynamics provide stronger learning signal than self-verification.

### Tasks

| Task | Type | Implicit Verification | Test Size | Rounds |
|------|------|----------------------|-----------|---------|
| **Mathematical Proofs** | Debate | Proof checking via debate | 40 | 10 |
| **Factual Claims** | Debate | Fact verification via contradiction | 40 | 10 |

### Procedures

#### A. Self-Training Baseline

Standard self-training loop (as in Part 1):
1. Generate proofs/claims
2. Self-verify quality
3. Filter high-quality examples
4. Train on filtered set
5. Measure γ_t over iterations

#### B. Self-Play (Debate)

1. **Generate**: Player A makes a claim/proof
2. **Challenge**: Player B argues against it (identifies flaws)
3. **Defend**: Player A responds to challenges
4. **Judge**: Player C evaluates debate winner
5. **Update**: Train on winning arguments
6. **Measure**: γ_t over iterations

### Metrics

- **γ_t^ST**: Self-training capability at iteration t
- **γ_t^SP**: Self-play capability at iteration t
- **separation**: γ_∞^SP - γ_∞^ST (should be positive per Theorem 4)
- **convergence_gap**: How much faster self-play converges

### Expected Results

1. **Separation**: γ_∞^SP > γ_∞^ST (self-play exceeds self-training)
2. **Magnitude**: Separation should be 10-30% improvement
3. **Convergence**: Self-play may converge faster due to stronger signal
4. **Theoretical bound**: Even self-play should satisfy γ_∞^SP ≤ ν_0^debate + ε, where ν_0^debate may be higher than ν_0^self

### Implementation Notes

**Roles:**
- Player A (Proposer): Generates claims/proofs
- Player B (Challenger): Identifies weaknesses
- Player C (Judge): Evaluates arguments

**Prompts:**

*Proposer:*
```
Task: {task}
Make a claim or provide a proof:
```

*Challenger:*
```
Task: {task}
Claim/Proof: {proposal}

Identify flaws or counterarguments:
```

*Judge:*
```
Task: {task}
Proposal: {proposal}
Challenge: {challenge}

Who presented the stronger argument? Rate on scale 0 (Challenger wins) to 1 (Proposer wins):
```

### Budget Breakdown

- Mathematical Proofs: 40 instances × 10 rounds × (3 roles) × 600 tokens × $0.003/1k = $2.16 per instance → $86.40
- Factual Claims: 40 instances × 10 rounds × (3 roles) × 500 tokens × $0.003/1k = $1.80 per instance → $72.00

**Total**: $158.40 (exceeds budget)

**Optimization**: Reduce to 20 instances each or 5 rounds each → $40-80

---

## Part 4: Constitutional AI Validation

**Status**: Design phase
**Budget**: $20-30
**Priority**: Low (primarily validates self-refinement variant)

### Hypothesis

Constitutional AI (critique against principles → revise) is a structured form of self-refinement. Should show similar convergence bounds but potentially better alignment with specified principles.

**Prediction**: Convergence to principle-adherence ceiling, bounded by model's ability to evaluate principle violations (verification).

### Tasks

| Task | Principle | Gap | Test Size |
|------|-----------|-----|-----------|
| **Story Writing** | "Be helpful and harmless" | Large | 30 |
| **Argument Generation** | "Use factual claims only" | Moderate | 30 |

### Procedure

1. **Generate**: Model writes story/argument
2. **Critique**: Model evaluates principle violations (0-1 score)
3. **Revise**: Model revises to reduce violations
4. **Iterate**: 5 rounds
5. **Measure**: Principle adherence over rounds

### Metrics

- **adherence_r**: Principle adherence at round r (human-evaluated)
- **self_eval_r**: Model's self-evaluation at round r
- **alignment_gap**: |adherence_r - self_eval_r| (calibration)

### Expected Results

1. **Convergence**: Adherence plateaus within 5 rounds
2. **Ceiling**: Final adherence ≤ self-evaluation capability
3. **Calibration**: Self-evaluation gap increases over rounds (model becomes overconfident)

### Budget Breakdown

- Story Writing: 30 instances × 5 rounds × 800 tokens × $0.003/1k = $0.36 per instance → $10.80
- Argument Generation: 30 instances × 5 rounds × 600 tokens × $0.003/1k = $0.27 per instance → $8.10
- **Total**: $18.90 (+ 50% buffer = $28.35)

---

## Cross-Experiment Comparisons

After completing all four experiment sets, conduct cross-mechanism analysis:

### Comparison 1: Convergence Rates

**Question**: Do different mechanisms converge at different rates?

**Analysis**:
- Plot convergence curves for all mechanisms on same task
- Compare iterations to convergence
- Statistical test: ANOVA on convergence iteration across mechanisms

**Expected**: Self-play converges fastest, self-training slowest, self-refinement intermediate

### Comparison 2: Fixed Point Heights

**Question**: Do all mechanisms converge to same ceiling?

**Analysis**:
- Compare γ_∞ across mechanisms on matched tasks
- Test if differences are statistically significant
- Check if all satisfy γ_∞ ≤ ν_0 + ε

**Expected**: Self-training and self-refinement converge to similar heights; self-play may exceed both

### Comparison 3: Gap Effect Universality

**Question**: Does gap effect hold across all mechanisms?

**Analysis**:
- Compute gap-improvement correlation for each mechanism
- Compare Spearman correlations across mechanisms
- Meta-analysis: Does gap predict improvement universally?

**Expected**: Negative correlation for all mechanisms, strongest for self-training

---

## Metrics Summary

### Primary Metrics (All Experiments)

| Metric | Symbol | Definition | Purpose |
|--------|--------|------------|---------|
| Generation accuracy | γ_t | Accuracy at iteration t | Track capability trajectory |
| Verification accuracy | ν_t | Verification accuracy | Measure ceiling |
| Convergence iteration | t_conv | When \|γ_t - γ_{t-1}\| < 0.02 | Quantify convergence rate |
| Fixed point | γ_∞ | limₜ→∞ γ_t | Test ceiling bound |
| Relative improvement | Δ_rel | (γ_∞ - γ_0) / γ_0 | Measure gain magnitude |
| Gap size | g_D | Difficulty gap parameter | Test gap-improvement relation |

### Secondary Metrics

| Metric | Symbol | Purpose |
|--------|--------|---------|
| Verification-generation gap | ν_0 - γ_0 | Quantify initial gap |
| Slack term | ε | Measure how much γ_∞ exceeds ν_0 |
| Convergence rate | λ | Exponential decay parameter |
| Improvement function | f(g_D) | Map gap to improvement bound |

### Cross-Mechanism Metrics

| Metric | Symbol | Purpose |
|--------|--------|---------|
| Self-play gain | γ_∞^SP - γ_∞^ST | Quantify self-play advantage |
| Mechanism efficiency | t_conv by mechanism | Compare convergence speeds |
| Universal gap effect | ρ(g_D, Δ) across mechanisms | Test theory generality |

---

## Budget Allocation

| Experiment | Tasks | Priority | Estimated Cost | Status |
|------------|-------|----------|----------------|--------|
| **Self-Training** | GSM8K, HumanEval, WritingPrompts | Critical | $100-150 | Implementation complete |
| **Self-Refinement** | Essays, Code, Math | High | $35-50 | Design complete |
| **Self-Play** | Proofs, Claims | Medium | $40-80 | Design complete |
| **Constitutional AI** | Stories, Arguments | Low | $20-30 | Design complete |
| **Cross-Analysis** | All tasks | High | $0 (analysis only) | Design complete |

**Total**: $195-310
**Recommended First Phase**: Self-Training + Self-Refinement = $135-200 (within budget)
**Optional Second Phase**: Self-Play + Constitutional = $60-110 (if budget allows)

---

## Implementation Timeline

### Phase 1: Core Validation ($135-200)

**Week 1-2: Self-Training**
- Day 1: Run canary experiment (GSM8K, $3-5)
- Day 2-3: Run full experiments (all 3 tasks, $100-150)
- Day 4-5: Analysis and figure generation

**Week 3: Self-Refinement**
- Day 1: Implement experiment code
- Day 2-3: Run experiments (all 3 tasks, $35-50)
- Day 4: Analysis

**Deliverable**: Section 5 of paper with real experimental results

### Phase 2: Extended Validation ($60-110, Optional)

**Week 4: Self-Play**
- Day 1-2: Implement debate framework
- Day 3-4: Run experiments ($40-80)
- Day 5: Analysis

**Week 5: Constitutional AI**
- Day 1: Implement critique-revision loop
- Day 2: Run experiments ($20-30)
- Day 3: Analysis

**Week 6: Cross-Analysis**
- Day 1-3: Cross-mechanism comparison
- Day 4-5: Write supplementary materials

**Deliverable**: Extended validation section + supplementary materials

---

## Pre-Registration Commitments

To prevent p-hacking, we commit to:

1. **Fixed hypotheses**: Testing specific predictions from Theorems 1-4
2. **Pre-specified metrics**: All metrics defined before running experiments
3. **No post-hoc analyses**: Analysis code written before seeing results
4. **Report all results**: Including null results and contradictions
5. **Canary validation**: Must pass diagnostics before full run
6. **Budget caps**: Hard limits prevent runaway costs

**Modifications Requiring Re-Registration:**
- Changing statistical tests or thresholds
- Adding new tasks or conditions
- Modifying filtering or training procedures
- Changing convergence criteria

**Allowed Without Re-Registration:**
- Bug fixes in evaluation code
- Prompt formatting adjustments (if canary fails)
- Task difficulty calibration (if accuracy is 0% or 100%)
- Reducing sample size due to budget constraints

---

## Risk Mitigation

### Risk 1: Results Contradict Theory

**Likelihood**: Low (simulation validated theory)
**Impact**: High (undermines paper)

**Mitigation**:
- Pre-registration prevents p-hacking
- Canary run provides early warning
- If contradiction found: investigate for bugs first, then report as finding

### Risk 2: Budget Overrun

**Likelihood**: Medium (API costs can vary)
**Impact**: Medium (blocks completion)

**Mitigation**:
- Canary validates cost estimates
- Hard budget caps in experiment code
- Can reduce sample sizes or iterations if needed
- Prioritized execution (critical experiments first)

### Risk 3: Experimental Pipeline Failures

**Likelihood**: Medium (API errors, parsing issues)
**Impact**: Medium (wasted budget)

**Mitigation**:
- Comprehensive canary diagnostics
- Checkpoint system for crash recovery
- Extensive error handling and retries
- Manual inspection of first few instances

### Risk 4: Weak or Null Results

**Likelihood**: Low-Medium
**Impact**: Medium (reduces paper impact)

**Mitigation**:
- Simulation suggests strong effects exist
- Multiple tasks increase chance of finding effects
- Null results still scientifically valuable (negative results)
- Can discuss why effects are weaker than predicted

---

## Success Criteria

### Minimum Viable Validation (MVP)

To satisfy internal review requirements and resolve FATAL issue #1:

**Must Have:**
- [x] Self-training experiments on 3 tasks (design complete)
- [ ] Real experimental results (not simulation)
- [ ] Figures showing convergence trajectories
- [ ] Statistical tests confirming Theorems 1 and 3

**Impact**: Predicted +2.0 points on review score (5.26 → 7.26)

### Full Validation (Ideal)

For strong Accept at ICLR:

**Should Have:**
- [ ] Self-refinement experiments (3 tasks)
- [ ] Self-play vs self-training comparison
- [ ] Cross-mechanism analysis
- [ ] Validation against published results (STaR, ReST, etc.)

**Impact**: Predicted +2.5-3.0 points on review score (5.26 → 7.76-8.26)

### Extended Validation (Exceptional)

For top-tier reviews:

**Nice to Have:**
- [ ] Constitutional AI experiments
- [ ] Multiple model families (Claude, GPT-4, Llama)
- [ ] Convergence rate analysis
- [ ] Information-theoretic gap measurements

**Impact**: Potential spotlight or oral presentation

---

## Deliverables

### For Paper

1. **Section 5: Empirical Validation**
   - Results from self-training experiments
   - Convergence trajectory figures
   - Statistical analyses confirming theorems
   - Gap-improvement correlation plots

2. **Supplementary Materials**
   - Complete experimental details
   - Self-refinement and self-play results (if completed)
   - Cross-mechanism comparisons
   - Raw data and analysis code

### For Platform

1. **Experiment Specifications**
   - Pre-registration specs for each experiment type
   - Implementation code with documentation
   - Analysis scripts and notebooks

2. **Session Reports**
   - Execution logs and cost tracking
   - Anomaly investigations
   - Lessons learned and recommendations

---

## Reproducibility

All experiments designed for full reproducibility:

1. **Deterministic seeds**: All random processes use fixed seeds
2. **Version control**: All code and specs in git
3. **Pre-registration**: Hypotheses and analyses committed before execution
4. **Checkpoint system**: Full state recovery after crashes
5. **Complete logging**: Every API call, response, and evaluation logged
6. **Public code**: Analysis code available in supplementary materials

**Reproducibility Checklist:**
- [ ] Pre-registration specs committed
- [ ] Implementation code documented
- [ ] Analysis scripts written before seeing results
- [ ] All random seeds specified
- [ ] Model versions and parameters recorded
- [ ] Complete execution logs saved
- [ ] Data and code available in supplementary

---

## References

**Related Experiment Designs:**
- STaR (Zelikman et al., 2022): Self-training baseline
- ReST (Gulcehre et al., 2023): RL self-improvement
- Constitutional AI (Bai et al., 2022): Critique-revision loop
- Mind the Gap (ICLR 2025): GV-gap measurement methodology

**Theoretical Foundations:**
- Theorem 1: Self-training convergence bound
- Theorem 2: Capability gain characterization
- Theorem 3: GV-gap monotonicity
- Theorem 4: Self-play separation result

**Platform Resources:**
- `experiments/self-training-validation/`: Complete self-training implementation
- `shared/templates/experiment/spec.yaml`: Pre-registration template
- Platform experiment protocol: See experimenter agent instructions

---

## Contact and Updates

**Project**: self-improvement-limits
**Linear Issue**: [DW-77](https://linear.app/oddurs/issue/DW-77) (Design) and [DW-78](https://linear.app/oddurs/issue/DW-78) (Execution)
**Last Updated**: 2026-03-22
**Version**: 1.0
**Status**: Design complete, ready for execution

---

**Design Team**: Experimenter Agent
**Review**: Pending Critic review of experimental design
**Approval**: Ready for budget allocation and execution
