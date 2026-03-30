# Community Strategy

**How Serre AI serves the research community. Not just papers -- artifacts.**

**Created**: 2026-03-11

---

## Philosophy

The most-cited papers in AI provide **tools**, not just insights. GSM8K (Cobbe et al., 2021) has 2000+ citations because researchers use it daily. BIG-Bench, HELM, SWE-Bench, MMLU -- these are infrastructure. A paper that introduces a benchmark used by 100 other papers has more impact than a paper cited 100 times for a sentence in Related Work.

Serre AI optimizes for **community adoption**, not just publication acceptance. Every research project must produce artifacts that other researchers can install, run, and build on. The paper is the narrative wrapper; the artifacts are the contribution.

Concretely, this means:
- Code ships before the paper is submitted, not after
- Benchmarks are pip-installable, not "available upon request"
- Datasets are on HuggingFace with proper cards, not buried in a .zip on a personal website
- Results are reproducible from a single `bash run.sh`, not from a 47-step manual process
- Leaderboards are maintained, not abandoned after publication

---

## Artifact Types

Every Serre AI research project produces six outputs. The paper is one of them.

### 1. Paper

- LaTeX, camera-ready, submitted to a top venue (NeurIPS, ICML, ACL, EMNLP, ICLR)
- arXiv preprint posted simultaneously with venue submission
- All theoretical claims formally stated with definitions, propositions, and proofs
- All empirical claims backed by confidence intervals, effect sizes, and statistical tests
- Reproducibility checklist completed (NeurIPS/ICML style)
- Appendix with full proofs, benchmark details, per-model results, and hyperparameters

### 2. Benchmark Suite

- Pip-installable Python package (e.g., `pip install reasongap`)
- CLI entry point for evaluation: `python -m reasongap.evaluate --model openai:gpt-4o --tasks B1,B2,B3`
- Programmatic API for integration into evaluation harnesses: `from reasongap import tasks, evaluate`
- Task specifications with controlled difficulty parameters
- Ground truth answers with verified correctness
- Evaluation metrics with reference implementations
- Comprehensive docstrings, type hints, and inline documentation
- `pytest` test suite verifying task generation, evaluation logic, and metric computation
- README with quickstart, API reference, and examples
- Apache 2.0 license

### 3. Dataset

- Hosted on HuggingFace Hub (e.g., `serre-ai/reasongap-benchmark`)
- Dataset card with: description, intended use, data format, column definitions, splits, usage examples, citation BibTeX, license, limitations, known issues
- Multiple splits: `test` (standard evaluation), `challenge` (harder subset), `diagnostic` (per-type breakdown)
- Evaluation results included as separate dataset (e.g., `serre-ai/reasongap-results`): model outputs, extracted answers, correctness labels, metadata
- CC-BY-4.0 license for data
- Versioned: dataset version matches paper version (v1.0 = submission data, v1.1 = camera-ready data)

### 4. Code Repository

- Public GitHub repository (e.g., `serre-ai/reasongap`)
- Clean directory structure: `src/`, `tests/`, `scripts/`, `data/`, `paper/`
- `requirements.txt` with pinned versions
- `run.sh` that reproduces all results end-to-end
- `expected_outputs/` directory with reference results for validation
- CI via GitHub Actions: tests pass, code lints, LaTeX compiles
- Tagged releases matching paper versions
- Issues enabled for community questions
- Apache 2.0 license for code

### 5. Blog Post

- 1500-word accessible summary published on `deepwork.site/blog/`
- Structure: motivation (why should practitioners care?), key finding (one sentence), methodology (high-level), results (with figures), practical implications (what should you do differently?), limitations, link to paper and code
- Written by the blog post agent, reviewed by human
- Cross-posted on social media with thread format
- Published within 48 hours of arXiv preprint
- Target audience: ML practitioners, not just researchers

### 6. Leaderboard

- Public page on `deepwork.site/leaderboards/<benchmark>`
- Auto-updated from PostgreSQL when new evaluation results are ingested
- Columns: model name, model family, parameter count, overall accuracy, per-task breakdown, CoT lift, evaluation date, submitted by
- Community submissions accepted via PR to `leaderboard-submissions/` directory in the benchmark repository
- Submission format: JSONL with model outputs, verified by CI before merge
- Historical tracking: shows how models improve over time
- Filterable by model family, size, evaluation condition

---

## Open Source Strategy

### Licensing

| Artifact | License | Rationale |
|----------|---------|-----------|
| Benchmark code | Apache 2.0 | Maximum adoption, allows commercial use |
| Evaluation data | CC-BY-4.0 | Open access with attribution |
| Analysis scripts | Apache 2.0 | Reproducibility requires open code |
| Paper source | arXiv license | Standard for preprints |
| Platform code (orchestrator, agents) | Apache 2.0 (after v1.0) | Meta-contribution: the methodology itself |

