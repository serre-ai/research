# Continuous Literature Intelligence -- Real-Time Research Monitoring

**Status:** Proposed
**Priority:** High
**Estimated effort:** 16-22 hours
**Dependencies:** Knowledge graph (minimal version), existing daemon and API infrastructure

## Problem

The platform has no systematic way to discover relevant new papers. The Noor (scout) agent runs on a 6-hour heartbeat, but it operates without structured data sources -- it relies on ad hoc web searches during its session window. Meanwhile, arXiv publishes 100-200 relevant papers per day across cs.AI, cs.CL, cs.LG, and cs.CC. New concurrent work could invalidate our novelty claims, and we would not know until manual checking.

For a NeurIPS 2026 submission, failing to cite or acknowledge concurrent work is a reviewer red flag. The platform should detect relevant new papers within 24 hours of posting and surface them with explanations of their relevance to our active claims.

## Data Sources

### arXiv (primary, daily)

- RSS/Atom feeds for each category: `http://export.arxiv.org/rss/{category}`
- Categories to monitor: `cs.AI`, `cs.CL`, `cs.LG`, `cs.CC`
- Volume: ~100-200 new papers/day across these categories (with overlap)
- Free, no API key, no rate limit on RSS
- Feeds update daily around 00:00 UTC (new listings) and 20:00 UTC (replacements)

### Semantic Scholar (primary, citation monitoring)

- Base URL: `https://api.semanticscholar.org/graph/v1`
- Key endpoints:
  - `GET /paper/search?query=...&fields=title,abstract,authors,year,citationCount,externalIds` -- keyword search
  - `GET /paper/{paperId}?fields=title,abstract,citations,references` -- paper details
  - `GET /paper/{paperId}/citations?fields=title,abstract,year,authors` -- papers citing this one
  - `GET /recommendations?positivePaperIds=...&fields=title,abstract` -- similar papers
- Rate limit: 100 requests per 5 minutes (free tier), effectively 1 request/second sustained
- No API key required for basic usage (optional key for higher limits)
- Paper IDs: arXiv IDs work directly (e.g., `ArXiv:2401.12345`)

### OpenAlex (backup)

- Base URL: `https://api.openalex.org`
- Free, open API, no key required (polite pool with `mailto` param)
- Good for: citation counts, institution data, concept tagging
- Use as fallback when Semantic Scholar is rate-limited or down

## Architecture

### Data Flow

```
              ┌─────────────┐
              │  arXiv RSS   │  (daily, ~200 papers)
              └──────┬───────┘
                     │ parse
                     ▼
              ┌─────────────┐      ┌──────────────────┐
              │   Papers DB  │◄─────│ Semantic Scholar  │  (citation monitoring)
              └──────┬───────┘      └──────────────────┘
                     │ embed abstracts
                     ▼
              ┌─────────────────┐
              │ Similarity Match │◄── knowledge graph claim embeddings
              └──────┬──────────┘
                     │ score > threshold
                     ▼
              ┌─────────────┐
              │  LLM Triage  │  (explain relevance, assign priority)
              └──────┬───────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     ┌────────┐ ┌────────┐ ┌────────────┐
     │ Alerts │ │ Forum  │ │ Knowledge  │
     │ (API)  │ │ (post) │ │ Graph      │
     └────────┘ └────────┘ └────────────┘
```

### Where This Fits

```
daemon.ts (cycle)
  ├── scoreProjects()              -- existing
  ├── runSession()                 -- existing
  ├── evalManager.tick()           -- existing
  ├── experimentLoop.tick()        -- from closed-loop roadmap
  └── literatureMonitor.tick()     -- NEW: poll sources, match, alert
```

The literature monitor runs once per daemon cycle (currently every 60 minutes). ArXiv RSS is fetched at most twice per day (it only updates twice). Citation checks are spread across cycles to stay within rate limits.

## New Types

### `orchestrator/src/types/literature.ts`

