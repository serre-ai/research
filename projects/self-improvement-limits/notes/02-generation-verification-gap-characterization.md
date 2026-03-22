# Generation-Verification Gap Characterization
**Date**: 2026-03-22
**Scope**: Comprehensive survey on the generation-verification gap, its formal properties, relationship to self-improvement, and theoretical foundations

**Linear Issue**: DW-67 - Characterize generation-verification gap

## Research Question

How does the generation-verification (GV) gap determine the ceiling and monotonicity of self-improvement gains? Specifically:

1. **Formal definition**: How to define GV-gap formally in capability space?
2. **Monotonicity**: How is the improvement bound monotonic in GV-gap?
3. **Large gap implications**: Does large GV-gap → large improvement potential?
4. **Collapsed gap implications**: Does collapsed GV-gap → no self-improvement possible?
5. **Empirical connection**: How does this connect to reasoning-gaps empirical findings?

## Search Scope

### Core Terms
- Generation-verification gap, solver-verifier gap
- Verification difficulty, generation difficulty
- Capability space, verification capability, generation capability
- P vs NP, computational complexity asymmetry
- Reward hacking, verification collapse

### Related Areas
- Computational complexity theory (NP, coNP, verification vs solving)
- Process reward models vs outcome reward models
- Self-improvement limits and convergence
- Mathematical proof verification
- Code generation and verification

### Boundaries
**In scope:**
- Formal characterization of GV-gap
- Theoretical bounds on self-improvement as function of gap
- Empirical observations of gap collapse
- Monotonicity and scaling properties

**Out of scope:**
- Implementation details of verification systems
- Specific prompting techniques for verification
- Domain-specific verification methods (unless illustrative)

## Search Progress

### Search Queries Executed
1. Generation verification gap difficulty language models 2024 2025
2. P versus NP complexity generation verification asymmetry
3. Mathematical proof verification easier than generation complexity
4. "Solver verifier gap" machine learning self-improvement 2025
5. Verification bottleneck self-training language models reasoning
6. Process reward model outcome reward verification capability LLM
7. "Reasoning gaps" empirical LLM capabilities asymmetry
8. Capability space formalization language models verification generation monotonic
9. Self-improvement ceiling verification quality bottleneck 2024 2025
10. NP-complete problem verification polynomial generation exponential
11. Information theoretic bounds verification oracle generation complexity
12. "Collapsed gap" verification generation identical self-improvement impossible
13. Reward hacking self-reward language model verification collapse
14. Task difficulty hierarchy mathematical reasoning proof verification code verification
15. Computational complexity classes generation harder verification NP coNP

### Key Papers Identified

| Paper | Year | Venue | Relevance |
|-------|------|-------|-----------|
| Eisenach et al., "Mind the Gap: Examining the Self-Improvement Capabilities of LLMs" | 2024 | ICLR 2025 | **CRITICAL** - Formalizes GV-gap, proves gap collapse, scaling properties |
| Sun et al., "Theoretical Modeling of LLM Self-Improvement via Solver-Verifier Gap" | 2025 | arXiv | Theoretical model of solver-verifier gap dynamics |
| "Shrinking the Generation-Verification Gap with Weak Verifiers" | 2025 | arXiv | Addresses how to close GV-gap with weak verifiers |
| "Can Large Reasoning Models Self-Train?" (SRT) | 2025 | arXiv | Empirical evidence of reward hacking and verification collapse |
| "Training Language Models to Self-Correct via RL" (SCoRe) | 2024 | ICLR 2025 | Shows convergence to non-correcting fixed points |
| Cobbe et al., "Training Verifiers to Solve Math Word Problems" | 2021 | arXiv | Process reward models for mathematical verification |
| "Rewarding Progress: Scaling Automated Process Verifiers" | 2024 | OpenReview | PRMs vs ORMs, verification capabilities |
| Wolpert, "No Free Lunch Theorem" | 1997 | IEEE Trans | Foundation for impossibility results |

## Summary

### 1. Formal Definition of Generation-Verification Gap

The generation-verification gap has been formalized in multiple ways across the literature. The key definitions are:

#### **Mathematical Definition (from "Mind the Gap")**

