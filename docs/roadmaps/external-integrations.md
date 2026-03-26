# External Integrations Roadmap

**Status**: Proposed
**Date**: 2026-03-21

APIs and services that give the platform eyes on the research landscape, the community, and itself.

---

## Tier 1 — Foundational (unlocks autonomous research)

### Semantic Scholar API

**Why**: The scout agent and literature intelligence pipeline exist in code but have no data source. Semantic Scholar is the richest free academic API available — paper search, citation graphs, related papers, author disambiguation. Without it, the platform is blind to what's being published.

**API**: `https://api.semanticscholar.org/graph/v1`
**Auth**: API key (free, higher rate limits with key)
**Cost**: Free
**Rate limits**: 1 req/sec without key, 10 req/sec with key, 1000/5min for batch

**Integration points**:

1. **Scout agent** (`.claude/agents/scout.md`)
   - Daily search for papers matching active project topics
   - Feed results into `literature/digests/digest-YYYY-MM-DD.md`
   - Generate new research ideas from trending papers → append to `docs/ideas/backlog.yaml`

2. **Knowledge graph** (`orchestrator/src/knowledge-graph.ts`)
   - Store paper metadata as `citation` type nodes with embeddings
   - Link to existing claims via `cites` / `supports` / `contradicts` edges
   - Semantic search: find papers nearest to a claim embedding

3. **Scoop detection**
   - Query for papers matching each active project's key terms weekly
   - Compare new paper abstracts against project knowledge graph embeddings
   - Alert via Slack if similarity > 0.8 (potential scoop or highly relevant work)

4. **Citation tracking** (post-publication)
   - Monitor citations of our published papers
   - Track who's citing us, in what context
   - Feed into strategist agent for portfolio decisions

**Key endpoints**:
```
GET  /paper/search?query={q}&fields=title,abstract,year,citationCount,authors
GET  /paper/{paperId}?fields=title,abstract,citations,references,embedding
GET  /paper/{paperId}/citations
GET  /paper/{paperId}/references
POST /paper/batch (up to 500 IDs per request)
GET  /recommendations/v1/papers/forpaper/{paperId}
```

**Implementation sketch**:
```typescript
// orchestrator/src/semantic-scholar.ts
export class SemanticScholarClient {
  private apiKey: string;
  private baseUrl = "https://api.semanticscholar.org/graph/v1";

  async searchPapers(query: string, limit = 20): Promise<Paper[]>;
  async getPaper(id: string): Promise<PaperDetail>;
  async getCitations(id: string): Promise<Citation[]>;
  async getRecommendations(id: string): Promise<Paper[]>;
  async batchGetPapers(ids: string[]): Promise<PaperDetail[]>;
  async findRelated(embedding: number[], threshold?: number): Promise<Paper[]>;
}
```

**Env var**: `SEMANTIC_SCHOLAR_API_KEY`

---

### arXiv API

**Why**: Daily firehose of new papers in target categories. Semantic Scholar indexes arXiv papers but with a 1-2 day delay. Direct arXiv access gives us same-day awareness.

**API**: `http://export.arxiv.org/api/query` (Atom/XML)
**Auth**: None
**Cost**: Free
**Rate limits**: 1 req/3sec, be respectful

**Integration points**:

1. **Daily ingestion** — Fetch new papers in cs.CL, cs.AI, cs.LG, cs.CC
2. **Embedding** — Title + abstract embedded via text-embedding-3-small
3. **Matching** — Cosine similarity against knowledge graph nodes, threshold at 0.75
4. **Event emission** — High-relevance matches emit `literature.match` event
5. **Planner** — Decides whether to schedule a scout session to read and integrate

**Key queries**:
```
# New papers in cs.CL from last 24h
GET /api/query?search_query=cat:cs.CL&sortBy=submittedDate&sortOrder=descending&max_results=100

# Search for specific topic
GET /api/query?search_query=all:"reasoning+gaps"+AND+cat:cs.CL&max_results=50
```

**Implementation**: Add to `semantic-scholar.ts` or create `orchestrator/src/arxiv.ts`. Parse Atom XML, extract title/abstract/authors/categories, embed and match.

