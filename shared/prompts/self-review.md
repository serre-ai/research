# Self-Review Prompt

## Objective

Conduct a rigorous, honest review of a paper draft as if reviewing for a top venue. The goal is to identify weaknesses before external reviewers do, enabling targeted improvements. Do not be kind — be accurate.

## Input

- **Paper**: Path to the LaTeX source or compiled PDF
- **Target venue**: The conference/journal this will be submitted to
- **Draft stage**: Early draft / Complete draft / Pre-submission
- **Specific concerns**: Any areas the author is already worried about (optional)

## Review Protocol

Read the paper twice:
1. **First pass**: Read for high-level understanding. Can you state the contribution in one sentence? Does the paper flow logically?
2. **Second pass**: Read critically, evaluating each section against the rubric below.

## Rubric

### Novelty (1-10)
- 1-3: Incremental or already done. Contribution is unclear or trivially extends prior work.
- 4-6: Moderate novelty. New combination or application, but core ideas exist.
- 7-8: Clearly novel contribution that advances the field.
- 9-10: Paradigm-shifting. Opens a new research direction.

**Questions to ask**: Has this been done? Would an expert be surprised? Is the contribution clearly articulated?

### Correctness (1-10)
- 1-3: Fundamental errors in proofs, methodology, or experimental design.
- 4-6: Mostly correct but with gaps, unstated assumptions, or weak controls.
- 7-8: Sound methodology with minor issues.
- 9-10: Rigorous and watertight.

**Questions to ask**: Are proofs complete? Are experiments properly controlled? Are statistical claims justified? Are there hidden assumptions?

### Significance (1-10)
- 1-3: Results don't matter much. Limited practical or theoretical impact.
- 4-6: Useful contribution but limited scope or applicability.
- 7-8: Important results that the community will build on.
- 9-10: Transformative. Changes how people think about the problem.

**Questions to ask**: Who benefits from this work? Will it be cited in 5 years? Does it enable new capabilities?

### Clarity (1-10)
- 1-3: Hard to follow. Key concepts undefined. Poor organization.
- 4-6: Readable but requires effort. Some sections unclear.
- 7-8: Well-written with clear exposition. A few rough spots.
- 9-10: Exceptional writing. Complex ideas made accessible.

**Questions to ask**: Can a graduate student in the field follow the paper? Are figures informative? Is notation consistent?

### Completeness (1-10)
- 1-3: Missing critical experiments, comparisons, or analysis.
- 4-6: Core experiments present but lacks ablations, baselines, or edge cases.
- 7-8: Thorough evaluation with minor gaps.
- 9-10: Exhaustive. Every reasonable question is addressed.

**Questions to ask**: Are there enough baselines? Ablations? Are failure cases analyzed? Is related work comprehensive?

### Reproducibility (1-10)
- 1-3: Cannot be reproduced from the paper. Missing critical details.
- 4-6: Could be reproduced with significant effort and guesswork.
- 7-8: Mostly reproducible. Code/data availability would help.
- 9-10: Fully reproducible. All details, code, and data provided.

**Questions to ask**: Are hyperparameters specified? Is the evaluation protocol clear? Could someone reimplement this from the paper alone?

## Overall Recommendation

Based on the rubric scores, assign one of:
- **Strong Accept**: Top 5% of submissions. Significant, novel, correct, well-written.
- **Accept**: Clear contribution. Minor weaknesses that don't undermine the core.
- **Borderline**: Has merit but significant weaknesses. Could go either way.
- **Reject**: Fundamental issues with novelty, correctness, or significance.
- **Strong Reject**: Below the threshold on multiple dimensions.

## Structured Output

```markdown
## Review Summary

**Overall recommendation**: [Strong Accept / Accept / Borderline / Reject / Strong Reject]

| Criterion       | Score | Key Issue |
|----------------|-------|-----------|
| Novelty         | X/10  | [one line] |
| Correctness     | X/10  | [one line] |
| Significance    | X/10  | [one line] |
| Clarity         | X/10  | [one line] |
| Completeness    | X/10  | [one line] |
| Reproducibility | X/10  | [one line] |

### Strengths
1. [Specific strength with reference to section/result]
2. [...]
3. [...]

### Weaknesses
1. [Specific weakness with reference to section/result]
2. [...]
3. [...]

### Questions for Authors
1. [Question that, if answered well, could change the recommendation]
2. [...]
3. [...]

### Suggestions for Improvement
1. [Actionable suggestion with specific guidance]
2. [...]
3. [...]

### Minor Issues
- [Typos, formatting, citation issues, etc.]
```

## Guidelines for the Reviewer Agent

- Be specific. "The experiments are weak" is useless. "Table 2 lacks comparison against [baseline X] which achieves Y on the same benchmark" is actionable.
- Distinguish fatal flaws from fixable issues.
- If you're unsure whether a proof is correct, say so explicitly rather than assuming.
- Check every table and figure: are axes labeled? Are numbers consistent with the text?
- Verify that the abstract accurately reflects the paper's actual contributions.
- Note where the paper overclaims (common in introductions and conclusions).
- Check that limitations are honestly discussed, not buried.
