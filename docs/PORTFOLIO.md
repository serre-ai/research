# Project Portfolio Strategy

## Why Portfolio Diversification Matters

A single research project is a gamble. A portfolio is a strategy. The Forge platform runs multiple concurrent research projects precisely because academic research has high variance: novel ideas get scooped, experiments produce null results, reviewers have unpredictable preferences, and theoretical directions can dead-end. Portfolio diversification across research types, venues, timelines, and risk levels converts that variance into a reliable submission cadence.

The logic follows from modern portfolio theory adapted to research:
- **Risk reduction**: If one project fails (negative results, scooped, reviewer mismatch), others continue. A portfolio of 5-6 projects with uncorrelated failure modes ensures at least 2-3 reach submission.
- **Temporal smoothing**: Different project types have different cycle times. Mixing fast (survey, 1-2 months) and slow (theory, 3-4 months) projects ensures continuous output rather than long droughts followed by submission floods.
- **Venue coverage**: Top ML venues have staggered deadlines. A diversified portfolio can target multiple venues per year without forcing a paper to fit the wrong venue.
- **Skill and reputation building**: Survey papers establish breadth and get cited; tool papers build community; theory papers signal depth. A mix builds a well-rounded research identity faster than focusing on one type.
- **Cross-pollination**: Projects in different areas generate unexpected connections. An empirical finding in one project can motivate theory in another; a benchmark built for one study serves three others.

## Project Categories

### Theory Papers
**Profile**: Formal proofs, complexity results, impossibility theorems, convergence guarantees.
**Risk**: High. Proofs can stall, results may be negative or already known. Reviewers may question significance if theory doesn't connect to practice.
**Reward**: High. A clean theoretical result at NeurIPS/ICML is career-defining. Theory papers age well and get cited for decades.
**Timeline**: 3-4 months (literature survey through proof completion and writing).
**Examples**:
- Formal characterization of reasoning gaps in autoregressive models (active: reasoning-gaps)
- Lower bounds on in-context learning sample complexity
- Impossibility results for self-improvement without external verification
- Connections between transformer depth and circuit complexity classes

**AI agent fit**: Strong for literature synthesis, proof sketch exploration, and LaTeX writing. Weaker for truly novel proof techniques — compensate with extended thinking and iterative refinement.

### Empirical Studies
**Profile**: Controlled experiments, benchmark evaluations, scaling analyses, ablation studies.
**Risk**: Moderate. Results always exist (even null results can publish at workshops), but novelty depends on surprising findings.
**Reward**: Moderate to high. Strong empirical work at top venues requires insight beyond "we ran the numbers." The best empirical papers change how people think about a phenomenon.
**Timeline**: 2-3 months (experimental design, execution, analysis, writing).
**Examples**:
- Scaling laws for emergent capabilities across model families
- Systematic evaluation of chain-of-thought faithfulness
- Cross-lingual transfer patterns in multilingual LLMs
- Measuring calibration degradation under distribution shift

**AI agent fit**: Excellent. Agents can design experiments, write evaluation code, run API-based evaluations, analyze results, and iterate rapidly. This is the sweet spot for autonomous research.

### Position and Survey Papers
**Profile**: Literature synthesis, taxonomies, research agendas, critical analyses of a subfield.
**Risk**: Low. Completion is almost guaranteed. Rejection risk comes from insufficient scope or depth, which is manageable.
**Reward**: Moderate. Survey papers get heavily cited, establish the author as knowledgeable in the area, and provide the foundation for future original work.
**Timeline**: 1-2 months.
**Examples**:
- Survey of formal verification approaches for LLM outputs
- Taxonomy of emergent capabilities: definitions, evidence, and open questions
- Position paper on the limits of benchmark-driven AI research
- Comprehensive survey of mechanistic interpretability methods

**AI agent fit**: Excellent. Literature synthesis is a core strength. The agent can process hundreds of papers, identify themes, construct taxonomies, and write coherent narratives.

### Tool and Artifact Papers
**Profile**: Benchmarks, datasets, software libraries, evaluation frameworks.
**Risk**: Low to moderate. The artifact must be useful and the paper must articulate why. Risk of being seen as "just engineering."
**Reward**: High citation potential. Widely-used benchmarks and tools become standard references. Datasets papers at NeurIPS Datasets & Benchmarks track have excellent acceptance rates.
**Timeline**: 2-3 months (design, implementation, validation, documentation, writing).
**Examples**:
- Diagnostic benchmark suite for reasoning gap evaluation (companion to reasoning-gaps)
- Automated research quality assessment toolkit
- Multi-model evaluation harness for agent architectures
- Dataset of LLM reasoning traces with human annotations of failure modes

