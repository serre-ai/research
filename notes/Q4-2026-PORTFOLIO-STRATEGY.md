# Q4 2026 Research Portfolio Strategy
**Date**: 2026-03-22
**Planning Period**: Q2 2026 (current) through Q1 2027
**Prepared by**: Researcher Agent

## Executive Summary

**Current State**: 5 active projects, 1 in final sprint (reasoning-gaps → NeurIPS 2026 May 6), 3 in early stages (theory papers), 1 infrastructure project.

**Critical Deadline**: NeurIPS 2026 paper deadline is **44 days away** (May 6, 2026). One project (reasoning-gaps) is nearly submission-ready. Two other projects target this deadline but are early-stage.

**Key Decisions**:
1. **CONTINUE** reasoning-gaps → NeurIPS 2026 (high probability)
2. **PIVOT** verification-complexity from NeurIPS 2026 → ICLR 2027 (insufficient time)
3. **CONTINUE** self-improvement-limits → ICLR 2027 (appropriate timeline)
4. **CONTINUE** agent-failure-taxonomy → ACL 2027 (survey paper, good fit)
5. **KILL** platform-engineering as research project (move to ops/maintenance)

**Q4 Resource Allocation**:
- Primary focus: reasoning-gaps submission + ICML 2027 / ACL 2027 pipeline
- Budget: $645 remaining in March, $1,000/month for Q2-Q4
- Target: 2 top-venue submissions in Q2 (NeurIPS), 3 in Q4 (ICLR + ACL)

---

## Project-by-Project Analysis

### 1. reasoning-gaps → NeurIPS 2026
**Status**: submission-prep (80% complete)
**Target Venue**: NeurIPS 2026 (deadline: May 6, 44 days)
**Decision**: **CONTINUE** (highest priority)

**Rationale**:
- Literature review complete (90+ papers)
- Formal framework complete (6-type taxonomy, 5 propositions with proofs)
- Benchmark complete (9 tasks, ReasonGap suite)
- Empirical evaluation complete (12 models, 159K instances, $355 spent)
- Tool-use and budget-sweep evals running on VPS (~$35 additional)
- Paper draft exists, updated for 12-model results

**Remaining Work** (estimated 2-3 weeks):
1. Integrate tool-use and budget-sweep results (2-3 days)
2. NeurIPS submission polish: anonymization, page check, proofread (3-4 days)
3. Pre-submission self-review and revision (3-5 days)
4. Supplementary materials preparation (code, appendix) (2-3 days)
5. arXiv preparation for post-submission (1-2 days)

**Budget**: $35 remaining for current evals, $0 additional needed for submission.

**Risk Assessment**: **Low**
- Completion probability: 95%
- Novelty risk: Low (comprehensive framework + empirical validation, no close concurrent work)
- Acceptance probability: 60-70% (strong theory-practice bridge, comprehensive evaluation)

**Next Steps**:
- Check VPS eval status (tool-use, budget-sweep)
- Download results when complete
- Integrate into paper + regenerate figures
- Final submission sprint (April 25-May 5)

---

### 2. self-improvement-limits → ICLR 2027
**Status**: drafting (40% complete)
**Target Venue**: ICLR 2027 (deadline: October 2026, ~6.5 months)
**Decision**: **CONTINUE**

**Rationale**:
- Strong theoretical contribution (impossibility results, fixed-point theory)
- Complements reasoning-gaps (forms "theoretical trilogy")
- Literature survey in progress (100 papers reviewed across 4 sessions)
- Full paper draft exists (v0.1, theorems stated with proof sketches)
- Timeline to ICLR 2027 is appropriate (6.5 months)

**Remaining Work** (estimated 3-4 months):
1. **Theorist**: Verify/prove all theorems rigorously (8-12 sessions)
   - Fixed-point convergence theorem
   - GV-gap ceiling theorem with explicit f(g_D)
   - Self-play conditions theorem
   - Initial condition dependence theorem
   - Uniqueness conditions characterization
2. **Experimenter**: Toy validation experiments (optional, 2-3 weeks)
   - Demonstrate fixed-point convergence empirically
   - Validate GV-gap predictions on controlled tasks
