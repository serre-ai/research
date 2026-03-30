# Serre AI Methodology

Last updated: 2026-03-11

This document defines how autonomous research works in Forge. It is the methodology reference for all research projects on the platform. Every agent session should be consistent with the principles and processes described here.

---

## Table of Contents

1. [The Research Loop](#1-the-research-loop)
2. [Research Taste Engine](#2-research-taste-engine)
3. [Literature Integration](#3-literature-integration)
4. [Experiment Design Standards](#4-experiment-design-standards)
5. [Quality Gates](#5-quality-gates)
6. [The Research Log](#6-the-research-log)
7. [Decision Protocol](#7-decision-protocol)
8. [Venue Strategy](#8-venue-strategy)

---

## 1. The Research Loop

Research is not a pipeline. It does not flow from literature review to hypothesis to experiment to paper in a straight line. Research is an evolutionary process: ideas are born, tested, revised, and sometimes killed. The Serre AI research loop reflects this reality.

### The Core Cycle

```
Hypothesize --> Formalize --> Test --> Assess --> Revise or Kill
     ^                                              |
     |                                              |
     +----------------------------------------------+
```

Every research project iterates through this cycle multiple times. A single project may execute dozens of micro-iterations before converging on a publishable result.

**Hypothesize.** Generate a specific, testable claim about the world. This is not "explore topic X" but "we predict that Y because Z." Hypotheses must be precise enough to be falsified.

**Formalize.** Translate the hypothesis into a precise framework: formal definitions, mathematical statements, or concrete experimental predictions. This step forces clarity. Vague hypotheses become precise claims, and many hypotheses that sounded good in natural language reveal themselves as trivially true or unfalsifiable when formalized.

**Test.** Design and execute experiments or proofs that evaluate the formalized claim. Tests must be designed before results are seen (pre-registration). The test should be capable of disproving the hypothesis, not just confirming it.

**Assess.** Evaluate results honestly. Does the data support the hypothesis? How strongly? Are there confounds? What alternative explanations exist? Assessment must be ruthless: we are looking for reasons the result might be wrong, not reasons it might be right.

**Revise or Kill.** Based on the assessment, either revise the hypothesis (narrow it, generalize it, add conditions) and re-enter the cycle, or kill the direction entirely. Killing is not failure; it is information. A killed hypothesis prevents wasted effort on a dead end.

### Micro-Iterations

Within each phase of a project, the same cycle operates at smaller scale:

- During benchmark design, each task goes through hypothesize (what gap should this task expose?), formalize (what is the task specification?), test (do pilot evaluations show the expected pattern?), assess (is the difficulty curve well-calibrated?), revise/kill (adjust parameters or drop the task).
- During paper writing, each claim goes through hypothesize (what should this section argue?), formalize (write the precise statement), test (does the evidence in our data support it?), assess (would a hostile reviewer accept this?), revise/kill (rewrite or remove the claim).

### Kill Criteria

Every project and every sub-direction has explicit kill criteria defined at the outset. These are conditions that, if met, trigger immediate abandonment of the direction. Kill criteria are checked automatically by the daemon at each cycle.

Examples from the reasoning-gaps project:
- If the formal framework cannot produce at least 3 non-trivial, testable predictions, kill the framework and redesign.
- If fewer than 2 out of 3 model families show the predicted pattern, the prediction fails.
- If a benchmark task shows ceiling effects (>95% accuracy) or floor effects (<5% accuracy) across all models, the task is uninformative and should be replaced.

Kill criteria prevent the sunk cost fallacy. When a direction is not working, the criteria force the decision rather than allowing the project to drift.

### Results That Contradict Predictions

When experimental results contradict a theoretical prediction, this triggers a mandatory revision cycle, not silence. The response is never to ignore the contradiction or to quietly adjust the prediction after seeing the data. The protocol is:

1. Log the contradiction explicitly in the research log.
2. Generate at least three candidate explanations for the discrepancy.
3. Design a targeted experiment to distinguish between explanations.
4. If the theory is wrong, revise the theory and re-derive predictions.
5. If the experiment is flawed, fix the experiment and re-run.

The reasoning-gaps project encountered this with the budget_cot B2 anomaly: CoT was predicted to help on Boolean formula evaluation, but the budget_cot condition showed a -0.254 drop. Investigation revealed the cause was a miscalibrated token budget (flat 20-word limit for exponentially complex formulas), not a failure of the theory. The fix was identified and queued for re-evaluation. This is the correct response: investigate, explain, fix.

---

## 2. Research Taste Engine

Research taste -- the ability to distinguish important questions from trivial ones, novel findings from rediscoveries, and genuine insights from plausible-sounding noise -- is the hardest problem in automated research. We do not claim to have solved it. We have built systems that approximate it.

### Research Radar

A daily scan of new publications to maintain awareness of the field.

**Sources:**
- arXiv: Daily RSS feeds for relevant categories (cs.AI, cs.CL, cs.LG, cs.CC, stat.ML)
- Semantic Scholar: API queries for papers citing our key references
- Conference proceedings: Major venue proceedings as they are released

**Processing:**
- Each new paper is scored on relevance to active projects (0-10 scale based on keyword overlap, citation graph proximity, and abstract semantic similarity)
- Papers scoring above threshold (7+) are flagged for detailed reading
- The scout agent reads flagged papers and updates per-project related-work knowledge bases

**Output:**
- Weekly digest of relevant new papers per project
- Alert if a paper appears to directly overlap with or scoop active work
- Trend tracking: which topics are gaining or losing attention

### Idea Pipeline

Ideas for new projects and new directions within existing projects are maintained in a ranked backlog.

**Format** (in `ideas.yaml`):
```yaml
- id: idea-001
  question: "Do reasoning gaps narrow differently for code-trained vs text-trained models?"
  hypothesis: "Code-trained models close compositional gaps faster due to structured training data"
  novelty_estimate: 7  # 1-10, based on literature search
  effort_estimate: medium  # low/medium/high
  venue_fit: ICML 2027
  status: backlog
  added: 2026-03-11
  notes: "Would extend reasoning-gaps framework. Requires access to code-trained model variants."
```

**Ranking criteria (in order of priority):**
1. Novelty: Is this actually new? Score based on Research Radar and literature search.
2. Importance: Does the answer matter? Would the community change behavior based on the result?
3. Feasibility: Can we execute this within budget and timeline?
4. Venue fit: Is there a natural venue for this work?

**Lifecycle:**
- Backlog: Idea recorded, not yet evaluated in depth
- Evaluated: Novelty and feasibility assessed, ranked against other ideas
- Active: Promoted to a project with BRIEF.md, status.yaml, and CLAUDE.md
- Killed: Removed from consideration with documented reason
- Published: Resulted in a submitted or published paper

### Kill Criteria (Project Level)

Before any project is promoted from evaluated to active, it must have explicit kill criteria. These are the conditions under which we abandon the project entirely, not just revise it.

Standard kill criteria applied to all projects:
- **Literature scoop.** If a paper appears during execution that substantially overlaps our contribution, kill or pivot.
- **Theoretical dead end.** If formalization reveals the core claim is trivially true, unfalsifiable, or already known, kill.
- **Empirical null result.** If experiments across all model families show no significant effect, the hypothesis is wrong. Kill.
- **Budget overrun.** If projected cost to completion exceeds allocated budget by more than 50%, kill or descope.

### Portfolio Management

We maintain multiple active projects at different stages, balancing exploration (early-stage, high-risk ideas) against exploitation (mature projects nearing completion).

**Target portfolio:**
- 1-2 mature projects in paper-writing or revision phase
- 1-2 mid-stage projects in experimentation phase
- 2-3 early-stage projects in literature review or formalization phase

**Allocation principle:** Borrow from Ethan Perez's formulation -- the goal is to reduce uncertainty at the fastest possible rate. This means:
- Early-stage projects should run the cheapest, fastest experiments first to determine whether the direction is viable.
- Mid-stage projects should focus on the experiments most likely to change the conclusions.
- Mature projects should focus on robustness checks and adversarial review.

At any given time, the portfolio should be generating information that helps us make better decisions about where to invest effort.

---

## 3. Literature Integration

The single most common failure mode in automated research systems is inadequate literature review. AI Scientist (Sakana) used keyword search over Semantic Scholar and repeatedly classified well-known concepts as novel discoveries. This is unacceptable.

Literature integration in Forge is not a phase that happens once at the beginning of a project. It is a continuous process that runs throughout the project lifecycle.

### The Problem with Keyword Search

Keyword search finds papers that use the same words. It does not find papers that address the same ideas using different terminology. This is not a minor limitation; it is a fatal one. Example: a search for "reasoning gaps in language models" will not find papers on "compositionality failures in neural sequence models" even though they address exactly the same phenomenon.

### Our Approach: Deep Synthesis

Literature integration operates at three levels:

**Level 1: Coverage.** Ensure we have found all relevant prior work. This uses multiple strategies:
- Keyword search (necessary but insufficient)
- Citation graph traversal: papers that cite our key references, and papers that those papers cite
- Author tracking: follow prolific researchers in the area
- Semantic search: embedding-based similarity to find terminologically different but conceptually related work
- Cross-disciplinary search: check adjacent fields (cognitive science, formal methods, programming languages) for relevant work

**Level 2: Understanding.** For each relevant paper, extract not just the result but the intellectual context:
- What question does this paper answer?
- What assumptions does it make?
- What does it NOT address?
- How does it relate to our specific claims?
- Where does it disagree with other papers we have read?

**Level 3: Synthesis.** Build a map of the intellectual landscape:
- What are the major schools of thought?
- Where is consensus? Where is active disagreement?
- What questions have been asked but not answered?
- What questions have not been asked at all?
- Is our proposed contribution genuinely new, or is it a rediscovery?

### Persistent Related-Work Knowledge Base

Each project maintains a knowledge base of related work that is updated throughout the project lifetime. This is stored in `notes/00-literature-synthesis.md` and related files.

The knowledge base is structured by theme, not by paper. Each theme includes:
- Key papers and their contributions
- Points of agreement and disagreement
- Open questions
- How the theme relates to our work

### The Scout Agent

A dedicated agent (or agent task) that runs periodically to:
- Check for new papers relevant to active projects
- Update the related-work knowledge base
- Flag papers that may scoop or overlap with active work
- Identify emerging techniques or results that could change our approach

### The Critical Test

Before any paper is submitted, the related-work section must pass a specific test: for every claim of novelty in the paper, we must be able to articulate why existing work does not already make this contribution. "We searched and did not find it" is insufficient. "We found work X, Y, and Z in this area, and our contribution differs because..." is required.

The distinction between "no one has done X" and "X is well-known under different terminology" must be explicitly addressed. This is where AI Scientist failed, and it is the most important check we perform.

---

## 4. Experiment Design Standards

All experiments in Forge follow these standards. These are not guidelines; they are requirements.

### Pre-Registration

Before running any experiment, the analysis plan must be specified:
- Hypotheses to test (with directional predictions)
- Statistical tests to use
- Significance thresholds
- What constitutes a "positive" versus "negative" result

This prevents p-hacking (running many analyses and reporting only the significant ones) and HARKing (hypothesizing after results are known). The analysis plan is committed to git before any data is collected.

Example from reasoning-gaps:
```
Pre-registered analysis plan (committed 2026-03-10):
- 6 primary analyses with specific hypotheses and tests
- 3 secondary/exploratory analyses (clearly labeled as exploratory)
- Bootstrap confidence intervals (10,000 resamples)
- McNemar's test for paired comparisons
- Effect sizes (Cohen's h) for all significant results
- Bonferroni correction for multiple comparisons
```

### Controlled Difficulty Parameters

Every benchmark and experimental task must have difficulty parameters that are explicitly controlled and varied. This serves two purposes:
1. It prevents the experiment from being informative at only one difficulty level.
2. It allows us to characterize how performance changes with difficulty, which is often more interesting than a single accuracy number.

For reasoning-gaps, each benchmark task (B1-B9) has difficulty parameters:
- B1 (Multi-step Arithmetic): number of operations (3, 5, 7)
- B2 (Boolean Formula Evaluation): formula depth (3, 5, 7)
- B3 (Variable Binding): number of variables and substitution depth
- And so on for each task.

### Multiple Model Families

All experiments must include models from at least 3 different families. This prevents results from being artifacts of a single model's training data or architecture.

For reasoning-gaps, the evaluation matrix includes:
- Anthropic: Haiku 4.5, Sonnet 4.6
- OpenAI: GPT-4o-mini, GPT-4o, o3
- Open-source: Llama 3.1 (8B, 70B), Ministral (8B), Mistral Small (24B), Qwen 2.5 (7B, 72B)

This covers 3 commercial families and 3 open-source families, with within-family scale comparisons.

### Statistical Rigor

Minimum standards for all statistical claims:

- **Confidence intervals.** All point estimates must be accompanied by 95% confidence intervals. Bootstrap CIs (10,000 resamples) are the default method.
- **Effect sizes.** Statistical significance alone is insufficient. Report effect sizes (Cohen's d, Cohen's h, or odds ratios as appropriate) for all comparisons.
- **Multiple comparison correction.** When running multiple tests, apply Bonferroni correction or control false discovery rate (Benjamini-Hochberg).
- **Paired tests.** When comparing conditions on the same instances, use paired tests (McNemar's for binary, paired t-test or Wilcoxon signed-rank for continuous).
- **Sample size justification.** For each experiment, calculate or justify the sample size needed for adequate statistical power.

### Budget Sensitivity Analysis

Every experiment plan includes a budget estimate and a sensitivity analysis:
- What is the minimum number of instances needed for statistical power?
- What is the cost per instance for each model?
- What is the total budget for the full experiment matrix?
- What happens if we reduce the matrix (fewer models, fewer difficulty levels, fewer instances)?

This analysis is performed before experiments are run, and the budget is approved (or the matrix is reduced) before any API calls are made.

Example from reasoning-gaps:
```
Full matrix: 12 models x 9 tasks x 3 conditions x ~500 instances = ~162,000 evaluations
Estimated cost: ~$370 (ranging from $0.22 for open-source via OpenRouter to $272 for Opus)
Decision: Run 9 models first (~$83), add Sonnet 4.6 ($55) and o3 ($40), defer Opus ($272)
```

### Ablation Studies

For any system or method with multiple components, ablation studies are required: remove or disable each component independently and measure the effect. This determines which components actually contribute and which are inert.

For reasoning-gaps, the ablation is built into the experimental design: the three conditions (direct, chain-of-thought, budget-constrained CoT) are ablations of reasoning support.

---

## 5. Quality Gates

Every project passes through five quality gates before submission. Each gate has explicit pass/fail criteria. Passing a gate is required to proceed; failing triggers a specific remediation protocol.

### Gate 1: Literature Novelty Check

**Question:** Is this work actually new?

**Pass criteria:**
- Comprehensive literature search completed (all three levels: coverage, understanding, synthesis)
- For every novelty claim, an explicit argument for why existing work does not subsume it
- No existing paper found that makes substantially the same contribution
- At least 3 reviewers would agree this is a novel contribution (simulated via adversarial prompting)

**Fail protocol:**
- If existing work is found that subsumes the contribution, either (a) pivot to a genuinely novel angle, or (b) kill the project.
- If the contribution is incremental rather than novel, either (a) strengthen the contribution, or (b) target a workshop instead of a main conference.

### Gate 2: Theoretical Soundness Review

**Question:** Are the theoretical claims correct, precise, and well-justified?

**Pass criteria:**
- All definitions are formally stated (no ambiguity in what is being claimed)
- All propositions and theorems have complete proofs or rigorous proof sketches
- Assumptions are explicitly stated and justified
- Claims are conditional where appropriate (e.g., "if TC^0 != NC^1, then...")
- No logical gaps or circular reasoning

**Fail protocol:**
- If a proof has a gap, fill the gap or weaken the claim to what can be proven.
- If a definition is ambiguous, formalize it precisely and check whether the results still hold.
- If an assumption is unjustified, either justify it or make it an explicit limitation.

### Gate 3: Experimental Rigor Review

**Question:** Are the experiments well-designed, properly executed, and reproducible?

**Pass criteria:**
- Analysis plan was pre-registered before data collection
- Statistical tests are appropriate for the data type and comparison
- Confidence intervals and effect sizes are reported for all claims
- Multiple comparison correction is applied where needed
- Results are reproducible (code, data, and random seeds are available)
- No selective reporting (all pre-registered analyses are reported, including null results)

**Fail protocol:**
- If statistical tests are inappropriate, re-analyze with correct tests.
- If results are not reproducible, debug and re-run.
- If selective reporting is detected, report all analyses and adjust conclusions accordingly.

### Gate 4: Adversarial Review

**Question:** Would a hostile but fair reviewer at the target venue accept this paper?

**Procedure:**
- Simulate three reviewers with different perspectives:
  - Reviewer 1: Theory expert who will scrutinize formal claims
  - Reviewer 2: Empiricist who will scrutinize experimental methodology
  - Reviewer 3: Skeptic who will question the motivation, novelty, and significance
- Each reviewer writes a full review (summary, strengths, weaknesses, questions, score)
- The paper must achieve an average score above the acceptance threshold for the target venue

**Pass criteria:**
- Average simulated score at or above venue acceptance threshold
- No reviewer identifies a fatal flaw (a weakness that cannot be addressed with revision)
- All reviewer questions have satisfactory answers

**Fail protocol:**
- Address all weaknesses identified by reviewers.
- If a fatal flaw is identified, determine whether it can be fixed. If not, the paper is not ready for this venue.
- Re-run the adversarial review after revision until it passes.

### Gate 5: Community Value Check

**Question:** Does this work produce artifacts that the community can use?

**Pass criteria:**
- At least one reusable artifact (benchmark, dataset, codebase, framework, tool)
- Artifact is documented, tested, and publicly accessible
- The artifact has value independent of the paper (someone who does not read the paper can still use it)
- Clear instructions for reproduction and extension

**Fail protocol:**
- If no reusable artifact exists, create one. Extract the most generalizable component of the work and package it.
- If the artifact exists but is undocumented, document it.
- If the artifact requires the paper for context, add standalone documentation.

---

## 6. The Research Log

Every project maintains an append-only research log. This is the institutional memory of the project: what was tried, what worked, what failed, and why.

### Purpose

The research log addresses the negative-space knowledge problem identified in "Why LLMs Aren't Scientists Yet." Most published papers describe what works. They do not describe the dozens of approaches that were tried and failed. This missing knowledge leads to wasted effort: other researchers (and other agent sessions) rediscover the same failures.

The research log captures this negative-space knowledge and makes it available to all future agent sessions.

### Format

The research log is stored in `notes/` as a series of timestamped session notes and thematic documents. Each entry includes:

```
## [Date] - [Topic]

### What was attempted
[Description of the approach, including motivation]

### What happened
[Factual description of results]

### Why it worked / didn't work
[Analysis of the result, including root cause for failures]

### Implications
[What this means for the project going forward]

### Decision
[What was decided as a result, referencing decisions_made in status.yaml if applicable]
```

### Rules

1. **Append-only.** Entries are never edited or deleted. If an earlier entry is wrong, add a new entry that corrects it with a reference to the original.

2. **Read before work.** Every agent session begins by reading the research log (or at minimum the most recent entries and any entries tagged as critical). This prevents rediscovery of known failures.

3. **Log failures explicitly.** Successful results are easy to remember and will appear in the paper. Failures are easy to forget and will not appear anywhere unless logged. The log exists primarily for failures.

4. **Log reasoning, not just outcomes.** "Approach X failed" is insufficient. "Approach X failed because Y, which means Z will also fail" is useful.

5. **Cross-reference decisions.** When a log entry leads to a decision, reference the corresponding entry in `decisions_made` in `status.yaml`. When a decision is made, reference the log entry that motivated it.

### Example from Reasoning-Gaps

The reasoning-gaps project has accumulated significant research log entries, including:

- Literature synthesis identifying the gap between complexity-theoretic bounds and empirical failure characterization (notes/00-literature-synthesis.md)
- Detailed analysis of transformer expressiveness results and their implications (notes/01-transformer-expressiveness.md)
- Session notes documenting the budget_cot B2 anomaly investigation (notes/SESSION-2026-03-10-analysis-infrastructure.md)
- Framework design evolution from initial taxonomy to final 6-type system (notes/05-formal-framework.md)

Each of these documents captures reasoning and decisions that would be lost without the log.

---

## 7. Decision Protocol

All research decisions in Forge are made autonomously by Claude. No human approval is required for standard research decisions. This is a deliberate design choice: requiring human approval creates bottlenecks that slow research to the pace of human availability. Autonomous decision-making with transparent logging enables 24/7 operation while maintaining accountability.

### Decision Categories

**Autonomous (no escalation required):**
- Research direction within an active project
- Experimental design and methodology
- Model selection and evaluation matrix
- Statistical methods and analysis approach
- Paper framing, structure, and argumentation
- Budget allocation within project limits
- Tool and infrastructure choices
- Formatting, organization, naming conventions

**Escalate to human for:**
- Single expenditure exceeding $100
- Project scope changes (adding or removing major research questions)
- Kill decisions (abandoning a project entirely)
- Venue selection and submission timing
- Commitments to external collaborators
- Any decision with irreversible consequences beyond the project

### Decision Format

Every non-trivial decision is logged in `decisions_made` in the project's `status.yaml`:

```yaml
- date: 2026-03-11
  decision: "Description of what was decided"
  rationale: "Why this option was chosen over alternatives"
```

For critical decisions (research direction, methodology, theoretical claims, paper scope), the decision entry should also include:
- Options that were considered
- Why the chosen option was preferred
- What would change the decision (conditions for revisiting)

### Decision Properties

**Decisions are immutable once logged.** A decision can be superseded by a later decision, but the original entry is never edited or deleted. This creates an auditable trail of how the research evolved.

**Decisions must have rationale.** "We decided X" is insufficient. "We decided X because Y, and not Z because W" is required. The rationale is the most valuable part of the log: it captures the reasoning that led to the choice.

**Decisions must be timely.** The purpose of autonomous decision-making is speed. When a decision point is reached, decide and proceed. Do not defer decisions unless new information is expected soon that would change the outcome.

### Extended Thinking

For critical decisions (research direction, methodology, theoretical claims, paper scope), agents must use extended thinking -- the highest reasoning level available. This ensures that important decisions receive proportional deliberation rather than being made hastily.

Lower-stakes decisions (formatting, organization, tool selection) should be made quickly without extended deliberation. The goal is to spend thinking time in proportion to decision importance.

---

## 8. Venue Strategy

Research quality and venue fit are distinct dimensions. A strong paper submitted to the wrong venue will be rejected. Venue strategy is part of research methodology, not an afterthought.

### Target Venues

We target the top venues in our research areas:

| Venue | Focus | Typical Deadline | Notes |
|-------|-------|------------------|-------|
| NeurIPS | Broad ML, theory + empirics | May | Our primary target. Strong fit for theory-practice bridging work. |
| ICML | ML theory and methods | Jan-Feb | Good for more theoretical contributions. |
| ICLR | Representation learning, deep learning | Sep-Oct | Good for architectural and training insights. |
| ACL | NLP and computational linguistics | Jan-Feb | For NLP-specific contributions. |
| EMNLP | Empirical NLP | May-Jun | For empirical NLP work. |
| AAAI | Broad AI, applications | Aug | For applied and interdisciplinary work. |

### Matching Research to Venue

The choice of venue should be made early (during project formulation) and should influence the research, not just the paper:

- **Theory-heavy work** (formal proofs, complexity bounds, expressiveness results): NeurIPS or ICML. These venues value formal rigor and welcome conditional complexity claims.
- **Empirical evaluation work** (large-scale benchmarks, model comparison): NeurIPS, EMNLP, or ICLR. These venues value comprehensive experiments and reproducibility.
- **NLP-specific work** (language understanding, generation, dialogue): ACL or EMNLP. These venues value linguistic insight alongside ML methodology.
- **Applied and interdisciplinary work**: AAAI. Broader audience, more receptive to cross-disciplinary contributions.
- **Early-stage ideas**: Workshop papers at any venue. Lower bar, faster feedback, builds community connections.

### Timeline

Standard timeline from idea to submission: 3 months.

```
Month 1: Literature review, formalization, initial experiments
Month 2: Full experiments, analysis, initial paper draft
Month 3: Paper writing, quality gates, revision, submission
```

This is aggressive but achievable with continuous operation. The reasoning-gaps project is approximately on this timeline (started 2026-03-07, targeting NeurIPS 2026 submission in May).

### Revision Strategy

Not every paper is accepted on the first submission. The revision strategy is:

1. **After rejection:** Read all reviews carefully. Classify each criticism as:
   - Valid and fixable: Add to revision plan
   - Valid but fundamental: May require pivoting the contribution
   - Invalid (reviewer misunderstood): Clarify in the paper
   - Subjective (reviewer preference): Note but do not necessarily change

2. **Critic review.** Run the adversarial review (Gate 4) again, incorporating the actual reviewer feedback. The simulated reviewers should now include the actual criticisms as known concerns.

3. **Revise.** Address all valid and fixable criticisms. For fundamental criticisms, decide whether to pivot or stand firm (with better explanation).

4. **Resubmit.** Target the next available venue in the priority list. Adapt the framing to the new venue's expectations while maintaining the core contribution.

5. **Kill threshold.** If a paper is rejected from 3 venues with consistent fundamental criticisms, re-evaluate whether the contribution is viable. This may trigger a kill decision.

### Workshop Strategy

Workshop papers serve a specific purpose: they are not "lesser" publications but a different kind of output.

Use workshop papers for:
- Testing early-stage ideas before committing to a full paper
- Getting community feedback on a new direction
- Establishing priority on an idea while the full work is in progress
- Building connections with researchers in the area

Workshop papers should be honest about their stage: "We present preliminary results on X" is appropriate. Do not present workshop papers as complete contributions.

---

## Appendix: Principles Summary

For quick reference, these are the core methodological principles:

1. **Research is evolution, not a pipeline.** Iterate, revise, kill. The cycle is the method.
2. **Pre-register everything.** Specify analyses before collecting data. No exceptions.
3. **Kill early and often.** Sunk cost is not a reason to continue. Kill criteria are checked continuously.
4. **Log failures explicitly.** The research log exists primarily for negative results and dead ends.
5. **Deep literature synthesis, not keyword search.** Understand the intellectual landscape, not just the citation graph.
6. **Multiple model families, minimum three.** Single-model results are anecdotes, not evidence.
7. **Statistical rigor is non-negotiable.** Confidence intervals, effect sizes, multiple comparison correction.
8. **Five quality gates before submission.** Novelty, theory, experiments, adversarial review, community value.
9. **Decide autonomously, log transparently.** Speed of autonomous decisions with accountability of transparent logging.
10. **Produce reusable artifacts.** Every project should leave behind tools the community can use.
