# Rejection Contingency Plan: NeurIPS 2026

**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Primary venue**: NeurIPS 2026
**Submission deadline**: May 6, 2026
**Expected decision**: August 2026
**Date prepared**: 2026-03-22

---

## Executive Summary

This document provides a comprehensive contingency plan if the paper is rejected from NeurIPS 2026. The plan covers:
1. **Immediate response protocol** (Days 1-3)
2. **Feedback analysis framework** (Week 1)
3. **Venue selection decision tree** (Week 1-2)
4. **Revision strategy by rejection type** (Weeks 2-8)
5. **Timeline mapping to alternative venues** (updated quarterly)
6. **Budget allocation for revision work** ($300-500 reserved)

**Key principle**: Rejection is a source of critical feedback, not a terminal outcome. The paper addresses a fundamental question with solid empirical work; the goal is to refine positioning, address legitimate concerns, and find the right venue-audience fit.

---

## Part 1: Immediate Response Protocol

### Day 1: Initial Assessment (2-4 hours)

**DO NOT:**
- React emotionally or defensively
- Immediately commit to a resubmission venue
- Start revising the paper without analysis
- Dismiss reviewer feedback as "unfair" without reflection

**DO:**
1. **Read all reviews completely** without taking notes
2. **Step away for 2-4 hours** before analysis
3. **Return and read again**, this time extracting all concerns
4. **Categorize each concern** into:
   - **Fatal flaw**: Threatens fundamental contribution (e.g., "framework is circular")
   - **Major issue**: Significant but addressable (e.g., "missing key baseline")
   - **Minor issue**: Easy to fix (e.g., "notation unclear")
   - **Misunderstanding**: Reviewer missed something in the paper
   - **Preference**: Style or framing choice, not correctness
5. **Count reviewer breakdown**:
   - How many Accept/Weak Accept/Borderline/Weak Reject/Reject?
   - Is there a clear outlier (e.g., one strong reject, two weak accepts)?
   - Did the meta-reviewer/AC weigh in? What was their position?

### Day 2-3: Feedback Synthesis (4-8 hours)

**Create structured document**: `reviews/NEURIPS_2026_FEEDBACK_ANALYSIS.md`

**Template structure**:
```markdown
# NeurIPS 2026 Rejection Analysis

## Decision Summary
- **Verdict**: [Accept/Reject, with vote breakdown]
- **Meta-reviewer summary**: [Key points from AC/meta-reviewer]
- **Overall tone**: [Positive but concerned / Mixed / Skeptical / Hostile]

## Fatal Flaws (if any)
[List any fundamental issues that threaten the contribution]

## Major Issues (addressable)
[Issues that require substantial work but are fixable]

## Minor Issues
[Easy fixes, clarifications, presentation improvements]

## Misunderstandings
[Points where reviewers missed content in the paper]

## Themes Across Reviews
[Common concerns mentioned by 2+ reviewers]

## Outliers
[Concerns raised by only 1 reviewer, especially if extreme]

## Positive Feedback
[What reviewers liked — important for preserving strengths]

## Recommended Actions
[Prioritized list of what to address in revision]
```

**Output**: Clear classification of all feedback with action items prioritized.

---

## Part 2: Rejection Scenarios & Analysis Framework

### Scenario A: Near Miss (Borderline Rejection)
**Indicators**:
- Multiple "Borderline" or "Weak Reject" scores
- Meta-reviewer mentions "close decision"
- Reviews acknowledge strengths but identify 1-2 fixable issues
- Tone: "This is interesting work, but..."

**Interpretation**:
- Paper is fundamentally sound
- Positioning or execution issues, not conceptual
- Likely competitive after revision

**Primary concern categories to expect**:
1. **Empirical coverage**: "Missing models X, Y" or "Need more baselines"
2. **Theoretical rigor**: "Propositions need full proofs" or "TC⁰ bound is informal"
3. **Benchmark design**: "Tasks too simple" or "Difficulty calibration unclear"
4. **Presentation**: "Framework too complex" or "Results buried in text"

**Recommended action**:
- Address all major issues definitively
- Resubmit to **same venue next year** (NeurIPS 2027) or **ICLR 2027** (earlier deadline)

---

### Scenario B: Mixed Reviews (Substantive Disagreement)
**Indicators**:
- Wide score spread (e.g., one Weak Accept, one Borderline, one Reject)
- Reviewers disagree on fundamental aspects
- Meta-reviewer acknowledges disagreement but sides with majority
- Tone: "Reviewers had differing views on..."

**Interpretation**:
- Paper is polarizing — some see value, others don't
- Likely a **framing or positioning issue**, not a content issue
- Different reviewers wanted different papers

**Primary concern categories to expect**:
1. **Scope ambiguity**: "Is this a theory paper or an empirical paper?"
2. **Contribution clarity**: "What's the main contribution?"
3. **Audience mismatch**: "This belongs in a theory venue" vs. "This is too empirical"
4. **Related work**: "How does this differ from [Song et al. 2026]?"

