# On the Optimal Depth of Chain-of-Thought: A Complexity-Theoretic Analysis

## Title
On the Optimal Depth of Chain-of-Thought: A Complexity-Theoretic Analysis

## Target Venue
ICLR 2027 (submission deadline ~Sep/Oct 2026)

## Research Area
Computational Complexity x LLM Reasoning

## Motivation
Recent work on Chain-of-Thought (CoT) reasoning in LLMs has produced contradictory findings about the relationship between CoT length and performance. "Demystifying Long Chain-of-Thought Reasoning" argues that longer CoT improves reasoning quality. "When More is Less" demonstrates that extended CoT can degrade performance. "SafeChain" reveals safety-performance tradeoffs in CoT length. These contradictions are not errors — they reflect an unrecognized confound: the computational complexity of the underlying task. We hypothesize that optimal CoT depth is determined by the verification complexity of the target problem. This resolves all three contradictions under a unified complexity-theoretic framework: longer CoT helps when the task requires it (NP-hard verification), hurts when it doesn't (polynomial verification), and introduces compounding noise when it exceeds the complexity boundary.

## Research Goals

### Primary
1. **Formalize optimal CoT depth** as a function of task complexity class and input size. Define what "optimal" means: the number of reasoning steps that maximizes correctness while minimizing hallucination cascades.
2. **Prove complexity-conditioned bounds** on useful CoT depth. Show that for tasks in TC^0, optimal depth is O(1); for tasks requiring super-constant circuit depth (NP-complete under standard assumptions), optimal depth scales polynomially; beyond the complexity boundary, additional steps degrade performance.
3. **Resolve the CoT length contradiction** by showing that each existing paper's findings are predicted by the framework when accounting for the complexity distribution of their evaluation tasks.

### Secondary
4. Characterize the **noise accumulation function** — how error compounds across CoT steps and how this interacts with task complexity to create a depth ceiling.
5. Connect to the **reasoning gap framework** from our prior work, extending it from the capability dimension (which problems can LLMs solve?) to the depth dimension (how much reasoning is optimal?).

## Hypotheses
- **H1**: For tasks solvable within the transformer's native complexity class (TC^0), optimal CoT depth is 0 — any CoT steps introduce noise without benefit, regardless of baseline accuracy level.
- **H2 (Easy-task regime)**: For tasks with CoT complexity c(n) ≤ 1/η (where η is per-step error), optimal depth equals c(n) — the model can fully solve the task, and depth tracks complexity.
- **H3 (Hard-task regime / Capability ceiling)**: For tasks with CoT complexity c(n) > 1/η, optimal depth saturates at 1/η regardless of task complexity. Noise caps useful depth before sufficient computation is reached. This capability ceiling is the key novel prediction.
- **H4**: The contradiction between existing CoT length papers dissolves when controlling for the CoT complexity of their evaluation tasks relative to each model's capability ceiling.

## Methodology
1. **Literature survey**: Survey CoT length/depth studies (pro-length, anti-length, and conditional findings). Survey computational complexity foundations relevant to reasoning depth (circuit depth, proof complexity, space-bounded computation). Survey empirical CoT scaling results.
2. **Formal framework**: Define CoT depth as a function d*(C, n) mapping (complexity class C, input size n) to optimal step count. Formalize the noise accumulation model: each step has error probability epsilon, and k steps compound to create a depth ceiling. Define "useful reasoning step" vs. "noise step" formally.
3. **Complexity-conditioned bounds**: Prove upper and lower bounds on d*(C, n) for C in {P, NP, coNP, PSPACE}. Use circuit complexity results (TC^0 bounds on transformers) to connect to concrete architectures. Prove that the optimal depth curve has a single maximum — performance increases then decreases with depth.
4. **Noise accumulation analysis**: Prove that per-step error accumulation creates a natural depth ceiling. Characterize how this ceiling depends on model capacity, task complexity, and prompt structure. Connect to error-correcting code theory for the "self-correction" regime.
5. **Empirical validation**: Design a benchmark suite with tasks of known complexity class and varying input size. Measure performance as a function of CoT depth (1, 2, 4, 8, 16, 32 steps). Validate that the empirical optimal depth matches theoretical predictions per complexity class.
6. **Dispute resolution**: Re-analyze the evaluation task distributions from the three contradictory papers. Show that their task mixes have different complexity profiles, predicting their different conclusions about CoT length.
7. **Paper writing**: ICLR 2027 format. Structure: introduction with the contradiction, formal framework, main results (3-4 theorems), noise analysis, empirical validation, dispute resolution, discussion connecting to reasoning-gaps and verification-complexity.

## Expected Contributions
- A formal framework for optimal CoT depth as a function of computational complexity
- Complexity-conditioned bounds on useful reasoning depth (theorems with proofs)
- Resolution of the CoT length contradiction in the literature
- A noise accumulation model explaining why longer CoT eventually hurts
- Empirical validation across tasks of known complexity class
- Connection to the broader program on formal foundations of LLM reasoning (reasoning-gaps, verification-complexity)

## Timeline
- **Phase 1** (Weeks 1-3): Literature survey — CoT length studies, complexity foundations, noise/error models
- **Phase 2** (Weeks 4-7): Formal framework — define d*(C, n), noise accumulation model, key definitions
- **Phase 3** (Weeks 8-12): Core proofs — complexity-conditioned bounds, noise ceiling theorem, optimal depth characterization
- **Phase 4** (Weeks 13-16): Empirical validation — benchmark design, experiments across complexity classes
- **Phase 5** (Weeks 17-19): Dispute resolution — re-analyze existing papers through our framework
- **Phase 6** (Weeks 20-24): Paper writing and polishing. Buffer: 2-3 weeks before ICLR deadline.

## Resource Requirements
- **Compute**: ~$300 for empirical validation. Multiple LLMs (GPT-4, Claude, open-source) on controlled tasks with varying CoT depth. Estimated ~15K API calls across 4 complexity classes x 6 depth settings x 3 models x multiple instances.
- **Data**: Synthetically generated tasks with known complexity class. Arithmetic (P), SAT instances (NP), graph problems (varying complexity), formal verification tasks (coNP).
- **External tools**: LaTeX, Python for experiments, standard ML stack.

## Risk Factors
- **Bounds too loose**: Complexity-theoretic bounds may be too loose to be empirically predictive. Mitigate by proving tight bounds for specific complexity classes and validating empirically.
- **CoT depth not cleanly controllable**: Models may not respect depth instructions. Mitigate by using structured prompting (numbered steps) and filtering for actual step count.
- **Noise model too simplistic**: Real CoT errors may not follow independent per-step accumulation. If independent, the result (exponential decay) is trivially provable and may be too obvious. If correlated (more realistic), clean bounds become much harder. Mitigate by proving results under both assumptions and characterizing the gap.
- **Depth vs. length gap**: The dispute papers likely measure CoT *length* (tokens), not *depth* (logical steps). The framework needs a formal bridge between the two. Mitigate by defining a length-to-depth mapping and analyzing when length is a good proxy for depth.
- **Prior work overlap**: CoT scaling is a hot topic. Mitigate by focusing on the complexity-theoretic angle — no existing work takes this formal approach. Our contribution is the theoretical framework, not the empirical observation.
