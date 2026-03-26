# Self-Improvement-Limits: Action Plan
**Updated**: 2026-03-26
**Status**: Revision phase — fixing draft v0.1 with 3 FATAL issues
**Timeline**: 6-10 weeks to submission-ready

---

## Current State

- **Paper**: 1600-line draft v0.1 (~45% complete)
- **Internal review score**: 5.26/10 (Reject to Borderline)
- **Target after fixes**: 7.6/10 (Accept, ~80% probability)
- **Issues**: 3 FATAL + 7 major (all fixable)

---

## Immediate Actions (This Week)

### 1. DECISION REQUIRED (By 2026-03-29)

**Choose experiment option for Section 5:**

- **Option A: Conduct real experiments** [RECOMMENDED]
  - Cost: $200-500
  - Timeline: 2-4 weeks
  - Impact: +2.0-3.0 points → 7.6/10 (Accept)
  - Acceptance probability: ~80%

- **Option B: Remove Section 5**
  - Cost: $0
  - Timeline: 1 day
  - Impact: 0 to -0.5 points → 6.0-6.5/10 (Borderline)
  - Acceptance probability: ~60%

- **Option C: Reframe as predictions**
  - Cost: $0
  - Timeline: 2 days
  - Impact: +0.2 points → 5.5-5.8/10 (Reject to Borderline)
  - Acceptance probability: ~40%

**Budget context**: $1000/month available, Option A is 20-50% of monthly budget

**Who decides**: User/Strategist

### 2. START IMMEDIATELY (Doesn't depend on decision)

