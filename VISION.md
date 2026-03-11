# Deepwork: Vision & Principles

**The North Star Document for the Deepwork Autonomous AI Research Platform**

---

## Mission

Build the world's best autonomous AI research engine. Not a paper mill. Not a writing assistant. A system that produces genuinely important, rigorous research that advances the field -- work that other researchers build on, cite for years, and actually use.

Deepwork is an autonomous research operation. Claude Code agents, orchestrated by a persistent daemon, conduct literature reviews, develop formal frameworks, build benchmarks, run evaluations, write papers, and iterate through adversarial self-review -- all in isolated git worktrees, all with full audit trails, all requiring minimal human intervention. The human sets the direction and exercises judgment at key decision points. The system does everything else.

The ambition is not incremental. We are building toward a future where a single researcher, aided by this platform, can sustain the output and rigor of a well-funded lab. Not by cutting corners, but by compressing the vast middle of the research process -- the literature search, the benchmark construction, the statistical analysis, the LaTeX formatting, the revision cycles -- into autonomous workflows that run 24 hours a day on a remote server, producing work that meets the standards of NeurIPS, ICML, ICLR, and ACL.

---

## Core Principles

### 1. Research Taste over Volume

Every automated research system that has failed -- AI Scientist, FARS, and the wave of "generate 100 papers" demos -- has failed for the same reason: generation without judgment. These systems optimize for throughput. They can produce text that looks like a paper. They cannot tell whether the paper matters.

Deepwork inverts this priority. We optimize for significance, not volume. The target is 3-4 excellent papers per year, not 100 mediocre ones. Each project is selected because it addresses a genuine gap in the literature, bridges disconnected fields, or provides tools the community needs. The system's job is not to write as many papers as possible. It is to write the right papers, well.

This principle has architectural consequences. The orchestrator does not parallelize to maximize paper count -- it parallelizes to maximize depth within a single project (running evaluations across model families simultaneously, for instance). Agent sessions are long and focused, not short and scattershot. The system spends more time reading and evaluating than writing. And every project goes through a rigorous selection gate before any resources are committed: Does this question matter? Is it tractable? Will the artifacts be useful beyond the paper itself?

### 2. Generate-Evaluate Loops

Research is not a linear pipeline from idea to paper. It is an evolutionary process: hypothesize, test, assess, revise or kill. The best work emerges from tight feedback loops where weak ideas die quickly and strong ideas get refined through iteration.

This is the lesson of AlphaEvolve and FunSearch. The power of LLMs in research is not in single-shot generation but in the generate-evaluate loop: produce a candidate (hypothesis, proof sketch, benchmark design, paper draft), evaluate it against explicit criteria, and feed the evaluation back into the next generation cycle. Deepwork is built around this loop at every level. Benchmark designs get tested against known ground truths before deployment. Formal claims get checked against the literature and stress-tested with edge cases. Paper drafts go through multiple revision cycles with simulated reviewer feedback.

The critical insight is that evaluation must be at least as sophisticated as generation. A system that can generate a plausible-sounding theoretical claim but cannot rigorously evaluate whether that claim is well-supported will produce confident nonsense. This is why Deepwork invests heavily in evaluation infrastructure -- statistical test suites, analysis pipelines, adversarial review prompts -- built before the work they evaluate.

### 3. Adversarial Self-Review

No paper leaves this system without surviving hostile criticism. This is the single most important quality gate in the entire platform.

The failure mode we guard against is not "the paper has a typo" or "the related work section is incomplete." It is "the paper's core claim does not hold up under scrutiny." Automated systems are particularly vulnerable to this because they can generate fluent, confident text that papers over logical gaps. The antidote is a dedicated adversarial review phase where a separate agent session -- with instructions to be maximally critical, to look for unstated assumptions, to find the weakest link in the argument chain -- tears the draft apart.

This is not a formality. The adversarial reviewer must have concrete power: it can flag claims as unsupported, demand additional experiments, identify missing baselines, and in the strongest case, recommend killing the project. Its objections must be addressed point by point before any submission proceeds. The system tracks which objections were raised, how they were addressed, and whether the resolution was substantive or cosmetic. This creates a paper trail that the human can audit and that makes the system's quality reasoning transparent.

### 4. Persistent Memory

The number one failure mode in automated research is memory degradation across sessions. An agent starts a new session and has no idea what was tried before, what failed, what decisions were made, or why. It repeats work. It contradicts earlier decisions. It loses context that took hours to build.

Deepwork treats memory as critical infrastructure, not an afterthought. Every project maintains structured state in `status.yaml` (the single source of truth for project phase, decisions, and next steps), research logs, git history, and a PostgreSQL database for queryable access to evaluation results. Every agent session begins by reading this state. Every session ends by updating it. The memory is not optional context -- it is a mandatory preamble that shapes every decision the agent makes.

This extends beyond individual projects. The platform maintains cross-project memory: what research strategies worked, which model families performed unexpectedly, what reviewer objections recurred. Over time, this accumulated knowledge becomes the system's most valuable asset -- a growing corpus of research judgment that no single session could reconstruct. The difference between a novice researcher and a seasoned one is not intelligence; it is accumulated context. Deepwork's memory architecture is designed to give every agent session the benefit of that accumulation.

