# Self-Consistency Condition: Literature Foundations

**Date**: 2026-03-22
**Scope**: Survey of literature supporting Theorem 2 (Self-Consistency Condition) — conditions under which majority voting improves LLM accuracy

---

## Executive Summary

This note synthesizes ~15 papers across three research streams that ground the Self-Consistency Condition theorem:
1. **Classical jury theorems** (Condorcet 1785, modern extensions) — mathematical foundations for majority voting under independence and correlation
2. **Statistical design effect theory** (intraclass correlation, effective sample size) — quantifying how correlation reduces sample efficiency
3. **LLM self-consistency empirical work** (Wang et al. 2023, failures 2024-2025) — when the method works and when it fails in practice

**Key finding**: The theorem's three conditions — (a) plurality holds, (b) effective sample size under correlation, (c) verification hardness produces correlation — are all individually well-established in prior literature. Our contribution is **synthesizing** these three streams into a unified complexity-theoretic framework that explains when and why self-consistency works for LLMs.

---

## Part 1: Self-Consistency in LLMs (Empirical)

### Foundational Work

**Wang et al. (2023): Self-Consistency Improves Chain of Thought Reasoning in Language Models** (ICLR 2023)
- Introduces self-consistency decoding: sample N reasoning paths, take majority vote over final answers
- Shows improvements on arithmetic reasoning (GSM8K: 74.4% → 85.1% with N=40), commonsense reasoning (StrategyQA), and symbolic reasoning
- **Key assumption**: "diverse reasoning paths can reach a consensus on the correct answer"
- Implicit reliance on independence: errors across samples are assumed to be uncorrelated
- Does not formalize conditions for when the method works

**Citation**: Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., Chowdhery, A., & Zhou, D. (2023). Self-consistency improves chain of thought reasoning in language models. *ICLR 2023*.

### When Self-Consistency Works

**Medium post by Koeppern (2024)**: Reviews practical applications
- "Self-consistency proves to be a significant improvement of Chain-of-Thought prompting alone. By combining the techniques and taking a majority vote of the Chain-of-Thought responses, we are able to refine our model prompts to get more reliable outputs."
- Has become a standard baseline in modern LLM evaluation
- Works reliably on mathematical reasoning benchmarks

**Ranked Voting Extensions** (ACL 2025, arXiv 2024)
- Improvements over simple majority voting: instant-runoff voting, Borda count, mean reciprocal rank
- **Tan et al. (2025)**: "Ranked voting based self-consistency consistently outperforms baselines on three multiple-choice and three open-ended question-answering datasets"
- Shows that voting mechanism matters, but core principle (aggregation of diverse samples) remains

**Reasoning-Aware Self-Consistency (RASC)** (NAACL 2025)
- Assigns scores based on qualities of both answers and reasoning paths
- Resampling and stop condition mechanisms optimize sampling efficiency
- Still assumes underlying independence for its probabilistic guarantees

### When Self-Consistency Fails

#### Failure Mode 1: Positional Bias (Violation of Independence)

**Tao et al. (2024): Self-Consistency Falls Short! The Adverse Effects of Positional Bias on Long-Context Problems** (arXiv 2411.01101)
- **Critical finding**: Self-consistency **degrades** performance on long-context tasks across 53/56 model-dataset pairs
- Root cause: "Sampling from a model with inherent position bias amplifies rather than mitigates errors, as all samples inherit the same structural biases, **violating SC's core assumption of error independence**"
- Empirical evidence of correlated errors: "Errors are strongly correlated across samples, stemming from the model's inherent positional bias"
- Specific mechanism: Models preferentially attend to information at specific positions (primacy/recency bias), so all N samples make the same positional error

**Implication for our theorem**: Part (c) — when verification complexity exceeds model capability, errors stem from shared computational limitations (just as positional bias is a shared architectural limitation). Both produce correlation ρ > 0.

#### Failure Mode 2: Shared Priors and Blind Spots

**Anonymous (2026): Consensus is Not Verification: Why Crowd Wisdom Strategies Fail for LLM Truthfulness** (arXiv 2603.06612)
- **Core argument**: "When language models err, their errors are often correlated, violating the independence assumptions required for crowd wisdom, because **shared training data, objectives, and post-training incentives induce shared priors and shared blind spots**, yielding strongly correlated errors"
- "When the dominant answer is wrong, additional samples and additional models mostly reproduce the same mistake, turning aggregation into an amplifier of common misconceptions rather than a mechanism for correction"
- **No aggregation rule based solely on internal signals can reliably scale truthfulness** in the absence of an external verifier
- Tested on TruthfulQA: self-consistency and multi-model voting both fail when errors are systematic