```typescript
export interface Paper {
  id: string;                  // canonical ID (arXiv ID preferred, else S2 ID)
  s2Id?: string;               // Semantic Scholar corpus ID
  arxivId?: string;            // e.g. "2401.12345"
  title: string;
  authors: string[];
  abstract: string;
  categories: string[];        // arXiv categories
  published: string;           // ISO date
  url: string;                 // link to paper
  citationCount?: number;
  embedding?: number[];        // abstract embedding vector
  source: "arxiv" | "s2" | "openalex";
  fetchedAt: string;
}

export interface LitAlert {
  id: string;                  // UUID
  paper: Paper;
  relevanceScore: number;      // 0.0 - 1.0 (cosine similarity or LLM-assigned)
  matchedClaims: Array<{
    claimId: string;
    statement: string;
    relation: "supports" | "contradicts" | "extends" | "competes" | "related";
    explanation: string;       // LLM-generated: why this paper matters for this claim
  }>;
  priority: "high" | "medium" | "low";
  suggestedAction: string;     // e.g. "Read and assess impact on Claim #47"
  project: string;             // which research project this is relevant to
  status: "new" | "reviewed" | "dismissed" | "integrated";
  createdAt: string;
  reviewedAt?: string;
}

export interface CitationWatch {
  paperId: string;             // paper we are watching for new citations
  title: string;               // for display
  project: string;
  lastChecked: string;
  knownCitations: number;      // count at last check
}
```

## New Files

### `orchestrator/src/literature-monitor.ts`

The main class. Orchestrates polling, matching, and alerting.

```typescript
export class LiteratureMonitor {
  constructor(
    rootDir: string,
    logger: ActivityLogger,
    notifier: Notifier,
    dbPool: pg.Pool | null,
  ) {}

  /**
   * Called every daemon cycle. Runs the appropriate polling step
   * based on time-of-day and rate limit state.
   *
   * Cycle budget: ~30 Semantic Scholar API calls (to stay well under 100/5min).
   */
  async tick(): Promise<void>;

  /**
   * Fetch new papers from arXiv RSS for configured categories.
   * Deduplicates against papers already in DB.
   * Called at most twice per day (matching arXiv update schedule).
   */
  async pollArxiv(categories: string[]): Promise<Paper[]>;

  /**
   * Check for new citations of papers in our watch list.
   * Uses Semantic Scholar citations endpoint.
   * Processes a batch of watched papers per cycle (round-robin).
   */
  async pollCitations(batchSize?: number): Promise<LitAlert[]>;

  /**
   * Match new papers against knowledge graph claims using embedding similarity.
   * Papers above the relevance threshold are passed to LLM triage.
   */
  async matchAgainstClaims(papers: Paper[]): Promise<LitAlert[]>;

  /**
   * LLM-assisted triage: for each candidate match, generate an explanation
   * of relevance and assign priority.
   * Uses Sonnet 4 for cost efficiency (~$0.02 per paper triaged).
   */
  async triagePaper(
    paper: Paper,
    matchedClaims: Array<{ claimId: string; statement: string; similarity: number }>,
  ): Promise<LitAlert>;

  /**
   * Add a paper to the citation watch list.
   * Typically called when a paper is referenced in our work.
   */
  async watchPaper(paperId: string, title: string, project: string): Promise<void>;

  /**
   * Remove a paper from the citation watch list.
   */
  async unwatchPaper(paperId: string): Promise<void>;

  /**
   * Get all active alerts, optionally filtered by project or status.
   */
  listAlerts(filters?: {
    project?: string;
    status?: LitAlert["status"];
    priority?: LitAlert["priority"];
    since?: string;
  }): Promise<LitAlert[]>;

  /**
   * Mark an alert as reviewed or dismissed.
   */
  async updateAlertStatus(alertId: string, status: LitAlert["status"]): Promise<void>;

  /**
   * Get configuration: watched categories, thresholds, watch list.
   */
  getConfig(): LitMonitorConfig;
}

interface LitMonitorConfig {
  arxivCategories: string[];           // default: ["cs.AI", "cs.CL", "cs.LG", "cs.CC"]
  similarityThreshold: number;         // default: 0.80
  highPriorityThreshold: number;       // default: 0.90
  maxPapersPerCycle: number;           // default: 50
  maxAlertsPerDay: number;             // default: 20
  citationBatchSize: number;           // default: 10
  embeddingModel: string;              // default: "text-embedding-3-small"
}
```

