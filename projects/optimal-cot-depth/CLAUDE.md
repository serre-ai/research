# Project: optimal-cot-depth

## Agent Instructions

### Context
This project develops a complexity-theoretic analysis of optimal Chain-of-Thought depth in language models. It resolves contradictions in the literature about whether longer CoT helps or hurts reasoning by proving that optimal depth is determined by the computational complexity of the underlying task. This is a theory project with empirical validation — the core contribution is formal bounds on useful reasoning depth per complexity class.

### Working on This Project
- Always read `BRIEF.md` for goals and `status.yaml` for current state before starting work
- Use commit scope `optimal-cot-depth` (e.g., `research(optimal-cot-depth): prove depth bound for NP tasks`)
- Update `status.yaml` after completing any significant milestone
- Work in the project's worktree: `.worktrees/optimal-cot-depth/`
- Push after every commit; create PRs at phase transitions

### Research Standards
- **Proofs must be fully formal** — no proof sketches or hand-waving in core results. Proof sketches acceptable in main text only when full proofs appear in appendix.
- Use standard computational complexity notation throughout: P, NP, coNP, PSPACE, TC^0, NC^1. Define non-standard notation before first use.
- All complexity class references must be precise — "NP-hard" vs. "NP-complete" vs. "in NP" are different claims with different implications for CoT depth.
- Connect explicitly to circuit complexity results on transformers (TC^0 bounds from Merrill & Sabharwal, reasoning-gaps framework).
- The three dispute papers must be cited and analyzed explicitly: "Demystifying Long Chain-of-Thought Reasoning", "When More is Less", "SafeChain". The framework must predict each paper's findings.
- Noise accumulation model must have formal error bounds, not just intuitive arguments. Connect to concentration inequalities and error propagation theory.
- Empirical validation must use tasks with known, provable complexity class — not approximate or informal difficulty ratings.
- Distinguish between CoT depth (number of reasoning steps) and CoT length (token count). This project is about depth (logical steps), not surface length.

### Paper Style
- LaTeX, targeting ICLR 2027 format
- Theorem environments for all formal statements (definition, theorem, lemma, proposition, corollary, assumption)
- Main text: theorem statements + proof sketches; appendix: full proofs
- Running example throughout: arithmetic (P) vs. subset sum (NP) vs. QBF (PSPACE) — showing how optimal depth differs
- Notation table in appendix for all symbols
- Figures: (1) optimal depth curve per complexity class, (2) empirical vs. predicted depth, (3) noise accumulation illustration
- Related work: connect to CoT scaling literature, circuit complexity, proof complexity, reasoning-gaps project

### Key Directories
- `literature/` — Survey notes on CoT length studies, complexity foundations, and noise models
- `proofs/` — Working proof drafts, lemma development, proof attempts
- `experiments/` — Benchmark design, evaluation scripts, results
- `paper/` — LaTeX source, figures, and bibliography
- `notes/` — Working notes, brainstorms, scratch work

### Decision Making
All decisions are made autonomously. Use extended thinking for:
- How to formalize "optimal depth" — the objective function matters (accuracy? expected utility? worst-case?)
- Which complexity classes to prove bounds for — P and NP are essential; coNP and PSPACE are valuable but may be secondary
- Noise model assumptions — independent vs. correlated per-step errors, fixed vs. input-dependent error rate
- How to handle the empirical-theory gap — the bounds are asymptotic but experiments are on finite instances
- Connection to verification-complexity project — CoT depth relates to verification cost, but keep projects independent
- Framing the dispute resolution — be precise and charitable to all three papers

Log all decisions in `status.yaml` with date and clear rationale.
