# Literature Survey: CoT Depth Optimization and Complexity Theory

Date: 2026-04-01

## 1. The Three Dispute Papers

### 1.1 Pro-Length: Yeo et al. (2025)

**Citation:** Edward Yeo, Yuxuan Tong, Morry Niu, Graham Neubig, Xiang Yue. "Demystifying Long Chain-of-Thought Reasoning in LLMs." arXiv:2502.03373. Feb 2025.

**Thesis:** Scaling inference compute through long CoT enables backtracking and error correction. SFT on long CoT data + RL yields the best results.

**Tasks:** MATH-500 (in-domain), AIME 2024, TheoremQA, MMLU-Pro-1k (all OOD). **Complexity profile: high-difficulty, multi-step — tasks where longer CoT is expected to help.**

**Setup:** Llama-3.1-8B, Qwen2.5-7B-Math. PPO with cosine reward. CoT length controlled via context windows (4K, 8K, 16K tokens).

**Key results:**
- Long CoT SFT on MATH-500: >70% accuracy vs. short CoT SFT: <55%
- Qwen2.5-Math-7B: Base 52.0% → SFT+RL 85.9% on MATH-500
- Emergent long CoT patterns: 54.1% vs. constructed: 48.2%

**Theoretical framing:** None. Purely empirical.

### 1.2 Anti-Length (with theory): Wu et al. (2025)

**Citation:** Yuyang Wu, Yifei Wang, Ziyu Ye, Tianqi Du, Stefanie Jegelka, Yisen Wang. "When More is Less: Understanding Chain-of-Thought Length in LLMs." arXiv:2502.07266. Feb 2025 (revised May 2025).

**Thesis:** Accuracy follows an **inverted U-shaped curve** with CoT length. Optimal length increases with task difficulty but decreases with model capability.

**Tasks:** Synthetic arithmetic (binary tree addition, depths T=12-80), MATH Level 5, GPQA. **Complexity profile: synthetic task provides precise control; real tasks are high-difficulty.**

**Setup:** GPT-2 variants (5-9 layers, synthetic), Qwen2.5 Instruct (1.5B-72B), Llama3.1 (8B, 70B). CoT length controlled via `<t>` control token.

**Key results:**
- Optimal steps decrease with model size: 14 steps (1.5B) → 4 steps (72B) on MATH
- Small model on optimal-length CoT outperforms larger models on random-length CoT
- **Theorem 4.2: N*(M,T) = TZ/(M(Z+1))** where Z from Lambert W function

**THIS IS THE CLOSEST PRIOR WORK TO OUR THESIS.** Wu et al. prove the inverted-U exists and derive a scaling law. But their "task difficulty T" and "model capability M" are abstract parameters — not grounded in complexity classes. Our contribution: replace T with circuit complexity class and prove the scaling law from complexity theory.

### 1.3 Safety Dimension: Jiang et al. (2025)

**Citation:** Fengqing Jiang et al. "SafeChain: Safety of Language Models with Long Chain-of-Thought Reasoning Capabilities." arXiv:2502.12025. ACL 2025 Findings.

**Thesis:** Long CoT does not guarantee safe outputs. Three strategies (ZeroThink, LessThink, MoreThink) manipulate CoT length for safety.

**Tasks:** Safety: StrongReject, WildJailbreak. Reasoning: GSM8K, MATH-500, AIME 2024, HumanEval, MBPP, LiveCodeBench. **Complexity profile: mixed — easy (GSM8K) through hard (AIME).**

**Setup:** 13 LRMs including DeepSeek-R1 series, QwQ, Gemini-Thinking.

**Key results:**
- R1-70B: only 32.3% safe on safety benchmarks
- ZeroThink (no CoT) yields best safety
- Safety degrades as CoT length increases

**Relevance to our paper:** Secondary. The safety angle is orthogonal to our complexity-theoretic analysis. Useful as evidence that longer CoT isn't always better, but the mechanism is different (safety misalignment vs. noise accumulation).

## 2. Complexity-Theoretic Foundations

### 2.1 The Complexity Hierarchy of CoT

