# Autonomous AI Research: The Karpathy Loop and Beyond

*Last updated: 2026-03-29*

The landscape of autonomous AI research systems as of early 2026. Covers the major projects, design patterns, results, and failure modes relevant to Forge's daemon architecture.

---

## The Karpathy Loop / AutoResearch

### Timeline

- **Feb 2, 2025** — Karpathy coins "vibe coding" ([X post](https://x.com/karpathy/status/1886192184808149383)). Collins Dictionary Word of the Year 2025.
- **Mar 6, 2026** — Open-sources `autoresearch` ([github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch)). 60K+ stars.
- **Mar 21, 2026** — "No Priors" podcast: describes the **"Loopy Era of AI"** — continuous self-improvement loops as standard at frontier labs ([transcript](https://podscripts.co/podcasts/no-priors-artificial-intelligence-technology-startups/andrej-karpathy-on-code-agents-autoresearch-and-the-loopy-era-of-ai)).

### Architecture

630 lines of Python. Three files:

| File | Role | Modifiable? |
|------|------|-------------|
| `prepare.py` | Data prep, tokenizer, eval | No (immutable) |
| `train.py` | GPT model, optimizer, training | Yes (agent edits this) |
| `program.md` | Natural-language instructions | Human edits |

**The loop:**
1. Agent reads `program.md` and `train.py`
2. Proposes modification with reasoning
3. Applies change, commits
4. Runs training for exactly **5 minutes** (wall-clock)
5. Evaluates `val_bpb` (validation bits-per-byte)
6. If improved: advance. If worse: revert.
7. Log results in TSV
8. Repeat — **"NEVER STOP"**

Fixed 5-minute budget = ~12 experiments/hour, ~100 overnight on a single GPU.

### Key Design Decisions

- **Single-file modification**: only `train.py`, keeping diffs reviewable
- **Simplicity gate**: 0.001 bpb improvement from "20 lines of hacky code" is rejected; same improvement from deletion is "definitely keep"
- **No context flooding**: output to `run.log`; agent reads results via grep
- **Stuck detection**: "give up after a few attempts" and move on
- **No human interaction**: "Do NOT pause to ask the human if you should continue"

### Results

- 700 experiments in 2 days continuous running
- 20 optimizations discovered → 11% speed improvement on larger model
- Found a bug in Karpathy's own attention implementation (missed after months of hand-tuning)
- Shopify CEO tested overnight: **19% performance gain** from 37 experiments

### Key Quotes

> "All LLM frontier labs will do this. It's the final boss battle."

> "The goal is not to emulate a single PhD student, it's to emulate a research community."

> "My manual coding skills are atrophying."

Sources: [Fortune](https://fortune.com/2026/03/17/andrej-karpathy-loop-autonomous-ai-agents-future/), [VentureBeat](https://venturebeat.com/technology/andrej-karpathys-new-open-source-autoresearch-lets-you-run-hundreds-of-ai), [NextBigFuture](https://www.nextbigfuture.com/2026/03/andrej-karpathy-on-code-agents-autoresearch-and-the-self-improvement-loopy-era-of-ai.html)

---

## Other Major Systems

### Sakana AI — AI Scientist

End-to-end system automating the full ML research lifecycle. Collaboration between Sakana AI, UBC, Vector Institute, Oxford.

- **v1 (Aug 2024)**: Linear pipeline
- **v2 (Apr 2025)**: Best-First Tree Search for parallel research exploration ([arXiv](https://arxiv.org/abs/2504.08066), [GitHub](https://github.com/SakanaAI/AI-Scientist-v2))
- **Nature paper (Mar 26, 2026)**: Published in Nature ([Sakana blog](https://sakana.ai/ai-scientist-nature/))

**Results**: First AI-generated paper accepted at ICLR 2025 workshop. Reviewer score 6.33 (top 45%, above acceptance threshold). Scored higher than 55% of human papers at workshop.

**Limitations**: None passed ICLR main conference track. External evaluations found hallucinations, faked results, overestimated novelty ([TechCrunch](https://techcrunch.com/2025/03/12/sakana-claims-its-ai-paper-passed-peer-review-but-its-a-bit-more-nuanced-than-that/), [critique arXiv](https://arxiv.org/abs/2502.14297)). "Embarrassing" citation errors.

### Google DeepMind — AlphaEvolve

Evolutionary coding agent using Gemini Flash (breadth) + Gemini Pro (depth). LLMs propose code changes, evaluators verify, evolutionary selection retains improvements.

- Beat Strassen's 1969 matrix multiplication algorithm
- Re-discovered SOTA for 75% of 50+ math problems, found better solutions for 20%
- 1% training time reduction for Gemini itself

Sources: [DeepMind blog](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/), [arXiv](https://arxiv.org/abs/2506.13131)

### Google DeepMind — AlphaProof / FunSearch

- **FunSearch (2023-24)**: LLM + evaluator evolutionary loop. First LLM-driven math discovery (cap set problem). [Blog](https://deepmind.google/blog/funsearch-making-new-discoveries-in-mathematical-sciences-using-large-language-models/)
- **AlphaProof (2024-25)**: RL-based formal math. Solved 4/6 IMO 2024 problems (silver medal). Nature AI, Nov 2025.

### Cognition — Devin

Autonomous software engineering agent. Plans, writes, debugs, tests, deploys.

- SWE-bench: 13.86% (vs 1.96% prior SOTA)
- Devin 2.0: 83% more tasks per compute unit
- Goldman Sachs pilot: 20% efficiency gains across 12,000 devs
- $10.2B valuation, $155M ARR in 18 months

Sources: [Cognition blog](https://cognition.ai/blog/devin-annual-performance-review-2025), [Contrary Research](https://research.contrary.com/company/cognition)

### OpenAI

- **Deep Research (Feb 2025)**: Agent that synthesizes hundreds of sources into reports. [Blog](https://openai.com/index/introducing-deep-research/)
- **Autonomous Researcher roadmap (Oct 2025)**: Altman on X: *"automated AI research intern by September 2026... true automated AI researcher by March 2028"*. Called it OpenAI's "North Star." ([TechCrunch](https://techcrunch.com/2025/10/28/sam-altman-says-openai-will-have-a-legitimate-ai-researcher-by-2028/), [MIT Tech Review](https://www.technologyreview.com/2026/03/20/1134438/openai-is-throwing-everything-into-building-a-fully-automated-researcher/))
- **Codex**: Cloud-based coding agent (GPT-5.3-Codex). Sandboxed, proposes PRs. Modes: `--suggest`, `--auto-edit`, `--full-auto`.

### Anthropic — Claude Code

- **Auto Mode (Mar 24, 2026)**: Two-layer classifier (fast filter + CoT reasoning) for auto-approving safe actions. 0.4% false positive, 5.7% false negative.
- **Autonomy research (Feb 2026)**: Analyzed 998K real-world tool calls. Experienced users auto-approve >40%. Claude pauses for clarification 2x more often than humans interrupt. 80% of tool calls have safeguards; only 0.8% are irreversible.
- SWE-bench: 80.9%. Uses 5.5x fewer tokens than Cursor for identical tasks.

Sources: [Measuring Agent Autonomy](https://www.anthropic.com/research/measuring-agent-autonomy), [Auto Mode](https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously)

### Others

- **AutoGPT**: 170K+ GitHub stars. Evolved to visual Agent Builder with step limits and human-in-the-loop.
- **The Ralph Loop** ([GitHub](https://github.com/snarktank/ralph)): Infinite loop feeding same prompt to coding agent. Progress in files/git, not context. Cursor plugin.
- **Manus AI** ([manus.im](https://manus.im)): Autonomous agent with cloud sandbox + sudo. Acquired by Meta (Dec 2025) for $2-3B.
- **CrewAI** ([crewai.com](https://crewai.com)): Multi-agent role-based orchestration. 100K+ certified devs. Powers automations at PwC, IBM, Capgemini, NVIDIA.

Community: [awesome-autoresearch](https://github.com/alvinunreal/awesome-autoresearch) — 50+ projects, benchmarks, and domain adaptations.

---

## Design Patterns

### A. Tight Experiment Loop (Karpathy)

```
modify code → time-boxed experiment → measure metric → keep/revert → repeat
```

Single file, single metric, fixed time budget. "NEVER STOP." Git-based checkpointing.

### B. Tree Search / Evolutionary (AI Scientist v2, AlphaEvolve)

```
generate candidates → evaluate in parallel → keep best → branch/evolve → repeat
```

Multiple candidates explored simultaneously. Breadth model (fast/cheap) + depth model (slow/accurate). Evaluator guards against hallucination.

### C. Multi-Agent Role-Based (CrewAI, Agent Laboratory)

```
planner → experimenter → critic → writer → reviewer
```

Specialized agents with defined roles. Pre-registration pipeline for expensive experiments.

### D. Stateless Iteration (Ralph Loop)

```
while PRD not complete: read files + git → plan → execute → commit → repeat
```

Same prompt every time. Progress lives in files and git, not context window. Each iteration is context-independent.

### Quality Control

| Pattern | Used by |
|---------|---------|
| Objective metrics (val_bpb, test pass rate) | AutoResearch, AlphaEvolve |
| Revert-on-regression (git) | AutoResearch, Forge |
| Simplicity gates | AutoResearch |
| Cost budgets (time/tokens/spend) | AutoResearch, Forge |
| Two-layer safety classifiers | Claude Code |
| Stuck detection ("give up after N") | AutoResearch, Forge |
| Pre-registration for expensive experiments | Forge |

---

## Failure Modes

1. **Low creativity / local optima** — Agents make incremental improvements, rarely paradigm shifts. AutoResearch GitHub issue #22: "Low creativity."
2. **Hallucination and fabrication** — AI Scientist v2 produced faked results even in peer-reviewed work. Citation errors persist.
3. **Model collapse in feedback loops** — Incorrect outputs fed back as training data degrade quality.
4. **Context window exhaustion** — Long-running agents lose context. Ralph Loop's approach: encode state in files/git.
5. **Cost spirals** — Early AutoGPT notorious for burning API credits. Modern: time budgets, step limits.
6. **Metric overfitting** — Agents optimize measured metric but miss broader quality. Simplicity gates partially address this.
7. **Stuck loops** — Cannot recover from errors, keep trying same failed approach. Mitigation: attempt limits.
8. **Human disengagement** — Experienced users increase auto-approve rates, stop questioning results.
9. **Workshop vs. conference quality gap** — AI Scientist accepted at workshop but not main track.
10. **Scaling from single-file to multi-system** — Karpathy's loop works on one GPU/one file. Multi-system research remains unsolved.

---

## Relevance to Forge

Forge's daemon architecture shares DNA with these systems but occupies a distinct niche:

| Dimension | AutoResearch | AI Scientist | Forge |
|-----------|-------------|--------------|----------|
| Scope | Single training loop | Full paper pipeline | Multi-project research + engineering |
| Metric | val_bpb | Reviewer score | Quality gate (human + automated) |
| Checkpoint | Git branch | Tree search | Git worktree branches |
| Cost control | 5-min time budget | Token limits | Tiered models + daily caps + per-project limits |
| Stuck handling | "Give up after few attempts" | Tree backtracking | Fingerprint comparison + session limits |
| Human role | Write `program.md` | Define research area | Write briefs, review, override |
| Output | Optimized train.py | Papers | Papers, experiments, code, infrastructure |

Key differentiators:
- **Multi-project orchestration** — not a single loop but a scheduler across concurrent research projects
- **Tiered model selection** — Opus for theory/writing, Sonnet for research/engineering, Haiku for scanning
- **Linear integration** — issues drive the loop, not a static program.md
- **Quality gates with human review** — score <40 retries, <70 goes to In Review, not just keep/revert
- **Output classification** — distinguishes research from infrastructure from noise

Key risks shared with the field:
- Stuck loops (addressed: fingerprint detection, session limits)
- Cost spirals (addressed: daily caps, per-project limits, tiered models)
- Quality drift (addressed: quality gates, commit gates)
- Human disengagement (partially addressed: Slack notifications, Linear tracking)
