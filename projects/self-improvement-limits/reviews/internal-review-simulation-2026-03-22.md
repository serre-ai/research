# Internal Review Simulation: Self-Improvement Limits Paper
**Date**: 2026-03-22
**Paper**: Impossibility Results for Unsupervised Self-Improvement in Language Models
**Draft version**: v0.1
**Target venue**: ICLR 2027

This document contains 5 synthetic reviews from different reviewer personas to identify weaknesses and blind spots before submission.

---

## Review 1: Theory Purist (Prof. Alice Martinez - MIT, Learning Theory)

**Overall recommendation**: Borderline

| Criterion       | Score | Key Issue |
|----------------|-------|-----------|
| Novelty         | 7/10  | Interesting formalization but builds heavily on existing frameworks |
| Correctness     | 4/10  | **CRITICAL: Proofs are incomplete and contain gaps** |
| Significance    | 8/10  | Important question with practical implications |
| Clarity         | 6/10  | Framework clear but proof presentation lacks rigor |
| Completeness    | 3/10  | **FATAL: Missing complete proofs, experiments are hypothetical** |
| Reproducibility | 2/10  | **FATAL: No experiments actually conducted, no code** |

**Average**: 5.0/10

### Strengths

1. **Important problem**: The question of self-improvement limits is fundamental for both AI safety and capability forecasting. Formalizing this rigorously is valuable.

2. **Clean formalization**: The framework in Section 3 (capability spaces, self-improvement operators) provides a clear mathematical structure. Definitions 1-5 are well-stated.

3. **Unifying perspective**: Treating self-training, self-refinement, and self-play in a common framework is elegant and allows direct comparison.

### Weaknesses

1. **CRITICAL - Incomplete proofs**: All four main theorems (Theorems 1-4) provide only "proof sketches" with promises of "full details in appendix." The appendix proofs (Section A) are also incomplete:
   - Lemma 1 (Filtered Data Quality): Assumes \(\delta_{FP}\) is well-defined but never characterizes it. How does false positive rate relate to verification capability?
   - Lemma 2 (Training Capability Bound): States this "follows from Assumption 2" but Assumption 2 is itself an assertion, not a proved fact. This is circular.
   - Theorem 1 proof: The step from "\(\nu_t \leq \nu_{max}\)" to "\(\nu_{max} \leq \nu_0 + \Delta\)" is unjustified. Why can't verification capability improve unboundedly through self-training?
   - Theorem 3 proof: The function \(f(g_D)\) is stated to exist but never explicitly constructed. The "information-theoretic argument" in Lemma 4 is hand-waving without formal mutual information bounds.

2. **FATAL - No empirical validation**: Section 5 describes hypothetical experiments but explicitly states these are "to be conducted." The paper presents:
   - "Figure 1 shows..." but no Figure 1 exists in the PDF
   - Specific accuracy numbers (e.g., \(\gamma_\infty = 0.67\)) without any actual evaluation
   - Statistical claims (\(p < 0.01\)) for non-existent data

   This is unacceptable for an ICLR submission. A theory paper need not have experiments, but you cannot claim empirical validation without conducting experiments.

3. **Assumption 2 is too strong and unverified**: The paper assumes training on quality-\(q\) data yields capability \(\leq q + \epsilon\). This is plausible but:
   - No proof or citation that this holds for neural networks
   - The bound may be loose—what if emergent capabilities arise during training?
   - The assumption essentially assumes the conclusion (capability is bounded by data quality)

4. **Circular reasoning in Theorem 1**: The proof states "if verification capability is non-decreasing and bounded." But WHY is verification capability bounded? If verification can improve through exposure to harder problems, \(\nu_t\) might grow without bound. The theorem needs to PROVE boundedness, not assume it.

5. **GV-gap function \(f\) is uncharacterized**: Theorem 3 claims \(f(g_D)\) is monotonically decreasing with specific limits, but:
   - No explicit form given (exponential? Power law? Rational?)
   - No proof of monotonicity
   - Information-theoretic argument (Lemma 4) is too vague—what is \(h\)? How is mutual information computed?

   Without characterizing \(f\), the theorem makes no testable predictions.

6. **Self-play separation result is informal**: Theorem 4's "objective outcome property" (Definition 5) is defined through examples rather than formal properties:
   - What does "efficiently computable independent of player capabilities" mean precisely?
   - The proof for Case 1 claims outcomes "provide verification oracle" but doesn't formalize this
   - \(\text{Gen}^*(G)\) is undefined—optimal with respect to what objective?

### Questions for Authors

1. **Proof completeness**: Can you provide complete, rigorous proofs for all theorems? Specifically:
   - Prove \(\nu_{max} \leq \nu_0 + \Delta\) for bounded \(\Delta\) in Theorem 1
   - Derive explicit form of \(f(g_D)\) and prove monotonicity in Theorem 3
   - Formalize "objective outcome" and prove the separation in Theorem 4

2. **Verification improvement**: Under what conditions can verification capability improve during self-training? If it cannot improve, why not? If it can, how do you bound the improvement?

3. **Experimental validation**: Will experiments be conducted before submission? If this is a pure theory paper, remove Section 5 entirely rather than presenting hypothetical results.

4. **Assumption justification**: Can you prove or provide strong evidence for Assumption 2? Cite prior work or provide a proof under specific conditions (e.g., PAC learning with bounded sample complexity).