3. **Writer**: Revision based on Theorist proofs (2-3 weeks)
4. **Critic**: Full review before submission (1-2 weeks)

**Budget**: Minimal (theory paper, small validation experiments ~$50-100)

**Risk Assessment**: **Medium-High**
- Completion probability: 65% (proof difficulty is uncertain)
- Novelty risk: Low (surveys found gaps our work should fill)
- Acceptance probability: 50-60% (theory papers are high-variance)

**Mitigation Strategy**:
- Set 3-week checkpoint for Theorist (May 15): if proofs are stuck, pivot to empirical characterization
- NeurIPS 2026 backup if scope reduces
- Workshop fallback (NeurIPS workshops Sept 2026)

**Next Steps**:
- Theorist session: rigorous proof development starting with monotone convergence
- Coordinate with Researcher notes (03-self-training-convergence-proof-strategy.md has detailed roadmap)

---

### 3. verification-complexity → ICLR 2027
**Status**: research (5% complete)
**Original Target**: NeurIPS 2026 (deadline: May 6, 44 days)
**Decision**: **PIVOT** to ICLR 2027 (October deadline)

**Rationale for Pivot**:
- Only 44 days to NeurIPS deadline
- Project is 5% complete (just initialized, no literature survey yet)
- Theory paper requiring: extensive literature survey (3 weeks), formal framework (4-6 weeks), theorem development + proofs (6-8 weeks), writing (2-3 weeks) = 15-20 weeks minimum
- NeurIPS timeline is infeasible
- ICLR 2027 (October, 6.5 months) is appropriate for this scope

**Pivoted Plan**:
- Target: ICLR 2027 (October 2026 deadline)
- Phase 1 (April-May): Literature survey on complexity theory, verification systems, interactive proofs
- Phase 2 (June-July): Formal framework development, theorem statements
- Phase 3 (August-Sept): Proof development, writing, revision
- Phase 4 (Sept-Oct): Critic review, submission polish

**Work Estimate** (4-5 months):
1. Literature survey (3-4 weeks): IP, PCP, verification complexity, LLM verification methods
2. Formal framework (4-5 weeks): verification complexity hierarchy, gap collapse conditions
3. Theorem development + proofs (6-8 weeks): main impossibility results
4. Empirical validation (2-3 weeks, optional): controlled experiments on existing benchmarks (~$100)
5. Writing + revision (3-4 weeks)
6. Critic review (1-2 weeks)

**Budget**: $100-150 (minimal empirical validation)

**Risk Assessment**: **High**
- Completion probability: 50% (ambitious theory project, proof difficulty uncertain)
- Novelty risk: Medium (need to differentiate from classical complexity theory)
- Acceptance probability: 45-55% (theory papers, high variance)

**Mitigation**:
- Start immediately after reasoning-gaps submission (mid-May)
- Set monthly checkpoints
- NeurIPS 2026 workshop backup if full paper doesn't converge
- Can narrow scope to core theorems if needed

**Next Steps**:
- **DEFER** until reasoning-gaps submitted
- Post-NeurIPS: Researcher begins literature survey (interactive proofs, PCP, verification complexity)

---

### 4. agent-failure-taxonomy → ACL 2027
**Status**: research (10% complete)
**Target Venue**: ACL 2027 (deadline: February 2027, ~11 months)
**Decision**: **CONTINUE** (low priority until Q3)

**Rationale**:
- Survey paper: lower risk, high completion probability
- ACL 2027 timeline is generous (11 months)
- Diversifies portfolio (empirical survey vs. theory papers)
- Relevant to platform improvement (feeds back into Deepwork development)
- Different research area (agent architectures vs. reasoning/theory)

**Work Estimate** (2-3 months active work):
1. Literature survey (4-5 weeks): agent papers 2023-2026, failure documentation
2. Failure instance collection (3-4 weeks): GitHub issues, blog posts, demonstrations
3. Grounded theory coding (4-5 weeks): open coding → taxonomy development
4. Controlled experiments (2-3 weeks): reproduce failures across frameworks
5. Writing + revision (3-4 weeks)

**Budget**: $50-100 (minimal API calls for agent demonstrations)

