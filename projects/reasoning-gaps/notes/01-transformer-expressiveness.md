# Literature: Transformer Expressiveness and Circuit Complexity

## Core Papers

### Circuit Complexity Characterizations

**Merrill & Sabharwal, "Saturated Transformers are Constant-Depth Threshold Circuits," TACL 2022.**
Saturated attention transformers with floating-point activations recognize only TC⁰ languages. First rigorous upper bound.

**Merrill & Sabharwal, "The Parallelism Tradeoff," TACL 2023.**
Log-precision transformers are in uniform TC⁰. If L ≠ P, cannot solve linear equalities or arbitrary CFGs. The parallelism that makes transformers scalable is what limits their computation.

**Merrill & Sabharwal, "A Logic for Expressing Log-Precision Transformers," NeurIPS 2023.**
Log-precision transformers = FO + Majority quantifiers. Tightest known upper bound via descriptive complexity.

**Chiang et al., "Transformers in DLOGTIME-Uniform TC⁰," 2024.**
Strengthened to DLOGTIME-uniform TC⁰ (strongest natural uniformity condition).

**"Circuit Complexity Bounds for RoPE-based Transformer Architecture," EMNLP 2025.**
RoPE transformers (LLaMA etc.) with d ≤ O(n) cannot solve arithmetic/Boolean formula evaluation.

### Hard Attention Results

**Hahn, "Theoretical Limitations of Self-Attention," TACL 2020.**
Hard attention transformers cannot recognize PARITY or Dyck-1. Within AC⁰.

**Yang, Chiang, Angluin, "Masked Hard-Attention Transformers = Star-Free Languages," NeurIPS 2024.**
Exact characterization: hard attention with causal masking = LTL = star-free languages.

### Expressiveness vs. Learnability

**Hahn & Rofin, "Why are Sensitive Functions Hard for Transformers?" ACL 2024 (Best Paper).**
Loss landscape constrains sensitivity. Highly sensitive functions create isolated, brittle optima. Expressiveness ≠ learnability.

**Chiang & Cholak, "Overcoming a Theoretical Limitation of Self-Attention," ACL 2022.**
Layer normalization enables soft-attention to recognize PARITY. Small architectural details qualitatively change expressiveness.

**Kozachinskiy, "Parity, Sensitivity, and Transformers," 2026.**
Whether parity is computable by a single-layer transformer remains open.

### Depth Results

**Merrill & Sabharwal, "A Little Depth Goes a Long Way," NeurIPS 2025.**
Θ(log n) depth enables regular languages and graph connectivity. Depth scaling more efficient than width or CoT. Unless NC = P, polylog depth ≠ P.

**Sanford, Hsu, Telgarsky, "Representational Strengths and Limitations," NeurIPS 2023.**
Depth separation via communication complexity arguments.

**Sanford, Hsu, Telgarsky, "Transformers, Parallel Computation, and Logarithmic Depth," ICML 2024.**
Constant self-attention layers ≈ constant MPC rounds. Formal parallel computation equivalence.

**Sanford, Hsu, Telgarsky, "One-Layer Transformers Fail to Solve Induction Heads," 2024.**
Communication complexity proof: induction heads require depth ≥ 2 (exponential separation).

### Chain-of-Thought Expressiveness

**Merrill & Sabharwal, "The Expressive Power of Transformers with Chain of Thought," ICLR 2024.**
Log steps → ≤ L. Linear steps → regular languages. Polynomial steps → exactly P. The definitive framework.

**Li, Liu, Zhou, Ma, "Chain of Thought Empowers Transformers to Solve Inherently Serial Problems," ICLR 2024.**
Without CoT: AC⁰. With T steps: circuits of size T. Concrete examples: permutation composition, iterated squaring.

**Bavandpour et al., "Lower Bounds for CoT Reasoning in Hard-Attention Transformers," 2025.**
Parity CoT length is optimal. Multiplication requires Ω(N) steps.

### Looped Transformers

**Giannou et al., "Looped Transformers as Programmable Computers," ICML 2023.**
Constant layers in a loop → Turing complete with appropriate encoding.

**Saunshi et al., "Reasoning with Latent Thoughts," ICLR 2025.**
k-layer transformer looped L times ≈ kL-layer non-looped. Looping = implicit CoT.

### Architecture Comparisons

**Delétang et al., "Neural Networks and the Chomsky Hierarchy," ICLR 2023.**
Chomsky hierarchy predicts generalization failures. Transformers and RNNs fail on non-regular tasks.

**Liu et al., "Transformers Learn Shortcuts to Automata," ICLR 2023.**
O(log T) layers suffice for length-T FSA simulation via hierarchical shortcuts (Krohn-Rhodes theory).

**Wen et al., "RNNs are not Transformers (Yet)," ICLR 2025.**
RNNs can't match transformers on in-context retrieval. Streaming lower bounds from communication complexity.

**"Computational Limits of State-Space Models and Mamba," 2024.**
SSMs/Mamba also in TC⁰. The ceiling is architecture-agnostic.

### Formal Frameworks

**Strobl et al., "What Formal Languages Can Transformers Express?" TACL 2024.**
Unified taxonomy: LHAT/RHAT ⊂ AC⁰, AHAT/SMAT ⊂ TC⁰, decoders+steps up to P. Essential reference.

**Weiss, Goldberg, Yahav, "Thinking Like Transformers" / RASP, ICML 2021.**
RASP programming language maps to transformer computations. Standard intermediate formalism.

**Strobl et al., "Transformers as Transducers," TACL 2025.**
Extends from recognition to generation (string-to-string transduction).

**Pérez, Barceló, Marinković, "Attention is Turing Complete," JMLR 2021.**
Arbitrary-precision → Turing complete. Important caveat: unrealistic assumption.

### Verification

**Salzer et al., "Transformer Encoder Satisfiability," 2024.**
TRSAT is undecidable for standard variants. Quantized: decidable but NEXPTIME-hard.

## The Central Open Question: TC⁰ vs NC¹

Whether TC⁰ = NC¹ is a major open problem. If TC⁰ ≠ NC¹ (widely believed), fixed-depth transformers fundamentally cannot solve directed graph reachability, Boolean formula evaluation, or arbitrary CFL parsing.
