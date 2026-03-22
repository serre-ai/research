# Project: self-improvement-limits

## Agent Instructions

### Context
This project develops formal impossibility results for unsupervised self-improvement in language models. It asks: can a language model improve its own capabilities without external ground truth? We formalize self-improvement as an iterative process and prove bounds on the maximum capability gain achievable through self-training, self-refinement, and self-play under various assumptions about the verification problem. This is an AI safety theory project — the results have direct implications for understanding the limits of recursive self-improvement.

### Working on This Project
- Always read `BRIEF.md` for goals and `status.yaml` for current state before starting work
- Use commit scope `self-improvement-limits` (e.g., `research(self-improvement-limits): formalize self-training operator`)
- Update `status.yaml` after completing any significant milestone
- Work in the project's worktree: `.worktrees/self-improvement-limits/`
- Push after every commit; create PRs at phase transitions

### Research Standards
- **Proofs must be fully formal** — no proof sketches or hand-waving in the core results. Every theorem, lemma, and proposition requires a complete proof. Proof sketches are acceptable only in the main text when full proofs appear in the appendix.
- All theoretical claims must be precisely stated with formal definitions in definition/theorem/lemma environments
- Clearly state all assumptions (axioms) and discuss which are essential vs. technical conveniences
- Distinguish between different self-improvement mechanisms: self-training (training on own outputs), self-refinement (iterative editing of outputs), self-play (competitive or cooperative multi-agent dynamics), and constitutional AI-style self-critique
- Connect to established learning theory: PAC learning, boosting, self-training convergence results, online learning
- Connect to optimization theory: fixed-point theorems (Banach, Brouwer, Kakutani), contraction mappings, monotone operators
- Negative results are the core contribution — impossibility results, upper bounds, separation results
- Every bound should be accompanied by a discussion of tightness: is the bound tight? Can you provide a matching lower bound or construction?
- Empirical validation should confirm theoretical predictions on controlled tasks, not replace formal analysis

### Paper Style
- LaTeX, targeting ICLR 2027 format
- Use theorem environments for all formal statements (definition, theorem, lemma, proposition, corollary)
- Main text contains theorem statements and proof sketches; full proofs in appendix
- Notation must be consistent and defined before first use — maintain a notation table
- Figures should illustrate key concepts: self-improvement trajectories, fixed-point convergence, generation-verification gap
- Related work should connect to learning theory, optimization theory, AI safety literature on recursive self-improvement, and empirical self-improvement methods
- Use a running example throughout (e.g., arithmetic self-improvement) to ground abstract definitions

### Key Directories
- `literature/` — Survey notes and reference summaries
- `proofs/` — Working proof drafts, lemma development, proof attempts
- `experiments/` — Empirical validation scripts and results
- `paper/` — LaTeX source, figures, and bibliography
- `notes/` — Working notes, brainstorms, and scratch work

### Decision Making
All decisions are made autonomously. Use extended thinking for:
- Axiom selection — which assumptions to impose on the generation and verification operators, and how to justify them
- Proof strategy — which proof techniques to use (fixed-point theorems, information-theoretic arguments, reduction to known impossibility results)
- Scope of self-play results — how deep to go into game-theoretic analysis vs. keeping self-play as a secondary contribution
- Whether to include computational complexity aspects (P vs. NP connections to generation vs. verification)
- How to frame AI safety implications — direct and substantive but not overblown
- Connection to reasoning-gaps project — how to reference and build on the reasoning gap framework without creating a dependency

Log all decisions in `status.yaml` with date and clear rationale.
