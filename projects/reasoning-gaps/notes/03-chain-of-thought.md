# Literature: Chain-of-Thought Reasoning — Limits and Analysis

## Foundational Work

**Wei et al., "Chain-of-Thought Prompting Elicits Reasoning," NeurIPS 2022.**
CoT with few exemplars dramatically improves arithmetic, commonsense, symbolic reasoning. Emergent ability appearing only in ~100B+ parameter models.

## When CoT Helps vs. Fails

**Sprague et al., "To CoT or not to CoT?" 2024.**
Meta-analysis of 100+ papers, 20 datasets, 14 models. CoT helps **primarily on math and symbolic reasoning**. On MMLU, helps only on questions containing "=". CoT underperforms symbolic solvers.

**Stechly et al., "Chain of Thoughtlessness?" NeurIPS 2024.**
CoT in planning: only helps with hand-crafted problem-specific examples. Deteriorates with problem size.

**Meincke et al., "The Decreasing Value of Chain of Thought," Wharton 2025.**
For reasoning models (o3-mini, o4-mini), CoT prompting gives only 2.9–3.1% improvement. 20–80% more time required. Diminishing returns as models improve.

**Zhao et al., "Is CoT Reasoning a Mirage?" 2025.**
CoT is "a brittle mirage" beyond training distributions. Reflects structured inductive bias, not genuine reasoning.

## Formal Analysis

**Merrill & Sabharwal, "The Expressive Power of Transformers with Chain of Thought," ICLR 2024.**
Log steps → ≤ L. Linear → regular languages. **Polynomial → exactly P.** The definitive complexity characterization.

**Li et al., "Chain of Thought Empowers Transformers to Solve Inherently Serial Problems," ICLR 2024.**
Without CoT: AC⁰/TC⁰. With T steps: circuits of size T. CoT provides serial computation to parallel architectures.

**Feng et al., "Towards Revealing the Mystery behind Chain of Thought," NeurIPS 2023 (Oral).**
Without CoT, bounded-depth transformers need super-polynomial size for basic arithmetic. Constant-size transformers solve these with CoT.

**Sanford et al., "Transformers, Parallel Computation, and Logarithmic Depth," ICML 2024.**
Constant self-attention layers ≈ constant MPC rounds. Explains why serial tasks need CoT.

**"Compositional Reasoning with Transformers, RNNs, and Chain of Thought," NeurIPS 2025.**
For tree-structured CRQs: transformers need log depth; RNNs need log embedding dim; CoT needs n tokens for input size n. No architecture strictly dominates.

## Faithfulness

**Turpin et al., "Language Models Don't Always Say What They Think," NeurIPS 2023.**
CoT systematically biased by input features. Models rationalize biased answers without acknowledging bias. Up to 36% accuracy drop on BIG-Bench Hard.

**Lanham et al., "Measuring Faithfulness in CoT Reasoning," Anthropic 2023.**
Larger, more capable models produce **less** faithful reasoning. Large variation across tasks.

**Chen, Benton et al., "Reasoning Models Don't Always Say What They Think," Anthropic 2025.**
Claude 3.7 Sonnet acknowledges hints in only 25% of cases. RL improves faithfulness initially but plateaus.

**"Chain-of-Thought Reasoning In The Wild Is Not Always Faithful," ICLR 2025 Workshop.**
Unfaithfulness on non-adversarial prompts. Rates: GPT-4o-mini 13%, Haiku 3.5 7%, Sonnet 3.7+thinking 0.04%.

**"FaithCoT-Bench," 2025.**
"Scalability paradox" — larger models produce more accurate but more deceptively plausible unfaithful CoTs.

**Barez et al., "Chain-of-Thought Is Not Explainability," Oxford 2025.**
CoT imposes linear narrative on fundamentally non-linear parallel computation. Post-hoc rationalizations by construction.

**"Robust Answers, Fragile Logic," 2025.**
Under imperceptible perturbations, LLMs maintain correct answers with inconsistent reasoning. "Decoupling Hypothesis" — CoT and answer computation are separate processes.

### Safety Implications
**"When CoT is Necessary, Models Struggle to Evade Monitors," 2025.**
When tasks REQUIRE CoT-as-computation, models cannot easily hide reasoning. Good for safety monitoring.

**METR, "CoT May Be Highly Informative Despite Unfaithfulness," August 2025.**
When CoT is computationally necessary, it is informative. Only 3/21,272 trajectories showed plausible faithfulness failure on complex tasks.

## Test-Time Compute Scaling

**Snell et al., "Scaling LLM Test-Time Compute Optimally," ICLR 2025 (Oral).**
Optimal test-time compute can make smaller models outperform 4x larger ones. Strategy depends on problem difficulty.

**"Inference Scaling Laws," ICLR 2025.**
Problem difficulty is sufficient statistic for compute-optimal strategy. Smaller models + advanced inference can be Pareto-optimal.

**"Mirage of Test-Time Scaling," 2025.**
Non-monotonic relationship: accuracy rises then FALLS with more thinking. DeepSeek R1 plummets from 60% to near coin-flip beyond 12K thinking tokens. "Overthinking" phenomenon.

**"Inverse Scaling in Test-Time Compute," 2025.**
Failure modes: distraction by irrelevant info, overfitting to framings, spurious correlations, amplified concerning behaviors.

**"The Art of Scaling Test-Time Compute," December 2025.**
30B+ tokens, 8 models. No single strategy universally dominates. Models form "short-horizon" vs "long-horizon" categories.

**"Fragile Thoughts: CoT Perturbations," 2026.**
13 models, 3B–1.5T params. Math errors: 50–60% loss in small models, strong scaling benefits. Unit conversion: 20–30% loss at ALL scales. Extra steps: 0–6% degradation regardless of scale.

## Alternatives to CoT

**Gao et al., "PAL: Program-Aided Language Models," ICML 2023.**
Offload execution to Python interpreter. Outperforms CoT by 15% on GSM8K. **Tool use strictly dominates CoT** on tasks where CoT helps.

**Li et al., "Chain of Code," ICML 2024.**
CoT + "LMulator" code emulation. 84% on BIG-Bench Hard (+12% over CoT).

**Schuurmans, "Memory Augmented LLMs are Computationally Universal," 2023.**
External read-write memory → Turing completeness. Alternative to CoT for computational universality.

**Schuurmans et al., "Autoregressive LLMs are Computationally Universal," 2024.**
Extended autoregressive decoding → Turing complete via Lag systems.

**Du et al., "Improving Factuality through Multiagent Debate," ICML 2024.**
Multi-agent debate as parallel alternative to serial CoT.

## Key Insight for Our Paper

CoT is the primary mechanism for escaping TC⁰ bounds. But:
1. It helps only on problems requiring **bounded serial composition** (math, symbolic execution)
2. It fails on problems requiring **unbounded recursion, search, or parallel decomposition**
3. It is often unfaithful — but precisely when it IS computationally necessary, it IS faithful
4. Tool use and external computation strictly dominate CoT where applicable

This maps perfectly to our framework: CoT closes gaps for problems at the TC⁰ boundary that need serial depth, but cannot close gaps requiring computation beyond the CoT budget or outside the serial paradigm.