#### Dispatch Researcher for Validation
- **Task**: Validate framework against published results
- **Reference**: `literature/VALIDATION-TASK.md`
- **Timeline**: 1 week
- **Cost**: ~$10-15
- **Priority**: HIGH
- **Papers to analyze**: STaR, ReST, Constitutional AI, AlphaGo
- **Deliverable**: Section 5.X draft (1.5-2 pages)
- **Impact**: +1.0 point (resolves Major Issue #5)

#### Dispatch Theorist for Proofs
- **Task**: Complete rigorous proofs for Theorems 1-4
- **Reference**: `proofs/PROOF-COMPLETION-TASK.md`
- **Timeline**: 2-4 weeks
- **Cost**: ~$20-40
- **Priority**: CRITICAL
- **Start with**:
  1. Lemma A.1 (verification boundedness)
  2. Corollary 1.1 (characterize ε)
  3. Justify Assumption 2
  4. Characterize f(g_D) in Theorem 3
  5. Formalize Theorem 4 (lower priority)
- **Impact**: +2.5-3.5 points (resolves FATAL Issues #2 and #3)

### 3. AFTER EXPERIMENT DECISION

#### If Option A: Dispatch Experimenter
- **Task**: Run designed experiments
- **Reference**: `experiments/EXPERIMENT-DESIGN.md` + existing code
- **Timeline**: 2-4 weeks
- **Cost**: $200-500
- **Tasks**:
  - Run self-training on GSM8K, HumanEval
  - Measure γ_t and ν_t over iterations
  - Generate Figure 1
  - Validate convergence predictions
  - Rewrite Section 5 with real results
- **Impact**: +2.0-3.0 points (resolves FATAL Issue #1)

#### If Option B/C: Dispatch Writer
- **Task**: Remove or reframe Section 5
- **Timeline**: 1-2 days
- **Cost**: ~$5
- **Impact**: Minimal (leaves FATAL Issue #1 unresolved or weakly addressed)

---

## Work Streams (Parallel Execution)

### Stream 1: Researcher (1 week)
✅ **Can start immediately**
- Validate against STaR, ReST, Constitutional AI, AlphaGo
- Extract empirical data from published results
- Compare to framework predictions
- Write Section 5.X with case studies
- **Status**: Ready to dispatch

### Stream 2: Theorist (2-4 weeks)
✅ **Can start immediately**
- Week 1-2: Lemma A.1 + Corollary 1.1 (most critical)
- Week 2: Justify Assumption 2
- Week 2-3: Characterize f(g_D) (hardest)
- Week 3-4: Formalize Theorem 4 (lower priority)
- **Status**: Ready to dispatch

### Stream 3: Experimenter (2-4 weeks)
⏳ **Blocked on experiment decision (due 2026-03-29)**
- If Option A: Run experiments, generate results, rewrite Section 5
- If Option B/C: Skip or minimal work
- **Status**: Waiting for decision

### Stream 4: Writer (1-2 weeks)
⏳ **Blocked on proof completion + experiment completion**
- Reframe "impossibility" claim (less overclaimed)
- Add practitioner's guide (operationalize Ver_M, Gen_M)
- Add caveats to safety discussion
- Polish notation, citations, figures
- **Status**: Will dispatch after Streams 1-3 complete

---

## Success Criteria

### Week 1-2 Milestones
- [ ] Experiment decision made (Option A/B/C)
- [ ] Researcher: 3-4 papers analyzed, validation note written
- [ ] Theorist: Lemma A.1 drafted, Corollary 1.1 started

### Week 3-4 Milestones
- [ ] Researcher: Section 5.X drafted (1.5-2 pages)
- [ ] Theorist: Lemma A.1 proved, Corollary 1.1 complete, Assumption 2 justified
- [ ] Experimenter (if A): Self-training experiments run on 2+ tasks

### Week 5-6 Milestones
- [ ] Theorist: f(g_D) characterized, Theorem 4 drafted
- [ ] Experimenter (if A): Figure 1 generated, Section 5 rewritten
- [ ] Writer: Presentation revision started

### Week 7-8 Milestones
- [ ] Writer: All major issues addressed
- [ ] All FATAL issues resolved
- [ ] Paper score ≥ 7.5/10 by internal assessment

### Week 9-10 (Buffer)
- [ ] Final polish complete
- [ ] Submission-ready

---

## Critical Paths

### Path to Submission-Ready (FATAL issues must be resolved)

```
┌─────────────────────────────────────────────────────┐
│ FATAL Issue #1: Experiments                        │
│ Resolution: Option A (conduct), B (remove), or C   │
│ Critical: YES — blocks submission                   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ FATAL Issue #2: Incomplete proofs                  │
│ Resolution: Complete Theorems 1-4 (2-4 weeks)      │
│ Critical: YES — blocks submission                   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ FATAL Issue #3: Uncharacterized ε                  │
│ Resolution: Corollary 1.1 (part of Issue #2)       │
│ Critical: YES — blocks submission                   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ Major Issues #4-10: Presentation                    │
│ Resolution: Writer revisions (1-2 weeks)            │
│ Critical: NO — but needed for strong acceptance     │
└─────────────────────────────────────────────────────┘
                          ↓
                 Submission-Ready
                 (6-10 weeks from now)
```

**Longest pole**: Proof completion (2-4 weeks)
**Second longest**: Experiments if Option A (2-4 weeks, but can run parallel to proofs)

---

## Budget Summary

### If Option A (Recommended)
- Researcher validation: $10-15
- Theorist proofs: $20-40
- Experimenter runs: $200-500
- Writer revision: $10-15
- **Total: $240-570**

### If Option B/C (Fallback)
- Researcher validation: $10-15
- Theorist proofs: $20-40
- Writer revision: $10-15
- **Total: $40-70**

**Budget available**: $1000/month
**Verdict**: Option A is well within budget

---

## Timeline Estimates

- **Optimistic**: 6 weeks (by 2026-05-05)
- **Realistic**: 8 weeks (by 2026-05-19)
- **Conservative**: 10 weeks (by 2026-06-02)
- **ICLR 2027 deadline**: ~Sep/Oct 2026
- **Buffer**: 16-20 weeks (very comfortable)

---

## Risk Mitigation

### Risk: Proofs harder than expected
- **Mitigation**: Prioritize critical proofs (Lemma A.1, Corollary 1.1), accept weaker Theorem 4
- **Fallback**: Submit with informal Theorem 4 (self-play as secondary result)

### Risk: Experiments don't validate theory
- **Mitigation**: Explain deviations, add caveats to theorems
- **Fallback**: Reframe as "bounds under specific conditions"

### Risk: Concurrent work scoops contribution
- **Mitigation**: Monitor arXiv during validation task
- **Fallback**: Emphasize distinctive contribution (g-v gap, self-play separation)

### Risk: Experiment budget exceeds $500
- **Mitigation**: Phase experiments (self-training first ~$150, then assess)
- **Fallback**: Option B (remove Section 5)

---

## Key Reference Documents

- **Project files**:
  - `BRIEF.md` — project goals and hypotheses
  - `status.yaml` — current state (NOW ACCURATE as of 2026-03-26)
  - `CLAUDE.md` — agent instructions

- **Paper draft**:
  - `paper/main.tex` (574 lines)
  - `paper/supplementary.tex` (1026 lines)

- **Task specifications** (ready for dispatch):
  - `literature/VALIDATION-TASK.md` — Researcher validation work
  - `proofs/PROOF-COMPLETION-TASK.md` — Theorist proof work

- **Theory notes**:
  - `notes/01-fixed-point-characterization.md`
  - `notes/02-generation-verification-gap-characterization.md`
  - `notes/03-self-training-convergence-proof-strategy.md`
  - `notes/NEXT-STEPS-THEORIST.md`

- **Experiments**:
  - `experiments/EXPERIMENT-DESIGN.md`
  - `experiments/run_experiment.py`
  - `experiments/SIMULATION-REPORT.md`

- **Reviews**:
  - `reviews/internal-review-simulation-2026-03-22.md` (comprehensive)
  - `reviews/review-synthesis-2026-03-22.md` (summary)
  - `reviews/revision-roadmap-2026-03-22.md` (fix strategy)

- **Meta-reviews**:
  - `notes/00-meta-review-diagnosis-2026-03-24.md` (diagnosis)
  - `notes/04-meta-review-status-fix-2026-03-26.md` (this session)
  - `NEXT-SESSION-RECOMMENDATIONS.md` (from 2026-03-24)

---

## DO NOT Repeat These Failed Approaches

❌ **Don't**: Survey literature "from scratch" — already embedded in paper
❌ **Don't**: Build formal framework "from scratch" — Section 3 complete
❌ **Don't**: Design experiments "from scratch" — already designed
❌ **Don't**: Write paper "from scratch" — revise existing draft
❌ **Don't**: Dispatch agents without clear task specifications
❌ **Don't**: Claim status is "not_started" when work exists

✅ **Do**: Fix what exists, validate against published results, complete proofs, run experiments
✅ **Do**: Reference task specification files (VALIDATION-TASK.md, PROOF-COMPLETION-TASK.md)
✅ **Do**: Dispatch Researcher and Theorist immediately (unblocked)
✅ **Do**: Make experiment decision by 2026-03-29
✅ **Do**: Track progress in status.yaml

---

## Contact / Questions

If unsure about next steps:
1. Read `notes/04-meta-review-status-fix-2026-03-26.md` (comprehensive analysis)
2. Check `status.yaml` for current state (NOW ACCURATE)
3. Review task specifications in `literature/VALIDATION-TASK.md` and `proofs/PROOF-COMPLETION-TASK.md`

**Project is unblocked and ready for execution.**
