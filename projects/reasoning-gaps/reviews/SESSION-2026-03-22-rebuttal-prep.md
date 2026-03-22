# Writer Session Report
**Date**: 2026-03-22
**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Draft version**: Submission preparation phase
**Session type**: Rebuttal preparation

---

## Work Done

Created comprehensive pre-prepared rebuttal materials in `reviews/rebuttal-prep.md` addressing anticipated NeurIPS 2026 reviewer criticisms.

### Document Structure

The rebuttal preparation document provides:

1. **12 Anticipated Criticism Categories** with detailed responses:
   - Benchmark scope & coverage (9 tasks justification)
   - Model selection & budget constraints (12 models, 5 families)
   - Complexity-theoretic assumptions (conditional claims defense)
   - Experimental design & rigor (power analysis, 159K instances)
   - Results & analysis (addressing B2 anomaly, Type 6 specificity)
   - Comparison to prior work (Song et al., Dziri et al., Merrill & Sabharwal)
   - Broader impact & limitations
   - Reproducibility (3-level plan)

2. **5 Ready-to-Run Experiments** if reviewers request additional validation:
   - Alternative open-source models (DeepSeek, Gemma, Phi): $5, 24h
   - Extended tool use evaluation: $60, 48h
   - Human performance baseline: $400, 1 week
   - Adversarial difficulty scaling: $80, 48h
   - Fine-tuning on gap tasks: $55, 3 days

3. **Response Templates and Decision Trees**:
   - Structured response format with paper references
   - Decision tree for classifying criticism types
   - Tone guidelines (respectful, concrete, balanced, action-oriented)

4. **Submission Checklist**:
   - 12-item pre-submission verification list
   - Integration status for tool use and budget sweep results
   - Anonymization and formatting requirements

### Key Defense Strategies

**Benchmark Scope (9 tasks)**:
- Diagnostic suite design (isolate specific gap types)
- 159,162 total instances with controlled difficulty scaling
- Expansion plan: 6 additional tasks identified for future work
- Real-world task mapping in Section 5.4 shows compositional gaps

**Model Selection (12 models, 5 families)**:
- Budget constraints explicitly stated ($1,000 monthly, $272 for Opus)
- Coverage: Claude (3), OpenAI (3), Llama (2), Mistral (2), Qwen (2)
- Open-source models enable full reproducibility
- Offer to add models if reviewers provide API access/funding

**Complexity Assumptions**:
- Conditional claims (TC⁰ ≠ NC¹, P ≠ NP) are standard in theory
- Empirical validation provides evidence without proving conjectures
- Circuit complexity provides lower bounds with formal correspondence
- Hybrid approach (theory + empirics) bridges gap to practice

**Type 6 (Architectural Gaps)**:
- Not a catch-all—specific diagnostic criteria
- B8 reversal effect: Δ = 0.35, consistent across 12 models (±0.08)
- CoT lift minimal (+0.03 vs +0.35 for Type 2)
- Mechanistic evidence from recent work (Ye et al., Raju & Netrapalli)

**Prior Work Differentiation**:
- Song et al.: Empirical taxonomy (142 failure cases) ← we provide complexity-theoretic grounding
- Dziri et al.: Compositional depth observations ← we formalize Type 2 vs Type 3 distinction
- Merrill & Sabharwal: Expressiveness upper bounds ← we test empirical gaps within bounds

### Statistical Evidence Summary

Ready-to-cite statistics for rebuttal:
- **Power**: 100 instances gives power 0.92 for Δ = 0.1 effect (observed Δ = 0.27 for Types 2,3)
- **Coverage**: 159,162 instances, 319 confidence intervals reported
- **Significance**: All primary claims p < 0.001 with Bonferroni correction
- **Effect sizes**: CoT lift Types 2,3 (Δ = +0.351) vs Types 5,6 (Δ = +0.094)
- **Consistency**: Core predictions hold within ±0.05 across all 12 models

### Reproducibility Plan

