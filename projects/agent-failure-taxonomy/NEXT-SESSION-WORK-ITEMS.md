# Next Session Work Items: Concrete, Ready-to-Execute Tasks

**Date**: 2026-03-25
**Status**: Research complete, ready for experiments and writing

---

## Option A: EXPERIMENTER AGENT (Priority 1)

### Session 7: Design Experimental Protocol

**Objective**: Create complete experimental protocol for validating the 9-category taxonomy

**Input Files to Read**:
1. `notes/05-taxonomy-final-structure.md` - Full taxonomy with 9 categories and 24 sub-categories
2. `BRIEF.md` - Methodology section for experimental approach
3. `status.yaml` progress.controlled_experiments - Priority failures already identified

**Tasks**:

1. **Framework Selection** (30 min)
   - Review and select 3-4 agent frameworks for experiments
   - Recommended: ReAct, AutoGPT, Reflexion, plan-then-execute
   - Document selection rationale (coverage of architecture types)

2. **Failure Prioritization** (45 min)
   - Choose 6-8 high-priority failures from taxonomy (1-2 per major category)
   - Priority failures already identified in status.yaml:
     - Tool fabrication (1.1)
     - Infinite loops (3.1)
     - Context degradation (4.3)
     - Self-correction failure (5.2)
     - Cascading errors (cross-cutting)
   - Add 1-3 more for coverage

3. **Success Criteria Definition** (30 min)
   - Define what "failure reproduced" means for each category
   - Specify measurable outcomes
   - Document edge cases

4. **Task Design** (45 min)
   - Design concrete tasks that should trigger each failure type
   - Specify environment setup for each task
   - Document expected agent behavior vs. actual failure

5. **Infrastructure Planning** (30 min)
   - Outline needed components for src/:
     - Framework wrappers (unified interface)
     - Task setup scripts
     - Logging utilities
     - Failure detection automation
   - Document dependencies and installation requirements

6. **Write Protocol Document** (30 min)
   - Save everything to `experiments/protocol.md`
   - Include: frameworks, failures, tasks, success criteria, infrastructure
   - Add clear next steps for Session 8 (infrastructure build)

**Deliverable**: `experiments/protocol.md` (complete experimental protocol)

**Estimated Time**: 3-4 hours
**Expected Score**: 75-90
**Value**: Unblocks empirical validation (critical path to publication)

---

## Option B: WRITER AGENT (Can run parallel to Experimenter)

### Session 7: Draft Introduction Section

**Objective**: Write introduction section for ACL 2027 paper

**Input Files to Read**:
1. `BRIEF.md` - Research goals, contributions, motivation
2. `notes/05-taxonomy-final-structure.md` - Taxonomy overview for contributions
3. `literature/05-competitor-deep-analysis.md` - For framing vs. existing work

**Tasks**:

1. **Motivation Paragraph** (30 min)
   - LLM agents deployed in complex settings (ReAct, AutoGPT, etc.)
   - Systematic failures poorly documented and understood
   - Individual reports exist but no comprehensive taxonomy
   - Without taxonomy: can't design robust agents or prioritize research

2. **Research Gap Paragraph** (30 min)
   - Existing taxonomies: implementation-level (Shah et al.) vs. our cognitive-level
   - No taxonomy with theoretical grounding (LLM capability mapping)
   - No architecture-failure correlation analysis
   - No design principles derived from failure patterns

3. **Contributions Paragraph** (45 min)
   - C1: 9-category hierarchical taxonomy (24 sub-categories)
   - C2: Grounded theory methodology with 50 instances
   - C3: C1-C8 LLM limitation mapping (cognitive foundations)
   - C4: 6 design principles for robust agents
   - C5: Architecture-failure correlation analysis
   - C6: Distinction of fundamental vs. correctable failures
   - C7: Reproducible failure dataset for community
   - C8: Complementary to Shah et al. (cognitive vs. implementation)

4. **Paper Structure Preview** (15 min)
   - Section 2: Related work (6 taxonomies, LLM reasoning limitations)
   - Section 3: Methodology (data collection, grounded theory, experiments)
   - Section 4: Taxonomy (9 categories with examples)
   - Section 5: LLM limitation mapping (C1-C8 framework)
   - Section 6: Architecture analysis (failure distribution)
   - Section 7: Design principles and mitigation strategies
   - Section 8: Discussion and limitations

5. **Format in ACL 2027 LaTeX** (30 min)
   - Use ACL template structure
   - Proper citations to key papers
   - ~1.5 pages total
   - Save to `paper/introduction.tex`

**Deliverable**: `paper/introduction.tex` (complete introduction section)

**Estimated Time**: 2-3 hours
**Expected Score**: 70-85
**Value**: Paper writing begins (critical path to publication)

---

### Session 8 (Writer continuation): Draft Related Work

**Input Files**:
1. `literature/` - All 5 literature notes (129KB surveyed work)
2. `literature/05-competitor-deep-analysis.md` - Shah et al. framing

**Structure**:
1. **Agent Frameworks** - ReAct, AutoGPT, Voyager, etc. (context)
2. **Existing Taxonomies** - Compare to 6 identified taxonomies
   - Shah et al. (2026): implementation faults vs. our cognitive failures
   - MAST (2025): multi-agent vs. our single-agent
   - Others: show gaps our work fills
