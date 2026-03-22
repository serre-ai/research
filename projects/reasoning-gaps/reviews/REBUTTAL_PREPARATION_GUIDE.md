# Rebuttal Preparation Guide

**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Venue**: NeurIPS 2026
**Date prepared**: 2026-03-22
**Expected rebuttal period**: July 2026

---

## Purpose

This document prepares for the eventual rebuttal phase by:
1. Anticipating common reviewer concerns for this type of paper
2. Documenting available resources for rapid response
3. Outlining potential additional experiments
4. Providing rebuttal workflow guidance

**Note**: This is preparatory work. The actual rebuttal will be written after receiving reviewer feedback (expected July 2026).

---

## Common Reviewer Concerns for Theory + Empirics Papers

Based on typical NeurIPS reviews for papers bridging theory and empirical evaluation:

### Theoretical Concerns

**1. Formalism rigor**
- "The formal framework relies on unproven complexity conjectures"
- "The connection to TC⁰ is informal/imprecise"
- "Propositions lack full proofs"

**Preparation**:
- ✅ All propositions have proof sketches (Appendix A)
- ✅ Conditional claims clearly stated ("if TC⁰ ≠ NC¹...")
- ✅ Standard complexity conjectures (widely assumed in theory community)
- **Ready**: Can expand any proof sketch to full proof if requested

**2. Expressiveness bounds**
- "Recent work shows transformers are Turing complete with sufficient context"
- "The TC⁰ bound may not apply to modern architectures"

**Preparation**:
- ✅ Paper cites Merrill & Sabharwal (2024) on CoT expressiveness
- ✅ Explicitly discusses saturated vs. practical transformers
- ✅ Framework focuses on practical limitations, not theoretical worst-case
- **Ready**: Can add discussion of Turing-completeness vs. practical capacity

### Empirical Concerns

**3. Model coverage**
- "Only 12 models evaluated; missing [specific model]"
- "Results may not generalize to future/larger models"

**Preparation**:
- ✅ 12 models across 5 families (Claude, GPT, Llama, Mistral, Qwen)
- ✅ Scale range: 7B to 123B+ parameters
- ✅ Includes reasoning-specialized models (o1-preview)
- **Ready**: Evaluation pipeline can add new models in ~6 hours
- **Cost**: ~$30-50 per additional model (full evaluation)

**4. Statistical rigor**
- "No confidence intervals reported"
- "Sample sizes too small"
- "Multiple comparisons not corrected"

**Preparation**:
- ✅ All results with 95% bootstrap CIs (10,000 resamples)
- ✅ Large sample sizes (159,162+ instances)
- ✅ Statistical tests pre-registered (primary.py)
- **Ready**: Can provide full statistical details, effect sizes, power analysis

**5. Benchmark validity**
- "Tasks are too artificial/simple"
- "Difficulty calibration unclear"
- "Ground truth verification?"

**Preparation**:
- ✅ All tasks have formal specifications (Appendix C)
- ✅ Difficulty parameters calibrated and varied
- ✅ Ground truth programmatically verified
- ✅ Validation set tested before full evaluation
- **Ready**: Can provide task design rationale, validation data

### Methodological Concerns

**6. CoT evaluation**
- "CoT prompts may be suboptimal"
- "Budget CoT calibration arbitrary"
- "Tool use comparison unfair?"

**Preparation**:
- ✅ Multiple CoT conditions (short, budget, tool use)
- ✅ Budget calibration based on theoretical bounds
- ✅ Tool use limited to Python execution (no cherry-picking)
- **Ready**: Can provide prompt variations, calibration analysis

**7. Result interpretation**
- "CoT lift could be due to [alternative explanation]"
- "Type-based differences may be confounded"
- "Missing ablations for [specific factor]"

**Preparation**:
- ✅ 6 primary analyses addressing alternative explanations
- ✅ Ablations: difficulty, scale, condition
- ✅ Cross-validation across model families
- **Ready**: Can run additional ablations (~$5-20 each)

