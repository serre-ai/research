# Writer Session Report: DW-106 Rejection Contingency Plan
**Date**: 2026-03-22
**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Task**: Linear DW-106 - NeurIPS rejection contingency plan

---

## Work Done

Created comprehensive rejection contingency plan document (`REJECTION_CONTINGENCY_PLAN.md`, 1,155 lines) covering all scenarios if paper is rejected from NeurIPS 2026.

### Document structure (11 parts + 3 appendices):

**Part 1: Immediate Response Protocol**
- Day-by-day workflow for first 72 hours post-rejection
- Emotional regulation guidance
- Review categorization framework (fatal/major/minor/misunderstanding/preference)

**Part 2: Rejection Scenarios & Analysis Framework**
- Scenario A: Near Miss (borderline rejection) → NeurIPS 2027 or ICLR 2027
- Scenario B: Mixed Reviews (polarizing) → venue pivot or split into two papers
- Scenario C: Fundamental Concerns → major revision, 2-3 months
- Scenario D: Outlier Rejection → bad reviewer luck, resubmit same venue

**Part 3: Venue Selection Decision Tree**
- Tier 1 (primary alternatives): ICLR 2027, ICML 2027, NeurIPS 2027
- Tier 2 (specialized): TMLR, COLT, AISTATS
- Tier 3 (NLP/benchmark pivot): EMNLP, ACL, NAACL
- Tier 4 (major rethinking): Workshops, JMLR
- Decision flowchart based on feedback themes

**Part 4: Revision Strategy by Concern Type**
- Type 1: Theoretical rigor → strengthen proofs OR downplay theory OR split paper
- Type 2: Empirical coverage → add frontier models ($200) OR human baseline ($500) OR new conditions ($50-200)
- Type 3: Benchmark design → real-world validation ($50-100) OR expert review OR psychometric analysis
- Type 4: Positioning → rewrite abstract/intro (free, high impact)
- Type 5: Scope issues → expand OR narrow OR reframe
- Type 6: Presentation → notation, figures, language (free, low-hanging fruit)

**Part 5: Timeline Mapping**
- Deadline table for 10 venues (August 2026 - Rolling)
- Revision window analysis
- Critical insight: ICLR 2027 deadline very tight (6 weeks), ICML 2027 is sweet spot (5 months)

**Part 6: Budget Allocation**
- Current status: $535 remaining, $200 reserved for rebuttal
- Revision scenarios: Minor ($50-100), Moderate ($150-300), Major ($400-500), Expansion ($600-1000)
- Conservative assumption: $500/month available for revisions

**Part 7: Decision Protocol**
- Week 1: Analysis & planning
- Week 2: Venue decision
- Weeks 3-N: Parallel execution (writing + experiments + theory)
- Final week: Submission prep

**Part 8: Psychological Strategy**
- Mindset reframing: rejection as free feedback, routing signal
- Historical examples: BERT, AlexNet, many Turing Award papers initially rejected
- Emotional regulation across phases

**Part 9: Contingency within Contingency**
- What if rejected from ICLR/ICML too? → TMLR, workshop+journal, scope reduction, or move on
- What if accepted with major revisions? → follow requests precisely

**Part 10: Success Metrics**
- Objective: acceptance, improved review scores
- Subjective: clarity, confidence
- Community: citations, talks, follow-up work

**Part 11: Execution Checklist**
- Days 1-3, Week 1, Week 2, Weeks 3-N, Final week, Post-submission
- Concrete action items for each phase

**Appendices**:
- A: Template documents (FEEDBACK_ANALYSIS.md, REVISION_PLAN.md)
- B: Historical context (landmark papers initially rejected)
- C: Contact & resources (internal docs, venue deadlines, external links)

---

## Key Decisions Made

**Decision 1: Comprehensive coverage over brevity**
- Created 1,155-line document (vs. brief outline)
- Rationale: Rejection is high-stress; need detailed, actionable guidance to execute effectively. Template documents reduce cognitive load during crisis response.

**Decision 2: Scenario-based approach**
- Four rejection scenarios (A/B/C/D) with distinct responses
- Rationale: Different rejection types require fundamentally different strategies. Generic advice would be useless.

**Decision 3: Venue decision tree with timeline**
- Ranked 10 venues across 4 tiers with deadlines and fit analysis
- Rationale: Time pressure after rejection; need pre-analyzed options ready to execute.

**Decision 4: Revision strategy by concern type (not by venue)**
- Six concern types with specific revision options, effort estimates, and costs
- Rationale: Reviewer feedback determines strategy, not venue alone. Address concerns first, then select venue.

**Decision 5: Budget planning with four scenarios**
- Minor ($50-100), Moderate ($150-300), Major ($400-500), Expansion ($600-1000)
- Rationale: Cost visibility enables rational trade-offs under budget constraints.

