# Review Synthesis and Revision Priorities
**Date**: 2026-03-22
**Paper**: Impossibility Results for Unsupervised Self-Improvement in Language Models
**Draft version**: v0.1

## Executive Summary

**Overall Assessment**: The paper addresses an important problem with an elegant framework, but has critical execution flaws that prevent acceptance at ICLR 2027 in its current form.

**Predicted scores**:
- Review 1 (Theory Purist): 5.0/10 - Borderline
- Review 2 (Empiricist): 4.3/10 - Reject
- Review 3 (Practitioner): 6.2/10 - Borderline
- Review 4 (Complexity Theorist): 6.5/10 - Accept
- Review 5 (Skeptical Senior): 4.3/10 - Reject

**Average predicted score**: **5.26/10**

**Target score**: 7.5+/10

**Gap to close**: +2.24 points (requires addressing all FATAL issues and most major weaknesses)

---

## Critical (FATAL) Issues - Must Fix for Any Chance of Acceptance

### Issue 1: Hypothetical Experiments Presented as Results [PRIORITY 1 - FATAL]

**Severity**: FATAL - All reviewers flagged this
**Mentioned by**: All 5 reviewers (unanimous)
**Impact on score**: -2.0 to -3.0 points

**Problem**:
Section 5 (Experiments) presents detailed results (specific accuracy numbers, statistical tests, p-values, correlation coefficients) for experiments that were never conducted. This is scientific misconduct if not clearly marked as hypothetical.

**Evidence from reviews**:
- R1: "FATAL: Missing complete proofs, experiments are hypothetical"
- R2: "FATAL - Fabricated experimental results... This is scientific misconduct"
- R3: "Missing experiments undermine trust"
- R5: "Empirical section is scientific misconduct"

**Three options** (choose one before submission):

**Option A: Conduct Actual Experiments** (RECOMMENDED if resources available)
- Timeline: 2-4 weeks
- Cost: ~$200-500 for API calls
- Requirements:
  - Implement self-training on 2-3 tasks (GSM8K, HumanEval, creative writing)
  - Measure γ_t and ν_t over 10 iterations
  - Generate actual figures showing convergence
  - Run statistical tests
  - Validate Theorem 1 predictions empirically
- Impact: Moves paper from 5.3 → 7.5+ (biggest single improvement possible)

**Option B: Remove Section 5 Entirely**
- Timeline: 1 day
- Impact: Submit as pure theory paper
- Requires: Reframing abstract/intro to not promise empirical validation
- Outcome: Score remains ~5.5-6.0 (incomplete proofs remain the bottleneck)

**Option C: Reframe as Predictions**
- Timeline: 2 days
- Changes needed:
  - Rename "Section 5: Empirical Validation" → "Section 5: Predicted Experimental Outcomes"
  - Change all past tense ("Figure 1 shows") → future/conditional ("We predict Figure 1 will show")
  - Add clear markers: "These are theoretical predictions to be validated in future work"
  - Move to appendix as "Proposed Experiments"
- Impact: Minimal (reviewers still view as incomplete)

**DECISION REQUIRED**: Choose option A, B, or C before submission.

**Recommendation**: Option A if possible (conduct minimal experiments on 1-2 tasks), otherwise Option B.

---

### Issue 2: Incomplete and Circular Proofs [PRIORITY 2 - FATAL]

**Severity**: FATAL for theory venue
**Mentioned by**: R1, R4, R5
**Impact on score**: -1.5 to -2.0 points

**Problem**:
Main theorems (Theorems 1-4) have proof sketches with gaps and circular reasoning. Appendix proofs are also incomplete.

**Specific gaps identified**:

#### Gap 2a: Verification Boundedness (Theorem 1)
**Issue**: Proof assumes ν_max ≤ ν_0 + Δ for bounded Δ but doesn't prove Δ is bounded.
**Why circular**: If verification can improve unboundedly through self-training, the whole theorem fails.
**Fix required**:
- Add Lemma: "Verification on self-generated data is bounded by verification on true distribution"
- Prove: ν(D_self) ≤ ν(D_true) + δ where δ is bounded
- Argue: Self-generated data is biased toward model's generation capability, limiting verification improvement

**Action**: Add new Lemma A.1 with complete proof in appendix

