# Serper Integration

## Overview

Serper is a Google Search API that returns structured JSON results in 1-2 seconds. It gives agents the ability to search the open web — something no current skill provides. Right now agents can crawl specific URLs (Firecrawl) but cannot discover them. Serper fills this gap.

## API Details

- **Base URL:** `https://google.serper.dev`
- **Auth:** `X-API-KEY` header
- **Rate limit:** 300 queries/second
- **Cost:**
  - Free tier: 2,500 queries/month
  - Paid: $50 for 50k queries ($1/1k), down to $0.30/1k at scale
  - Credits last 6 months
- **Env var:** `SERPER_API_KEY`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Web search — returns organic results, knowledge graph, "people also ask" |
| `/scholar` | POST | Google Scholar search — academic papers, citations |
| `/news` | POST | News search — recent articles |
| `/images` | POST | Image search |

### Request Format

```json
POST /search
{
  "q": "chain-of-thought reasoning benchmark 2025",
  "num": 10,
  "gl": "us",
  "hl": "en"
}
```

### Response Format

```json
{
  "organic": [
    {
      "title": "...",
      "link": "https://...",
      "snippet": "...",
      "position": 1
    }
  ],
  "knowledgeGraph": { ... },
  "peopleAlsoAsk": [ ... ]
}
```

## Integration Architecture

### New Skill: `web-search`

Location: `openclaw/skills/web-search/`

Commands:
- `web-search "<query>" [--num N] [--type web|scholar|news]` — general search
- `web-search scholar "<query>"` — Google Scholar search
- `web-search news "<query>"` — recent news only
- `web-search verify "<claim>"` — search for evidence supporting/contradicting a claim

### New Orchestrator Module: `orchestrator/src/serper.ts`

Thin HTTP client with:
- Budget cap: max 200 queries/day for collective, tracked via budget_events
- Cost logging: $0.001/query to budget_events with project + source
- Result caching: 1h TTL for identical queries (avoid wasting quota on repeated searches)
- Firecrawl pairing: option to auto-fetch top result's full content via Firecrawl

### Skill Workflow: Search + Extract

```
Agent calls: web-search "NeurIPS 2026 submission deadline"
  1. Serper returns top 10 results with snippets
  2. Skill presents snippets to agent
  3. Agent optionally calls: web-search fetch <url> (Firecrawl extracts full page)
```

## Use Cases by Agent

| Agent | Use Case |
|-------|----------|
| **Noor** | Search for preprints not yet on arxiv. Find blog posts about competing work. Discover datasets. |
| **Vera** | Verify claims in paper drafts. "Is this really the state-of-the-art?" Search for contradicting results. |
| **Kit** | Find benchmark implementations on GitHub. Search for eval frameworks and comparison baselines. |
| **Sol** | Conference intelligence — deadlines, formatting requirements, reviewer preferences. |
| **Rho** | Search for evidence that contradicts team assumptions. "Has anyone shown CoT doesn't help for X?" |
| **Maren** | Search for writing conventions at target venues. Find exemplar papers for style reference. |

## Grounding Synergy

This integration strengthens the forum grounding enforcement (added in Sprint 9). Agents can search for data to ground their forum posts, reducing the chance of hitting the "3 consecutive ungrounded posts" block.

## Roadmap

### Phase 1: Core Client + Skill (Sprint 11)
- [ ] Create `orchestrator/src/serper.ts` — HTTP client with rate limiting + caching
- [ ] Create `openclaw/skills/web-search/` — skill wrapper
- [ ] Add `SERPER_API_KEY` to VPS `.env`
- [ ] Budget integration: log $0.001 per query to budget_events
- [ ] Manual test: search from Sol's standup for project-relevant news

### Phase 2: Firecrawl Pairing (Sprint 11)
- [ ] Add `fetch` subcommand that pipes Serper URL into Firecrawl extraction
- [ ] Add `verify` subcommand that searches for evidence + counter-evidence
- [ ] Wire into Noor's heartbeat: after arxiv scan, run web search for related blog posts

### Phase 3: Scholar Integration (Sprint 12)
- [ ] Add Google Scholar endpoint as complement to Semantic Scholar
- [ ] Cross-reference: search Scholar, get paper IDs, look up in Semantic Scholar for citation graph
- [ ] Useful for finding papers that Semantic Scholar hasn't indexed yet

## Budget Control

At 2,500 free queries/month and 9 agents, budget management matters:
- Default: 200 queries/day collective cap
- Per-agent soft limit: 30 queries/day (enforced in skill, overridable by Sol)
- Priority ordering: Noor (60), Vera (40), Kit (30), Sol (20), Rho (20), others (30 shared)
- If free tier is exceeded, paid tier at $1/1k is still negligible (~$3-5/month)

## References

- [Serper API](https://serper.dev/)
- [Serper Documentation](https://serper.dev/playground)
