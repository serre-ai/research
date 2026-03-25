# Immediate Actionable Work Items

**Date**: 2026-03-25
**Status**: Ready to start immediately

---

## High Priority: Experimental Infrastructure (EXPERIMENTER)

### Work Item 1: Experimental Protocol Design
**Status**: Ready to start
**Agent**: Experimenter
**Estimated Effort**: 1 session
**Blockers**: None

**Tasks**:
1. Select 3-4 agent frameworks for testing
   - Recommended: ReAct (baseline), AutoGPT (autonomous), Reflexion (self-correction), Plan-then-Execute (planning)
   - Criteria: Well-documented, reproducible, representative of different architectures
2. Choose 6-8 high-priority failures from taxonomy
   - Tool fabrication (1.1) - ReAct known to exhibit this
   - Infinite loops (3.1) - AutoGPT known issue
   - Context degradation (4.3) - Long-context failure
   - Self-correction failure (5.2) - Reflexion exhibits this
   - Cascading errors (cross-cutting) - Multi-step tasks
   - Constraint hallucination (2.1) - ToT-style agents
3. Define success criteria for each failure category
   - What constitutes "reproduced"? (e.g., tool fabrication = agent calls non-existent tool)
   - Measurement approach: logs, metrics, or manual verification?
4. Design data collection format
   - Structured logs (JSON/YAML)
   - Metrics: success rate, steps to failure, recovery attempts
   - Screenshots/transcripts for qualitative analysis
5. Document in `experiments/protocol.md`

**Output**: Protocol document that subsequent sessions can follow

---

### Work Item 2: Framework Selection and Setup
**Status**: Ready after Work Item 1
**Agent**: Experimenter
**Estimated Effort**: 1 session
**Dependencies**: Protocol from Work Item 1

**Tasks**:
1. Install/configure selected frameworks
2. Create unified wrapper interface in `src/framework_wrapper.py`
   - Common methods: initialize(), step(), get_logs(), reset()
   - Handle framework-specific quirks
3. Implement task setup scripts for priority failures
   - Each priority failure gets a setup function
   - Example: `setup_tool_fabrication_task()` creates environment with many tools
4. Add logging infrastructure
   - Capture all agent actions, tool calls, observations
   - Structured format for automated analysis
5. Create failure detection utilities
   - Automated detection where possible (e.g., tool fabrication = call to undefined tool)
   - Manual verification protocol for others
6. Document setup in `experiments/setup.md`

**Output**: Working infrastructure, all frameworks testable

---

### Work Item 3: Pilot Experiments
**Status**: Ready after Work Item 2
**Agent**: Experimenter
**Estimated Effort**: 1 session
**Dependencies**: Infrastructure from Work Item 2

**Tasks**:
1. Select 2-3 failures for pilot (recommend: tool fabrication, infinite loop, self-correction failure)
2. Run each failure scenario across 2+ frameworks
3. Collect structured data: logs, metrics, observations
4. Validate taxonomy categories:
   - Does failure match category definition?
   - Are boundary criteria clear enough?
   - Any ambiguous cases?
5. Document results in `experiments/pilot-results.md`:
   - Success: Which failures reproduced as expected?
   - Surprises: Unexpected behaviors or new failure modes
   - Refinements: Needed adjustments to taxonomy or protocol
6. Update `status.yaml`: increment `experiments_run` counter

**Output**: Pilot results, validated methodology, refinements for full experiments

---

## Medium Priority: Paper Writing (WRITER)

### Work Item 4: Introduction Section
**Status**: Ready to start NOW (no blockers)
**Agent**: Writer
**Estimated Effort**: 1 session
**Blockers**: None

**Tasks**:
1. Draft motivation (0.5 pages):
   - Agent deployment increasing (AutoGPT, Claude Code, Devin, etc.)
   - Failures are systematic but poorly documented
   - Current state: scattered reports, no unified framework
   - Impact: Can't design robust agents, can't prioritize research
2. Draft research gap (0.3 pages):
   - Existing work: partial taxonomies for specific domains
   - Gap: No comprehensive taxonomy with theoretical grounding + architecture analysis
3. Draft contributions (0.4 pages):
   - 9-category hierarchical taxonomy with clear boundaries (50 instances)
   - LLM limitation mapping (C1-C8) connecting to reasoning gaps
   - Architecture-failure correlation with controlled validation
   - Design principles for robust agent architectures
4. Draft paper structure overview (0.3 pages)
5. Write to `paper/introduction.tex` (ACL 2027 format)

**Output**: Introduction section (~1.5 pages)

