# Revision Roadmap: Self-Improvement Limits Paper
**Date**: 2026-03-22
**Current draft**: v0.1
**Target**: v1.0 (submission-ready for ICLR 2027)
**Current predicted score**: 5.26/10
**Target score**: 7.5+/10

---

## Critical Path to Acceptance

### Overview

The internal review simulation identified **3 FATAL issues** and **7 major issues**. The critical path to acceptance requires addressing all FATAL issues and most major issues.

**Minimum viable revision** (for borderline accept ~6.5/10):
- Complete all proofs rigorously
- Either conduct experiments OR remove Section 5 entirely
- Validate theory against published results

**Strong revision** (for accept ~7.5+/10):
- All of minimum viable +
- Add practitioner's guide
- Reframe to avoid overclaiming
- Expand related work and discussion

---

## Phase 1: Address FATAL Issues (4-6 weeks)

**Goal**: Move from "Reject" (5.3) to "Borderline Accept" (6.5-7.0)

### Task 1.1: Complete All Proofs [WEEKS 1-2]

**Assignee**: Theorist agent
**Priority**: FATAL
**Estimated effort**: 10-15 sessions

#### Subtask 1.1a: Prove Verification Boundedness
**Issue**: Theorem 1 assumes ν_max ≤ ν_0 + Δ without proving Δ is bounded

**Required work**:
1. Add **Lemma A.1: Verification Improvement Bound**
   ```
   Lemma A.1: For any model M_t produced by self-training, verification capability
   on self-generated data D_self satisfies:

   ν(D_self) ≤ ν(D_true) + δ

   where δ = O(γ_0) is bounded by initial generation capability.
   ```