**Recommended action**:
- Clarify positioning in intro/abstract
- Consider **venue pivot** to better audience fit (see Part 3)
- Potentially **split into two papers**: theory-focused (COLT/STOC) + empirical (ICML/ICLR)

---

### Scenario C: Fundamental Concerns (Clear Rejection)
**Indicators**:
- Multiple "Reject" or "Strong Reject" scores
- Meta-reviewer agrees with rejection
- Reviews identify conceptual or methodological flaws
- Tone: "This paper has serious issues..."

**Interpretation**:
- Reviewers see a fundamental problem with the approach
- Not just execution — the contribution itself is questioned
- Requires major rethinking, not just revision

**Primary concern categories to expect**:
1. **Novelty**: "This is incremental over [prior work]"
2. **Validity**: "The TC⁰ bound doesn't apply to modern LLMs"
3. **Significance**: "The taxonomy is obvious" or "Gaps are already known"
4. **Experimental design**: "Benchmark is flawed" or "Results are contaminated"

**Recommended action**:
- **Deep revision** (2-3 months)
- Consider **scope pivot**:
  - Option 1: Focus on theoretical framework only → theory venue (COLT, ALT)
  - Option 2: Focus on benchmark suite → empirical venue (EMNLP, EACL)
  - Option 3: Strengthen both contributions with additional work → resubmit ICLR/ICML
- Potentially seek **external feedback** from colleagues in complexity theory + LLM evaluation

---

### Scenario D: Outlier Rejection (One Strong Reject, Others Positive)
**Indicators**:
- One reviewer gives "Strong Reject" or "Reject"
- Other reviewers give "Weak Accept" or "Borderline"
- Meta-reviewer breaks tie (usually conservatively → rejection)
- Tone of outlier: Often hostile or misunderstanding core contribution

**Interpretation**:
- Bad luck with reviewer assignment
- One reviewer may have misunderstood paper or brought bias
- Paper is likely solid but fell victim to meta-reviewer conservatism

**Primary concern categories to expect**:
- Outlier: Usually one extreme concern (e.g., "This framework is vacuous")
- Other reviewers: Minor presentation or scope issues

**Recommended action**:
- Address all reviewers' concerns, including the outlier
- If outlier concern is a clear misunderstanding, add clarifying text
- Resubmit to **same venue next cycle** (reviewers likely to be different)
- OR submit to **overlapping venue** (ICML if rejected from NeurIPS) where reviewer pool differs

---

## Part 3: Venue Selection Decision Tree

### Primary Considerations

**Factor 1: Timeline urgency**
- **High urgency** (results aging, competition): → Earliest deadline (ICLR, AISTATS)
- **Medium urgency** (want publication by EOY 2027): → ICML, NeurIPS 2027
- **Low urgency** (quality > speed): → Take time for major revision → top venue 2028

**Factor 2: Feedback themes**
- **"Too theoretical for NeurIPS"**: → COLT, ALT, STOC/FOCS workshop
- **"Not enough theory"**: → ICML, ICLR (more empirics-friendly)
- **"Benchmark is the contribution"**: → EMNLP, NAACL, ACL (NLP venues accept benchmarks)
- **"Framework is interesting, empirics weak"**: → Theory workshop + extended journal version

**Factor 3: Revision scope**
- **Minor revisions (< 2 weeks)**: → Quick turnaround venue (AISTATS, EACL)
- **Moderate revisions (1-2 months)**: → ICLR, ICML
- **Major revisions (3-6 months)**: → NeurIPS 2027, or journal (JMLR, TMLR)

---

### Venue Options Ranked by Fit

#### Tier 1: Primary alternatives (best fit)

**1. ICLR 2027**
- **Deadline**: Late September 2026 (~4 months post-rejection)
- **Pros**:
  - Strong theory + empirics community
  - Accepts diagnostic benchmarks
  - Merrill, Li, Dziri all publish here
  - Shorter review cycle than NeurIPS
- **Cons**:
  - More competitive than NeurIPS in recent years
  - Preprint culture means less secrecy
- **Best if**: Mixed reviews suggested "empirics need strengthening" or "reframe for ML audience"

**2. ICML 2027**
- **Deadline**: Late January 2027 (~5-6 months post-rejection)
- **Pros**:
  - Top-tier venue, comparable prestige to NeurIPS
  - Strong theory track
  - Longer revision window
- **Cons**:
  - Review quality variable
  - Very competitive (20-25% acceptance)
- **Best if**: Reviews said "solid work, minor issues" → take time to perfect

**3. NeurIPS 2027**
- **Deadline**: May 2027 (~9 months post-rejection)
- **Pros**:
  - Same venue, likely different reviewers
  - Long revision window for deep changes
  - Clear signal: "we addressed your concerns"
- **Cons**:
  - Long wait (decision August 2027)
  - Risk of similar reviews if positioning unchanged
- **Best if**: Near-miss rejection with clear action items

---

#### Tier 2: Specialized venues (strong fit for narrower scope)