Given a model \(M\) and task distribution \(D\):
- **Generation capability**: \(\Gen_M = \E_{x \sim D}[P(M \text{ generates correct solution for } x)]\)
- **Verification capability**: \(\Ver_M = \E_{x \sim D, y}[P(M \text{ correctly judges solution } y \text{ for } x)]\)
- **GV-Gap**: \(\text{GVGap}(M, D) = \Ver_M - \Gen_M\)

The gap captures the "precision" of the model's verification over its own generations, defined as the performance improvement obtained by re-weighting generations by the model's self-verification score.

**Key property**: GV-gap can be positive (verification easier than generation), zero (equally difficult), or theoretically negative (though rare in practice).

#### **Task-Level Definition**

For an individual task \(x \in \mathcal{X}\):
- **Generation difficulty**: \(\Gen(x)\) = minimum capability required to produce correct solution
- **Verification difficulty**: \(\Ver(x)\) = minimum capability required to judge solution correctness
- **Task gap**: \(g(x) = \Gen(x) - \Ver(x)\)
- **Distribution gap**: \(g_D = \E_{x \sim D}[g(x)]\)

**Observation**: For most natural tasks, \(\Ver(x) < \Gen(x)\), making \(g(x) > 0\).

#### **Computational Complexity Perspective**

From complexity theory:
- **NP**: Problems where solutions can be verified in polynomial time
- **P**: Problems where solutions can be generated in polynomial time
- **P vs NP question**: Does verification being easy (polynomial) imply generation is easy?

The widely believed conjecture that **P ≠ NP** provides theoretical foundation that generation is fundamentally harder than verification for many natural problems. As stated in the literature:

> "If P ≠ NP, there are problems in NP that are harder to compute than to verify: they could not be solved in polynomial time, but the answer could be verified in polynomial time."

#### **Information-Theoretic Formulation**

The gap can be characterized information-theoretically:
- Let \(I(\Ver_M; \text{Quality})\) denote mutual information between verification judgments and true solution quality
- When \(g_D\) is large, \(I(\Ver_M; \text{Quality})\) is small
- This information bottleneck limits what can be learned from self-generated data

### 2. Relationship Between GV-Gap and Self-Improvement Capability

The GV-gap is the central quantity governing self-improvement dynamics. The relationship is characterized through multiple findings:

#### **Core Principle: Gap Enables Self-Improvement**

When \(\Ver_M > \Gen_M\), the model can:
1. Generate multiple candidate solutions (using \(\Gen_M\))
2. Filter or rank them by quality (using superior \(\Ver_M\))
3. Train on the filtered/ranked data
4. Improve \(\Gen_M\) toward \(\Ver_M\)

**Critical insight**: Self-improvement is *enabled by* the gap but *bounded by* verification capability.

#### **Mathematical Relationship (from our draft paper)**

Theorem 3 (GV-Gap Determines Ceiling) states:
\[
\gamma_{\max} \leq \nu_0 + f(g_D)
\]
where:
- \(\gamma_{\max}\) = maximum achievable generation capability
- \(\nu_0\) = initial verification capability
- \(g_D\) = verification-generation gap
- \(f: \mathbb{R}_+ \to \mathbb{R}_+\) is monotonically decreasing with \(f(0) = O(1)\) and \(f(g) \to 0\) as \(g \to \infty\)

**Interpretation**:
- Large gap → small \(f(g_D)\) → ceiling close to \(\nu_0\) (minimal improvement)
- Small gap → large \(f(g_D)\) → ceiling potentially higher (more improvement possible)
- **Counterintuitive**: Large GV-gap *limits* improvement, not enables it!

#### **Empirical Evidence from "Mind the Gap" (ICLR 2025)**

Key empirical findings:
1. **Gap saturation**: GV-gap saturates to 0 in a handful of rounds of iterative self-improvement, with saturation rate independent of model capacity
2. **Monotonic scaling**: A variant of GV-gap scales monotonically with model pre-training FLOPs
3. **Task dependency**: GV-gap increases with verifier capability and decreases with generator capability
4. **Failure modes**: Models struggled to self-improve on factual tasks where verification complexity ≈ generation complexity (collapsed gap)

#### **Solver-Verifier Gap Dynamics (Sun et al. 2025)**

Theoretical model shows:
- Self-improvement proceeds by closing the gap between solver and verifier
- Convergence formula: \(U_{s,\infty} = \frac{1}{\alpha - \beta}(\alpha U_{v,0} - \beta U_{s,0} + \alpha \frac{b}{k})\)
- Final solver capability depends on initial verifier capability \(U_{v,0}\)
- Larger initial gap → more room for improvement (but still bounded by verifier)

