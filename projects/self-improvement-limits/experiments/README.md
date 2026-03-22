# Empirical Validation Experiments
## Self-Improvement Limits Project

**Status**: Design complete, ready for execution
**Budget**: ~$200 (platform allocation)
**Linear Issues**: [DW-77](https://linear.app/oddurs/issue/DW-77) (Design), [DW-78](https://linear.app/oddurs/issue/DW-78) (Execution)

---

## Overview

This directory contains all empirical validation experiments for the self-improvement-limits paper. Our goal is to validate theoretical impossibility results through controlled experiments on tasks with varying generation-verification gaps.

**What We're Testing:**
- **Theorem 1**: Self-improvement converges to γ_∞ ≤ ν_0 + ε
- **Theorem 2**: Capability gain bounded by verification capability
- **Theorem 3**: Improvement inversely related to GV-gap
- **Theorem 4**: Self-play can exceed self-training bounds

---

## Quick Start

### For Reviewers: See Simulation Results

Already completed simulation validates the methodology:

```bash
cd self-training-validation
python run_simulated_experiment.py
open results/simulated/convergence_trajectories.png
```

**Result**: All theoretical predictions confirmed (see `self-training-validation/SIMULATION-REPORT.md`)

### For Execution: Run Real Experiments

```bash
# 1. Set API key
export ANTHROPIC_API_KEY="your-key-here"

# 2. Run canary (validates pipeline, ~$5)
cd self-training-validation
python run_experiment.py --task gsm8k --mode canary

# 3. If canary passes, run full experiments (~$150)
python run_experiment.py --task gsm8k --mode full
python run_experiment.py --task humaneval --mode full
python run_experiment.py --task writingprompts --mode full
```

---

## Directory Structure

```
experiments/
├── README.md                          # This file
├── EXPERIMENT-DESIGN.md               # Complete experimental design (all mechanisms)
│
├── self-training-validation/          # Self-training experiments (Theorems 1-3)
│   ├── spec.yaml                      # Pre-registration specification
│   ├── README.md                      # Execution guide
│   ├── run_experiment.py              # Full experiment runner (API-based)
│   ├── run_simulated_experiment.py   # Simulation (no cost)
│   ├── SIMULATION-REPORT.md           # Simulation results & analysis
│   ├── SESSION-SUMMARY-2026-03-22.md  # Design session report
│   └── results/
│       ├── simulated/                 # Simulation outputs (complete)
│       │   ├── convergence_trajectories.png
│       │   ├── simulated_gsm8k.json
│       │   ├── simulated_humaneval.json
│       │   └── simulated_writingprompts.json
│       └── full/                      # Real experiment outputs (pending)
│
└── [Future: self-refinement-validation/]
    [Future: self-play-validation/]
    [Future: constitutional-ai-validation/]
```

---

## Experiment Status

### Part 1: Self-Training (Critical Priority)

**Status**: ✓ Design complete, ✓ Implementation complete, ✓ Simulation complete
**Budget**: $100-150
**Location**: `self-training-validation/`
**Tests**: Theorems 1, 2, 3

| Task | Gap | Status | Cost |
|------|-----|--------|------|
| GSM8K | 0.20 (moderate) | Simulated ✓ | $50 |
| HumanEval | 0.10 (small) | Simulated ✓ | $25 |
| WritingPrompts | 0.50 (large) | Simulated ✓ | $25 |

**Key Results (Simulation)**:
- All tasks converged within 10 iterations ✓
- γ_∞ ≤ ν_0 + ε holds for all tasks ✓
- Small gap → larger improvement (HumanEval: 7.1%, WritingPrompts: 0.2%) ✓

**Next Step**: Run real experiments (requires $150 budget allocation)

### Part 2: Self-Refinement (High Priority)

**Status**: ✓ Design complete, ⏳ Implementation pending
**Budget**: $35-50
**Location**: Not yet created
**Tests**: Theorem 2 (iterative improvement variant)

| Task | Gap | Predicted Improvement |
|------|-----|----------------------|
| Code Debugging | 0.15 (small) | High |
| Math Problem Solving | 0.20 (moderate) | Moderate |
| Essay Writing | 0.45 (large) | Low |

**Design**: See `EXPERIMENT-DESIGN.md` Part 2
**Next Step**: Implement experiment code after Part 1 complete

### Part 3: Self-Play (Medium Priority)

**Status**: ✓ Design complete, ⏳ Implementation pending
**Budget**: $40-80
**Location**: Not yet created
**Tests**: Theorem 4 (self-play separation)

| Task | Type | Tests |
|------|------|-------|
| Mathematical Proofs | Debate | Self-play > self-training |
| Factual Claims | Debate | Implicit verification via contradiction |

**Design**: See `EXPERIMENT-DESIGN.md` Part 3
**Next Step**: Implement after Parts 1-2 if budget allows

### Part 4: Constitutional AI (Low Priority)

**Status**: ✓ Design complete, ⏳ Implementation pending
**Budget**: $20-30
**Location**: Not yet created
**Tests**: Self-refinement variant with principles

**Design**: See `EXPERIMENT-DESIGN.md` Part 4
**Next Step**: Optional, if budget and time permit

---

## Design Philosophy

### Pre-Registration

All experiments follow rigorous pre-registration protocol to prevent p-hacking:

1. **Hypotheses specified before execution** (in `spec.yaml`)
2. **Metrics and analyses pre-defined** (no post-hoc changes)
3. **Canary validation required** (pipeline must work before full run)
4. **Report all results** (including null results)

See `shared/templates/experiment/spec.yaml` for template.

### Controlled Validation

We test theory on **controlled tasks** with known properties:

- **Arithmetic/Math**: Easy verification (check answer) → small gap
- **Code**: Easy verification (run tests) → small gap
- **Logic**: Moderate verification (check reasoning) → moderate gap
- **Creative Writing**: Hard verification (subjective quality) → large gap

This allows us to **vary the gap systematically** and test Theorem 3's prediction: small gap → large improvement.

### Efficient Implementation

To stay within $200 budget:

- **In-context learning** instead of fine-tuning (5× cheaper)
- **Small test sets** (50-100 instances per task)
- **Parallel execution** where possible
- **Canary runs** validate costs before full execution
- **Checkpoint system** prevents wasted work on crashes

---

## Key Metrics

### Primary Metrics (All Experiments)

| Metric | Symbol | Measures |
|--------|--------|----------|
| **Generation accuracy** | γ_t | Model capability at iteration t |
| **Verification accuracy** | ν_t | Model's ability to judge quality |
| **Convergence iteration** | t_conv | When improvement plateaus |
| **Fixed point** | γ_∞ | Final converged capability |
| **Relative improvement** | Δ | (γ_∞ - γ_0) / γ_0 |
| **Gap size** | g_D | Verification - generation difficulty |

### Validation Criteria

**Theorem 1**: γ_∞ ≤ ν_0 + ε for all tasks
**Theorem 3**: Spearman correlation between g_D and Δ should be negative (r < -0.75)
**Theorem 4**: γ_∞^self-play > γ_∞^self-training (statistically significant)

---

## Budget Plan

### Phase 1: Minimum Viable Validation ($135-200)

**Resolves FATAL issue #1 from internal review**

- Self-training experiments: $100-150
- Self-refinement experiments: $35-50
- **Total**: $135-200
- **Impact**: +2.0 points on review score (5.26 → 7.26)

### Phase 2: Full Validation ($60-110, Optional)

**Strengthens paper for top-tier acceptance**

- Self-play experiments: $40-80
- Constitutional AI experiments: $20-30
- **Total**: $60-110
- **Impact**: +0.5 points on review score (7.26 → 7.76)

### Budget Allocation Strategy

1. **Run Phase 1 first** (critical experiments)
2. **Evaluate results** (do they confirm theory?)
3. **Decide on Phase 2** based on:
   - Remaining budget
   - Phase 1 results quality
   - Time until submission deadline
   - Reviewer feedback (if applicable)

---

## Timeline

### Completed (2026-03-22)

- [x] Experimental design (all mechanisms)
- [x] Self-training implementation
- [x] Self-training simulation
- [x] Validation of methodology

### Next Steps (Week 1-2)

- [ ] Budget allocation ($150-200)
- [ ] Run canary experiment (GSM8K)
- [ ] Run full self-training experiments
- [ ] Generate figures and analysis

### Future (Weeks 3-4, Optional)

- [ ] Implement self-refinement code
- [ ] Run self-refinement experiments
- [ ] Cross-mechanism analysis
- [ ] Write supplementary materials

---

## Success Criteria

### Minimum Success (MVP)

To resolve FATAL issue #1 and achieve Accept:

✅ **Must have**:
- Real experimental results (not simulation)
- Validation of Theorems 1 and 3
- Publication-quality figures
- Statistical tests confirming predictions

📊 **Impact**: Predicted score 7.0-7.5/10 (Accept)

### Full Success

To achieve strong Accept or spotlight:

✅ **Should have**:
- Validation across multiple mechanisms
- Cross-mechanism comparisons
- Validation against published results (STaR, ReST)
- Comprehensive supplementary materials

📊 **Impact**: Predicted score 7.5-8.5/10 (Strong Accept)

---

## How to Execute

### Prerequisites

```bash
# Install dependencies
pip install anthropic numpy pandas matplotlib scipy datasets

# Set API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Running Experiments

#### Step 1: Canary Run (~$5, 1 hour)

Validates pipeline before committing to full budget:

```bash
cd self-training-validation
python run_experiment.py \
  --task gsm8k \
  --mode canary \
  --output-dir results/canary

# Check diagnostics
cat results/canary/gsm8k_canary_diagnostics.json
```

**Pass criteria**:
- ✓ 100% pipeline completion (no crashes)
- ✓ Reasonable accuracy (0.1 < γ_0 < 0.9)
- ✓ Verification gap exists (ν_0 > γ_0 + 0.05)
- ✓ Cost within 2× estimate

#### Step 2: Full Experiments (~$150, 4-6 hours)

If canary passes:

```bash
# Run all tasks in parallel (if budget allows)
for task in gsm8k humaneval writingprompts; do
  python run_experiment.py \
    --task $task \
    --mode full \
    --output-dir results/full &
done

# Wait for completion
wait

# Generate analysis
python analyze_results.py --input-dir results/full
```

#### Step 3: Review Results

```bash
# View figures
open results/full/convergence_trajectories.png
open results/full/gap_improvement_correlation.png

# Read analysis
cat results/full/statistical_analysis.md
```

---

## Troubleshooting

### Canary Fails: Accuracy = 0%

**Diagnosis**: Prompt formatting or evaluation bug

**Fix**:
1. Inspect first 5 generated solutions manually
2. Check answer extraction logic
3. Verify ground truth is correct
4. Revise prompts and re-run canary

### Canary Fails: No Verification Gap

**Diagnosis**: Task too hard or too easy for model

**Fix**:
1. Try different model (GPT-4 instead of Claude)
2. Adjust task difficulty
3. Use alternative task with clearer gap

### Results Don't Match Theory

**Diagnosis**: Could be bug or genuine anomaly

**Action**:
1. ✓ Check evaluation code for bugs
2. ✓ Inspect individual instances for patterns
3. ✓ If bug: fix and re-run
4. ✓ If genuine: report as finding (anomalies are interesting!)
5. ✗ DO NOT modify analysis to fit theory (p-hacking)

### Budget Exceeded

**Diagnosis**: API usage higher than estimated

**Fix**:
1. Reduce sample size (500 → 250 per iteration)
2. Reduce iterations (10 → 5)
3. Use cheaper model (Sonnet → Haiku)
4. Implement streaming/batching for efficiency

---

## Related Documents

**Design Documents**:
- `EXPERIMENT-DESIGN.md` - Complete experimental design (all mechanisms)
- `self-training-validation/spec.yaml` - Self-training pre-registration
- `self-training-validation/README.md` - Self-training execution guide

**Analysis Reports**:
- `self-training-validation/SIMULATION-REPORT.md` - Simulation results
- `self-training-validation/SESSION-SUMMARY-2026-03-22.md` - Design session report

**Platform Resources**:
- `../../BRIEF.md` - Project goals and hypotheses
- `../../status.yaml` - Project status and decisions
- `../../../shared/templates/experiment/spec.yaml` - Pre-registration template

---

## Citation

If using this experimental design:

```bibtex
@misc{sil-experiments-2026,
  title={Empirical Validation of Self-Improvement Limits: Experimental Design},
  author={DeepWork Research Platform},
  year={2026},
  note={Project: self-improvement-limits, Issues: DW-77, DW-78},
  url={https://github.com/deepwork-research/self-improvement-limits}
}
```

---

## Contact

**Project**: self-improvement-limits
**Linear Issues**: [DW-77](https://linear.app/oddurs/issue/DW-77), [DW-78](https://linear.app/oddurs/issue/DW-78)
**Last Updated**: 2026-03-22
**Version**: 1.0
**Status**: Design complete, ready for execution

For questions or issues, see project documentation or Linear issues.
