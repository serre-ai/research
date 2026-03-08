# Literature: Empirical Reasoning Failures in LLMs

## Taxonomies and Surveys

**Song, Han, Goodman, "Large Language Model Reasoning Failures," TMLR 2026.**
Dual-axis taxonomy: reasoning types (embodied/non-embodied, informal/formal) × failure types (architectural, application-specific, robustness). First comprehensive survey.

**Mohsin et al., "On the Fundamental Limits of LLMs at Scale," 2025.**
Proof-informed framework: five fundamental limitations (hallucination, context compression, reasoning degradation, retrieval fragility, multimodal misalignment). No computably enumerable model family can be universally hallucination-free.

## Compositional Reasoning Failures

**Dziri et al., "Faith and Fate: Limits of Transformers on Compositionality," NeurIPS 2023.**
Transformers solve compositional tasks via "linearized subgraph matching" — memorizing computation subgraphs rather than systematic algorithms. Performance decays rapidly with complexity. Tested: multi-digit multiplication, logic grids, dynamic programming.

**Li, Jiang, Xie et al., "Understanding and Patching Compositional Reasoning in LLMs," ACL 2024 Findings.**
Failures stem from improperly generated implicit reasoning in middle layers. MHSA modules are critical. Developed CREME patching method.

**Yu, Belinkov, Ananiadou, "Back Attention: Multi-Hop Reasoning," EMNLP 2025.**
Multi-hop failures stem from relation attribute extraction stage where conflicting logits reduce accuracy. Proposes "back attention" mechanism.

## State Tracking and Working Memory

**Gong & Zhang, "Self-Attention Limits Working Memory Capacity," 2024.**
As N-back difficulty increases, attention entropy increases and disperses. Self-attention directly constrains working memory capacity. Parallels executive attention theory.

**Hahn, "Theoretical Limitations of Self-Attention," TACL 2020.**
Self-attention cannot model periodic finite-state languages or hierarchical structure unless layers/heads grow with input length.

**Saparov et al., "Transformers Struggle to Learn to Search," ICLR 2025.**
Graph connectivity: difficulty increases with graph size. Not resolved by more parameters or CoT. Fundamental architectural limitation.

## Causal and Counterfactual Reasoning

**Yamin et al., "Failure Modes of LLMs for Causal Reasoning on Narratives," ICML 2025 Workshop.**
Two failure modes: (1) inferring causality from temporal order, (2) relying on memorized knowledge over narrative context.

**Joshi et al., "LLMs Are Prone to Fallacies in Causal Inference," EMNLP 2024.**
Post hoc fallacy persists even with randomized order. Models struggle to infer causation from counterfactuals.

## Mathematical and Logical Reasoning

**Mirzadeh et al., "GSM-Symbolic," ICLR 2025 (Apple).**
Adding one irrelevant clause → up to 65% performance drop across ALL SOTA models. Performance varies with numerical values in identical structures. Concludes: pattern matching, not reasoning.

**Wan et al., "LogicAsker," EMNLP 2024.**
34 atomic + 208 extended logic rules. Failure rates: 29%–90% across models. Fine-grained decomposition of logical reasoning failures.

**Nezhurina et al., "Alice in Wonderland," NeurIPS Scientific Methods Workshop 2024.**
Trivially simple counting/relational problems cause complete reasoning collapse. Models express strong overconfidence in wrong answers.

**Hazra et al., "3-SAT Phase Transition Characterization," 2025.**
LLM accuracy drops at 3-SAT phase transitions where statistical shortcuts are unavailable. Only DeepSeek R1 shows signs of genuine reasoning via in-context tree search.

## Mechanistic Analyses

**Zhang, "Comprehension Without Competence," 2025.**
"Computational split-brain syndrome" — instruction and action pathways are geometrically dissociated. LLMs articulate correct principles without reliably applying them. Failures are computational execution, not knowledge gaps.

**Berglund et al., "The Reversal Curse," ICLR 2024.**
Models trained on "A is B" fail to generalize to "B is A." Likelihood of correct reverse answer = random. Fundamental autoregressive limitation.

**"Negation: A Pink Elephant in the LLMs' Room?" 2025.**
Insensitivity to negation presence. Vision-language models drop ~25% on negated captions. Best models: ~39% on negation multiple-choice.

**"Limited Reasoning Space," 2025.**
"Reasoning collapse" — beyond critical chain length, accuracy drops catastrophically. Modeled via non-autonomous stochastic dynamical systems. Exponential decay with logical depth.

## Planning and Search

**Kambhampati et al., "LLMs Can't Plan," ICML 2024 (Position).**
GPT-4: ~30% on Blocksworld vs 78% human. CoT doesn't help. Self-verification degrades with more backprompts. Proposes LLM-Modulo with external verifiers.

**Stechly et al., "Chain of Thoughtlessness," NeurIPS 2024.**
CoT improvements in planning only with exceedingly problem-specific hand-annotated examples. Deteriorates with problem size.

## Cross-Cutting Themes

1. **Scale-resistant failures**: GSM-Symbolic, Alice in Wonderland, LogicAsker all show failures that barely improve with scaling → architectural, not capacity
2. **Pattern matching masquerading as reasoning**: Dziri (subgraph matching), GSM-Symbolic (value sensitivity), Zhao (distribution dependence)
3. **Comprehension-competence gap**: Models articulate correct rules but fail to apply them (Zhang 2025)
4. **Reasoning collapse at depth**: Exponential accuracy decay with logical chain length
5. **Specific operation failures**: Negation, reversal, counterfactual — each points to a structural limitation