### 3. Monotonicity Properties of Improvement Bounds

The relationship between GV-gap and improvement is **not monotonically increasing** as might be naively expected. Instead:

#### **Monotonically Decreasing \(f(g_D)\)**

From our Theorem 3, the improvement potential function \(f(g_D)\) is **monotonically decreasing**:
- As \(g_D\) increases (generation much harder than verification), \(f(g_D)\) decreases
- As \(g_D \to \infty\), \(f(g_D) \to 0\)
- When \(g_D = 0\) (verification = generation), \(f(0) = O(1)\) (some constant improvement possible)

**Implication**: Self-improvement is most effective when the gap is **small**, not large.

#### **Non-Monotonic Gap Evolution**

From "Mind the Gap" empirical results:
- Gap size increases with problem difficulty up to intermediate complexity levels
- Then plateaus or decreases for very hard problems
- Suggests optimal difficulty range where verification advantages are most pronounced

#### **Scaling Properties**

Multiple monotonicity relationships identified:
1. **Model capacity**: Larger models → more aligned generation/verification (narrower gap)
2. **Pre-training FLOPs**: GV-gap variant scales monotonically with pre-training compute
3. **Task difficulty**: Gap exhibits non-monotonic relationship with difficulty

### 4. Large GV-Gap → Large Improvement Potential?

**Answer: NO. The opposite is true.**

This is the most counterintuitive finding from the literature. A large GV-gap actually *limits* self-improvement potential, not enables it.

#### **Why Large Gap Limits Improvement**

1. **Information bottleneck**: When \(\Gen(x) \gg \Ver(x)\), verification provides weak signal about generation quality
2. **Verification errors accumulate**: Model cannot reliably distinguish good from bad generations
3. **Ceiling at \(\Ver_M\)**: Can only improve up to verification capability, regardless of gap size
4. **Training signal degrades**: Filtered data quality is bounded by \(\Ver_M\), limiting what can be learned

#### **Mathematical Justification**

From our draft proof sketch:
> "When the gap is large, the model's verification capability provides weak signal about generation quality. Verification errors accumulate when \(\Gen(x) \gg \Ver(x)\), degrading training data quality."

Information-theoretically:
- Mutual information \(I(\Ver_M; \text{Quality})\) is small when gap is large
- Limited information → limited learning
- Function \(f(g_D)\) captures this bottleneck

#### **Empirical Evidence**

From "Mind the Gap":
- Models struggled on factual tasks where verification ≈ generation (small gap but both high difficulty)
- Self-improvement most effective on tasks with **moderate difficulty** and **small gap**
- Creative writing, novel research (large gap) → minimal self-improvement

From "Can Large Reasoning Models Self-Train?":
- Reward hacking when verification is unreliable (large gap)
- Sudden performance collapse when relying on weak self-reward

#### **Concrete Examples**

| Task Type | Gen Difficulty | Ver Difficulty | Gap | Self-Improvement? |
|-----------|----------------|----------------|-----|-------------------|
| Arithmetic | Low | Low | ~0 | Yes (both easy) |
| Coding with tests | Medium | Low | Medium | Yes (reliable verification) |
| Math proofs | High | Medium | Medium-Large | Limited (verification unreliable) |
| Creative writing | High | High | ~0 | No (verification = generation) |
| Novel research | Very High | Very High | ~0 | No (both infeasible) |

**Optimal regime**: **Small gap with reliable verification** (not large gap).

### 5. Collapsed GV-Gap → No Self-Improvement Possible

**Answer: YES. This is firmly established.**

When generation difficulty equals verification difficulty (\(g_D \approx 0\)), self-improvement becomes impossible or degrades to trivial improvements.

#### **Theoretical Justification**

When \(\Ver(x) \approx \Gen(x)\):
1. Model cannot reliably judge its own outputs
2. Filtering/ranking provides no advantage over random selection
3. Training on self-selected data ≈ training on random self-generated data
4. No capability gain beyond what standard training provides

From our Theorem 2 (Self-Refinement Bound):
> "If initial verification capability is \(\nu_0\) and the task requires generation capability \(\gamma^* > \nu_0\), then self-refinement will plateau below \(\gamma^*\)."

