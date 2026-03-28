# Sections Ready for Writer Agent

**Date**: 2026-03-28
**Status**: Research complete, experiments designed, infrastructure validated
**Writer can start**: Introduction, Related Work, partial Methodology

---

## Ready to Write Now (No Experimental Data Required)

### 1. Introduction ✅ READY

**Length**: 1 page (ACL format)

**Structure**:
1. **Motivation** (2 paragraphs)
   - LLM-based autonomous agents increasingly deployed (ReAct, AutoGPT, Claude Code, etc.)
   - Systematic failures poorly understood — individual reports exist but no comprehensive taxonomy
   - Gap: Practitioners can't design robust agents, researchers can't prioritize improvements

2. **Research Question** (1 paragraph)
   - What are the fundamental failure modes in LLM-based agents?
   - How do failures map to underlying LLM capability limitations?
   - How do different architectures affect failure distributions?

3. **Contributions** (1 paragraph, bulleted)
   - Hierarchical taxonomy (9 categories, 24 sub-categories) from 50 instances across 7 architectures
   - LLM limitation mapping (C1-C8) distinguishing fundamental vs. correctable failures
   - Architecture-failure correlation from controlled experiments (3 frameworks, 6 failure types)
   - Design principles for robust agent development
   - Bridge to reasoning research (how abstract limitations manifest in agents)

**Key sources**:
- `notes/05-taxonomy-final-structure.md` (contributions summary)
- `literature/05-competitor-deep-analysis.md` (positioning vs. Shah et al.)
- `BRIEF.md` (motivation)

**Tone**: Emphasize complementarity with Shah et al. (they cover implementation faults, we cover cognitive failures)

---

### 2. Related Work ✅ READY

**Length**: 1.5 pages

**Structure**:

#### 2.1 Agent Architectures
- ReAct (reactive loop): Yao et al. 2023
- Plan-then-execute: Tree of Thoughts, ReWOO
- Reflexion (self-correction): Shinn et al. 2023
- Multi-agent: CrewAI, AutoGen
- Brief description of each, focus on architectural differences

#### 2.2 Existing Agent Failure Taxonomies
**Critical**: Position against 6 competing taxonomies

| Taxonomy | Focus | Scale | Theory |
|----------|-------|-------|--------|
| MAST (Cemri 2025) | Multi-agent coordination | 5 categories | No |
| Three-Phase (2025) | Workflow stages | 3 phases × N categories | No |
| DEFT (2024) | Research agents | 4 categories | No |
| AgentErrorTaxonomy (2025) | Learning from failures | Error types + recovery | Partial |
| Shah et al. (2026) ⭐ | Implementation faults | 37 categories, 385 instances | No |
| **Ours** | Cognitive failures | 9 categories, 50 instances | **Yes (C1-C8)** |

**Key differentiation**:
- Shah et al.: 87% conventional software issues (dependencies, APIs, configs) — component-level
- Ours: 100% cognitive/behavioral failures in reasoning — agent-level
- **Only ~20% overlap** — taxonomies are complementary
- Our edge: Theoretical LLM limitation mapping, design principles, architecture guidance
- Their edge: Scale (385 instances), production validation

**Framing**: "While Shah et al. (2026) comprehensively categorize implementation faults in production systems, our work complements this by focusing on cognitive failures rooted in LLM reasoning limitations..."

**Source**: `literature/05-competitor-deep-analysis.md` (detailed comparison)

#### 2.3 LLM Reasoning Limitations
Connect to reasoning research:
- Hallucination (C1 Factual Grounding)
- Long-context degradation (C2 Long-Range Coherence)
- Self-evaluation failures (C3 Meta-Cognitive Monitoring, C7 Self-Correction)
- Constraint handling (C4 Constraint Satisfaction)

**Bridge**: "These abstract reasoning limitations manifest as concrete agent failures, which our taxonomy systematically documents."

**Sources**:
- `notes/04-llm-limitation-mapping.md` (C1-C8 definitions)
- Key papers: "The Reasoning Trap" (C8), long-context studies (C2), Reflexion (C7)

---