**Notes**: Can start BEFORE experiments complete. Introduction doesn't depend on experimental results.

---

### Work Item 5: Methodology Section (Partial)
**Status**: Ready to start NOW
**Agent**: Writer
**Estimated Effort**: 0.5 session
**Blockers**: None

**Tasks**:
1. Draft data collection subsection:
   - 50 failure instances from 5 source types
   - 2023-2026 timeframe
   - 7 architecture types
   - Inclusion/exclusion criteria
2. Draft taxonomy development subsection:
   - Grounded theory methodology
   - Open coding: 50 instances → 150 codes → 9 categories
   - Axial coding: relationships, hierarchies, boundary refinement
   - Theoretical mapping: C1-C8 LLM capability dimensions
3. Defer experimental methodology until experiments designed (Work Item 1 complete)

**Output**: Partial methodology section (~1 page)

---

## Low Priority (But Can Start): Competitor Analysis (RESEARCHER)

### Work Item 6: Deep-Read Competitor Paper
**Status**: Ready to start NOW
**Agent**: Researcher (FINAL task for this agent)
**Estimated Effort**: 1 focused session
**Blockers**: None

**Tasks**:
1. Fetch arXiv:2603.06847 "Characterizing Faults in Agentic AI" (March 2026)
2. Deep-read paper:
   - Extract all 37 categories with definitions
   - Note their methodology (385 real-world faults)
   - Identify their theoretical framework (if any)
3. Compare to our taxonomy:
   - Overlap: Which of our 9 categories correspond to their 37?
   - Differences: What do they cover that we don't? (and vice versa)
   - Granularity: Why 9 vs 37? (hierarchical structure vs flat)
4. Articulate our unique contributions:
   - Theoretical grounding (C1-C8 mapping) - do they have this?
   - Architecture correlation - do they analyze by architecture?
   - Hierarchical structure with explicit boundaries - flat or hierarchical?
   - Design principles - prescriptive or descriptive?
5. Write detailed comparison in `literature/05-competitor-deep-analysis.md`
6. Update differentiation strategy in `status.yaml`

**Output**: Competitor analysis note, clear differentiation

**Notes**:
- This is the LAST task for Researcher agent on this project
- Writer agent needs this before drafting Related Work section
- Can run in parallel with Experimenter Work Items 1-3

---

## Recommended Execution Order

### Parallel Track A (Critical Path - Experiments):
1. Work Item 1 (Experimenter) → Work Item 2 (Experimenter) → Work Item 3 (Experimenter)
   - Sequential dependency, must run in order
   - ~3 sessions total

### Parallel Track B (Paper Writing):
1. Work Item 4 (Writer) - Can start immediately
2. Work Item 5 (Writer) - Can start immediately
   - No dependencies between these two
   - ~1.5 sessions total

### Parallel Track C (Research Cleanup):
1. Work Item 6 (Researcher) - Can start immediately
   - Must complete before Related Work section (not listed above, but next Writer task)
   - 1 session

**Total estimated effort**: 5-6 sessions to complete all immediate work

**Timeline**: If running in parallel (Tracks A, B, C concurrent), could complete in ~3 session cycles

---

## What NOT to Do

❌ **Do NOT collect more failure instances**
- 50 instances is sufficient for grounded theory
- Further collection is scope creep
- Research phase is COMPLETE

❌ **Do NOT refine taxonomy further without empirical data**
- Taxonomy is "substantially complete"
- Further refinement should be driven by experimental findings
- Don't over-theorize before validation

❌ **Do NOT write Results/Discussion sections yet**
- Must wait for experiments to complete
- Introduction, Methodology (partial), Related Work can proceed now

❌ **Do NOT assign Researcher agent for general work**
- Researcher has ONE remaining task: competitor deep-read (Work Item 6)
- After that, Researcher is done with this project
- Experimenter and Writer take over

---

## Success Criteria (Next 5-6 Sessions)

After completing these work items, project should have:

✅ Experimental protocol designed and documented
✅ Infrastructure built and tested across 3-4 frameworks
✅ 2-3 pilot experiments completed with results documented
✅ Competitor analysis complete with clear differentiation
✅ Introduction section drafted (~1.5 pages)
✅ Methodology section partially drafted (~1 page)
✅ Clear path to full experimental validation (remaining 4-6 experiments)
✅ Clear path to paper completion (Related Work, Results, Discussion sections)

**Project confidence**: Should increase from 0.7 to 0.85+ after these work items

**Timeline to submission**: On track for ACL 2027 (Feb 2027) if this work completes in next 2-3 weeks