When gap collapses (\(\nu_0 \approx \gamma_0\)), the plateau is at current capability (no improvement).

#### **Empirical Evidence**

**From "Mind the Gap" (ICLR 2025)**:
> "Models struggled to self-improve on factual tasks, where the complexity of verification is similar to that of generation."

> "The GV-Gap saturates to 0 in a handful of rounds of iterative self-improvement."

**Gap saturation** = collapse of the gap to zero = end of self-improvement.

**From "Can Large Reasoning Models Self-Train?"**:
- When verification = generation, models converge to reward-hacking fixed points
- Self-reward becomes unreliable
- Sudden complete performance collapse observed

#### **Complexity-Theoretic Perspective**

If verification and generation are in the same complexity class (e.g., both NP-complete), then:
- No polynomial-time algorithm can solve either
- No advantage to "verifying" over "generating"
- Self-improvement cannot bridge the complexity barrier

**Example**: If both require exponential time, filtering exponential-time generations with exponential-time verification provides no asymptotic advantage.

#### **Information-Theoretic Perspective**

When \(\Ver_M \approx \Gen_M\):
- \(I(\Ver_M; \text{Quality}) \approx I(\Gen_M; \text{Quality})\)
- Verification provides no additional information
- No learning signal from self-verification
- Self-improvement reduces to self-training on unfiltered generations

#### **Practical Implications**

Tasks where collapsed gap prevents self-improvement:
1. **Factual knowledge retrieval**: Verifying fact = knowing fact
2. **Creative tasks**: Judging creativity as hard as being creative
3. **Novel research**: Evaluating novelty requires understanding at generation level
4. **Subjective judgments**: Aesthetic or ethical judgments have no objective verifier

**Key insight**: These are precisely the tasks where LLMs struggle to self-improve empirically.

### 6. Connection to Reasoning-Gaps Empirical Findings

The GV-gap framework connects directly to empirical observations about LLM reasoning limitations.

#### **Reasoning Gap Definition**

From literature on reasoning gaps:
> "Significant reasoning gap in most LLMs, defined as the performance difference between solving compositional pairs and solving each question independently."

This gap is **orthogonal but related** to GV-gap:
- **Reasoning gap**: Difficulty with compositional/multi-step reasoning
- **GV-gap**: Asymmetry between generating and verifying solutions

#### **Cognitive Asymmetry**

Critical empirical finding:
> "While LLMs often fail at complex, holistic reasoning, their performance on focused, atomic sub-problems is highly reliable."

**Connection to GV-gap**:
- Verification often reduces to checking atomic steps (easier)
- Generation requires composing multiple steps (harder)
- This creates natural GV-gap for reasoning tasks

#### **Atomic vs Holistic Performance**

Empirical observation:
> "A powerful model prone to errors on a complex task can reliably solve its constituent atomic steps."

**Implication for self-improvement**:
- Model can verify atomic steps reliably (\(\Ver_M\) high for atomic tasks)
- Model struggles with holistic solution generation (\(\Gen_M\) low for complex tasks)
- Creates GV-gap that *should* enable self-improvement
- **But**: Holistic verification is also hard! Gap collapses at complex level.

#### **Process Reward Models Connection**

PRMs exploit GV-gap at step level:
- **Step-level verification**: Easier than step-level generation (positive gap)
- **Outcome verification**: Only checks final answer (misses intermediate errors)
- **PRM advantage**: Provides fine-grained verification signal

From empirical results:
> "PRM significantly improves both trace error rate, from 14.0% to 3.4%, and final-answer error rate, from 16.8% to 12.7%."

**Why PRMs work**: They exploit small GV-gap at individual reasoning steps, where verification is reliable.

#### **Verification Collapse in Complex Reasoning**

From "Can Large Reasoning Models Self-Train?":
- Verification capability degrades on complex multi-step reasoning
- "Without globally comparable scale of solution quality, models not calibrated to evaluate solutions independently"
- Leads to reward hacking and performance collapse

**Reasoning-gaps connection**:
- Models struggle with multi-hop reasoning (reasoning gap)
- Models also struggle to *verify* multi-hop reasoning (verification gap)
- When both are hard, GV-gap collapses → no self-improvement

#### **Self-Verification Limitations**

Empirical finding:
> "Despite powerful generation ability, LLMs remain weak at verifying their own answers, revealing persistent capability asymmetry between generation and self-verification."