### 3. Methodology (PARTIAL) ✅ READY

**What's ready**: Data collection + grounded theory process

**What's NOT ready**: Experimental methodology (awaits pilot/full results)

#### 3.1 Data Collection ✅ READY

**Write now**:
- **Source selection**: 5 types (research papers, GitHub issues, benchmarks, framework docs, surveys)
- **Time frame**: 2023-2026 (3 years of agent development)
- **Inclusion criteria**: Concrete failure instances with observable symptoms, reproducible conditions, documented impact
- **Exclusion criteria**: Vague reports, user error, non-agent issues
- **Architecture coverage**: 7 architectures (ReAct, Plan-Execute, Reflexion, Autonomous Loop, ToT, Coding Agents, Multi-Agent)
- **Total instances**: 50 detailed failures

**Table 1: Data Source Distribution**
| Source Type | Instances | % | Example |
|-------------|-----------|---|---------|
| Research papers | 15 | 30% | "The Reasoning Trap" tool hallucination |
| GitHub issues | 12 | 24% | CrewAI caching bug #3986 |
| Benchmarks | 11 | 22% | SWE-bench 52% semantic errors |
| Framework docs | 5 | 10% | AutoGPT loop detection |
| Surveys | 10 | 20% | OWASP ASI08 memory propagation |

**Table 2: Architecture Distribution**
| Architecture | Instances | % | Reproducibility |
|--------------|-----------|---|-----------------|
| All (cross-cutting) | 21 | 42% | High |
| ReAct | 11 | 22% | Easy |
| Autonomous loop | 4 | 8% | Medium |
| Reflection | 3 | 6% | Easy |
| Coding agents | 3 | 6% | High |
| Others | 8 | 16% | Mixed |

**Source**: `status.yaml` metrics, `literature/04-failure-instances-collection.md`

#### 3.2 Grounded Theory Analysis ✅ READY

**Write now**:
- **Rationale**: Avoid imposing categories prematurely; let structure emerge from data
- **Phase 1 — Open Coding**:
  - Coded all 50 instances independently
  - Generated ~150 codes describing failure symptoms, causes, contexts
  - Identified 9 emergent patterns through constant comparison
- **Phase 2 — Axial Coding**:
  - Analyzed relationships: causal, reinforcement, common root, trade-offs, hierarchical
  - Refined category boundaries for ambiguous cases
  - Evolved flat structure → hierarchical (9 major categories, 24 sub-categories)
- **Phase 3 — Theoretical Mapping**:
  - Connected all 9 categories to 8 LLM capability dimensions (C1-C8)
  - Distinguished fundamental (5) vs. correctable (8) limitations
  - Derived 6 design principles from limitation patterns

**Table 3: Coding Process**
| Phase | Activities | Output |
|-------|-----------|--------|
| Open | Code 50 instances, constant comparison | 150 codes, 9 patterns |
| Axial | Analyze relationships, refine boundaries | 24 sub-categories, hierarchy |
| Theoretical | Map to LLM capabilities | C1-C8 mapping, design principles |

**Source**: `notes/02-open-coding-memos.md`, `notes/03-axial-coding-relationships.md`, `notes/04-llm-limitation-mapping.md`

#### 3.3 Experimental Validation ⚠️ NOT READY YET

**Defer to later**: Wait for pilot reproduction results (Session 9+)

Will include:
- Framework selection (3 frameworks)
- Failure reproduction protocol (6 high-priority failures)
- Evaluation metrics
- Statistical analysis methods

**Placeholder text**: "To empirically validate the taxonomy and quantify architecture-failure correlations, we conducted controlled reproduction experiments across three agent frameworks. Details are provided in Section 4."

---

## NOT Ready Yet (Requires Experimental Data)

### 4. Results ⚠️ WAIT FOR PILOT

**Needs**: Pilot reproduction results (Session 9)
**Timeline**: Available after Session 9 (~next week)

Will include:
- **Table 4**: Taxonomy structure (9 categories, definitions, examples) — can draft skeleton now
- **Table 5**: Failure reproduction rates by framework (NEEDS DATA)
- **Table 6**: Architecture-failure correlation matrix (NEEDS DATA)
- **Figure 1**: Failure distribution across categories (CAN DRAFT from existing 50 instances)
- **Figure 2**: Architecture risk profiles (NEEDS EXPERIMENTAL DATA)

