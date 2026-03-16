# Deepwork: Vision & Principles

**The North Star Document for the Deepwork Autonomous AI Research Platform**

---

## Mission

Build the world's best autonomous AI research engine. Not a paper mill. Not a writing assistant. A system that produces genuinely important, rigorous research that advances the field -- work that other researchers build on, cite for years, and actually use.

Deepwork is an autonomous research operation. Claude Code agents, orchestrated by a persistent daemon, conduct literature reviews, develop formal frameworks, build benchmarks, run evaluations, write papers, and iterate through adversarial self-review -- all in isolated git worktrees, all with full audit trails, all requiring minimal human intervention. The human sets the direction and exercises judgment at key decision points. The system does everything else.

The ambition is not incremental. We are building toward a future where a single researcher, aided by this platform, can sustain the output and rigor of a well-funded lab. Not by cutting corners, but by compressing the vast middle of the research process -- the literature search, the benchmark construction, the statistical analysis, the LaTeX formatting, the revision cycles -- into autonomous workflows that run 24 hours a day on a remote server, producing work that meets the standards of NeurIPS, ICML, ICLR, and ACL.

---

## The Intelligence Stack

The platform is organized into three layers that separate concerns while enabling tight feedback loops between them.

### Knowledge Layer — what the system knows

A persistent, queryable knowledge graph stored in PostgreSQL with pgvector embeddings. Every claim, finding, hypothesis, citation, and experimental result is a node. Relationships encode provenance: this claim is supported by that experiment, which used this dataset, which was inspired by that paper. The graph spans projects -- an insight from reasoning-gaps is discoverable by agent-failure-taxonomy.

Continuous literature intelligence feeds the graph. arXiv and Semantic Scholar are monitored in real time; new papers are embedded and matched against the system's existing knowledge. The graph does not just store what the system has read -- it stores what the system believes, with confidence weights and evidence chains.

### Planning Layer — what the system should do next

A dedicated research planner replaces rigid phase-based scheduling. The planner is itself an agent that reasons about the current state of the knowledge graph, the goals of each active project, and the expected value of possible next actions. It composes tasks -- not from a fixed menu, but from an understanding of what would most advance each project right now.

The planner specifies everything about a task: which model to use, how many turns to allow, what tools to enable, what context to inject. A literature review gets a different session configuration than a statistical analysis. The planner also decides when to stop: when a line of investigation is not yielding diminishing returns but zero returns, it kills the task and reallocates resources.

### Execution Layer — the work itself

Agent sessions carry out the plans. Each session operates in an isolated git worktree with a specific mandate, context window, and toolset. Sessions report back structured results: findings are written to the knowledge graph, not just to files. The verification layer ensures that every claim in a paper draft traces back to specific evidence in the graph. If a claim cannot be grounded, it is flagged.

The execution layer includes closed-loop experimentation: hypothesis, experiment design, execution, analysis, and belief update -- automated end to end. It includes review simulation: synthetic reviewer personas calibrated to actual venue review distributions, predicting acceptance probability before any human sees the draft.

These three layers create the generate-evaluate loop at the architectural level. Knowledge informs planning. Planning directs execution. Execution produces knowledge. The system learns from every cycle.

---

## Core Principles

### 1. Research Taste over Volume

Every automated research system that has failed -- AI Scientist, FARS, and the wave of "generate 100 papers" demos -- has failed for the same reason: generation without judgment. These systems optimize for throughput. They can produce text that looks like a paper. They cannot tell whether the paper matters.

Deepwork inverts this priority. We optimize for significance, not volume. The target is 3-4 excellent papers per year, not 100 mediocre ones. Each project is selected because it addresses a genuine gap in the literature, bridges disconnected fields, or provides tools the community needs. The system's job is not to write as many papers as possible. It is to write the right papers, well.

### 2. Closed-Loop Experimentation

Research is not a linear pipeline from idea to paper. It is an evolutionary process: hypothesize, test, assess, revise or kill. The best work emerges from tight feedback loops where weak ideas die quickly and strong ideas get refined through iteration.

Deepwork automates this loop end to end. A hypothesis enters the system. An experiment is designed, executed, and analyzed. Results update the knowledge graph's belief weights. If the hypothesis is supported, the planner composes follow-up experiments to strengthen the evidence. If refuted, the system records why and moves on. No human intervention required for the loop itself -- only for the meta-question of whether the research direction is worth continuing.

### 3. Adversarial Self-Review

No paper leaves this system without surviving hostile criticism. The failure mode we guard against is not "the paper has a typo" but "the paper's core claim does not hold up under scrutiny." The antidote is a dedicated adversarial review phase where a separate agent session -- with instructions to be maximally critical -- tears the draft apart.

Review simulation extends this further: synthetic reviewer personas calibrated to venue-specific review distributions predict acceptance probability and identify the weakest arguments. The adversarial reviewer can flag claims as unsupported, demand additional experiments, and recommend killing the project. Its objections must be addressed point by point before submission proceeds.

### 4. Persistent, Structured Memory

The number one failure mode in automated research is memory degradation across sessions. An agent starts a new session and has no idea what was tried before, what failed, or why.

Deepwork treats memory as critical infrastructure. The knowledge graph is the long-term memory: every finding, every decision, every failed approach is a queryable node with embeddings for semantic retrieval. Status files remain the operational source of truth per project. Git history provides the full audit trail. PostgreSQL stores evaluation results for cross-session analysis. Every agent session begins by reading relevant state from the graph. Every session ends by writing structured results back.

This extends across projects. The knowledge graph enables cross-project intelligence: what research strategies worked, which model families performed unexpectedly, what reviewer objections recurred. Over time, this accumulated knowledge becomes the system's most valuable asset.