**Risk Assessment**: **Low**
- Completion probability: 85% (survey papers rarely fail to complete)
- Novelty risk: Low (gap in literature confirmed)
- Acceptance probability: 65-75% (ACL accepts taxonomy/survey papers)

**Timeline Strategy**:
- **Phase 1** (May-June): Literature survey during post-NeurIPS downtime
- **Phase 2** (July-Sept): Failure collection + coding
- **Phase 3** (Oct-Nov): Controlled experiments
- **Phase 4** (Dec-Jan): Writing + revision
- **Phase 5** (Feb): Submission

**Next Steps**:
- **DEFER** active work until May (post-NeurIPS)
- Low-priority background work: collect agent failure examples as encountered

---

### 5. platform-engineering → Operations
**Status**: active (infrastructure maintenance)
**Decision**: **KILL** as research project, **CONTINUE** as operations

**Rationale**:
- Not a research project (no paper output)
- Belongs in operational category alongside VPS maintenance
- Current status: "Idle — no open backlog tickets"
- Should be handled by platform maintenance, not research portfolio

**Action**:
- Remove from active research project portfolio
- Move to operations/infrastructure tracking
- Handle backlog tickets as they arise (on-demand)
- Budget: already accounted for in fixed infrastructure costs ($455.50/month subscriptions)

---

## Conference Deadline Calendar

### Q2 2026 (April-June)
| Deadline | Venue | Target Projects | Priority |
|----------|-------|----------------|----------|
| **May 6** | **NeurIPS 2026** | reasoning-gaps | **P0 (CRITICAL)** |
| June 15 | EMNLP 2026 | (none) | - |

### Q3 2026 (July-September)
| Deadline | Venue | Target Projects | Priority |
|----------|-------|----------------|----------|
| Aug 15 | AAAI 2027 | (none - too early) | - |
| Sept 15 | NeurIPS Workshops | (backup for any project) | P2 (backup) |

### Q4 2026 (October-December)
| Deadline | Venue | Target Projects | Priority |
|----------|-------|----------------|----------|
| **Oct 1** | **ICLR 2027** | self-improvement-limits, verification-complexity | **P1 (HIGH)** |

### Q1 2027 (January-March)
| Deadline | Venue | Target Projects | Priority |
|----------|-------|----------------|----------|
| **Jan 30** | **ICML 2027** | (new empirical project TBD) | **P1** |
| **Feb 15** | **ACL 2027** | agent-failure-taxonomy | **P1** |

---

## ICML 2027 Planning (January Deadline)

**Timeline**: 10 months from now
**Target**: 1 empirical paper
**Budget**: $300-400

