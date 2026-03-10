# 6-12 Month Research Roadmap

Starting date: March 2026.

This roadmap charts the growth of the Deepwork platform from a single active research project to a steady-state autonomous research lab producing monthly submissions to top ML/AI venues.

## Phase 1: Foundation (Months 1-2, March-April 2026)

### Objectives
- Complete the reasoning-gaps project through literature review and formal framework
- Launch a second research project (empirical study, lower risk)
- Establish the publishing pipeline (arXiv workflow, blog, website skeleton)
- Validate the autonomous research workflow end-to-end

### Milestones

| Milestone | Target Date | Description |
|-----------|------------|-------------|
| reasoning-gaps lit review complete | March 31 | 50+ papers surveyed, formal framework sketched |
| Second project launched | April 7 | Selected from idea backlog, BRIEF.md written |
| Research website skeleton | April 15 | Static site deployed with papers page and first blog post |
| reasoning-gaps formal framework | April 30 | Core definitions and main theorem statements complete |
| First arXiv preprint | April 30 | Position/survey piece or early reasoning-gaps draft |

### Resource Allocation
- **Budget**: $1,000/month
- **Projects**: 2 (reasoning-gaps + one empirical/survey)
- **Agent hours**: ~60% reasoning-gaps, ~30% second project, ~10% infrastructure

### Key Decisions Required
- Select the second project from the idea backlog (by March 20)
- Decide on static site generator (Astro vs. Hugo) for research website
- Establish LaTeX build pipeline in CI

---

## Phase 2: Scale (Months 3-4, May-June 2026)

### Objectives
- Submit reasoning-gaps to NeurIPS 2026 (deadline mid-May)
- Have 3-4 concurrent projects running
- First empirical project approaching submission (targeting EMNLP 2026 in June)
- Website live with 3+ blog posts
- Idea backlog at 15+ ideas

### Milestones

| Milestone | Target Date | Description |
|-----------|------------|-------------|
| reasoning-gaps NeurIPS submission | May 15 | Full paper submitted, arXiv preprint posted |
| Third project launched | May 1 | Targeting AAAI 2027 (August deadline) |
| Fourth project launched | May 20 | Tool/benchmark project, targeting NeurIPS D&B |
| Blog post: reasoning-gaps | May 20 | Accessible summary of the submitted paper |
| Second paper submission | June 15 | Empirical project submitted to EMNLP 2026 |
| Budget increase to $2,000/month | June 1 | Based on demonstrated output |

### Resource Allocation
- **Budget**: $1,000 -> $2,000/month
- **Projects**: 3-4
- **Agent distribution**: Balanced across projects; writing-phase projects get priority

### Risks
- NeurIPS deadline pressure may degrade quality. Mitigation: enforce quality gates; submit only if self-review >= 7/10; fallback to ICLR 2027 if not ready.
- Scaling to 3-4 projects may reveal coordination issues. Mitigation: stagger phases; no more than 2 projects in the same phase simultaneously.

---

## Phase 3: Optimize (Months 5-6, July-August 2026)

### Objectives
- 5-6 concurrent projects at various phases
- Receive NeurIPS 2026 reviews (September) — prepare for rebuttal
- Submit 1-2 more papers (AAAI 2027 in August, ICLR 2027 prep)
- Refine agent workflow based on first submission experiences
- Website has 8+ blog posts and all submitted papers listed

### Milestones

| Milestone | Target Date | Description |
|-----------|------------|-------------|
| Fifth project launched | July 1 | Survey or position paper |
| Sixth project launched | July 15 | Exploratory high-risk project |
| AAAI 2027 submission | August 15 | Theory or empirical project |
| NeurIPS workshop submissions | August 30 | 1-2 workshop papers from exploratory work |
| Agent workflow retrospective | August 15 | Document what works, what doesn't, adjust process |
| EMNLP 2026 decisions received | August 30 | First acceptance/rejection data |

### Resource Allocation
- **Budget**: $2,000/month
- **Projects**: 5-6
- **Agent distribution**: Writing-phase projects get 2x allocation; exploration gets 0.5x