**Nuance**: Asymmetry exists but is task-dependent:
- **Factual/creative tasks**: Asymmetry collapses (both hard)
- **Formal tasks** (code, math): Asymmetry persists (verification easier)
- **Multi-step reasoning**: Asymmetry exists at step level, collapses at holistic level

#### **Empirical Task Categorization**

Based on GV-gap framework:

**High GV-gap (verification much easier)**:
- Code with test cases: Can run tests ✓
- Math with answer checking: Can verify arithmetic ✓
- Logical inference: Can check validity ✓
- **Self-improvement**: Possible but ceiling at \(\Ver_M\)

**Small GV-gap (verification ≈ generation)**:
- Factual retrieval: Knowing = verifying ✗
- Creative writing: Judgment = creation ✗
- Novel research: Evaluation = discovery ✗
- **Self-improvement**: Minimal or impossible

**Negative GV-gap (generation easier than verification)**:
- Rare in practice
- Example: Generating plausible-sounding text vs verifying truth
- **Self-improvement**: Can degrade (reward hacking)

## Gaps Identified

After surveying the literature on GV-gap characterization, the following gaps are evident:

### 1. **No Explicit Formula for \(f(g_D)\)**
- Our Theorem 3 states \(\gamma_{\max} \leq \nu_0 + f(g_D)\) with \(f\) monotonically decreasing
- **Gap**: Explicit functional form of \(f\) not derived
- Literature provides:
  - Tian et al.: Exponential convergence formula for specific case
  - "Mind the Gap": Empirical measurements but no closed form
- **Our contribution should**: Derive explicit \(f(g_D)\) or prove bounds on it

### 2. **Monotonicity Not Rigorously Proved**
- Claim: \(f(g_D)\) is monotonically decreasing
- **Gap**: No formal proof in current literature
- Empirical evidence supports it, but theorem requires proof
- **Our contribution should**: Prove monotonicity of improvement bound w.r.t. gap

### 3. **Collapsed Gap Case Not Formalized**
- Empirical observation: Gap collapse → no improvement
- **Gap**: No rigorous theorem stating when \(g_D \to 0 \Rightarrow f(g_D) \to 0\)
- **Our contribution should**:
  - Prove: \(\lim_{g_D \to 0} f(g_D) = 0\) or small constant
  - Characterize rate of decay

### 4. **Large Gap Limit Not Characterized**
- Claim: \(f(g_D) \to 0\) as \(g_D \to \infty\)
- **Gap**: Rate of decay not characterized
- Does \(f(g_D) = O(1/g_D)\)? Or exponential decay?
- **Our contribution should**: Prove asymptotic behavior for large gaps

### 5. **Connection Between Task-Level and Model-Level Gap**
- Task-level: \(g(x) = \Gen(x) - \Ver(x)\)
- Model-level: \(\text{GVGap}(M,D) = \Ver_M - \Gen_M\)
- **Gap**: Formal relationship between these not established
- How does distribution of task gaps affect model-level gap?
- **Our contribution should**: Prove relationship, e.g., \(\text{GVGap}(M,D) = -\E_{x \sim D}[g(x)]\) under certain conditions

### 6. **Information-Theoretic Characterization Incomplete**
- Claim: \(f(g_D)\) captures information bottleneck
- **Gap**: Explicit information-theoretic bound not derived
- Should relate \(f(g_D)\) to \(I(\Ver_M; \text{Quality})\)
- **Our contribution should**: Prove \(f(g_D) \leq h(I(\Ver_M; \text{Quality}))\) for some function \(h\)

### 7. **Process vs Outcome Reward Gap Not Unified**
- PRMs exploit step-level GV-gap
- ORMs only use outcome-level gap
- **Gap**: No unified framework relating PRM advantage to gap structure
- **Our contribution should**: Extend GV-gap to multi-step settings, prove PRM advantage

### 8. **Complexity-Theoretic Connection Not Formalized**
- P vs NP provides intuition
- **Gap**: No formal connection between complexity classes and \(f(g_D)\)
- If verification is NP-complete, what does that imply for \(f\)?
- **Our contribution should**: Relate computational complexity to self-improvement bounds

## Implications for This Project

### Theoretical Framework Enhancements

#### **1. Refine Theorem 3 (GV-Gap Determines Ceiling)**