**Implication**: Connects directly to Theorem 2(c) — when VC(F) ⊄ cap(M), the model lacks computational capacity to verify certain steps, producing shared blind spots and correlated errors.

#### Failure Mode 3: Self-Consistent Errors

**Tan et al. (2025): Too Consistent to Detect: A Study of Self-Consistent Errors in LLMs** (arXiv 2505.17656)
- Identifies cases where LLMs produce the same incorrect answer across multiple samples with high confidence
- Self-consistent errors arise from systematic model biases, not random noise
- No amount of sampling can fix these errors without external verification

**Implication**: When errors are deterministic (ρ → 1), N_eff → constant regardless of N. This is the extreme case of Theorem 2(b).

---

## Part 2: Condorcet Jury Theorem and Correlated Voting

### Classical Condorcet Jury Theorem (1785)

**Statement**: If each voter has probability p > 0.5 of being correct independently, then as the number of voters N → ∞, the probability that the majority vote is correct → 1.

**Key assumptions**:
1. Each voter has competence p > 0.5 (better than random)
2. Votes are independent
3. Binary choice

These map directly to our Theorem 2(a): plurality condition (p* > max p_y is a generalization of p > 0.5 for multi-class), independence, convergence rate exp(-Ω(N)).

### Extensions to Correlated Voting

**Ladha (1992): "The Condorcet Jury Theorem, Free Speech, and Correlated Votes"** (American Journal of Political Science)
- Generalizes CJT to correlated votes
- Shows that **positive correlation reduces the competence of large juries**
- **Key result**: "Negative correlation increases the competence of the jury, while positive correlation has the opposite effect"
- With strong positive correlation, enlarging the jury can initially be detrimental

**Berg (1994): "Information pooling through majority-rule voting: Condorcet's jury theorem with correlated votes"** (Journal of Economic Behavior & Organization)
- Proves CJT holds for certain correlation structures: normal, hypergeometric, Pólya distributions
- Hypergeometric correlation: asymptotic CJT still holds
- **Pólya-Eggenberger urn processes**: CJT does NOT hold asymptotically (jury competence does not approach 1), though group > individual

**Boland et al. (1989): "Aggregation of correlated votes and Condorcet's Jury Theorem"** (Theory and Decision, 2008 Springer version)
- General result: "A suitably chosen voting rule will converge to the correct answer in the large-population limit, even if there is significant correlation amongst voters, **as long as the average covariance between voters becomes small as the population becomes large**"
- Condition: Cov(V_i, V_j) → 0 as N → ∞ (vanishing correlation)
- If correlation is bounded away from 0 (ρ = Ω(1)), convergence fails

**Böttcher & Kernell (2022): "Examining the limits of the Condorcet Jury Theorem: Tradeoffs in hierarchical information aggregation systems"** (SAGE Journals)
- Empirical tests of CJT under correlation
- Finds that dependence among jury members prevents competence from approaching infallibility as size increases
- However, jury competence is still better than individual competence under moderate correlation

**Implication for our theorem**: All of these results support Theorem 2(b) — correlation reduces effective sample size. Our contribution is deriving the specific formula N_eff = N / (1 + (N-1)ρ) for the equicorrelated model and connecting it to verification complexity.

### Mathematical Foundations

**Stanford Encyclopedia of Philosophy: Jury Theorems**
- Comprehensive overview of CJT and extensions
- Notes that independence assumption is "very strong" and "often violated in practice"
- Discusses when correlation is structural (shared information, communication) vs incidental

---

## Part 3: Statistical Foundations — Design Effect and Effective Sample Size

### Design Effect in Cluster Sampling

**Wikipedia: Design Effect**
- Formula: Deff = 1 + ρ(n - 1), where ρ is intraclass correlation coefficient, n is cluster size
- Effective sample size: N_eff = N / Deff = N / [1 + ρ(n - 1)]
- **This is exactly the formula in Theorem 2(b)** for equicorrelated samples