### Key Activities
- **Rebuttal preparation**: When NeurIPS reviews arrive, allocate focused agent time for rebuttal (typically 1 week)
- **Kill/pivot decisions**: By this point, at least one project likely needs to be killed or pivoted. Use kill criteria from PORTFOLIO.md.
- **Process refinement**: Analyze which project types produce the best agent output. Adjust portfolio mix accordingly.

---

## Phase 4: Steady State (Months 7-9, September-November 2026)

### Objectives
- Regular monthly submission cadence (1 paper/month)
- NeurIPS 2026 decision: if accepted, prepare camera-ready and presentation
- ICLR 2027 submission (October deadline)
- Portfolio rebalancing based on 6 months of data
- 15+ blog posts, 4+ open-source releases

### Milestones

| Milestone | Target Date | Description |
|-----------|------------|-------------|
| NeurIPS 2026 decisions | September 15 | Accept/reject; plan next steps |
| Camera-ready (if accepted) | October 1 | Final version with de-anonymization |
| ICLR 2027 submission | October 10 | At least one strong paper |
| Monthly submission cadence achieved | October 31 | Confirmed: 1 submission per month for 3 consecutive months |
| Budget increase to $3,000/month | November 1 | Based on portfolio performance |
| AAAI 2027 decisions | November 15 | Second round of acceptance data |
| Open-source release #3 | November 30 | Third code/benchmark/dataset release |

### Resource Allocation
- **Budget**: $2,000 -> $3,000/month
- **Projects**: 5-6 (rolling; some complete, new ones start)
- **Agent distribution**: Mature projects get priority; new projects enter slowly

### Key Activities
- **Conference presentation prep**: If NeurIPS accepts, prepare poster or talk. Agent can draft poster content and talking points.
- **Portfolio rebalancing**: With 6 months of data, assess which project types have the best ROI. Adjust the 6-project mix.
- **Community engagement**: Respond to citations, engage with papers that build on our work, attend (virtually) workshop sessions.

---

## Phase 5: Evaluate and Plan (Months 10-12, December 2026-February 2027)

### Objectives
- Year 1 impact assessment
- Methodology refinement based on acceptance/rejection data
- Plan Year 2 research agenda
- ICML 2027 submission (January deadline)
- Comprehensive retrospective

### Milestones

| Milestone | Target Date | Description |
|-----------|------------|-------------|
| ICML 2027 submission | January 25, 2027 | Flagship empirical or theory paper |
| ACL 2027 submission | February 15, 2027 | NLP-focused project |
| Year 1 retrospective | December 31 | Full assessment of all metrics |
| Year 2 research strategy | January 15, 2027 | Updated roadmap, portfolio plan, budget plan |
| Idea backlog refresh | January 31, 2027 | Full re-scoring, 20+ ideas, clear A-tier candidates |
| ICLR 2027 decisions | January 2027 | Third round of acceptance data |

### Resource Allocation
- **Budget**: $3,000/month
- **Projects**: 5-6
- **Additional**: Allocate 10% of budget for retrospective analysis and tooling improvements

### Key Activities
- **Impact assessment**: Count papers submitted, accepted, cited. Calculate cost per paper, cost per acceptance.
- **Methodology refinement**: Which quality standards predicted acceptance? Which agent workflows produced the best papers? Update QUALITY-STANDARDS.md and agent instructions.
- **Year 2 planning**: Based on what worked, plan the next year's portfolio. Consider:
  - Doubling down on successful research areas
  - Entering new areas where the platform has proven capability
  - Increasing budget if ROI is positive
  - Hiring human collaborators for specific projects

---

## Budget Projections

| Quarter | Monthly Budget | Quarterly Total | Allocation |
|---------|---------------|----------------|------------|
| Q1 (Mar-May 2026) | $1,000-1,500 | $3,500 | 2 projects, infrastructure setup |
| Q2 (Jun-Aug 2026) | $2,000 | $6,000 | 4-6 projects, first submissions |
| Q3 (Sep-Nov 2026) | $2,500-3,000 | $8,000 | 5-6 projects, steady state |
| Q4 (Dec-Feb 2027) | $3,000 | $9,000 | 5-6 projects, Year 2 planning |
| **Year 1 Total** | — | **$26,500** | — |