3. **LLM Reasoning Limitations** - Connect to broader reasoning research
4. **Positioning** - Emphasize complementarity, not competition

**Deliverable**: `paper/related-work.tex`

**Estimated Time**: 3-4 hours
**Expected Score**: 75-85

---

### Session 9 (Writer continuation): Draft Methodology

**What can be written NOW**:

1. **Data Collection** (ready)
   - 50 failure instances
   - 5 source types (papers, blog posts, GitHub, public demos, benchmarks)
   - 7 agent architectures represented
   - Source selection criteria
   - Instance documentation format

2. **Grounded Theory Analysis** (ready)
   - Phase 1: Open coding (150 codes → 9 patterns)
   - Phase 2: Axial coding (5 relationship types, boundary refinement)
   - Phase 3: Theoretical mapping (C1-C8 connection)
   - Validation approach

3. **Taxonomy Development Process** (ready)
   - Iterative refinement
   - Inter-category boundary criteria
   - Sub-category development
   - Architecture correlation matrix

**What CANNOT be written yet**:

4. **Experimental Methodology** (awaiting Session 7 Experimenter protocol)
   - Framework selection → Needs protocol
   - Task design → Needs protocol
   - Failure reproduction procedure → Needs protocol
   - Success criteria → Needs protocol

**Deliverable**: `paper/methodology.tex` (Sections 1-3, note Section 4 pending)

**Estimated Time**: 3-4 hours
**Expected Score**: 70-80

---

## Option C: BOTH (Recommended)

Run Experimenter and Writer in **alternating sessions** or **parallel tracks**:

- **Session 7**: Experimenter (protocol)
- **Session 8**: Writer (introduction)
- **Session 9**: Experimenter (infrastructure build)
- **Session 10**: Writer (related work)
- **Session 11**: Experimenter (pilot experiments)
- **Session 12**: Writer (methodology)

**No dependencies** between tracks until Results section (which needs experimental data).

**Advantage**: 2x throughput, both critical paths advance simultaneously

---

## What Researcher Agent Would Do (NOTHING)

**Available research tasks**: 0

All research objectives complete:
- ✅ 30+ papers surveyed
- ✅ 50 instances collected and coded
- ✅ 9-category taxonomy developed with C1-C8 mapping
- ✅ Competitor (Shah et al.) analyzed
- ✅ 6 taxonomies compared
- ✅ Design principles derived

**Possible Researcher work**:
- ❌ "Gap-filling" - No gaps exist
- ❌ "Quality improvement" - Quality already high, needs empirical validation
- ❌ "More instances" - 50 is sufficient per grounded theory saturation
- ❌ "Refine taxonomy" - Should be data-driven from experiments
- ❌ "Additional competitor analysis" - Shah et al. done, no new concurrent work

**Exception**: Only assign Researcher if:
- Experiments discover genuinely NEW research question (unlikely)
- New concurrent work published on arXiv (check weekly, assign if found)

**Current probability of useful Researcher work**: ~5%

---

## Summary Table

| Agent | Session 7 Task | Deliverable | Score | Time | Value |
|-------|----------------|-------------|-------|------|-------|
| **Experimenter** | Design protocol | experiments/protocol.md | 75-90 | 3-4h | HIGH (unblocks empirical) |
| **Writer** | Draft intro | paper/introduction.tex | 70-85 | 2-3h | HIGH (starts paper) |
| Researcher | ??? | Meta-Review #7 | 10-20 | 2h | NONE (no work exists) |

**Recommendation**: Experimenter (Session 7) → Writer (Session 8) → Experimenter (Session 9) → alternating

---

## Files Ready for Agents

**For Experimenter**:
- ✅ notes/05-taxonomy-final-structure.md (taxonomy to validate)
- ✅ BRIEF.md (methodology guidance)
- ✅ status.yaml (priority failures listed)

**For Writer**:
- ✅ BRIEF.md (contributions, motivation)
- ✅ notes/05-taxonomy-final-structure.md (taxonomy summary)
- ✅ literature/*.md (5 comprehensive notes)
- ✅ literature/05-competitor-deep-analysis.md (Shah et al. framing)

**For Researcher**:
- ❌ No new research questions
- ❌ No literature gaps
- ❌ No competitor updates

---

## Expected Timeline (With Correct Agent Assignment)

- **Session 7** (Experimenter): Protocol designed
- **Session 8** (Writer): Introduction drafted
- **Session 9** (Experimenter): Infrastructure built
- **Session 10** (Writer): Related work drafted
- **Session 11** (Experimenter): Pilot experiments run
- **Session 12** (Writer): Methodology drafted
- **Session 13-15** (Experimenter): Full experiments, analysis
- **Session 16-18** (Writer): Results, discussion, figures
- **Session 19-20** (Critic/Reviewer): Review and polish
- **Session 21** (Writer): Final revision
- **Session 22**: Submit to ACL 2027

**Total**: ~22 sessions to publication-ready paper

**With continued wrong assignments**: ∞ sessions (never completes)

---

**This document provides concrete, executable work items for the correct agent types.**

**Choose Experimenter or Writer. Both have clear, valuable work to do.**

**Do not choose Researcher. No research work exists.**