**4. TMLR (Transactions on Machine Learning Research)**
- **Deadline**: Rolling (submit anytime)
- **Pros**:
  - No deadline pressure
  - Iterative review until acceptance (if work is sound)
  - Growing prestige
  - Good for work that's technically solid but not flashy
- **Cons**:
  - Lower visibility than conferences
  - Slower review process (3-6 months)
- **Best if**: Want guaranteed publication of sound work without deadline stress

**5. COLT 2027 (Conference on Learning Theory)**
- **Deadline**: February 2027
- **Pros**:
  - Perfect fit for complexity-theoretic framework
  - Reviewers will understand TC⁰/NC¹ bounds
  - High prestige in theory community
- **Cons**:
  - Empirics may be undervalued
  - Very theory-focused audience
  - 12-page limit (would need to cut empirics heavily)
- **Best if**: Reviews said "empirics are weak, theory is strong" → pivot to theory-only paper

**6. AISTATS 2027**
- **Deadline**: October 2026 (~2 months post-rejection)
- **Pros**:
  - Fast turnaround
  - Values careful empirical work with statistical rigor
  - Our bootstrap CIs + pre-registered analyses are a good fit
- **Cons**:
  - Tier 1.5 venue (below NeurIPS/ICML/ICLR)
  - Less visibility
- **Best if**: Minor revisions needed, want quick publication

---

#### Tier 3: NLP/Benchmark venues (if scope pivots)

**7. EMNLP 2027**
- **Deadline**: May 2027
- **Pros**:
  - Values benchmark contributions highly
  - LLM reasoning is core topic
  - Practical/applied focus
- **Cons**:
  - Theory will be undervalued
  - May need to reframe entirely for NLP audience
- **Best if**: Reviews said "benchmark is valuable, theory is overkill"

**8. ACL 2027 / NAACL 2027**
- **Deadlines**: January 2027 / November 2026
- **Pros/Cons**: Similar to EMNLP
- **Best if**: Pivot to benchmark-focused paper for NLP community

---

#### Tier 4: Workshops + Journals (if major rethinking needed)

**9. NeurIPS 2026 Workshop (e.g., MiLETS, Robustness)**
- **Deadline**: September 2026
- **Pros**:
  - Fast way to get feedback
  - Can present preliminary work
  - Network with community