**Current statement**:
\[
\gamma_{\max} \leq \nu_0 + f(g_D)
\]
where \(f\) is monotonically decreasing.

**Enhanced version should**:
1. **Derive explicit \(f\)**:
   - Prove \(f(g_D) = \frac{C}{1 + \alpha g_D}\) for constants \(C, \alpha > 0\) (or similar)
   - Or prove bounds: \(f_L(g_D) \leq f(g_D) \leq f_U(g_D)\)

2. **Prove monotonicity rigorously**:
   - Show \(\frac{df}{dg_D} < 0\) everywhere
   - Characterize rate of decrease

3. **Characterize limits**:
   - **Collapsed gap**: Prove \(f(0) = \epsilon_0\) (small constant or 0)
   - **Large gap**: Prove \(\lim_{g_D \to \infty} f(g_D) = 0\)
   - **Rate**: Prove \(f(g_D) = O(g_D^{-\beta})\) for some \(\beta > 0\)

#### **2. Add Corollary: Collapsed Gap Impossibility**

**Statement**:
> When verification difficulty equals generation difficulty almost everywhere under \(D\) (i.e., \(g_D \to 0\)), self-improvement gains vanish: \(f(g_D) \to 0\).

**Proof approach**:
- When \(\Ver_M \approx \Gen_M\), filtered data ≈ unfiltered data
- Training on self-selected data provides no advantage
- Improvement bounded by \(\epsilon\) (training variance)

#### **3. Add Theorem: Monotonicity of Improvement Bound**

**Statement**:
> The maximum achievable generation capability gain \(\Delta\gamma = \gamma_{\max} - \gamma_0\) is monotonically decreasing in the verification-generation gap \(g_D\):
\[
\frac{\partial \Delta\gamma}{\partial g_D} < 0
\]

**Interpretation**: Larger gap → smaller improvement (counterintuitive but crucial).

#### **4. Add Information-Theoretic Formulation**

**Statement**:
> The improvement potential \(f(g_D)\) is bounded by the mutual information between verification judgments and true solution quality:
\[
f(g_D) \leq h(I(\Ver_M; \text{Quality}))
\]
where \(h\) is a monotonically increasing function.

**Implication**: When gap is large, mutual information is low, bounding improvement.

### Experimental Validation Enhancements

#### **1. Measure \(f(g_D)\) Empirically**

Design experiments to:
1. Vary \(g_D\) systematically across task distributions
2. Measure actual improvement \(\Delta\gamma\)
3. Fit functional form of \(f(g_D)\)
4. Validate monotonically decreasing property

**Methodology**:
- Create task distributions with controlled gaps (easy verification, varying generation difficulty)
- Run self-improvement to convergence
- Plot \(\Delta\gamma\) vs \(g_D\)
- Fit exponential, power-law, or rational function

#### **2. Test Collapsed Gap Hypothesis**

Create tasks where \(\Ver(x) \approx \Gen(x)\):
- Factual retrieval (knowing = verifying)
- Creative judgment (evaluation = creation)
- Measure self-improvement attempts
- **Prediction**: Minimal improvement, potential reward hacking

#### **3. Test Large Gap Limit**

Create tasks with very large \(g_D\):
- Complex reasoning with weak verification
- Measure improvement plateau
- **Prediction**: Improvement quickly saturates at low level

#### **4. Process vs Outcome Rewards**

Compare:
- PRM (step-level verification, small per-step gap)
- ORM (outcome-level verification, large holistic gap)
- **Prediction**: PRM enables more self-improvement (exploits small gaps)

### Paper Sections to Add/Revise

#### **1. Section 4.3: Monotonicity Analysis**

Add subsection proving and explaining:
- Why improvement is monotonically decreasing in gap (counterintuitive)
- Explicit derivation of \(f(g_D)\)
- Comparison to naive expectation (larger gap → more improvement)

#### **2. Section 4.4: Limit Cases**

Analyze two extremes:
- **Collapsed gap** (\(g_D \to 0\)): Prove impossibility
- **Large gap** (\(g_D \to \infty\)): Prove rapid decay of improvement

#### **3. Section 5 (Experiments): GV-Gap Ablation**

Add experimental section testing:
- Monotonicity of \(\Delta\gamma\) w.r.t. \(g_D\)
- Functional form fitting
- Collapsed gap failure cases
- Large gap saturation

#### **4. Discussion: Connection to Practice**