| Paper | Without CoT | With CoT | CoT Steps |
|-------|------------|----------|-----------|
| Li et al. (ICLR 2024) | AC^0 (bounded precision) | Circuits of size T | T steps |
| Merrill & Sabharwal (ICLR 2024) | TC^0 | P (generalized pre-norm) | poly(n) |
| Feng et al. (NeurIPS 2023) | Cannot do arithmetic | Can do arithmetic | Constant size model |
| Amiri et al. (ICML 2025) | — | Lower bounds | Linear for parity |
| Barcelo et al. (ICML 2025) | — | EH rank = exact steps | l steps for l-fold composition |

### 2.2 Key Paper: Li et al. (ICLR 2024)

**Citation:** Zhiyuan Li, Hong Liu, Denny Zhou, Tengyu Ma. "Chain of Thought Empowers Transformers to Solve Inherently Serial Problems." arXiv:2402.12875.

**Central theorem:** T CoT steps with constant-depth transformer = boolean circuits of size T.

Without CoT: bounded to AC^0. This is the cleanest CoT-complexity correspondence. Our paper should build on this as the foundation.

### 2.3 Key Paper: Merrill & Sabharwal (ICLR 2024)

**Citation:** William Merrill, Ashish Sabharwal. "The Expressive Power of Transformers with Chain of Thought." arXiv:2310.07923.

Three CoT regimes:
- O(log n) steps: marginally beyond standard transformers
- O(n) steps: all regular languages (projected pre-norm)
- poly(n) steps: exactly P (generalized pre-norm)

### 2.4 Lower Bounds: Amiri et al. (ICML 2025)

**Citation:** Alireza Amiri et al. "Lower Bounds for Chain-of-Thought Reasoning in Hard-Attention Transformers." arXiv:2502.02393.

First systematic CoT lower bounds. Parity needs linear CoT (tight up to constants). Also linear lower bounds for multiplication, median, reachability.

### 2.5 Exact Characterization: Barcelo et al. (ICML 2025)

**Citation:** Pablo Barcelo et al. "Ehrenfeucht-Haussler Rank and Chain of Thought." arXiv:2501.12997.

Ehrenfeucht-Haussler rank = exact minimum CoT steps. l-fold composition needs exactly l steps. Most precise known depth-problem correspondence.

### 2.6 Learnability: Kim & Suzuki (ICLR 2025 Oral)

**Citation:** Juno Kim, Taiji Suzuki. "Transformers Provably Solve Parity Efficiently with Chain of Thought." arXiv:2410.08633.

Expressivity ≠ learnability. With teacher forcing, parity learned in 1 gradient update. Without: substantially harder. Training regime matters for whether theoretical CoT capacity is realized.

### 2.7 Length Generalization: Huang et al. (NeurIPS 2025)

**Citation:** Yu Huang et al. "Transformers Provably Learn Chain-of-Thought Reasoning with Length Generalization." arXiv:2511.07378.

First optimization guarantee for NC^1-complete problems with CoT. Important: goes beyond TC^0.

## 3. Anti-Length / Noise Evidence

### 3.1 Don't Overthink It: Hassid et al. (2025)

**Citation:** Michael Hassid et al. "Don't Overthink it. Preferring Shorter Thinking Chains for Improved LLM Reasoning." arXiv:2505.17813.

Shortest chains up to **34.5% more accurate** than longest. LN-Super-49B: shortest 63.4% vs. longest 28.9% on AIME.

### 3.2 Curse of CoT: Zheng et al. (TMLR 2025)

**Citation:** Tianshi Zheng et al. "The Curse of CoT: On the Limitations of Chain-of-Thought in In-Context Learning." arXiv:2504.05081.

Direct answering outperforms CoT by **20.42% relative** on pattern-based tasks (ARC-AGI, MiniARC, RAVEN, SCAN). 16 LLMs, 9 benchmarks.

### 3.3 Mind Your Step: Liu et al. (ICML 2025)

**Citation:** Ryan Liu et al. "Mind Your Step (by Step): Chain-of-Thought can Reduce Performance on Tasks where Thinking Makes Humans Worse." arXiv:2410.21333.

Up to **36.3% absolute accuracy drop** with CoT on implicit statistical learning, visual recognition, exception-pattern classification.

### 3.4 Noisy Rationales: Zhou et al. (NeurIPS 2024)

