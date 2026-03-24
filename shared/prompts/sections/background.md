# Background Section Guide

## Purpose
Give the reader exactly the machinery they need to understand your contribution.
Nothing more. This section is a service, not a literature review.

## Structure (3-4 subsections, ~1 page total)

### Notation Block
Define all notation **here**, not scattered through later sections. Use a compact
block or table format. Stick to standard notation wherever possible — do not invent
new symbols for existing concepts (e.g., use P, NP, PSPACE as-is).

### Key Concepts
Cover 2-3 concepts that are essential prerequisites. For each:
- One sentence definition
- One sentence explaining why it matters for this paper
- A citation to the canonical source

Skip anything a typical ML venue reviewer already knows (what a Transformer is,
what chain-of-thought prompting means). Include what they might not know from
adjacent fields (complexity classes, verification theory, formal methods).

### Problem Setup
State the formal problem your paper addresses. Use the notation you just defined.
This should be 1-2 paragraphs that translate the intuitive gap from the introduction
into a precise technical question.

### The Gap (closing paragraph)
End with one paragraph that bridges to your contribution: "Existing formulations
treat X as Y, but this misses Z. We address this by..." This is the transition
into your framework section.

## Rules

- **One page maximum.** Readers skip long backgrounds. If you need more space,
  move details to an appendix.
- **Standard notation first.** Only introduce custom notation when no standard
  exists. When you must define something new, motivate why.
- **No related work here.** Background is definitions and setup. Positioning
  against other papers belongs in Related Work.
- **No results here.** Don't preview your findings — that's what the intro does.

## Common Mistakes
- Spending half a page defining Transformers to a NeurIPS audience.
- Introducing notation in background but changing it in later sections.
- Including 15 citations of related approaches — that's Related Work, not Background.
- Forgetting to define a symbol that appears in Theorem 1.