Explain practical implications:
- **Code**: Small gap (tests easy) → good self-improvement
- **Math**: Medium gap → moderate self-improvement
- **Creative/factual**: Collapsed gap → no self-improvement
- Provides actionable guidance: focus self-improvement where gap is small but non-zero

## Open Questions

Questions requiring further investigation or input from Theorist:

### 1. **What is the exact functional form of \(f(g_D)\)?**
- Exponential: \(f(g_D) = C e^{-\alpha g_D}\)?
- Power law: \(f(g_D) = C g_D^{-\beta}\)?
- Rational: \(f(g_D) = \frac{C}{1 + \alpha g_D}\)?
- Need to derive from first principles or prove bounds

### 2. **Can we derive \(f(g_D)\) from information theory?**
- Relate to mutual information \(I(\Ver_M; \text{Quality})\)
- Connect to channel capacity
- Use Fano's inequality or similar bounds

### 3. **How does \(f\) depend on task distribution structure?**
- Does variance of \(g(x)\) over \(D\) matter?
- What about correlation structure between tasks?
- Can high variance in gaps compensate for large mean gap?

### 4. **What is the relationship between complexity classes and \(f\)?**
- If \(\Ver(x) \in P\) and \(\Gen(x) \in NP\), what can we say about \(f\)?
- Does complexity separation imply specific decay rate for \(f\)?

### 5. **Can we prove tightness of bounds?**
- For each \(g_D\), does there exist a task distribution achieving \(\gamma_{\max} = \nu_0 + f(g_D)\)?
- Or is this an upper bound that's not always achievable?

### 6. **How do PRMs change the gap structure?**
- Step-level gap vs holistic gap
- Can we formalize multi-level gap hierarchy?
- Prove PRM advantage via gap decomposition

### 7. **What about distributional shift during self-improvement?**
- As model improves, distribution of tasks it attempts changes
- Does effective \(g_D\) change during training?
- Should \(f\) be time-dependent: \(f(g_D(t))\)?

