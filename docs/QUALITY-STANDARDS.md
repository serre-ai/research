# Research Quality Standards

This document defines the minimum quality bar for every research output produced by the Forge platform. Every paper, benchmark, and artifact must meet these standards before submission. There are no exceptions.

## What Makes a Paper Publishable at a Top Venue

Top ML venues (NeurIPS, ICML, ICLR) accept roughly 25-30% of submissions. The accepted papers share four qualities:

1. **Novelty**: The paper presents an idea, result, or perspective that is meaningfully new. "New" does not require a paradigm shift — a novel combination of known techniques applied to a well-motivated problem counts. But the reader must learn something they did not know before.

2. **Rigor**: Claims are supported by evidence. Theoretical claims have proofs. Empirical claims have controlled experiments with appropriate statistical treatment. The methodology would survive scrutiny from a skeptical expert in the subfield.

3. **Clarity**: The paper is well-written, well-organized, and accessible to a knowledgeable reader outside the paper's narrow subfield. Notation is consistent. Figures are informative. The contribution is stated precisely in the introduction.

4. **Significance**: The work matters. It addresses a real problem, advances understanding in a meaningful way, or provides tools that others will use. Significance is the hardest criterion to meet and the most common reason for rejection at top venues.

A paper that is strong on all four gets accepted. A paper that is weak on any one is at serious risk.

## Minimum Standards by Venue Tier

### Top-Tier Main Conference (NeurIPS, ICML, ICLR)
- **Novelty**: Core contribution must be clearly novel. At least one of: new theoretical result, new method with demonstrated advantage, new empirical finding that changes understanding, or new benchmark/dataset that enables previously impossible evaluations.
- **Rigor**: Full proofs for theoretical claims (appendix acceptable for lengthy derivations). Empirical results with statistical significance, ablations, and reproducibility details. No hand-waving on methodology.
- **Clarity**: Professional quality writing. Clear notation table. Self-contained abstract. Introduction states contribution in first page. Related work thoroughly covers relevant prior art.
- **Significance**: Must pass the "so what?" test. The paper should change how at least some researchers think about the problem or provide tools they will actually use.
- **Completeness**: All promised experiments delivered. No "left for future work" on core claims.

### Top-Tier NLP (ACL, EMNLP)
All of the above, plus:
- **Linguistic grounding**: Claims about language understanding must engage with linguistic theory, not just benchmark numbers.
- **Multilingual awareness**: If applicable, discuss cross-lingual implications. Monolingual English-only studies need strong justification.
- **Ethics statement**: Required. Must address potential misuse, bias, and societal impact.
- **Limitations section**: Mandatory. Must be honest and substantive, not perfunctory.

### Second-Tier / Workshop Papers
- **Novelty**: Can be more incremental. A well-executed replication, negative result, or focused extension of prior work is acceptable.
- **Rigor**: Same statistical standards as top-tier, but scope can be narrower (fewer baselines, smaller-scale experiments acceptable).
- **Clarity**: Same standard. Poor writing is never acceptable at any tier.
- **Significance**: Can address a smaller audience. A result interesting to one subfield is sufficient.

### Nature Machine Intelligence / Science Journals
All top-tier standards, plus:
- **Broader impact**: Must articulate significance beyond ML. Interdisciplinary connections expected.
- **Accessibility**: Writing must be understandable to a broad scientific audience, not just ML specialists.
- **Long-form narrative**: These venues expect a story, not just results. Motivation and context receive more space.

## Literature Review Standards

Every project must conduct a thorough literature review before any original work begins. The literature review is not a formality — it is the foundation that ensures novelty and positions the contribution.

### Minimum Requirements
- **Volume**: Survey a minimum of 30-50 papers. For well-established subfields, 60-80 may be necessary.
- **Recency**: At least 60% of cited papers should be from the last 3 years (2024-2026). The remaining 40% covers foundational and classic work.
- **Coverage breadth**: Must include work from at least 4 distinct research groups or institutions. Do not rely solely on one lab's line of work.
- **Source diversity**: Draw from at least 3 different venues (e.g., NeurIPS + ICML + arXiv + ACL). Do not limit to a single conference track.
- **Pre-print awareness**: Check arXiv for work submitted in the last 6 months that may not yet be published. Being scooped by an overlooked preprint is preventable.

### Organization
- Maintain per-project literature notes in `projects/<name>/literature/`
- Each reviewed paper should have a structured summary:
  - Full citation
  - Key contribution (1-2 sentences)
  - Methodology summary
  - Relevance to our project (how does it relate, what gap does it leave)
  - Strengths and limitations
- Organize papers by theme/subtopic, not chronologically
- Identify the 5-10 most directly relevant papers ("core references") and understand them deeply