### Budget Breakdown by Category

| Category | Share | Monthly at $3K | Notes |
|----------|-------|---------------|-------|
| API calls (model evaluations) | 45% | $1,350 | Empirical projects drive this |
| Compute (inference, benchmarks) | 25% | $750 | Scales with project count |
| Data services (Firecrawl, APIs) | 15% | $450 | Literature review, web scraping |
| Infrastructure (hosting, CI) | 10% | $300 | Website, GitHub Actions |
| Reserve | 5% | $150 | Unexpected costs |

### Budget Guardrails
- No single project may exceed 35% of monthly budget
- Reserve fund: maintain $500 buffer at all times
- If monthly spending exceeds 90% of budget by the 20th, freeze new project launches until next month
- Budget increases require demonstrated output (1+ submissions in the prior period)

---

## Success Metrics (Year 1)

### Primary Metrics

| Metric | Target | Stretch | How Measured |
|--------|--------|---------|-------------|
| Papers submitted to top venues | 8 | 12 | Count of unique submissions |
| Papers accepted at top venues | 3 | 5 | Acceptance notifications |
| Workshop papers submitted | 4 | 6 | Count |
| Workshop papers accepted | 3 | 5 | Acceptance notifications |
| arXiv preprints | 8 | 12 | arXiv listings |
| Open-source releases | 3 | 5 | Public GitHub repos |
| Blog posts | 12 | 20 | Published on research website |
| Total citations (12-month) | 20 | 50 | Google Scholar + Semantic Scholar |

### Secondary Metrics

| Metric | Target | How Measured |
|--------|--------|-------------|
| Avg. self-review score at submission | 7.5/10 | status.yaml records |
| Avg. reviewer score (where available) | 5.5/10 | Venue review data |
| Cost per submitted paper | < $500 | Budget tracking |
| Cost per accepted paper | < $1,500 | Budget tracking |
| Time from idea to submission | < 4 months | Pipeline tracking |
| Idea backlog depth | 15+ ideas | backlog.yaml |
| Portfolio diversity (distinct areas) | 4+ areas | Project metadata |

### Quarterly Checkpoints

**Month 3 (May 2026)**: First submission completed. Is the workflow viable? Are quality gates being met? Decide whether to accelerate scaling.

**Month 6 (August 2026)**: 3+ submissions completed. First acceptance/rejection data. Is the acceptance rate on track? Decide on budget increase to $3K. Major strategy adjustment if acceptance rate is 0%.

**Month 9 (November 2026)**: 6+ submissions. Multiple rounds of feedback. Calibrate quality standards against actual reviewer expectations. Decide Year 2 scope.

**Month 12 (February 2027)**: Full year retrospective. All metrics evaluated. Year 2 plan finalized.

---

## Risk Factors and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Low acceptance rate (< 20%) | Medium | High | Improve quality gates; get human feedback on drafts; target workshops as stepping stones |
| Budget insufficient for planned scale | Low | Medium | Prioritize empirical projects (lower API cost for higher output); use open-source models more |
| Agent quality plateau | Medium | Medium | Invest in better prompts, specialized agents, and human-in-the-loop for critical decisions |
| Research area becomes saturated | Low | Medium | Monitor arXiv velocity in target areas; pivot to adjacent areas quickly |
| Technical infrastructure failure | Low | Medium | Keep platform simple; git is the source of truth; minimal dependencies |
| Scooping on active project | Medium | High per-project | Maintain 5-6 projects (portfolio diversification); monitor arXiv daily; accelerate promising projects |
| Reviewer lottery (bad luck) | Medium | Medium per-paper | Always have backup venue; workshop as fallback; resubmit with improvements |
| Burnout on operator side | Low | High | Platform is autonomous by design; operator involvement is review and direction-setting, not execution |