### Release Timeline

1. **At submission**: arXiv preprint + GitHub repo with benchmark code and evaluation scripts. Data on HuggingFace. Blog post on deepwork.site. This is non-negotiable -- no "code available upon request."
2. **At acceptance**: Tagged release matching camera-ready. Updated dataset with any revisions. Leaderboard live on deepwork.site.
3. **Post-publication**: Ongoing maintenance. New models added to leaderboard as they release. Bug fixes. Community PRs reviewed within 1 week.
4. **Platform open-source (v1.0 stable)**: Orchestrator, agent definitions, session runner, daemon. Documentation as blueprint for autonomous research workflows. Target: 3-6 months after first paper accepted.

### What We Keep Private

- API keys and credentials (obviously)
- Raw Claude Code session transcripts (may contain intermediate reasoning we don't want to bias future work)
- Internal project briefs before publication (avoid scooping risk)
- Budget details beyond what's in the paper (internal operational concern)

---

## Community Engagement

### Pre-Publication

- **Workshop submissions**: Submit early-stage ideas to venue workshops (e.g., NeurIPS workshops, ICML workshops). Lower bar, faster feedback cycle. Workshop papers can be expanded into main conference submissions.
- **arXiv preprints**: Post at time of submission. Get community feedback during review period. Update based on informal feedback before camera-ready.

### At Publication

- **Twitter/X thread**: 8-12 tweet thread summarizing key findings. Include one figure, one table, one surprising result. Tag relevant researchers whose work we build on. Post at 9am EST on a weekday.
- **Blog post**: Published on deepwork.site within 48 hours of preprint. Cross-posted where relevant (e.g., r/MachineLearning for empirical work).
- **GitHub repository**: Public with issues enabled. Pin "Getting Started" issue with quickstart guide.

### Post-Publication

- **GitHub Issues**: Respond to community questions within 48 hours. Triage: bugs get fixed in 1 week, feature requests get labeled and prioritized, questions get answered.
- **Leaderboard maintenance**: Add new models within 1 week of their release. Major model releases (GPT-5, Claude 4, Llama 4) evaluated within 48 hours and results posted.
- **Benchmark updates**: If a task is found to be trivially solvable by new models, add harder variants. Version the benchmark (v1.0, v1.1, v2.0) with clear changelog.
- **Citation of follow-up work**: Track papers that use our benchmarks or build on our framework. Cite them in updated versions. This builds goodwill and encourages adoption.

---

## Impact Metrics

Targets for each research project (first 12 months post-publication):

| Metric | Target | How We Track |
|--------|--------|-------------|
| Paper citations | 50+ | Semantic Scholar API, weekly check |
| Benchmark adoption | Used by 10+ other papers | Semantic Scholar citation context search |
| HuggingFace dataset downloads | 1,000+ | HuggingFace Hub API |
| GitHub stars | 100+ | GitHub API |
| Blog post views | 5,000+ | deepwork.site analytics |
| Leaderboard submissions | 20+ models | PR count in benchmark repo |
| Community Issues/PRs | 15+ | GitHub API |

These are leading indicators. The lagging indicator is: **does the community use our tools in their daily work?** If a researcher benchmarks a new model and includes our benchmark in their evaluation suite without us asking, that's success.

### Tracking Implementation

- Weekly cron job queries Semantic Scholar, HuggingFace Hub, and GitHub APIs
- Results stored in PostgreSQL `impact_metrics` table
- Dashboard view on deepwork.site showing trajectory per project
- Slack alert when milestones are crossed (first external citation, 100 downloads, 50 stars)

---

## Current Project Artifact Plans

### reasoning-gaps (NeurIPS 2026)

**Paper**: "On the Reasoning Gaps of Large Language Models: A Formal Characterization"
- 6-type reasoning gap taxonomy bridging computational complexity and empirical LLM evaluation
- 5 formal propositions with proofs connecting TC^0/NC^1/P complexity classes to observable model behavior
- Empirical evaluation across 11 models, 4 families, 9 diagnostic tasks, 3 conditions
- Key finding: CoT lift +0.271 for Type 2-3 gaps (complexity-bridgeable) vs +0.037 for Type 5-6 gaps (fundamental), confirming theoretical predictions

**Benchmark**: `reasongap` Python package
- 9 diagnostic tasks (B1-B9) with parameterized difficulty
- B1: multi-step arithmetic (Type 1 -- serial composition)
- B2: formula evaluation (Type 2 -- depth-bounded recursion)
- B3: list reversal (Type 2 -- sequence manipulation)
- B4: variable binding (Type 3 -- working memory)
- B5: graph reachability (Type 4 -- search/planning)
- B6: parity checking (Type 5 -- global computation)
- B7: compositional semantics (Type 3 -- binding + composition)
- B8: state tracking (Type 6 -- stateful computation)
- B9: recursive pattern matching (Type 4 -- recursive structure)
- Controlled difficulty via parameterized depth, length, and branching factor
- CLI: `pip install reasongap && python -m reasongap.evaluate --model openai:gpt-4o --tasks all`
- Includes 4 model clients (Anthropic, OpenAI, OpenRouter, vLLM) with rate limiting and retry

**Dataset**: `serre-ai/reasongap-benchmark` on HuggingFace
- 121,614+ evaluation instances across 11 models
- Columns: task, model, condition, input, expected_output, model_output, extracted_answer, correct, latency_ms, token_count
- Splits: `full` (all instances), `by_model` (per-model subsets), `by_type` (per-gap-type subsets)
- Results dataset: `serre-ai/reasongap-results` with aggregated accuracy, CIs, and CoT lift per model per task

**Code Repository**: `serre-ai/reasongap`
- Benchmark generation, evaluation, and analysis code
- `run.sh` reproducing all results from scratch
- `expected_outputs/` with reference accuracy numbers for validation
- GitHub Actions: pytest, lint, LaTeX compile

**Blog Post**: "Why Your LLM Fails at Reasoning: A Formal Taxonomy"
- 1500 words, practitioner-oriented
- Lead with the surprising finding: CoT helps for some reasoning failures but is provably useless for others
- Include the 6-type taxonomy as a practical diagnostic tool
- Practical takeaway: how to identify which type of failure your application hits, and what to do about it

**Leaderboard**: `deepwork.site/leaderboards/reasongap`
- 11 models at launch (9 complete + Sonnet 4 + o3)
- Per-task breakdown showing which gap types each model handles well
- Community submission pipeline via GitHub PR

### agent-failure-taxonomy (ACL 2027)

**Paper**: Taxonomy and diagnostic benchmark for agentic AI failure modes
- Systematic categorization of how LLM agents fail in multi-step tasks
- Diagnostic benchmark suite isolating specific failure modes
- Evaluation across agent frameworks and model families

**Benchmark**: `agentfail` Python package (planned)
- Diagnostic tasks isolating: planning failures, tool use errors, context loss, goal drift, hallucinated actions, recovery failures
- Controlled environments with known-correct action sequences

**Dataset**: `deepwork/agentfail-benchmark` on HuggingFace (planned)
- Agent traces with annotated failure points
- Multiple agent frameworks and model backends

**Blog Post**: "A Field Guide to Agent Failures" (planned)
- Practitioner-oriented guide to diagnosing and mitigating agent failure modes

**Leaderboard**: `deepwork.site/leaderboards/agentfail` (planned)

---

## Forge Platform as Meta-Contribution

The platform itself is a research artifact. The methodology -- autonomous AI agents conducting research, writing papers, running experiments -- is novel and worth documenting.

### What We Open-Source (after v1.0 stable)

**Orchestrator**: The daemon, session runner, project manager, and git engine. TypeScript, well-documented, tested. Other researchers can fork it to run their own autonomous research workflows.

**Agent Definitions**: The `.claude/agents/*.md` files that define researcher, writer, reviewer, scout, critic, and editor roles. These are prompt engineering artifacts that encode research methodology.

**Decision Protocol**: The `status.yaml` schema and decision logging pattern. A lightweight framework for autonomous AI decision-making with full auditability.

**Research Log Pattern**: The `research-log.md` append-only log for inter-session continuity. A simple solution to the problem of AI agents losing context across sessions.

### Documentation

- Architecture guide: how the daemon works, how agents are selected, how sessions run
- Setup guide: how to deploy your own Forge instance (VPS + PostgreSQL + Claude Code)
- Agent authoring guide: how to define new agent roles for your research domain
- Project template: `BRIEF.md` + `status.yaml` + `CLAUDE.md` starter files

### What This Enables

A single researcher with a $1,000/month budget can run an autonomous research lab that:
- Scans literature daily for relevant new work
- Maintains multiple research projects in parallel
- Writes papers with formal proofs, empirical evaluation, and statistical rigor
- Produces community artifacts (benchmarks, datasets, leaderboards)
- Tracks impact and maintains published work post-publication

This is the meta-contribution: not just the research papers Serre AI produces, but the demonstration that this workflow is viable, reproducible, and effective.
