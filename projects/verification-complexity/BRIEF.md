# The Computational Complexity of Verifying LLM Outputs Across Reasoning Domains

## Title
The Computational Complexity of Verifying LLM Outputs Across Reasoning Domains

## Target Venue
NeurIPS 2026 (abstract May 4, paper May 6); fallback ICLR 2027

## Research Area
ML Theory × Computational Complexity

## Motivation
Verification of LLM outputs — checking whether a generated answer is correct — is widely assumed to be easier than generation itself. This assumption underpins RLHF reward modeling, self-consistency decoding, majority voting, and constitutional AI oversight. Yet the assumption's validity varies dramatically across reasoning domains. For mathematical proofs, verification is indeed polynomial-time checkable (the P vs NP gap). For open-ended planning or creative reasoning, verifying output quality may be computationally as hard as producing it. A formal characterization of when verification is easy or hard has immediate consequences for which AI alignment and training techniques can work in principle.

## Research Goals

### Primary
1. **Formally define a verification complexity hierarchy for LLM reasoning tasks** — classify tasks by the computational complexity of their verification procedures, connecting to classical complexity classes (P, NP, coNP, PSPACE, interactive proof systems).
2. **Prove that the generation-verification gap collapses for specific task families** — show that for planning, creative problem-solving, and optimization tasks, no polynomial-time verifier exists (under standard complexity assumptions), undermining reward-model-based training.
3. **Derive predictions about when self-consistency and majority voting improve performance** — prove that these methods succeed only when verification is strictly easier than generation, and validate empirically.

### Secondary
4. Connect verification complexity to the feasibility of scalable oversight in AI safety — formalize when human or AI verification of model outputs is tractable.
5. Characterize the boundary between verifiable and non-verifiable reasoning, identifying task features that predict which regime a problem falls into.

## Hypotheses
- **H1**: For mathematical proof generation, verification is strictly easier than generation (polynomial-time checkable), and RLHF-style methods can leverage this gap effectively. Prediction: reward models trained on proof-verification signals converge faster and generalize better than those trained on preference data.
- **H2**: For open-ended reasoning tasks (planning, creative problem-solving), the generation-verification gap collapses — verifying the quality of a plan or solution is computationally as hard as generating a good one. Prediction: self-consistency and majority voting yield no statistically significant improvement on planning benchmarks.
- **H3**: The verification complexity class of a task predicts whether self-consistency and majority voting improve performance. Tasks with polynomial-time verification show improvement; tasks without do not. This is testable across existing benchmarks.

## Methodology
1. **Literature review**: Survey classical complexity-theoretic verification results (P vs NP, interactive proofs, PCP theorem, AM/MA), existing work on LLM output verification, reward model limitations, and scalable oversight proposals. Map the landscape of what is formally known about verification hardness.
2. **Formal framework development**: Define a verification complexity hierarchy for LLM reasoning tasks. Formalize the generation-verification gap. Prove theorems about gap collapse for specific task families. Connect to interactive proof systems (the verifier as a bounded computational agent). Develop the connection between verification complexity and trainability of reward models.
3. **Empirical validation**: Design controlled experiments testing predictions from the theoretical framework. Measure self-consistency and majority voting effectiveness across tasks with varying verification complexity. Test whether verification complexity predicts reward model training dynamics. Use existing benchmarks (GSM8K, MATH, PlanBench, ARC) plus targeted synthetic tasks.
4. **Paper writing and submission**: Write the paper in NeurIPS format. Lead with theoretical contributions (definitions, theorems, proofs), follow with empirical validation, close with implications for AI safety and scalable oversight. Target May 4 abstract deadline.

## Expected Contributions
- A formal verification complexity hierarchy for LLM reasoning tasks, grounded in classical complexity theory
- Proofs that the generation-verification gap collapses for specific task families under standard complexity assumptions
- A predictive theory connecting verification complexity to the effectiveness of self-consistency, majority voting, and reward-model-based training
- Empirical validation across mathematical reasoning, planning, and creative problem-solving domains
- Concrete implications for AI safety: formal characterization of when oversight of AI outputs is and is not tractable

## Timeline
- **Phase 1** (Weeks 1–3, Mar 21 – Apr 10): Literature review of complexity-theoretic verification results, interactive proof systems, and LLM verification methods. Deliverable: comprehensive literature synthesis.
- **Phase 2** (Weeks 3–6, Apr 7 – Apr 25): Formal framework development. Define verification complexity hierarchy, prove core theorems, formalize gap collapse conditions. Deliverable: complete formal framework with proofs.
- **Phase 3** (Weeks 5–8, Apr 21 – May 1): Empirical validation experiments. Test predictions on existing benchmarks. Deliverable: experimental results with statistical analysis.
- **Phase 4** (Weeks 7–9, May 1 – May 6): Paper writing and submission. Deliverable: camera-ready NeurIPS submission.

Note: Phases overlap deliberately. Framework development begins before literature review is fully complete; empirical work begins as soon as predictions are formalized. Buffer is minimal given the May 6 deadline — scope may need to be narrowed to core theorems plus targeted validation.

## Resource Requirements
- **Compute**: Minimal for a theory paper. ~$100 for empirical validation experiments (API calls to Claude, GPT-4o, open-source models for self-consistency/voting experiments on existing benchmarks). ~10K API calls total.
- **Data**: Existing public benchmarks only (GSM8K, MATH, PlanBench, ARC). No custom data collection required.
- **External tools**: LaTeX, standard Python scientific stack (scipy, matplotlib). No special tooling.
- **Estimated cost**: ~$100 total compute. Well within monthly budget, especially given reasoning-gaps entering submission phase.

## Risk Factors
- **Theorems are too weak or already known**: Core results may end up being straightforward corollaries of existing complexity theory. Mitigation: focus on the novel connection to LLM training methods (RLHF, self-consistency) rather than pure complexity results. The contribution is the bridge, not the endpoints.
- **Empirical validation is inconclusive**: Self-consistency experiments may not cleanly separate verification-easy from verification-hard tasks. Mitigation: use synthetic tasks with provably different verification complexity as controlled experiments, supplementing natural benchmarks.
- **Scope creep into full complexity theory paper**: The connection to interactive proofs, PCP, and zero-knowledge could expand indefinitely. Mitigation: strict scope to verification of LLM outputs specifically. Relegate general complexity results to related work.
- **Timeline pressure from NeurIPS deadline**: 6.5 weeks is tight for a theory paper with empirical validation. Mitigation: if theorems take longer than expected, submit a theory-only paper and add empirics for camera-ready or target ICLR 2027 instead.
