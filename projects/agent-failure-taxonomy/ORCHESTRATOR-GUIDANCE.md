# Orchestrator Guidance: Agent-Failure-Taxonomy Project

**Last Updated**: 2026-03-25
**Project Status**: Research Complete → Experimental Phase
**Confidence**: 0.8 (HIGH)

---

## Critical Information

### ✅ ALL RESEARCH WORK COMPLETE

The research phase is **100% complete** as of 2026-03-25:
- [x] Literature survey (30+ papers, 4 comprehensive notes)
- [x] Failure collection (50 instances across 7 architectures)
- [x] Taxonomy development (9 categories, 24 sub-categories, C1-C8 mapping)
- [x] Competitor analysis (Shah et al. deep-read, differentiation secure)

**There are NO remaining Researcher tasks for this project.**

---

## ❌ DO NOT DO THESE THINGS

### 1. DO NOT Assign Researcher Agent for "gap-filling"
**Why**: This caused 3 consecutive failed sessions (scores 5, 5, 15).
**Reason**: There are no gaps to fill. 50 instances is sufficient. Taxonomy is complete.
**Previous failed strategies**:
- "researcher/gap_filling" → 3 failures
- "researcher/quality_improvement" → 1 failure

### 2. DO NOT Assign Researcher Agent for "meta-review"
**Why**: Multiple meta-reviews have been done. The diagnosis is clear: phase transition needed.
**Last meta-review**: 2026-03-25 (this session)
**Outcome**: ALL research complete, move to Experimenter + Writer

### 3. DO NOT Assign Researcher Agent at all
**Exception**: ONLY if experiments reveal a genuine NEW research question not covered in existing literature.
**Otherwise**: Researcher work is done. Do not assign.

### 4. DO NOT Try to "improve" the taxonomy before experiments
**Why**: The taxonomy is theoretically grounded and ready for empirical validation.
**Improvement should come from experimental findings**, not pre-emptive theorizing.

### 5. DO NOT Worry About Competitor Paper (Shah et al. 2026)
**Status**: Analyzed, threat level LOW
**Conclusion**: Complementary (implementation vs. cognitive), ~20% overlap, novelty secure
**Our unique contributions**: C1-C8 mapping, design principles, architecture correlation
**No action needed**: Differentiation strategy clear, framing established

---

## ✅ DO THESE THINGS NEXT

### Priority 1: Assign Experimenter Agent
**Objective**: Design and implement controlled experiments

**Session 1 - Design Protocol**
```
Design experimental protocol for agent-failure-taxonomy project.
Select 3-4 frameworks (ReAct, AutoGPT, Reflexion, plan-then-execute).
Choose 6-8 high-priority failures from notes/05-taxonomy-final-structure.md.
Define success criteria for "failure reproduced" in each category.
Document in experiments/protocol.md.
```

**Session 2 - Build Infrastructure**
```
Build experiment infrastructure in src/.
Create framework wrappers with unified interface.
Implement task setup scripts for priority failures.
Add logging and failure detection utilities.
Document in experiments/setup.md.
```

**Session 3 - Run Pilot**
```
Run pilot experiments for 2-3 failures (tool fabrication, infinite loop, self-correction).
Reproduce across 2+ frameworks.
Validate taxonomy categories apply as expected.
Document results in experiments/pilot-results.md.
Update status.yaml experiments_run counter.
```

**Estimated**: 2-3 focused sessions

---

### Priority 2: Assign Writer Agent (Can Run in Parallel)
**Objective**: Draft paper sections that don't require experimental data

**Session 1 - Introduction**
```
Draft introduction section for agent-failure-taxonomy paper (ACL 2027).
Motivation: Agent deployment increasing, failures poorly documented.
Research gap: No cognitive-level taxonomy with theoretical grounding.
Contributions: 9-category taxonomy, C1-C8 mapping, design principles, architecture guidance.
Write to paper/introduction.tex (~1.5 pages).
```

**Session 2 - Related Work**
```
Draft related work section.
Position vs. Shah et al. (2026) using literature/05-competitor-deep-analysis.md.
Framing: Complementary (implementation vs. cognitive failures).
Compare to 6 taxonomies total (Shah, MAST, Three-Phase, AgentError, DEFT, Reasoning Trap).
Connect to LLM reasoning limitations.
Write to paper/related-work.tex (~2 pages).
```

**Session 3 - Partial Methodology**
```
Draft methodology section (partial).
Data collection: 50 instances, 5 sources, 7 architectures, 2023-2026.
Grounded theory: open coding → axial coding → theoretical mapping to C1-C8.
Defer experimental methodology until protocol designed.
Write to paper/methodology.tex (~1.5 pages for data + coding).
```

**Estimated**: 2-3 sessions for initial drafts

---

## Parallel Execution Strategy

### Why Parallel Works Here
- **Experimenter** needs no input from Writer (protocol design is independent)
- **Writer** can draft introduction/related work without experimental data
- **No blocking dependencies** between these tracks until Results section

### Recommended Schedule
```
Week 1:
- Session 1: Experimenter (protocol design)
- Session 2: Writer (introduction)

Week 2:
- Session 3: Experimenter (build infrastructure)
- Session 4: Writer (related work)

Week 3:
- Session 5: Experimenter (pilot experiments)
- Session 6: Writer (partial methodology)

Week 4:
- Session 7: Experimenter (full experiments if pilot succeeds)
- Session 8: Writer (results + discussion drafts after experiments)
```

**Total**: 6-8 sessions to complete draft → ~2-3 months with buffer

---

## Success Criteria