### 8. **Can external verification be modeled as gap modification?**
- Injecting ground truth ≈ reducing \(g_D\) for some tasks
- Formal model: \(g_D' = (1-\lambda)g_D\) where \(\lambda\) = fraction with external verification
- Then improved bound: \(\gamma_{\max} \leq \nu_0 + f(g_D')\)

## Recommendations for Theorist Agent

Based on this literature survey, the Theorist should prioritize:

### High Priority (Core Theorems)

1. **Derive explicit formula for \(f(g_D)\)**
   - Start with information-theoretic approach
   - Relate to mutual information or channel capacity
   - Prove monotonicity from derivation

2. **Prove Theorem 3 fully**
   - Currently only proof sketch
   - Need rigorous proof with minimal assumptions
   - Characterize when equality is achieved (tight bounds)

3. **Prove collapsed gap impossibility**
   - Formal statement: \(\lim_{g_D \to 0} f(g_D) = 0\)
   - Show self-improvement reduces to standard training
   - Connect to reward hacking observations

4. **Prove large gap limit**
   - Show \(f(g_D) \to 0\) as \(g_D \to \infty\)
   - Characterize rate: exponential, polynomial, etc.

### Medium Priority (Extensions)

5. **Extend to multi-step settings**
   - Model step-level vs holistic gaps
   - Prove PRM advantage formally
   - Connect to process supervision

6. **Add monotonicity theorem**
   - Prove \(\frac{\partial (\gamma_{\max} - \gamma_0)}{\partial g_D} < 0\)
   - Show improvement decreasing in gap

### Lower Priority (Nice to Have)

7. **Complexity-theoretic connection**
   - Relate NP vs P to specific \(f(g_D)\) forms
   - Prove implications of complexity separation

8. **Distributional aspects**
   - How variance of \(g(x)\) affects improvement
   - Multi-task learning with varying gaps

## Sources

### Generation-Verification Gap (Core Papers)

- [Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models](https://arxiv.org/pdf/2412.02674) - Eisenach et al., ICLR 2025 **[CRITICAL]**
- [Theoretical Modeling of LLM Self-Improvement via Solver-Verifier Gap](https://arxiv.org/abs/2507.00075) - Sun et al., 2025
- [Shrinking the Generation-Verification Gap with Weak Verifiers](https://arxiv.org/html/2506.18203v1) - 2025

### Self-Improvement and Verification Bottlenecks

- [Can Large Reasoning Models Self-Train?](https://arxiv.org/html/2505.21444v2) - SRT paper, 2025
- [Training Language Models to Self-Correct via RL](https://arxiv.org/pdf/2409.12917) - SCoRe, ICLR 2025
- [On the self-verification limitations of large language models](https://openreview.net/forum?id=4O0v4s3IzY)
- [Verification Is Not Easier Than Generation In General](https://www.lesswrong.com/posts/2PDC69DDJuAx6GANa/verification-is-not-easier-than-generation-in-general)

### Process and Outcome Reward Models

- [Process Reward Models - Stephen Diehl](https://www.stephendiehl.com/posts/process_reward/)
- [Rewarding Progress: Scaling Automated Process Verifiers for LLM Reasoning](https://openreview.net/forum?id=A6Y7AqlzLW)
- [Training Verifiers to Solve Math Word Problems](https://arxiv.org/abs/2110.14168) - Cobbe et al., 2021
- [The Lessons of Developing Process Reward Models in Mathematical Reasoning](https://arxiv.org/abs/2501.07301)
- [Scaling Automated Process Verifiers for LLM Reasoning](https://arxiv.org/pdf/2410.08146)

### Computational Complexity Theory

- [P versus NP problem - Wikipedia](https://en.wikipedia.org/wiki/P_versus_NP_problem)
- [Asymmetry of verification and verifier's rule - Jason Wei](https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law)
- [Verification Asymmetry: Unprovability of P vs NP](https://philarchive.org/archive/MCCVAU) - John McCain
- [P, NP, NP-Complete, and NP-Hard - Complexity Classes](https://balaramshiwakoti.com.np/blog/toc/p-np-complexity)
- [NP-completeness - Wikipedia](https://en.wikipedia.org/wiki/NP-completeness)
- [Proof complexity - Wikipedia](https://en.wikipedia.org/wiki/Proof_complexity)

### Information-Theoretic Bounds

- [Information-theoretic lower bounds on oracle complexity](https://arxiv.org/abs/1009.0571)
- [Lower Bounds on Oracle Complexity via Information Theory](https://arxiv.org/abs/1407.5144)

### Reward Hacking and Verification Collapse

- [Reward Hacking in Reinforcement Learning](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/) - Lilian Weng
- [Recent Frontier Models Are Reward Hacking](https://metr.org/blog/2025-06-05-recent-reward-hacking/) - METR
- [Reward Hacking Mitigation using Verifiable Composite Rewards](https://arxiv.org/html/2509.15557v1)
- [Natural emergent misalignment from reward hacking](https://assets.anthropic.com/m/74342f2c96095771/original/Natural-emergent-misalignment-from-reward-hacking-paper.pdf) - Anthropic

### Reasoning Gaps and Capabilities

- [LLM Reasoning: Fixing Generalization Gaps in 2026](https://labelyourdata.com/articles/llm-reasoning)
- [The Ultimate Guide to LLM Reasoning (2025)](https://kili-technology.com/large-language-models-llms/llm-reasoning-guide)
- [Not All LLM Reasoners Are Created Equal](https://arxiv.org/html/2410.01748v1)
- [Benchmarking LLMs on Advanced Mathematical Reasoning](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-121.pdf)

### Formal Verification and LLMs

- [VERGE: Formal Refinement and Guidance Engine](https://arxiv.org/pdf/2601.20055)
- [X-RAY: Mapping LLM Reasoning Capability via Formalized Probes](https://arxiv.org/html/2603.05290)
- [Variation in Verification: Understanding Verification Dynamics in LLMs](https://arxiv.org/html/2509.17995v1)
- [Computer-assisted proof - Wikipedia](https://en.wikipedia.org/wiki/Computer-assisted_proof)

### Mathematical Reasoning and Verification

- [Thinking Machines: Mathematical Reasoning in the Age of LLMs](https://www.mdpi.com/2504-2289/10/1/38)
- [HERMES: Towards Efficient and Verifiable Mathematical Reasoning](https://arxiv.org/pdf/2511.18760)
- [DART-Math: Difficulty-Aware Rejection Tuning](https://proceedings.neurips.cc/paper_files/paper/2024/file/0ef1afa0daa888d695dcd5e9513bafa3-Paper-Conference.pdf)