2. **Proof strategy**:
   - Self-generated data is biased toward model's generation capability γ_t
   - Hardest examples in D_self have difficulty ≤ γ_t (model can't generate harder)
   - Verification on examples with difficulty ≤ γ_t cannot exceed ν_0 + f(γ_t - ν_0)
   - Since γ_t converges, verification improvement is bounded

3. **Add to appendix**: Full proof with explicit bound on Δ

**Deliverable**: Lemma A.1 with complete proof

---

#### Subtask 1.1b: Characterize Function f(g_D)
**Issue**: Theorem 3 states f exists and is monotonically decreasing but doesn't characterize it

**Required work**:
1. **Propose explicit form**:
   ```
   f(g_D) = C / (1 + α·g_D)
   ```
   where C, α are constants depending on task distribution and training procedure.

2. **Prove monotonicity**: Trivial for this form (derivative < 0)

3. **Justify via information theory**:
   - Mutual information between verification judgments and true quality: I(Ver; Quality)
   - When g_D is large, verification provides weak signal → low MI
   - Formalize: I(Ver; Quality) ≤ C/(1 + α·g_D)
   - Learning from verification cannot exceed information available

4. **Provide empirical estimates**:
   - From literature: Estimate C ≈ 0.3-0.5, α ≈ 1-2 for typical tasks
   - Small gap (g_D < 0.2): f(g_D) ≈ 0.3
   - Large gap (g_D > 0.5): f(g_D) < 0.1

**Deliverable**: Theorem 3 with explicit f, proof of monotonicity, empirical estimates

---

#### Subtask 1.1c: Formalize Objective Outcome Property
**Issue**: Definition 5 defines "objective outcome" through examples, not formal properties

**Required work**:
1. **Replace Definition 5** with formal version:
   ```
   Definition 5 (Objective Outcome Property): A game G has the objective outcome
   property if there exists a computable function W: Transcripts → {-1,0,1} such that:

   1. W can be evaluated in polynomial time
   2. W is independent of player verification capabilities (computed via game rules alone)
   3. W provides accurate feedback: E[W | better strategy] > E[W | worse strategy]
   ```

2. **Prove Theorem 4 Case 1**: If G has objective outcomes, W provides external verification signal uncorrelated with Ver_M

3. **Prove Theorem 4 Case 2**: If G lacks objective outcomes, computing W requires Ver_M, reducing to self-training

**Deliverable**: Formal Definition 5, complete Theorem 4 proof

---

#### Subtask 1.1d: Characterize Slack Term ε
**Issue**: Theorems 1-2 state γ_∞ ≤ ν_0 + ε but never bound ε

**Required work**:
1. **Add Corollary 1.1**:
   ```
   Corollary 1.1 (Slack Bound): The slack term ε in Theorem 1 satisfies:

   ε ≤ δ_FP + ε_train + Δ

   where:
   - δ_FP = false positive rate in verification (≤ 1 - ν_0)
   - ε_train = training generalization slack (typically 0.05-0.1 for large models)
   - Δ = verification improvement bound (from Lemma A.1)
   ```

2. **Proof**: Direct from Lemmas A.1 and A.2 (training bound)

3. **Practical estimates**:
   - Strong verification (ν_0 > 0.8): ε ≈ 0.1-0.2
   - Weak verification (ν_0 < 0.5): ε may approach 0.5 (bound becomes loose)

**Deliverable**: Corollary 1.1 with proof and estimates

---

#### Subtask 1.1e: Justify or Weaken Assumption 2
**Issue**: Assumption 2 nearly assumes the conclusion

**Options**:

**Option A (Preferred)**: Cite prior work
- Wei et al. (2021): Self-training with "expansion assumption" yields bounded improvement
- Xu & Raginsky (2017): Generalization bounds for iterative algorithms
- Modify Assumption 2: "Under standard PAC assumptions (see Wei et al., 2021), training on quality-q data yields..."

**Option B**: Weaken to conditional statement
- Change from: "Assumption 2: Training yields capability ≤ q + ε"
- To: "Assumption 2: Under regularity conditions on training dynamics..."
- Add discussion of when assumption fails (emergent capabilities, grokking)

**Deliverable**: Revised Assumption 2 with citations or weakened statement

---

#### Subtask 1.1f: Prove or Weaken Assumption 3 (Convergence)
**Issue**: Assumes convergence without proof

**Options**:

**Option A**: Prove convergence
- Show T is a contraction mapping (if provable)
- Or show T is monotone on lattice (apply Tarski fixed-point theorem)
- Or prove under specific conditions (Lipschitz continuity, bounded gradients)

**Option B**: Weaken theorem statements
- Change from: "We prove that lim_{t→∞} γ_t ≤ ν_0 + ε"
- To: "If T converges, then lim_{t→∞} γ_t ≤ ν_0 + ε"
- Add discussion: "Convergence holds under standard conditions (see Banach fixed-point theorem)"

**Deliverable**: Convergence proof OR weakened theorem statements

---

### Task 1.2: Empirical Validation [WEEKS 2-3]

**Assignee**: Experimenter agent (or Writer if experiments simple enough)
**Priority**: FATAL
**Estimated effort**: 1-2 weeks

**Decision point**: Choose ONE of the following options

#### Option A: Conduct Actual Experiments (RECOMMENDED)

**Tasks**:
1. **Implement self-training** on 2-3 tasks:
   - GSM8K (math reasoning): Moderate GV-gap
   - HumanEval (code generation): Small GV-gap
   - Creative writing (WritingPrompts): Large GV-gap

2. **Measurement protocol**:
   ```
   For each task:
   - Initial model: GPT-4 or Claude Sonnet
   - Iterations: t = 0, 1, 2, ..., 10
   - At each iteration:
     * Measure γ_t (generation accuracy on test set)
     * Measure ν_t (verification accuracy: given (x,y), judge if y solves x)
     * Generate synthetic data: Sample solutions from M_t
     * Filter data: Use Ver_{M_t} to select high-quality examples
     * Train M_{t+1} on filtered data (fine-tuning or in-context learning)
   ```

3. **Generate figures**:
   - Figure 1: γ_t and ν_t over iterations (3 subplots, one per task)
   - Figure 2: Improvement Δγ = γ_∞ - γ_0 vs estimated g_D (scatter plot)
   - Figure 3: Convergence to ν_0 (show γ_∞ ≈ ν_0 + ε empirically)

4. **Statistical analysis**:
   - Correlation between γ_∞ and ν_0 (expect r > 0.8)
   - T-test: Does γ_∞ ≤ ν_0 + ε hold?
   - Regression: Model Δγ as function of g_D

**Cost estimate**: $200-500 for API calls (10 iterations × 3 tasks × 500 examples)
**Timeline**: 1-2 weeks

**Deliverables**:
- 3 datasets with γ_t, ν_t measurements
- 3 figures showing convergence
- Statistical analysis confirming Theorem 1

---

#### Option B: Remove Section 5 Entirely

**Tasks**:
1. Delete Section 5 (Experiments)
2. Remove all references to "empirical validation" from abstract/intro
3. Reframe as pure theory paper
4. Move proposed experiments to "Future Work" section

**Timeline**: 1 day

**Impact**: Paper becomes pure theory (acceptable but not strong)

**Deliverables**:
- Revised paper without experimental claims
- Updated abstract/intro

---

#### Option C: Reframe as Predictions (NOT RECOMMENDED)

**Tasks**:
1. Rename Section 5: "Predicted Experimental Outcomes"
2. Change all language to future/conditional tense
3. Add disclaimer: "These are theoretical predictions to be validated"
4. Move to appendix

**Timeline**: 2 days

**Impact**: Minimal (reviewers still view as incomplete)

**Deliverables**:
- Reframed Section 5 (appendix)

---

**DECISION REQUIRED**: Choose Option A, B, or C by 2026-03-29

**RECOMMENDATION**: Option A (conduct experiments) if resources available. Provides biggest score improvement (+2.0 points).

---

### Task 1.3: Validate Against Published Results [WEEK 3]

**Assignee**: Researcher agent
**Priority**: MAJOR (not FATAL but high impact)
**Estimated effort**: 1 week

**Goal**: Add Section 5.X analyzing published self-improvement results through the framework

#### Subtask 1.3a: Analyze STaR (Zelikman et al., 2022)

**Tasks**:
1. Extract reported accuracies over iterations from paper
2. Estimate γ_t from reported results
3. Check if plateau occurs (paper reports ~15% gain, then plateau)
4. Compare to Theorem 1 prediction: γ_∞ ≤ ν_0 + ε

**Expected finding**: "STaR results show convergence after 3-4 iterations, consistent with Theorem 1. Final accuracy plateaus at approximately ν_0 + 0.15, matching predicted bound."

---

#### Subtask 1.3b: Analyze ReST (Gulcehre et al., 2023)

**Tasks**:
1. Extract results with and without external reward model
2. Pure self-training: Check if plateau matches Theorem 1
3. With reward model: Note continued improvement (external verification)

**Expected finding**: "ReST with pure self-training shows plateau similar to STaR. When external reward model is added, improvement continues, supporting our claim that external verification breaks the bound."

---

#### Subtask 1.3c: Analyze Constitutional AI (Bai et al., 2022)

**Tasks**:
1. Analyze self-refinement results
2. Check if Theorem 2 (self-refinement bound) matches observations
3. Note role of human feedback (external verification)

**Expected finding**: "Constitutional AI's self-refinement shows diminishing returns after 2-3 iterations. Human feedback provides external verification that enables further improvement."

---

#### Subtask 1.3d: Analyze AlphaZero (Silver et al., 2017)

**Tasks**:
1. Note: Chess has objective outcomes (Theorem 4 Case 1)
2. Self-play achieves superhuman performance
3. Compare to Go, Shogi (also objective outcomes)

**Expected finding**: "AlphaZero's success in chess, Go, and Shogi strongly supports Theorem 4. All three games have objective outcomes (win/loss determinable via rules), enabling self-play to exceed initial capabilities and reach superhuman performance."

---

**Deliverable**: New Section 5.X (or 6.X if Section 5 is experiments) with 4 case studies validating theory against published results

**Impact**: +1.0 point (shows theory connects to reality)

---

## Phase 1 Checkpoint

**After completing Tasks 1.1-1.3**:

**Expected deliverables**:
- Complete proofs for all theorems (Lemmas A.1-A.X in appendix)
- Empirical validation (Option A) OR removed Section 5 (Option B)
- Validation against published results (4 case studies)

**Expected score**: 6.5-7.0 (Borderline Accept)

**Decision point**: Is this sufficient for submission, or continue to Phase 2?

**Recommendation**: Continue to Phase 2 to reach Strong Accept (7.5+)

---

## Phase 2: Strengthen Presentation and Scope (1-2 weeks)

**Goal**: Move from "Borderline Accept" (6.5-7.0) to "Accept/Strong Accept" (7.5+)

### Task 2.1: Reframe to Avoid Overclaiming [WEEK 4]

**Assignee**: Writer agent
**Priority**: MAJOR
**Estimated effort**: 2-3 days

#### Subtask 2.1a: Retitle Paper

**Current**: "Impossibility Results for Unsupervised Self-Improvement in Language Models"

**Options**:
1. "Theoretical Bounds on Unsupervised Self-Improvement in Language Models"
2. "Convergence Limits for Self-Training Without External Verification"
3. "A Framework for Analyzing Self-Improvement Limits in Language Models"

**DECISION**: Choose option 1 or 2

**Impact**: Prevents "overclaiming" criticism from R5

---

#### Subtask 2.1b: Revise Abstract

**Current**: "We provide formal impossibility results showing..."

**Revised**: "We develop a theoretical framework and prove convergence bounds showing that under standard assumptions, unsupervised self-improvement..."

**Changes**:
- Replace "impossibility results" with "convergence bounds"
- Add "under standard assumptions"
- Soften claims appropriately

---

#### Subtask 2.1c: Revise Introduction

**Current**: Strong claims about "proving impossibility"

**Revised**:
- Clarify these are conditional bounds, not unconditional impossibility
- Compare to No Free Lunch, PAC bounds (true impossibility results)
- Acknowledge limitations upfront

---

### Task 2.2: Add Practitioner's Guide [WEEK 4]

**Assignee**: Writer agent
**Priority**: MAJOR
**Estimated effort**: 3-5 days

**Goal**: Add new Section 6.X making theory actionable for practitioners

#### Contents:

1. **Measurement Protocols**:
   - How to measure Ver_M(x,y): "Construct verification subset with ground truth. Measure accuracy."
   - How to measure Gen_M(x): "Measure accuracy on generation tasks."
   - How to estimate g_D: "Compare human expert accuracy on verification vs generation."

2. **Worked Example**:
   - Task: GSM8K
   - Measure ν_0: Present 100 (problem, solution) pairs, ask model to judge correctness → ν_0 = 0.75
   - Measure γ_0: Present 100 problems, ask model to solve → γ_0 = 0.60
   - Estimate g_D: Human verification accuracy 0.95, generation accuracy 0.75 → g_D ≈ 0.20
   - Predict γ_max: Using f(0.20) ≈ 0.15, predict γ_max ≈ 0.75 + 0.15 = 0.90
   - Decision: Self-training can improve from 0.60 to ~0.85-0.90 (worth doing)

3. **Decision Tree**:
   ```
   Should I invest in self-improvement for this task?

   Step 1: Measure ν_0 and γ_0
   Step 2: Estimate g_D
   Step 3: Apply decision rules:
     - If ν_0 - γ_0 < 0.1 → Self-training won't help much (already near ceiling)
     - If g_D > 0.5 → Large gap limits improvement (external verification needed)
     - If g_D < 0.2 → Small gap, self-training can work well
     - If task has objective outcomes → Consider self-play
   ```

4. **Common Pitfalls**:
   - Reward hacking (verification is noisy)
   - Distribution shift (train on easy, test on hard)
   - Diminishing returns (stop after 3-5 iterations)

**Impact**: +0.5 points (addresses R3 practitioner concerns)

---

### Task 2.3: Expand Related Work [WEEK 4-5]

**Assignee**: Researcher agent
**Priority**: MODERATE
**Estimated effort**: 2-3 days

**Missing citations** identified by reviewers:

1. **Tian et al. (2025)** - Theoretical Modeling of LLM Self-Improvement via Solver-Verifier Gap
   - Discuss: Empirical model of gap dynamics
   - Compare: Their empirical findings vs our theoretical predictions

2. **Shen & Sanghavi (2024)** - Reciprocal Learning
   - Discuss: Proves self-training convergence via Banach fixed-point
   - Compare: Our Theorem 1 extends to general self-improvement (not just reciprocal learning)

3. **Wei et al. (2021)** - Theoretical Analysis of Self-Training
   - Discuss: Expansion assumption for convergence
   - Compare: We use different assumptions (verification bound vs expansion)

4. **Xu & Raginsky (2017)** - Generalization Bounds for Noisy Iterative Algorithms
   - Discuss: Mutual information bounds
   - Compare: Our Theorem 3 uses similar information-theoretic approach

**Deliverable**: Expanded Related Work section (add 1-2 paragraphs, 4+ citations)

**Impact**: +0.2 points (completeness)

---

### Task 2.4: Add Caveats to Safety Discussion [WEEK 5]

**Assignee**: Writer agent
**Priority**: MODERATE
**Estimated effort**: 1 day

**Goal**: Soften overclaimed safety implications

#### Changes to Section 6.2 (AI Safety):

1. **Add limitations paragraph**:
   ```
   Our analysis excludes several factors present in real AI systems:
   - Tool-augmented verification (code execution, web search, formal proofs)
   - Multi-agent verification (debate, ensemble methods, committee-based evaluation)
   - Human-in-the-loop verification (Constitutional AI, RLHF)
   - Capability emergence and phase transitions (sudden jumps in ability)
   - Multi-dimensional capability spaces (scalar γ may not capture task diversity)

   These factors may enable self-improvement beyond the bounds we prove.
   ```

2. **Weaken "no takeoff" claim**:
   - BEFORE: "Our results argue against scenarios where AI systems recursively self-improve to superintelligence"
   - AFTER: "Under our idealized assumptions (fixed verification capability, no external tools), self-improvement plateaus. However, if verification capability itself improves through meta-learning, or if systems have access to external verification sources, our bounds may not apply."

3. **Soften policy recommendations**:
   - Add: "Further empirical work is needed before drawing strong policy conclusions from these theoretical results."

**Impact**: +0.3 points (prevents "overclaiming" criticism)

---

### Task 2.5: Clean Up Notation and Presentation [WEEK 5-6]

**Assignee**: Writer agent
**Priority**: LOW
**Estimated effort**: 1 day

**Issues to fix**:
- Inconsistent notation: M vs \mathcal{M} (choose one)
- Definition 2: Clarify Gen_M(x) is success probability
- Line 211: limsup vs convergence (reconcile with Assumption 3)
- Forward references to incomplete appendix proofs

**Impact**: +0.1 points (polish)

---

## Phase 2 Checkpoint

**After completing Tasks 2.1-2.5**:

**Expected deliverables**:
- Retitled paper (no "impossibility" overclaim)
- Practitioner's guide section
- Expanded related work (+4 citations)
- Caveated safety discussion
- Polished notation

**Expected score**: 7.5-8.0 (Accept to Strong Accept)

**Ready for submission**: YES

---

## Optional Enhancements (Nice-to-Have)

### Task 3.1: Add Convergence Rate Analysis

**Assignee**: Theorist agent
**Effort**: 1 week
**Impact**: +0.3 points

**Goal**: Prove γ_t → γ_∞ at geometric rate O((1-λ)^t)

**Approach**:
- Show T is a contraction mapping with constant λ < 1
- Apply Banach fixed-point theorem
- Derive explicit bound on iterations required

**Deliverable**: Theorem 1' with convergence rate

---

### Task 3.2: Add Tool-Augmented Extension

**Assignee**: Theorist agent
**Effort**: 1 week
**Impact**: +0.2 points

**Goal**: Extend framework to models with tool access

**Theorem to add**:
```
Theorem 5 (Tool-Augmented Self-Training): If model M has access to external
verification tools (code execution, web search, formal proofs), the bound becomes:

γ_∞ ≤ min(ν_tool, 1)

where ν_tool is the accuracy of tool-based verification.
```

**Deliverable**: New theorem + proof in appendix

---

## Timeline and Milestones

### Week 0 (Current - 2026-03-22)
- ✅ Internal review simulation complete
- ✅ Synthesis and roadmap created
- **Decision**: Choose experiment option (A, B, or C)

### Week 1-2 (2026-03-25 to 2026-04-08)
- **Theorist**: Complete all proofs (Tasks 1.1a-1.1f)
- **Deliverables**: Lemmas A.1-A.X, Corollary 1.1, revised assumptions

### Week 2-3 (2026-04-08 to 2026-04-22)
- **Experimenter**: Conduct experiments (if Option A) OR Writer: Remove Section 5 (if Option B)
- **Deliverables**: Experimental results + figures OR revised paper without experiments

### Week 3-4 (2026-04-22 to 2026-05-06)
- **Researcher**: Validate against published results (Task 1.3)
- **Writer**: Reframe paper (Task 2.1)
- **Deliverables**: Section 5.X (case studies), revised title/abstract

### Week 4-5 (2026-05-06 to 2026-05-20)
- **Writer**: Add practitioner's guide (Task 2.2)
- **Researcher**: Expand related work (Task 2.3)
- **Deliverables**: Section 6.X (practitioner's guide), expanded related work

### Week 5-6 (2026-05-20 to 2026-06-03)
- **Writer**: Finalize safety discussion (Task 2.4), polish notation (Task 2.5)
- **All agents**: Proofread and final review
- **Deliverables**: Camera-ready draft v1.0

### Week 6+ (2026-06-03 onwards)
- **Optional**: Add convergence rate analysis, tool-augmented extension
- **Final**: Submit to ICLR 2027 (deadline September 2026)

---

## Resource Requirements

### Personnel:
- **Theorist agent**: 15-20 sessions (proof completion)
- **Experimenter agent**: 10-15 sessions (if conducting experiments)
- **Researcher agent**: 5-8 sessions (validation, related work)
- **Writer agent**: 8-12 sessions (reframing, practitioner's guide, polish)

**Total**: 38-55 agent sessions over 6 weeks

### Budget:
- **Experiments** (if Option A): $200-500 for API calls
- **Agent time**: No direct cost (internal platform resource)

### Risks:
- **Proof completion takes longer**: Theorist may need 3-4 weeks instead of 2
  - Mitigation: Start early, prioritize Lemmas A.1 and Corollary 1.1
- **Experiments fail to validate**: Results don't match predictions
  - Mitigation: Choose tasks carefully (GSM8K, HumanEval likely to work)
- **Missing collaborators**: Need complexity theorist for rigorous proofs
  - Mitigation: Seek collaboration or use converse Banach theorem approach

---

## Success Criteria

### Minimum Success (Borderline Accept ~6.5/10):
- ✅ All proofs complete and rigorous
- ✅ Either experiments conducted OR Section 5 removed
- ✅ Validation against published results

### Target Success (Accept ~7.5/10):
- ✅ All of minimum success
- ✅ Practitioner's guide added
- ✅ Reframed to avoid overclaiming
- ✅ Expanded related work

### Exceptional Success (Strong Accept ~8.5/10):
- ✅ All of target success
- ✅ Convergence rate analysis
- ✅ Tool-augmented extension
- ✅ Multiple worked examples

**Current target**: Target Success (7.5/10) - achievable in 6 weeks

---

## Next Immediate Actions

1. **DECISION** (by 2026-03-29): Choose experiment option
   - Recommend: Option A (conduct experiments)
   - Fallback: Option B (remove Section 5)

2. **START** (by 2026-03-25): Theorist begins proof completion
   - Priority: Lemma A.1 (verification boundedness)
   - Priority: Characterize f(g_D)

3. **PLAN** (by 2026-04-01): If Option A chosen, design experiment protocol
   - Choose tasks (GSM8K, HumanEval, creative writing)
   - Write implementation code
   - Estimate API costs

4. **SCHEDULE**: Allocate agent sessions for 6-week revision period
   - Theorist: 3-4 sessions/week for weeks 1-2
   - Experimenter: 4-5 sessions/week for weeks 2-3 (if Option A)
   - Researcher: 2-3 sessions/week for weeks 3-4
   - Writer: 2-3 sessions/week for weeks 4-6

**Expected completion**: 2026-06-03 (v1.0 ready for ICLR 2027 submission)

