# HTN Planning Verification Complexity: Literature Survey

**Date**: 2026-03-22
**Scope**: Comprehensive survey of computational complexity results for HTN (Hierarchical Task Network) plan verification, with focus on the generation-verification gap for planning tasks.

---

## Executive Summary

HTN plan verification complexity has been extensively studied from 2015-2025. The key finding relevant to Theorem 3 (Gap Collapse for Planning) is that verification complexity varies dramatically based on:

1. **Representation** (grounded vs lifted)
2. **Verification question** (feasibility vs optimality vs valid decomposition)
3. **Structural restrictions** (total order, recursion depth, etc.)

**Critical Issue Identified**: The paper draft cites "Behnke, Höller & Biundo, 2024" claiming coNP-completeness for HTN plan verification. However, literature search reveals the actual paper is Behnke, Höller & Biundo (2015, ICAPS) which proves **NP-completeness**, not coNP-completeness. This requires urgent clarification from the Theorist agent.

---

## Key Papers

| Paper | Year | Venue | Main Result | Relevance |
|-------|------|-------|-------------|-----------|
| Behnke, Höller & Biundo | 2015 | ICAPS | HTN plan verification is NP-complete for grounded problems | Foundational complexity result |
| Erol, Hendler & Nau | 1996 | AMAI | HTN plan existence is PSPACE-complete | Generation complexity |
| Lin et al. | 2024 | Uni Ulm Tech Report | Grounded k-length plan existence NP-complete; lifted version PSPACE-hard | Grounded vs lifted distinction |
| Lauer, Lin & Bercher | 2025 | ICAPS | Tight bounds for lifted HTN verification; PSPACE-complete for lifted case | Recent tight bounds |
| Kambhampati et al. | 2024 | ICML | LLMs cannot self-verify plans empirically | Empirical validation of impossibility |
| Stechly, Valmeekam & Kambhampati | 2024 | arXiv 2402.08115 | Self-critique fails on planning; external verification needed | Self-verification limitations |

---

## Detailed Findings

### 1. Grounded HTN Plan Verification: NP-Complete

**Source**: Behnke, G., Höller, D., & Biundo, S. (2015). "On the Complexity of HTN Plan Verification and Its Implications for Plan Recognition." *Proceedings of the International Conference on Automated Planning and Scheduling*, 25(1), 25-33.

**Main result**: Verifying whether a given plan (sequence of actions) is a solution to an HTN planning problem is **NP-complete**, even for very simple HTN planning problems.

**Restrictions tested**: The result holds even with:
- No preconditions and effects
- No ordering in methods
- No recursion in decomposition hierarchy
- Restrictions on decomposition depth

**Why NP-complete**:
- **Upper bound (in NP)**: A certificate is a decomposition tree showing how the plan derives from the initial task network. Checking validity of the tree is polynomial-time.
- **Lower bound (NP-hard)**: Reduction from 3-SAT.

**Key insight**: The hardness comes from the existential question: "Does there exist a valid decomposition tree for this action sequence?"

### 2. Lifted HTN Plan Verification: PSPACE-Complete

**Source**: Lauer, P., Lin, S., & Bercher, P. (2025). "Tight Bounds for Lifted HTN Plan Verification and Bounded Plan Existence." *Proceedings of the International Conference on Automated Planning and Scheduling*, 35(1), 64-73.

**Main result**: For lifted (non-grounded) HTN planning with variables and quantifiers, verification is **PSPACE-complete**.

**Implication**: Operating on lifted representations is fundamentally harder than grounded representations. However, for specific structural restrictions, more efficient algorithms exist.

### 3. Classical STRIPS Plan Verification: PTIME

**Source**: Well-known folklore result, confirmed in multiple planning textbooks.

**Result**: For classical STRIPS planning with grounded operators, plan verification is **polynomial-time**.

**Algorithm**:
1. Initialize state s₀
2. For each action aᵢ: check preconditions, apply effects to get sᵢ
3. Check goal satisfaction in final state

**Complexity**: O(k · |state|) where k is plan length.

**Key distinction**: STRIPS verification is easy because there's no hidden existential quantifier. You just simulate the plan forward.

### 4. HTN Plan Generation: PSPACE-Complete

**Source**: Erol, K., Hendler, J., & Nau, D. (1996). "Complexity results for HTN planning." *Annals of Mathematics and Artificial Intelligence*, 18:69-93.

**Result**: HTN plan existence (finding whether any plan exists) is **PSPACE-complete** via reduction from TQBF.

**Implication for GV-Gap**:
- Generation: PSPACE-complete
- Verification (grounded): NP-complete
- Gap: PSPACE vs NP (assuming hierarchy separations)

---

## The NP vs coNP Question

### Issue

Our paper's Theorem 3 (line 297) claims: "VC(F_HTN) ∈ coNP-hard for plan verification (Behnke, Höller & Biundo, 2024)."

