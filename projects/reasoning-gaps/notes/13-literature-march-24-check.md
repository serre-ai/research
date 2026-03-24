# Literature Currency Check: March 14-24, 2026

**Date**: 2026-03-24
**Scope**: Quick scan for concurrent work published in last 11 days
**Previous check**: March 13, 2026 (evening session)

---

## Search Strategy

Searched arXiv and Google Scholar for:
- "transformer reasoning complexity" + March 2026
- "chain of thought limitations" + March 2026
- "transformer expressiveness circuit complexity" + recent

**Result**: 1 potentially relevant paper found

---

## New Paper Identified

### Transformers Can Learn Rules They've Never Seen (arXiv:2603.17019v1)
**Authors**: (not specified in abstract)
**Published**: March 17, 2026
**Venue**: arXiv preprint

**Contribution**: Proves that transformers can recover compositional rules absent from training data (not merely interpolate). Uses cellular automata to show transformers achieve 100% accuracy on unseen rules while k-NN/GP/SVM/RF provably achieve 0%.

**Mechanism**: Constraint propagation through multi-step prediction. Soft unrolling (96.7%) >> hard unrolling (65.5%).

**Relevance to our work**: ⚠️ **Orthogonal, not competing**

**Analysis**:
- **Their focus**: Rule learning and extrapolation (what transformers CAN do)
- **Our focus**: Reasoning limitations (what transformers CANNOT do)
- **Complementary framing**: They show transformers can learn compositional rules; we show they still fail on certain complexity classes even with CoT
- **No scoop risk**: Different research question, different contribution

**Action**: ✅ **Note for awareness but no integration needed**

Could cite in Discussion/Related Work as evidence that transformers have strong compositional learning abilities, making their systematic failures on depth/serial gaps more striking (not explained by lack of compositional capacity).

---

## Other Papers Found

### Circuit Complexity Bounds for RoPE-based Transformer Architecture (arXiv:2411.07602)
**Published**: November 2024
**Status**: Already aware (outside March 14-24 window)

### What Formal Languages Can Transformers Express? A Survey (TACL 2024)
**Status**: Already cited (Strobl et al., key reference)

---

## Concurrent Work Assessment

**Status**: ✅ **No scooping threats detected**

No papers in the last 11 days address:
- Formal taxonomy of LLM reasoning gaps
- Empirical validation of complexity-theoretic predictions
- Diagnostic benchmarks for gap types
- Systematic CoT effectiveness analysis by gap type

---

## Recommendation

**For submission**: No changes needed to paper

**For revision** (post-acceptance):
- Consider adding citation to arXiv:2603.17019 in Related Work
- Frame as: "Transformers demonstrate strong compositional learning [2603.17019], yet systematically fail on our benchmark tasks, suggesting capacity limitations are not due to poor generalization but fundamental architectural bounds"

---

## Coverage Assessment

Literature coverage remains comprehensive:
- **Transformer expressiveness**: 15+ papers (Merrill, Strobl, Hahn, etc.)
- **CoT theory**: 5+ papers (Li, Feng, Dziri, etc.)
- **Empirical limitations**: 10+ papers (Song, Mirzadeh, Sprague, etc.)
- **Mechanistic analysis**: 5+ papers (Ye, Raju, etc.)

**Total surveyed**: 90+ papers through March 13
**New additions**: 1 paper (March 17, orthogonal)
**Final count**: 91 papers surveyed

**Status**: ✅ Literature review remains current and comprehensive
