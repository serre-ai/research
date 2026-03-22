# Self-Training Convergence Bound: Proof Strategy and Mathematical Tools
**Date**: 2026-03-22
**Scope**: Literature survey on proof techniques for establishing convergence bounds in self-training systems
**Linear Issue**: DW-60 - Prove self-training convergence bound

## Research Question

How to rigorously prove that self-training without external verification converges to a fixed point bounded by the model's initial verification capability?

**Target Theorem** (from paper draft):
> Let \(\M_0\) be an initial model with verification capability \(\nu_0 = \E_{x \sim \D}[\Ver_{\M_0}(x)]\). Let \(\M_t = \T^t(\M_0)\) denote the model after \(t\) iterations of self-training. Under Assumptions (monotonic training, verification-generation gap, bounded improvement), there exists \(\epsilon > 0\) such that:
> \[
> \limsup_{t \to \infty} \Gen_{\M_t} \leq \nu_0 + \epsilon
> \]

## Proof Strategy Overview

Based on literature survey, the proof should follow this structure:

### **Stage 1: Show filtered data quality is bounded by verification capability**
- Formalize relationship between verification accuracy and training data quality
- Prove lemma: Expected quality of filtered dataset \(\D_t^+\) is at most \(\nu_t + \delta_{FP}\)
- Use probabilistic argument over verification judgments

### **Stage 2: Show training on quality-q data produces capability bounded by q**
- Invoke Assumption 1 (monotonic training) or prove it from first principles
- Establish \(\Gen_{\M_{t+1}} \leq \text{Quality}(\D_t^+) + \epsilon_{\text{train}}\)
- Account for generalization error and optimization slack

### **Stage 3: Combine bounds iteratively to establish convergence**
- Show verification capability is non-decreasing but bounded: \(\nu_t \leq \nu_{t+1} \leq \nu_{\max}\)
- Establish \(\nu_{\max} \leq \nu_0 + \Delta\) for some finite \(\Delta\)
- Prove fixed-point convergence using contraction or monotone convergence
- Conclude \(\Gen_{\M_{\infty}} \leq \nu_0 + \epsilon\) where \(\epsilon = \Delta + \delta_{FP} + \epsilon_{\text{train}}\)

### **Stage 4: Characterize conditions for unique vs multiple fixed points**
- Apply Banach fixed-point theorem if contraction property holds (unique fixed point)
- Apply Tarski fixed-point theorem if monotonicity holds on lattice (multiple fixed points possible)
- Characterize initial condition dependence if multiple equilibria exist

## Mathematical Tools and Techniques

### 1. Contraction Mapping and Banach Fixed-Point Theorem