### Positioning
- For every core reference, explicitly state how our work differs
- Identify the gap our contribution fills — the literature review should make this gap obvious
- Acknowledge related concurrent work fairly. Never omit a relevant paper to make our contribution seem more novel.

## Empirical Standards

### Experimental Design
- **Baselines**: Minimum 3 baselines, including:
  - The strongest known prior method
  - A simple/naive baseline (random, majority class, etc.)
  - At least one recent (2024-2026) competitive method
- **Ablation studies**: For every design choice in the proposed method, include an ablation that removes or substitutes that component. This is non-negotiable for top venues.
- **Dataset selection**: Use established benchmarks where they exist. If creating a new benchmark, validate it thoroughly. Never evaluate only on a custom dataset with no standard reference point.
- **Hyperparameter treatment**: Report all hyperparameters. Describe the tuning procedure (grid search, random search, Bayesian optimization). Report tuning budget. Apply the same tuning effort to baselines as to the proposed method.

### Statistical Rigor
- **Multiple runs**: Minimum 3 random seeds for all stochastic experiments. Report mean and standard deviation.
- **Statistical significance**: Either:
  - Report p-values (p < 0.05 minimum, p < 0.01 preferred) with appropriate tests (paired t-test, bootstrap, permutation test depending on setting), or
  - Report 95% confidence intervals
- **Effect size**: When possible, report effect sizes alongside significance tests. A statistically significant but practically meaningless improvement is not a contribution.
- **Multiple comparisons**: If testing multiple hypotheses, apply correction (Bonferroni, Holm-Bonferroni, or FDR control).

### Reproducibility
- All code must be released (GitHub, linked in paper)
- Report complete hyperparameters in the paper or appendix
- Report computational cost: GPU hours, API cost, wall-clock time
- Report model versions and API dates for any model accessed via API (API model behavior changes over time)
- Pin software versions in requirements files
- Random seeds must be reported and reproducibility verified before submission

### Figures and Tables
- Tables: always include error bars (standard deviation or confidence interval)
- Figures: vector graphics (PDF/SVG) preferred over raster (PNG/JPG)
- All figures must have self-contained captions (a reader should understand the figure without reading the main text)
- Color-blind accessible palettes (avoid red-green distinctions without additional encoding like shape/pattern)
- Consistent formatting across all figures in a paper

## Theoretical Standards

### Formal Precision
- **Definitions**: All technical terms must be formally defined before first use. Use `\begin{definition}...\end{definition}` environments.
- **Theorem statements**: Must be precise and self-contained. A reader should understand what is being claimed from the theorem statement alone.
- **Assumptions**: All assumptions must be explicitly stated, numbered, and justified. Unjustified assumptions are a top reason for rejection of theory papers.
- **Proof structure**: Proofs must be complete. If a proof is lengthy, provide a proof sketch in the main text and the full proof in the appendix. Every step must be justified.

### Proof Quality
- No proof by intimidation ("it is easy to see that..."). If it is easy, show it.
- Cite prior results used in proofs explicitly (Lemma X from [Reference Y])
- Check boundary cases and edge conditions
- Verify that all variables are bound and all quantifiers are correct
- For complexity-theoretic claims: clearly state the computational model and the measure of complexity

### Theory-Practice Connection
- For theory papers submitted to ML venues (not pure math venues), the theoretical results must connect to practice
- Include at least one of:
  - Empirical validation of theoretical predictions
  - Concrete examples showing the theory applies to real systems
  - Discussion of practical implications and limitations of the theoretical results
- State which aspects of practice the theory does and does not capture

## Writing Standards

### Abstract (150-250 words)
Structure: (1) Context/problem, (2) Gap or limitation of prior work, (3) Our approach, (4) Key result/finding, (5) Significance/implication. Every sentence must earn its place. No filler phrases ("In recent years, there has been growing interest in...").

### Introduction (1.5-2 pages)
Structure: (1) Motivation and context, (2) Problem statement, (3) Why existing approaches are insufficient, (4) Our contribution (bulleted list of 3-4 concrete claims), (5) Paper outline. The contribution list is the most important part — reviewers read it first and judge whether to read further.

### Notation
- Provide a notation table if using more than 5 distinct symbols
- Be consistent: once a symbol is defined, use it the same way throughout
- Follow subfield conventions (e.g., bold lowercase for vectors, bold uppercase for matrices)
- Define notation in order of appearance

### Related Work
- Organize by theme, not by paper
- For each theme: summarize the state of the art, then state how our work relates
- Be fair: accurately represent prior work, acknowledge its strengths
- Be precise about the difference between our work and the closest prior art
- Minimum 20 references for a full paper; 40-60 for thorough coverage at top venues