#### Gap 2b: Uncharacterized Function f(g_D) (Theorem 3)
**Issue**: f(g_D) asserted to be monotonically decreasing but not characterized or proved.
**Why problematic**: Without explicit f, theorem makes no testable predictions.
**Fix required**:
- Propose explicit form: f(g_D) = C/(1 + αg_D) for constants C, α
- Prove monotonicity (trivial for this form)
- Justify via mutual information bound: I(Verification; Quality) ≤ C/(1 + αg_D)
- Provide empirical estimates of C, α from literature if possible

**Action**: Derive explicit f or prove specific properties (e.g., f(g) = O(1/g))

#### Gap 2c: Objective Outcome Property (Definition 5, Theorem 4)
**Issue**: "Objective outcome" defined through examples, not formal properties.
**Why problematic**: Unclear when the definition applies—is debate "objective"? Multi-turn evaluation?
**Fix required**:
- Formal definition: "Game G has objective outcomes if ∃ computable W: Transcripts → {-1,0,1} such that W can be evaluated in poly-time independent of player capability"
- Prove: If W is objective, then self-play provides external verification signal
- Formalize Gen*(G) as optimal strategy value under perfect play

**Action**: Replace example-based definition with formal one

#### Gap 2d: Assumption 2 Justification
**Issue**: Assumes training on quality-q data yields capability ≤ q + ε without proof.
**Why problematic**: This assumption essentially IS the conclusion (data quality bounds capability).
**Fix options**:
1. Prove under PAC framework with distributional assumptions
2. Cite prior work proving similar bounds (e.g., Xu & Raginsky 2017)
3. Weaken to "under regularity conditions..." and discuss when it fails

**Action**: Choose option 2 or 3 (option 1 requires significant new theory work)

#### Gap 2e: Assumption 3 (Convergence Existence)
**Issue**: Assumes fixed point exists without proof.
**Why problematic**: Many iterative processes don't converge (oscillation, chaos, divergence).
**Fix required**:
- Prove convergence under standard conditions (T is contraction or monotone operator)
- Or weaken theorems to: "If T converges, then the limit satisfies..."
- Cite Banach fixed-point theorem or Tarski fixed-point theorem as applicable

**Action**: Prove convergence OR weaken theorem statements

**Overall Fix for Issue 2**:
- Add 3-5 new lemmas with complete proofs
- Derive explicit f(g_D) or prove f(g) = O(1/g)
- Formalize all definitions rigorously
- Justify or weaken Assumptions 2-3

**Timeline**: 2-4 weeks for a theorist
**Impact**: Moves score from 5.3 → 6.5-7.0

---

### Issue 3: Uncharacterized Slack Terms (ε in Theorems 1-2) [PRIORITY 3 - MAJOR]

**Severity**: Major - Makes results potentially vacuous
**Mentioned by**: R4, R5
**Impact on score**: -1.0 to -1.5 points

**Problem**:
Theorems state γ_∞ ≤ ν_0 + ε but never characterize ε. If ε is large (e.g., ε = 0.5), the bound is too loose to be meaningful.

**Reviewer quotes**:
- R5: "If ε is unbounded, the result is vacuous. If ε is large, the bound is too loose to be useful."
- R4: "Missing: Characterization of ε in bounds... Can ε be large enough to make the bound vacuous?"

**Fix required**:
1. **Theoretical bound**: Prove ε ≤ δ_FP + ε_train + Δ where:
   - δ_FP = false positive rate (function of verification capability)
   - ε_train = training slack (function of optimization quality)
   - Δ = verification improvement bound (proved in fix for Issue 2a)

2. **Empirical estimates**: Provide rough estimates:
   - "For modern LLMs with high-quality training, we expect ε ≈ 0.1-0.2"
   - "For small models or noisy verification, ε may approach 0.5"

3. **Add corollary**: "Under Lipschitz-continuous training dynamics, ε ≤ L · δ_FP where L is the Lipschitz constant"

**Action**: Add Corollary 1.1 characterizing ε with proof

**Timeline**: 3-5 days
**Impact**: Prevents "vacuous bound" criticism

---

## Major Issues - Significantly Hurt Score

### Issue 4: Misleading "Impossibility Result" Framing [PRIORITY 4]

**Severity**: Major - Overclaiming
**Mentioned by**: R5, implied by R1
**Impact on score**: -0.5 to -1.0 points

**Problem**:
Title and abstract claim "impossibility results" but actual results are conditional bounds with uncharacterized slack terms. True impossibility results (No Free Lunch, PAC lower bounds) are unconditional.

**Reviewer quote**:
- R5: "This is not an impossibility result—it's a conditional bound with unknown constants."