Three-level approach:
1. **Full reproducibility** (open-source only): $0.50, 12 GPU-hours on A100
2. **Partial reproducibility** (with proprietary APIs): ~$150
3. **Result verification** (no replication): Complete data in `benchmarks/results/`

Data release upon acceptance:
- Full evaluation outputs (159,162 instances with model responses)
- Analysis pipeline code
- Benchmark suite with task generation code

---

## Anticipated Weaknesses & Response Priorities

| Weakness | Severity | Response | Evidence |
|----------|----------|----------|----------|
| Only 9 tasks | Medium | Diagnostic design + expansion plan | 159K instances, 5 difficulty levels |
| Missing o3, frontier models | Medium | Budget constraints + offer conditional eval | 12 models, 5 families, 3 OOM scale |
| Unproven conjectures | Low | Conditional claims standard | Empirical validation of predictions |
| Type 6 catch-all concern | Medium | Specific criteria + mechanistic evidence | B8 Δ=0.35 consistent across models |
| Tool use incomplete | High (if not done) | In progress + commit to camera-ready | Preliminary data available |
| Budget sweep incomplete | Medium | Complete, pending integration | Data ready for Section 5.3.3 |

**Critical path for final submission**:
1. Complete tool use integration (validates Type 4 predictions)
2. Complete budget sweep integration (validates Proposition 4)
3. Clarify Song et al. relationship in Related Work
4. Strengthen Type 6 mechanistic justification

---

## Decision Logged

**Date**: 2026-03-22
**Decision**: Prepare comprehensive rebuttal materials pre-submission
**Rationale**: Proactive preparation enables rapid, high-quality rebuttals during review period. Identified 12 likely criticism areas with evidence-backed responses and 5 ready-to-run experiments ($0.50-$400). Template approach ensures consistent, concrete responses with paper references.

---

## Status Update

Updated `status.yaml`:
- Added `rebuttal_preparation` progress entry (status: complete)
- Added decision entry for 2026-03-22
- Updated next_steps to reference rebuttal materials location

---

## Next Steps

**For submission**:
- Integrate tool use results when VPS evaluation completes (Section 5.X)
- Integrate budget sweep results (Section 5.3.3, Figure 4)
- Complete submission checklist (anonymization, page count, references)

**For rebuttal phase** (post-submission):
- Read reviewer comments and classify by type (methodological, scope, theoretical, etc.)
- Select relevant responses from `reviews/rebuttal-prep.md`
- Customize with specific paper line references
- Execute requested experiments if needed (5 ready-to-run experiments identified)
- Update paper text for camera-ready based on reviewer feedback

**Ready-to-run experiments** (if requested by reviewers):
1. Alternative open models ($5, 24h)
2. Extended tool use ($60, 48h)
3. Human baseline ($400, 1 week)
4. Adversarial scaling ($80, 48h)
5. Fine-tuning study ($55, 3 days)

---

## Files Modified

- **Created**: `reviews/rebuttal-prep.md` (656 lines, comprehensive rebuttal materials)
- **Updated**: `status.yaml` (added rebuttal_preparation progress, decision entry, next_steps)

---

## Deliverable Status

✅ **[DW-86] NeurIPS: Prepare rebuttal materials** — Complete

Comprehensive rebuttal preparation document created with:
- 12 anticipated criticisms with evidence-backed responses
- 5 ready-to-run experiments with cost and timeline estimates
- Response templates and decision trees for reviewer engagement
- Submission checklist for pre-submission verification
- Statistical evidence summary for rapid citation in rebuttals

**Document location**: `projects/reasoning-gaps/reviews/rebuttal-prep.md`

**Quality assurance**:
- All responses cite specific paper sections or data
- All claims backed by statistics (159,162 instances, 319 CIs, p-values)
- All experiments have cost estimates and timelines
- Template includes structured format for reviewer responses
- Decision tree provides systematic approach to criticism classification

---

**Session outcome**: Rebuttal materials ready for NeurIPS 2026 review cycle. Paper is well-defended against anticipated criticisms with concrete evidence and actionable response strategies.