### 5. Minimal Human Decisions

The human's role is to navigate, not to drive. The system proposes; the human disposes. Daily digests, binary decisions, kill switches. Not "what should we do next?" but "here is what we plan to do next -- approve or veto?"

This is a deliberate design choice rooted in the observation that human attention is the scarcest resource in the system. A researcher using Deepwork should not spend hours directing agents. They should spend minutes reviewing summaries and making high-level calls: Is this research direction worth pursuing? Should we submit to this venue or that one? Is this draft ready for adversarial review? The target is fewer than 20 human decision points across an entire project lifecycle, from idea to submission.

This does not mean the human is unimportant. Quite the opposite: the human's judgment is so valuable that it should be reserved for the decisions where it matters most. The system handles the 95% of decisions that are execution-level (which statistical test to use, how to format the figures, what order to present results) and surfaces only the 5% that require taste, strategic judgment, or ethical consideration. The human's job is to be the editor-in-chief, not the staff writer.

### 6. Community-First Artifacts

Research that matters produces artifacts that the community actually uses. Papers are the narrative wrapper around reusable contributions. A paper without a benchmark, dataset, or tool is a story; a paper with them is infrastructure.

Every Deepwork project is designed from the start to produce at least one artifact beyond the paper itself. The reasoning-gaps project produces a diagnostic benchmark suite (ReasonGap) and a formal taxonomy. Future projects will produce datasets on HuggingFace, evaluation tools on GitHub, and benchmark leaderboards. These artifacts are not afterthoughts bolted on during the camera-ready revision -- they are first-class deliverables that shape the research design from day one.

This principle also guides what research we pursue. We favor work that creates frameworks others can build on over work that makes a narrow empirical claim. A paper that introduces a taxonomy cited by 50 follow-up studies is worth more than a paper that achieves a new SOTA on a single benchmark. The question is not "can we publish this?" but "will other researchers use what we build?"

### 7. Radical Transparency

Every decision logged. Every failed approach recorded. Full audit trails from first commit to final submission. This is not bureaucracy -- it is the system learning from its own history.

The research literature has a massive publication bias problem: we see what worked, never what was tried and abandoned. Deepwork's decision logs, git history, and research notes capture the "negative space" of research -- the hypotheses that didn't pan out, the experimental designs that were flawed, the theoretical claims that fell apart under scrutiny. This negative-space knowledge is extraordinarily valuable. It prevents the system from repeating mistakes across projects. It gives the human a clear view of the reasoning behind every choice. And it produces a secondary artifact: a transparent record of how autonomous research actually works, warts and all.

Transparency also serves as a quality mechanism. When every decision must be logged with a rationale, the agent is forced to articulate why it is making each choice. This is the computational equivalent of "if you can't explain it simply, you don't understand it well enough." Sloppy reasoning shows up immediately in the logs. The act of writing the rationale often reveals that the decision needs more thought.

---

## What We Are Not

**Not a paper mill.** FARS and similar systems demonstrate that LLMs can generate text formatted like academic papers at scale. We have zero interest in this. Generating 100 papers that no one reads, cites, or builds on is worse than useless -- it pollutes the literature and wastes reviewer time. Deepwork produces 3-4 papers per year. Every one of them should be worth reading.

**Not a writing assistant.** The system does the research, not just the writing. It conducts literature reviews, develops formal frameworks, designs and runs experiments, analyzes results, and builds artifacts. Writing is the final mile, not the whole journey. A writing assistant takes your ideas and makes them pretty. Deepwork takes a research question and produces the ideas, the evidence, and the narrative.

**Not fully autonomous in the "no human" sense.** Human taste and judgment remain essential. The system cannot yet reliably assess whether a research question is important, whether a result is surprising, or whether a framing will resonate with the community. These are exactly the decisions we route to the human. Full autonomy is not the goal; effective human-AI collaboration at minimal cost to human attention is the goal.

**Not trying to replace researchers.** We are building the best researcher's best tool. A system that extends what one person can accomplish, not one that makes people unnecessary. The long-term vision is a world where any researcher with a good question and access to Deepwork can produce work that competes with well-funded labs -- democratizing research capacity, not eliminating researchers.

---

## The Research Philosophy

### Bridge Theory and Practice

The most impactful work in machine learning lives at the intersection of theory and empirical evaluation. Pure theory without experiments is untethered from reality. Pure empirics without theory is stamp collecting. Deepwork targets the bridge.

The reasoning-gaps project exemplifies this: it connects formal complexity theory (TC^0, NC^1, known transformer expressiveness bounds) with large-scale empirical evaluation across model families. The theoretical framework generates specific, testable predictions. The empirical evaluation confirms, refines, or refutes them. The result is a paper that satisfies both the theory-minded reviewer who wants formal rigor and the empirics-minded reviewer who wants experimental evidence.

### Build Diagnostic Tools, Not Leaderboard Entries