### Presentation Concerns

**8. Clarity**
- "Framework too complex"
- "Notation inconsistent"
- "Figure X unclear"

**Preparation**:
- ✅ Notation table maintained (paper/notation.md)
- ✅ All figures with self-contained captions
- ✅ Framework motivated with examples
- **Ready**: Can revise any section, regenerate figures

**9. Related work**
- "Missing citation: [paper Y]"
- "Unfair comparison to [prior work]"
- "Positioning unclear vs. [concurrent work]"

**Preparation**:
- ✅ 40+ references across theory and empirics
- ✅ Literature review through March 2026 (notes/11-literature-update-march-13-2026.md)
- ✅ Fair acknowledgment of prior work strengths
- **Ready**: Can add citations, expand related work

---

## Resources for Rapid Response

### Experiment Infrastructure
All evaluation code is version-controlled and documented:

**Evaluation pipeline**:
- `benchmarks/experiments/run_full_analysis.py` - Master pipeline
- `benchmarks/experiments/eval_runner.py` - Model evaluation
- `benchmarks/experiments/primary.py` - Statistical analyses
- `benchmarks/experiments/viz_utils.py` - Visualization

**Adding a new model**:
1. Add API configuration to `benchmarks/config.yaml`
2. Run `python eval_runner.py --models new_model_name`
3. Re-run analysis: `python run_full_analysis.py`
4. Regenerate paper: `tectonic main.tex`

**Estimated time**: 4-6 hours (includes evaluation runtime)
**Estimated cost**: $30-50 (depending on model pricing)

### Additional Experiments

**Prepared but not yet run** (can execute if reviewers request):

**1. Extended scale analysis**
- Evaluate largest available models (GPT-5, Claude Opus 5, etc.)
- **Purpose**: Test if gaps persist at frontier scale
- **Cost**: $100-200
- **Time**: 8-12 hours

**2. Fine-grained difficulty sweep**
- More granular difficulty levels for B2, B3, B5
- **Purpose**: Identify exact phase transition points
- **Cost**: $10-20
- **Time**: 2-4 hours

**3. Prompt variation study**
- Systematic CoT prompt engineering (10+ variants per task)
- **Purpose**: Address "suboptimal prompt" concern
- **Cost**: $50-100
- **Time**: 12-24 hours

**4. Architecture ablations**
- Test different attention patterns (if API-accessible)
- **Purpose**: Isolate architectural vs. training factors
- **Cost**: Depends on model availability
- **Time**: Variable

**5. Human baseline**
- Recruit humans to solve tasks (via Prolific/MTurk)
- **Purpose**: Establish human performance ceiling
- **Cost**: $200-500 (depending on sample size)
- **Time**: 1-2 weeks

**6. Adversarial robustness**
- Paraphrase tasks, vary surface form
- **Purpose**: Show gaps are semantic, not superficial
- **Cost**: $20-50
- **Time**: 4-8 hours

### Analysis Variations

**Already implemented, can regenerate on demand**:

- Different confidence levels (90%, 95%, 99%)
- Alternative statistical tests (permutation, t-test)
- Different visualization styles
- Subgroup analyses (model family, scale tier)
- Correlation analyses
- Error case studies

**Implementation**: Modify parameters in `run_full_analysis.py`, re-run
**Time**: 5-15 minutes (plus analysis runtime ~30 min)

### Theoretical Extensions

**Can develop if requested**:

**1. Full formal proofs**
- Expand all proof sketches to rigorous proofs
- **Effort**: 2-4 days (per proposition)
- **Deliverable**: Extended appendix with complete proofs

**2. Tighter complexity bounds**
- Refine TC⁰/NC¹ characterizations
- **Effort**: 1-2 weeks
- **Deliverable**: Revised Section 3 with sharper bounds