After next 3 sessions (1 Experimenter + 2 Writer or vice versa), project should have:
- ✅ Experimental protocol defined and documented
- ✅ Introduction section drafted
- ✅ Related work section drafted (or in progress)

After 6 sessions (3 Experimenter + 3 Writer):
- ✅ Infrastructure built and pilot experiments run
- ✅ Introduction, related work, methodology sections drafted
- ✅ Clear path to full experimental validation
- ✅ Results/discussion sections outlined, awaiting data

**Target confidence after 6 sessions**: 0.85-0.9

---

## Red Flags to Watch For

### 🚩 If a session scores < 40
**Check**: Was Researcher agent assigned? → If YES, this is the problem
**Fix**: Assign Experimenter or Writer instead

### 🚩 If agent reports "need more instances"
**Response**: 50 instances is sufficient for grounded theory. Do not collect more.
**Exception**: If experiments reveal a genuinely new failure mode not in taxonomy

### 🚩 If agent wants to "refine taxonomy before experiments"
**Response**: Taxonomy refinement should be driven by experimental findings, not speculation
**Action**: Proceed with experiments as designed

### 🚩 If agent is "stuck" on competitor paper
**Response**: Competitor analysis is complete (literature/05-competitor-deep-analysis.md)
**Action**: Use that document for Related Work framing, move forward

### 🚩 If multiple agents want to work on same section
**Response**: Coordinate clearly (e.g., Experimenter owns experiments/, Writer owns paper/)
**Action**: Ensure no file conflicts by clear ownership boundaries

---

## Timeline and Milestones

### Milestone 1: Experimental Protocol Complete (1 session)
- Frameworks selected
- Priority failures identified
- Success criteria defined
- **Target**: End of week 1

### Milestone 2: Introduction + Related Work Drafted (2 sessions)
- Introduction clearly states contributions
- Related Work positions vs. competitors (especially Shah et al.)
- **Target**: End of week 2

### Milestone 3: Infrastructure Built (1 session)
- Framework wrappers working
- Task setups implemented
- Logging infrastructure ready
- **Target**: End of week 2

### Milestone 4: Pilot Experiments Complete (1 session)
- 2-3 failures reproduced
- Taxonomy validation initial results
- **Target**: End of week 3

### Milestone 5: Full Draft Ready for Revision (6-8 sessions total)
- All sections drafted
- Experiments complete
- Tables/figures generated
- **Target**: End of 2-3 months

### Milestone 6: Submission Ready (10-12 sessions total)
- Revisions complete
- Multiple internal reviews
- ACL 2027 format verified
- **Target**: December 2026 (2 months before Feb 2027 deadline)

---

## Budget and Resources

**Estimated API costs**:
- Experimenter: $200-300 (framework API calls for experiments)
- Writer: $50-100 (document generation)
- Revisions: $50-100 (editing, refinement)
- **Total**: $300-500 for full paper (within monthly $1000 budget)

**External dependencies**:
- None. All agent frameworks available via pip.
- No special access needed.
- No human intervention required until final review.

---

## Frequently Asked Questions

### Q: Should we collect more failure instances?
**A**: NO. 50 is sufficient for grounded theory. More instances won't change taxonomy structure at this point.

### Q: Should we do another meta-review?
**A**: NO. Multiple meta-reviews have been done. Diagnosis is clear: assign Experimenter + Writer.

### Q: What if experiments show taxonomy needs changes?
**A**: GOOD. That's the point of empirical validation. Make data-driven refinements, document in paper.

### Q: Can Writer start before experiments finish?
**A**: YES. Introduction, related work, and methodology (data collection + coding) can all be drafted now. Only Results/Discussion need experimental data.

### Q: What about the competitor paper (Shah et al.)?
**A**: Already analyzed. Complementary, not competing. Use literature/05-competitor-deep-analysis.md for framing. No further action needed.

### Q: When should we create a PR?
**A**: After milestone completion (e.g., after pilot experiments, after first draft complete). Not needed for every session.

### Q: Should we assign Researcher if experiments find something unexpected?
**A**: ONLY if it's a genuinely new research question requiring literature survey. Most experimental surprises don't need new research, just adjustment to protocol or taxonomy refinement.

---

## Key Files for Reference

**For Experimenter**:
- `notes/05-taxonomy-final-structure.md` — Full taxonomy with priority failures
- `experiments/` — Directory for protocol, setup, results (currently empty)
- `src/` — Directory for infrastructure code (currently empty)

**For Writer**:
- `BRIEF.md` — Project goals and contributions
- `notes/05-taxonomy-final-structure.md` — Taxonomy details for introduction
- `literature/05-competitor-deep-analysis.md` — Shah et al. comparison for related work
- `notes/02-open-coding-memos.md`, `03-axial-coding-relationships.md`, `04-llm-limitation-mapping.md` — Methodology details
- `paper/` — Directory for LaTeX (currently empty, ACL 2027 format)

---

## Summary

**Current Status**: Research phase 100% complete, ready for Experimenter + Writer parallel execution

**DO**: Assign Experimenter (protocol, infrastructure, experiments) and Writer (intro, related work, methods)

**DO NOT**: Assign Researcher (all objectives met, no remaining tasks)

**Confidence**: 0.8 (HIGH) — Project on track for ACL 2027

**Timeline**: 6-8 sessions to draft, 10-12 to submission-ready (2-3 months)

**Next Session**: Experimenter (protocol design) OR Writer (introduction) — either works, can run in parallel

---

**Document Status**: Complete
**Last Updated**: 2026-03-25
