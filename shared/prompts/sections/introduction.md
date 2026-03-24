# Introduction Section Guide

## Purpose
The introduction sells the paper. A reader who finishes the intro should understand
what you did, why it matters, and why they should keep reading.

## Structure (4-5 paragraphs)

### Paragraph 1 — The Phenomenon
Open with a **concrete failure example**, not abstract motivation.
Show something surprising or broken: a specific model failing a specific task,
a counterintuitive result, a real-world consequence. Ground the reader immediately.

### Paragraph 2 — The Gap
What is missing in current understanding? Why don't existing explanations cover
the phenomenon from paragraph 1? Be specific: name the approaches that fall short
and say exactly where they break. One sentence per approach is enough.

### Paragraph 3 — Why the Gap Exists
Explain the structural reason current work misses this. Is it the wrong abstraction?
Missing formalism? Incomplete evaluation? This paragraph justifies the need for
your contribution — make the reader feel the gap is real and important.

### Paragraph 4 — Contributions
State contributions as a **numbered list of 3-5 items**. Each item should be one
sentence with a concrete, falsifiable claim. Not "We propose a framework" but
"We introduce a 6-type complexity taxonomy that predicts CoT accuracy within 5%."

### Final Sentence
End with: **"Our central thesis: [one sentence]."** This anchors the entire paper.

## Rules

- **NO forward references** like "In Section 3 we..." — the intro must stand alone.
- **Include one compelling data point** that hooks the reader. Pull the single most
  striking number from your results and put it in paragraph 1 or 2.
- **No roadmap paragraph.** Nobody reads "The remainder of this paper is organized
  as follows." The section headings are the roadmap.
- Use active voice: "We show" not "It is shown."
- Keep to ~1 page (12% of main text per paper-style.yaml).

## Common Mistakes
- Opening with "Large language models have shown remarkable..." — too generic.
- Listing contributions that are actually methodology steps, not results.
- Burying the hook after two paragraphs of background nobody asked for.
- Making claims without the one data point that makes them credible.