**Fix required**:
1. **Retitle**: Change to one of:
   - "Theoretical Bounds on Unsupervised Self-Improvement in Language Models"
   - "Convergence Limits for Self-Training Without External Verification"
   - "A Framework for Self-Improvement Limits in Language Models"

2. **Reframe abstract**: Replace "we prove impossibility results" with "we derive theoretical bounds showing that..."

3. **Add comparison**: Discuss relationship to true impossibility results (No Free Lunch, PAC lower bounds) and clarify differences

**Action**: Revise title, abstract, and introduction framing

**Timeline**: 1-2 days
**Impact**: Prevents "overclaiming" criticism, sets appropriate expectations

---

### Issue 5: No Validation Against Published Results [PRIORITY 5]

**Severity**: Major for ICLR (empirical venue)
**Mentioned by**: R2, R3, R5
**Impact on score**: -1.0 point

**Problem**:
Paper cites STaR, ReST, Constitutional AI, AlphaZero but never checks if published results match theoretical predictions.

**Reviewer quotes**:
- R2: "Never validates whether the theoretical framework actually explains their observed behavior"
- R3: "Our internal experiments with self-training show plateaus after 3-5 iterations, consistent with Theorem 1"
- R5: "Never analyzes whether published results match theoretical predictions"

**Fix required**:
Add new subsection: "5.X Analysis of Published Self-Improvement Results"

Analyze 3-4 published papers:

1. **STaR (Zelikman et al., 2022)**:
   - Extract γ_t from reported accuracies across iterations
   - Check if plateau occurs (reported: ~15% gain over 3-4 iterations, then plateau)
   - Compare to predicted ν_0 + ε bound
   - Verdict: "Consistent with Theorem 1 prediction of convergence"

2. **ReST (Gulcehre et al., 2023)**:
   - Note: Uses external reward model (not pure self-training)
   - Shows continued improvement beyond STaR
   - Compare to prediction: "External verification breaks the bound"
   - Verdict: "Supports our framework—external verification enables improvement"

3. **Constitutional AI (Bai et al., 2022)**:
   - Extract self-refinement accuracy improvements
   - Check if plateau matches Theorem 2
   - Note: Uses human feedback (external verification)
   - Verdict: "Mixed—self-refinement plateaus, human feedback improves further"

4. **AlphaZero (Silver et al., 2017)**:
   - Chess has objective outcomes → matches Theorem 4 Case 1
   - Self-play achieves superhuman performance
   - Verdict: "Strongly supports Theorem 4—objective outcomes enable unbounded improvement"

**Action**: Add analysis subsection with 3-4 case studies

**Timeline**: 1 week (requires reading papers, extracting data, making comparisons)
**Impact**: Moves score from 5.3 → 6.0 (shows theory connects to reality)

---

### Issue 6: Poor Operationalization for Practitioners [PRIORITY 6]

**Severity**: Moderate - Limits practical impact
**Mentioned by**: R3 (Practitioner)
**Impact on score**: -0.5 points

**Problem**:
Framework uses abstract quantities (Gen(x), Ver(x), γ, ν, g_D) but never explains how to measure them in practice.

**Reviewer quote**:
- R3: "How do I measure Ver_M(x,y) for open-ended reasoning, creative tasks, multi-step code?"

**Fix required**:
Add new section: "6.X Practitioner's Guide to Applying the Framework"

Include:
1. **Measurement protocols**:
   - Ver_M: "Accuracy on verification subset with known ground truth"
   - Gen_M: "Accuracy on generation tasks"
   - g_D: "Difference in human expert accuracy between verification and generation"

2. **Worked example**:
   - Task: GSM8K (math word problems)
   - Ver_M: Measure model accuracy on verifying correctness of solutions (given problem + proposed solution, judge if correct)
   - Gen_M: Measure model accuracy on generating solutions
   - Estimate g_D: g_D ≈ 0.2 (verification 20% easier than generation)
   - Predict γ_max: If ν_0 = 0.75, predict γ_max ≈ 0.85-0.90

3. **Decision tree**: "Should I invest in self-improvement for this task?"
   - Measure ν_0 and current γ_0
   - Estimate g_D
   - If ν_0 - γ_0 < 0.1 → self-training won't help much
   - If g_D > 0.5 → self-training limited by large gap
   - Recommendation: Use external verification or tools

**Action**: Add practitioner's guide section

**Timeline**: 3-5 days
**Impact**: Increases practical value, addresses R3 concerns

---

### Issue 7: Overclaimed Safety Implications [PRIORITY 7]

**Severity**: Moderate - Credibility issue
**Mentioned by**: R2, R3, R5
**Impact on score**: -0.5 points