**Citation:** Zhanke Zhou et al. "Can Language Models Perform Robust Reasoning in Chain-of-thought Prompting with Noisy Rationales?" arXiv:2410.23856.

Irrelevant thoughts: -1.4% to -19.8%. Inaccurate thoughts: **-2.2% to -40.4%**. Inaccurate steps are far more damaging than irrelevant ones.

## 4. Optimal Length / Efficiency

### 4.1 Thinking-Optimal Scaling: Yang et al. (NeurIPS 2025)

**Citation:** Wenkai Yang et al. "Towards Thinking-Optimal Scaling of Test-Time Compute for LLM Reasoning." arXiv:2502.18080.

Optimal length distribution differs across domains. Both overthinking and underthinking harm reasoning.

### 4.2 Deep-Thinking Tokens: Chen et al. (2026)

**Citation:** Wei-Lin Chen et al. "Think Deep, Not Just Long: Measuring LLM Reasoning Effort via Deep-Thinking Tokens." arXiv:2602.13517.

Introduces Deep-Thinking Ratio (DTR). Raw token counts are unreliable proxies for reasoning quality. **Supports our depth-vs-length distinction.**

### 4.3 Token Complexity: Lee et al. (ICML 2025)

**Citation:** Ayeong Lee, Ethan Che, Tianyi Peng. "How Well do LLMs Compress Their Own Chain-of-Thought? A Token Complexity Approach." arXiv:2503.01141.

Each task has intrinsic token complexity. Current compression far from information-theoretic limits.

### 4.4 CoT Compression: Li et al. (2026)

**Citation:** Juncai Li et al. "Chain Of Thought Compression: A Theoretical Analysis." arXiv:2601.21576.

Learning signal for high-order logical dependencies exponentially decays when skipping intermediate steps in irreducible problems.

## 5. Surveys

- **Stop Overthinking** (TMLR 2025, arXiv:2503.16419): First structured survey on efficient reasoning.
- **Towards Reasoning Era** (arXiv:2503.09567): Comprehensive taxonomy of long vs. short CoT.

## 6. Gap Analysis: What Our Paper Contributes

### What exists:
1. **Complexity classes of CoT:** Li et al. (T steps = circuits of size T), Merrill & Sabharwal (poly(n) = P)
2. **Lower bounds on CoT:** Amiri et al. (linear for parity), Barcelo et al. (exact for composition)
3. **Inverted-U phenomenon:** Wu et al. (Theorem 4.2, abstract parameters)
4. **Empirical evidence:** Pro-length on hard tasks, anti-length on easy/pattern tasks

### What's missing (our contribution):
1. **Nobody connects the inverted-U to complexity classes.** Wu et al.'s Theorem 4.2 uses abstract T (difficulty) and M (capability). We ground T in circuit complexity classes and M in transformer depth/TC^0.
2. **No formal noise ceiling theorem grounded in complexity.** The degradation beyond optimal depth is observed empirically but not formally tied to complexity-class boundaries.
3. **No explicit resolution of the contradiction.** Papers note that "it depends on the task" but nobody formally characterizes WHICH tasks benefit from depth by their complexity class.
4. **No bridge between depth (logical steps) and length (tokens).** Chen et al. (2026) introduce DTR but don't connect it to complexity theory.

### Positioning risk:
Wu et al.'s Theorem 4.2 is close. We must clearly differentiate: they prove existence of optimal length via abstract parameters. We prove optimal DEPTH via complexity classes. The distinction is:
- Their T = informal "task difficulty" (parameterized by arithmetic tree depth)
- Our T = circuit complexity class (P, NP, etc.) — a formal object with structural implications
- Their M = informal "model capability" (parameterized by layer count)
- Our M = transformer computation class (TC^0) — tied to established results

### Key theorem targets:
1. For tasks in TC^0 (solvable without CoT): d*(TC^0, n) = O(1)
2. For tasks requiring boolean circuit of size T: d*(T) ≥ T (from Li et al., already known)
3. **Novel:** For tasks in NP \ TC^0: d*(n) = Θ(poly(n)) with tight characterization
4. **Novel:** Noise ceiling: for d > d*(C, n), accuracy degrades as (1-η)^(d - d*(C,n))
5. **Novel:** Unification: map each dispute paper's task distribution to complexity profile, predict their findings