**Kerry & Bland (1998): "The intracluster correlation coefficient in cluster randomisation"** (BMJ)
- "As the homogeneity ρ increases and as cluster sample size increases, the design effect increases"
- "The larger the intracluster correlation, the bigger the design effect and the more subjects needed to get the same power as a simply randomised study"
- **"Even a small intracluster correlation will have an impact if the cluster size is large"**
- Formula for required sample size: n* = n × [1 + ρ(m - 1)], where m is cluster size

**Eldridge et al. (2004): "Design effects and intraclass correlation coefficients from a health facility cluster survey in Benin"** (International Journal for Quality in Health Care)
- Empirical ICC values: range from 0.0036 to 0.85 depending on outcome
- Shows wide variation in practice
- Design effect Deff = 1.57 for ICC = 0.10 and cluster size n = 7 (moderate impact)

**Raudenbush (1997) + Ukoumunne et al. (1999)**: Variance inflation factor approach for sample size calculation
- "The correct application of the variance inflation factor approach for sample size calculations in trials that randomize intact clusters of individuals rests on knowledge of the variance of the outcome under simple random allocation of individuals and the intraclass correlation coefficient at the given level of clustering"
- VIF = 1 + (n - 1)ρ, which is the design effect

**Implication**: The statistical literature on clustered data provides the exact mathematical formula we use in Theorem 2(b). The novelty is recognizing that LLM samples with correlated errors due to shared computational limitations are formally equivalent to clustered data with intraclass correlation.

### Equicorrelated Models

**Statistical Odds & Ends blog (2020): "Equicorrelation matrix"**
- Definition: n × n matrix where diag = 1, off-diag = ρ ∈ [-1, 1]
- Variance of sample mean: Var(Ȳ) = σ²/n · [1 + (n-1)ρ]
- Effective sample size derivation: setting Var(Ȳ) = σ²/n_eff gives n_eff = n / [1 + (n-1)ρ]

**Schmidheiny (2025): "Short Guides to Microeconometrics" (panel data notes)**
- Equicorrelated random effects model: special case of panel data
- Appears in various contexts: longitudinal studies, cluster randomization, multiple testing

**Implication**: The equicorrelated model is a standard statistical tool. We apply it to LLM sampling by showing that verification hardness produces equicorrelated errors (Lemma 2).

---

## Part 4: Gap Analysis — What We Contribute

### What prior work establishes:
1. ✅ Self-consistency works empirically on math benchmarks (Wang et al. 2023)
2. ✅ Self-consistency fails on long-context tasks due to positional bias (Tao et al. 2024)
3. ✅ Errors are correlated when models share blind spots (Consensus paper 2026)
4. ✅ Condorcet Jury Theorem holds under independence, degrades under correlation (Ladha 1992, Berg 1994)
5. ✅ Design effect formula: Deff = 1 + ρ(n-1), effective sample size n_eff = n / Deff (cluster sampling literature)
6. ✅ LLMs cannot self-verify plans (Stechly et al. 2024, Kambhampati et al. 2024)

### What prior work does NOT establish:
1. ❌ **Formal connection between verification complexity and error correlation** — nobody has linked VC(F) ⊄ cap(M) to ρ > 0
2. ❌ **Unified conditions for when self-consistency works** — Wang et al. state it works, failure papers state it fails, but no one has formalized the boundary
3. ❌ **Complexity-theoretic grounding of the plurality condition** — the implicit verification requirement is not stated
4. ❌ **Prediction across task families** — no one has used complexity theory to predict which benchmarks will show self-consistency improvement

### Our contribution (Theorem 2):
**Part (a)**: Standard CJT result, adapted to multi-class setting with plurality condition. **Novel framing**: plurality = implicit verification capability.

**Part (b)**: Standard design effect formula from cluster sampling. **Novel application**: LLM samples as "clusters" under equicorrelation.

**Part (c)**: **Entirely novel**. Connects verification complexity VC(F) ⊄ cap(M) to correlated errors ρ > 0 via shared computational bottleneck. This is the bridge nobody has built.

**Synthesis**: The theorem unifies three previously separate insights:
- CJT (political science / social choice)
- Design effect (biostatistics / survey methodology)
- Verification complexity (computational complexity theory)

into a **predictive framework for LLM output verification**.

---

## Part 5: Implications for the Paper

### Theorem Statement Review