**Classical Result**: [Banach Fixed-Point Theorem](https://en.wikipedia.org/wiki/Banach_fixed-point_theorem)
- Every contraction mapping on a complete metric space has a **unique** fixed point
- **Contraction property**: \(d(f(x), f(y)) \leq \lambda d(x, y)\) for \(\lambda < 1\)
- **Convergence guarantee**: Iterative sequence \(x, f(x), f^2(x), \ldots\) converges geometrically to fixed point
- **Rate**: \(d(f^n(x), x^*) \leq \lambda^n d(x, x^*)\)

**Applications in ML/RL**:
- [Bellman operator convergence](https://www.tuananhle.co.uk/notes/bellman-convergence.html): Policy iteration and value iteration use Bellman operator as contraction with discount factor \(\gamma < 1\)
- [Deep equilibrium models](https://link.springer.com/article/10.1007/s13398-024-01636-6): Fixed points of neural network layers
- [Reciprocal learning convergence](https://arxiv.org/html/2408.06257): Proves self-training algorithms converge at linear rates when sample adaptation is Lipschitz

**Proof technique for our setting**:
1. Define metric \(d(\M, \M') = \| \Gen_{\M} - \Gen_{\M'} \|_{\infty}\) on model space
2. Show self-training operator \(\T\) satisfies \(d(\T(\M), \T(\M')) \leq \lambda d(\M, \M')\) for some \(\lambda < 1\)
3. This requires bounding how much generation capability can change between iterations
4. Challenge: \(\T\) may not be globally contracting - may need to restrict to subset of model space or use different metric

**Alternative**: [Converse to Banach theorem](https://arxiv.org/abs/1702.07339) - If iterative map converges to unique fixed point, there exists a metric under which it is contracting. We can prove convergence first, then invoke this result to characterize the metric.

### 2. Monotone Convergence

**Classical Result**: [Monotone Convergence Theorem](https://en.wikipedia.org/wiki/Monotone_convergence_theorem)
- Every bounded monotone sequence converges
- If \(x_n\) is increasing and \(x_n \leq B\) for all \(n\), then \(\lim_{n \to \infty} x_n\) exists and \(\leq B\)

**Application to self-training**:
1. Show capability sequence \(\{\Gen_{\M_t}\}_{t=0}^{\infty}\) is non-decreasing (monotonic improvement)
2. Show sequence is bounded above by \(\nu_0 + \epsilon\) (verification-limited ceiling)
3. Conclude sequence converges to some limit \(\gamma_{\infty} \leq \nu_0 + \epsilon\)

**Proof technique**:
- Monotonic improvement: Training on filtered data of quality \(q_t\) produces model with quality \(\geq q_{t-1}\) (Assumption: training doesn't hurt)
- Bounded above: Quality of filtered data bounded by verification capability, so \(\Gen_{\M_t} \leq \nu_t + \delta \leq \nu_0 + \Delta + \delta\)
- By monotone convergence theorem, limit exists

**Reference**: [Policy Improvement Theorem](https://yuanz.web.illinois.edu/teaching/IE498fa19/lec_16.pdf) in RL proves monotonic improvement of value function, ensuring convergence to optimality. Similar structure applies to self-training.

### 3. Lipschitz Continuity and Smoothness

**Definition**: Function \(f\) is \(L\)-Lipschitz if \(|f(x) - f(y)| \leq L \|x - y\|\)

**Relevance**:
- [Lipschitz constants in neural networks](https://link.springer.com/article/10.1007/s10994-020-05929-w) control generalization and robustness
- [Training dynamics with Lipschitz bounds](https://proceedings.mlr.press/v162/meunier22a/meunier22a.pdf) guarantee convergence rates
- Lipschitz constant \(< 1\) implies contraction

**Application to self-training**:
- Show training procedure \(\text{Train}(\cdot, \D)\) is Lipschitz in model parameters
- Show verification function \(\Ver_{\M}\) is Lipschitz in model capability
- Compose these to bound change in capability per iteration
- If overall Lipschitz constant \(< 1\), have contraction and unique fixed point

**Proof technique**:
1. Establish \(|\Gen_{\M_{t+1}} - \Gen_{\M_t}| \leq L \cdot |\Ver_{\M_t} - \Ver_{\M_{t-1}}|\) for some \(L\)
2. If verification improvement diminishes (\(\Ver_{\M_t} \to \nu_{\max}\)), then generation improvement diminishes
3. Use Cauchy criterion to prove convergence

### 4. Information-Theoretic Bounds

**Key Concept**: [Information Bottleneck Principle](https://lilianweng.github.io/posts/2017-09-28-information-bottleneck/)
- Learning is limited by mutual information between observations and labels
- Generalization bounds scale with information bottleneck, not parameter count

**Application to verification bottleneck**:
- Let \(I(\Ver_{\M}; \text{Quality})\) be mutual information between verification judgments and true solution quality
- When verification capability is limited, this mutual information is bounded
- Learning from self-generated data cannot extract more information than \(I(\Ver_{\M}; \text{Quality})\)

**Proof technique** (for Theorem 3 on GV-gap):
1. Show \(I(\Ver_{\M}; \text{Quality}) \leq h(g_{\D})\) where \(h\) decreases with gap \(g_{\D}\)
2. When gap is large, verification errors increase, reducing mutual information
3. Maximum learnable capability bounded by information available: \(\gamma_{\max} \leq \nu_0 + f(I(\Ver_{\M}; \text{Quality}))\)
4. Derive explicit form for \(f(g_{\D})\) in terms of gap

**Reference**: [Generalization bounds via information theory](https://proceedings.mlr.press/v202/kawaguchi23a/kawaguchi23a.pdf) - Finite sample bounds based on mutual information between algorithm and data

### 5. Error Propagation Analysis

**Key Question**: How do verification errors propagate through iterative training?

**Relevant work**:
- [Error propagation in iterative algorithms](https://arxiv.org/html/2508.12094v3): Derives per-step error propagation equations
- [Generalization error bounds for noisy iterative algorithms](https://ieeexplore.ieee.org/document/8437571/): Bounds based on bounded, noisy updates with Markovian structure
- [Training data error propagation](https://www.mdpi.com/2072-4292/12/6/1034): Errors in training data propagate to model predictions

**Proof technique**:
1. Let \(e_t\) be verification error at iteration \(t\): \(e_t = |\Ver_{\M_t} - \text{TrueVerification}|\)
2. Show filtered data contains false positives/negatives: \(\text{Quality}(\D_t^+) \leq \Ver_{\M_t}(1 - e_t) + e_t \cdot 0 = \Ver_{\M_t}(1 - e_t)\)
3. Training on noisy data: \(\Gen_{\M_{t+1}} \leq \text{Quality}(\D_t^+) + \epsilon_{\text{train}} \leq \Ver_{\M_t}(1 - e_t) + \epsilon_{\text{train}}\)
4. If \(e_t\) bounded away from 0, capability gain per iteration shrinks
5. Total capability gain over infinite iterations: \(\sum_{t=0}^{\infty} (\Gen_{\M_{t+1}} - \Gen_{\M_t})\) converges, implying bounded limit

### 6. Fixed-Point Characterization (Building on Note 01)

From the fixed-point characterization survey, three frameworks apply:

**A. Banach Framework** (Contraction → Unique Fixed Point)
- **When applicable**: If self-training operator is contraction
- **Implication**: Unique fixed point, convergence guaranteed from any initialization
- **Uniqueness**: Only one capability level can be self-consistent
- **Challenge**: May not be globally contracting - need to prove contraction property or restrict domain

**B. Tarski Framework** (Monotone on Lattice → Multiple Fixed Points)
- **When applicable**: If capability space forms lattice and self-training is monotone
- **Implication**: Multiple fixed points possible, but minimal and maximal ones exist
- **Initial condition dependence**: Different initializations may reach different fixed points
- **Basins of attraction**: Capability space partitioned into regions leading to different equilibria
- **Connection**: Explains empirical observations of "reward hacking" (bad fixed points) vs successful self-improvement (good fixed points)

**C. Nash Equilibrium Framework** (Game Theory → Self-Play Fixed Points)
- **When applicable**: Self-play settings where model competes against itself
- **Implication**: Fixed point is Nash equilibrium of game
- **Multiple equilibria**: Games typically have many Nash equilibria
- **Connection**: Addressed in separate theorem (Theorem 4 on self-play)

**Recommended approach for self-training**:
- Use **Tarski framework** if proving general result allowing multiple fixed points
- Use **Banach framework** if can prove contraction property (stronger result, unique fixed point)
- Use **monotone convergence** if neither contraction nor lattice structure is established

## Proof Strategy Recommendation

Based on literature survey, I recommend this proof approach:

### **Approach A: Monotone Convergence (Most Robust)**

**Advantages**:
- Requires minimal assumptions (monotonicity + boundedness)
- Directly applicable to our setting
- Well-understood in RL literature

**Proof outline**:
1. **Lemma 1** (Filtered data quality): \(\E_{(x,y) \sim \D_t^+}[\text{Quality}(y)] \leq \nu_t + \delta_{FP}\)
   - Proof: Verification at capability \(\nu_t\) correctly identifies quality-\(\nu_t\) solutions. False positives contribute at most \(\delta_{FP}\).

2. **Lemma 2** (Training bound): Training on quality-\(q\) data yields \(\Gen_{\M'} \leq q + \epsilon_{\text{train}}\)
   - Proof: Model learns to mimic training data. Generalization error \(\epsilon_{\text{train}}\) bounded by standard learning theory (VC dimension, Rademacher complexity, etc.)

3. **Lemma 3** (Verification improvement bound): \(\nu_t \leq \nu_{t+1} \leq \nu_0 + \Delta\) for some finite \(\Delta\)
   - Proof: Verification can improve through exposure to diverse examples, but only up to model's representational capacity. Bound \(\Delta\) by model complexity.

4. **Main theorem** (Convergence):
   - Combine Lemmas 1-3: \(\Gen_{\M_{t+1}} \leq \nu_t + \delta_{FP} + \epsilon_{\text{train}} \leq \nu_0 + \Delta + \delta_{FP} + \epsilon_{\text{train}}\)
   - Sequence \(\{\Gen_{\M_t}\}\) is monotonically non-decreasing (by construction of self-training)
   - Sequence is bounded above by \(\nu_0 + \epsilon\) where \(\epsilon = \Delta + \delta_{FP} + \epsilon_{\text{train}}\)
   - By monotone convergence theorem, sequence converges to limit \(\gamma_{\infty} \leq \nu_0 + \epsilon\)

**Key challenge**: Proving Lemma 3 (verification improvement is bounded). This requires analyzing how verification capability changes through training.

### **Approach B: Contraction Mapping (Stronger Result if Provable)**

**Advantages**:
- Proves unique fixed point (stronger than just existence)
- Provides convergence rate (geometric)
- More elegant mathematical structure

**Proof outline**:
1. Define metric on model space: \(d(\M, \M') = \sup_{x \sim \D} |\Gen_{\M}(x) - \Gen_{\M'}(x)|\)
2. Show \(d(\T(\M), \T(\M')) \leq \lambda d(\M, \M')\) for some \(\lambda < 1\)
3. Apply Banach fixed-point theorem: unique fixed point \(\M^*\) with \(\Gen_{\M^*} \leq \nu_0 + \epsilon\)
4. Convergence rate: \(d(\M_t, \M^*) \leq \lambda^t d(\M_0, \M^*)\)

**Key challenge**: Proving contraction property. Self-training may not be globally contracting. Alternative:
- Use [converse Banach theorem](https://arxiv.org/abs/1702.07339): If we prove convergence to unique fixed point by other means, there exists metric making \(\T\) a contraction
- Or apply contraction in restricted domain (e.g., models with capability below \(\nu_0 + \epsilon\))

### **Approach C: Information-Theoretic (For Theorem 3 on GV-Gap)**

**Use case**: Proving how gap \(g_{\D}\) determines function \(f(g_{\D})\) in ceiling theorem

**Proof outline**:
1. Quantify information available from verification: \(I(\Ver_{\M}; \text{Quality}) = H(\text{Quality}) - H(\text{Quality} | \Ver_{\M})\)
2. When gap is large, verification errors increase: \(H(\text{Quality} | \Ver_{\M})\) increases
3. Mutual information decreases: \(I(\Ver_{\M}; \text{Quality}) \leq h(g_{\D})\) where \(h\) is decreasing
4. Learning bounded by information: \(\gamma_{\max} - \gamma_0 \leq C \cdot I(\Ver_{\M}; \text{Quality})\) for some constant \(C\)
5. Conclude: \(\gamma_{\max} \leq \nu_0 + f(g_{\D})\) where \(f(g_{\D}) = C \cdot h(g_{\D})\)

**Key challenge**: Making information-theoretic argument rigorous for our setting. Need to formalize "Quality" as random variable and compute entropy/mutual information.

## Existing Results to Build On

### 1. Self-Training Convergence Guarantees (2024-2025)

**Reciprocal Learning** ([Shen & Sanghavi, Aug 2024](https://arxiv.org/html/2408.06257)):
- Proves self-training converges at **linear rates** to approximately optimal model
- Uses **Banach fixed-point theorem** when predictions are probabilistic and sample adaptation is Lipschitz
- Key condition: Sample adaptation must be **non-greedy**, **randomized or regularized**
- Result: \(\text{error}(t) \leq \lambda^t \text{error}(0)\) for some \(\lambda < 1\)

**Relevance**: Our self-training operator may satisfy similar conditions. If we show filtered sampling is Lipschitz and non-greedy, can adapt their proof.

**Theoretical Analysis of Self-Training with Deep Networks** ([Wei et al., ICLR 2021](https://openreview.net/forum?id=rC8sJ4i6kaH)):
- Proves minimizers of self-training objectives achieve high accuracy under "expansion" assumption
- Expansion: Low-probability subset expands to large-probability neighborhood
- Sample complexity: Polynomial in margin and Lipschitzness
- Key lemma: Self-training error bounded by \(O(\epsilon_{\text{init}} + \text{complexity} / n)\)

**Relevance**: Provides finite-sample guarantees we can invoke. Our bounded verification capability corresponds to their complexity term.

**Improving Self-Training Under Distribution Shifts** ([NeurIPS 2024](https://proceedings.neurips.cc//paper_files/paper/2024/hash/1b99db17b54735d22dbed15c24f2dbdc-Abstract-Conference.html)):
- Analyzes self-training when test distribution differs from training
- Proposes temporal consistency ensemble to improve robustness
- Shows self-training can fail catastrophically under distribution shift

**Relevance**: Suggests we need to assume i.i.d. or bounded distribution shift for convergence guarantees.

### 2. Policy Iteration Convergence (RL Literature)

**Bellman Operator Convergence** ([Lecture notes](https://www.tuananhle.co.uk/notes/bellman-convergence.html)):
- Bellman operator \(T\) is contraction: \(\|TV - TU\|_{\infty} \leq \gamma \|V - U\|_{\infty}\)
- Iterating \(T\) converges to unique fixed point \(V^*\) (optimal value function)
- Convergence rate: Geometric at rate \(\gamma\)

**Relevance**: Self-training operator may not be contraction, but similar structure. We can try to find appropriate metric making it a contraction.

**Policy Improvement Theorem** ([Lecture notes](https://yuanz.web.illinois.edu/teaching/IE498fa19/lec_16.pdf)):
- If \(Q^{\pi}(s, \pi') \geq V^{\pi}(s)\) for all \(s\), then \(V^{\pi'} \geq V^{\pi}\)
- Guarantees monotonic improvement of value function
- Convergence to optimality when no further improvement possible

**Relevance**: Directly applicable! Self-training improves by filtering to higher-quality data. Monotonic improvement structure is analogous.

### 3. Generalization Bounds for Noisy Iterative Algorithms

**Information-Theoretic Generalization Bounds** ([Xu & Raginsky, ISIT 2017](https://ieeexplore.ieee.org/document/8437571/)):
- Generalization error bounded by mutual information \(I(\text{Algorithm}; \text{Data})\)
- For iterative algorithms with bounded noisy updates: \(\text{gen\_error} \leq O(\sqrt{I / n})\)
- Markovian structure allows composition of bounds across iterations

**Relevance**: Can bound how much capability improves per iteration based on information in filtered data.

**Error Propagation in Iterative Processes** ([Li et al., 2025](https://arxiv.org/html/2508.12094v3)):
- Derives per-step error propagation equations for iterative algorithms
- Shows errors accumulate geometrically if per-step error \(> 0\)
- Provides bounds on total accumulated error

**Relevance**: Verification errors at each iteration propagate to final capability. Can bound cumulative effect.

## Open Questions for Theorist

1. **Contraction vs Monotone Convergence**: Can we prove self-training operator is a contraction, or should we use weaker monotone convergence?

2. **Verification Improvement Bound (Lemma 3)**: How to rigorously bound \(\Delta\) such that \(\nu_t \leq \nu_0 + \Delta\)?
   - Option 1: Assume bounded model capacity
   - Option 2: Prove verification cannot improve beyond certain threshold without external supervision
   - Option 3: Characterize as function of task distribution properties

3. **False Positive Rate \(\delta_{FP}\)**: How to characterize \(\delta_{FP}\) as function of verification capability and task difficulty?
   - Use ROC analysis: \(\delta_{FP}\) decreases as verification capability increases
   - Connect to GV-gap: Larger gap → higher \(\delta_{FP}\)

4. **Training Error \(\epsilon_{\text{train}}\)**: Should we invoke standard generalization bounds (VC dimension, Rademacher complexity) or derive custom bound for self-training setting?
   - Standard approach: Use PAC learning bounds
   - Custom approach: Account for distribution shift between self-generated data and true distribution

5. **Uniqueness of Fixed Point**: Does self-training have unique fixed point (Banach) or multiple fixed points (Tarski)?
   - Empirical evidence suggests multiple fixed points (reward hacking vs successful improvement)
   - If multiple, how to characterize which fixed point is reached based on \(\M_0\)?

6. **Explicit Form of \(f(g_{\D})\)**: Can we derive closed-form expression for improvement bound as function of GV-gap?
   - Information-theoretic approach: \(f(g_{\D}) = C / (1 + g_{\D})\) or \(f(g_{\D}) = C \exp(-\alpha g_{\D})\)
   - Empirical approach: Fit to experimental data (see Note 02 on GV-gap)

## Connection to Existing Literature Surveys

This proof strategy builds on:
- **Note 01 (Fixed-Point Characterization)**: Applies Banach/Tarski/Nash frameworks to characterize convergence
- **Note 02 (GV-Gap Characterization)**: Uses gap to bound improvement via information bottleneck

Key integration:
- **Theorem 1 (Self-Training Bound)**: Use monotone convergence + bounded verification (this note)
- **Theorem 2 (Self-Refinement Bound)**: Similar proof structure, but refinement instead of filtering
- **Theorem 3 (GV-Gap Determines Ceiling)**: Use information-theoretic argument (Note 02 insights)
- **Theorem 4 (Self-Play Separation)**: Use game-theoretic fixed points (Note 01, Nash framework)

## Recommendations for Next Steps

For the Theorist agent working on DW-60:

1. **Immediate priority**: Prove Lemma 1 (filtered data quality bound) rigorously
   - Formalize probabilistic argument over verification judgments
   - Bound false positive rate as function of verification capability
   - This is the foundation for all other results

2. **Short-term**: Complete monotone convergence proof (Approach A)
   - Prove Lemmas 1-3
   - Apply monotone convergence theorem
   - This establishes Theorem 1 with existence of bounded fixed point

3. **Medium-term**: Attempt contraction proof (Approach B)
   - Check if self-training satisfies Lipschitz conditions
   - If yes, prove contraction property and upgrade to unique fixed point
   - If no, use converse Banach theorem to characterize metric

4. **Long-term**: Information-theoretic characterization (Approach C)
   - Derive explicit \(f(g_{\D})\) for Theorem 3
   - Connect to empirical findings in Note 02
   - This completes the theoretical framework

## Key References

### Contraction Mapping and Fixed-Point Theory
- [Banach Fixed-Point Theorem - Wikipedia](https://en.wikipedia.org/wiki/Banach_fixed-point_theorem)
- [The Banach Fixed Point Theorem: selected topics](https://link.springer.com/article/10.1007/s13398-024-01636-6) (Springer, 2024)
- [Banach fixed point theorem for fractional integral contraction](https://link.springer.com/article/10.1186/s13663-025-00819-z) (2025)
- [A Converse to Banach's Fixed Point Theorem and its CLS Completeness](https://arxiv.org/abs/1702.07339)
- [Monotone Convergence Theorem - Wikipedia](https://en.wikipedia.org/wiki/Monotone_convergence_theorem)

### Reinforcement Learning Convergence Proofs
- [Proof of Convergence of the Bellman Operator](https://www.tuananhle.co.uk/notes/bellman-convergence.html)
- [Lecture 16: Value Iteration, Policy Iteration](https://yuanz.web.illinois.edu/teaching/IE498fa19/lec_16.pdf) (UIUC)
- [Bellman Operators are Contractions](https://cfml.se/bellman-operators-are-contractions/)
- [Convergence Properties of Policy Iteration](https://editorialexpress.com/jrust/research/siam_dp_paper.pdf)
- [Bellman operator convergence enhancements in RL](https://arxiv.org/html/2505.14564) (2025)

### Self-Training Convergence Theory
- [Reciprocal Learning](https://arxiv.org/html/2408.06257) (Aug 2024) - Proves linear convergence via Banach theorem
- [Theoretical Analysis of Self-Training with Deep Networks](https://openreview.net/forum?id=rC8sJ4i6kaH) (ICLR 2021)
- [Improving self-training under distribution shifts](https://proceedings.neurips.cc//paper_files/paper/2024/hash/1b99db17b54735d22dbed15c24f2dbdc-Abstract-Conference.html) (NeurIPS 2024)
- [Self-Training: A Survey](https://arxiv.org/pdf/2202.12040) (2022)

### Lipschitz Continuity and Neural Networks
- [Regularisation of neural networks by enforcing Lipschitz continuity](https://link.springer.com/article/10.1007/s10994-020-05929-w) (2020)
- [Efficiently Computing Local Lipschitz Constants](https://arxiv.org/abs/2210.07394) (2022)
- [A Dynamical System Perspective for Lipschitz Neural Networks](https://proceedings.mlr.press/v162/meunier22a/meunier22a.pdf) (ICML 2022)
- [Contraction Theory for Optimization, Control, and Neural Networks](https://arxiv.org/html/2404.11707v1) (2024)

### Information-Theoretic Bounds
- [Anatomize Deep Learning with Information Theory](https://lilianweng.github.io/posts/2017-09-28-information-bottleneck/) (Lilian Weng)
- [How Does Information Bottleneck Help Deep Learning?](https://proceedings.mlr.press/v202/kawaguchi23a/kawaguchi23a.pdf) (ICML 2023)
- [Information Bottleneck: Theory and Applications](https://pmc.ncbi.nlm.nih.gov/articles/PMC7764901/) (2020)

### Error Propagation and Data Quality
- [Error Propagation Mechanisms in Quantized Diffusion Models](https://arxiv.org/html/2508.12094v3) (2025)
- [Generalization Error Bounds for Noisy, Iterative Algorithms](https://ieeexplore.ieee.org/document/8437571/) (ISIT 2017)
- [Accounting for Training Data Error in ML](https://www.mdpi.com/2072-4292/12/6/1034) (2020)
- [Understanding the Gain from Data Filtering](https://arxiv.org/html/2512.14230) (2024)
- [Learning with Bad Training Data via Iterative Trimmed Loss](http://proceedings.mlr.press/v97/shen19e/shen19e.pdf) (ICML 2019)

### Monotone Operators and Neural Networks
- [Non-Euclidean Monotone Operator Theory](https://arxiv.org/html/2303.11273) (2023)
- [Learning Monotone Dynamics by Neural Networks](https://cpsl.pratt.duke.edu/sites/cpsl.pratt.duke.edu/files/docs/wang_acc22.pdf) (ACC 2022)
- [Neural Operator: Learning Maps Between Function Spaces](https://www.jmlr.org/papers/volume24/21-1524/21-1524.pdf) (JMLR 2023)

## Summary

The proof of self-training convergence bound is **tractable** using established techniques from fixed-point theory, reinforcement learning, and learning theory. The recommended approach is:

1. **Prove bounded convergence using monotone convergence theorem** (most robust, requires minimal assumptions)
2. **Attempt to strengthen to contraction proof** if Lipschitz conditions can be established (yields uniqueness)
3. **Use information-theoretic argument for GV-gap characterization** (explains why large gap limits improvement)

The key technical challenges are:
- Bounding verification capability improvement (\(\Delta\))
- Characterizing false positive rate (\(\delta_{FP}\))
- Establishing training error bound (\(\epsilon_{\text{train}}\))

Recent 2024-2025 work on reciprocal learning and self-training provides direct precedents showing similar convergence results are provable using Banach fixed-point theorem under suitable conditions.

The Theorist should start with the monotone convergence proof to establish existence of bounded fixed point, then work toward strengthening the result with contraction property or information-theoretic characterization of the bound.