### `orchestrator/src/arxiv-client.ts`

Minimal arXiv RSS client. No external dependencies -- uses Node.js built-in `fetch` and a simple XML parser.

```typescript
export class ArxivClient {
  /**
   * Fetch papers from arXiv RSS feed for a category.
   * Returns papers published since the given date.
   */
  async fetchCategory(category: string, since?: string): Promise<Paper[]>;

  /**
   * Fetch papers from multiple categories, deduplicate by arXiv ID.
   */
  async fetchCategories(categories: string[], since?: string): Promise<Paper[]>;

  /**
   * Parse arXiv RSS/Atom XML into Paper objects.
   * Handles both RSS 2.0 and Atom formats.
   */
  private parseRssFeed(xml: string, category: string): Paper[];
}
```

The RSS XML is simple enough to parse with regex or a minimal SAX approach. No need for a full XML library. Each `<item>` contains `<title>`, `<link>`, `<description>` (abstract), `<dc:creator>` (authors), and `<arxiv:primary_category>`.

### `orchestrator/src/s2-client.ts`

Semantic Scholar API client. Rate-limit aware with built-in backoff.

```typescript
export class SemanticScholarClient {
  private requestTimes: number[] = [];   // sliding window for rate limiting
  private readonly maxRequestsPer5Min = 90;  // stay under 100 limit

  /**
   * Search for papers by keyword query.
   */
  async search(query: string, limit?: number): Promise<Paper[]>;

  /**
   * Get paper details by ID (arXiv ID, DOI, or S2 corpus ID).
   */
  async getPaper(paperId: string): Promise<Paper | null>;

  /**
   * Get papers that cite a given paper.
   * Returns only citations not already known (new since lastChecked).
   */
  async getCitations(
    paperId: string,
    knownCount?: number,
  ): Promise<Array<{ paper: Paper; context?: string }>>;

  /**
   * Get recommended papers based on positive examples.
   * Useful for finding related work we might have missed.
   */
  async getRecommendations(
    positivePaperIds: string[],
    limit?: number,
  ): Promise<Paper[]>;

  /**
   * Rate-limit aware fetch. Waits if necessary to stay under limits.
   */
  private async rateLimitedFetch(url: string): Promise<Response>;
}
```

### `orchestrator/src/embedding-client.ts`

Thin wrapper for embedding API calls. Supports batch embedding for cost efficiency.

```typescript
export class EmbeddingClient {
  constructor(
    private model: string = "text-embedding-3-small",
    private apiKey?: string,  // defaults to OPENAI_API_KEY env var
  ) {}

  /**
   * Embed a single text string. Returns float32 vector.
   */
  async embed(text: string): Promise<number[]>;

  /**
   * Batch embed multiple texts. More cost-efficient than individual calls.
   * OpenAI supports up to 2048 texts per batch.
   */
  async embedBatch(texts: string[]): Promise<number[][]>;

  /**
   * Compute cosine similarity between two vectors.
   */
  static cosineSimilarity(a: number[], b: number[]): number;
}
```

Embedding costs with `text-embedding-3-small`:
- ~200 abstracts/day x ~300 tokens/abstract = ~60,000 tokens/day
- At $0.02/1M tokens = ~$0.0012/day = **~$0.04/month**

## Database Schema Additions