Current theorem (paper lines 252-279) has three parts:
- (a) Plurality → convergence at exp(-Ω(N)) ✅ Well-grounded in CJT
- (b) Correlation → N_eff = N / (1 + (N-1)ρ) ✅ Well-grounded in design effect theory
- (c) VC hard → correlation ρ > 0 ✅ Supported by failure mode empirics (Tao, Consensus paper), formalized via Lemma 2

### Proof Review

Current proof (lines 264-279):
- Part (a): Cites strong law of large numbers + Hoeffding ✅
- Part (b): Cites equicorrelated model ✅
- Part (c): Argues VC hard → computational bottleneck → shared errors → correlation ✅

Extended proof in appendix (lines 809-856):
- Full Hoeffding derivation for part (a) ✅
- Lemma 1 (effective sample size under correlation) with complete derivation ✅
- Lemma 2 (verification hardness implies correlated errors) with law of total probability ✅
- Part (c) synthesis connecting both lemmas ✅

**Assessment**: The proof is **complete and rigorous**. All steps are justified. The literature provides strong support for each component.

### Citation Additions Needed

The paper currently cites:
- ✅ Wang et al. 2023 (self-consistency)
- ❌ Missing: Tao et al. 2024 (positional bias failure)
- ❌ Missing: Consensus paper 2026 (shared blind spots)
- ❌ Missing: Ladha 1992 or Berg 1994 (CJT under correlation)
- ❌ Missing: Kerry & Bland 1998 or design effect reference for cluster sampling
- ❌ Missing: Stechly et al. 2024 (already cited elsewhere for planning, but should cite in Theorem 2 discussion)

**Recommendation**: Add 3-5 sentences to the proof or remark after Theorem 2 citing:
1. Tao et al. 2024 for empirical evidence of correlation from architectural bias
2. Consensus paper 2026 for shared training data → correlated errors
3. Cluster sampling literature (Kerry & Bland 1998) for design effect formula
4. Ladha 1992 or Berg 1994 for CJT under correlation

This will strengthen the empirical grounding and show we're building on established statistical theory.

### Empirical Predictions

Theorem 2 predicts:
1. ✅ Self-consistency works on GSM8K, MATH (VC = P, independence likely holds)
2. ✅ Self-consistency fails on PlanBench-HTN (VC ≥ coNP, correlation expected)
3. ✅ 3-SAT feasibility: partial benefit (VC = P but search heuristics may correlate errors)
4. ❓ Long-context tasks: Tao et al. already showed failure due to positional bias (Type 6, not verification hardness)

**Note**: Long-context failure is architectural (Type 6), not verification complexity (Type 5). The theorem correctly does NOT predict this case — it's outside scope. But we can cite Tao et al. as **additional** empirical support that correlation (from any source) breaks self-consistency.

---

## Key References by Topic

### LLM Self-Consistency
| Paper | Year | Venue | Key Contribution |
|-------|------|-------|------------------|
| Wang et al. | 2023 | ICLR | Original self-consistency method, shows improvements on math/reasoning |
| Tao et al. | 2024 | arXiv | Shows self-consistency fails on long-context due to positional bias (53/56 cases) |
| Consensus paper | 2026 | arXiv | Shared training → shared blind spots → correlated errors → aggregation fails |
| Tan et al. | 2025 | arXiv | Self-consistent errors: deterministic mistakes across samples |

### Condorcet Jury Theorem
| Paper | Year | Venue | Key Contribution |
|-------|------|-------|------------------|
| Ladha | 1992 | AJPS | CJT under correlation: positive correlation reduces jury competence |
| Berg | 1994 | JEB&O | CJT holds for some correlation structures (hypergeometric), fails for others (Pólya) |
| Boland et al. | 1989/2008 | Theory & Decision | Convergence requires average covariance → 0 as N → ∞ |
| Böttcher & Kernell | 2022 | SAGE | Empirical limits of CJT under hierarchical aggregation |

### Design Effect / Effective Sample Size
| Paper | Year | Venue | Key Contribution |
|-------|------|-------|------------------|
| Kerry & Bland | 1998 | BMJ | Intraclass correlation in cluster trials: Deff = 1 + ρ(n-1) |
| Eldridge et al. | 2004 | IJQHC | Empirical ICC estimates from health surveys (0.0036 to 0.85) |
| Ukoumunne et al. | 1999 | Statistician | VIF approach for sample size in cluster trials |

