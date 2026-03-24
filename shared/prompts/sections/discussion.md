# Discussion Section Guide

## Purpose
Explain what the results mean beyond the numbers. Connect findings to practice,
theory, and the field's open questions. Be honest about what you didn't do.

## Structure

### Practical Implications (lead with this)
What should practitioners DO differently based on your findings? Be concrete:
"Engineers building multi-step reasoning systems should expect CoT to fail for
tasks requiring NP-hard verification" is actionable. "Our results have
implications for the field" is not.

Give 2-3 specific recommendations. If your paper doesn't change anyone's
behavior, this paragraph forces you to articulate why it should.

### Connections to Theory
How do your results fit into the broader theoretical landscape? Do they support
or challenge existing frameworks? What do they tell us about the nature of the
problem? This is where you can be speculative — but label speculation clearly.

### Limitations (be honest and specific)
Name the real limitations, not strawmen. Each limitation should be:
- **Specific**: "Our evaluation covers 9 synthetic tasks but no real-world
  applications" — not "Limitations exist."
- **Honest**: If the benchmark is artificial, say so. If sample sizes are small
  for some conditions, say so.
- **Constructive**: For each limitation, briefly note how it could be addressed.

Do NOT be defensive. Reviewers respect authors who understand their own
paper's boundaries. Trying to minimize limitations reads as evasive.

### Future Work (3-4 concrete next steps)
Each future direction should have enough detail that someone could start working
on it. Include:
- What the research question would be
- What data or experiments would be needed
- Why you think it would yield interesting results

"Extend to more models" is not a future direction. "Evaluate Gemini Ultra on
Type 5-6 tasks to test whether architectural differences in mixture-of-experts
affect verification complexity bounds" is.

## Rules

- **Do NOT repeat the results.** The reader just finished the experiments
  section. Reference specific findings by name ("the Type 4 result") but don't
  re-state the numbers.
- **Practical implications first, theory second.** Most readers care about
  "what does this mean for me?" before "what does this mean for the field?"
- **Target ~15% of main text** (per paper-style.yaml).
- **No new data here.** All quantitative claims belong in experiments.

## Common Mistakes
- Restating every result from Section 5 in slightly different words.
- Vague limitations: "Our work has limitations" tells the reviewer nothing.
- Vague future work: "Further research is needed" — banned phrase.
- Skipping practical implications entirely — the section becomes a weaker
  version of the conclusion.
- Being either too defensive ("despite these limitations, our work is still
  significant") or too dismissive ("we leave this minor issue for future work").
