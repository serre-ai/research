# Blog Post Prompt

## Objective

Convert an academic paper into an accessible, engaging blog post for a technical but non-specialist audience. The post should convey the key ideas and findings without requiring background in the specific subfield.

## Input

- **Paper**: Path to the paper source or PDF
- **Target audience**: ML practitioners / general tech audience / researchers in adjacent fields
- **Length**: Short (800-1200 words) / Standard (1500-2500 words) / Long-form (3000+ words)
- **Tone**: Technical but approachable. Think Distill.pub or The Gradient, not arxiv abstract.

## Structure

### 1. Hook / Headline
- Lead with the most surprising or consequential finding
- Frame it as a question or tension: "LLMs can write code but can't count to ten — why?"
- Avoid jargon in the opening paragraph
- The first sentence should make someone want to read the second sentence

### 2. The Problem in Plain Language
- What's the real-world problem or scientific question?
- Why should someone outside this subfield care?
- Use a concrete example or analogy to ground abstract concepts
- 2-3 paragraphs maximum

### 3. What Existed Before
- Brief context: what did people try and why wasn't it enough?
- Be fair to prior work but make the gap clear
- 1-2 paragraphs — don't turn this into a related work section

### 4. What We Did
- Describe the approach in intuitive terms first, then add precision
- Use diagrams or figure descriptions (describe what a key figure would show)
- Avoid notation; use words instead of symbols
- If there's a formal framework, explain the intuition behind each definition
- 3-5 paragraphs depending on complexity

### 5. Key Findings
- Lead with the headline result
- Present 2-4 key findings, each with:
  - The finding in one sentence
  - Why it's surprising or important
  - A concrete example or number that makes it tangible
- Describe figures: "Figure 3 shows that as problem complexity increases, model accuracy drops sharply — but only for certain problem types"
- Use comparisons: "X% better than the previous best" or "equivalent to going from Y to Z"

### 6. Why It Matters
- Practical implications: what should practitioners do differently?
- Theoretical implications: what does this change about how we understand the problem?
- Forward-looking: what does this enable or motivate?
- 1-2 paragraphs

### 7. Technical Deep-Dive (Optional)
- For readers who want the details
- Can include formal definitions, proof sketches, or algorithm descriptions
- Clearly demarcated so casual readers can skip it
- Use expandable sections or a "For the technically curious" heading

### 8. Limitations and Open Questions
- What doesn't the paper answer? (Be honest — builds credibility)
- What's the most interesting open question?
- 1 paragraph

### 9. Links and Resources
- Link to the paper (arxiv, venue)
- Link to code repository (if available)
- Link to related blog posts or explainers
- BibTeX citation block

## Writing Guidelines

- **No jargon without explanation**: If you must use a technical term, define it inline or in parentheses
- **Active voice**: "We found that X" not "It was found that X"
- **Concrete before abstract**: Show the example, then state the general principle
- **Honest about limitations**: Don't oversell. Readers trust authors who acknowledge boundaries.
- **Short paragraphs**: 3-5 sentences maximum. Use whitespace.
- **Subheadings**: Break up long sections. A reader should be able to skim headings and get the gist.

## Figure Descriptions

For each key figure from the paper, write a description of what a blog-friendly version would look like:
- What does the x-axis and y-axis represent (in plain language)?
- What's the key visual pattern the reader should notice?
- What's the takeaway caption?

## Output

Save to `paper/blog-post.md` in the project directory.

## Quality Criteria

- A smart person outside the field can understand the core contribution after reading
- No claim in the blog post is stronger than the claim in the paper
- At least one concrete example or analogy that makes the key insight tangible
- The post is self-contained (doesn't require reading the paper to make sense)
- Tone is engaging without being informal or clickbaity