- **Cons**:
  - Not archival (doesn't count as publication)
  - Limited visibility
- **Best if**: Want community feedback before major revision

**10. Journal of Machine Learning Research (JMLR)**
- **Deadline**: Rolling
- **Pros**:
  - No length limit (can include full proofs, all experiments)
  - High prestige
  - Thorough review process
- **Cons**:
  - Very slow (6-12 months review)
  - Less visibility than conferences in ML
- **Best if**: Major revision needed, want to write "definitive" version

---

### Decision Matrix

Use this flowchart after reading rejection feedback:

```
START: Rejected from NeurIPS 2026
  │
  ├─ Fatal flaw identified?
  │   ├─ YES → Major revision (3-6 months)
  │   │        ├─ Theoretical issue → COLT or TMLR
  │   │        └─ Empirical issue → ICML/ICLR 2027
  │   │
  │   └─ NO → Fixable issues?
  │       ├─ Minor (< 2 weeks) → AISTATS 2027 (Oct deadline)
  │       ├─ Moderate (1-2 months) → ICLR 2027 (Sep deadline)
  │       └─ Major (2-3 months) → ICML 2027 (Jan deadline)
  │
  ├─ Reviews suggested scope change?
  │   ├─ "Too theoretical" → ICML/ICLR (more empirics-friendly)
  │   ├─ "Not enough theory" → COLT or add more proofs
  │   ├─ "Benchmark is the contribution" → EMNLP/ACL
  │   └─ "Split into two papers" → Theory paper (COLT) + Empirical (ICML)
  │
  └─ Timeline preference?
      ├─ Fast publication → AISTATS or TMLR
      ├─ Same venue next year → NeurIPS 2027
      └─ Best possible venue → Take time, target ICML/ICLR
```

---

## Part 4: Revision Strategy by Concern Type

### Concern Type 1: "Theoretical rigor insufficient"

**Common manifestations**:
- "Propositions lack full proofs"
- "TC⁰ bound is informal/imprecise"
- "Relies on unproven conjectures"
- "Framework doesn't add beyond existing results"

**Diagnosis**: Reviewers wanted a theory paper, got a hybrid.

**Revision options** (pick ONE direction):

**Option A: Strengthen theory**
- Expand all proof sketches to full proofs (Appendix A)
- Add Proposition 6: formal bound on CoT budget vs. accuracy
- Cite more complexity theory results
- Add discussion of when conjectures might fail
- **Effort**: 2-3 weeks
- **Cost**: $0 (pure theory work)
- **Target venue**: COLT, ICML theory track, NeurIPS 2027

**Option B: Downplay theory**
- Move framework to appendix
- Lead with empirical findings
- Frame as "complexity-inspired taxonomy" not "formal characterization"
- **Effort**: 1 week (restructuring)
- **Cost**: $0
- **Target venue**: ICLR, EMNLP

**Option C: Split paper**
- Paper 1: "A Complexity-Theoretic Framework for LLM Reasoning Gaps" (theory-only, COLT)
- Paper 2: "ReasonGap: A Diagnostic Benchmark for LLM Reasoning" (empirics-only, ICML/EMNLP)
- **Effort**: 3-4 weeks (writing two papers)
- **Cost**: $0
- **Target venues**: COLT + ICML/EMNLP

---

### Concern Type 2: "Empirical evaluation incomplete"

**Common manifestations**:
- "Missing key models (e.g., Gemini, Claude Opus 5)"
- "Need human baseline"
- "Only 12 models, need more"
- "Missing ablation: [specific condition]"

**Diagnosis**: Reviewers want more comprehensive empirical coverage.

**Revision options**:

**Option A: Add frontier models**
- Evaluate latest models (Gemini 2.5, GPT-5, Claude Opus 5, Llama 4)
- **Effort**: 6-8 hours per model
- **Cost**: $30-100 per model (estimate $200 total for 4 models)
- **Impact**: Addresses "missing models" directly

**Option B: Add human baseline**
- Recruit 100 participants via Prolific
- Administer subset of tasks (B1-B6, 50 instances each)
- Statistical comparison with model performance
- **Effort**: 1-2 weeks (setup + data collection + analysis)
- **Cost**: $300-500 (participant payments)
- **Impact**: Strong response to "how do humans perform?" question

**Option C: Add new conditions**
- Self-consistency (sample N times, take majority vote)
- Retrieval-augmented (provide relevant examples)
- Fine-tuning (if open-source models)
- **Effort**: 1-2 weeks per condition
- **Cost**: $50-200 per condition
- **Impact**: Shows robustness of findings across methods

**Recommended**: Add 2-4 frontier models ($100-200) + one new condition ($50-100). Defer human baseline unless specifically requested by multiple reviewers.

---

### Concern Type 3: "Benchmark design flawed"

**Common manifestations**:
- "Tasks are too artificial"
- "Difficulty calibration is arbitrary"
- "Contamination risk"
- "Ground truth may be incorrect"

**Diagnosis**: Reviewers doubt whether benchmark isolates the claimed phenomena.

**Revision options**:

**Option A: Validate with real-world tasks**
- Map each gap type to existing benchmarks (GSM8K, BBH, MATH)
- Show correlations between ReasonGap performance and real-world failures
- **Effort**: 1-2 weeks
- **Cost**: $50-100 (evaluating on existing benchmarks)
- **Impact**: Addresses "artificial task" concern

**Option B: Add external validation**
- Recruit domain experts to verify task design
- Provide mathematical proofs of ground truth correctness
- **Effort**: 1 week (writing validation appendix)
- **Cost**: $0-200 (if paying experts)
- **Impact**: Increases confidence in benchmark validity

**Option C: Expand difficulty analysis**
- Add psychometric analysis (IRT models)
- Show monotonicity: harder instances → lower accuracy
- Correlate difficulty with theoretical predictions
- **Effort**: 1 week
- **Cost**: $0 (analysis only)
- **Impact**: Demonstrates systematic difficulty calibration

**Recommended**: Option A (real-world mapping) + Option C (difficulty analysis). These are low-cost and high-impact.

---

### Concern Type 4: "Positioning unclear"

**Common manifestations**:
- "How does this differ from Song et al.?"
- "Is this a theory or empirics paper?"
- "Contribution is incremental"
- "Framing is confusing"

**Diagnosis**: Reviewers couldn't quickly grasp the contribution or novelty.

**Revision options**:

**Option A: Rewrite abstract + intro**
- Lead with concrete finding: "CoT closes depth gaps but not intractability gaps"
- State contribution in one sentence
- Add "comparison to prior work" paragraph in intro
- **Effort**: 2-3 days
- **Cost**: $0
- **Impact**: High — first impression matters

**Option B: Strengthen related work**
- Add comparison table: This work vs. [Merrill 2024, Song 2026, Li 2024]
- Explicitly state what's novel in each contribution
- **Effort**: 1 week
- **Cost**: $0
- **Impact**: Directly addresses "how is this different?" question

**Option C: Add "Positioning" subsection**
- End of Section 1 (Introduction)
- Explicit paragraph: "Our work differs from X in three ways: ..."
- **Effort**: 1 day
- **Cost**: $0
- **Impact**: Makes novelty crystal clear

**Recommended**: All three (total effort: 1-2 weeks, $0 cost). Positioning is critical and costs nothing but time.

---

### Concern Type 5: "Scope too broad / too narrow"

**Common manifestations**:
- "Trying to do too much"
- "Should focus on just the benchmark"
- "Needs more depth on [specific aspect]"

**Diagnosis**: Mismatch between reviewer expectations and paper scope.

**Revision options**:

**Option A: Expand scope**
- Add more theoretical results (full proofs, tighter bounds)
- Add more empirical conditions (retrieval, fine-tuning, human baseline)
- **Effort**: 1-2 months
- **Cost**: $200-500
- **Target venue**: JMLR (no length limit)

**Option B: Narrow scope**
- Focus on 3-4 gap types instead of 6
- Drop weaker contributions (e.g., if Type 6 is least convincing)
- **Effort**: 1 week (restructuring)
- **Cost**: $0
- **Target venue**: ICML/ICLR (tighter narrative)

**Option C: Reframe without changing content**
- Change abstract/intro to set expectations correctly
- Explicitly state scope limitations in intro
- **Effort**: 2-3 days
- **Cost**: $0
- **Target venue**: Same as before

**Recommended**: Option C first (always). Only expand/narrow if multiple reviewers agree on direction.

---

### Concern Type 6: "Presentation issues"

**Common manifestations**:
- "Notation is inconsistent"
- "Figure X is unclear"
- "Results are hard to parse"
- "Too much jargon"

**Diagnosis**: Content is sound, delivery needs polish.

**Revision strategy**:
- Fix all notation issues (use notation.md as reference)
- Regenerate unclear figures with better labels
- Add summary tables for complex results
- Simplify language in abstract/intro
- **Effort**: 1-2 weeks
- **Cost**: $0
- **Impact**: Medium (won't change minds, but removes friction)

**Recommended**: Always address presentation issues — they're low-hanging fruit.

---

## Part 5: Timeline Mapping

### If rejection decision arrives: August 2026

| Venue | Deadline | Decision | Revision window | Notes |
|-------|----------|----------|-----------------|-------|
| **AISTATS 2027** | Oct 2026 | Jan 2027 | 2 months | Fast, minor revisions only |
| **ICLR 2027** | Late Sep 2026 | May 2027 | **6 weeks** | Tight but doable for moderate revisions |
| **NAACL 2027** | Nov 2026 | Mar 2027 | 3 months | If pivoting to NLP focus |
| **ICML 2027** | Late Jan 2027 | May 2027 | 5 months | Best for moderate-major revisions |
| **COLT 2027** | Feb 2027 | May 2027 | 6 months | If pivoting to theory focus |
| **ACL 2027** | Mar 2027 | Jun 2027 | 7 months | NLP venue alternative |
| **EMNLP 2027** | May 2027 | Aug 2027 | 9 months | Benchmark-focused |
| **NeurIPS 2027** | May 2027 | Aug 2027 | 9 months | Same venue, long revision window |
| **TMLR** | Rolling | 3-6 months | Anytime | No deadline pressure |
| **JMLR** | Rolling | 6-12 months | Anytime | Definitive version |

**Critical observation**: ICLR 2027 deadline is VERY tight (6 weeks post-decision). Only feasible if:
- Rejection is "near miss" with minor fixes
- All experiments/infrastructure already in place
- Only need presentation/positioning changes

For moderate-major revisions, **ICML 2027 (January deadline) is the sweet spot**: 5 months revision window, top-tier venue, good theory+empirics fit.

---

## Part 6: Budget Allocation

### Current budget status (as of March 2026)
- **Monthly budget**: $1,000
- **Spent on evaluation**: ~$465
- **Remaining**: ~$535
- **Reserved for rebuttal**: $200

### Post-rejection budget (if rejected in August)

Assume monthly $1,000 budget continues:
- **August 2026**: $1,000 available
- **September 2026**: +$1,000 = $2,000
- **October 2026**: +$1,000 = $3,000
- Etc.

**Conservative assumption**: $500/month available for revision experiments (rest reserved for infrastructure, other projects)

### Revision budget by scenario

**Scenario 1: Minor revisions (< $100)**
- Fix presentation issues
- Add 1-2 frontier models
- Regenerate figures
- **Total**: $50-100
- **Timeline**: 2 weeks
- **Target**: AISTATS or ICLR (if fast)

**Scenario 2: Moderate revisions ($100-300)**
- Add 4-6 new models
- Add 1 new condition (e.g., self-consistency)
- Real-world task mapping
- Difficulty analysis
- **Total**: $150-300
- **Timeline**: 1-2 months
- **Target**: ICML, NeurIPS 2027

**Scenario 3: Major revisions ($300-500)**
- Add frontier models
- Human baseline (Prolific study)
- Multiple new conditions
- Extended experiments (difficulty sweep, prompt variations)
- **Total**: $400-500
- **Timeline**: 2-3 months
- **Target**: ICML, JMLR, NeurIPS 2027

**Scenario 4: Scope expansion ($500-1000)**
- All of Scenario 3
- Plus: Fine-tuning experiments
- Plus: Adversarial robustness tests
- Plus: Extended theoretical work (external collaboration)
- **Total**: $600-1000
- **Timeline**: 3-6 months
- **Target**: JMLR (definitive version)

**Recommended allocation**: Reserve $300-500 for revision experiments. This covers Scenarios 1-3 comfortably.

---

## Part 7: Decision Protocol

### Week 1: Analysis & Planning

**Day 1-3**: Execute immediate response protocol (Part 1)

**Day 4-7**:
1. Complete feedback analysis document
2. Identify revision type (minor/moderate/major)
3. Estimate revision effort (weeks) and cost ($)
4. Draft venue shortlist (3-5 options)

**Output**: `reviews/NEURIPS_2026_FEEDBACK_ANALYSIS.md` + `reviews/REVISION_PLAN.md`

### Week 2: Venue Decision

**Use decision matrix (Part 3)** to select target venue.

**Key questions**:
1. How much time do we have until next deadline?
2. What's the minimum viable revision to address concerns?
3. Is venue change warranted, or should we resubmit to NeurIPS 2027?

**Decision criteria**:
- **If near-miss rejection** → Same venue next year OR fast turnaround (ICLR/AISTATS)
- **If fundamental concerns** → Scope pivot → different venue (COLT if theory, EMNLP if benchmark)
- **If mixed reviews** → Reframe positioning → overlapping venue (ICML, ICLR)

**Output**: Venue selected, revision timeline planned

### Week 3-N: Execution

Follow revision strategy (Part 4) based on concern types identified.

**Parallel tracks**:
1. **Writing**: Revise abstract, intro, related work, positioning
2. **Experiments**: Run any additional evaluations needed
3. **Theory**: Expand proofs or theoretical framework if needed

**Commit strategy**:
- Daily commits for writing changes
- Commit after each experiment completes
- Tag major milestones (e.g., `revision/v1-intro-rewrite`)

**Status tracking**: Update `status.yaml` weekly with revision progress

### Final Week: Submission Prep

**Checklist**:
- [ ] All reviewer concerns addressed (or rebutted)
- [ ] Paper compiles cleanly
- [ ] Within page limit for target venue
- [ ] References updated (any new 2026/2027 work)
- [ ] Figures regenerated if needed
- [ ] Appendix reorganized for new venue style
- [ ] Submission.zip package created
- [ ] Metadata prepared (title, abstract, keywords)

**Final verification**: Read paper end-to-end as if seeing for first time. Does it flow? Is contribution clear?

---

## Part 8: Psychological Strategy

### Mindset for rejection

**Rejection is normal in top-tier ML venues**:
- NeurIPS acceptance rate: ~25%
- ICML acceptance rate: ~20-25%
- ICLR acceptance rate: ~25-30%

**This means**: 75% of submitted papers are rejected, including many strong papers. Rejection ≠ bad paper.

**Reframe rejection as**:
- **Free expert feedback** (would cost $thousands if consulting)
- **Opportunity to improve** (published version will be stronger)
- **Routing signal** (perhaps wrong venue, not wrong paper)

**Historical examples**:
- BERT was rejected from ICLR before acceptance at NAACL
- AlexNet was rejected from NIPS before winning ImageNet
- Many Turing Award papers were initially rejected

### Emotional regulation

**Immediate reaction (Day 1)**:
- Allow yourself to feel disappointed (normal human response)
- Avoid immediate action (don't email reviewers, don't rage-revise)
- Talk to colleagues/collaborators for perspective

**Analysis phase (Days 2-7)**:
- Separate ego from paper (reviewers critique work, not you)
- Look for patterns (if 3 reviewers say X, they're probably right)
- Identify "easy wins" (low-effort, high-impact fixes)

**Revision phase (Weeks 2-N)**:
- Focus on making the paper better, not "proving reviewers wrong"
- Treat revision as craft, not combat
- Celebrate small wins (each section improved, each experiment completed)

**Resubmission**:
- Confidence that paper is now stronger
- Excitement about getting it in front of new reviewers
- Realistic expectations (still ~25% acceptance rate)

---

## Part 9: Contingency within Contingency

### What if rejected from ICLR/ICML too?

**Scenario**: Rejected from NeurIPS 2026, revised and submitted to ICML 2027, rejected again.

**Analysis questions**:
1. Are reviews consistent across venues? (Same concerns → likely valid)
2. Are reviews contradictory? (Venue mismatch → try different audience)
3. Is there a persistent fatal flaw? (May need to acknowledge limitation or change approach)

**Options**:
1. **TMLR**: Iterative review until acceptance (if work is sound)
2. **Workshop + journal**: Get community feedback via workshop, then write extended journal version
3. **Scope reduction**: Focus on strongest 1-2 contributions, cut the rest
4. **Preprint + move on**: ArXiv preprint, cite in future work, focus on next project

**Decision rule**: If rejected from 2 top-tier venues with similar concerns, likely a fundamental issue. Either:
- Address it definitively (may require substantial new work)
- Acknowledge it as limitation and target venue that values other aspects
- Move on to next project (sunk cost fallacy is real)

### What if accepted with major revisions?

**Note**: NeurIPS typically doesn't have "major revisions" — decision is binary (accept/reject). However, some venues (TMLR, journals) do.

**If this happens**:
- Follow revision requests precisely
- Don't add new content beyond what's requested
- Document all changes clearly
- Resubmit within deadline (usually 1-2 months)

---

## Part 10: Success Metrics

### How to measure revision success

**Objective metrics**:
- Acceptance at target venue (primary goal)
- Review scores improve vs. NeurIPS submission
- Fewer major concerns flagged

**Subjective metrics**:
- Paper reads more clearly
- Contribution is more obvious
- Related work positioning is sharper
- We're confident in the work (not defensive)

**Community metrics** (post-publication):
- Citations within first year
- Invited talks / workshop presentations
- Follow-up work by other groups
- Impact on practice (do people use ReasonGap benchmark?)

---

## Part 11: Checklist for Execution

When rejection decision arrives:

### Immediate (Days 1-3)
- [ ] Read all reviews without reacting
- [ ] Step away for 2-4 hours
- [ ] Re-read and extract all concerns
- [ ] Categorize concerns (fatal/major/minor/misunderstanding/preference)
- [ ] Count reviewer breakdown
- [ ] Create `NEURIPS_2026_FEEDBACK_ANALYSIS.md`

### Week 1
- [ ] Identify themes across reviews
- [ ] Classify rejection scenario (A/B/C/D from Part 2)
- [ ] Estimate revision effort (time + cost)
- [ ] Draft venue shortlist (3-5 options)
- [ ] Create `REVISION_PLAN.md`

### Week 2
- [ ] Select target venue using decision matrix
- [ ] Confirm deadline and revision window
- [ ] Allocate budget for experiments
- [ ] Plan parallel revision tracks (writing + experiments + theory)
- [ ] Update `status.yaml` with revision phase

### Weeks 3-N (Revision execution)
- [ ] Address all major concerns
- [ ] Run additional experiments if needed
- [ ] Rewrite abstract + intro if positioning issue
- [ ] Strengthen related work
- [ ] Fix presentation issues
- [ ] Daily commits + weekly status updates

### Final week
- [ ] Compile paper, check page limit
- [ ] Verify all concerns addressed
- [ ] Read end-to-end for flow
- [ ] Generate submission package
- [ ] Submit before deadline
- [ ] Document submission in `status.yaml`

### Post-submission
- [ ] Archive NeurIPS reviews + revision plan
- [ ] Create decision log in `status.yaml`
- [ ] Prepare for next review cycle
- [ ] Optional: Post preprint to ArXiv

---

## Appendix A: Template Documents

### Template: NEURIPS_2026_FEEDBACK_ANALYSIS.md

```markdown
# NeurIPS 2026 Rejection Analysis

**Decision date**: 2026-08-XX
**Overall verdict**: [Reject / Accept]
**Vote breakdown**: [e.g., 1 Weak Accept, 2 Borderline, 1 Reject]

## Meta-Reviewer Summary
[Paste meta-reviewer comments]

**Key points**:
- [Extract 3-5 key points]

## Reviewer 1
**Score**: [1-10 or categorical]
**Confidence**: [1-5]
**Summary**: [One sentence]

**Strengths**:
- [Quoted or paraphrased]

**Weaknesses**:
- [Quoted or paraphrased]

**Questions**:
- [Quoted]

**Overall assessment**: [Positive / Mixed / Negative]

## Reviewer 2
[Same structure]

## Reviewer 3
[Same structure]

## Cross-Review Analysis

### Themes (mentioned by 2+ reviewers)
1. [Theme 1, e.g., "Theoretical rigor"]
   - Reviewer 1: [specific quote]
   - Reviewer 2: [specific quote]
2. [Theme 2]
   - ...

### Outliers (mentioned by 1 reviewer only)
- [Issue mentioned only by Reviewer X]

### Contradictions
- Reviewer X said [A], but Reviewer Y said [opposite of A]

## Classification

**Rejection scenario**: [A/B/C/D from Part 2]

**Fatal flaws**: [Yes/No]
- [If yes, list them]

**Major issues** (addressable):
1. [Issue 1]
2. [Issue 2]

**Minor issues**:
- [List]

**Misunderstandings**:
- [Points where reviewers missed content in paper]

**Positive feedback** (preserve in revision):
- [What reviewers liked]

## Recommended Actions

**Priority 1** (must address):
1. [Action item]
2. [Action item]

**Priority 2** (should address):
- [Action items]

**Priority 3** (nice to have):
- [Action items]

**Estimated effort**: [X weeks]
**Estimated cost**: [$Y]
**Recommended venue**: [Venue name, deadline]
```

---

### Template: REVISION_PLAN.md

```markdown
# Revision Plan: [Target Venue]

**Source**: NeurIPS 2026 rejection
**Target venue**: [ICML 2027 / ICLR 2027 / etc.]
**Deadline**: [Date]
**Revision window**: [X weeks/months]
**Date created**: 2026-XX-XX

## Revision Scope

**Classification**: [Minor / Moderate / Major]

**Key changes needed**:
1. [Change 1]
2. [Change 2]
3. [Change 3]

## Work Breakdown

### Track 1: Writing (X weeks, $0)
- [ ] Rewrite abstract
- [ ] Rewrite introduction
- [ ] Expand related work
- [ ] Add positioning section
- [ ] Fix notation throughout
- [ ] Improve figure captions
- [ ] Proofread end-to-end

**Owner**: Writer agent
**Deadline**: [Date]

### Track 2: Experiments (X weeks, $Y)
- [ ] Evaluate 4 frontier models ($200)
- [ ] Add self-consistency condition ($50)
- [ ] Real-world task mapping ($50)
- [ ] Difficulty analysis ($0)

**Owner**: Experimenter agent
**Deadline**: [Date]

### Track 3: Theory (X weeks, $0)
- [ ] Expand Proposition 1 proof
- [ ] Expand Proposition 2 proof
- [ ] Add Proposition 6 (CoT budget bound)
- [ ] Strengthen complexity argument in Section 3

**Owner**: Theorist agent
**Deadline**: [Date]

## Timeline

| Week | Track 1 (Writing) | Track 2 (Experiments) | Track 3 (Theory) |
|------|-------------------|------------------------|-------------------|
| 1 | Abstract + intro | Model eval setup | Proof outlines |
| 2 | Related work | Run evaluations | Proposition 1 |
| 3 | Positioning | Analysis | Proposition 2 |
| 4 | Figures + tables | Integration | Proposition 6 |
| 5 | Proofread | - | Integration |
| 6 | Final polish | - | Final check |

## Budget

| Item | Cost | Priority |
|------|------|----------|
| Frontier models (4x) | $200 | High |
| Self-consistency | $50 | Medium |
| Real-world mapping | $50 | Medium |
| Human baseline | $400 | Defer |
| **Total** | **$300** | |

**Available budget**: $500
**Reserve**: $200 (for unexpected requests)

## Success Criteria

**Must have**:
- [ ] All Priority 1 reviewer concerns addressed
- [ ] Paper compiles cleanly
- [ ] Within page limit for target venue
- [ ] Contribution is clear in abstract

**Should have**:
- [ ] All Priority 2 concerns addressed
- [ ] New experiments strengthen claims
- [ ] Related work updated with 2026-2027 papers

**Nice to have**:
- [ ] Priority 3 concerns addressed
- [ ] Paper is shorter/clearer than before

## Risk Factors

1. **Timeline risk**: [e.g., "ICLR deadline is tight, only 6 weeks"]
   - Mitigation: [e.g., "Prioritize writing, defer experiments if needed"]

2. **Budget risk**: [e.g., "Frontier models may cost more than estimated"]
   - Mitigation: [e.g., "Evaluate 2 models instead of 4 if over budget"]

3. **Scope risk**: [e.g., "Reviewers may have contradictory requests"]
   - Mitigation: [e.g., "Follow majority opinion, acknowledge limitation"]

## Checkpoints

**Week 2**: Abstract + intro done, experiments launched
**Week 4**: All writing complete, experiments integrated
**Week 6**: Final polish, ready for submission

## Next Steps

1. [Immediate next action]
2. [Second action]
3. [Third action]
```

---

## Appendix B: Historical Context

### Example rejections that became landmark papers

**Example 1: "Attention Is All You Need" (Transformer paper)**
- Submitted to ICLR 2017: Rejected
- Revised and submitted to NIPS 2017: Accepted
- Now: 100,000+ citations

**Example 2: "BERT"**
- Submitted to ICLR 2019: Rejected
- Submitted to NAACL 2019: Accepted
- Now: 80,000+ citations

**Example 3: "Deep Residual Learning" (ResNet)**
- Initial submission: Met with skepticism
- Revised with better presentation: Became foundational
- Now: 150,000+ citations

**Lesson**: Many groundbreaking papers were initially rejected. Rejection doesn't mean the work is bad — often it means the presentation needs refinement or the venue match was wrong.

---

## Appendix C: Contact & Resources

### Internal resources
- **Rebuttal preparation**: `reviews/REBUTTAL_PREPARATION_GUIDE.md`
- **Submission guide**: `paper/OPENREVIEW_SUBMISSION_GUIDE.md`
- **Evaluation pipeline**: `benchmarks/experiments/`
- **Analysis pipeline**: `benchmarks/experiments/run_full_analysis.py`

### External resources
- **NeurIPS review process**: https://nips.cc/Conferences/2026/ReviewerGuidelines
- **OpenReview**: https://openreview.net/
- **ArXiv**: https://arxiv.org/ (for preprints)

### Venue deadlines (2026-2027)
- **AISTATS 2027**: October 2026
- **ICLR 2027**: Late September 2026
- **ICML 2027**: Late January 2027
- **COLT 2027**: February 2027
- **ACL 2027**: March 2027
- **NeurIPS 2027**: May 2027

[Check https://aideadlin.es/ for exact dates]

---

## Revision History

- **2026-03-22**: Initial version created (pre-submission)
- **2026-08-XX**: [Updated after receiving reviews]
- **2026-XX-XX**: [Updated after revision completion]

---

**Prepared by**: Writer Agent
**Status**: Ready for use if rejection occurs
**Next review**: After NeurIPS decision (August 2026)