### Suggestions for Improvement

1. **Either provide complete proofs OR remove incompletely proved theorems**: If proofs cannot be completed rigorously, state results as conjectures and provide empirical evidence. Do not claim "we prove" without complete proofs.

2. **Remove or clearly mark Section 5 as hypothetical**: If experiments haven't been run, either:
   - Conduct them before submission
   - Present as "proposed experiments" in future work
   - Remove the section entirely

   Do NOT present hypothetical data as actual results.

3. **Characterize \(f(g_D)\) explicitly**: Derive an explicit form (even with unknown constants) or prove specific properties (e.g., \(f(g) = O(1/g)\) or \(f(g) = \exp(-\alpha g)\)).

4. **Add a "Limitations of Current Results" section**: Be honest about what is proved vs conjectured vs empirically validated.

5. **Consider restructuring as**: "Framework and Conjectures" (proven framework + conjectured bounds) + "Partial Results" (what IS rigorously proved) + "Future Work" (complete proofs + experiments).

### Minor Issues

- Line 218: "The key insight is..." should provide formal statement before intuition
- Definition 2 (Model Capability): \(\Gen_M(x) \to [0,1]\) but then used as probability—clarify this is success probability
- Notation inconsistency: \(\mathcal{M}\) for model vs \(M\) subscript
- Several forward references to appendix sections that contain incomplete proofs

### Recommendation Justification

