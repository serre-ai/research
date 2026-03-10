# Literature Review Prompt

## Objective

Conduct a structured literature survey on a specific topic, producing a comprehensive annotated bibliography with synthesis. The output should inform research direction and identify gaps worth pursuing.

## Input

- **Topic**: The specific research question or area to survey
- **Project**: The project this survey serves (for relevance filtering)
- **Scope**: Approximate number of papers to cover (default: 20-40)
- **Seed papers**: 2-5 known papers to start from (if available)

## Search Strategy

### Phase 1: Seed Collection
1. Start with any provided seed papers
2. Search for the topic's foundational papers (highest citation count, survey papers)
3. Identify the top 3-5 venues where this work appears (conferences, journals, workshops)

### Phase 2: Forward and Backward Search
4. For each seed paper, review its references (backward search) for foundational work
5. Search for papers that cite the seeds (forward search) for recent extensions
6. Search by keyword combinations across:
   - Semantic Scholar API
   - ArXiv (cs.CL, cs.LG, cs.AI, stat.ML as appropriate)
   - Google Scholar (for cross-disciplinary work)

### Phase 3: Completeness Check
7. Verify coverage of all major research groups working on this topic
8. Check for very recent work (last 6 months) that may not yet be well-cited
9. Look for negative results and critiques of the dominant approach

### Keywords
Generate 5-10 keyword combinations. Example format:
- `"reasoning" AND "large language models" AND "limitations"`
- `"transformer" AND "expressiveness" AND "complexity"`

## Per-Paper Summary Format

For each paper, produce a structured entry:

```markdown
### [Key] Author et al. (Year) — Short Title

- **Full title**: [Complete title]
- **Authors**: [All authors]
- **Venue**: [Conference/Journal, Year]
- **URL**: [Link to paper]
- **Key contribution**: [1-2 sentences: what is new in this paper?]
- **Methodology**: [How did they approach the problem?]
- **Key results**: [Main findings, with numbers where relevant]
- **Relevance**: [How does this connect to our project? What can we build on or contrast with?]
- **Limitations**: [What's missing, flawed, or incomplete?]
- **Key quotes**: [1-2 direct quotes that capture the paper's core insight]
- **Cites/Cited-by**: [Notable connections to other papers in this survey]
```

## Synthesis Structure

After individual summaries, write a synthesis section organized as:

### Themes
Group papers into 3-6 thematic clusters. For each:
- Theme name and description
- Which papers belong to this theme
- The consensus view and any internal disagreements

### Evolution
How has thinking on this topic evolved? Key turning points?

### Gaps
What questions remain unanswered? Where do existing approaches fall short? Which gaps are most promising for new work?

### Contradictions
Where do papers disagree? What evidence exists on each side?

### Open Questions
5-10 specific, answerable research questions that emerge from this survey.

### Relevance to Our Project
How does this literature inform our specific hypotheses and methodology? What should we adopt, extend, or challenge?

## Output

Save the completed survey to `literature/<topic-slug>.md` in the project directory.

Update `status.yaml`:
- Set `progress.literature_review.status` to `in_progress` or `complete`
- Add key references to `key_references`
- Update `metrics.papers_reviewed`

## Quality Criteria

- Covers foundational, recent, and adjacent work
- Every paper summary has concrete relevance assessment (not just "related to our work")
- Synthesis identifies at least 3 non-obvious gaps or contradictions
- Minimum 20 papers for a focused survey, 40+ for a broad area
- No uncited claims in the synthesis section
