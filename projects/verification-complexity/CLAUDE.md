# Project: verification-complexity

## Agent Instructions

### Context
This project formally characterizes the computational complexity of verifying LLM outputs across reasoning domains. It connects classical complexity theory (P vs NP, interactive proofs, PCP theorem) to practical LLM training and inference methods (RLHF, self-consistency, majority voting), showing that the widely assumed generation-verification gap does not hold uniformly. The work has direct implications for AI safety and scalable oversight.

### Working on This Project
- Always read `BRIEF.md` for goals and `status.yaml` for current state before starting work
- Use commit scope `verification-complexity` (e.g., `research(verification-complexity): prove gap collapse for planning tasks`)
- Update `status.yaml` after completing any significant milestone
- Work in the project's worktree: `.worktrees/verification-complexity/`
- Push after every commit; create PRs at phase transitions

### Research Standards
- **Proofs must be fully formal** — no proof sketches, no hand-waving, no "it is easy to see." Every theorem and lemma must have a complete proof with all steps justified. If a proof relies on a known result, cite it precisely (theorem number, paper, year).
- **Distinguish between verification in the complexity-theoretic sense and practical LLM output checking** — the former is about worst-case computational complexity of a decision problem; the latter is about whether a reward model or human can judge output quality. The paper must be precise about which sense is meant at every point.
- **All complexity-theoretic claims must be conditional on standard assumptions** — state explicitly whether results hold unconditionally or require P != NP, the exponential time hypothesis, or other conjectures. Never claim unconditional results that are actually conditional.
- **Connect classical results to LLM-specific settings** — pure complexity theory is not the contribution. The contribution is the bridge: showing what classical verification complexity implies for concrete LLM methods.
- Empirical claims require statistical rigor: confidence intervals, significance tests, effect sizes
- Negative results are valuable — if self-consistency works on a task predicted to be verification-hard, that is an important finding to document and explain

### Paper Style
- LaTeX, targeting NeurIPS 2026 format
- Use theorem environments for all formal statements: definition, theorem, lemma, proposition, corollary
- Number and name all definitions (e.g., "Definition 3.1 (Verification Complexity Class)")
- Proofs should be in the main text for core results, appendix for supporting lemmas
- Use a running example throughout: contrast mathematical proof verification (easy) with plan quality verification (hard) to build intuition
- Related work should cover: (a) classical complexity of verification (IP, PCP, AM/MA), (b) LLM output verification methods, (c) scalable oversight and AI safety, (d) self-consistency and majority voting
- Figures should illustrate the verification complexity hierarchy and the generation-verification gap across task types
- Cross-reference reasoning-gaps paper where appropriate — the two frameworks are complementary

### Key Directories
- `literature/` — Survey notes on complexity-theoretic verification, LLM verification methods, scalable oversight
- `paper/` — LaTeX source, figures, and bibliography
- `notes/` — Working notes, proof drafts, counterexample attempts
- `experiments/` — Empirical validation scripts and results
- `data/` — Experimental data and benchmark results

### Decision Making
All decisions are made autonomously. Use extended thinking for:
- Which theorems to prove vs. which to state as conjectures — the paper needs enough formal results to be rigorous but can't prove everything
- How to formalize "verification" for tasks without clean ground truth (planning, creative writing) — this is the hardest definitional challenge
- Whether to include interactive verification protocols (debate, recursive reward modeling) or scope to single-round verification
- How deep to go into the connection with scalable oversight — this could be a separate paper
- Whether empirical validation is strong enough for NeurIPS or whether to fall back to theory-only and target ICLR 2027

Log all decisions in `status.yaml` with date and clear rationale.
