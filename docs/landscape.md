# Competitive Landscape: Automated AI Research Systems

Last updated: 2026-03-11

This document surveys the current landscape of automated and semi-automated AI research systems. It covers production systems, tools, infrastructure, and critical analysis from the literature. Each entry includes an honest assessment of strengths, weaknesses, architectural insights, and relevance to Deepwork.

---

## Table of Contents

1. [Production Systems](#production-systems)
2. [Tools and Infrastructure](#tools-and-infrastructure)
3. [Critical Analysis from Literature](#critical-analysis-from-literature)
4. [Comparative Table](#comparative-table)
5. [Where Deepwork Fits](#where-deepwork-fits)

---

## Production Systems

### 1. AlphaEvolve (DeepMind, May 2025)

**What it is.** An evolutionary coding agent that uses an ensemble of Gemini models (Flash and Pro) to discover and optimize algorithms. It pairs program generation with automated evaluation in an evolutionary loop: generate candidate programs, evaluate them against a fitness function, select the best, mutate, repeat.

**Key results.** Improved upon the best known matrix multiplication algorithm (Strassen's) for specific matrix sizes. Across a benchmark of known algorithmic problems, it rediscovered state-of-the-art solutions 75% of the time and improved upon them in 20% of cases. Applied internally at Google to optimize data center operations, chip design, and mathematical kernel code.

**What it does well.**
- The evolutionary loop is genuinely general-purpose. The same framework works for combinatorial optimization, numerical algorithms, and heuristic design.
- Pairing generation with automated evaluation sidesteps the hallucination problem: wrong solutions are simply scored low and discarded.
- Ensemble approach (Flash for volume, Pro for quality) is a practical way to balance exploration cost against solution quality.

**Where it fails.**
- Requires a well-defined, automatically evaluable fitness function. This restricts it to domains where correctness or quality can be measured programmatically. Cannot handle subjective quality judgments, theoretical novelty, or tasks where evaluation itself is the hard problem.
- Not designed for open-ended research. It optimizes within a known problem formulation rather than discovering new problems or generating new theory.
- No persistent memory or learning across runs. Each evolutionary campaign starts fresh.

**Key architectural insight.** Separate generation from evaluation completely. Let the LLM be creative and prolific; let a deterministic evaluator be the quality filter. This is the most robust pattern in the landscape.

**Relevance to Deepwork.** The generate-evaluate separation is directly applicable. Our benchmark evaluation pipeline for reasoning-gaps follows the same pattern: generate model responses, evaluate against known ground truth. For future projects involving algorithm design or optimization, AlphaEvolve's evolutionary approach is worth studying.

---

### 2. FunSearch (DeepMind, Dec 2023/2024)

**What it is.** An LLM-based system that uses a generate-evaluate loop to search for mathematical functions that solve open problems. The LLM proposes candidate functions, an automated evaluator scores them, and the best candidates seed the next generation.

**Key results.** Published in Nature. First demonstration of an LLM-driven system making a genuine discovery on an open mathematical problem: it found new constructions for the cap set problem (a long-standing problem in extremal combinatorics), producing the largest known cap sets in certain dimensions.

**What it does well.**
- Demonstrated that LLMs can contribute to genuine mathematical discovery, not just rediscovery. This was a credibility milestone for the entire field.
- The key insight is searching in function space rather than solution space. The LLM generates programs that generate solutions, which is more compact and generalizable.
- Clean, interpretable output: the discovered functions can be analyzed by mathematicians to extract new structural insights.

**Where it fails.**
- Narrow applicability. Works best on problems where (a) solutions can be represented as short programs, (b) solution quality can be scored automatically, and (c) the search space is rich enough to benefit from LLM priors.
- No theoretical understanding of why or when it works. Success feels somewhat unpredictable.
- Computationally expensive for the class of results it produces.

**Key architectural insight.** Search in program space, not solution space. Programs are compact, composable, and can encode structural patterns that flat solutions cannot.

**Relevance to Deepwork.** The program-space search idea is powerful for benchmark design and analysis. When we need to find minimal examples that expose reasoning gaps, searching in the space of problem generators rather than individual problems is more effective.

---

### 3. AlphaProof (DeepMind, 2024; Nature Nov 2025)

**What it is.** A reinforcement learning system that proves mathematical theorems in Lean 4 (a formal proof language). It combines a language model for proof step generation with RL-based search, trained on a large corpus of formalized mathematics. Combined with AlphaGeometry 2 for geometry problems.

**Key results.** Solved 4 out of 6 problems at IMO 2024, achieving a score equivalent to a silver medal. When the score from AlphaGeometry 2 was combined, the system reached gold-medal-equivalent performance. By mid-2025, Gemini Deep Think achieved gold-level performance on IMO 2025.

**What it does well.**
- Formal verification eliminates hallucination entirely for the domain of mathematical proofs. If the Lean proof type-checks, it is correct. Period.
- RL training creates genuine mathematical capability over time, not just pattern matching.
- The combination of neural generation with formal verification is the gold standard for trustworthy AI-assisted mathematics.

**Where it fails.**
- Restricted to domains with formal verification infrastructure. Lean coverage of mathematics, while growing, is still a fraction of the field.
- Does not generate new conjectures or identify interesting problems. It proves statements it is given.
- Requires enormous compute for training and inference. Not accessible outside frontier labs.
- The gap between competition math and research math is significant. IMO problems are hard but well-posed; research problems require formulation, not just solution.

**Key architectural insight.** Formal verification as the evaluation function transforms proof search from a generative problem into a search problem with perfect feedback. This is the cleanest instantiation of the generate-evaluate paradigm.

**Relevance to Deepwork.** Our reasoning-gaps project uses formal complexity-theoretic claims that could benefit from machine-checked proofs. More broadly, the principle of grounding claims in verifiable formalism aligns with our methodology. We should track Lean formalization tools as they mature.

---

### 4. AI Co-Scientist (Google, Feb 2025)

**What it is.** A multi-agent system for scientific hypothesis generation and evaluation. Uses a generate-debate-evolve architecture: one agent generates hypotheses, multiple agents debate and critique them, and the system evolves the best hypotheses through iterative refinement.

**Key results.** Generated drug repurposing predictions that were subsequently confirmed through wet-lab experiments. Reduced hypothesis generation timelines from weeks to days in collaboration with domain scientists. Demonstrated practical utility in biomedical research.

**What it does well.**
- The debate mechanism provides a form of internal adversarial review. Hypotheses that survive multi-agent critique are more robust than those from single-pass generation.
- Designed for human-in-the-loop collaboration. Scientists provide domain constraints and evaluate output, while the system handles breadth of exploration.
- Practical validation: wet-lab confirmation is the strongest form of evidence that the system produces useful output.

**Where it fails.**
- Requires expensive domain-expert evaluation of output. The system generates hypotheses, but a human scientist must still determine which are worth pursuing.
- The debate mechanism can converge on plausible-sounding but incorrect hypotheses if all agents share the same training biases.
- Closed system. No published details on architecture sufficient to reproduce.
- Unclear how well it generalizes beyond biomedical applications.

**Key architectural insight.** Multi-agent debate as a quality filter. Instead of one model generating and one evaluating, multiple models argue, which surfaces different failure modes and assumptions.

**Relevance to Deepwork.** The debate/adversarial review pattern maps directly to our quality gate system. Our Gate 4 (adversarial review) should simulate this kind of multi-perspective critique. The generate-debate-evolve loop is worth implementing for hypothesis generation in future projects.

---

### 5. AI Scientist v1 (Sakana, Aug 2024) and v2 (Apr 2025)

**What it is.** End-to-end automated research paper generation. v1 was the first system to go from idea to written paper autonomously, at roughly $15 per paper. v2 introduced progressive agentic tree search for experiment design and VLM-based feedback for figure quality. v2 produced the first AI-generated paper accepted at an ICLR workshop.

**Key results.** v1 demonstrated that the full research pipeline (ideation, experiment, writing) could be automated end-to-end at trivial cost. v2 improved experiment design quality through tree search over experimental configurations and used vision-language models to assess figure quality and readability.

**What it does well.**
- Extremely low cost per paper makes it feasible to explore many ideas in parallel.
- Open-source, enabling community iteration and benchmarking.
- v2's tree search over experimental configurations is a good approach to avoiding the single-path failure mode.
- End-to-end demonstration: proved the concept is viable, even if quality is low.

**Where it fails.**
- Literature review is the critical weakness. v1 used keyword search over Semantic Scholar, which fundamentally cannot perform intellectual synthesis. The result: papers confidently classified well-known concepts as novel contributions. This is not a minor flaw; it means the system cannot determine whether its work is actually new.
- Paper quality is low by conference standards. The $15/paper figure is misleading because the papers are not publishable at top venues without significant human revision.
- No persistent state across runs. Each paper is generated from scratch, so the system cannot build on its own prior work.
- Experiment design, even in v2, is constrained to template-based variations. It cannot design genuinely novel experimental methodologies.

**Key architectural insight.** The failure of keyword-based literature review is the single most important lesson in this landscape. If a system cannot distinguish "no one has done X" from "X is well-known under different terminology," it will waste effort on rediscovery. Deep literature synthesis is a prerequisite, not an optional feature.

**Relevance to Deepwork.** AI Scientist is the closest system to what we are building, and its failures are our design requirements. Our literature integration system exists specifically because of AI Scientist's literature review failure. Our quality gates exist because AI Scientist has none. Our persistent state exists because AI Scientist's lack of memory means it cannot learn from its own work. AI Scientist is the baseline we must definitively surpass.

---

### 6. FARS (Analemma, Mar 2026)

**What it is.** Fully Automated Research System. A multi-agent system that ran for 228 hours continuously, producing 100 research papers, consuming 11.4 billion tokens at a cost of approximately $104,000 ($1,040/paper). Uses separate agents for ideation, planning, experiment execution, and writing.

**Key results.** The 100 papers received an average review score of 5.05 (on the standard 1-10 scale), compared to a human average of 4.21 at ICLR. This headline number is attention-grabbing but requires careful interpretation.

**What it does well.**
- Demonstrated sustained autonomous operation over 228 hours, which is an engineering achievement.
- The multi-agent architecture with specialized roles (ideation, planning, execution, writing) is a reasonable decomposition of the research process.
- Quantity enables portfolio effects: with 100 papers, even if most are mediocre, some may be genuinely good.

**Where it fails.**
- The 5.05 average score is misleading. FARS papers were scored by AI reviewers calibrated on ICLR reviews. The comparison with human ICLR average (4.21) is apples-to-oranges: ICLR submissions include many weak papers from inexperienced researchers, while FARS papers are optimized to look good to an automated reviewer. The relevant comparison would be FARS scores from human expert reviewers, which are not reported.
- At $1,040/paper, this is two orders of magnitude more expensive than AI Scientist with unclear quality improvement. The cost-quality tradeoff is not compelling.
- Quantity-focused: 100 papers in 228 hours means less than 2.3 hours per paper. This is incompatible with the kind of deep thinking that produces important research.
- No evidence of genuine novelty in any of the 100 papers. Volume without novelty is noise.

**Key architectural insight.** Sustained autonomous operation is achievable but insufficient. The bottleneck is not runtime or scale but research taste: the ability to distinguish important questions from trivial ones.

**Relevance to Deepwork.** FARS represents the opposite end of our design philosophy. We explicitly do not want to produce 100 papers; we want 3-4 papers that matter. FARS validates the multi-agent architecture but demonstrates that scaling quantity without quality produces expensive mediocrity. Our budget constraints ($1,000/month) are actually an advantage here: they force us to be selective.

---

### 7. AI-Researcher (HKUDS, NeurIPS 2025 Spotlight)

**What it is.** A three-stage framework for automated research: idea generation, experiment execution, and paper writing. Uses Claude as the backbone model, achieving 93.8% task completeness. Introduced Scientist-Bench, a benchmark for evaluating automated research systems. Available as a service at novix.science.

**Key results.** NeurIPS 2025 Spotlight paper, which is a strong endorsement of the framework's contribution. 93.8% completeness rate with Claude means the system rarely fails to produce output, though output quality is a separate question. Scientist-Bench provides a standardized way to compare systems.

**What it does well.**
- Scientist-Bench is a genuine contribution: the field needed a benchmark for automated research systems, and having one enables systematic comparison.
- Three-stage decomposition is clean and allows independent improvement of each stage.
- High completeness rate suggests robust engineering.
- Using Claude (rather than GPT-4) as backbone is a pragmatic choice given Claude's strength on long-form analytical tasks.

**Where it fails.**
- Completeness is not quality. A system can complete 93.8% of tasks while producing mediocre output for all of them.
- The three-stage pipeline is linear. Real research is iterative: experiments should feed back into hypotheses, failed experiments should trigger revision, and writing should reveal gaps in understanding.
- Limited discussion of novelty detection or literature synthesis quality.

**Key architectural insight.** Benchmark the benchmarker. Creating Scientist-Bench recognizes that we cannot improve automated research without measuring it. The meta-level contribution (how to evaluate automated research) may be more important than the system itself.

**Relevance to Deepwork.** Scientist-Bench is worth using to evaluate our own system. The three-stage framework provides a useful comparison point, but our iterative approach (hypothesize-formalize-test-assess-revise) is more faithful to actual research practice than a linear pipeline.

---

### 8. CodeScientist (Ai2, ACL Findings 2025)

**What it is.** A system that uses genetic search over paired paper-and-code artifacts to discover new scientific insights. It mutates both the conceptual framing (paper) and the implementation (code) in tandem, using execution results to guide evolution.

**Key results.** Identified 19 potential scientific discoveries, of which 6 were validated as genuinely novel by human experts. Published at ACL Findings 2025.

**What it does well.**
- The paired paper+code representation is clever. By evolving both together, the system maintains alignment between theory and implementation, which is a common failure mode in other systems.
- 6 human-validated discoveries is a meaningful result. These are not rediscoveries or trivial variations.
- Genetic search provides diversity that greedy or beam-search approaches miss.

**Where it fails.**
- 6 out of 19 validation rate (31.6%) means most "discoveries" are false positives. Human expert review is still required as a filter.
- Genetic search is computationally expensive and the search space grows combinatorially with the complexity of the paper+code artifact.
- Limited to computational science domains where code execution provides meaningful signal.

**Key architectural insight.** Co-evolve theory and implementation. Keeping them coupled prevents the drift that occurs when a system writes a paper about one thing and implements another.

**Relevance to Deepwork.** The paired theory+code evolution is relevant to our benchmark development process, where formal framework claims and benchmark implementations should evolve together. The 31.6% validation rate also calibrates expectations: even good systems produce mostly false leads.

---

### 9. Agent Laboratory (EMNLP 2025)

**What it is.** A three-phase system (literature review, experimentation, writing) that focuses on producing state-of-the-art ML code alongside papers. Uses o1-preview for the best results. Achieves 84% cost reduction compared to alternatives.

**Key results.** Published at EMNLP 2025. The generated code achieves competitive performance with human-written ML implementations. 84% cost reduction over comparable approaches.

**What it does well.**
- Focus on code quality alongside paper quality. In ML research, the code IS the contribution as much as the paper.
- Cost-effective: 84% reduction is significant for accessibility.
- Using o1-preview (a reasoning-focused model) for research tasks is a good model selection decision.

**Where it fails.**
- "State-of-the-art ML code" is narrower than it sounds. The system works well for standard ML pipelines (data loading, model training, evaluation) but not for novel architectures or unconventional approaches.
- Three-phase linear pipeline has the same limitations as AI-Researcher.
- Literature review phase quality is not discussed in detail, which usually means it is not strong.

**Key architectural insight.** Model selection matters enormously. Using a reasoning-specialized model (o1-preview) for research tasks outperforms using a general-purpose model, even if the general-purpose model is otherwise stronger.

**Relevance to Deepwork.** Validates the importance of model selection for different research phases. Our evaluation of reasoning-gaps uses different models for different purposes (Claude for analysis, open-source models as evaluation targets). The cost reduction approach is worth studying.

---

### 10. AgentRxiv (Mar 2025)

**What it is.** A preprint server designed for AI research agents to share and build upon each other's work. Agents can upload research artifacts, discover relevant prior work from other agents, and incorporate it into their own research.

**Key results.** Agents with access to prior research from the AgentRxiv archive showed 11.4% improvement in research quality. Multi-lab sharing (multiple agent teams contributing to the same archive) increased improvement to 13.7%.

**What it does well.**
- Addresses a fundamental problem: individual agent runs are isolated and cannot benefit from prior work. AgentRxiv provides the infrastructure for cumulative progress.
- The 11.4-13.7% improvement demonstrates that sharing is genuinely beneficial, not just overhead.
- Conceptually elegant: a preprint server for agents mirrors human research infrastructure.

**Where it fails.**
- Quality control is even harder for agent-generated preprints than for human preprints. Without curation, the archive can fill with noise.
- 13.7% improvement is modest. Human researchers benefit far more from reading prior work, suggesting agents are not yet good at extracting and applying insights from papers.
- Scalability concerns: as the archive grows, the signal-to-noise ratio may degrade.

**Key architectural insight.** Research is cumulative. Any system that treats each run as independent is leaving significant value on the table. Shared memory and shared artifacts are force multipliers.

**Relevance to Deepwork.** This validates our persistent state architecture. Our status.yaml, research logs, and cross-project knowledge bases serve the same function as AgentRxiv but within a single platform. We should consider whether publishing intermediate artifacts could benefit the broader community.

---

### 11. BioLab (Sep 2025)

**What it is.** An 8-agent system specifically designed for computational biology research. Uses 104 biological foundation models as specialized tools. Agents can query protein structure predictors, gene expression models, and other domain-specific models during research.

**Key results.** Designed antibodies with binding affinity (IC50) surpassing Pembrolizumab, a widely used cancer immunotherapy drug. This is a concrete, testable, high-value result.

**What it does well.**
- Deep domain specialization. Rather than being general-purpose, BioLab is built specifically for biology and has access to 104 domain-specific models.
- The 8-agent architecture allows specialization within the system: different agents handle different aspects of biological research.
- Producing antibodies that surpass an existing drug is a result with direct commercial and medical value.

**Where it fails.**
- Extremely narrow. The architecture and tool suite are specific to computational biology and do not generalize.
- Requires access to 104 foundation models, which is an enormous infrastructure requirement.
- In silico predictions of antibody binding need wet-lab validation. The IC50 claims are computational predictions, not experimental results.

**Key architectural insight.** Domain-specific tool access transforms what agents can do. General-purpose LLMs are weak at biology; LLMs with access to AlphaFold, gene expression models, and molecular dynamics simulators can make genuine contributions.

**Relevance to Deepwork.** The principle of domain-specific tool access applies to our work. For reasoning-gaps, our "tools" are evaluation infrastructure and complexity theory formalisms. For future projects, integrating domain-specific models (theorem provers, code analyzers, statistical packages) would follow BioLab's pattern.

---

### 12. AutoDiscovery (Ai2, Feb 2026)

**What it is.** A Bayesian surprise-driven engine for scientific discovery. Indexes 108 million abstracts and 12 million full papers. Uses surprise (deviation from expected patterns in the literature) to identify potential discoveries. Applied to cancer genomics and marine ecology.

**Key results.** Identified previously unrecognized patterns in cancer genomic data and marine ecology datasets. The Bayesian surprise metric provides a principled way to prioritize what is genuinely new versus what is expected.

**What it does well.**
- Bayesian surprise is a principled operationalization of "novelty." Rather than relying on keyword matching or embedding similarity, it quantifies how much a finding deviates from what the literature would predict.
- Massive literature coverage (108M abstracts) provides a strong prior for what is already known.
- Applied to multiple domains, suggesting some generality.

**Where it fails.**
- Surprise is not the same as importance. Many surprising findings are surprising because they are wrong, not because they are novel.
- The 108M abstract index requires significant infrastructure to build and maintain.
- Unclear how well it handles interdisciplinary discoveries, where a finding might be unsurprising in one field but novel in another.

**Key architectural insight.** Operationalize novelty quantitatively. "Is this new?" is a question that can be answered (approximately) by measuring surprise against a comprehensive literature model.

**Relevance to Deepwork.** The Bayesian surprise approach could improve our Gate 1 (literature novelty check). Currently our novelty check relies on synthesis and judgment; a quantitative surprise metric would add rigor. Worth integrating their approach or building a simplified version.

---

## Tools and Infrastructure

### OpenAI Deep Research

**What it is.** An agentic browsing system built on o3 that can perform multi-step research tasks: searching the web, reading documents, synthesizing information, and producing structured reports. Supports MCP (Model Context Protocol) connections for tool integration.

**Strengths.** Strong at information gathering and synthesis. MCP support enables integration with external tools. o3's reasoning capabilities make it effective for multi-step research tasks.

**Weaknesses.** A research assistant, not a research agent. It retrieves and synthesizes information but does not generate hypotheses, design experiments, or write papers. No persistent state across sessions.

**Relevance to Deepwork.** Useful as a tool within our pipeline, particularly for literature review and competitive landscape research. Not a competitor to our end-to-end approach.

### OpenAI Prism (Jan 2026)

**What it is.** A LaTeX-native research workspace powered by GPT-5.2. Provides an integrated environment for academic writing with citation management, equation rendering, and AI-assisted drafting.

**Strengths.** LaTeX-native design is a genuine differentiator for academic writing. Citation management reduces one of the most tedious aspects of paper writing. GPT-5.2 integration means strong language quality.

**Weaknesses.** Writing tool, not a research tool. Helps with the final 20% of the research process (paper writing) but not the preceding 80% (ideation, experimentation, analysis). No experiment execution or data analysis capabilities.

**Relevance to Deepwork.** Our paper writing phase could potentially use Prism, but integrating it would add a dependency without much benefit since Claude handles LaTeX writing well.

### OpenAI Codex

**What it is.** An autonomous engineering agent capable of 25-hour uninterrupted runs, processing up to 13 million tokens per session. Designed for large-scale code generation, refactoring, and engineering tasks.

**Strengths.** Extended runtime capability (25h) is unique. 13M token context enables work on large codebases. Autonomous operation without human babysitting.

**Weaknesses.** Engineering-focused. Strong at building software, not at scientific research. No understanding of experimental design, statistical analysis, or theoretical reasoning.

**Relevance to Deepwork.** Could be useful for infrastructure development (building the orchestrator, analysis pipeline tooling) but not for research itself.

### Stanford Agentic Reviewer (PaperReview.ai)

**What it is.** An automated paper review system that evaluates papers across 7 dimensions. Achieves Spearman correlation of 0.42 with human reviewers, compared to 0.41 for human-human inter-reviewer correlation.

**Strengths.** Matching human inter-reviewer correlation is a meaningful achievement. 7-dimension evaluation provides structured feedback rather than a single score. Publicly available.

**Weaknesses.** Correlation of 0.42 is still low in absolute terms, meaning reviews are only weakly predictive. Automated reviewers may share systematic biases that differ from human biases. Cannot assess true novelty (only perceived novelty based on training data).

**Relevance to Deepwork.** Directly relevant to our Gate 4 (adversarial review). We should use this or a similar system as part of our quality gate pipeline, while recognizing its limitations.

### LitLLM

**What it is.** A RAG-based (retrieval-augmented generation) system for literature review. Retrieves relevant papers and generates literature review sections with proper citations.

**Strengths.** 18-26% reduction in hallucinated references compared to unaugmented LLM generation. Grounds citations in actual papers rather than fabricating them.

**Weaknesses.** Retrieval quality determines output quality. Still generates hallucinated references 74-82% as often as baseline, which is not acceptable for publication. RAG approaches struggle with synthesis (connecting ideas across papers) versus retrieval (finding relevant papers).

**Relevance to Deepwork.** A partial solution to the literature review problem. Better than AI Scientist's keyword search but not sufficient for deep synthesis. Could be used as a first-pass filter before deeper analysis.

### HELM (Stanford)

**What it is.** Holistic Evaluation of Language Models. A standardized framework for evaluating LLMs across many dimensions: accuracy, calibration, robustness, fairness, bias, toxicity, and efficiency.

**Strengths.** Comprehensive and standardized. Widely adopted as a reference benchmark. Covers dimensions beyond accuracy.

**Weaknesses.** Static benchmarks are subject to contamination over time. Does not evaluate research-specific capabilities (hypothesis generation, experimental design, literature synthesis).

**Relevance to Deepwork.** Our reasoning-gaps benchmark suite (B1-B9) is complementary to HELM: we focus specifically on reasoning capabilities that HELM covers only shallowly.

### RE-Bench (METR)

**What it is.** A benchmark of 7 ML research engineering tasks designed to compare AI systems against human researchers. Humans are approximately 2x better than AI systems at the 32-hour mark.

**Strengths.** Direct human-AI comparison on realistic research tasks. Time-controlled evaluation (measuring performance at different time horizons) reveals how the gap changes with effort.

**Weaknesses.** Only 7 tasks, which limits statistical power. ML engineering is narrower than research in general. 2x gap may narrow quickly as models improve.

**Relevance to Deepwork.** Provides calibration for our expectations. At the 32h mark, AI is roughly half as effective as a human researcher on engineering tasks. For more open-ended research (our focus), the gap is likely larger.

---

## Critical Analysis from Literature

### "Why LLMs Aren't Scientists Yet" (arXiv:2601.03315, Jan 2026)

This paper identifies six failure modes of LLM-based research systems and proposes design principles to address them. It is the most important critical analysis of the field to date.

**Six failure modes:**

1. **Training data bias.** LLMs gravitate toward popular topics and well-known approaches. They have difficulty with genuinely novel ideas that are underrepresented in training data.

2. **Implementation drift.** Over long research runs, the system gradually drifts from its stated methodology. What it says it is doing and what it is actually doing diverge.

3. **Memory degradation.** In extended sessions, earlier context is lost or distorted. The system may contradict its own earlier findings without realizing it.

4. **Missing eureka instinct.** LLMs lack the sudden insight that characterizes breakthrough research. They can explore systematically but cannot make the creative leaps that connect disparate ideas.

5. **Insufficient domain intelligence.** General-purpose models lack the deep domain knowledge that specialist researchers accumulate over years. They can approximate but cannot match deep expertise.

6. **Weak scientific taste.** LLMs cannot reliably distinguish important questions from trivial ones, novel findings from rediscoveries, or genuine insights from plausible-sounding nonsense.

**Three unsolved problems:**

1. **Long-horizon coherence.** Maintaining a consistent research vision across days or weeks of work, with multiple experiments and revisions, remains unsolved. Current systems lose the thread.

2. **Research taste.** The ability to judge what is interesting, important, and worth pursuing. This is the hardest problem and there is no clear path to solving it with current architectures.

3. **Negative-space knowledge.** Knowing what does NOT work, what has been tried and failed, and why certain approaches are dead ends. This knowledge is rarely written down and therefore rarely in training data.

**Four design principles:**

1. **Start abstract, ground later.** Begin with high-level hypotheses and formalize progressively. Do not start with implementation details.

2. **Verify everything.** Assume all intermediate results may be wrong. Build verification into every step.

3. **Plan for failure.** Design research workflows that expect most ideas to fail. Kill criteria, fallback plans, and explicit go/no-go decisions should be built in.

4. **Log everything.** Create persistent, append-only records of all decisions, findings, and failures. This is the only way to build negative-space knowledge.

**Relevance to Deepwork.** This paper is essentially our design specification. Our architecture addresses each failure mode: persistent state addresses memory degradation, quality gates address weak scientific taste, the research log addresses negative-space knowledge, and the decision protocol addresses implementation drift. The three unsolved problems (long-horizon coherence, research taste, negative-space knowledge) are our primary research challenges as a platform.

---

### 25-Researcher Survey on AI Research Automation (arXiv:2603.03338, Mar 2026)

A survey of 25 AI researchers (mix of academia and industry) on their expectations for research automation.

**Key findings:**

- **Automation order.** Researchers expect coding to automate first, then mathematical derivation, then structured experimental research. Research taste and novel hypothesis generation are expected to automate last, if ever.

- **Institutional dynamics.** 17 out of 25 researchers expect the most advanced automated research systems to be kept internal to frontier labs, creating an asymmetry between industry and academia.

- **Epistemic divide.** Researchers at frontier labs (DeepMind, OpenAI, Anthropic) take the possibility of recursive self-improvement seriously. Academic researchers are more skeptical, viewing current systems as sophisticated tooling rather than genuine research agents.

- **Practical consensus.** All 25 agreed that current systems are useful for literature review, experimental code generation, and paper formatting. Disagreement is about whether systems can ever handle the creative core of research.

**Relevance to Deepwork.** The automation ordering (coding first, taste last) aligns with our experience: our benchmark implementation was straightforward, but ensuring the research question itself is novel and important required human judgment. The institutional asymmetry prediction is relevant to our positioning: we are building in the open, which puts us at a disadvantage for raw model access but an advantage for community contribution and reproducibility.

---

## Comparative Table

| System | Scope | Quality | Cost | Open Source | Key Innovation | Key Weakness |
|--------|-------|---------|------|-------------|----------------|--------------|
| AlphaEvolve | Algorithm optimization | High (within scope) | High (Google internal) | No | Evolutionary search + auto eval | Requires evaluable fitness function |
| FunSearch | Mathematical discovery | High (single result) | High | No | Program-space search | Narrow applicability |
| AlphaProof | Theorem proving | Very high | Very high | No | RL + formal verification | Restricted to formalized math |
| AI Co-Scientist | Hypothesis generation | Medium-high | Unknown | No | Multi-agent debate | Requires domain expert evaluation |
| AI Scientist v1/v2 | End-to-end papers | Low-medium | ~$15/paper | Yes | Full pipeline automation | Terrible literature review |
| FARS | End-to-end papers (bulk) | Medium (AI-scored) | ~$1,040/paper | No | 228h sustained operation | Quantity over quality; AI-scored |
| AI-Researcher | End-to-end papers | Medium | Moderate | Partial | Scientist-Bench | Linear pipeline |
| CodeScientist | Computational discovery | Medium-high | Moderate | Yes | Co-evolved paper+code | 31.6% validation rate |
| Agent Laboratory | ML papers + code | Medium | Low (84% reduction) | Yes | SOTA ML code generation | Limited to standard ML pipelines |
| AgentRxiv | Research sharing infra | N/A (infrastructure) | Low | Yes | Agent-to-agent knowledge sharing | Quality control unsolved |
| BioLab | Antibody design | High (in silico) | High | No | 104 domain-specific models | Extremely narrow domain |
| AutoDiscovery | Literature-based discovery | Medium-high | High (infrastructure) | No | Bayesian surprise for novelty | Surprise is not importance |

---

## Where Deepwork Fits

Deepwork occupies a distinct position in this landscape. We are not trying to compete on volume (FARS), algorithm optimization (AlphaEvolve), or narrow domain expertise (BioLab). Our position is defined by four design choices:

### 1. Quality over quantity

FARS produces 100 papers in 228 hours. AI Scientist produces papers at $15 each. We aim to produce 3-4 papers per year that are accepted at top venues (NeurIPS, ICML, ACL) and contain genuine contributions. This is a fundamentally different optimization target that requires different architecture: persistent state, iterative refinement, adversarial review, and explicit kill criteria.

### 2. Theory-practice bridge

Most systems in this landscape are either theoretical (AlphaProof, FunSearch) or empirical (AI Scientist, Agent Laboratory). Our reasoning-gaps project explicitly bridges both: formal complexity-theoretic framework grounded in large-scale empirical evaluation across 12 models and 9 diagnostic tasks. This bridging is rare and, based on community reception, valued.

### 3. Persistent state and cumulative learning

AI Scientist, FARS, and most other systems treat each run as independent. We maintain persistent state: status.yaml tracks project evolution, the research log captures negative-space knowledge, decisions are logged with rationale, and cross-session context is preserved. This is the AgentRxiv insight (cumulative research is better than isolated runs) but implemented within a single platform.

### 4. Reusable artifacts

Our research produces not just papers but reusable artifacts: benchmark suites (ReasonGap B1-B9), analysis pipelines, formal frameworks, and evaluation infrastructure. These have value beyond the papers they appear in. AI Scientist produces papers that are immediately disposable; we produce papers backed by tools the community can use.

### Honest assessment of our weaknesses

- **Scale.** We operate on a $1,000/month budget with 2 Claude Code Max accounts. We cannot match Google's compute or OpenAI's model access.
- **Research taste.** Despite our quality gates, we still depend heavily on human judgment for the highest-level question: "Is this research important?" The research taste engine (Research Radar, idea pipeline) helps but does not solve this.
- **Model dependence.** We are built on Claude. If Claude's capabilities regress or pricing changes dramatically, our platform is affected. We have no fallback model infrastructure.
- **Team of one.** Unlike FARS (multiple specialized agents running in parallel for 228 hours) or BioLab (8 agents + 104 models), our agent team is small. This limits throughput, though it matches our quality-over-quantity philosophy.

### Where we have an edge

The systems that produce the best results in this landscape (AlphaEvolve, AlphaProof, AI Co-Scientist) share a common pattern: they pair generation with rigorous evaluation, maintain coherent research direction, and iterate based on feedback. Our architecture follows this pattern, just at smaller scale. The systems that produce the worst results (AI Scientist v1, FARS) share a different pattern: linear pipelines, no persistent memory, no quality gates. We are architected to avoid these failure modes.

Our realistic ambition is not to match DeepMind's research output. It is to demonstrate that a small-scale, quality-focused, persistent-state research platform can produce work that matters -- and to do so transparently, with reusable artifacts, at a fraction of the cost.
