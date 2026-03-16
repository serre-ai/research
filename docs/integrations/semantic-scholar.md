# Semantic Scholar Integration

## Overview

Semantic Scholar is a free, AI-powered academic search engine by the Allen Institute for AI (AI2). Its Academic Graph API provides access to 200M+ papers with citation graphs, abstract embeddings, author tracking, and paper recommendations.

This integration upgrades Noor from a keyword-based arxiv scanner to a graph-navigating research scout capable of tracking citation velocity, detecting competing work, and discovering related papers through embedding similarity.

## API Details

- **Base URL:** `https://api.semanticscholar.org/graph/v1`
- **Auth:** API key via `x-api-key` header (free — request at https://www.semanticscholar.org/product/api)
- **Rate limit:** 1 req/s with API key. Batch endpoint handles up to 500 papers per call, making this generous.
- **Cost:** $0
- **Env var:** `SEMANTIC_SCHOLAR_API_KEY`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/paper/{paper_id}` | GET | Full metadata: abstract, citations, references, influential citations, fields of study |
| `/paper/search?query=` | GET | Keyword search with relevance ranking, returns top matches |
| `/paper/batch` | POST | Bulk lookup — up to 500 paper IDs per call |
| `/paper/{id}/citations` | GET | Papers that cite this paper (paginated) |
| `/paper/{id}/references` | GET | Papers this paper cites |
| `/recommendations/v1/papers/forpaper/{id}` | GET | Embedding-based paper recommendations |
| `/author/{id}` | GET | Author metadata |
| `/author/{id}/papers` | GET | All papers by an author (paginated) |

### Field Selection

All endpoints support a `fields` query parameter to select which fields to return:
```
?fields=title,abstract,citationCount,influentialCitationCount,year,authors,references
```

### Paper ID Formats

- Semantic Scholar ID: `649def34f8be52c8b66281af98ae884c09aef38b`
- arXiv: `arXiv:2201.11903`
- DOI: `DOI:10.18653/v1/2022.acl-long.244`
- ACL: `ACL:2022.acl-long.244`
- PMID, MAG, CorpusId also supported

## Integration Architecture

### New Skill: `semantic-scholar`

Location: `openclaw/skills/semantic-scholar/`

Commands:
- `semantic-scholar search "<query>" [--limit N]` — keyword search
- `semantic-scholar paper <id>` — full paper details
- `semantic-scholar citations <id> [--influential-only]` — who cites this paper
- `semantic-scholar recommend <id> [--limit N]` — find similar papers
- `semantic-scholar author <author_id>` — track a researcher
- `semantic-scholar batch <id1,id2,...>` — bulk lookup

### New Orchestrator Module: `orchestrator/src/semantic-scholar.ts`

Thin HTTP client wrapping the API with:
- Rate limiting (1 req/s with exponential backoff)
- Response caching (papers don't change often — 24h TTL)
- Field selection defaults per use case

### New DB Table: `paper_tracking`

```sql
CREATE TABLE paper_tracking (
    paper_id        TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    authors         JSONB,
    year            INT,
    citation_count  INT NOT NULL DEFAULT 0,
    influential_citations INT NOT NULL DEFAULT 0,
    fields_of_study JSONB,
    relevance_score REAL,
    project         TEXT,
    first_seen      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_polled     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE citation_snapshots (
    id              SERIAL PRIMARY KEY,
    paper_id        TEXT NOT NULL REFERENCES paper_tracking(paper_id),
    citation_count  INT NOT NULL,
    influential_citations INT NOT NULL,
    polled_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Weekly Citation Sweep (Cron)

A cron job (or Lev's nightly digest) runs `paper/batch` on all tracked papers, logs citation counts to `citation_snapshots`, and flags any paper with >10% citation growth in a week.

## Use Cases by Agent

| Agent | Use Case |
|-------|----------|
| **Noor** | Primary user. Keyword search + recommendations for literature discovery. Author tracking for key researchers. Replaces simple arxiv category scanning. |
| **Vera** | Cross-references claims in paper drafts against citation data. "Is this really the most-cited work on X?" |
| **Kit** | Looks up benchmark papers to find comparable eval setups and baselines. |
| **Maren** | Verifies related work section completeness. Are there highly-cited papers we're missing? |
| **Rho** | Checks if the team is ignoring contradictory evidence. Searches for papers that challenge our thesis. |

## Roadmap

### Phase 1: Core Client + Skill (INT-1)
- [ ] Create `orchestrator/src/semantic-scholar.ts` — HTTP client with rate limiting
- [ ] Create `openclaw/skills/semantic-scholar/` — skill wrapper
- [ ] Add `SEMANTIC_SCHOLAR_API_KEY` to VPS `.env`
- [ ] Wire into Noor's heartbeat: after arxiv scan, run recommendations on top findings
- [ ] Manual test: search for "chain-of-thought reasoning" and verify results

### Phase 2: Citation Tracking (INT-2)
- [ ] Create `paper_tracking` and `citation_snapshots` tables
- [ ] Seed with reasoning-gaps reference list (~30 papers)
- [ ] Build weekly citation sweep cron job
- [ ] Add citation velocity alerts to Sol's standup
- [ ] Add citation data to Lev's nightly digest

### Phase 3: Competing Work Detection (INT-3)
- [ ] Build recommendation-based competitor scanner
- [ ] Track authors of key competing groups
- [ ] Auto-file forum signal threads when competing work detected
- [ ] Wire into Noor's heartbeat: run competitor scan every 6h cycle

## References

- [API Documentation](https://api.semanticscholar.org/api-docs/)
- [API Tutorial](https://www.semanticscholar.org/product/api/tutorial)
- [API Release Notes](https://github.com/allenai/s2-folks/blob/main/API_RELEASE_NOTES.md)
- [Python Client](https://semanticscholar.readthedocs.io/)
