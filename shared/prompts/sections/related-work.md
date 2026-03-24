# Related Work Section Guide

## Purpose
Position your contribution against the field. The reader should finish this
section understanding exactly what's new about your work and why existing
approaches don't cover the same ground.

## Structure

### Group by Theme, Not Chronologically
Organize into 3-5 thematic subsections. Each subsection covers one line of
related research. Example groupings:
- "Chain-of-thought reasoning"
- "Computational complexity of inference"
- "Benchmark design for reasoning evaluation"

Within each group, cover the 2-4 most relevant papers. Don't aim for exhaustive
coverage — aim for positioning.

### The 3-5 Closest Competitors
Identify the papers most similar to yours and compare explicitly. For each:
1. **What they got right** — acknowledge their contribution genuinely.
   Be generous. "Wei et al. (2022) demonstrated that CoT prompting unlocks
   multi-step reasoning" — give credit.
2. **What they missed** — identify the specific gap. "However, their analysis
   does not distinguish between tasks where CoT aids computation vs. tasks
   where the reasoning structure itself is intractable."
3. **How you differ** — one sentence stating your advance. "We formalize this
   distinction using verification complexity classes."

### Closing Paragraph
End with a clear statement of what's novel about your approach relative to the
closest prior work. This is not a repetition of contributions — it's a
positioning statement. "Unlike [closest work], we [specific difference]. Unlike
[second closest], we [specific difference]."

## Rules

- **Be generous to prior work.** Acknowledge contributions genuinely before
  stating gaps. Papers that dismiss prior work read as insecure. Papers that
  build on prior work read as mature.
- **Position against competitors explicitly.** Don't just summarize related
  work — compare it to yours. Every paragraph should make clear how your
  contribution relates.
- **Group by theme.** Chronological ordering ("In 2020... In 2021... In 2022...")
  is lazy and unhelpful. The reader wants conceptual organization.
- **Target ~10% of main text** (per paper-style.yaml).
- **Minimum 30 references** total in the paper (per paper-style.yaml), with at
  least 5 from the last 12 months.

## Placement
Per paper-style.yaml, Related Work comes **after the contribution** (framework +
experiments), not before. This is NeurIPS/ICLR standard. The reader already
understands your approach, so positioning is more meaningful.

## Common Mistakes
- Turning related work into a literature review — summarizing 30 papers without
  comparing any of them to yours.
- Being dismissive: "Unlike all prior work, we are the first to..." — almost
  certainly untrue, and reviewers will notice.
- Missing the closest competitor — if a reviewer knows a paper you didn't cite
  that does something very similar, it's a red flag.
- Placing related work before the contribution, forcing the reader to evaluate
  positioning before understanding what you actually did.
- Including papers just to pad the reference count — every citation should serve
  a purpose.
