# Publishing Pipeline

This document covers every step from finished paper to public visibility: arXiv, conference submission, web publishing, open-source release, and promotion.

## arXiv Submission Workflow

### Timing Strategy
- **Post to arXiv before conference decisions.** This establishes priority and gets community feedback.
- **Optimal timing**: Post 1-2 weeks after conference submission, once the anonymity-compatible policy of the venue permits. Check each venue's policy:
  - NeurIPS: allows arXiv posting; does not require anonymity on arXiv
  - ICML: allows arXiv posting; anonymity not required externally
  - ICLR: allows arXiv posting; OpenReview is public but anonymous
  - ACL/EMNLP: check the specific year's policy; ARR has its own rules
  - AAAI: generally allows arXiv posting
- **Never post to arXiv the same day as submission** to avoid trivial deanonymization for double-blind venues.
- **Update the arXiv preprint** after acceptance with the camera-ready version.

### LaTeX Packaging Checklist
1. Use the venue's official LaTeX template (NeurIPS, ICML, etc.) or `article` class for arXiv-first papers
2. Flatten all `\input{}` commands into a single `.tex` file (arXiv prefers this)
3. Include all figures as PDF/EPS (vector) or high-resolution PNG
4. Ensure the paper compiles cleanly with `pdflatex` or `latexmk`
5. Remove all comments and TODO markers from the source
6. Include `\bibliographystyle{plainnat}` or venue-appropriate style
7. BibTeX: use `.bib` file, not inline `\bibitem`
8. Test compilation in a clean environment (Docker or Overleaf) before upload

### arXiv Metadata
- **Title**: Exact match with the paper title
- **Authors**: All authors listed, in order, with correct affiliations
- **Abstract**: Copy from the paper (arXiv allows 1920 characters)
- **Categories**: Primary + cross-list. Common ML categories:
  - `cs.LG` (Machine Learning) — primary for most ML papers
  - `cs.CL` (Computation and Language) — NLP papers
  - `cs.AI` (Artificial Intelligence) — general AI
  - `stat.ML` (Machine Learning, Statistics) — cross-list for theory
  - `cs.CV` (Computer Vision) — vision papers
- **Comments**: Include venue name if submitted (e.g., "Submitted to NeurIPS 2026")
- **License**: CC BY 4.0 (recommended for maximum reuse)

### arXiv Submission Steps
1. Create an arXiv account if needed (one-time)
2. Prepare the submission package: `.tex`, `.bib`, figures, `.bbl` file
3. Upload via arXiv web interface or the arXiv API
4. Verify the compiled PDF matches expectations
5. Submit; wait for moderation (usually 1-2 business days)
6. Record the arXiv ID in `projects/<name>/status.yaml`

## Conference Submission

### Per-Venue Formatting Reference

| Venue | Template | Pages (Main) | Appendix | Supplementary | Blind |
|-------|----------|-------------|----------|---------------|-------|
| NeurIPS | `neurips_2026.sty` | 9 | Unlimited | Allowed | Double-blind |
| ICML | `icml2027.sty` | 8 | Unlimited | Allowed | Double-blind |
| ICLR | OpenReview LaTeX | 9 | Unlimited | Allowed | Double-blind (public) |
| ACL | ACL rolling review | 8 (long) / 4 (short) | Limited | Allowed | Double-blind |
| EMNLP | Same as ACL (ARR) | 8 (long) / 4 (short) | Limited | Allowed | Double-blind |
| AAAI | AAAI Press format | 7 + 2 (refs/ethics) | Separate upload | Allowed | Double-blind |

### Pre-Submission Checklist

Run this checklist for every submission. No exceptions.

**Content**:
- [ ] All self-review criteria score >= 7/10
- [ ] Abstract within word limit (usually 150-250 words)
- [ ] Contribution list is clear and in the introduction
- [ ] All experiments complete with statistical significance
- [ ] Limitations section present and substantive
- [ ] Broader impact / ethics statement (if required by venue)

**Formatting**:
- [ ] Correct venue template used
- [ ] Page count within limits (count carefully; references often excluded but check)
- [ ] Font size matches template requirements
- [ ] Margins unmodified from template
- [ ] Figures and tables are referenced in text and numbered correctly
- [ ] References formatted per venue style (author-year vs. numbered)
- [ ] No orphaned references (every `\cite` has a corresponding `\bibitem`)
- [ ] No broken cross-references (`??` in compiled PDF)