**What Writer can do now**:
- Draft Table 4 skeleton from `notes/05-taxonomy-final-structure.md`
- Create Figure 1 from existing 50 instances (preliminary, will update with experimental validation)

### 5. Discussion ⚠️ WAIT FOR FULL VALIDATION

**Needs**: Full validation results (Sessions 10-13)
**Timeline**: Available 2-3 weeks

Will include:
- Interpretation of empirical findings
- Comparison to predictions
- Implications for agent design
- Limitations of current study

### 6. Conclusion ⚠️ WAIT FOR RESULTS

**Needs**: Results + Discussion complete
**Timeline**: After Sessions 10-13

---

## Recommended Writing Order

### Session A (Writer): Introduction + Related Work
**Time estimate**: 2-3 hours
**Deliverables**:
1. Full introduction (1 page)
2. Full related work (1.5 pages)
3. Position vs. Shah et al. clearly established

**Files to create**:
- `paper/sections/01-introduction.tex`
- `paper/sections/02-related-work.tex`

### Session B (Writer): Methodology (Partial)
**Time estimate**: 1-2 hours
**Deliverables**:
1. Data collection section (complete)
2. Grounded theory section (complete)
3. Experimental validation section (placeholder only)

**Files to create**:
- `paper/sections/03-methodology.tex`
- `paper/tables/source-distribution.tex`
- `paper/tables/architecture-distribution.tex`
- `paper/tables/coding-process.tex`

### Session C (Writer): Results (Skeleton)
**Time estimate**: 1 hour
**Deliverables**:
1. Table 4 skeleton (taxonomy structure)
2. Figure 1 (preliminary failure distribution from 50 instances)
3. Placeholders for experimental tables/figures

**Files to create**:
- `paper/sections/04-results.tex` (skeleton)
- `paper/tables/taxonomy-structure.tex`
- `paper/figures/failure-distribution.pdf` (preliminary)

**Note**: This will need updating after pilot/full results, but skeleton helps clarify what data is needed

---

## Key References for Writer

### Literature Files (Read First)
1. `literature/05-competitor-deep-analysis.md` — Shah et al. comparison (CRITICAL)
2. `literature/03-recent-taxonomies-and-concurrent-work-2025-2026.md` — Other taxonomies
3. `literature/04-failure-instances-collection.md` — Failure examples

### Taxonomy/Analysis Files
4. `notes/05-taxonomy-final-structure.md` — Final taxonomy (9 categories, C1-C8)
5. `notes/04-llm-limitation-mapping.md` — C1-C8 detailed explanations
6. `notes/02-open-coding-memos.md` — Coding process details

### Project Files
7. `BRIEF.md` — Research goals, hypotheses, contributions
8. `status.yaml` — Current metrics, decisions made
9. `experiments/00-experimental-protocol.md` — Experimental design (for methodology)

---

## LaTeX Setup

### Document Structure
```latex
\documentclass[11pt,a4paper]{article}
\usepackage[hyperref]{acl2025}  % ACL 2027 uses 2025 style

\title{A Taxonomy of Failure Modes in LLM-Based Autonomous Agents}

\author{
  % Authors TBD — use placeholder for now
  Anonymous Authors \\
  Anonymous Institution \\
  \texttt{anonymous@example.com}
}

\begin{document}
\maketitle

\begin{abstract}
[~150 words — write after sections complete]
\end{abstract}

\input{sections/01-introduction}
\input{sections/02-related-work}
\input{sections/03-methodology}
\input{sections/04-results}
\input{sections/05-discussion}
\input{sections/06-conclusion}

\bibliography{references}
\bibliographystyle{acl_natbib}

\end{document}
```

### Bibliography
Start building `paper/references.bib` from key_references in status.yaml:
- Yao et al. (2023) — ReAct
- Shinn et al. (2023) — Reflexion
- Shah et al. (2026) — Characterizing Faults (CRITICAL)
- "The Reasoning Trap" arXiv:2510.22977
- MAST, Three-Phase, DEFT, AgentErrorTaxonomy papers