**Problem**:
Discussion Section 6.2 claims "no self-improvement takeoff" and "alignment implications" but results don't support strong claims.

**Reviewer quotes**:
- R2: "Overstated implications for AI safety... assumes verification is fixed, ignores tool use and human feedback"
- R5: "This gives false confidence to policymakers... actual message should be: 'Under idealized assumptions...'"

**Fix required**:
Revise Section 6.2 to add caveats:

1. **Weaken "no takeoff" claim**:
   - BEFORE: "Our results argue against scenarios where AI systems recursively self-improve to superintelligence"
   - AFTER: "Under our idealized assumptions (fixed verification capability, no external tools, no multi-agent collaboration), self-improvement plateaus. However, these assumptions may not hold in practice, and verification capability itself could improve through meta-learning"

2. **Add limitations paragraph**:
   "Our analysis excludes several factors present in real systems:
   - Tool-augmented verification (code execution, web search, formal proofs)
   - Multi-agent verification (debate, ensemble methods)
   - Human-in-the-loop verification (Constitutional AI, RLHF)
   - Capability emergence (sudden jumps in ability)
   - Multi-dimensional capabilities (scalar γ may not capture complexity)"

3. **Soften policy recommendations**:
   - BEFORE: "AI safety efforts should focus on preventing systems from developing strong verification capabilities"
   - AFTER: "One implication is that verification capability may be a bottleneck for self-improvement. However, further empirical work is needed before drawing strong policy conclusions"

**Action**: Add caveats to Section 6.2

**Timeline**: 1 day
**Impact**: Prevents "overclaiming" criticism on safety

---

## Moderate Issues - Improve Paper Quality

### Issue 8: Missing Convergence Rate Analysis [PRIORITY 8]

**Mentioned by**: R4
**Impact**: +0.3 points if added

**Fix**: Add analysis of convergence rate (geometric vs linear vs sublinear)
- Prove: γ_t → γ_∞ at rate O((1-λ)^t) for contraction constant λ
- Or: Bound number of iterations required to reach ε-close to γ_∞

**Action**: Add Theorem 1' with convergence rate
**Timeline**: 1 week (requires theory work)

---

### Issue 9: Missing Related Work Citations [PRIORITY 9]

**Mentioned by**: R4, R5
**Impact**: +0.2 points if fixed

**Missing papers to cite and discuss**:
1. Tian et al. (2025) - Theoretical Modeling of LLM Self-Improvement via Solver-Verifier Gap [highly relevant]
2. Shen & Sanghavi (2024) - Reciprocal Learning (proves self-training convergence via Banach)
3. Wei et al. (2021) - Theoretical Analysis of Self-Training
4. Xu & Raginsky (2017) - Generalization Bounds for Noisy Iterative Algorithms

**Action**: Add citations and discussion in Related Work
**Timeline**: 2-3 days

---

### Issue 10: Notation and Presentation Issues [PRIORITY 10]

**Mentioned by**: R1, R4
**Impact**: +0.1 points if fixed

**Issues**:
- Inconsistent notation: M vs \mathcal{M}
- Definition 2: Gen_M(x) → [0,1] but used as probability (clarify)
- Line 211: limsup suggests non-convergence (conflicts with Assumption 3)

**Action**: Clean up notation, clarify definitions
**Timeline**: 1 day

---

## Prioritized Revision Plan

### Phase 1: Address FATAL Issues (Required for Acceptance)

**Duration**: 4-6 weeks
**Impact**: Score 5.3 → 6.5-7.0

1. **Week 1-2: Fix Proofs** [Issue 2]
   - Add Lemma A.1: Verification boundedness
   - Derive explicit f(g_D) or prove f(g) = O(1/g)
   - Formalize Definition 5 (objective outcomes)
   - Add convergence proof or weaken theorem statements
   - Characterize ε (Corollary 1.1)

2. **Week 2-3: Empirical Validation** [Issue 1]
   - Option A: Conduct experiments (recommended)
     - Implement self-training on GSM8K, HumanEval
     - Measure γ_t, ν_t over 10 iterations
     - Generate figures, run statistics
   - Option B: Remove Section 5 (fallback)

3. **Week 3-4: Validate Against Published Results** [Issue 5]
   - Analyze STaR, ReST, AlphaZero results
   - Add Section 5.X with case studies
   - Show theory matches published observations

**Deliverable after Phase 1**: Paper with complete proofs, empirical validation, and case studies

**Expected score after Phase 1**: 6.5-7.0 (borderline accept)