**Project Selection Criteria**:
- Fast execution (2-3 months active work)
- High completion probability (empirical, not theory)
- Leverages existing infrastructure (ReasonGap benchmark, analysis pipeline)
- Differentiates from reasoning-gaps (don't retread same ground)

**Top Candidates from Backlog**:

### Option A: cot-faithfulness-audit (Score: 3.95)
**Pros**:
- Direct complement to reasoning-gaps (shares framework)
- Reuses ReasonGap benchmark + analysis pipeline
- Clear empirical methodology
- High impact (CoT faithfulness is widely relevant)
- Fast timeline (3 months estimated)

**Cons**:
- May feel incremental relative to reasoning-gaps
- Needs differentiation angle

**Recommendation**: **Strong candidate**. Start September 2026, submit January 2027.

### Option B: scaling-emergence-thresholds (Score: 4.00)
**Pros**:
- Extends reasoning-gaps into scaling dimension
- High novelty + impact
- Topical (emergence debate is active)

**Cons**:
- Requires access to model scale series (expensive or need partnerships)
- 3-month timeline might be tight
- Higher risk than Option A

**Recommendation**: **Consider** if we can secure model access partnerships, otherwise defer.

### Option C: context-window-utilization (Score: 3.75)
**Pros**:
- Empirical, fast (2 months)
- Highly practical
- Different from reasoning-gaps (avoids overlap)

**Cons**:
- Lower novelty score
- May be better suited for EMNLP/ACL than ICML

**Recommendation**: **Backup option** for EMNLP 2026 (June deadline) or ACL 2027.

**Decision**: Start planning **cot-faithfulness-audit** in August 2026 for ICML 2027 submission.

---

## ACL 2027 Planning (February Deadline)

**Timeline**: 11 months from now
**Target**: 1-2 papers (1 confirmed, 1 optional)

### Confirmed: agent-failure-taxonomy
- Survey paper, low risk, good ACL fit
- See detailed analysis in Section 4 above

### Optional: context-window-utilization
- If reasoning-gaps generates bandwidth in Q3
- Empirical study, NLP-adjacent
- 2-month timeline, low cost ($100-150)
- Could start November, submit February

**Recommendation**:
- Primary: agent-failure-taxonomy (committed)
- Secondary: context-window-utilization (opportunistic, if bandwidth available)

---

## Resource Allocation Plan

### Budget Breakdown (March-December 2026)

**Fixed Costs** (monthly):
- Claude Code Max: $400/month × 10 months = $4,000
- Hetzner VPS: $5.50/month × 10 months = $55
- Firecrawl API: $50/month × 10 months = $500
- **Total Fixed**: $4,555

**Variable Research Budget**:
- Monthly allocation: $1,000/month
- Total Q2-Q4: $1,000 × 10 months = $10,000
- Already spent (March): $355 (reasoning-gaps)
- **Remaining**: $645 (March) + $10,000 (Apr-Dec) = **$10,645**

**Per-Project Allocation**:

| Project | Phase | Budget | Timeline |
|---------|-------|--------|----------|
| reasoning-gaps | Submission | $35 (eval completion) | April-May |
| self-improvement-limits | Theory development | $100 (validation) | May-Sept |
| verification-complexity | Theory development | $150 (validation) | May-Sept |
| agent-failure-taxonomy | Survey + experiments | $100 (demos) | May-Jan |
| cot-faithfulness-audit | Empirical eval | $400 (models + evals) | Aug-Dec |
| context-window-utilization | Empirical eval (optional) | $150 | Nov-Jan |
| **Contingency** | - | $200 | - |
| **Total Allocated** | - | **$1,135** | - |

**Remaining Unallocated**: $10,645 - $1,135 = **$9,510**

**Reserve Strategy**:
- Keep $2,000 as emergency reserve
- Remaining $7,500 available for:
  - New projects starting Q3-Q4
  - Expanded experiments if results warrant
  - Additional empirical projects for ICML/ACL pipeline
  - Conference travel (if papers accepted)

### Time Allocation (Agent Sessions)

**Q2 2026 (April-June)**:
- 90% reasoning-gaps (final sprint + submission)
- 10% self-improvement-limits (Theorist proof development begins)

**Q3 2026 (July-Sept)**:
- 40% self-improvement-limits (Theorist + Writer)
- 30% verification-complexity (Researcher + Theorist)
- 20% agent-failure-taxonomy (Researcher survey)
- 10% cot-faithfulness-audit (planning + scoping)

**Q4 2026 (Oct-Dec)**:
- 30% self-improvement-limits (final sprint → ICLR)
- 30% verification-complexity (final sprint → ICLR)
- 25% cot-faithfulness-audit (execution → ICML)
- 15% agent-failure-taxonomy (coding + experiments)

**Q1 2027 (Jan-Mar)**:
- 40% agent-failure-taxonomy (writing + submission → ACL)
- 30% cot-faithfulness-audit (writing + submission → ICML)
- 20% reasoning-gaps (if accepted: camera-ready, blog post, release)
- 10% new project scoping (for next cycle)

---

## Portfolio Metrics & Success Criteria

### Annual Targets (Year 1: March 2026 - March 2027)

| Metric | Target | Stretch | Current Progress |
|--------|--------|---------|------------------|
| Papers submitted to top venues | 8 | 12 | 0 (reasoning-gaps in progress) |
| Papers accepted at top venues | 3 | 5 | 0 |
| Workshop papers submitted | 4 | 6 | 0 |
| arXiv preprints posted | 8 | 12 | 0 |
| Open-source releases | 3 | 5 | 0 (ReasonGap ready) |

**Projected Submissions (March 2026 - March 2027)**:

| Quarter | Venue | Project | Status |
|---------|-------|---------|--------|
| Q2 2026 | NeurIPS 2026 | reasoning-gaps | On track |
| Q4 2026 | ICLR 2027 | self-improvement-limits | Planned |
| Q4 2026 | ICLR 2027 | verification-complexity | Planned |
| Q1 2027 | ICML 2027 | cot-faithfulness-audit | Planned |
| Q1 2027 | ACL 2027 | agent-failure-taxonomy | Planned |
| Q1 2027 | ACL 2027 (optional) | context-window-utilization | Optional |

**Total**: 5 confirmed submissions, 1 optional = **5-6 top-venue papers in Year 1**

**Gap to Target**: Need 2-3 additional projects in Q3-Q4 to hit 8 submission target.

### Risk-Adjusted Forecast

**Probability-Weighted Acceptances**:
- reasoning-gaps @ NeurIPS: 65% × 1 = 0.65
- self-improvement-limits @ ICLR: 55% × 1 = 0.55
- verification-complexity @ ICLR: 50% × 1 = 0.50
- cot-faithfulness-audit @ ICML: 60% × 1 = 0.60
- agent-failure-taxonomy @ ACL: 70% × 1 = 0.70
- **Expected acceptances**: **3.0**

**Meets target of 3 acceptances.** Stretch goal (5) requires higher success rate or more submissions.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| reasoning-gaps rejected at NeurIPS | 30-40% | High | ICLR 2027 resubmit; already strong work |
| Self-improvement-limits proofs don't close | 35% | High | Pivot to empirical characterization; workshop backup |
| Verification-complexity timeline slips | 40% | Medium | NeurIPS workshops; ICML 2027 backup |
| Budget overrun from evals | 20% | Medium | Hard caps enforced; $9,510 reserve available |
| Concurrent work scoops contribution | 15% | High | Daily arXiv monitoring; differentiation via depth |
| Agent session inefficiency | 25% | Medium | Quality gates; self-review before phase transitions |

---

## Strategic Recommendations

### Immediate Actions (Next 2 Weeks)

1. **reasoning-gaps**: Check VPS eval status, integrate results, begin submission prep
2. **Portfolio**: Commit to Q4 plan (ICLR × 2, ICML × 1, ACL × 1)
3. **Budget**: Approve allocations ($1,135 committed, $9,510 reserve)
4. **Backlog**: Add cot-faithfulness-audit to active project pipeline (start date: Aug 2026)

### Phase Gates (Checkpoints)

**May 15, 2026**: Post-NeurIPS Review
- reasoning-gaps submitted?
- self-improvement-limits proof progress check (go/pivot decision)
- Launch verification-complexity literature survey

**August 1, 2026**: Q3 Portfolio Review
- ICLR project progress (on track for October?)
- Launch cot-faithfulness-audit scoping
- agent-failure-taxonomy survey status

**October 15, 2026**: Pre-ICLR Review
- ICLR submissions complete?
- ICML/ACL projects on track?
- Budget review (50% of year elapsed)

**January 15, 2027**: Year-End Review
- ICML/ACL submissions status
- Acceptance outcomes (reasoning-gaps, ICLR projects)
- Year 1 metrics vs. targets
- Year 2 portfolio planning

---

## Conclusion

**Portfolio Health**: **Strong**

- 1 near-complete project (reasoning-gaps) with high submission probability
- 4 active projects with staggered timelines across 3 venues
- Budget is healthy ($10,645 available vs. $1,135 committed)
- Portfolio is diversified: 2 theory (SIL, VC), 1 empirical (CoT), 1 survey (AFT), 1 benchmark (RG)
- Timeline is realistic: no overcommitments, appropriate phase spacing

**Key Success Factors**:
1. Deliver reasoning-gaps to NeurIPS (44 days, P0)
2. Make go/pivot decision on self-improvement-limits proofs by May 15
3. Maintain discipline on budget caps ($200-400 per empirical project)
4. Start ICML pipeline (cot-faithfulness-audit) in August
5. Execute quality gates between project phases

**Next Session**: Return to reasoning-gaps final sprint (integrate VPS evals, submission prep).