This paper addresses an important question with a promising framework, but the execution is severely incomplete. The proofs have gaps, the experiments are hypothetical, and key results (Theorem 3's function \(f\)) are uncharacterized.

**This cannot be accepted in current form.** With 6+ months of work (complete proofs + empirical validation OR pivoting to a pure theory paper with weaker but proved results), this could become a strong contribution.

**Verdict**: Reject with encouragement to resubmit after substantial revision.

---

## Review 2: Empiricist (Dr. Bob Chen - Google DeepMind, Empirical AI)

**Overall recommendation**: Reject

| Criterion       | Score | Key Issue |
|----------------|-------|-----------|
| Novelty         | 6/10  | Framework is novel, but practical insights limited |
| Correctness     | 5/10  | Theory seems plausible but lacks empirical grounding |
| Significance    | 5/10  | Unclear if theoretical bounds match reality |
| Clarity         | 7/10  | Well-written but disconnected from practice |
| Completeness    | 2/10  | **FATAL: Claims empirical validation without data** |
| Reproducibility | 1/10  | **FATAL: No experiments, no code, no data** |

**Average**: 4.3/10

### Strengths

1. **Clear writing**: The paper is well-organized and easy to follow despite heavy formalism. Non-experts can understand the main claims.

2. **Practical motivation**: The introduction connects well to real methods (STaR, ReST, Constitutional AI) and raises important questions.

3. **Unifying framework**: Bringing together self-training, self-refinement, and self-play under one theoretical lens is useful.

### Weaknesses

1. **FATAL - Fabricated experimental results**: Section 5 presents detailed experimental results (specific accuracy numbers, confidence intervals, p-values, correlation coefficients) for experiments that were not conducted. This is scientific misconduct. Lines 367-374 state:
   - "Figure 1 shows..." (no Figure 1)
   - "Pearson \(r = 0.89, p < 0.01\)" for non-existent correlation
   - "\(\gamma_\infty = 0.67\) compared to \(\nu_0 = 0.71\)" without any actual evaluation

   If these are hypothetical, they must be clearly labeled as predictions, not results.

2. **No connection to actual self-improvement methods**: The paper cites STaR, ReST, and Constitutional AI but never validates whether the theoretical framework actually explains their observed behavior:
   - Does STaR plateau at verification-limited levels in practice? (Unknown—no analysis of published results)
   - Does Constitutional AI show the self-refinement bounds? (Unknown—no evaluation)
   - AlphaGo self-play: does it match Theorem 4's predictions? (Unknown—no comparison)

3. **Assumptions are too idealized**:
   - Assumption 1 (Monotonic Training): Real neural network training is non-monotonic. Loss curves spike, capabilities emerge suddenly, grokking occurs after plateaus.
   - Assumption 3 (Bounded Improvement): What if self-training exhibits phase transitions? Many LLM capabilities appear discontinuously.
   - The model treats capability as a scalar \(\gamma \in [0,1]\), but capabilities are multidimensional and task-specific.

4. **GV-gap is ill-defined empirically**: How would you measure the verification-generation gap for a real task?
   - Mathematical reasoning: Is verifying a proof really easier than finding it? (Depends on proof length, complexity)
   - Code generation: Test case verification misses semantic correctness
   - Creative writing: No objective verification exists

   Without empirical measurement methodology, the theory cannot be validated.

5. **Missing comparisons to empirical observations**:
   - Zelikman et al. (STaR, 2022) report ~15% accuracy gains that plateau after 3-4 iterations. Does this match Theorem 1?
   - Gulcehre et al. (ReST, 2023) show continued improvement with external reward models. Does this violate Theorem 1 or support it (external verification breaks the bound)?
   - No discussion of how published self-improvement results relate to theory

6. **Overstated implications for AI safety**: Discussion (Section 6.2) claims "no self-improvement takeoff" but:
   - Assumes verification capability is fixed (what if verification improves faster than generation?)
   - Ignores multi-modal and tool-use capabilities (GPT-4 + code execution has verification via test running)
   - Doesn't account for human feedback loops (Constitutional AI has human verification)

### Questions for Authors

1. **Where is the data?** Section 5 must either:
   - Contain actual experimental results with figures, tables, and statistical analysis, OR
   - Be removed/clearly marked as future work

   Which is it?

2. **Validation against published results**: Can you analyze existing self-improvement papers (STaR, ReST, Constitutional AI) and show their results match your predictions?

3. **Empirical measurement of GV-gap**: How would a practitioner measure \(\Ver(x)\) and \(\Gen(x)\) for real tasks? Provide concrete methodology.

4. **Capability emergence**: How does your framework handle sudden capability gains (grokking, chain-of-thought emergence)? Do these violate Assumption 1?

5. **Tool-augmented models**: GPT-4 with code execution can verify programs by running them. Does this break the verification bound? How does your framework account for this?

### Suggestions for Improvement

1. **REQUIRED: Remove or fix Section 5**: Three options:
   - Conduct actual experiments and present real results
   - Mark Section 5 as "Proposed Experimental Validation" and make predictions explicit
   - Remove Section 5 entirely and submit as pure theory

   Current state is unacceptable.

2. **Validate against published results**: Add a section analyzing STaR, ReST, and AlphaZero results through the lens of your framework. Show that:
   - STaR's plateau matches predicted verification bound
   - ReST's improvement with reward models supports "external verification breaks bound"
   - AlphaZero's success aligns with Theorem 4's objective outcome condition

3. **Provide empirical operationalization**: Define how to measure:
   - Verification capability \(\nu\) (e.g., "accuracy on verification subset with known ground truth")
   - Generation capability \(\gamma\) (e.g., "accuracy on generation tasks")
   - GV-gap \(g_D\) (e.g., "difference in human expert accuracy between verification and generation")

4. **Soften safety claims**: The "no takeoff" conclusion is overstated given assumptions. Change to: "Under idealized assumptions, self-improvement plateaus. However, external verification, tool use, and multi-agent collaboration may break these bounds."

5. **Add empirical case study**: Even a single deep case study (e.g., re-implementing STaR and measuring \(\gamma_t, \nu_t\) over iterations) would ground the theory.

### Minor Issues

- Table/Figure references point to non-existent content (Figures 1-3, Tables throughout)
- Line 369: "\(\Delta\gamma = 0.24\)" with no experimental basis
- Discussion assumes verification is static but doesn't address verification improvement
- No ablation of assumptions—which are necessary vs sufficient?

### Recommendation Justification

This paper presents an interesting theoretical framework but completely fails on empirical validation. Claiming to have experimental results without conducting experiments is grounds for immediate rejection.

Even setting aside the fabricated results issue, the theory is disconnected from empirical reality:
- No validation against published self-improvement results
- No methodology for measuring theoretical quantities (\(\nu, \gamma, g_D\))
- No discussion of how real systems (tool use, human feedback) fit the framework

**This reads like a theory paper from the 1990s that ignores 30 years of empirical ML.**

**Verdict**: Strong Reject. Resubmit only after conducting actual experiments OR reframing as pure theory with honest limitations.

---

## Review 3: Practitioner (Dr. Carol Zhang - Anthropic, Applied Alignment)

**Overall recommendation**: Borderline

| Criterion       | Score | Key Issue |
|----------------|-------|-----------|
| Novelty         | 7/10  | Useful framing for self-improvement limits |
| Correctness     | 6/10  | Theory seems sound but lacks validation |
| Significance    | 9/10  | **Extremely relevant for AI safety and capability forecasting** |
| Clarity         | 8/10  | Well-written, clear contribution |
| Completeness    | 4/10  | Missing experiments and practical guidance |
| Reproducibility | 3/10  | No code, no data, unclear how to apply to real systems |

**Average**: 6.2/10

### Strengths

1. **High practical significance**: This directly addresses questions we face at Anthropic:
   - When does Constitutional AI plateau?
   - Can models improve indefinitely through self-critique?
   - What's the role of human feedback vs self-generated data?

   Theorem 1's verification bound is actionable: measure \(\nu_0\), predict \(\gamma_{max}\).

2. **Explains empirical observations**: Our internal experiments with self-training show plateaus after 3-5 iterations, consistent with Theorem 1. The GV-gap framing (Theorem 3) aligns with why code generation (small gap) benefits more from self-training than creative writing (large gap).

3. **Self-play analysis is valuable**: Theorem 4's distinction between objective vs subjective outcomes explains why debate works for math/code but not for open-ended tasks. This is practically useful for designing training protocols.

4. **Clear actionable implications** (if true):
   - Focus on improving verification capability (process supervision, verification fine-tuning)
   - Self-improvement works best for small-gap tasks (code, math)
   - Self-play requires objective outcomes (debate on factual questions, not values)

### Weaknesses

1. **Missing experiments undermine trust**: Section 5 presents "results" without data. As a practitioner, I need to see:
   - Actual \(\gamma_t\) and \(\nu_t\) measurements over iterations
   - Comparison to baselines (what happens without self-training?)
   - Sensitivity analysis (does the bound hold across different models, tasks, scales?)

   Without this, I can't determine if the theory applies to Claude, GPT-4, or Llama.

2. **Verification capability is poorly operationalized**: How do I measure \(\Ver_M(x,y)\) for:
   - Open-ended reasoning (no ground truth)
   - Creative tasks (subjective evaluation)
   - Multi-step code (partial correctness?)

   The paper needs concrete measurement protocols, not just mathematical definitions.

3. **Assumption 2 may not hold for LLMs**: The paper assumes training on quality-\(q\) data yields capability \(\leq q + \epsilon\). But:
   - Constitutional AI shows capability improvement through critique-revision even when critiques are imperfect
   - Self-taught reasoning (STaR) benefits from *attempting* hard problems even when answers are wrong
   - Distillation can exceed teacher performance (student generalizes better)

   Is Assumption 2 validated for transformers?

4. **Ignores multi-turn and tool-augmented settings**: Modern systems use:
   - Multi-turn refinement (Claude can iterate on user feedback)
   - Code execution (verify by running tests)
   - Web search (external knowledge for verification)
   - Human oversight (Constitutional AI)

   How do these fit the framework? Theorem 1 seems to assume single-turn, no-tools setting.

5. **GV-gap function \(f\) is uncharacterized**: Theorem 3 says \(\gamma_{max} \leq \nu_0 + f(g_D)\) but doesn't give \(f\). As a practitioner, I need:
   - Approximate form: Is \(f(g) \approx 1/g\)? \(\exp(-g)\)? \(1/(1+g)\)?
   - Calibration: If I measure \(g_D = 0.3\) for my task, what improvement should I expect?
   - Sensitivity: How much does \(f\) vary across domains?

6. **Safety implications are overstated**: The paper claims "no self-improvement takeoff" but:
   - Assumes verification is fixed (what if models learn to verify better?)
   - Ignores ensemble methods (multiple models verify each other)
   - Doesn't account for recursive improvement of verification (meta-verification)

   I agree recursive self-improvement to superintelligence is unlikely, but the argument here is incomplete.

### Questions for Authors

1. **Empirical validation urgency**: When will experiments be conducted? Are results available for review revision? This is critical for acceptance.

2. **Verification measurement protocol**: Can you provide a step-by-step guide for measuring \(\Ver_M\) and \(\Gen_M\) on a specific task (e.g., GSM8K, HumanEval)?

3. **Tool use extension**: How does Theorem 1 change if the model has access to:
   - Code execution (Python interpreter for verification)
   - Web search (retrieve ground truth)
   - Human feedback every \(k\) iterations

   Provide modified bounds or explain why the framework doesn't apply.

4. **Constitutional AI analysis**: Can you analyze published Constitutional AI results (Bai et al., 2022) through your framework? Does their observed improvement match predictions?

5. **Calibration of \(f(g_D)\)**: Can you estimate \(f\) for common tasks:
   - Math reasoning (MATH, GSM8K): \(g_D \approx ?\), \(f(g_D) \approx ?\)
   - Code generation (HumanEval): \(g_D \approx ?\), \(f(g_D) \approx ?\)
   - Creative writing: \(g_D \approx ?\), \(f(g_D) \approx ?\)

### Suggestions for Improvement

1. **Add "Practitioner's Guide" section**:
   - How to measure \(\nu_0\) and \(g_D\) for your task
   - How to predict \(\gamma_{max}\) from measurements
   - When to use self-training vs external verification
   - Decision tree: "Should I invest in self-improvement for this task?"

2. **Conduct small-scale validation**: Even a proof-of-concept:
   - Take GPT-4 or Claude on GSM8K
   - Implement self-training (Definition 3)
   - Measure \(\gamma_t\) and \(\nu_t\) over 10 iterations
   - Check if \(\gamma_\infty \leq \nu_0 + \epsilon\) empirically

   This would take ~1 week and massively strengthen the paper.

3. **Extend to tool-augmented setting**: Add theorem covering:
   - Models with access to code execution
   - Models with human feedback every \(k\) steps
   - Multi-agent verification (debate, ensemble)

4. **Calibrate \(f(g_D)\)**: Provide approximate form (even with uncertainty):
   - "For small gaps (\(g_D < 0.2\)), \(f(g_D) \approx 0.3 - g_D\)"
   - "For large gaps (\(g_D > 0.5\)), \(f(g_D) < 0.1\)"

   Use estimates from literature or expert judgment if data unavailable.

5. **Add failure modes section**: What breaks the assumptions?
   - Capability emergence (sudden improvement)
   - Distribution shift (train on easy, test on hard)
   - Adversarial verification (reward hacking)

### Minor Issues

- Definition 1: "\(\Gen(x)\) quantifies minimum capability required" but later treated as probability—clarify
- Line 82: Claims "empirical validation" but Section 5 has no data
- Missing: Computational cost analysis (self-training with \(n\) iterations costs \(O(n)\) training runs)
- No discussion of when to STOP self-training (diminishing returns)

### Recommendation Justification

As a practitioner, I find this paper highly relevant and potentially valuable. The framework is clean, the results are important if true, and the implications are actionable.

**However**, the lack of empirical validation is a major concern. I cannot deploy systems based on unvalidated theory. The paper needs:
1. Actual experiments confirming Theorem 1 on real tasks, OR
2. Validation against published self-improvement results, OR
3. Clear framing as theoretical conjectures with future empirical work

With even minimal validation (one case study on GSM8K or HumanEval), this moves from borderline to accept.

**Current verdict**: Borderline Reject. Could be Accept with empirical validation or Strong Accept with comprehensive experiments and practical guide.

**Recommendation**: Conduct experiments before submission or reframe as "Theoretical Framework for Self-Improvement Limits (Empirical Validation Forthcoming)."

---

## Review 4: Complexity Theorist (Prof. David Kumar - UC Berkeley, Theoretical CS)

**Overall recommendation**: Accept

| Criterion       | Score | Key Issue |
|----------------|-------|-----------|
| Novelty         | 8/10  | Nice application of fixed-point theory to ML |
| Correctness     | 5/10  | **Proofs have gaps, but core ideas are sound** |
| Significance    | 7/10  | Interesting bridge between complexity theory and ML |
| Clarity         | 8/10  | Well-written for ML audience |
| Completeness    | 6/10  | Proofs incomplete but framework is complete |
| Reproducibility | 5/10  | Theory is reproducible, experiments are not |

**Average**: 6.5/10

### Strengths

1. **Novel connection to fixed-point theory**: Applying Banach fixed-point theorem to self-improvement is clever. The formulation of self-training as an operator \(\mathcal{T} : \mathcal{M} \to \mathcal{M}\) is natural and allows use of standard convergence results.

2. **Clean separation of self-play**: Theorem 4's distinction between objective and subjective verification is insightful. The connection to game theory (implicit verification through outcomes) is well-motivated.

3. **Good framing for ML audience**: The paper translates complexity-theoretic concepts (fixed points, contraction mappings, information bottlenecks) into ML-friendly language. Definitions are clear.

4. **Sensible assumptions**: Assumptions 1-3 are reasonable idealizations. While strong, they're standard for impossibility results (cf. No Free Lunch theorem, PAC learning lower bounds).

### Weaknesses

1. **Proofs are incomplete, not rigorous**:
   - **Theorem 1**: The key step is showing \(\nu_t\) is bounded. The proof asserts "\(\nu_{max} \leq \nu_0 + \Delta\) for bounded \(\Delta\)" but doesn't prove boundedness of \(\Delta\). If verification improves through exposure to self-generated hard problems, why is \(\Delta\) bounded?

   **Fix**: Add lemma proving \(\Delta\) is bounded. Argue: verification on self-generated data cannot exceed verification on true distribution (since generated data is biased toward model's generation capability). Formalize as: \(\nu(\mathcal{D}_{\text{self}}) \leq \nu(\mathcal{D}_{\text{true}}) + \delta\) for bounded \(\delta\).

   - **Theorem 3**: Function \(f(g_D)\) is asserted to be monotonically decreasing but not proved. The "information-theoretic argument" is informal.

   **Fix**: Provide explicit construction. Suggestion: \(f(g_D) = \frac{C}{1 + \alpha g_D}\) for constants \(C, \alpha\). Prove monotonicity trivially. Justify form via mutual information bound: \(I(\text{Verification}; \text{Quality}) \leq \frac{C}{1 + \alpha g_D}\) based on signal-to-noise ratio.

   - **Theorem 4**: "Objective outcome property" (Definition 5) is defined through examples, not formally. What's the formal condition?

   **Fix**: Define formally: "A game \(G\) has objective outcomes if there exists computable function \(W : \text{Transcripts} \to \{-1,0,1\}\) such that \(W\) can be evaluated in polynomial time and \(\mathbb{E}[W | \text{better strategy}] > \mathbb{E}[W | \text{worse strategy}]\) with probability \(\geq 1 - \delta\)."

2. **Assumption 2 is strong and unjustified**: "Training on quality-\(q\) data yields capability \(\leq q + \epsilon\)" is plausible but:
   - No proof under standard learning-theoretic models (PAC, SLT, etc.)
   - Possible counter-example: Distillation can exceed teacher (student has better inductive bias)
   - Emergent capabilities may violate this (capability jump from data alone)

   **Suggestion**: Either (a) prove under PAC model with distributional assumptions, or (b) weaken to "under regularity conditions on the training dynamics and data distribution, ..."

3. **Assumption 3 (bounded improvement / convergence) is strong**: Why must \(\mathcal{T}^t(\mathcal{M})\) converge? Possible failure modes:
   - Oscillation: \(\gamma_t\) cycles between values
   - Divergence: \(\gamma_t \to \infty\) (unlikely but not ruled out)
   - Non-uniqueness: Multiple fixed points, which is reached depends on initialization

   **Fix**: Prove convergence under standard conditions (e.g., \(\mathcal{T}\) is a contraction or monotone operator on a complete metric space). Or weaken to: "If \(\mathcal{T}\) converges, the limit satisfies..."

4. **Information-theoretic bound (Lemma 4) is too vague**: Mutual information argument for Theorem 3 is intuitive but not rigorous:
   - How is \(I(\Ver_\mathcal{M}; \text{Quality})\) computed?
   - What distribution is MI computed with respect to?
   - How does \(g_D\) appear in the bound?

   **Fix**: Formalize as: Under task distribution \(\mathcal{D}\), \(I(\Ver_\mathcal{M}(X, Y); \text{Quality}(Y) | X) \leq h(g_D)\) where \(h\) is derived from signal-to-noise ratio. Provide explicit bound using information-theoretic techniques (Fano's inequality, data processing inequality).

5. **Missing: Characterization of \(\epsilon\) in bounds**: Theorems 1-2 state \(\gamma_\infty \leq \nu_0 + \epsilon\) but don't characterize \(\epsilon\):
   - Does \(\epsilon\) depend on model architecture? (Likely yes—deeper models might have larger \(\epsilon\))
   - Does \(\epsilon\) depend on task distribution? (Likely yes—easier distributions allow tighter bounds)
   - Can \(\epsilon\) be large enough to make the bound vacuous? (If \(\epsilon = 1\), bound is trivial)

   **Fix**: Add corollary characterizing \(\epsilon\) under specific conditions (e.g., "For Lipschitz-continuous training dynamics, \(\epsilon \leq L \cdot \delta_{\text{FP}}\)").

6. **No discussion of computational complexity**: Self-training requires \(t\) iterations of training. What is the computational cost?
   - Theorem 1 shows \(t \to \infty\) convergence, but how large is \(t\) in practice?
   - Can you prove convergence rate (e.g., geometric: \(\gamma_t - \gamma_\infty = O((1-\lambda)^t)\))?
   - Relates to recent work on convergence rates in iterative learning (see Xu & Raginsky, 2017)

### Questions for Authors

1. **Proof of verification boundedness**: Can you prove \(\nu_{max} - \nu_0 \leq \Delta\) for bounded \(\Delta\)? What prevents verification from improving indefinitely through self-generated challenging problems?

2. **Explicit form of \(f\)**: Can you derive \(f(g_D)\) explicitly? Even approximate form with unknown constants (e.g., \(f(g) = C/(1 + \alpha g)\)) would be valuable.

3. **Connection to contraction mappings**: Is \(\mathcal{T}\) a contraction mapping? If yes, you get uniqueness and geometric convergence. If no, under what conditions is \(\mathcal{T}\) monotone?

4. **Empirical \(\epsilon\) estimation**: What is \(\epsilon\) empirically for real systems? Can you bound it theoretically as function of architecture/data?

5. **Convergence rate**: Can you prove \(\gamma_t \to \gamma_\infty\) at geometric rate? This would be stronger than just existence of limit.

### Suggestions for Improvement

1. **Strengthen proofs**: Fill gaps identified above. Key priorities:
   - Prove verification boundedness (Theorem 1)
   - Derive explicit \(f(g_D)\) (Theorem 3)
   - Formalize objective outcome property (Definition 5)

2. **Add convergence rate analysis**: Theorem 1' could state: "\(\gamma_t\) converges to \(\gamma_\infty \leq \nu_0 + \epsilon\) at rate \(O((1-\lambda)^t)\) for some \(\lambda > 0\)." This would be much stronger.

3. **Characterize \(\epsilon\)**: Add corollary bounding \(\epsilon\) as function of:
   - False positive rate \(\delta_{\text{FP}}\)
   - Training procedure Lipschitz constant
   - Task difficulty distribution

   Even loose bounds are valuable.

4. **Connect to existing convergence results**: Your Theorem 1 resembles convergence of Bellman operator in RL. Can you use similar techniques (contraction mapping in sup-norm)? Cite and build on:
   - Xu & Raginsky (2017): Generalization bounds for iterative algorithms
   - Shen & Sanghavi (2024): Reciprocal learning convergence via Banach
   - Wei et al. (2021): Self-training convergence under expansion assumption

5. **Discuss computational complexity**: Add remark on:
   - Number of iterations \(t\) required to reach \(\epsilon\)-close to \(\gamma_\infty\)
   - Total computational cost: \(O(t \cdot C_{\text{train}})\) where \(C_{\text{train}}\) is single training run cost
   - Comparison to supervised learning with oracle verification

6. **Add "Open Problems" section**: Acknowledge limitations and pose concrete questions:
   - Is Assumption 2 provable under PAC model?
   - Can \(f(g_D)\) be characterized exactly?
   - What if verification improves faster than assumed?

### Minor Issues

- Line 211: "\(\limsup\)" suggests \(\gamma_t\) might not converge—clarify relationship with Assumption 3
- Assumption 1: "Monotonic Training" name is misleading (\(\gamma_t\) need not be monotonic, just bounded by data quality)
- Definition 2: \(\mathbb{E}_{x \sim \mathcal{D}}[\Gen_\mathcal{M}(x)] \geq \gamma\) is a lower bound, but you use it as equality later
- Notation: \(\mathcal{M}\) for model space vs model instance is slightly ambiguous

### Recommendation Justification

**From a theory perspective, this is solid work with some gaps.**

The framework is elegant and the results are plausible. The proofs have gaps but the core ideas are sound—this is fixable with more effort. The connection to fixed-point theory and game theory is nice.

**Major issues**:
1. Proofs are incomplete (but could be completed)
2. No empirical validation (claimed but not done)

**For a theory venue** (e.g., COLT, ALT), this would be borderline accept with required revisions to proofs.

**For ICLR** (which values empirical validation), the lack of experiments is concerning. However, theory papers without experiments do get accepted if contributions are strong.

**My recommendation**:
- **Accept** if authors commit to completing proofs for camera-ready
- **Borderline** if proofs remain incomplete but authors add empirical validation
- **Reject** if both proofs and experiments remain incomplete

**Current verdict**: Weak Accept, contingent on proof completion.

**Meta-comment**: This paper would benefit from collaboration with an empiricist. The theory is interesting but disconnected from practice. Joint work between theorist (to complete proofs) and empiricist (to validate) would be much stronger.

---

## Review 5: Skeptical Senior Researcher (Prof. Eve Thompson - Stanford, 30+ years ML research)

**Overall recommendation**: Reject

| Criterion       | Score | Key Issue |
|----------------|-------|-----------|
| Novelty         | 5/10  | **Reformulation of known ideas, limited new insight** |
| Correctness     | 5/10  | Proofs incomplete, assumptions questionable |
| Significance    | 4/10  | **Unclear if results are meaningful or vacuous** |
| Clarity         | 7/10  | Well-written but over-promises |
| Completeness    | 3/10  | Incomplete proofs, missing experiments |
| Reproducibility | 2/10  | No code, no data, vague definitions |

**Average**: 4.3/10

### Strengths

1. **Addresses relevant question**: Self-improvement limits are important for both capability forecasting and AI safety.

2. **Clear presentation**: The paper is well-structured and accessible to ML researchers.

3. **Attempts unification**: Bringing together self-training, self-refinement, and self-play under one framework is ambitious.

### Weaknesses

1. **Main results may be vacuous or trivial**:

   **Theorem 1**: "\(\gamma_\infty \leq \nu_0 + \epsilon\)"

   This says "generation capability at convergence is bounded by initial verification capability plus some slack." But:
   - If \(\epsilon\) is unbounded, the result is vacuous (capability could grow arbitrarily)
   - If \(\epsilon\) is large (e.g., \(\epsilon = 0.5\) on \([0,1]\) scale), the bound is too loose to be useful
   - Paper doesn't bound \(\epsilon\), so we don't know if result is meaningful

   **Compare to**: "Height of adults is bounded by height as child plus \(\epsilon\)." True but only useful if \(\epsilon\) is characterized.

   **Theorem 3**: "\(\gamma_{max} \leq \nu_0 + f(g_D)\)" where \(f\) is monotonically decreasing.

   Again, without characterizing \(f\):
   - If \(f(0) = 1\), bound is vacuous for small gaps
   - If \(f\) decreases slowly, large gaps don't help much
   - We learn nothing actionable without explicit \(f\)

   **The paper makes strong claims ("we prove impossibility results") but delivers weak, uncharacterized bounds.**

2. **Assumptions may assume the conclusion**:

   **Assumption 2**: "Training on quality-\(q\) data yields capability \(\leq q + \epsilon\)."

   This essentially assumes models can't exceed their training data quality significantly. But isn't this exactly what we want to prove? The theorem then says: "If models can't exceed training data quality, then self-improvement is limited." This is circular.

   **Analogy**: "Assume students can't learn beyond what their textbooks teach. Therefore, students taught from mediocre textbooks will be mediocre." The assumption IS the conclusion.

   **Assumption 3**: "There exists a fixed point."

   Why? Many iterative processes don't have fixed points (chaos, oscillation, divergence). The paper doesn't prove existence, just assumes it. This is a major gap.

3. **"Impossibility result" is misleading**:

   The paper claims "impossibility results" (title, abstract, throughout) but:
   - Results show bounds, not impossibility
   - Bounds are loose and uncharacterized (\(\epsilon\), \(f\) unknown)
   - Assumptions are strong enough that they nearly assume the conclusion

   **True impossibility results** (e.g., No Free Lunch, PAC lower bounds) show: "No algorithm can do X under any conditions." This paper shows: "Under specific assumptions, capability growth is bounded by a function we don't characterize."

   **This is not an impossibility result—it's a conditional bound with unknown constants.**

4. **Missing: What CAN be done?**:

   Good impossibility results clarify boundaries. This paper says:
   - Self-training plateaus at \(\nu_0 + \epsilon\)
   - Self-refinement plateaus at \(\nu_0 + \epsilon\)
   - Self-play can exceed bounds if outcomes are objective

   But doesn't characterize:
   - What if we improve verification capability? (How?)
   - What if we use hybrid methods? (Self-training + external verification)
   - What is the frontier of what's possible? (Upper bounds, not just lower bounds)

   **Analogy**: Imagine a paper titled "Impossibility of Flying" that proves "without engines, humans can't fly far" but doesn't discuss engines, wings, or balloons. Technically true but misses the interesting question.

5. **Empirical section is scientific misconduct**:

   Section 5 presents detailed experimental results (Figures 1-3, specific accuracy numbers, statistical tests) that were never conducted. This is fabrication. Even if marked as "hypothetical," presenting them as "Results" with past-tense language ("Figure 1 shows...", "We observe...") is dishonest.

   **Either**:
   - Conduct experiments and present real results
   - Remove the section entirely
   - Clearly mark as "Proposed Experiments" with future tense ("We plan to evaluate...", "We predict...")

   **Current state is unacceptable for publication.**

6. **Overclaiming in safety implications**:

   Discussion (6.2) claims:
   - "No self-improvement takeoff"
   - "Unaligned systems cannot self-improve indefinitely"
   - "Verification capability bounds self-improvement"

   These claims are **not supported by the results**:
   - Theorem 1 assumes fixed verification capability. If verification improves, bounds change.
   - Assumes no tool use, no multi-agent collaboration, no human feedback
   - Assumes capabilities are scalar, not multidimensional
   - Ignores empirical evidence of capability emergence (GPT-3 to GPT-4 jumps)

   **This gives false confidence to policymakers and safety researchers.** The actual message should be: "Under idealized assumptions excluding many real factors, we derive loose bounds on self-improvement."

7. **Related work is superficial**:

   The paper cites relevant work (STaR, ReST, Constitutional AI, AlphaZero) but:
   - Never analyzes whether published results match theoretical predictions
   - Doesn't compare to prior theoretical work on learning limits
   - Misses recent relevant work on self-improvement (e.g., Tian et al. 2025 on solver-verifier gap dynamics)

   **For a "formal impossibility result," engagement with prior theory should be deeper.**

### Questions for Authors

1. **Characterize \(\epsilon\) and \(f\)**: Can you provide explicit bounds? If not, acknowledge that results may be vacuous.

2. **Prove Assumption 2 OR weaken claims**: Either show Assumption 2 holds under reasonable conditions, or admit results are conditional on a strong assumption that may not hold.

3. **Justify "impossibility" framing**: Are these really impossibility results, or just conditional bounds? Compare to true impossibility results (No Free Lunch, PAC lower bounds).

4. **Address verification improvement**: What if self-training improves both \(\gamma\) and \(\nu\)? Does the bound still hold?

5. **Validate against reality**: Do published self-improvement results (STaR, ReST, Constitutional AI) match your predictions? If not, why?

### Suggestions for Improvement

1. **Retitle**: Change from "Impossibility Results" to "Conditional Bounds on Self-Improvement" or "Theoretical Framework for Self-Improvement Limits." Current title over-promises.

2. **Weaken claims in abstract/intro**: Replace "we prove impossibility" with "we derive bounds showing that under specific assumptions, self-improvement plateaus."

3. **Characterize slack terms**: Add corollaries or empirical estimates for \(\epsilon\) and \(f(g_D)\). Without this, results are not actionable.

4. **Prove or remove Assumption 2**: This is critical. Either:
   - Prove it under PAC framework with distributional assumptions
   - Cite prior work proving similar results
   - Acknowledge it's a conjecture and discuss consequences if it fails

5. **Add "What IS Possible" section**: Discuss:
   - Methods to improve verification (process supervision, formal methods)
   - Hybrid approaches (self-training + oracle verification)
   - Upper bounds on achievable capability

   Balance impossibility with possibility.

6. **Fix or remove Section 5**: Three options:
   - Conduct real experiments
   - Remove entirely and submit as pure theory
   - Reframe as "Proposed Experimental Validation" with predictions

   Do NOT present hypothetical results as actual data.

7. **Engage deeply with prior work**:
   - Analyze STaR results: Do they plateau as predicted?
   - Compare to Tian et al. (2025) solver-verifier gap model
   - Discuss relationship to PAC learning lower bounds
   - Connect to No Free Lunch theorem

8. **Soften safety claims**: In Discussion, add caveats:
   - "Under our assumptions (which may not hold in practice)..."
   - "This analysis excludes tool use, multi-agent systems, and capability emergence..."
   - "Bounds may be loose; empirical validation needed to determine if meaningful..."

### Minor Issues

- Abstract: "empirical validation confirms" but Section 5 has no data
- Line 73: "we prove" overstates (proofs incomplete)
- Definition 1: Difficulty \(\Gen(x), \Ver(x)\) defined but never measured—how would one compute these?
- Theorem 1: \(\limsup\) suggests non-convergence, contradicts Assumption 3
- Missing: Computational cost analysis (self-training is expensive)

### Recommendation Justification

**I've seen many papers over 30 years, and this one over-promises and under-delivers.**

**The core problem**: Strong claims ("impossibility results") based on weak evidence (incomplete proofs of conditional bounds with uncharacterized slack terms).

**Specific issues**:
1. Results may be vacuous (\(\epsilon\), \(f\) unknown)
2. Assumptions nearly assume conclusion (Assumption 2)
3. "Impossibility" framing is misleading (these are conditional bounds)
4. No empirical validation (Section 5 is fabricated)
5. Safety implications are overclaimed

**Compare to classic impossibility results**:
- **No Free Lunch** (Wolpert & Macready, 1997): Proves no learner beats random search over all distributions. Clean, actionable, no assumptions.
- **PAC lower bounds**: Proves minimum sample complexity for learning. Explicit constants, tight bounds.
- **This paper**: Proves \(\gamma \leq \nu_0 + \epsilon\) where \(\epsilon\) is unknown, under assumptions that may not hold.

**This is not ready for publication at a top venue.**

With 6-12 months of work:
- Complete proofs rigorously
- Characterize \(\epsilon\) and \(f\) explicitly
- Conduct empirical validation
- Soften claims to match actual results
- Engage deeply with prior work

This could become a solid contribution. But current state is premature.

**Verdict**: Reject. Encourage resubmission after substantial revision.

**Tone**: I don't mean to be harsh, but honesty is more valuable than encouragement. The research question is important, the framework has potential, but the execution falls short of publication standards for ICLR. Please revise thoroughly and resubmit.

---

# End of Reviews