**Env var**: None needed

---

### Slack Workspace + Webhook

**Why**: The daemon runs 24/7 but you have zero visibility without SSH. The `Notifier` class (`orchestrator/src/notifier.ts`) already supports Slack webhooks — just needs the URL configured.

**Setup**:
1. Create Slack workspace (or use existing)
2. Create incoming webhook at `https://api.slack.com/messaging/webhooks`
3. Add `SLACK_WEBHOOK_URL` to VPS `.env`
4. Optionally create channels: `#daemon`, `#research`, `#alerts`

**What gets notified** (already coded in `Notifier`):
- Session completed (project, agent, commits, cost, quality score)
- Budget warnings (80% daily, 90% monthly)
- Daemon errors
- Eval job completion
- Phase transitions

**What to add**:
- Scoop alerts (from Semantic Scholar integration)
- Daily digest summary
- Paper build status (compile success/failure)
- Uptime alerts (from monitoring service)

**Cost**: Free (Slack free tier is sufficient for notifications)
**Env var**: `SLACK_WEBHOOK_URL`

---

## Tier 2 — Research quality & publication

### Hugging Face Hub API

**Why**: NeurIPS reviewers expect benchmarks and data to be accessible. A published HF dataset with a leaderboard is how benchmarks get adopted and cited. The ReasonGap suite is ready to publish.

**API**: `huggingface_hub` Python library or REST API
**Auth**: HF token
**Cost**: Free for public datasets/models

**What to publish**:

1. **ReasonGap Benchmark Suite** (`deepwork/reasoning-gaps-benchmark`)
   - 9 diagnostic tasks (B1–B9) as a HF dataset
   - Task generators for reproducibility
   - Dataset card with paper citation, usage examples, leaderboard
   - ~160K evaluation instances as downloadable splits

2. **Evaluation Results** (`deepwork/reasoning-gaps-results`)
   - Per-model, per-task, per-condition results
   - Raw model outputs (for analysis reproducibility)
   - Pre-computed analysis artifacts

3. **Future projects** — Each new benchmark/dataset gets its own HF repo

**Implementation sketch**:
```python
# projects/reasoning-gaps/publish_hf.py
from huggingface_hub import HfApi, DatasetCard

api = HfApi()
api.create_repo("deepwork/reasoning-gaps-benchmark", repo_type="dataset")
api.upload_folder(folder_path="benchmarks/tasks", repo_id="deepwork/reasoning-gaps-benchmark")
# Upload dataset card, splits, evaluation results
```

**Env var**: `HF_TOKEN`

---

### Zenodo API

**Why**: Permanent DOIs for datasets and code. Required by many venues for reproducibility. Reviewers trust DOI-backed data more than "available on request."

**API**: `https://zenodo.org/api/`
**Auth**: Personal access token
**Cost**: Free (up to 50GB per deposit)

**What to deposit**:
1. ReasonGap evaluation dataset (with DOI)
2. Analysis code archive (tagged to paper version)
3. Supplementary materials ZIP (mirrors NeurIPS submission)

**Integration**:
- Script to create deposit, upload files, publish
- DOI gets embedded in paper LaTeX (`\href{https://doi.org/10.5281/zenodo.XXXXX}{...}`)
- Versioned deposits: update when paper is revised

**Key endpoints**:
```
POST /api/deposit/depositions          # Create draft
PUT  /api/files/{bucket_id}/{filename} # Upload file
POST /api/deposit/depositions/{id}/actions/publish  # Mint DOI
```

**Env var**: `ZENODO_TOKEN`

---

### OpenReview API

**Why**: Real reviewer behavior data at target venues. Instead of guessing what NeurIPS reviewers care about, learn from actual reviews on related papers. Dramatically improves the review simulation system (§7.2).

**API**: `https://api2.openreview.net`
**Auth**: OpenReview account credentials
**Cost**: Free

**What to extract**:

1. **Reviewer comments on related papers**
   - Search for papers matching our topics at NeurIPS 2024/2025
   - Extract common objections, praise patterns, score distributions
   - Build a reviewer behavior model for simulation