**Anonymization** (for double-blind venues):
- [ ] No author names or affiliations in the paper
- [ ] No self-identifying references ("In our prior work [Author, 2024]..." -> "In prior work [Anonymous, 2024]...")
- [ ] No identifying information in figure metadata
- [ ] No GitHub links to non-anonymized repositories
- [ ] Supplementary code anonymized (remove git history, author names)
- [ ] No acknowledgments section (add after acceptance)

**Supplementary Material**:
- [ ] Clearly labeled and referenced from main paper
- [ ] Proofs in appendix are complete and self-contained
- [ ] Code supplement is a clean zip file with README
- [ ] Dataset supplements include documentation and licenses

**Final Checks**:
- [ ] PDF compiles without warnings
- [ ] All pages render correctly (check embedded fonts)
- [ ] File size within venue limits (usually 50MB for paper, varies for supplements)
- [ ] Co-authors have reviewed and approved (if applicable)
- [ ] Submission portal account created and tested before deadline day

### Submission Day Protocol
1. Submit at least 12 hours before the deadline. Server congestion causes failures in the final hours.
2. Download and review the venue-compiled PDF (OpenReview, CMT, etc. sometimes re-render)
3. Verify all figures appear correctly in the compiled version
4. Save a screenshot/PDF of the submission confirmation
5. Record submission ID and timestamp in `projects/<name>/status.yaml`

## Camera-Ready Process

After acceptance notification:
1. Read all reviewer comments thoroughly
2. Address every comment (even those you disagree with — explain your reasoning)
3. Prepare a revision document mapping reviewer comments to changes
4. De-anonymize: add authors, affiliations, acknowledgments
5. Add funding acknowledgments if applicable
6. Final proofread with fresh eyes
7. Submit camera-ready by the deadline
8. Update arXiv with the camera-ready version (add "Accepted at [Venue]" in comments)

## Web Publishing Pipeline

### Blog Post for Every Paper

Every submitted paper gets an accompanying blog post. This is non-negotiable — a blog post reaches 10x the audience of the paper itself.

**Blog post structure**:
1. **Title**: Accessible, may differ from paper title (less technical, more engaging)
2. **TL;DR**: 2-3 sentences for the key finding
3. **Motivation**: Why this problem matters, in plain language
4. **Key Idea**: The core contribution explained without jargon (or with jargon carefully defined)
5. **Main Result**: The headline finding with one key figure
6. **How It Works**: Brief methodology overview (skip details, link to paper)
7. **Implications**: What this means for practitioners, researchers, and the field
8. **Limitations**: Honest assessment of what the work does not show
9. **Links**: Paper (arXiv), code (GitHub), data, citation BibTeX

**Writing guidelines for blog posts**:
- Target audience: ML-aware practitioners, not specialists in the subfield
- Length: 800-1500 words
- Include at least one figure from the paper (the most informative one)
- Use concrete examples to explain abstract concepts
- Avoid: "We show that our method outperforms baselines." Instead: "When we tested [method] on [task], it improved accuracy from X% to Y% — a Z% reduction in errors."

**Auto-generation workflow**:
1. Paper is submitted -> agent generates a blog post draft from the paper
2. Blog post is reviewed and edited
3. Published to the research website on submission day (or shortly after)
4. Updated after acceptance with acceptance information

### Research Website Structure

The research website lives in `docs/site/` and is built with a static site generator (Astro or Hugo).

```
docs/site/
├── src/
│   ├── pages/
│   │   ├── index.astro          # Landing page
│   │   ├── papers.astro         # Papers listing (all publications)
│   │   ├── blog/
│   │   │   ├── index.astro      # Blog listing
│   │   │   └── [slug].astro     # Individual blog posts
│   │   └── experiments/
│   │       └── index.astro      # Experiments dashboard (live results)
│   ├── content/
│   │   ├── papers/              # Paper metadata (YAML/MDX)
│   │   └── blog/                # Blog posts (MDX)
│   └── layouts/
│       └── BaseLayout.astro
├── public/
│   ├── papers/                  # PDFs of papers
│   └── figures/                 # Figures for blog posts
├── astro.config.mjs
└── package.json
```

**Papers page** includes for each paper:
- Title, authors, venue, date
- Abstract
- Links: PDF, arXiv, code, blog post, slides
- BibTeX citation block (click to copy)

**Blog** is the primary content channel:
- Paper summaries (one per paper)
- Research process notes (how we approached a problem)
- Technical tutorials related to our research
- Monthly research updates

**Experiments dashboard** (future):
- Live results from running experiments
- Interactive plots (Observable/D3 embedded)
- Comparison tables across projects