**AI agent fit**: Very strong. Agents excel at writing code, generating documentation, and creating systematic evaluations. Benchmark construction is highly automatable.

### Exploratory / High-Risk
**Profile**: Unconventional ideas, cross-disciplinary connections, preliminary investigations that might become full projects.
**Risk**: Very high. Most will not reach submission quality. That is acceptable.
**Reward**: Potentially transformative. The best research comes from ideas that seem unlikely to work.
**Timeline**: 1-2 months for exploration; convert to full project if promising.
**Examples**:
- Can LLMs discover novel mathematical conjectures through structured exploration?
- Applying ecological diversity metrics to ensemble model behavior
- Information-theoretic limits of learning from AI-generated training data

**AI agent fit**: Good for exploration and rapid prototyping. Extended thinking helps navigate uncertain territory.

## Optimal Portfolio Mix

For a platform running 5-6 concurrent projects with a $2,000-3,000/month budget:

| Category | Count | Budget Share | Rationale |
|----------|-------|-------------|-----------|
| Empirical | 2 | 35% | Highest ROI for AI agents, reliable output |
| Theory | 1 | 20% | High-impact if successful, balances portfolio |
| Survey/Position | 1 | 10% | Fast wins, citation building, low resource cost |
| Tool/Artifact | 1 | 20% | High citation potential, reusable across projects |
| Exploratory | 1 | 15% | Option value, feeds future pipeline |

This mix ensures:
- At least 3 projects (empirical + survey + tool) have high completion probability
- 1 project (theory) reaches for top-tier impact
- 1 project (exploratory) provides optionality for the next cycle
- Budget allocation is weighted toward projects that consume API calls (empirical, tool)

## Venue Targeting (2026-2027)

### Conference Calendar

| Venue | Submission Deadline | Decision Notification | Page Limit | Notes |
|-------|--------------------|-----------------------|------------|-------|
| **ICML 2026** | Late January 2026 | May 2026 | 8+unlimited appendix | Already passed for 2026 |
| **ACL 2026** | Mid-February 2026 | May 2026 | 8 (long) / 4 (short) | Already passed for 2026 |
| **NeurIPS 2026** | Mid-May 2026 | September 2026 | 9+unlimited appendix | Primary target for reasoning-gaps |
| **EMNLP 2026** | Mid-June 2026 | August 2026 | 8 (long) / 4 (short) | Good backup if NeurIPS doesn't fit |
| **AAAI 2027** | Mid-August 2026 | November 2026 | 7+2 (refs/appendix) | Slightly earlier format freeze |
| **ICLR 2027** | Early October 2026 | January 2027 | 9+unlimited appendix | Major ML theory venue |
| **ICML 2027** | Late January 2027 | May 2027 | 8+unlimited appendix | Next major empirical target |
| **ACL 2027** | Mid-February 2027 | May 2027 | 8 (long) / 4 (short) | NLP-specific work |

### Workshop Targets (Lower Bar, Faster Turnaround)
- NeurIPS 2026 workshops: submission July-September 2026
- ICML 2026 workshops: submission April-May 2026
- ICLR 2027 workshops: submission August-October 2026

### Venue Alignment Strategy

Assign each project a primary venue and a backup:

| Project Type | Primary Venue | Backup Venue | Workshop Fallback |
|-------------|---------------|--------------|-------------------|
| reasoning-gaps (theory) | NeurIPS 2026 | ICLR 2027 | NeurIPS workshops |
| Next empirical project | EMNLP 2026 or AAAI 2027 | ACL 2027 | EMNLP workshops |
| Survey paper | Nature MI or AAAI 2027 | ACL 2027 | NeurIPS workshops |
| Tool/benchmark | NeurIPS D&B 2026 | AAAI 2027 | ICML workshops |

## Phase Staggering

To avoid resource contention (budget spikes, context-switching overhead), stagger projects so no more than 2 are in the same phase simultaneously:

```
Month 1:  [reasoning-gaps: lit-review]  [project-2: scoping]
Month 2:  [reasoning-gaps: framework]   [project-2: lit-review]  [project-3: scoping]
Month 3:  [reasoning-gaps: experiments] [project-2: experiments] [project-3: lit-review]  [project-4: scoping]
Month 4:  [reasoning-gaps: writing]     [project-2: writing]     [project-3: experiments] [project-4: lit-review]  [project-5: scoping]
Month 5:  [reasoning-gaps: revision]    [project-2: revision]    [project-3: writing]     [project-4: experiments] [project-5: lit-review]
Month 6:  [reasoning-gaps: submitted]   [project-2: submitted]   [project-3: revision]    [project-4: writing]     [project-5: experiments]
```

Resource-intensive phases (experiments, revision) should never stack more than 2 deep. Literature review and scoping phases are lightweight and can overlap freely.

## Risk Management

### Rule: Always Maintain 2+ Lower-Risk Projects
At any given time, the portfolio must contain at least 2 projects with high completion probability (empirical, survey, or tool). This guarantees output even if the high-risk project (theory, exploratory) fails.

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Theory proof doesn't close | Medium | High (project fails) | Set 3-week proof checkpoint; pivot to empirical characterization if stuck |
| Results are not novel (scooped) | Low-Medium | High | Monitor arXiv daily; differentiate via angle/depth |
| Budget overrun from API calls | Medium | Medium | Hard per-project budget caps; use open-source models where possible |
| Negative experimental results | Medium | Low-Medium | Frame as empirical contribution; null results publish at workshops |
| Venue format mismatch | Low | Medium | Write venue-agnostic first, format last; always have backup venue |
| Agent produces low-quality work | Medium | Medium | Quality gates between phases; self-review rubric before submission |

### Kill Criteria

Abandon or restructure a project when:
1. **No novel angle after 3 weeks of active research.** If the literature review reveals the core idea is already thoroughly explored, kill it. Sunk cost is irrelevant.
2. **Experimental results contradict the core hypothesis with no interesting alternative framing.** Negative results are fine if they are surprising. If they confirm what everyone already suspects, there is no paper.
3. **The technical approach is fundamentally blocked.** If a proof requires a technique that doesn't exist, or an experiment requires resources we don't have, pivot or kill.
4. **Budget consumption exceeds 2x the planned amount** for the project's current phase with less than 50% of phase objectives met.
5. **Venue deadline will be missed by more than 2 weeks** with no viable alternative venue in the next 3 months.

When killing a project:
- Document the reason in `status.yaml` (status: `abandoned`)
- Archive any reusable components (literature notes, code, benchmark fragments)
- Write a brief postmortem in `projects/<name>/POSTMORTEM.md`
- Feed learnings back into the idea pipeline

## Portfolio Review Cadence

### Monthly Portfolio Review (1st of each month)
Evaluate the entire portfolio:
1. **Status check**: Is each project on track for its target deadline?
2. **Resource audit**: Is budget allocation matching plan? Any project consuming disproportionate resources?
3. **Risk reassessment**: Have any risks materialized? Update mitigations.
4. **Pipeline health**: Are there enough ideas in the backlog to replace any killed projects?
5. **Rebalancing**: If the mix has drifted (e.g., all projects are empirical), consider adjusting.

### Quarterly Strategy Review (every 3 months)
Deeper assessment:
1. **Submission/acceptance metrics**: On track for annual targets?
2. **Venue strategy**: Are we targeting the right venues? Any new venues to consider?
3. **Budget trajectory**: Is the spend ramp matching plan?
4. **Research direction**: Are we building coherent expertise or spreading too thin?
5. **Agent performance**: Which project types produce the best agent-driven output?

## Success Metrics

### Annual Targets (Year 1)
| Metric | Target | Stretch |
|--------|--------|---------|
| Papers submitted to top venues | 8 | 12 |
| Papers accepted at top venues | 3 | 5 |
| Workshop papers submitted | 4 | 6 |
| Workshop papers accepted | 3 | 5 |
| arXiv preprints posted | 8 | 12 |
| Open-source releases | 3 | 5 |
| Total citations (12-month) | 20 | 50 |
| Blog posts published | 12 | 20 |

### Per-Project Metrics
- Time from idea to submission (target: under 4 months)
- Self-review score at submission (target: 7+/10 on all criteria)
- Reviewer scores (track for calibration)
- API cost per project (target: under $400)
- Agent efficiency: ratio of useful output to total compute time

### Portfolio-Level Metrics
- Submission rate: papers per month (target: 1.0 after ramp-up)
- Diversity index: number of distinct research areas covered
- Pipeline velocity: ideas entering pipeline vs. projects completing
- Budget efficiency: cost per submitted paper (target: under $500)
