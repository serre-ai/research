# Agent Assignment Recommendations for Agent-Failure-Taxonomy

**Date**: 2026-03-25
**Context**: Phase transition from Research → Experimental

---

## Current Status Summary

✅ **Research Phase COMPLETE**
- 50 failure instances collected and coded
- 9-category hierarchical taxonomy with 24 sub-categories
- Theoretical grounding: 8 LLM capability dimensions (C1-C8)
- Dual-view structure (symptom-based + cause-based)
- 6 design principles derived

❌ **Experimental Phase NOT STARTED**
- No experiment infrastructure (`src/` and `experiments/` empty)
- No controlled reproductions across frameworks
- Architecture-failure correlations remain qualitative

❌ **Paper Writing NOT STARTED**
- `paper/` directory empty
- Introduction and related work can begin now
- Competitor deep-read needed before Related Work section

---

## Recommended Agent Assignments (Next 5 Sessions)

### Session 1: EXPERIMENTER AGENT
**Objective**: Design experimental protocol and select frameworks

**Prompt**:
```
Design controlled experiment protocol for agent-failure-taxonomy project.
Tasks:
1. Select 3-4 agent frameworks (recommend: ReAct, AutoGPT, Reflexion, simple plan-then-execute)
2. Choose 6-8 high-priority failures from taxonomy (1-2 per major category)
3. Define "failure reproduced" success criteria for each category
4. Design data collection format (structured logs, metrics, screenshots)
5. Document protocol in experiments/protocol.md

Read notes/05-taxonomy-final-structure.md for the 9 categories and priority failures.
```

**Expected Output**: Experimental protocol document, framework selection rationale

---

### Session 2: EXPERIMENTER AGENT
**Objective**: Build experiment infrastructure

**Prompt**:
```
Build experiment infrastructure for agent-failure-taxonomy controlled experiments.
Tasks:
1. Create src/ directory structure
2. Implement framework wrappers (unified interface for ReAct, AutoGPT, etc.)
3. Write task/environment setup scripts for priority failures
4. Implement logging utilities and data collection
5. Add failure detection automation where possible
6. Document setup in experiments/setup.md

Use protocol from experiments/protocol.md. Target frameworks: [from Session 1].
```

**Expected Output**: Working infrastructure in `src/`, setup documentation

---

### Session 3: EXPERIMENTER AGENT
**Objective**: Run pilot experiments

**Prompt**:
```
Run pilot experiments to validate taxonomy and infrastructure.
Tasks:
1. Select 2-3 well-documented failures from taxonomy (suggest: tool fabrication, infinite loop, self-correction failure)
2. Reproduce each failure across 2+ frameworks
3. Validate that taxonomy categories apply as expected
4. Document results in experiments/pilot-results.md
5. Note any surprises (failures that don't reproduce, new failure modes observed)
6. Update status.yaml with experiments_run count

Use infrastructure from src/. Record structured logs and metrics.
```

**Expected Output**: Pilot experiment results, validation of taxonomy applicability

---

### Session 4: RESEARCHER AGENT (Final Research Task)
**Objective**: Deep-read competitor paper for differentiation strategy

**Prompt**:
```
Deep-read competitor paper and write detailed comparison.
Tasks:
1. Fetch and read arXiv:2603.06847 "Characterizing Faults in Agentic AI" (March 2026)
2. Extract their 37-category taxonomy structure
3. Compare to our 9-category hierarchical taxonomy (read notes/05-taxonomy-final-structure.md)
4. Identify: overlap, differences, our unique theoretical contributions
5. Write detailed comparison in literature/05-competitor-deep-analysis.md
6. Update differentiation strategy in status.yaml

This is the FINAL researcher task. Do NOT attempt to collect more failure instances.
```

**Expected Output**: Competitor analysis note, updated differentiation strategy

---

### Session 5: WRITER AGENT
**Objective**: Draft introduction section

**Prompt**:
```
Draft introduction section for agent-failure-taxonomy paper (ACL 2027 format).
Tasks:
1. Motivation: Why agent failures matter (deployment risks, poor documentation, systematic patterns)
2. Research gap: No comprehensive taxonomy with theoretical grounding + architecture analysis
3. Contributions:
   - 9-category hierarchical taxonomy with clear boundaries
   - LLM limitation mapping (C1-C8) bridging to reasoning gaps
   - Architecture-failure correlation with controlled validation
   - Design principles for robust agents
4. Paper structure overview
5. Write to paper/introduction.tex

Read BRIEF.md for goals, notes/05-taxonomy-final-structure.md for taxonomy details.
Target length: ~1.5 pages.
```

**Expected Output**: Introduction section in LaTeX

---

## Agent Assignments NOT to Use

❌ **DO NOT**: Assign "Researcher / gap_filling"
- Reason: Research phase complete, 50 instances sufficient
- This strategy caused 3 consecutive failed sessions (scores 5, 5, 15)
- Taxonomy development done, no more instances needed

❌ **DO NOT**: Assign "Researcher / anything except competitor deep-read"
- Reason: Researcher work is complete except one specific task (Session 4 above)
- Researcher agent should NOT design experiments, write paper, or collect more data

---

## Parallel Work Opportunities

Sessions 1-3 (Experimenter) can run in sequence, while Session 4 (Researcher) and Session 5 (Writer) can run in parallel or after Session 1.

**Recommended sequence**:
1. Session 1 (Experimenter) - Design protocol
2. Sessions 2-3 (Experimenter) - Build infrastructure and run pilots
3. Session 4 (Researcher) + Session 5 (Writer) - In parallel
4. Session 6+ (Writer) - Continue drafting (methods, related work, results)

---

## Success Metrics

After these 5 sessions, project should have:
- ✅ Experimental protocol defined
- ✅ Infrastructure built and tested
- ✅ 2-3 pilot experiments completed
- ✅ Competitor differentiation clearly articulated
- ✅ Introduction section drafted
- ✅ Clear path to full experimental validation and paper completion

**Estimated time to full draft**: 8-10 additional sessions (3-4 Experimenter for full experiments, 4-6 Writer for remaining sections)

---

## Critical Notes for Orchestrator

1. **Phase transition is the key insight**: Project was not stuck—it just needed the right agent for the next phase

2. **Confidence increased**: From 0.5 to 0.7 after this meta-review

3. **Project viability**: High (8/10). Taxonomy is well-developed, theoretically grounded, and ready for validation

4. **ACL 2027 timeline**: ~11 months to deadline. On track if experimental phase starts now.

5. **Directory structure fixed**: Notes were in nested `projects/.../projects/.../` path—now corrected

6. **No blockers identified**: All resources available, no external dependencies, clear path forward
