# arxiv-scout

Literature scanning skill for monitoring arxiv and Semantic Scholar.

## Usage
Used by Noor to scan for new papers relevant to active research projects.

## Sources

### arxiv API
- Base URL: `http://export.arxiv.org/api/query`
- Query format: `search_query=cat:{category}+AND+{keywords}&sortBy=submittedDate&sortOrder=descending&max_results=50`
- Categories: cs.CL, cs.AI, cs.LG, cs.CC

### Semantic Scholar API
- Base URL: `https://api.semanticscholar.org/graph/v1`
- Paper search: `/paper/search?query={query}&limit=20&fields=title,abstract,authors,year,citationCount`
- Citation lookup: `/paper/{paper_id}/citations?fields=title,abstract,year`

## Procedure
1. Query arxiv for each category with project-specific keywords
2. Parse Atom XML responses — extract title, abstract, authors, arxiv ID, categories
3. Score papers against project relevance criteria (see `references/arxiv-categories.md`)
4. For high-scoring papers, query Semantic Scholar for citation context
5. Return structured results sorted by relevance score

## Rate Limits
- arxiv: 1 request per 3 seconds (be polite)
- Semantic Scholar: 100 requests per 5 minutes (no key needed for basic access)

## Output
Returns JSON array of scored papers:
```json
[
  {
    "score": 4,
    "title": "...",
    "authors": ["..."],
    "arxiv_id": "2603.12345",
    "abstract": "...",
    "categories": ["cs.CL", "cs.AI"],
    "relevance_reason": "...",
    "relevant_projects": ["reasoning-gaps"]
  }
]
```