---

### Phase 2: Improve Presentation and Scope (Move to Strong Accept)

**Duration**: 1-2 weeks
**Impact**: Score 6.5-7.0 → 7.5+

4. **Week 5: Reframe and Add Practitioner's Guide** [Issues 4, 6]
   - Retitle paper (remove "impossibility")
   - Add Section 6.X: Practitioner's Guide
   - Add measurement protocols and worked examples

5. **Week 5-6: Strengthen Related Work and Discussion** [Issues 7, 9]
   - Add missing citations (Tian et al., Shen & Sanghavi, etc.)
   - Add caveats to safety implications
   - Discuss limitations honestly

6. **Week 6: Polish** [Issues 8, 10]
   - Fix notation inconsistencies
   - Add convergence rate analysis (if time permits)
   - Proofread thoroughly

**Deliverable after Phase 2**: Polished paper ready for submission

**Expected score after Phase 2**: 7.5-8.0 (accept to strong accept)

---

## Decision Points

### Decision 1: Experiments or Pure Theory?

**Option A: Conduct Experiments** (RECOMMENDED)
- Pro: Biggest score improvement (+2.0 points)
- Pro: Addresses all 5 reviewers' concerns
- Con: Requires 2-4 weeks and $200-500
- Result: Strong paper with both theory and validation

**Option B: Pure Theory (Remove Section 5)**
- Pro: Faster (1 day)
- Pro: Focuses on theory strengths
- Con: Score remains ~6.0 (borderline)
- Con: 3/5 reviewers still concerned about proofs
- Result: Acceptable theory paper but not strong

**RECOMMENDATION**: Option A if resources available, otherwise delay submission to conduct experiments.

---

### Decision 2: Submission Timeline

**Option A: Submit to ICLR 2027**
- Deadline: September 2026
- Time available: 6 months
- Sufficient time for Phase 1 + Phase 2 revisions
- **RECOMMENDED**

**Option B: Submit to NeurIPS 2026**
- Deadline: May 2026
- Time available: 2 months
- Only sufficient for Phase 1 (partial fixes)
- Risk: Borderline acceptance at best

**RECOMMENDATION**: Target ICLR 2027 with full revisions rather than rushing to NeurIPS 2026.

---

### Decision 3: Collaborators Needed?

**Current gaps in expertise**:
1. **Theory**: Need rigorous proofs → Consider co-authoring with complexity theorist
2. **Experiments**: Need empirical validation → Consider co-authoring with ML empiricist
3. **Application**: Need practitioner insights → Consider feedback from Anthropic/OpenAI researchers

**Recommendation**: Seek collaboration for Phase 1 (proofs + experiments) to strengthen both theory and empirics.

---

## Summary of Required Revisions

### Must-Have (for any acceptance):
- ✅ Complete all proofs rigorously (add 3-5 lemmas)
- ✅ Conduct experiments OR remove Section 5
- ✅ Characterize ε and f(g_D)
- ✅ Validate against published results (STaR, ReST, AlphaZero)

### Should-Have (for strong acceptance):
- ✅ Add practitioner's guide with measurement protocols
- ✅ Reframe title/abstract (remove "impossibility" overclaim)
- ✅ Add caveats to safety implications
- ✅ Expand related work (cite Tian et al., Shen & Sanghavi, etc.)

### Nice-to-Have (for exceptional paper):
- ⭕ Add convergence rate analysis
- ⭕ Provide explicit formula for f(g_D)
- ⭕ Add tool-augmented extension

---

## Predicted Acceptance Scores After Revisions

### Current (v0.1 - no revisions):
- **Average**: 5.26/10
- **Verdict**: Reject

### After Phase 1 (proofs + experiments + validation):
- **Average**: 6.8/10
- **Verdict**: Borderline Accept

### After Phase 1 + Phase 2 (full revisions):
- **Average**: 7.6/10
- **Verdict**: Accept (meets 7.5+ target)

---

## Next Immediate Actions

1. **DECIDE**: Experiments (Option A) vs Pure Theory (Option B)
2. **PRIORITIZE**: If experiments → start implementation immediately
3. **THEORIST WORK**: Begin filling proof gaps (Issue 2)
4. **TIMELINE**: Aim for ICLR 2027 (6 months), not NeurIPS 2026 (2 months)

**Estimated total effort**: 6-8 weeks of focused work by writer + theorist + experimenter
**Estimated cost**: $200-500 (API calls for experiments)
**Expected outcome**: Strong Accept at ICLR 2027

