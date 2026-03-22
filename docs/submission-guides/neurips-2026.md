# NeurIPS 2026 Submission Guide

Complete reference for submitting to NeurIPS 2026. Sourced from the official [Call for Papers](https://neurips.cc/Conferences/2026/CallForPapers), [Main Track Handbook](https://neurips.cc/Conferences/2026/MainTrackHandbook), and [Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist).

Last updated: 2026-03-21.

---

## Deadlines

| Milestone | Date |
|-----------|------|
| Abstract submission | May 4, 2026 (AOE) |
| Full paper submission | May 6, 2026 (AOE) |
| Author notification | September 24, 2026 (AOE) |

All authors must have an updated OpenReview profile by the full paper deadline.

---

## Page Limits

| Content | Limit | Counts toward 9 pages? |
|---------|-------|------------------------|
| Main text, figures, tables | **9 pages** | Yes |
| References | Unlimited | No |
| Appendix (proofs, extra results) | Unlimited | No |
| NeurIPS Paper Checklist | ~2 pages | No |

**Camera-ready (if accepted): 10 content pages.**

Violating page limits or style = desk rejection without review.

---

## File Requirements

- **Format**: Single PDF containing (in order): paper, references, appendix, checklist
- **Main PDF**: 50MB max
- **Supplementary ZIP**: 100MB max (code, data, extra figures)
- **LaTeX**: Must use official `neurips_2026.sty`, unmodified
- Microsoft Word templates are discontinued

---

## Desk-Rejection Triggers

These will get your paper rejected without review:

1. Exceeding 9-page content limit
2. Missing NeurIPS Paper Checklist
3. Modifying margins, fonts, or spacing in the style file
4. Anonymization violations (author names, affiliations, self-identifying citations)
5. Dual submission to another archival venue
6. Missing OpenReview profile for any author
7. Submission from a U.S.-sanctioned institution

---

## Anonymization (Double-Blind)

- No author names, affiliations, or acknowledgments
- Self-citations in third person: "Smith et al. [1] showed..." NOT "Our previous work [1]..."
- All external links must be anonymously browsable
- Supplementary code must be anonymized
- `\begin{ack}` environment is automatically hidden during review
- If citing your own concurrent unpublished work: include anonymized copy in supplementary as "Anonymous et al."

---

## Style File Options

```latex
\usepackage{neurips_2026}                    % anonymous submission (default)
\usepackage[main]{neurips_2026}              % main track, explicit
\usepackage[dandb]{neurips_2026}             % datasets & benchmarks track
\usepackage[position]{neurips_2026}          % position paper track
\usepackage[creativeai]{neurips_2026}        % creative AI track
\usepackage[main, final]{neurips_2026}       % camera-ready
\usepackage[preprint]{neurips_2026}          % arXiv preprint
\usepackage[nonatbib]{neurips_2026}          % suppress auto-loaded natbib
\usepackage[sglblindworkshop]{neurips_2026}  % workshop, single-blind
\usepackage[dblblindworkshop]{neurips_2026}  % workshop, double-blind
```

---

## Contribution Types

Select one at submission:

- **General** — standard research contribution
- **Theory** — primarily theoretical
- **Use-Inspired** — motivated by practical application
- **Concept & Feasibility** — early-stage ideas with preliminary evidence
- **Negative Results** — well-executed work that didn't produce expected results

Reviewers receive type-specific guidance for fair evaluation.

---

## Paper Checklist (16 Questions)

Mandatory. Included at the end of the PDF. Uses `\answerYes{}`, `\answerNo{}`, `\answerNA{}` macros defined in the style file. Answering "No" or "N/A" is generally not grounds for rejection — reviewers are told to reward honesty.

| # | Topic | What they're looking for |
|---|-------|--------------------------|
| 1 | **Claims** | Abstract/intro match actual contributions and scope |
| 2 | **Limitations** | Honest discussion in a dedicated section; reviewers told not to penalize |
| 3 | **Theory/Proofs** | All assumptions stated; complete proofs (main or appendix) |
| 4 | **Reproducibility** | Enough detail to reproduce main results |
| 5 | **Open access** | Code/data included (not required, but encouraged) |
| 6 | **Experimental details** | Hyperparameters, data splits, selection methods |
| 7 | **Statistical significance** | Error bars, CIs, significance tests; explain what they capture |
| 8 | **Compute resources** | GPU type, total compute, cost |
| 9 | **Code of Ethics** | Compliance confirmed |
| 10 | **Broader impacts** | Negative societal impacts discussed where applicable |
| 11 | **Safeguards** | Responsible release for high-risk models |
| 12 | **Licenses** | Existing assets credited, licenses stated |
| 13 | **New assets** | Documented with structured templates |
| 14 | **Crowdsourcing** | Full instructions, fair compensation (min wage) |
| 15 | **IRB approval** | Obtained if human subjects involved |
| 16 | **LLM usage** | Non-standard LLM use in methodology disclosed |

### Error bar guidance (Q7)
- Clearly state what variability factors error bars capture (train/test split, initialization, random seeds)
- Explain calculation method (bootstrap, analytic formula)
- State assumptions (e.g., normality)
- Prefer 2-sigma; 1-sigma acceptable if noted
- Avoid symmetric bars for asymmetric distributions

---

## LLM/Agent Usage Policy

**Does not require disclosure:**
- Spell checkers, grammar tools
- Basic code assistance
- Editing aid

**Requires disclosure (in experimental setup):**
- LLM usage that is important, original, or non-standard to core methods

**Rules:**
- Authors remain fully responsible for all content (text, figures, references)
- Must verify tool outputs — hallucinated citations violate Code of Conduct
- LLMs cannot be listed as authors
- Prompt injections to manipulate reviewing are strictly prohibited

---

## Dual Submission Policy

- Cannot submit to another archival venue while under NeurIPS review
- Non-archival workshops are fine
- "Thin slicing" (multiple similar papers hoping one succeeds) is prohibited
- Policy applies throughout entire review process
- Violation at any stage = desk rejection

---

## Preprint Policy

- Non-anonymous preprints (arXiv, websites) are allowed
- Use `[preprint]` option in style file, NOT `[final]`
- Do not write "Under review at NeurIPS"
- Avoid aggressive social media promotion
- Reviewers instructed not to actively search for preprints
- Papers posted after March 1, 2026 are treated as "contemporaneous work"

---

## Supplementary Materials

- Single ZIP file, up to 100MB
- Include training/evaluation code with dependency specs
- Follow [Papers with Code](https://github.com/paperswithcode/releasing-research-code) guidelines
- Must be anonymized during review
- Reviewers keep code/data strictly confidential
- Reviewers should run code in isolated environments (Docker, VM)

---

## Author Response Period

Three phases:
1. **Authors view & respond** — reviewers cannot see responses until period ends
2. **Bidirectional discussion** — authors, reviewers, and ACs can exchange
3. **Reviewer-AC only** — authors locked out

Rules:
- 10,000 characters max per review response
- Markdown supported, no file uploads
- No identifying information (violates anonymity)
- No external links (exception: anonymized code link to AC if requested)
- Scope: clarify questions, not comprehensive revision

---

## Camera-Ready (if accepted)

**Allowed edits:**
- Title, keywords, abstract (no substantial changes)
- Author order reordering
- No author additions/removals

**Required additions:**
- **Funding transparency statement** (36-month lookback): all third-party funding/support
- **Competing interests disclosure** (36-month lookback): financial relationships that could influence
- **Lay summary**: paragraph-length, jargon-free overview for general public
- Use `[final]` option in style file

**Format:** 10 content pages + unlimited references/appendix/checklist

---

## Presentation Requirements

- At least one author must register for the main conference
- Virtual Only Pass is insufficient
- Must attend in person (satellite attendance OK if satellite exists)
- Student authors need only student registration
- One registration covers multiple accepted papers
- No-show: NeurIPS may revoke acceptance; orals may be downgraded to posters

---

## Ethics Review

- Reviewers/ACs may flag submissions for Code of Ethics violations
- Flagged papers sent to ethics review committee
- Ethics reviewers cannot reject papers — only program chairs can
- Ethics comments visible to authors (who may respond)

Key ethics areas:
- Human subjects (fair wages, IRB compliance)
- Privacy and consent
- Deprecated datasets
- Safety, security, discrimination, surveillance
- Bias and fairness
- Environmental impact

Report violations to: hotline@neurips.cc

---

## Publication & Visibility

**Accepted papers:**
- Reviews, meta-reviews, and discussions published on OpenReview
- Reviewer/AC identities remain anonymous

**Rejected papers:**
- Authors have 2 weeks post-notification to opt-in to deanonymized public posting
- Shown as rejected in OpenReview
- Not counted as NeurIPS publications

---

## Conflicts of Interest

Two types:

**Domain conflicts** (public, based on Education & Career History):
- Papers hidden from reviewers/ACs sharing same institutional domain
- Last 3 years only
- Include all affiliations (consulting, sabbaticals ≥20%)

**Personal conflicts:**
- Family/close personal relationship
- PhD advisor/advisee
- Co-authors on research articles (last 3 years)
- Optional hidden conflicts for edge cases (visible only to PCs)

False declaration = removal from system, rejection of all papers, institutional notification, future sanctions.

---

## Anti-Collusion & Plagiarism

Both trigger the same penalties:
- Immediate removal from reviewing system
- Rejection of all papers under consideration
- Identity sharing with sister conferences
- Institutional notification
- Future NeurIPS sanctions

---

## Reviewer Expectations (useful for understanding what reviewers are told)

Reviewers are instructed to:
- Be fair, precise, scientifically focused
- Substantiate critiques with references
- Avoid vague criticisms
- Address technical content, not just presentation
- Keep post-publication visibility in mind (reviews are published)
- Counter bias against unfashionable subjects
- Encourage risk-taking for new approaches
- Accept preliminary results for concept papers
- Read author responses carefully and update reviews if warranted

---

## Our Submission Checklist

Before submitting, verify:

- [ ] Content ≤ 9 pages (figures/tables count, refs/appendix/checklist don't)
- [ ] Using unmodified `neurips_2026.sty`
- [ ] No author names, affiliations, or acknowledgments visible
- [ ] Self-citations in third person
- [ ] All 16 checklist questions answered
- [ ] `\begin{ack}` section present (auto-hidden during review)
- [ ] No `\todo{}` macros remaining
- [ ] PDF < 50MB
- [ ] Supplementary ZIP < 100MB (if applicable)
- [ ] All external links anonymously browsable
- [ ] No "Under review at NeurIPS" in preprint
- [ ] OpenReview profiles updated for all authors
- [ ] Contribution type selected
- [ ] Single PDF order: paper → refs → appendix → checklist