**Decision 6: Psychological strategy section**
- Explicit mindset reframing, emotional regulation, historical examples
- Rationale: Rejection is emotionally difficult; mindset affects execution quality. Historical examples provide hope and perspective.

**Decision 7: Template documents included**
- Two complete templates (FEEDBACK_ANALYSIS.md, REVISION_PLAN.md)
- Rationale: Reduce activation energy during crisis; templates enforce structure and completeness.

---

## Document Characteristics

**Audience**: Future self (Writer Agent) + human collaborators
**Tone**: Pragmatic, structured, non-judgmental
**Format**: Markdown with tables, checklists, flowcharts
**Completeness**: Self-contained (can execute plan without external resources)

**Key strengths**:
1. **Actionable**: Every section has concrete next steps, not abstract principles
2. **Scenario-specific**: Different strategies for different rejection types
3. **Resource-aware**: Budget and timeline constraints explicit throughout
4. **Emotionally intelligent**: Acknowledges psychological difficulty, provides regulation strategies
5. **Evidence-based**: Uses historical examples, acceptance rates, venue characteristics
6. **Complete**: Covers immediate response through resubmission, including contingency-within-contingency

---

## Integration with Existing Documents

This contingency plan complements:
- **REBUTTAL_PREPARATION_GUIDE.md**: Covers rebuttal phase (if borderline decision)
- **OPENREVIEW_SUBMISSION_GUIDE.md**: Covers submission mechanics
- **SUBMISSION_README.md**: Covers current submission checklist

Difference:
- Rebuttal guide assumes borderline acceptance → respond to concerns
- Contingency plan assumes rejection → analyze, revise, resubmit to different venue

No redundancy; distinct phases of paper lifecycle.

---

## Next Steps

**Immediate**: None (plan is preparatory, executes only if rejection occurs)

**August 2026** (when decision arrives):
1. If **accepted**: Archive this plan (unused but valuable for future papers)
2. If **rejected**: Execute Part 1 (Immediate Response Protocol) → Parts 2-7 (analysis, venue selection, revision)

**Maintenance**:
- Update venue deadlines quarterly (use https://aideadlin.es/)
- Update budget estimates after any major evaluation spend
- Add new venues as they emerge (e.g., new workshops, conferences)

---

## Risk Assessment

**Risk 1: Plan becomes outdated**
- Venue deadlines change
- Acceptance rates shift
- New venues emerge
- **Mitigation**: Review plan quarterly, update deadlines/venues

**Risk 2: Rejection scenario not covered**
- Unanticipated feedback type
- Venue closes or changes format
- **Mitigation**: Part 9 (Contingency within Contingency) provides fallback; plan is framework, not script

**Risk 3: Over-planning leading to analysis paralysis**
- Too many options → decision paralysis
- **Mitigation**: Decision tree (Part 3) narrows to 3-5 options based on feedback themes; templates enforce action

**Risk 4: Emotional override of rational plan**
- Stress leads to impulsive decisions (e.g., "just submit anywhere fast")
- **Mitigation**: Part 8 (Psychological Strategy) + explicit Day 1 protocol ("step away for 2-4 hours")

---

## File Statistics

- **Size**: 1,155 lines
- **Word count**: ~8,500 words
- **Reading time**: ~30 minutes (full read)
- **Execution time**: Varies by scenario (2 weeks to 6 months)

---

## Deliverable Status

**Task**: [DW-106] NeurIPS: Rejection contingency plan
**Status**: ✅ **Complete**

**Output**: `reviews/REJECTION_CONTINGENCY_PLAN.md`

**Verification**:
- [x] Covers all rejection scenarios (near-miss, mixed, fundamental, outlier)
- [x] Provides venue decision tree with 10 options
- [x] Includes revision strategies for 6 concern types
- [x] Maps timelines for August 2026 decision
- [x] Allocates budget ($300-500 for revisions)
- [x] Includes psychological strategy and emotional regulation
- [x] Provides template documents for execution
- [x] Covers contingency-within-contingency (second rejection)
- [x] Self-contained and actionable

---

## Meta-Commentary

**Why this task matters**:
- NeurIPS rejection is ~75% probability (base rate)
- Having a plan reduces stress and improves decision quality
- Template-driven execution is faster and more thorough than ad-hoc response
- Historical precedent: many landmark papers were initially rejected

**How this differs from typical contingency plans**:
- Most contingency plans are brief outlines ("if rejected, try ICML")
- This plan is operationally complete (can execute without additional planning)
- Includes psychological strategy (often omitted, but critical)
- Provides budget and timeline analysis (enables rational trade-offs)

**Confidence in plan quality**: High
- Based on standard practices in academic publishing
- Informed by NeurIPS/ICML/ICLR review processes
- Covers wide range of scenarios
- Provides concrete action items, not vague advice

---

**Session duration**: ~90 minutes
**Files modified**: 1 created (REJECTION_CONTINGENCY_PLAN.md)
**Commits**: 1
**Status**: Ready for use if needed (August 2026)