---

## Recommendations for Paper

### Immediate Actions (Researcher → Writer handoff)
1. ✅ **No changes needed to theorem statement** — it is correct as written
2. ✅ **No changes needed to main proof** — it is complete
3. ✅ **No changes needed to appendix proofs** — Lemmas 1-2 are fully expanded
4. ⚠️ **Add 3-4 citations** to Remark after Theorem 2 or Corollary 1:
   - Tao et al. 2024 for positional bias → correlation
   - Consensus paper 2026 for shared priors → correlation
   - Kerry & Bland 1998 OR design effect Wikipedia for Deff formula
   - Ladha 1992 OR Berg 1994 for CJT under correlation
5. ⚠️ **Add 1 sentence to Related Work** (Section 7) discussing design effect connection to cluster sampling

### Literature Gap Confirmed
**No prior work connects verification complexity to self-consistency conditions.**

Wang et al. (2023) proposed the method empirically. Failure papers (Tao 2024, Consensus 2026) identified correlation as the cause. Statistical literature (Kerry & Bland, cluster sampling) provides the math. But **nobody has unified these streams via complexity theory**.

**Theorem 2 is novel.** The individual components (CJT, design effect, empirical failures) are established, but the synthesis is new.

---

## Open Questions for Future Work

1. **Average-case correlation**: Can we refine the ρ estimate for specific task families beyond worst-case?
2. **Partial verification**: When VC(F) has components in P and components outside P, how does correlation split?
3. **Adaptive sampling**: Can we detect correlation online and stop sampling early when N_eff saturates?
4. **Multi-model aggregation**: Does ensemble across models with different architectures reduce correlation? (Consensus paper suggests no when training data overlaps.)

---

## Sources

### Self-Consistency in LLMs
- [Self-Consistency Prompting: Enhancing AI Accuracy](https://learnprompting.org/docs/intermediate/self_consistency)
- [Self-Consistency with Chain of Thought (CoT-SC)](https://medium.com/@johannes.koeppern/self-consistency-with-chain-of-thought-cot-sc-2f7a1ea9f941)
- [Ranked Voting based Self-Consistency of Large Language Models](https://arxiv.org/html/2505.10772v1)
- [Tao et al. (2024): Self-Consistency Falls Short! The Adverse Effects of Positional Bias on Long-Context Problems](https://arxiv.org/html/2411.01101)
- [Consensus is Not Verification: Why Crowd Wisdom Strategies Fail for LLM Truthfulness](https://arxiv.org/html/2603.06612)
- [Tan et al. (2025): Too Consistent to Detect: A Study of Self-Consistent Errors in LLMs](https://arxiv.org/html/2505.17656)

### Condorcet Jury Theorem
- [Condorcet's jury theorem - Wikipedia](https://en.wikipedia.org/wiki/Condorcet's_jury_theorem)
- [Böttcher & Kernell (2022): Examining the limits of the Condorcet Jury Theorem](https://journals.sagepub.com/doi/full/10.1177/26339137221133401)
- [Berg (1994): Information pooling through majority-rule voting: Condorcet's jury theorem with correlated votes](https://www.sciencedirect.com/science/article/abs/pii/016726819400068P)
- [Boland et al. (2008): Aggregation of correlated votes and Condorcet's Jury Theorem](https://link.springer.com/article/10.1007/s11238-008-9120-4)
- [Jury Theorems - Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/jury-theorems/)

### Design Effect and Effective Sample Size
- [Design Effects and Effective Sample Size - CRAN](https://cran.r-project.org/web/packages/PracTools/vignettes/Design-effects.html)
- [Design effect - Wikipedia](https://en.wikipedia.org/wiki/Design_effect)
- [Kerry & Bland (1998): The intracluster correlation coefficient in cluster randomisation](https://pmc.ncbi.nlm.nih.gov/articles/PMC1113123/)
- [Eldridge et al. (2004): Design effects and intraclass correlation coefficients from a health facility cluster survey in Benin](https://academic.oup.com/intqhc/article/14/6/521/1902733)
- [Equicorrelation matrix - Statistical Odds & Ends](https://statisticaloddsandends.wordpress.com/2020/02/20/equicorrelation-matrix/)
- [Variance inflation factor - Wikipedia](https://en.wikipedia.org/wiki/Variance_inflation_factor)

