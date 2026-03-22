# Self-Improvement Limits: Project Brief

## Title
**Impossibility Results for Unsupervised Self-Improvement in Language Models**

## One-Sentence Summary
We develop formal impossibility results showing that self-improvement without verification oracles is fundamentally limited, proving bounds on the maximum capability gain achievable through self-training, self-refinement, and self-play.

## Research Question
Can a language model improve its own capabilities without external ground truth?

## Claimed Contribution
This paper provides rigorous theoretical foundations for understanding the limits of self-improvement in language models:

1. **Formalization**: We formalize self-improvement as an iterative process where a model generates training data, evaluates it, and trains on selected examples, without access to external verification.

2. **Impossibility Theorems**: We prove that self-improvement without external verification converges to a fixed point bounded by the model's initial verification capability, establishing fundamental limits independent of model architecture or training procedure.

3. **Verification-Generation Gap**: We characterize how the gap between generation difficulty and verification difficulty determines the ceiling for self-improvement gains, proving that this gap cannot be bridged through iteration alone.

4. **Self-Play Analysis**: We prove conditions under which self-play can exceed self-training bounds, showing that benefits arise only when the game structure provides implicit verification.

## Key Hypotheses

1. **Fixed Point Convergence**: Self-improvement without external verification converges to a fixed point that is bounded by the model's initial verification capability.

2. **Verification-Limited Growth**: The gap between generation and verification difficulty determines the ceiling for self-improvement gains.

3. **Self-Play Conditions**: Self-play can exceed self-training bounds only when the game structure provides implicit verification (e.g., outcomes are objectively determinable).

## Target Venue
- **Primary**: ICLR 2027 (submission deadline: September 2026)
- **Secondary**: NeurIPS 2026 (submission deadline: May 2026)

**Paper type**: Theory paper with formal proofs

## Estimated Timeline
4 months from initialization to submission-ready draft

## Portfolio Fit
Complements the reasoning-gaps project by providing impossibility results rather than just characterization. Together they form a theoretical program:
- **reasoning-gaps**: What can't LLMs do?
- **self-improvement-limits**: What can't they learn to do on their own?

Forms part of a "theoretical trilogy" with reasoning-gaps and verification-complexity.

## Related Work (Initial Survey Needed)

### Self-Improvement in LLMs
- Self-training and self-play methods (STaR, ReST, Expert Iteration)
- Constitutional AI and self-refinement
- Recursive self-improvement in AI safety literature

### Verification and Evaluation
- Verification vs generation difficulty gaps
- Automated evaluation without ground truth
- Reward model limitations

### Impossibility Results in ML
- PAC learning impossibility results
- No-free-lunch theorems
- Sample complexity lower bounds

### Theoretical Foundations
- Fixed point theory and convergence analysis
- Game theory for self-play
- Information theory bounds on learning

## Success Criteria

### Theoretical Rigor
- [ ] All theorems have complete, rigorous proofs
- [ ] All assumptions are stated explicitly
- [ ] All definitions are formal and unambiguous
- [ ] Proofs are verifiable by expert readers

### Novelty and Impact
- [ ] Results go beyond existing negative results in ML theory
- [ ] Connection to practical self-improvement methods is clear
- [ ] Implications for AI safety and alignment are articulated
- [ ] Results provide actionable guidance for practitioners

### Presentation Quality
- [ ] Paper is accessible to ML researchers without theory background
- [ ] Intuition is provided before formalism
- [ ] Examples illustrate key concepts
- [ ] Related work is comprehensive and fair

### Acceptance Prediction
- [ ] Target acceptance score: 7.5+/10
- [ ] Predicted reviewer concerns are addressed preemptively
- [ ] Proofs are presented at appropriate level of detail
- [ ] Limitations are acknowledged honestly

## Open Questions (To Be Resolved)

1. **Scope of results**: Should we focus on text generation, or include other modalities?
2. **Assumptions**: What minimal assumptions allow for meaningful impossibility results?
3. **Practical implications**: Can we provide quantitative predictions testable in experiments?
4. **Positive results**: Should we include constructive results showing when self-improvement IS possible?

## Dependencies

### Prerequisites
- Literature survey on self-improvement methods (Researcher agent)
- Literature survey on verification and impossibility results (Researcher agent)
- Formal framework for self-improvement processes (Theorist agent)

### Theoretical Work Required
- Formalize self-training, self-refinement, and self-play (Theorist)
- Develop impossibility theorems with proofs (Theorist)
- Prove convergence and fixed-point results (Theorist)
- Characterize verification-generation gap (Theorist)

### Writing Work Required
- Draft paper incorporating formal framework (Writer)
- Present proofs with appropriate detail (Writer)
- Write clear intuitions and examples (Writer)
- Polish based on critic feedback (Writer)

## Current Status
**Phase**: Initialization (as of 2026-03-22)

This project was initialized in response to Linear issue DW-91, though the issue incorrectly assumed a paper already existed for revision. The project is now properly initialized and ready for theoretical development.

**Next immediate steps**:
1. Literature survey (Researcher agent)
2. Formal framework development (Theorist agent)
3. Theorem development and proof (Theorist agent)

## Notes
- This is a theory-heavy paper requiring deep expertise in learning theory, game theory, and formal methods
- Quality of proofs is paramount - better to have fewer, more rigorous results than many informal arguments
- Connection to practical methods is important for impact, but should not come at the cost of rigor
- Consider including a "practical implications" section that translates theoretical results into actionable insights
