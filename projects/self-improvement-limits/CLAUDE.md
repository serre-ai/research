# Self-Improvement Limits: Agent Instructions

## Project Overview
This project develops formal impossibility results for unsupervised self-improvement in language models. The goal is to prove rigorous theoretical bounds showing that self-improvement without verification oracles is fundamentally limited.

**Status**: Initialization phase (as of 2026-03-22)
**Next phase**: Literature survey, then theory development
**Target venue**: ICLR 2027

## Agent-Specific Guidance

### For Researcher Agent
**Primary task**: Comprehensive literature survey

Survey three areas:
1. **Self-improvement methods**: STaR, ReST, Expert Iteration, Constitutional AI, self-refinement, recursive self-improvement
2. **Verification without ground truth**: Reward modeling, automated evaluation, verification complexity
3. **Impossibility results in ML**: PAC learning lower bounds, no-free-lunch theorems, sample complexity

**Deliverables**:
- Annotated bibliography in `notes/literature-survey.md`
- Identification of gaps this paper will fill
- Key papers added to `paper/references.bib`
- Summary of existing negative results to differentiate from

**Focus**: Find the frontier of what's known about self-improvement limits. We need to go beyond hand-waving arguments to formal impossibility results.

### For Theorist Agent
**Primary task**: Develop formal framework and prove core theorems

**Phase 1: Formalization** (estimate: 4-6 sessions)
- Formalize self-training as iterative process: \(\M_{t+1} = \T(\M_t, \D_{\M_t})\)
- Define verification capability \(\Ver(\M)\) and generation capability \(\Gen(\M)\)
- Formalize verification-generation gap
- Define convergence criteria and fixed points
- Document all definitions in `notes/formal-framework.md`

**Phase 2: Core theorems** (estimate: 8-12 sessions)
- **Theorem 1**: Fixed-point convergence - prove self-improvement converges to fixed point bounded by \(\Ver(\M_0)\)
- **Theorem 2**: Capability gain bounds - prove \(\Gen(\M_{\infty}) \leq \Ver(\M_0) + \epsilon\) for some \(\epsilon\)
- **Theorem 3**: Verification-generation gap - characterize ceiling as function of gap
- **Theorem 4**: Self-play conditions - prove when self-play exceeds self-training

**Phase 3: Proof development** (estimate: 4-6 sessions)
- Write complete, rigorous proofs for all theorems
- Verify all assumptions are minimal and stated explicitly
- Create proof sketches for main text
- Write full proofs for appendix
- Document in `notes/proofs.md`

**Quality bar**: Proofs must be verifiable by expert readers. Better to have 2-3 strong theorems than 10 informal results.

**Notes**:
- Consider whether results should be information-theoretic, computational, or both
- Think about minimal assumptions - what's the weakest setting where impossibility holds?
- Connection to existing theory: PAC learning, online learning, game theory
- May need to develop new proof techniques - this is novel territory

### For Writer Agent
**Primary task**: Draft paper integrating theoretical framework

**DO NOT START** until:
1. Literature survey is complete (Researcher)
2. Formal framework is documented (Theorist)
3. Core theorems are proved (Theorist)

**When ready to draft**:
1. Read `notes/literature-survey.md`, `notes/formal-framework.md`, `notes/proofs.md`
2. Draft sections in order: Introduction → Related Work → Framework → Impossibility Results → Self-Play Analysis → Discussion → Conclusion → Abstract (last)
3. Present intuition before formalism in each section
4. Include examples to illustrate non-obvious concepts
5. Maintain consistent notation (see `paper/main.tex` for defined commands)

**Proof presentation**:
- Main text: Theorem statement + intuition + proof sketch (1-2 paragraphs)
- Appendix: Full rigorous proof
- Every assumption must be explicit in theorem statement

**Style**:
- Audience: ML researchers without heavy theory background
- Avoid: "clearly," "obviously," "trivially" (what's obvious to you isn't to readers)
- Use: Concrete examples, running examples, toy scenarios
- LaTeX: Use `\cref{}` for cross-references, `\( \)` for inline math

### For Critic Agent
**Primary task**: Review paper for correctness and clarity

**Focus areas**:
1. **Correctness**: Are assumptions stated? Are proofs sound? Any overclaims?
2. **Rigor**: Are definitions formal? Are theorem statements precise?
3. **Clarity**: Is intuition provided? Are examples helpful? Is presentation accessible?
4. **Novelty**: How does this differ from existing impossibility results?
5. **Impact**: Are practical implications clear? Is connection to real methods explained?

**Target acceptance score**: 7.5+/10

**Common issues to watch for**:
- Circular reasoning in fixed-point arguments
- Implicit assumptions not stated in theorems
- Proofs that don't actually prove the claimed result
- Overclaims about what impossibility results imply for practice
- Missing related work that proves similar bounds

## Project-Specific Conventions

### Notation
Follow notation defined in `paper/main.tex`:
- \(\M\): Model
- \(\D\): Distribution
- \(\T\): Training procedure
- \(\V\): Verification function
- \(\Gen\): Generation capability
- \(\Ver\): Verification capability

Add new notation to `paper/main.tex` custom commands and document in `notes/notation.md`.

### File Organization
- `paper/`: LaTeX source files
- `notes/`: Research notes, formal framework, proof sketches
- `reviews/`: Critic reviews, reviewer simulations
- `experiments/`: (Unlikely for pure theory paper, but available for toy examples)

### Commits
Use conventional commits:
- `research(self-improvement-limits): description` - for literature survey, theory development
- `paper(self-improvement-limits): description` - for paper drafting
- `proof(self-improvement-limits): description` - for theorem proving work

## Critical Success Factors

1. **Rigor over breadth**: Better to prove 3 strong theorems than claim 10 informal results
2. **Minimal assumptions**: Weakest possible assumptions make results more powerful
3. **Clear positioning**: Must distinguish from existing negative results in ML
4. **Practical connection**: Theory must connect to real self-improvement methods
5. **Accessible presentation**: ML researchers must be able to understand contributions

## Open Questions to Resolve

These should be answered during theory development:

1. **Scope**: Focus on language models specifically, or broader class of models?
2. **Verification model**: How to formalize verification capability? Information-theoretic? Computational?
3. **Self-play**: What game-theoretic framework? Extensive form? Normal form?
4. **Positive results**: Should we include constructive results showing when self-improvement IS possible?
5. **Empirical validation**: Should we include toy experiments demonstrating theoretical predictions?

## Timeline Estimate

From current state to submission-ready:
- Literature survey: 3-5 sessions
- Theory development: 12-20 sessions
- Paper drafting: 5-8 sessions
- Review and revision: 3-5 sessions
- Final polish: 2-3 sessions

**Total**: 25-40 sessions over 3-4 months

## Related Projects

- **reasoning-gaps**: Characterizes what LLMs can't do (complementary)
- **verification-complexity**: Studies how hard it is to verify (direct dependency)
- Together these form a "theoretical trilogy" for understanding LLM limitations

## Current Blockers

None. Project is initialized and ready for work.

**Next immediate action**: Researcher agent should begin literature survey.