```sql
-- Papers discovered through literature monitoring
CREATE TABLE lit_papers (
    id              TEXT PRIMARY KEY,        -- arXiv ID or S2 corpus ID
    s2_id           TEXT,
    arxiv_id        TEXT,
    title           TEXT NOT NULL,
    authors         JSONB NOT NULL,          -- string array
    abstract        TEXT,
    categories      JSONB DEFAULT '[]',      -- string array
    published       DATE,
    url             TEXT,
    citation_count  INTEGER DEFAULT 0,
    embedding       vector(1536),            -- pgvector extension
    source          TEXT NOT NULL,            -- 'arxiv', 's2', 'openalex'
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lit_papers_arxiv ON lit_papers (arxiv_id);
CREATE INDEX idx_lit_papers_published ON lit_papers (published);

-- Requires pgvector extension for similarity search
-- CREATE EXTENSION IF NOT EXISTS vector;
-- CREATE INDEX idx_lit_papers_embedding ON lit_papers
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- Note: if pgvector is not available, similarity matching falls back to
-- application-level cosine similarity computed in TypeScript.

-- Literature alerts
CREATE TABLE lit_alerts (
    id              TEXT PRIMARY KEY,
    paper_id        TEXT NOT NULL REFERENCES lit_papers(id),
    relevance_score REAL NOT NULL,
    matched_claims  JSONB NOT NULL,          -- array of {claimId, statement, relation, explanation}
    priority        TEXT NOT NULL DEFAULT 'low',
    suggested_action TEXT,
    project         TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'new'
                    CHECK (status IN ('new', 'reviewed', 'dismissed', 'integrated')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ
);

CREATE INDEX idx_lit_alerts_project ON lit_alerts (project);
CREATE INDEX idx_lit_alerts_status ON lit_alerts (status);
CREATE INDEX idx_lit_alerts_priority ON lit_alerts (priority);
CREATE INDEX idx_lit_alerts_created ON lit_alerts (created_at);

-- Citation watch list
CREATE TABLE lit_citation_watches (
    paper_id        TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    project         TEXT NOT NULL,
    known_citations INTEGER NOT NULL DEFAULT 0,
    last_checked    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**pgvector note**: The VPS (Hetzner CPX21, Ubuntu 24.04, PostgreSQL 16) can install pgvector via `apt install postgresql-16-pgvector`. If pgvector is not available, the system falls back to computing cosine similarity in TypeScript -- slower but functional. The paper volume (~200/day) is small enough that brute-force similarity in JS is fine.

## Integration Details

### Integration with Daemon

The daemon gains one new call in its `cycle()` method:

```typescript
// In daemon.ts cycle(), after experimentLoop.tick():
try {
  await this.literatureMonitor.tick();
} catch (err) {
  console.error("Literature monitor tick error:", err);
}
```

The `tick()` method internally decides what to do based on state:
- If arXiv has not been polled today: fetch RSS feeds
- If there are new papers awaiting embedding: embed them
- If there are embedded papers awaiting matching: match against claims
- If there are matches awaiting triage: triage with LLM
- If it is time for citation checks: poll a batch of watched papers

This staged approach ensures each cycle stays within rate limits and completes quickly.

### Integration with Knowledge Graph

New papers create connections to existing claims:

- Embedding similarity identifies candidate matches (fast, cheap)
- LLM triage confirms the relationship and classifies it (supports/contradicts/extends/competes/related)
- Confirmed matches create `citation` type claims in the knowledge graph
- High-priority alerts (new paper contradicts or competes with our claims) trigger re-assessment

### Integration with Noor (Scout Agent)

The scout agent's heartbeat session reads recent alerts:

```
Noor's context injection (added to session prompt):
- "Since your last session, 3 new relevant papers were detected:"
  - [Paper title] — [relation] to [claim statement] — [explanation]
  - ...
