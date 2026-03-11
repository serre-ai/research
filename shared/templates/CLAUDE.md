# Project: {{project_name}}

## Agent Instructions

### Context
{{project_context — 2-3 sentences describing what this project investigates and why it matters. Reference the research area and the core question being addressed.}}

### Working on This Project
- Always read `BRIEF.md` for goals and `status.yaml` for current state before starting work
- Use commit scope `{{project_name}}` (e.g., `research({{project_name}}): add literature survey`)
- Update `status.yaml` after completing any significant milestone
- Work in the project's worktree: `.worktrees/{{project_name}}/`
- Push after every commit; create PRs at phase transitions

### Research Standards
- All theoretical claims must be precisely stated with formal definitions
- Empirical claims require statistical rigor: confidence intervals, significance tests, effect sizes
- Distinguish correlation from causation in all analysis
- Negative results are valuable — document what didn't work and why
- Every claim in the paper must be traceable to evidence in `experiments/` or `literature/`
{{project_specific_standards — Add any domain-specific standards here, e.g., "Benchmark tasks must have known ground truth" or "Proofs must be fully formal, not proof sketches"}}

### Paper Style
- LaTeX, targeting {{venue}} format
- Use theorem environments for all formal statements (definition, theorem, lemma, proposition)
- Empirical results with confidence intervals and ablations
- Figures should be self-contained (readable without the main text)
- Related work should be comprehensive and fair to competing approaches
{{project_specific_style — Add any style notes specific to this paper, e.g., "Connect to cognitive science perspectives" or "Use running example throughout"}}

### Key Directories
- `literature/` — Survey notes and reference summaries
- `experiments/` — Scripts, results, and analysis
- `paper/` — LaTeX source, figures, and bibliography
- `notes/` — Working notes, brainstorms, and scratch work
- `data/` — Datasets and processed data
- `src/` — Reusable code (benchmarks, evaluation tools, etc.)

### Decision Making
All decisions are made autonomously. Use extended thinking for:
- Research direction and scope decisions
- Methodology choices that affect the paper's contribution claims
- Which baselines, models, or datasets to include
- Whether to expand or narrow the paper's scope
- Budget allocation for API-based evaluations
{{project_specific_decisions — List 2-4 project-specific decisions that will likely arise, e.g., "Choice of which model families to include in evaluation"}}

Log all decisions in `status.yaml` with date and clear rationale.
