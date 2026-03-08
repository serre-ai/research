# Project: reasoning-gaps

## Agent Instructions

### Context
This project investigates the formal characterization of reasoning limitations in large language models. It bridges computational complexity theory with empirical LLM evaluation.

### Working on This Project
- Always read `BRIEF.md` for goals and `status.yaml` for current state before starting work
- Use commit scope `reasoning-gaps` (e.g., `research(reasoning-gaps): add literature survey`)
- Update `status.yaml` after completing any significant milestone

### Research Standards
- All theoretical claims must be precisely stated with formal definitions
- Empirical claims require evaluation across at least 3 model families
- Benchmark tasks must have known ground truth and controlled difficulty parameters
- Distinguish between "the model fails" and "the model fails systematically" — we care about the latter

### Paper Style
- LaTeX preferred, targeting NeurIPS format
- Formal definitions in definition/theorem environments
- Empirical results with confidence intervals and ablations
- Related work should connect to both ML theory and cognitive science perspectives

### Key Directories
- `literature/` — Survey notes and reference summaries
- `benchmarks/` — Diagnostic task specifications and data
- `experiments/` — Evaluation scripts and results
- `paper/` — LaTeX source for the paper

### Decision Escalation
Flag for human decision:
- Choice of which model families to include in evaluation
- Scope of complexity-theoretic claims (how formal vs. informal)
- Whether to include cognitive science framing
- Budget allocation for API-based evaluations