- "2 new citations of our references were detected."
```

This transforms Noor from doing ad hoc web searches to processing structured, pre-triaged intelligence.

### Integration with Forum

High-priority alerts are auto-posted to the OpenClaw forum for collective discussion:

```typescript
// In literatureMonitor, after triaging a high-priority alert:
if (alert.priority === "high") {
  await forumClient.createThread({
    title: `[Lit Alert] ${alert.paper.title}`,
    body: `New paper detected that ${alert.matchedClaims[0].relation}s our claim:\n\n` +
          `**Claim**: ${alert.matchedClaims[0].statement}\n` +
          `**Paper**: ${alert.paper.title} (${alert.paper.url})\n` +
          `**Relevance**: ${(alert.relevanceScore * 100).toFixed(0)}%\n\n` +
          `**Analysis**: ${alert.matchedClaims[0].explanation}\n\n` +
          `**Suggested action**: ${alert.suggestedAction}`,
    author: "noor",
    tags: ["literature", alert.project],
  });
}
```

### Integration with API

New endpoints in `orchestrator/src/routes/literature.ts`:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/literature/alerts` | List alerts (filterable by project, status, priority, date range) |
| `GET` | `/api/literature/alerts/:id` | Get alert detail |
| `PATCH` | `/api/literature/alerts/:id` | Update alert status (reviewed/dismissed/integrated) |
| `GET` | `/api/literature/papers` | List discovered papers (filterable, paginated) |
| `GET` | `/api/literature/papers/:id` | Get paper detail with matched claims |
| `GET` | `/api/literature/watches` | List citation watch list |
| `POST` | `/api/literature/watches` | Add paper to watch list |
| `DELETE` | `/api/literature/watches/:id` | Remove paper from watch list |
| `GET` | `/api/literature/stats` | Monitoring stats (papers fetched, alerts generated, etc.) |

WebSocket channel: `literature` -- broadcasts new alerts in real-time.

### Integration with Notifier (Slack)

Notification triggers:
- **High-priority alert**: New paper contradicts or competes with our claims. Includes paper title, URL, relevance score, and the specific claim affected.
- **Concurrent work detected**: Paper with >0.90 similarity to our project's core claims. This is the most important alert -- it means someone else may be working on the same thing.
- **Citation milestone**: A paper we reference crosses a citation count threshold (e.g., 10, 50, 100 citations) -- indicates growing relevance of the area.
- **Daily digest**: Summary of papers found, alerts generated, citation changes. Sent once per day.

### Embedding Strategy

**Model**: `text-embedding-3-small` (1536 dimensions)
- Cheapest OpenAI embedding model at $0.02/1M tokens
- Sufficient quality for abstract-level similarity (we only need to identify candidates, LLM triage handles precision)

**What gets embedded**:
- All new paper abstracts (batch embedded once per arXiv poll)
- All active knowledge graph claims (embedded once, re-embedded when claim text changes)

**Matching logic**:
1. Compute cosine similarity between each new paper embedding and all active claim embeddings
2. Papers with max similarity >= 0.80 are candidates for triage
3. Papers with max similarity >= 0.90 are high-priority candidates
4. LLM triage filters false positives and classifies the relationship

**Storage**: Embeddings stored in PostgreSQL (pgvector if available, else JSONB with application-level similarity). At ~200 papers/day, the table grows by ~73,000 rows/year -- well within PostgreSQL's capabilities.

**Cost**: ~$0.04/month for embeddings. Negligible.

### Semantic Scholar Rate Limit Management

The free tier allows 100 requests per 5 minutes. Our strategy:

- **Per-cycle budget**: 30 requests max (leaves headroom for concurrent usage)
- **Citation checks**: 10 papers per cycle, 1 request each = 10 requests
- **Recommendation checks**: 5 requests per cycle (batched)
- **Paper detail lookups**: up to 15 per cycle (for newly discovered papers)
- **Backoff**: If a 429 is received, pause literature monitoring for the remainder of the cycle
- **Sliding window**: Track request timestamps in memory, wait if approaching limit

At one daemon cycle per hour, this gives us 720 Semantic Scholar requests per day -- enough to monitor citation changes for ~240 papers daily.

## Task Breakdown