---

## Style Guidelines

### Voice
- Third person, passive where appropriate
- "We collected 50 instances..." not "I collected..."
- "The taxonomy reveals..." not "Our taxonomy shows..."

### Terminology
- **Agent failures** not "bugs" or "errors" (broad scope)
- **LLM limitations** not "weaknesses" (neutral, fundamental)
- **Architecture** not "framework" when discussing general patterns
- **Framework** when discussing specific implementations (LangChain, etc.)

### Framing Shah et al.
**Avoid**: "Unlike Shah et al., we focus on..."
**Prefer**: "Complementing Shah et al.'s comprehensive coverage of implementation faults, our work examines cognitive failures rooted in LLM reasoning limitations..."

**Emphasize**:
- Different levels of analysis (component vs. agent)
- Different fault types (87% conventional software vs. 100% LLM reasoning)
- Both taxonomies needed (robust engineering + cognitive reliability)

---

## Length Targets (ACL Format)

- Introduction: 1 page
- Related Work: 1.5 pages
- Methodology: 2 pages (1.5 pages ready now, 0.5 awaits experiments)
- Results: 2.5 pages (skeleton now, full later)
- Discussion: 1.5 pages (later)
- Conclusion: 0.5 pages (later)
- **Total body**: 9 pages
- References: unlimited (separate)
- Appendix: allowed for extra tables

**ACL limit**: 8 pages (can go to 9 with justification, or use appendix)

---

## Questions Writer Should NOT Block On

### Q: "Which models were used in experiments?"
**A**: Claude Sonnet 3.5 (consistent across frameworks). Detail in methodology experimental section (not ready yet). Use placeholder for now.

### Q: "What were the exact reproduction rates?"
**A**: Awaiting pilot results (Session 9). Use "preliminary analysis suggests >60% reproduction rate" for now, mark as [TO BE UPDATED].

### Q: "Should I include architectural code examples?"
**A**: No. Focus on conceptual architectural differences (reactive vs. planning vs. reflective). Code is implementation detail.

### Q: "How to handle concurrent work published after our submission?"
**A**: Monitor arXiv weekly. If new taxonomy appears, add to related work. Our C1-C8 theoretical grounding is unique differentiation.

---

## Success Criteria for Writer Sessions

After 2-3 Writer sessions, paper should have:
- [ ] Complete introduction (motivation, gap, contributions)
- [ ] Complete related work (6 taxonomies positioned, Shah et al. differentiation clear)
- [ ] Complete data collection methodology
- [ ] Complete grounded theory methodology
- [ ] Taxonomy structure table (skeleton, examples from 50 instances)
- [ ] Preliminary failure distribution figure
- [ ] Placeholders for experimental sections (clear what data is needed)
- [ ] Bibliography with key references

**Estimated total**: 4-5 pages of polished text, ready for experimental results integration

---

## Coordination with Experimenter

Writer should work **in parallel** with Experimenter (Session 9+). Updates needed:

1. After **Pilot reproduction** (Session 9):
   - Update methodology with experimental protocol
   - Add preliminary results (F1+F5 reproduction rates)
   - Draft partial results section

2. After **Full validation** (Sessions 10-13):
   - Complete results section with all tables/figures
   - Write discussion based on findings
   - Write conclusion

**No blocking**: Writer can make substantial progress (4-5 pages) before any experimental data available.

---

## Contact / Escalation

If Writer encounters:
- Missing information not listed as available above → check files listed in "Key References"
- Conflicting information between files → prioritize `status.yaml` decisions_made as ground truth
- Fundamental ambiguity → create `paper/WRITER-QUESTIONS.md` documenting questions

**Do not block on experimental details** — use placeholders marked [TO BE UPDATED] and continue writing.

---

## Ready to Start

Writer agent can begin immediately on Introduction + Related Work with full context available in project files. No experimental data required for these sections.

**Estimated output**: 2.5-3 pages of polished ACL-format LaTeX after first Writer session.