However, the actual Behnke et al. paper is from **2015** (not 2024) and proves **NP-completeness** (not coNP-completeness).

### Possible Interpretations

1. **Citation error**: The year and complexity class are both wrong. Should be "Behnke et al. 2015, NP-complete."

2. **Different problem**: Perhaps there's a coNP-complete variant of the problem:
   - **NP-complete**: "Does there exist a valid decomposition tree?" (existential)
   - **coNP-complete**: "Is this the unique/optimal decomposition?" (universal)
   - **coNP-complete**: "Does there NOT exist any valid decomposition?" (complement)

3. **Unpublished result**: There may be a 2024 paper not yet indexed that proves a coNP-completeness result.

4. **Plan optimality verification**: Perhaps the coNP-hardness refers to verifying that a plan is *optimal*, not just *valid*:
   - Valid plan: NP-complete (Behnke 2015)
   - Optimal plan: coNP-complete (?) - checking "no better plan exists"

### Resolution Needed

**Action for Theorist**: Clarify the exact verification problem being referenced:
- Is it plan validity (NP-complete per Behnke 2015)?
- Is it plan optimality (coNP-complete - citation needed)?
- Is it decomposition uniqueness (complexity class unknown)?

**Recommendation**: If no coNP-complete result exists in the literature, the theorem can still hold with NP-complete verification. The key claim is that verification is *not* polynomial-time, which is true whether it's NP-complete or coNP-complete. However, the citation must be corrected.

---

## Empirical Validation: LLMs Cannot Self-Verify Plans

### Source 1: Kambhampati et al. (ICML 2024)

**Full citation**: Kambhampati, S., Valmeekam, K., Guan, L., Verma, M., Stechly, K., Bhambri, S., Saldyt, L., & Murthy, A. (2024). "Position: LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks." *Proceedings of the 41st International Conference on Machine Learning (ICML)*, 235, 22895-22907.

**Main claim**: "Auto-regressive LLMs cannot, by themselves, do planning or self-verification (which is after all a form of reasoning)."

**Empirical findings**:
- LLMs fail at both plan generation and plan verification
- Self-verification does not improve planning performance
- External model-based verifiers are necessary

**Implication**: Even though plan verification is theoretically "easier" than generation (NP vs PSPACE), LLMs cannot exploit this gap because verification still exceeds their computational capabilities.

### Source 2: Stechly, Valmeekam & Kambhampati (2024)

**Full citation**: Stechly, K., Valmeekam, K., & Kambhampati, S. (2024). "On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks." *arXiv:2402.08115 [cs.AI]*.

**Venue**: arXiv preprint (likely submitted to venue - check for publication status)

**Experimental domains**:
- Game of 24
- Graph Coloring
- STRIPS planning

**Key findings**:
1. **Self-critique fails**: "Significant performance collapse with self-critique" - GPT-4 cannot identify its own errors.
2. **External verification works**: When a correct external reasoner validates solutions, performance improves substantially.
3. **Simplicity matters**: "Merely re-prompting with a sound verifier maintains most of the benefits" - complex setups add little value.

**Theoretical insight**: "The findings challenge the widespread assumption that verification should be easier than generation for LLMs, suggesting this computational complexity principle doesn't apply when models rely on approximate retrieval rather than formal reasoning."

**Connection to our framework**: This validates Theorem 2 (Self-Consistency Condition) and Theorem 3 (Gap Collapse). When VC(F) ∉ cap(M), self-verification fails because the model lacks the computational capacity to check its own work.

---

## Structural Complexity Analysis (2024-2025)

### Source: Structural Complexity of HTN Planning

**Citations found**:
- arXiv:2401.14174 (2024)
- IJCAI 2025 proceedings

**Key results**:
- Plan Verification is **fixed-parameter tractable** on primitive task networks parameterized by vertex cover number (vcn)
- Generalized partial order width is a stable tractability measure for PLAN VERIFICATION
- Polynomial algorithms exist for restricted classes (constant width, total order, etc.)

**Implication**: While worst-case complexity is NP-complete, average-case or structurally restricted instances may be easier. This could explain why LLMs show *some* planning capability on simple, well-structured tasks but fail on complex hierarchical plans.

---

## Verification Complexity Hierarchy

Based on the literature, the planning verification complexity hierarchy is:

| Planning Formalism | Generation Complexity | Verification Complexity | GV-Gap |
|--------------------|----------------------|------------------------|--------|
| Classical STRIPS (grounded) | NP-complete | **PTIME** | Large (NP vs P) |
| HTN (grounded) | PSPACE-complete | **NP-complete** | Medium (PSPACE vs NP) |
| HTN (lifted) | EXPTIME-complete | **PSPACE-complete** | Small (EXPTIME vs PSPACE) |