| # | Task | Hours | Dependencies |
|---|------|-------|--------------|
| 1 | Define types in `orchestrator/src/types/literature.ts` | 1 | -- |
| 2 | Implement `ArxivClient` (RSS fetch, XML parse, dedup) | 2 | -- |
| 3 | Implement `SemanticScholarClient` (search, citations, recommendations, rate limiting) | 2-3 | -- |
| 4 | Implement `EmbeddingClient` (single + batch embed, cosine similarity) | 1-2 | -- |
| 5 | Implement `LiteratureMonitor` class (tick, pollArxiv, pollCitations, matchAgainstClaims, triagePaper) | 3-4 | 1, 2, 3, 4 |
| 6 | Add DB schema migration (lit_papers, lit_alerts, lit_citation_watches) | 1 | -- |
| 7 | Integrate `LiteratureMonitor.tick()` into `daemon.ts` cycle | 1 | 5 |
| 8 | Forum auto-posting for high-priority alerts | 1 | 5 |
| 9 | Noor context injection (add recent alerts to scout session prompt) | 1 | 5 |
| 10 | API routes (`/api/literature/*`) and WebSocket channel | 1-2 | 5, 6 |
| 11 | Slack notifications (high-priority alerts, daily digest) | 1 | 5 |
| 12 | Seed citation watch list with reasoning-gaps references | 1 | 3, 6 |
| **Total** | | **16-22** | |

Tasks 1, 2, 3, 4, and 6 can all run in parallel. Task 5 depends on all of them.

## Validation: Reasoning-Gaps Concurrent Work Detection

To validate the system works, seed it with the reasoning-gaps project:

1. **Watch list**: Add all papers cited in the reasoning-gaps bibliography (~30-40 papers). These include Wei et al. (2022) on CoT, Feng et al. (2024) on CoT limitations, Merrill & Sabharwal on expressiveness bounds, etc.

2. **Claim embeddings**: Embed the core claims from the paper:
   - "Chain-of-thought reasoning provides significant benefit only for tasks requiring serial depth or recursive structure"
   - "Intractable tasks show minimal CoT lift regardless of model scale"
   - "The theoretical upper bound on CoT benefit is determined by the task's complexity class relative to TC0"

3. **Run for one week**: Monitor arXiv cs.AI + cs.CL + cs.LG daily. Check citations of watched papers.

4. **Expected outcomes**:
   - 5-15 alerts per week (given active research in CoT reasoning)
   - At least 1 high-priority alert if concurrent work exists
   - Citation monitoring detects any new papers citing our key references
   - False positive rate below 20% (verified by human review of first week's alerts)

## Success Criteria

- Platform detects relevant new papers within 24 hours of arXiv posting.
- 80%+ of generated alerts are rated as genuinely relevant by human review.
- Concurrent work is detected before submission deadline (critical for novelty claims).
- Citation graph updates automatically when new papers cite our references.
- Total cost of literature monitoring stays under $1/month (embeddings + LLM triage).
- System operates within Semantic Scholar rate limits without failures.
- Noor's scout sessions are measurably more productive with pre-triaged intelligence.

## Open Questions

1. **pgvector on VPS**: Should we install pgvector now or use application-level similarity first?
   - **Recommendation**: Start with application-level cosine similarity in TypeScript. At ~200 papers/day the volume is trivially small. Add pgvector later if needed for full-text semantic search across thousands of papers.

2. **Embedding model choice**: `text-embedding-3-small` (cheap, good enough) vs `voyage-3` (better for academic text, slightly more expensive)?
   - **Recommendation**: Start with `text-embedding-3-small`. If precision is insufficient after the first week of validation, switch to `voyage-3`.

3. **Full-text access**: Should we download and parse full PDFs for deeper analysis, or is abstract-level matching sufficient?
   - **Recommendation**: Abstract-level matching for automated triage. Full-text analysis can be done by Noor during a scout session when a high-priority alert is generated. Parsing PDFs adds complexity and cost for marginal benefit at the triage stage.

4. **Multiple projects**: The literature monitor should serve all active projects, not just reasoning-gaps. How to handle project-specific relevance?
   - **Recommendation**: Each project registers its own claim embeddings and watch list. The monitor runs once per cycle across all projects, but alerts are tagged per project. This scales naturally as new projects are added.
