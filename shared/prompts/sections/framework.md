# Framework / Theory Section Guide

## Purpose
Present your formal contribution: definitions, theorems, and the conceptual
machinery that makes predictions. This is the intellectual core of the paper.

## Structure

### Definitions First
Number every definition (Definition 1, 2, 3...). For each:
1. **Motivate it** — one sentence explaining why this concept is needed.
2. **State it formally** — precise mathematical or formal language.
3. **Ground it with the running example** — show how the definition applies
   to a concrete instance the reader can follow.

Build complexity gradually: simple, self-contained definitions first, then
derived concepts that depend on earlier ones.

### Running Example
Choose one concrete example and thread it through the entire section. Every
definition, every theorem should be illustrated with this same example. The
reader should be able to understand the framework purely through the example
even if the formalism is dense.

### Theorems and Proof Sketches
Place theorems immediately after the definitions they depend on. For each theorem:
1. **State the theorem formally** with all conditions.
2. **Give a proof sketch** (2-3 sentences): state the key insight and the
   proof technique. "The proof proceeds by reduction from X to Y, showing
   that any instance of Z can be encoded as..."
3. **State the implication** — what does this theorem predict about real systems?
4. **Defer the full proof** to the appendix with a clear reference.

### Predictions
End the section with explicit, numbered predictions that follow from the theorems.
These predictions are what the experiments section will test. Each prediction
should be falsifiable: "Prediction 1: Tasks in Type 4 will show accuracy
below 60% for all models, because Theorem 2 implies..."

## Rules

- **Definitions before theorems.** Never reference a concept before defining it.
- **One concept per definition.** Don't pack two ideas into Definition 3.
- **Proof sketches, not full proofs, in main text.** Reviewers want the key idea,
  not every epsilon-delta step. Full proofs go in the appendix.
- **Make predictions explicit and testable.** Vague implications like "this
  suggests models might struggle" are not predictions.
- **Target ~20% of main text** (per paper-style.yaml).

## Common Mistakes
- Presenting definitions without motivation — the reader doesn't know why they
  should care about Definition 4 until you tell them.
- Skipping the running example — formalism without grounding is unreadable.
- Stating theorems without connecting them to empirical predictions.
- Putting a 2-page proof in main text that should be in the appendix.
- Introducing notation not established in Background.