**Key insight**: As planning formalisms become more expressive (STRIPS → grounded HTN → lifted HTN), verification complexity increases:
- STRIPS: P (just simulate)
- Grounded HTN: NP-complete (search for decomposition tree)
- Lifted HTN: PSPACE-complete (handle quantifiers and variables)

**Implication for Theorem 3**: The gap collapse is *relative to polynomial-time verifiers*. For grounded HTN:
- Verification is NP-complete
- No polynomial-time verifier exists (assuming P ≠ NP)
- Therefore, reward models (polynomial-time function approximators) cannot learn correct verification
- Self-consistency fails because errors are correlated (shared NP-hard verification bottleneck)

---

## Implications for the Paper

### 1. Citation Correction Required

**Current (incorrect)**: "Behnke, Höller & Biundo, 2024, coNP-hard"
**Should be**: "Behnke, Höller & Biundo, 2015, NP-complete"

**Alternative**: If the coNP-hardness claim is essential, find or prove a result about plan *optimality* verification (not just validity).

### 2. Theorem 3 Still Holds

Even with NP-completeness (not coNP-completeness), the key claim remains valid:

**Theorem 3 (corrected version)**: For grounded HTN planning, VC(F_HTN) is **NP-complete** (Behnke et al. 2015). Therefore:
- No polynomial-time verifier exists (assuming P ≠ NP)
- Reward models cannot learn verification in the worst case
- Self-consistency fails due to correlated errors from shared verification bottleneck
- The GV-Gap collapses *relative to polynomial-time verifiers*

### 3. Empirical Validation is Strong

The Kambhampati et al. (2024) and Stechly et al. (2024) papers provide compelling empirical evidence that:
- LLMs cannot self-verify plans
- External verification is necessary
- Self-critique produces "performance collapse"

This validates the theoretical prediction from Theorem 3.

### 4. Related Work Section Should Include

Add these citations:
- Behnke et al. (2015) - corrected from 2024
- Erol et al. (1996) - for generation complexity
- Kambhampati et al. (2024) ICML - LLMs can't plan
- Stechly et al. (2024) arXiv - self-verification limitations
- Lauer et al. (2025) ICAPS - lifted HTN tight bounds
- Lin et al. (2024) - grounded vs lifted complexity

---

## Open Questions

1. **Is there a coNP-complete result for HTN verification?** If so, what is the exact problem formulation?

2. **Average-case complexity**: Behnke et al. show NP-completeness for severely restricted cases. What about typical instances from planning benchmarks? Are they easier?

3. **Plan optimality verification**: Is verifying that a plan is *optimal* (not just valid) coNP-complete for HTN? This would strengthen Theorem 3.

4. **Interactive verification**: Can debate protocols (IP = PSPACE) verify HTN plans with polynomial-time judges? This would connect to the scalable oversight section.

5. **Verification for PlanBench**: What is the actual verification complexity for the HTN instances in PlanBench? Are they grounded or lifted? Do they require decomposition tree verification?

---

## Recommendations for Next Steps

### For Theorist Agent
1. **Verify the coNP claim**: Check if there's a legitimate coNP-completeness result for some variant of HTN verification (optimality, uniqueness, etc.)
2. **Correct citations**: Update bibliography with correct years and complexity classes
3. **Strengthen Theorem 3**: Consider proving a sharper result distinguishing:
   - STRIPS (P verification) → GV-gap holds
   - HTN (NP-complete verification) → GV-gap collapses relative to P-time verifiers

### For Experimenter Agent
1. **Characterize PlanBench instances**: What verification complexity do the actual benchmark instances have?
2. **Test verification difficulty**: Can LLMs verify plans better than they can generate them on HTN tasks?
3. **Measure correlation**: Test whether errors are correlated on PlanBench-HTN (predicted by Theorem 2)

### For Writer Agent
1. **Update bibliography**: Add Kambhampati 2024, Stechly 2024, correct Behnke citation
2. **Clarify Theorem 3 statement**: Be precise about which verification problem is NP-complete vs coNP-complete
3. **Add empirical validation citations**: The Kambhampati and Stechly papers provide strong empirical support

---

## Sources

- [On the Complexity of HTN Plan Verification (ICAPS 2015)](https://ojs.aaai.org/index.php/ICAPS/article/view/13728)
- [Tight Bounds for Lifted HTN Plan Verification (ICAPS 2025)](https://ojs.aaai.org/index.php/ICAPS/article/view/36102)
- [LLMs Can't Plan (ICML 2024)](https://arxiv.org/abs/2402.01817)
- [Self-Verification Limitations (arXiv 2024)](https://arxiv.org/abs/2402.08115)
- [Structural Complexity Analysis (arXiv 2024)](https://arxiv.org/abs/2401.14174)
- [HTN Plan Verification Complexity (Uni Ulm 2024)](https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.090/Publikationen/2024/Lin2024PlanVerificationComplexity.pdf)