**3. Alternative theoretical frameworks**
- Circuit complexity, formal languages, automata theory
- **Effort**: 1-2 weeks
- **Deliverable**: New appendix with alternative characterizations

---

## Rebuttal Workflow (When Reviews Arrive)

### Phase 1: Review Analysis (Day 1)
**Time budget**: 4-6 hours

1. **Read all reviews completely** (don't react immediately)
2. **Extract all concerns** into structured list
3. **Categorize each concern**:
   - Factual error in review (reviewer misunderstood)
   - Valid major issue (threatens acceptance)
   - Valid minor issue (easy fix)
   - Style/presentation preference
4. **Prioritize**: Major first, then minor, then style
5. **Identify common themes** across reviewers

### Phase 2: Response Planning (Day 1-2)
**Time budget**: 6-8 hours

For each concern:
1. **Determine response type**:
   - Clarification (reviewer misread paper)
   - Acknowledgment + fix (reviewer is right)
   - Rebuttal (reviewer is wrong, provide evidence)
   - Additional experiment (reviewer needs more data)
2. **Plan paper changes**:
   - Section to modify
   - What to add/remove/revise
   - Estimated effort
3. **Budget additional experiments**:
   - What experiment addresses concern
   - Cost and time estimate
   - Priority (must-have vs. nice-to-have)

### Phase 3: Additional Experiments (Day 2-5)
**Time budget**: Variable (depends on requests)

**Typical rebuttal period**: 7-10 days
**Available for experiments**: 3-5 days max

**Prioritization**:
- Only run experiments that address major concerns
- Prefer fast experiments ($<50, <12 hours)
- If expensive experiment needed, justify cost vs. acceptance likelihood

**Pre-approved budget for rebuttal experiments**: $200
(Remaining from $1,000 monthly budget: ~$535)

### Phase 4: Response Writing (Day 5-6)
**Time budget**: 8-12 hours

Use template: `shared/templates/paper/rebuttal.md`

**Structure**:
1. **Meta-summary** (1 paragraph): Thank reviewers, summarize changes
2. **Per-reviewer responses**:
   - Acknowledge overall assessment
   - Point-by-point responses
   - Clear, specific, respectful
   - Always reference paper changes or evidence
3. **Summary table**: All changes mapped to reviewer concerns
4. **Checklist**: Verify all points addressed

**Tone guidelines**:
- Professional, never defensive
- If reviewer is wrong, provide evidence politely
- If reviewer is right, acknowledge and thank them
- Focus on improving the paper, not "winning" the argument

### Phase 5: Paper Revision (Day 6-7)
**Time budget**: 6-10 hours

**Revision checklist**:
- [ ] All promised changes implemented
- [ ] No new claims without evidence
- [ ] Revised sections read coherently
- [ ] Figures/tables regenerated if needed
- [ ] References updated
- [ ] Compile successfully
- [ ] Read end-to-end for consistency

**Git workflow**:
```bash
git checkout -b revision/neurips-2026-rebuttal
# Make all changes
git add -A
git commit -m "paper(reasoning-gaps): address reviewer feedback"
tectonic main.tex
git add main.pdf
git commit -m "paper(reasoning-gaps): compile revised version"
git push origin revision/neurips-2026-rebuttal
```

### Phase 6: Submission (Day 7)
**Time budget**: 1-2 hours

**OpenReview rebuttal submission**:
1. Navigate to paper submission page
2. Upload rebuttal document (markdown or PDF)
3. Upload revised PDF (if allowed)
4. Submit before deadline
5. Save confirmation

**Double-check**:
- All reviewer concerns addressed in rebuttal
- Rebuttal matches paper changes
- No promises we can't keep in camera-ready version

---

## Anticipated Review Scenarios

### Scenario 1: Mostly Positive (Accept/Weak Accept)
**Likely concerns**: Minor clarifications, presentation improvements
**Response strategy**: Quick fixes, grateful tone, minor revisions
**Additional experiments**: Unlikely needed
**Effort**: Low (1-2 days)

### Scenario 2: Mixed (Borderline)
**Likely concerns**: One major issue + several minor issues
**Response strategy**:
- Address major issue definitively (experiment if needed)
- Fix all minor issues
- Show paper is strong overall
**Additional experiments**: 1-2 focused experiments (~$50, 1-2 days)
**Effort**: Medium (3-5 days)

### Scenario 3: Skeptical (Weak Reject)
**Likely concerns**: Fundamental questions about framework or empirics
**Response strategy**:
- Substantial additional evidence
- Multiple experiments addressing concerns
- Possible theoretical extension
- Show reviewers' concerns are addressable
**Additional experiments**: 2-4 experiments (~$100-150, 3-4 days)
**Effort**: High (5-7 days)

### Scenario 4: Reject (Strong Reject)
**Likely concerns**: Fatal flaws, unfixable in rebuttal period
**Response strategy**:
- Clarify misunderstandings if possible
- Acknowledge limitations honestly
- Argue strengths outweigh weaknesses
- Prepare for rejection, plan revision for next venue
**Additional experiments**: Only if they address fatal flaw
**Effort**: Variable

---

## Budget Reserve for Rebuttal

### Current Budget Status
- **Monthly budget**: $1,000
- **Spent so far**: ~$465
- **Remaining**: ~$535

### Rebuttal Budget Allocation
- **Reserve for rebuttal experiments**: $200
- **Reserve for extended evaluations**: $150
- **Reserve for human baseline (if needed)**: $100
- **Emergency reserve**: $85

### Cost Estimates by Experiment Type
- **Single model, full evaluation**: $30-50
- **Single task, difficulty sweep**: $5-10
- **Prompt variation study (1 task, 10 variants)**: $10-20
- **Extended scale (frontier model)**: $50-100
- **Human baseline (100 participants)**: $200-500

---

## Checklist for Rebuttal Readiness

### Infrastructure
- [x] Evaluation pipeline documented and tested
- [x] Analysis scripts version-controlled
- [x] Figure generation automated
- [x] Paper compilation verified
- [x] All data backed up

### Documentation
- [x] All experiments documented (notebooks, scripts)
- [x] Benchmark specifications formal (Appendix C)
- [x] Statistical methods pre-registered (primary.py)
- [x] Notation table maintained
- [x] Related work up-to-date (through March 2026)

### Resources
- [x] Rebuttal template available
- [x] API access for all models verified
- [x] Budget allocated for additional experiments
- [x] Time blocked for rebuttal week (July 2026)

### Preparation
- [x] Common concerns anticipated
- [x] Response strategies outlined
- [x] Experiment menu prepared
- [x] Workflow documented

---

## Timeline Summary

**Current date**: 2026-03-22

**Upcoming milestones**:
1. **April 5, 2026**: OpenReview portal opens
2. **May 4, 2026**: Abstract submission deadline
3. **May 6, 2026**: Full paper submission deadline
4. **May 7 - July 15, 2026**: Review period (~10 weeks)
5. **Mid-July 2026**: Rebuttal period begins ← **DW-104 executes here**
6. **Late July 2026**: Rebuttal deadline (~1 week window)
7. **August 2026**: Author notification
8. **October 2026**: Camera-ready deadline (if accepted)
9. **December 6-12, 2026**: NeurIPS conference

**Next action**: Wait for portal opening (April 5), then submit paper.

---

## Contact

**Primary author**: (Anonymized for review)
**Repository**: https://github.com/oddurs/deepwork (private during review)
**OpenReview**: Will be available after submission

---

**Prepared by**: Writer Agent
**Date**: 2026-03-22
**Status**: Ready for rebuttal phase (when it arrives)
**Next review**: July 2026 (after receiving reviewer feedback)