### 5. Minimal Human Decisions

The human's role is to navigate, not to drive. Daily digests, binary decisions, kill switches. Not "what should we do next?" but "here is what we plan to do next -- approve or veto?"

The target is fewer than 20 human decision points across an entire project lifecycle. The research planner handles the 95% of decisions that are execution-level. The human is reserved for the 5% that require taste, strategic judgment, or ethical consideration. The human's job is to be the editor-in-chief, not the staff writer.

### 6. Community-First Artifacts

Research that matters produces artifacts the community actually uses. Every Deepwork project is designed from the start to produce at least one artifact beyond the paper: benchmark suites, datasets on HuggingFace, evaluation tools on GitHub. These are first-class deliverables that shape the research design from day one.

We favor work that creates frameworks others can build on over work that makes a narrow empirical claim. A paper that introduces a taxonomy cited by 50 follow-up studies is worth more than a paper that achieves a new SOTA on a single benchmark.

### 7. Radical Transparency

Every decision logged. Every failed approach recorded. Full audit trails from first commit to final submission. The knowledge graph captures the "negative space" of research -- hypotheses that didn't pan out, experimental designs that were flawed, theoretical claims that fell apart. This negative-space knowledge prevents the system from repeating mistakes and gives the human a clear view of the reasoning behind every choice.

---

## What We Are Not

**Not a paper mill.** Deepwork produces 3-4 papers per year. Every one of them should be worth reading.

**Not a writing assistant.** The system does the research, not just the writing. It conducts literature reviews, develops formal frameworks, designs and runs experiments, analyzes results, and builds artifacts. Writing is the final mile.

**Not fully autonomous.** Human taste and judgment remain essential for assessing whether a research question is important, whether a result is surprising, or whether a framing will resonate. Full autonomy is not the goal; effective human-AI collaboration at minimal cost to human attention is the goal.

**Not trying to replace researchers.** We are building the best researcher's best tool. A system that extends what one person can accomplish, not one that makes people unnecessary.

---

## The Research Philosophy

**Bridge theory and practice.** The most impactful ML work lives at the intersection of formal theory and empirical evaluation. Deepwork targets the bridge: theoretical frameworks that generate testable predictions, evaluated at scale.

**Build diagnostic tools, not leaderboard entries.** We produce benchmarks that diagnose specific capabilities, not monolithic benchmarks that produce a single score. The field has enough leaderboards. It needs better diagnostics.

**Connect disparate fields.** The most cited papers bring an insight from one field into another. The knowledge graph and literature intelligence are designed to surface these connections automatically.

**Make conditional claims, not overclaims.** We report confidence intervals, distinguish systematic failures from noise, and ground claims in established conjectures. Precision in claims is a competitive advantage.

**Produce frameworks, not just findings.** Findings get cited once. Frameworks get cited for years. We aim for work that provides structure others build on.

---

## Success Metrics

**Research Quality:** Papers accepted at NeurIPS, ICML, ICLR, ACL. At least one spotlight/oral per year. Reviewer scores above acceptance threshold.

**Community Impact:** Benchmarks adopted by 5+ groups within 12 months. Datasets with 1,000+ HuggingFace downloads. Code repos with 100+ GitHub stars. Artifacts cited independently of the paper.

**Operational Efficiency:** Research question to submission under 3 months. Fewer than 20 human decisions per project. Under $2,000 API/compute cost per accepted paper. 95%+ system uptime.

**Platform Intelligence:** Cross-project knowledge transfer demonstrable in later projects. Review simulation accuracy within 1 point of actual reviewer scores. Planner task-value estimates correlate with actual session outcomes.

---

## The North Star

A system where you say: "Investigate whether [phenomenon X] has [property Y], and if so, produce a NeurIPS-quality paper with diagnostic benchmarks."

Three months later, you have a paper with formal framework and empirical evaluation, a diagnostic benchmark suite, a HuggingFace dataset, a GitHub repository, and a blog post. You made fewer than 20 decisions. Most of them yes/no. None about formatting, statistical tests, or LaTeX.

The reasoning-gaps project is the first proof: from research question to near-complete NeurIPS submission in under two weeks, with a formal framework, 9 diagnostic benchmarks, 121,000+ evaluation instances across 9 model families, and a full analysis pipeline. The gap between where we are and the north star is not capability -- it is the intelligence stack. Building the knowledge graph, the planner, and the verification layer closes that gap.

---

## Roadmap Sketch

**Now (Q1 2026):** Single-project proof of concept complete. Reasoning-gaps demonstrates the full pipeline. Platform runs on Hetzner VPS with TypeScript daemon. Begin knowledge graph schema and pgvector integration.

**Next (Q2 2026):** Intelligence stack foundations. Knowledge graph operational. Research planner replaces phase-based scheduling. Event-driven architecture replaces polling daemon. Closed-loop experimentation running on second project.

**Q3 2026:** Verification layer enforces claims-to-evidence traceability. Review simulation calibrated against real NeurIPS/ACL reviews. Continuous literature intelligence monitoring arXiv. 2-3 concurrent projects with cross-project knowledge transfer.

**Q4 2026 - Q1 2027:** Mature platform. Meta-learning from session quality data improves planner decisions. Project proposals generated from literature monitoring and knowledge graph gaps. Artifact release pipeline automated. The system develops genuine research taste through accumulated experience.

**Eventually:** The system identifies promising research directions, proposes projects with estimated impact and cost, runs them to completion with human oversight at key gates, releases artifacts, monitors community adoption, and feeds adoption data back into project selection -- a self-sustaining research operation that gets better with every project it completes.

---

*This document is a living artifact. The principles are durable. The specifics will change. That's the point.*