### General Prose Quality
- Active voice preferred ("We prove..." not "It is proved...")
- Short sentences for technical content, varied length for narrative sections
- One idea per paragraph
- Precise language: "improves accuracy by 3.2 percentage points" not "significantly improves accuracy"
- Avoid jargon without definition
- No first-person singular ("I") in multi-author or anonymous submissions

## Self-Review Rubric

Before any paper advances from the revision phase to submission, it must be scored on the following rubric. Each criterion is scored 1-10.

| Criterion | Score Range | Description |
|-----------|-----------|-------------|
| **Novelty** | 1-10 | 1 = trivial extension of known work, 10 = paradigm-shifting new idea |
| **Technical Rigor** | 1-10 | 1 = major errors/gaps, 10 = bulletproof proofs/experiments |
| **Clarity** | 1-10 | 1 = incomprehensible, 10 = a pleasure to read |
| **Significance** | 1-10 | 1 = no one would care, 10 = everyone in the field needs to read this |
| **Completeness** | 1-10 | 1 = critical experiments missing, 10 = nothing left to add |
| **Positioning** | 1-10 | 1 = ignores prior work, 10 = perfect context and differentiation |
| **Presentation** | 1-10 | 1 = ugly/sloppy formatting, 10 = polished and professional |
| **Reproducibility** | 1-10 | 1 = impossible to reproduce, 10 = run one script and get all results |

**Scoring guidelines**:
- 1-3: Fundamental problems. Do not submit.
- 4-5: Significant weaknesses. Major revision needed.
- 6-7: Solid but could be stronger. Minor revision or accept risk.
- 8-9: Strong paper. Submit with confidence.
- 10: Exceptional. Rare. Do not inflate scores.

**Minimum for submission**: All criteria must score 7 or higher. If any criterion scores below 7, return to revision with targeted improvements for that criterion.

**Record scores** in `projects/<name>/status.yaml` under `self_review` before submitting.

## Common Rejection Reasons and Prevention

| Rejection Reason | Frequency | Prevention Strategy |
|-----------------|-----------|-------------------|
| **Lack of novelty** | Very common | Thorough literature review; explicit novelty statement; differentiation table vs. top-5 closest works |
| **Insufficient baselines** | Common | Minimum 3 baselines rule; include the strongest known method |
| **Missing ablations** | Common | Ablation for every design choice; plan ablations during experimental design, not as an afterthought |
| **Claims exceed evidence** | Common | Scope claims precisely; use hedging language for weaker results; never claim "state-of-the-art" without comprehensive comparison |
| **Poor writing/organization** | Common | Follow section templates; revise at least twice; check flow between sections |
| **Lack of significance** | Moderately common | Ask "so what?" for every result; connect to real problems; discuss implications |
| **Reproducibility concerns** | Moderately common | Release code; report all hyperparameters; pin model versions |
| **Unfair comparison** | Moderately common | Apply same tuning budget to baselines; use official implementations where available |
| **Ignoring related work** | Less common | Comprehensive literature review; be fair to competitors |
| **Formatting/length violations** | Rare but fatal | Pre-submission checklist; compile and check page count early |

## Quality Gates

Quality gates define what must be true before a project transitions between phases. These are enforced by the agent before updating `status.yaml`.

### Gate 1: Research Phase -> Drafting Phase
All of the following must be true:
- [ ] Literature review complete: 30+ papers surveyed, core references identified
- [ ] Clear thesis statement written (1-2 sentences)
- [ ] Novel angle confirmed: differentiation from top-5 closest works articulated
- [ ] Sufficient evidence gathered: experiments show the core claim holds, or theoretical framework is complete enough to prove main results
- [ ] Venue selected with backup; deadline timeline mapped
- [ ] Outline of all paper sections exists with bullet points for each section

### Gate 2: Drafting Phase -> Revision Phase
All of the following must be true:
- [ ] Complete draft exists: all sections written (abstract, intro, method, experiments, related work, conclusion)
- [ ] All figures and tables present (can be rough versions)
- [ ] All main experiments completed and reported
- [ ] Proofs complete (at least in appendix) for all theoretical claims
- [ ] Page count within venue limits (or clear plan for cutting)
- [ ] All references formatted correctly

### Gate 3: Revision Phase -> Submission Phase
All of the following must be true:
- [ ] Self-review score >= 7/10 on ALL eight criteria
- [ ] Ablation studies complete for every design choice
- [ ] Statistical significance reported for all empirical claims
- [ ] Reproducibility package prepared (code, configs, seeds)
- [ ] Notation consistency verified across all sections
- [ ] Figures are publication-quality (vector, accessible colors, self-contained captions)
- [ ] Anonymization verified (for double-blind venues)
- [ ] Page limits respected (hard constraint)
- [ ] Appendix/supplementary material properly formatted
- [ ] One complete end-to-end proofread with no remaining TODOs or placeholders
- [ ] All self-review criteria below 8 have had targeted revision attempts