### Publishing Workflow
1. Write blog post in `docs/site/src/content/blog/`
2. Add paper metadata to `docs/site/src/content/papers/`
3. Commit and push; GitHub Actions builds the static site
4. Deploy to GitHub Pages or Cloudflare Pages (auto-deploy on push to main)

## Open-Source Release Strategy

### What to Release
Every paper should have accompanying open-source artifacts. Release:

| Artifact | Priority | Format |
|----------|----------|--------|
| Evaluation code | Required | GitHub repository |
| Training code (if applicable) | Required | GitHub repository |
| Benchmark/dataset | Required (if novel) | GitHub + HuggingFace/Zenodo |
| Pre-trained models | Recommended | HuggingFace Hub |
| Interactive demos | Nice-to-have | Gradio/Streamlit on HuggingFace Spaces |

### Repository Standards
- **README**: Clear description, installation instructions, usage examples, citation
- **LICENSE**: MIT for code, CC BY 4.0 for data/models
- **Requirements**: Pinned dependency versions (`requirements.txt` or `pyproject.toml`)
- **Reproducibility**: Single command to reproduce all results (e.g., `make reproduce` or `bash run_all.sh`)
- **Documentation**: Docstrings for all public functions; at minimum a README, ideally readthedocs
- **Tests**: At least smoke tests that verify the code runs end-to-end
- **CI**: GitHub Actions that run tests on push

### Release Timing
1. **At submission**: Post code to anonymous GitHub (for supplementary material)
2. **At arXiv posting**: Release public repository with full code
3. **At acceptance**: Update repository with camera-ready code, add badge/link to published paper
4. **Post-conference**: Address community feedback, fix issues, add features

### Naming Convention
Repository name: `deepwork-<project-slug>` (e.g., `deepwork-reasoning-gaps`)

## Social Media and Visibility

### Twitter/X Thread Template
For each paper, prepare a Twitter/X thread:

**Tweet 1** (hook):
> New paper: [Accessible title or question]
>
> [One-sentence key finding]
>
> Paper: [arXiv link]
> Code: [GitHub link]
>
> Thread below with the key ideas. [1/N]

**Tweet 2** (problem):
> The problem: [What gap or question does this address?]
>
> [Figure or diagram if possible] [2/N]

**Tweet 3** (approach):
> Our approach: [High-level method in 1-2 sentences]
>
> [Key insight that makes this work] [3/N]

**Tweet 4** (results):
> Key results:
> - [Result 1]
> - [Result 2]
> - [Result 3]
>
> [Results figure] [4/N]

**Tweet 5** (implications + links):
> What this means: [Practical implications]
>
> Paper: [link]
> Blog: [link]
> Code: [link]
>
> Feedback welcome. [5/5]

### LinkedIn Post Template
More formal, single post:
> Excited to share our new work on [topic].
>
> [2-3 sentence summary of the contribution and key finding]
>
> [Why it matters for practitioners/the field]
>
> Links: Paper ([arXiv]), Code ([GitHub]), Blog post ([website])
>
> [Relevant hashtags: #MachineLearning #NeurIPS2026 #AIResearch]

### Visibility Checklist per Paper
- [ ] arXiv preprint posted
- [ ] Blog post published
- [ ] Twitter/X thread drafted and posted
- [ ] LinkedIn post published
- [ ] GitHub repository public with README
- [ ] Paper added to research website
- [ ] Google Scholar profile updated
- [ ] Semantic Scholar profile checked
- [ ] Relevant subreddits / forums notified (r/MachineLearning, if appropriate)

## Citation Tracking

### Automated Monitoring
- **Google Scholar Alerts**: Set up alerts for each paper title and for the research lab name
- **Semantic Scholar API**: Weekly automated check for new citations:
  ```
  GET https://api.semanticscholar.org/graph/v1/paper/arXiv:<id>/citations
  ```
- **Track in status.yaml**: Record citation count monthly in each project's status file

### Metrics to Track
- Total citations per paper (monthly snapshot)
- Citation velocity (citations per month, first 6 months)
- Citing paper venues (are we cited by top-venue papers?)
- Self-citation ratio (keep below 30%)
- h-index trajectory (for the research group overall)

### Response to Citations
- If a paper cites our work critically: read the critique, consider addressing in a follow-up
- If a paper extends our work: potential collaboration opportunity
- If a paper misrepresents our work: consider a public clarification (blog post or comment)
- Track which of our papers get cited most and investigate why — this informs future project selection
