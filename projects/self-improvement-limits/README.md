# Self-Improvement Limits

**Impossibility Results for Unsupervised Self-Improvement in Language Models**

## Status
- **Phase**: Initialization
- **Initialized**: 2026-03-22
- **Target venue**: ICLR 2027
- **Paper exists**: No (theoretical development in progress)

## Project Goal
Develop formal impossibility results showing that self-improvement without verification oracles is fundamentally limited, proving bounds on the maximum capability gain achievable through self-training, self-refinement, and self-play.

## Repository Structure
```
self-improvement-limits/
├── BRIEF.md              # Project goals and contribution claims
├── status.yaml           # Current state and progress tracking
├── CLAUDE.md            # Agent-specific instructions
├── paper/               # LaTeX source for paper
│   ├── main.tex         # Main paper file
│   ├── iclr2027.sty     # ICLR style file
│   └── references.bib   # Bibliography
├── notes/               # Research notes and theory development
│   └── NEXT-STEPS-THEORIST.md  # Detailed guide for theory work
├── reviews/             # Critic reviews (when available)
└── experiments/         # Toy examples (if needed)
```

## Current Phase: Initialization ✓
- [x] Project directory created
- [x] BRIEF.md written
- [x] status.yaml initialized
- [x] LaTeX template set up
- [x] Agent instructions documented

## Next Phase: Theory Development
**Owner**: Theorist agent

1. Formalize self-improvement processes (self-training, self-refinement, self-play)
2. Define verification capability and generation capability
3. Prove core impossibility theorems:
   - Fixed-point convergence
   - Verification bounds on capability gain
   - Verification-generation gap characterization
   - Self-play conditions

See `notes/NEXT-STEPS-THEORIST.md` for detailed guidance.

## Key Hypotheses

1. **Fixed Point Convergence**: Self-improvement without external verification converges to a fixed point bounded by the model's initial verification capability.

2. **Verification-Limited Growth**: The gap between generation and verification difficulty determines the ceiling for self-improvement gains.

3. **Self-Play Conditions**: Self-play can exceed self-training bounds only when the game structure provides implicit verification.

## Related Projects
- **reasoning-gaps**: Characterizes what LLMs can't do
- **verification-complexity**: Studies how hard it is to verify what they do
- Together these form a "theoretical trilogy"

## Linear Issues
- DW-91: Paper revision (premature - created before paper existed)
- DW-98: ICLR submission (premature - created before paper existed)

Both issues were created in error. This initialization establishes the foundation for future work.

## Notes
This is a theory paper requiring rigorous proofs. Estimated timeline: 4 months from initialization to submission-ready draft.