2. **Acceptance/rejection patterns**
   - Which types of papers get accepted vs rejected?
   - What scores correlate with acceptance?
   - How do rebuttals affect outcomes?

3. **Venue-specific expectations**
   - NeurIPS vs ICLR vs ACL reviewer norms
   - Format expectations, page limits, checklist emphasis

**Key endpoints**:
```
GET /notes?content.venue=NeurIPS+2025&content.title=reasoning  # Search papers
GET /notes?forum={forumId}                                      # Get all reviews for a paper
GET /notes?invitation=NeurIPS.cc/2025/Conference/-/Official_Review  # All reviews
```

**Implementation**: Feed extracted review patterns into the review simulation agent. Store reviewer archetypes (detail-oriented, big-picture, methodology-focused) in the knowledge graph.

**Env var**: `OPENREVIEW_USERNAME`, `OPENREVIEW_PASSWORD`

---

## Tier 3 — Platform reliability

### Uptime Monitoring

**Why**: 11-hour VPS outage with zero alerting. The daemon could be down for days and nobody would know.

**Options** (all have free tiers):
- **UptimeRobot** — 50 monitors free, 5-min checks, email/SMS/Slack alerts
- **Betterstack (formerly Better Uptime)** — 10 monitors free, 3-min checks, incident pages
- **Cronitor** — Also handles cron job monitoring (useful for daemon heartbeat)

**Setup**:
1. Create HTTP monitor pointing at `http://89.167.5.50/api/health` (or HTTPS once SSL is set up)
2. Configure alert channels: email + Slack webhook
3. Set alert threshold: 2 consecutive failures (to avoid false positives)
4. Optionally monitor the daemon heartbeat file (`.deepwork.heartbeat`) via a cron check

**Cost**: Free tier sufficient

---

### Error Tracking (Sentry)

**Why**: The daemon silently swallows errors to journalctl. Ghost project FK errors, planner 503s, knowledge maintenance failures — all buried in logs nobody reads. Sentry gives structured error tracking with deduplication, stack traces, and alerts.

**Setup**:
1. Create Sentry project (Node.js / TypeScript)
2. `npm install @sentry/node` in orchestrator
3. Initialize in `orchestrator/src/index.ts`
4. Sentry auto-captures unhandled exceptions + rejections
5. Add manual `Sentry.captureException()` in key catch blocks (daemon cycle, knowledge maintenance, session runner)

**What it catches**:
- Daemon cycle errors (currently logged and ignored)
- Knowledge graph FK violations (ghost projects)
- Session runner failures (timeout, budget exceeded, SDK errors)
- API route errors (planner 503, etc.)
- Unhandled promise rejections

**Cost**: Free tier (5K errors/month, 1 user) is more than enough

**Env var**: `SENTRY_DSN`

---

## Implementation Priority

| Integration | Priority | Effort | Depends on | Unlocks |
|---|---|---|---|---|
| Slack webhook | Do first | 30 min | Slack workspace | Visibility into everything |
| Uptime monitoring | Do first | 15 min | Public endpoint | Outage alerting |
| Semantic Scholar | High | 4–6 hours | API key | Literature intelligence, scoop detection |
| arXiv API | High | 2–3 hours | Nothing | Daily paper feeds |
| Sentry | Medium | 1–2 hours | Sentry account | Error visibility |
| Hugging Face Hub | Medium | 3–4 hours | HF account | Benchmark publication (NeurIPS reviewers expect this) |
| Zenodo | Medium | 2–3 hours | Zenodo account | Dataset DOIs for paper |
| OpenReview | Lower | 4–6 hours | Account | Review simulation training data |

**Recommended order**: Slack → Uptime → Semantic Scholar + arXiv → Sentry → HF Hub + Zenodo (before NeurIPS submission) → OpenReview

---

## Env Vars Summary

Add to VPS `.env`:
```bash
# Tier 1
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
SEMANTIC_SCHOLAR_API_KEY=...

# Tier 2
HF_TOKEN=hf_...
ZENODO_TOKEN=...
OPENREVIEW_USERNAME=...
OPENREVIEW_PASSWORD=...

# Tier 3
SENTRY_DSN=https://...@sentry.io/...
```
