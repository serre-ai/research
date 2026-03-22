# Impossibility Results for Unsupervised Self-Improvement in Language Models

## Title
Impossibility Results for Unsupervised Self-Improvement in Language Models

## Target Venue
ICLR 2027 (submission deadline ~Sep/Oct 2026), with NeurIPS 2026 as backup

## Research Area
AI Safety x AI/ML Theory

## Motivation
A growing body of work explores self-improvement in language models — self-training on model-generated data, iterative self-refinement, self-play, and constitutional AI-style self-critique. These approaches promise scalable capability gains without expensive human annotation. But can a system genuinely improve beyond its own ability to distinguish good outputs from bad? Without external ground truth, self-improvement is constrained by the model's own verification capability. Despite extensive empirical exploration, no formal characterization exists of when and why unsupervised self-improvement must plateau. This project provides that characterization through impossibility results.

## Research Goals

### Primary
1. **Formalize self-improvement** as an iterative process over a capability space, defining generation, verification, and update operators with explicit assumptions for each self-improvement mechanism (self-training, self-refinement, self-play, constitutional AI).
2. **Prove convergence bounds** showing that self-improvement without external verification converges to a fixed point bounded by the model's initial verification capability, and characterize the tightness of these bounds under various assumptions.
3. **Characterize the generation-verification gap** as the fundamental quantity governing self-improvement ceilings, proving that the difficulty gap between generating correct outputs and verifying them determines the maximum achievable capability gain.

### Secondary
4. Identify conditions under which self-play can exceed self-training bounds (when game structure provides implicit verification), and formalize these conditions.
5. Provide empirical validation of the theoretical bounds using small-scale self-improvement experiments on controlled tasks with known difficulty parameters.

## Hypotheses
- **H1**: Self-improvement without external verification converges to a fixed point that is bounded by the model's initial verification capability. Formally, if the model cannot reliably distinguish correct from incorrect outputs for problems above difficulty level d*, then iterative self-training cannot improve performance above d*.
- **H2**: The gap between generation and verification difficulty determines the ceiling for self-improvement gains. When verification is easy relative to generation (e.g., math problems with checkable solutions), self-improvement yields larger gains than when verification is as hard as generation (e.g., open-ended reasoning).
- **H3**: Self-play can exceed self-training bounds only when the game structure provides implicit verification — that is, when the competitive dynamics create a signal that correlates with ground truth without requiring an external oracle.

## Methodology
1. **Literature survey**: Survey self-improvement literature across self-training (He et al., Huang et al.), self-refinement (Madaan et al.), self-play (Burns et al., Chen et al.), and constitutional AI (Bai et al.). Identify implicit assumptions about verification in each approach. Survey relevant learning theory (PAC learning, boosting, self-training convergence) and optimization theory (fixed-point theorems, contraction mappings).
2. **Formal framework**: Define the self-improvement process formally. Model a language model as a pair (G, V) of generation and verification capabilities over a difficulty-parameterized task space. Define self-training, self-refinement, and self-play as specific operators. Establish axioms capturing realistic assumptions about LLM capabilities.
3. **Convergence proofs**: Prove that under the defined axioms, each self-improvement operator converges to a fixed point. Characterize the fixed point in terms of the initial verification capability V. Prove upper bounds on the capability gap between the fixed point and the initial state. Establish separation results between mechanisms (self-play vs. self-training).
4. **Fixed-point characterization**: Analyze the structure of the fixed points — are they unique? How do they depend on the initial conditions? Under what conditions can the system escape local fixed points? Connect to existing results on iterative refinement and boosting.
5. **Empirical validation**: Design controlled experiments with small language models on tasks with tunable generation-verification gaps. Validate that empirical self-improvement trajectories match theoretical predictions. Tasks: arithmetic (easy verification), logical reasoning (moderate verification), creative writing quality (hard verification). Budget: ~$200.
6. **Paper writing**: ICLR 2027 format. Structure: introduction, formal framework, main results (3-4 theorems), proof sketches in main text with full proofs in appendix, empirical validation, discussion of implications for AI safety.

## Expected Contributions
- A formal framework for analyzing self-improvement in language models, unifying self-training, self-refinement, self-play, and constitutional AI under a common theoretical lens
- Impossibility results (theorems with proofs) establishing ceilings on unsupervised self-improvement as a function of verification capability
- Characterization of the generation-verification gap as the fundamental quantity governing self-improvement potential
- Separation results showing when and why self-play can exceed self-training bounds
- Empirical validation on controlled tasks confirming theoretical predictions
- Implications for AI safety: formal bounds on recursive self-improvement without human oversight

## Timeline
- **Phase 1** (Weeks 1-4, Mar 21 - Apr 18): Literature survey and formal framework development. Deliverable: complete survey of self-improvement approaches, formal definitions of all operators and axioms.
- **Phase 2** (Weeks 5-9, Apr 19 - Jun 6): Core proof development. Deliverable: convergence theorems for self-training and self-refinement, generation-verification gap characterization.
- **Phase 3** (Weeks 10-13, Jun 7 - Jul 4): Self-play separation results and fixed-point characterization. Deliverable: complete theoretical results.
- **Phase 4** (Weeks 14-17, Jul 5 - Aug 1): Empirical validation experiments. Deliverable: experimental results confirming theoretical predictions.
- **Phase 5** (Weeks 18-22, Aug 2 - Sep 12): Paper writing and polishing. Deliverable: submission-ready paper. Buffer: 2-3 weeks before expected ICLR deadline.

## Resource Requirements
- **Compute**: ~$200 for empirical validation experiments. Small language models (7B-8B) via API on controlled tasks. Estimated ~10K API calls across 3 task families x 3 self-improvement mechanisms x multiple iterations.
- **Data**: No special datasets needed. Tasks are synthetically generated with controlled difficulty parameters (arithmetic sequences, logic puzzles, constrained writing).
- **External tools**: Standard LaTeX setup. Python for experiments and plotting. No specialized libraries beyond standard ML stack.
- **Estimated cost**: ~$200 total. This is primarily a theory project; compute needs are minimal.

## Risk Factors
- **Theorems are too weak**: The bounds may be loose enough to be uninteresting. Mitigate by working on tightness results in parallel and by ensuring at least some bounds are shown to be tight via matching constructions.
- **Assumptions criticized as unrealistic**: Formal results require axioms, and reviewers may object to the axioms. Mitigate by (a) stating multiple results under progressively weaker assumptions, (b) empirically validating that the axioms hold for real LLMs on controlled tasks, (c) discussing which axioms are essential vs. technical conveniences.
- **Prior work overlap**: Self-improvement theory is an active area. Mitigate by conducting thorough literature review early and positioning the contribution clearly. Our focus on impossibility results (not algorithms) and the generation-verification gap framing is distinctive.
- **Self-play results too complex**: The game-theoretic analysis for self-play may be technically difficult. Mitigate by scoping self-play results as secondary and ensuring the self-training/self-refinement results stand alone as a complete contribution.