We produce benchmarks and evaluation suites that diagnose specific capabilities, not monolithic benchmarks that produce a single score. A diagnostic benchmark tells you what a model can and cannot do. A leaderboard benchmark tells you which model is "best" by some opaque aggregate. The field has enough leaderboards. It needs better diagnostics.

### Connect Disparate Fields

The most cited papers are often the ones that bring an insight from one field into another. Deepwork is particularly well-suited to this because its literature review process can span fields that a single human researcher might not cover. The reasoning-gaps project connects computational complexity theory, cognitive science (System 1/System 2 reasoning), and empirical ML evaluation. Future projects should similarly look for unexploited connections.

### Make Conditional Claims, Not Overclaims

Academic incentives push toward strong claims. Deepwork pushes back. We make conditional claims grounded in established conjectures ("if TC^0 does not equal NC^1, then...") rather than unsupported universal statements. We report confidence intervals, not just point estimates. We distinguish between "the model fails on this task" and "the model fails systematically on this task class, and here is the structural reason why." Precision in claims is a competitive advantage: reviewers trust precise, qualified claims far more than sweeping ones.

### Produce Frameworks, Not Just Findings

A finding is "Model X scores Y% on task Z." A framework is "here is a taxonomy of reasoning gap types, here is how to diagnose them, and here is which interventions address which types." Findings get cited once, in related work sections. Frameworks get cited for years, in methodology sections. We aim for the kind of work that gets cited 500+ times because it provides structure that others build on.

---

## Success Metrics

### Research Quality
- Papers accepted at top-tier venues: NeurIPS, ICML, ICLR, ACL, AAAI
- At least one paper per year receives a spotlight or oral designation
- Reviewer scores average above the acceptance threshold (not borderline accepts)

### Community Impact
- Benchmarks adopted by at least 5 independent research groups within 12 months of release
- Datasets on HuggingFace with 1,000+ downloads within 6 months
- Code repositories with 100+ GitHub stars within 12 months
- At least one artifact from each project gets cited independently of the paper

### Operational Efficiency
- Time from research question to submission: under 3 months
- Human decision points per project: fewer than 20 across the entire lifecycle
- Cost per accepted paper: under $2,000 in API and compute costs
- System uptime: 95%+ (the daemon runs, sessions complete, no silent failures)

### Platform Maturity
- Concurrent active projects: 3-5 at steady state
- Successful adversarial review kill rate: at least 20% of generated drafts get sent back for major revision (if nothing ever fails review, the review is too soft)
- Cross-project learning: decisions in later projects demonstrably informed by earlier project logs

---

## The North Star

A system where you can say:

> "Investigate whether [phenomenon X] has [property Y], and if so, produce a NeurIPS-quality paper with diagnostic benchmarks."

And 3 months later, you have:

- A paper with formal framework, empirical evaluation, and clear contributions
- A diagnostic benchmark suite, documented and released
- A HuggingFace dataset with evaluation results across model families
- A GitHub repository with reproduction code
- A blog post summarizing key findings for a broader audience

With you having made fewer than 20 decisions along the way. Most of them yes/no. None of them about formatting, statistical tests, or LaTeX layout. All of them about whether the research direction is worth pursuing and whether the results are ready to share with the world.

This is not science fiction. The reasoning-gaps project is the first proof of concept: from research question to near-complete NeurIPS submission in under two weeks, with a formal framework, 9 diagnostic benchmarks, 121,000+ evaluation instances across 9 model families, a pre-registered analysis pipeline, and a paper draft -- all produced by autonomous agent sessions with minimal human steering.

The gap between where we are and the north star is not capability. It is reliability, memory, and self-assessment. The agents can do the work. The challenge is making them do it consistently, remember what they've done, and honestly evaluate whether it's good enough. Every architectural decision in Deepwork -- the persistent state, the adversarial review, the structured decision logs, the evaluation-before-generation discipline -- is designed to close that gap.

---

## Roadmap Sketch

**Now (Q1 2026):** Single-project proof of concept. Reasoning-gaps project demonstrates the full pipeline: literature review through paper submission. Platform runs on Hetzner VPS with TypeScript orchestrator daemon. Manual project setup, semi-automated evaluation.

**Next (Q2-Q3 2026):** Multi-project operation. 2-3 concurrent projects on independent branches. Adversarial review pipeline automated. Cross-project memory begins accumulating. Dashboard provides real-time visibility into all active projects.

**Later (Q4 2026 - Q1 2027):** Mature platform. Project proposals generated and filtered autonomously based on literature monitoring. Artifact release pipeline (HuggingFace, GitHub, blog) automated. Community feedback (citation tracking, benchmark adoption) feeds back into project selection. The system begins to develop genuine research taste through accumulated experience.

**Eventually:** The system identifies promising research directions from new arXiv papers, proposes projects with estimated impact and cost, runs them to completion with human oversight at key gates, releases artifacts, and monitors community adoption -- a self-sustaining research operation that gets better with every project it completes.

---

*This document is a living artifact. It will be revised as the platform matures, as we learn what works and what doesn't, and as the capabilities of the underlying AI systems evolve. The principles are durable. The specifics will change. That's the point.*
