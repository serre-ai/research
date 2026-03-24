/**
 * LiteratureMonitor — full literature intelligence system.
 *
 * DB-backed paper storage, embedding-based semantic matching,
 * LLM triage, and citation watch list. Replaces the lightweight
 * LiteratureScanner (Level 1) with a persistent pipeline.
 *
 * Processing stages per tick:
 *   1. Poll — fetch new papers from arXiv + S2
 *   2. Embed — generate embeddings for new paper abstracts
 *   3. Match — cosine similarity against project claims
 *   4. Triage — LLM-assisted relevance classification
 *   5. Alert — create alerts and notify on threats
 */

import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import pg from "pg";
import type { ArxivClient, ArxivPaper } from "./arxiv.js";
import type { SemanticScholarClient, S2Paper } from "./semantic-scholar.js";
import type { ActivityLogger } from "./logger.js";
import type { Notifier } from "./notifier.js";
import type { EventBus } from "./event-bus.js";
import type { EmbedFn } from "./embeddings.js";
import type { KnowledgeGraph, ClaimRow } from "./knowledge-graph.js";

// ============================================================
// Topic taxonomy types
// ============================================================

interface TopicEntry {
  name: string;
  display: string;
  keywords: string[];
}

interface TopicTaxonomy {
  topics: TopicEntry[];
}

// ============================================================
// Types
// ============================================================

export interface LitPaper {
  id: string;
  arxivId: string | null;
  s2Id: string | null;
  doi: string | null;
  title: string;
  abstract: string | null;
  authors: string[];
  venue: string | null;
  year: number | null;
  publishedAt: string | null;
  categories: string[];
  citationCount: number;
  url: string | null;
  pdfUrl: string | null;
  source: "arxiv" | "s2" | "manual";
  discoveredAt: string;
}

export interface LitAlert {
  id: number;
  paperId: string;
  project: string;
  priority: "low" | "medium" | "high" | "critical";
  relation: "competes" | "supports" | "extends" | "contradicts" | "related";
  similarity: number | null;
  matchedClaim: string | null;
  matchedTerms: string[];
  explanation: string | null;
  triageModel: string | null;
  acknowledged: boolean;
  createdAt: string;
  paper?: LitPaper;
}

export interface CitationWatch {
  id: number;
  paperId: string | null;
  arxivId: string | null;
  s2Id: string | null;
  title: string;
  project: string;
  reason: string | null;
  lastChecked: string | null;
  lastCitationCount: number;
  active: boolean;
  createdAt: string;
}

export interface MonitorStats {
  totalPapers: number;
  totalAlerts: number;
  unacknowledgedAlerts: number;
  activeWatches: number;
  lastScanAt: string | null;
}

interface ProjectTerms {
  project: string;
  keyTerms: string[];
}

// ============================================================
// Monitor
// ============================================================

const ARXIV_CATEGORIES = ["cs.CL", "cs.AI", "cs.LG", "cs.CC"];
const MATCH_SIMILARITY_THRESHOLD = 0.75;
const THREAT_SIMILARITY_THRESHOLD = 0.85;

export class LiteratureMonitor {
  private lastTickAt = 0;
  private taxonomyCache: TopicEntry[] | null = null;

  constructor(
    private pool: pg.Pool,
    private s2: SemanticScholarClient,
    private arxiv: ArxivClient,
    private embedFn: EmbedFn | null,
    private kg: KnowledgeGraph | null,
    private logger: ActivityLogger,
    private notifier: Notifier,
    private eventBus: EventBus | null,
  ) {}

  // ============================================================
  // Topic taxonomy
  // ============================================================

  /** Load topic taxonomy from shared/config/research-topics.yaml. Cached in memory. */
  private loadTopicTaxonomy(): TopicEntry[] {
    if (this.taxonomyCache) return this.taxonomyCache;

    try {
      // Resolve path relative to this file: ../../shared/config/research-topics.yaml
      const thisDir = dirname(fileURLToPath(import.meta.url));
      const yamlPath = join(thisDir, "..", "..", "shared", "config", "research-topics.yaml");
      const raw = readFileSync(yamlPath, "utf-8");

      // Lightweight YAML parse — the file is a simple list structure.
      // We avoid a full YAML dependency by parsing the known structure.
      const topics: TopicEntry[] = [];
      let current: Partial<TopicEntry> | null = null;

      for (const line of raw.split("\n")) {
        const trimmed = line.trim();
        if (trimmed.startsWith("#") || trimmed === "") continue;

        const nameMatch = trimmed.match(/^- name:\s*(.+)/);
        if (nameMatch) {
          if (current?.name) topics.push(current as TopicEntry);
          current = { name: nameMatch[1].trim(), display: "", keywords: [] };
          continue;
        }

        if (current) {
          const displayMatch = trimmed.match(/^display:\s*"?([^"]*)"?/);
          if (displayMatch) {
            current.display = displayMatch[1];
            continue;
          }

          const kwMatch = trimmed.match(/^- "([^"]+)"/);
          if (kwMatch && current.keywords) {
            current.keywords.push(kwMatch[1]);
          }
        }
      }
      if (current?.name) topics.push(current as TopicEntry);

      this.taxonomyCache = topics;
      console.log(`[LitMonitor] Loaded ${topics.length} topic categories with ${topics.reduce((s, t) => s + t.keywords.length, 0)} keywords`);
      return topics;
    } catch (err) {
      console.error("[LitMonitor] Failed to load topic taxonomy:", err);
      return [];
    }
  }

  /** Classify a paper against the topic taxonomy. Returns topic names where 2+ keywords match. */
  private classifyTopics(title: string, abstract: string | null): string[] {
    const topics = this.loadTopicTaxonomy();
    const text = (title + " " + (abstract ?? "")).toLowerCase();

    const matched: string[] = [];
    for (const topic of topics) {
      const matchCount = topic.keywords.filter(kw => {
        // Use word-boundary regex for single-word keywords, includes for multi-word
        if (kw.includes(" ") || kw.includes("-")) {
          return text.includes(kw.toLowerCase());
        }
        const regex = new RegExp(`\\b${kw.toLowerCase()}\\b`);
        return regex.test(text);
      }).length;
      if (matchCount >= 2) {
        matched.push(topic.name);
      }
    }
    return matched;
  }

  /** Update a paper's topics in the database. */
  private async updatePaperTopics(paper: LitPaper): Promise<void> {
    const topics = this.classifyTopics(paper.title, paper.abstract);
    if (topics.length > 0) {
      await this.pool.query(
        "UPDATE lit_papers SET topics = $1 WHERE id = $2",
        [topics, paper.id],
      );
    }
  }

  /**
   * Get a representative set of search terms from the taxonomy for broad filtering.
   * Rotates keyword selection based on day of year so different terms are searched each day.
   */
  private getTopLevelSearchTerms(): string[] {
    const topics = this.loadTopicTaxonomy();
    const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));

    const terms: string[] = [];
    for (const topic of topics) {
      if (topic.keywords.length === 0) continue;
      const idx = dayOfYear % topic.keywords.length;
      terms.push(topic.keywords[idx]);
    }
    return terms;
  }

  /**
   * Backfill topics for papers that have null topics.
   * Processes up to 100 papers per call. Called once per tick.
   */
  private async backfillTopics(): Promise<void> {
    const { rows } = await this.pool.query(
      `SELECT id, title, abstract FROM lit_papers
       WHERE topics IS NULL
       ORDER BY discovered_at DESC
       LIMIT 100`,
    );

    if (rows.length === 0) return;

    let classified = 0;
    for (const row of rows) {
      const topics = this.classifyTopics(row.title as string, row.abstract as string | null);
      if (topics.length > 0) {
        await this.pool.query(
          "UPDATE lit_papers SET topics = $1 WHERE id = $2",
          [topics, row.id],
        );
        classified++;
      } else {
        // Set empty array so we don't reprocess
        await this.pool.query(
          "UPDATE lit_papers SET topics = '{}' WHERE id = $1",
          [row.id],
        );
      }
    }

    if (classified > 0) {
      console.log(`[LitMonitor] Backfill: classified ${classified}/${rows.length} papers`);
    }
  }

  // ============================================================
  // Main entry point — called from daemon cycle
  // ============================================================

  /**
   * Run one tick of the literature monitor pipeline.
   * Gated to once per 24h internally.
   */
  async tick(projects: ProjectTerms[]): Promise<void> {
    const hoursSinceLast = (Date.now() - this.lastTickAt) / (1000 * 60 * 60);
    if (this.lastTickAt > 0 && hoursSinceLast < 24) return;
    this.lastTickAt = Date.now();

    console.log("[LitMonitor] Starting daily literature scan");

    for (const project of projects) {
      if (!project.keyTerms.length) continue;
      try {
        // Stage 1: Poll
        const newPapers = await this.pollForProject(project);
        console.log(`[LitMonitor] ${project.project}: ${newPapers.length} new papers`);

        // Stage 2: Embed new papers
        if (this.embedFn && newPapers.length > 0) {
          await this.embedPapers(newPapers);
        }

        // Stage 3: Match against claims
        const matches = await this.matchAgainstClaims(project.project, newPapers);

        // Stage 4: Keyword-based matching (fallback when no embeddings)
        const keywordMatches = this.keywordMatch(newPapers, project.keyTerms);

        // Stage 5: Create alerts
        const allMatches = this.mergeMatches(matches, keywordMatches);
        if (allMatches.length > 0) {
          await this.createAlerts(project.project, allMatches);
        }

        // Log results
        await this.logger.log({
          type: "session_end",
          project: project.project,
          data: {
            source: "literature_monitor",
            newPapers: newPapers.length,
            alerts: allMatches.length,
          },
        });

        if (this.eventBus) {
          await this.eventBus.emit("literature.scan_completed", {
            project: project.project,
            newPapers: newPapers.length,
            alerts: allMatches.length,
          }).catch(() => {});
        }
      } catch (err) {
        console.error(`[LitMonitor] Error processing ${project.project}:`, err);
      }
    }

    // Backfill topics for papers missing classification
    try {
      await this.backfillTopics();
    } catch (err) {
      console.error("[LitMonitor] Topic backfill error:", err);
    }

    // Broad topic-based search (independent of any project)
    try {
      await this.broadTopicScan();
    } catch (err) {
      console.error("[LitMonitor] Broad topic scan error:", err);
    }

    // Check citation watches across all projects
    try {
      await this.pollCitations();
    } catch (err) {
      console.error("[LitMonitor] Citation poll error:", err);
    }
  }

  // ============================================================
  // Stage 1: Poll
  // ============================================================

  private async pollForProject(project: ProjectTerms): Promise<LitPaper[]> {
    const newPapers: LitPaper[] = [];

    // arXiv keyword searches
    for (const term of project.keyTerms.slice(0, 4)) {
      try {
        const catQuery = ARXIV_CATEGORIES.map((c) => `cat:${c}`).join(" OR ");
        const query = `all:"${term}" AND (${catQuery})`;
        const papers = await this.arxiv.search(query, {
          maxResults: 15,
          sortBy: "submittedDate",
          sortOrder: "descending",
        });

        for (const paper of papers) {
          const stored = await this.upsertArxivPaper(paper);
          if (stored) newPapers.push(stored);
        }
      } catch (err) {
        console.error(`[LitMonitor] arXiv query failed for "${term}":`, err);
      }
    }

    // S2 keyword searches
    for (const term of project.keyTerms.slice(0, 4)) {
      try {
        const papers = await this.s2.search(term, {
          limit: 15,
          year: "2025-",
          fieldsOfStudy: "Computer Science",
        });

        for (const paper of papers) {
          const stored = await this.upsertS2Paper(paper);
          if (stored) newPapers.push(stored);
        }
      } catch (err) {
        console.error(`[LitMonitor] S2 query failed for "${term}":`, err);
      }
    }

    // Recent papers from core categories
    try {
      const recent = await this.arxiv.recent(["cs.CL", "cs.AI"], 30);
      for (const paper of recent) {
        const stored = await this.upsertArxivPaper(paper);
        if (stored) newPapers.push(stored);
      }
    } catch (err) {
      console.error("[LitMonitor] arXiv recent fetch failed:", err);
    }

    return newPapers;
  }

  /** Broad topic-based search — stores papers matching 2+ topic keywords regardless of project. */
  private async broadTopicScan(): Promise<void> {
    const taxonomyTerms = this.getTopLevelSearchTerms();
    if (taxonomyTerms.length === 0) return;

    const currentYear = new Date().getFullYear();
    const yearFilter = `${currentYear - 1}-`;
    let totalStored = 0;

    // Limit to top 5 terms per tick to stay lightweight
    for (const term of taxonomyTerms.slice(0, 5)) {
      try {
        // Search S2 with this term (limit 10 papers per search)
        const papers = await this.s2.search(term, {
          limit: 10,
          year: yearFilter,
          fieldsOfStudy: "Computer Science",
        });

        for (const paper of papers) {
          // Only store if the paper matches 2+ topic keywords
          const topics = this.classifyTopics(paper.title, paper.abstract ?? "");
          if (topics.length === 0) continue;

          const stored = await this.upsertS2Paper(paper);
          if (stored) {
            await this.updatePaperTopics(stored);
            totalStored++;
          }
        }
      } catch (err) {
        console.error(`[LitMonitor] Broad topic search failed for "${term}":`, err);
      }

      try {
        // Also search arXiv
        const catQuery = ARXIV_CATEGORIES.map((c) => `cat:${c}`).join(" OR ");
        const query = `all:"${term}" AND (${catQuery})`;
        const arxivPapers = await this.arxiv.search(query, {
          maxResults: 10,
          sortBy: "submittedDate",
          sortOrder: "descending",
        });

        for (const paper of arxivPapers) {
          const topics = this.classifyTopics(paper.title, paper.abstract ?? "");
          if (topics.length === 0) continue;

          const stored = await this.upsertArxivPaper(paper);
          if (stored) {
            await this.updatePaperTopics(stored);
            totalStored++;
          }
        }
      } catch (err) {
        console.error(`[LitMonitor] Broad arXiv search failed for "${term}":`, err);
      }
    }

    if (totalStored > 0) {
      console.log(`[LitMonitor] Broad topic scan: stored ${totalStored} new papers`);
    }
  }

  /** Insert arXiv paper if not already in DB. Returns the paper if newly inserted, null if existing. */
  private async upsertArxivPaper(paper: ArxivPaper): Promise<LitPaper | null> {
    const { rows } = await this.pool.query(
      "SELECT id FROM lit_papers WHERE arxiv_id = $1",
      [paper.id],
    );
    if (rows.length > 0) return null;

    const id = `arx_${paper.id.replace(/[./]/g, "_")}`;
    await this.pool.query(
      `INSERT INTO lit_papers (id, arxiv_id, title, abstract, authors, year, published_at, categories, url, pdf_url, source)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'arxiv')
       ON CONFLICT DO NOTHING`,
      [
        id,
        paper.id,
        paper.title,
        paper.abstract,
        JSON.stringify(paper.authors),
        paper.published ? new Date(paper.published).getFullYear() : null,
        paper.published || null,
        JSON.stringify(paper.categories),
        `https://arxiv.org/abs/${paper.id}`,
        paper.pdfUrl,
      ],
    );

    // Classify topics on newly inserted paper
    const topics = this.classifyTopics(paper.title, paper.abstract);
    if (topics.length > 0) {
      await this.pool.query(
        "UPDATE lit_papers SET topics = $1 WHERE id = $2",
        [topics, id],
      );
    }

    return {
      id,
      arxivId: paper.id,
      s2Id: null,
      doi: paper.doi,
      title: paper.title,
      abstract: paper.abstract,
      authors: paper.authors,
      venue: null,
      year: paper.published ? new Date(paper.published).getFullYear() : null,
      publishedAt: paper.published,
      categories: paper.categories,
      citationCount: 0,
      url: `https://arxiv.org/abs/${paper.id}`,
      pdfUrl: paper.pdfUrl,
      source: "arxiv",
      discoveredAt: new Date().toISOString(),
    };
  }

  /** Insert S2 paper if not already in DB. Returns the paper if newly inserted, null if existing. */
  private async upsertS2Paper(paper: S2Paper): Promise<LitPaper | null> {
    const { rows } = await this.pool.query(
      "SELECT id FROM lit_papers WHERE s2_id = $1",
      [paper.paperId],
    );
    if (rows.length > 0) return null;

    const id = `s2_${paper.paperId.slice(0, 40)}`;
    const arxivId = paper.externalIds?.ArXiv ?? null;

    // Check if we already have this paper via arXiv ID
    if (arxivId) {
      const { rows: existing } = await this.pool.query(
        "SELECT id FROM lit_papers WHERE arxiv_id = $1",
        [arxivId],
      );
      if (existing.length > 0) {
        // Update with S2 ID
        await this.pool.query(
          "UPDATE lit_papers SET s2_id = $1, citation_count = $2 WHERE arxiv_id = $3",
          [paper.paperId, paper.citationCount, arxivId],
        );
        return null;
      }
    }

    await this.pool.query(
      `INSERT INTO lit_papers (id, s2_id, arxiv_id, doi, title, abstract, authors, venue, year, published_at, categories, citation_count, url, source)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 's2')
       ON CONFLICT DO NOTHING`,
      [
        id,
        paper.paperId,
        arxivId,
        paper.externalIds?.DOI ?? null,
        paper.title,
        paper.abstract,
        JSON.stringify(paper.authors.map((a) => a.name)),
        paper.venue,
        paper.year,
        paper.publicationDate,
        JSON.stringify(paper.fieldsOfStudy ?? []),
        paper.citationCount,
        paper.url,
      ],
    );

    // Classify topics on newly inserted paper
    const topics = this.classifyTopics(paper.title, paper.abstract ?? "");
    if (topics.length > 0) {
      await this.pool.query(
        "UPDATE lit_papers SET topics = $1 WHERE id = $2",
        [topics, id],
      );
    }

    return {
      id,
      arxivId,
      s2Id: paper.paperId,
      doi: paper.externalIds?.DOI ?? null,
      title: paper.title,
      abstract: paper.abstract,
      authors: paper.authors.map((a) => a.name),
      venue: paper.venue,
      year: paper.year,
      publishedAt: paper.publicationDate,
      categories: paper.fieldsOfStudy ?? [],
      citationCount: paper.citationCount,
      url: paper.url,
      pdfUrl: null,
      source: "s2",
      discoveredAt: new Date().toISOString(),
    };
  }

  // ============================================================
  // Stage 2: Embed
  // ============================================================

  private async embedPapers(papers: LitPaper[]): Promise<void> {
    if (!this.embedFn) return;

    for (const paper of papers) {
      if (!paper.abstract) continue;
      try {
        const text = `${paper.title}. ${paper.abstract}`;
        const embedding = await this.embedFn(text);
        const vecStr = `[${embedding.join(",")}]`;
        await this.pool.query(
          "UPDATE lit_papers SET embedding = $1 WHERE id = $2",
          [vecStr, paper.id],
        );
      } catch (err) {
        console.error(`[LitMonitor] Embedding failed for ${paper.id}:`, err);
      }
    }
  }

  // ============================================================
  // Stage 3: Match against claims
  // ============================================================

  private async matchAgainstClaims(
    project: string,
    papers: LitPaper[],
  ): Promise<Array<{ paper: LitPaper; similarity: number; claimStatement: string }>> {
    if (!this.kg || !this.embedFn) return [];

    const matches: Array<{ paper: LitPaper; similarity: number; claimStatement: string }> = [];

    // Get embedded papers
    const { rows: embeddedPapers } = await this.pool.query(
      `SELECT id, embedding FROM lit_papers
       WHERE id = ANY($1) AND embedding IS NOT NULL`,
      [papers.map((p) => p.id)],
    );

    if (embeddedPapers.length === 0) return matches;

    // Get project claims with embeddings
    const { rows: claims } = await this.pool.query(
      `SELECT id, statement, embedding FROM claims
       WHERE project = $1 AND embedding IS NOT NULL
       LIMIT 100`,
      [project],
    );

    if (claims.length === 0) return matches;

    // Compute similarities
    for (const ep of embeddedPapers) {
      const paper = papers.find((p) => p.id === ep.id);
      if (!paper) continue;

      for (const claim of claims) {
        try {
          const { rows: simRows } = await this.pool.query(
            `SELECT 1 - ($1::vector <=> $2::vector) AS similarity`,
            [ep.embedding, claim.embedding],
          );
          const similarity = parseFloat(simRows[0]?.similarity ?? "0");

          if (similarity >= MATCH_SIMILARITY_THRESHOLD) {
            matches.push({
              paper,
              similarity,
              claimStatement: claim.statement as string,
            });
            break; // One match per paper is enough
          }
        } catch {
          // pgvector query failed — skip
        }
      }
    }

    return matches;
  }

  // ============================================================
  // Stage 4: Keyword matching (fallback)
  // ============================================================

  private keywordMatch(
    papers: LitPaper[],
    terms: string[],
  ): Array<{ paper: LitPaper; matchedTerms: string[]; score: number }> {
    const matches: Array<{ paper: LitPaper; matchedTerms: string[]; score: number }> = [];

    for (const paper of papers) {
      const text = `${paper.title} ${paper.abstract ?? ""}`.toLowerCase();
      const matched = terms.filter((t) => text.includes(t.toLowerCase()));

      if (matched.length >= 2) {
        matches.push({
          paper,
          matchedTerms: matched,
          score: matched.length / terms.length,
        });
      }
    }

    return matches;
  }

  // ============================================================
  // Merge matches from both methods
  // ============================================================

  private mergeMatches(
    embeddingMatches: Array<{ paper: LitPaper; similarity: number; claimStatement: string }>,
    keywordMatches: Array<{ paper: LitPaper; matchedTerms: string[]; score: number }>,
  ): Array<{
    paper: LitPaper;
    similarity: number | null;
    matchedClaim: string | null;
    matchedTerms: string[];
    priority: LitAlert["priority"];
    relation: LitAlert["relation"];
  }> {
    const seen = new Set<string>();
    const results: Array<{
      paper: LitPaper;
      similarity: number | null;
      matchedClaim: string | null;
      matchedTerms: string[];
      priority: LitAlert["priority"];
      relation: LitAlert["relation"];
    }> = [];

    // Embedding matches (higher quality)
    for (const m of embeddingMatches) {
      seen.add(m.paper.id);
      results.push({
        paper: m.paper,
        similarity: m.similarity,
        matchedClaim: m.claimStatement,
        matchedTerms: [],
        priority: m.similarity >= THREAT_SIMILARITY_THRESHOLD ? "high" : "medium",
        relation: m.similarity >= THREAT_SIMILARITY_THRESHOLD ? "competes" : "related",
      });
    }

    // Keyword matches (only add if not already from embeddings)
    for (const m of keywordMatches) {
      if (seen.has(m.paper.id)) continue;
      results.push({
        paper: m.paper,
        similarity: null,
        matchedClaim: null,
        matchedTerms: m.matchedTerms,
        priority: m.score >= 0.5 ? "medium" : "low",
        relation: "related",
      });
    }

    return results;
  }

  // ============================================================
  // Stage 5: Create alerts
  // ============================================================

  private async createAlerts(
    project: string,
    matches: Array<{
      paper: LitPaper;
      similarity: number | null;
      matchedClaim: string | null;
      matchedTerms: string[];
      priority: LitAlert["priority"];
      relation: LitAlert["relation"];
    }>,
  ): Promise<void> {
    for (const match of matches) {
      // Check if alert already exists for this paper+project
      const { rows: existing } = await this.pool.query(
        "SELECT id FROM lit_alerts WHERE paper_id = $1 AND project = $2",
        [match.paper.id, project],
      );
      if (existing.length > 0) continue;

      await this.pool.query(
        `INSERT INTO lit_alerts (paper_id, project, priority, relation, similarity, matched_claim, matched_terms)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [
          match.paper.id,
          project,
          match.priority,
          match.relation,
          match.similarity,
          match.matchedClaim,
          match.matchedTerms,
        ],
      );

      // Store in knowledge graph as citation claim
      if (this.kg) {
        try {
          const authorStr = match.paper.authors.slice(0, 3).join(", ");
          const yearStr = match.paper.year ? ` (${match.paper.year})` : "";
          await this.kg.addClaim({
            project,
            claimType: "citation",
            statement: `${authorStr}${yearStr}: "${match.paper.title}" — ${match.relation} to project claims`,
            confidence: match.similarity ?? 0.5,
            source: match.paper.url ?? match.paper.id,
            sourceType: "paper",
            metadata: {
              paperId: match.paper.id,
              arxivId: match.paper.arxivId,
              relation: match.relation,
              priority: match.priority,
            },
          });

          // Add relation if we have a matched claim
          if (match.matchedClaim) {
            const relationType = match.relation === "competes" ? "contradicts"
              : match.relation === "supports" ? "supports"
              : match.relation === "extends" ? "refines"
              : "related_to";

            // Find the claim ID for the matched claim text
            const { rows: claimRows } = await this.pool.query(
              `SELECT id FROM claims WHERE project = $1 AND statement = $2 LIMIT 1`,
              [project, match.matchedClaim],
            );

            if (claimRows.length > 0) {
              // Find the citation claim we just inserted
              const { rows: citRows } = await this.pool.query(
                `SELECT id FROM claims WHERE project = $1 AND source = $2 ORDER BY created_at DESC LIMIT 1`,
                [project, match.paper.url ?? match.paper.id],
              );

              if (citRows.length > 0) {
                await this.kg.addRelation({
                  sourceId: citRows[0].id as string,
                  targetId: claimRows[0].id as string,
                  relation: relationType as "contradicts" | "supports" | "refines" | "related_to",
                  strength: match.similarity ?? 0.5,
                  evidence: `Literature monitor: paper "${match.paper.title}" ${match.relation} claim`,
                });
              }
            }
          }
        } catch (err) {
          console.error(`[LitMonitor] KG integration failed for ${match.paper.id}:`, err);
        }
      }

      // Notify on high/critical alerts
      if (match.priority === "high" || match.priority === "critical") {
        await this.notifier.notify({
          event: "Literature Threat",
          project,
          summary: `${match.relation}: "${match.paper.title}" by ${match.paper.authors[0] ?? "?"} et al. (sim=${match.similarity?.toFixed(2) ?? "keyword"})`,
          level: match.priority === "critical" ? "error" : "warning",
        });

        if (this.eventBus) {
          await this.eventBus.emit("literature.threat_detected", {
            project,
            paperId: match.paper.id,
            title: match.paper.title,
            priority: match.priority,
            relation: match.relation,
            similarity: match.similarity,
          }).catch(() => {});
        }
      }
    }
  }

  // ============================================================
  // Citation velocity
  // ============================================================

  /**
   * Compute citation velocity for papers from the last 6 months.
   * Designed to run weekly — compares current S2 citation count
   * against stored count and computes monthly rate.
   */
  async computeCitationVelocity(): Promise<void> {
    const { rows } = await this.pool.query(
      `SELECT id, s2_id, citation_count, analyzed_at FROM lit_papers
       WHERE discovered_at > NOW() - INTERVAL '6 months'
         AND s2_id IS NOT NULL`,
    );

    if (rows.length === 0) {
      console.log("[LitMonitor] No papers with S2 IDs for velocity computation");
      return;
    }

    // Batch query S2 for updated citation counts (batches of 500)
    const s2Ids = rows.map((r: Record<string, unknown>) => r.s2_id as string).filter(Boolean);
    let updated: Array<{ paperId: string; citationCount: number }> = [];

    for (let i = 0; i < s2Ids.length; i += 500) {
      const batch = s2Ids.slice(i, i + 500);
      try {
        const batchResults = await this.s2.batchGetPapers(batch);
        updated = updated.concat(batchResults);
      } catch (err) {
        console.error(`[LitMonitor] Batch velocity fetch failed (batch ${i / 500}):`, err);
      }
    }

    let velocityUpdates = 0;
    const now = new Date();
    for (const paper of updated) {
      if (!paper) continue;
      const row = rows.find((r: Record<string, unknown>) => r.s2_id === paper.paperId);
      if (!row) continue;

      const prevCount = (row.citation_count as number) ?? 0;
      const newCount = paper.citationCount ?? 0;
      const delta = newCount - prevCount;

      // Compute monthly rate normalized by days since last check
      let velocity = 0;
      const lastAnalyzed = row.analyzed_at ? new Date(row.analyzed_at as string) : null;
      if (lastAnalyzed && delta > 0) {
        const daysSinceCheck = Math.max(1, (now.getTime() - lastAnalyzed.getTime()) / (1000 * 60 * 60 * 24));
        velocity = (delta / daysSinceCheck) * 30; // monthly rate
      } else if (delta > 0) {
        velocity = delta; // no previous check — raw delta as fallback
      }

      if (delta !== 0 || velocity !== 0) {
        await this.pool.query(
          "UPDATE lit_papers SET citation_count = $1, citation_velocity = $2, analyzed_at = NOW() WHERE id = $3",
          [newCount, velocity, row.id],
        );
        velocityUpdates++;
      }
    }

    console.log(`[LitMonitor] Citation velocity: updated ${velocityUpdates}/${rows.length} papers`);
  }

  // ============================================================
  // Citation watch
  // ============================================================

  /** Check watched papers for new citations. */
  async pollCitations(): Promise<void> {
    const { rows: watches } = await this.pool.query(
      `SELECT id, arxiv_id, s2_id, title, project, last_citation_count
       FROM lit_citation_watches
       WHERE active = TRUE
       ORDER BY last_checked ASC NULLS FIRST
       LIMIT 10`,
    );

    for (const watch of watches) {
      try {
        const paperId = watch.s2_id
          ? watch.s2_id
          : watch.arxiv_id
            ? `ArXiv:${watch.arxiv_id}`
            : null;

        if (!paperId) continue;

        const paper = await this.s2.getPaper(paperId);
        if (!paper) continue;

        const newCount = paper.citationCount;
        const oldCount = watch.last_citation_count ?? 0;

        await this.pool.query(
          `UPDATE lit_citation_watches
           SET last_checked = NOW(), last_citation_count = $1
           WHERE id = $2`,
          [newCount, watch.id],
        );

        if (newCount > oldCount) {
          const delta = newCount - oldCount;
          console.log(`[LitMonitor] ${watch.title}: +${delta} citations (${oldCount} → ${newCount})`);

          // Fetch the new citing papers
          if (delta <= 20) {
            const citations = await this.s2.getCitations(paperId, delta + 5);
            for (const cit of citations) {
              if (cit.citingPaper) {
                await this.upsertS2Paper(cit.citingPaper);
              }
            }
          }
        }
      } catch (err) {
        console.error(`[LitMonitor] Citation check failed for watch ${watch.id}:`, err);
      }
    }
  }

  // ============================================================
  // Public API methods (used by routes)
  // ============================================================

  /** Add a paper to the citation watch list. */
  async watchPaper(opts: {
    arxivId?: string;
    s2Id?: string;
    title: string;
    project: string;
    reason?: string;
  }): Promise<CitationWatch> {
    const { rows } = await this.pool.query(
      `INSERT INTO lit_citation_watches (arxiv_id, s2_id, title, project, reason)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING *`,
      [opts.arxivId ?? null, opts.s2Id ?? null, opts.title, opts.project, opts.reason ?? null],
    );
    return this.rowToWatch(rows[0]);
  }

  /** Remove a paper from the citation watch list. */
  async unwatchPaper(watchId: number): Promise<boolean> {
    const { rowCount } = await this.pool.query(
      "UPDATE lit_citation_watches SET active = FALSE WHERE id = $1",
      [watchId],
    );
    return (rowCount ?? 0) > 0;
  }

  /** Get alerts for a project, optionally filtered. */
  async getAlerts(opts: {
    project?: string;
    priority?: string;
    acknowledged?: boolean;
    limit?: number;
  }): Promise<LitAlert[]> {
    const conditions: string[] = [];
    const params: unknown[] = [];
    let idx = 1;

    if (opts.project) {
      conditions.push(`a.project = $${idx++}`);
      params.push(opts.project);
    }
    if (opts.priority) {
      conditions.push(`a.priority = $${idx++}`);
      params.push(opts.priority);
    }
    if (opts.acknowledged !== undefined) {
      conditions.push(`a.acknowledged = $${idx++}`);
      params.push(opts.acknowledged);
    }

    const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
    const limit = opts.limit ?? 50;
    params.push(limit);

    const { rows } = await this.pool.query(
      `SELECT a.*, p.title AS paper_title, p.authors AS paper_authors, p.url AS paper_url,
              p.year AS paper_year, p.abstract AS paper_abstract
       FROM lit_alerts a
       JOIN lit_papers p ON p.id = a.paper_id
       ${where}
       ORDER BY a.created_at DESC
       LIMIT $${idx}`,
      params,
    );

    return rows.map((r: Record<string, unknown>) => ({
      id: r.id as number,
      paperId: r.paper_id as string,
      project: r.project as string,
      priority: r.priority as LitAlert["priority"],
      relation: r.relation as LitAlert["relation"],
      similarity: r.similarity as number | null,
      matchedClaim: r.matched_claim as string | null,
      matchedTerms: (r.matched_terms as string[]) ?? [],
      explanation: r.explanation as string | null,
      triageModel: r.triage_model as string | null,
      acknowledged: r.acknowledged as boolean,
      createdAt: (r.created_at as Date).toISOString(),
      paper: {
        id: r.paper_id as string,
        arxivId: null,
        s2Id: null,
        doi: null,
        title: r.paper_title as string,
        abstract: r.paper_abstract as string | null,
        authors: (r.paper_authors as string[]) ?? [],
        venue: null,
        year: r.paper_year as number | null,
        publishedAt: null,
        categories: [],
        citationCount: 0,
        url: r.paper_url as string | null,
        pdfUrl: null,
        source: "s2" as const,
        discoveredAt: "",
      },
    }));
  }

  /** Acknowledge an alert. */
  async acknowledgeAlert(alertId: number): Promise<boolean> {
    const { rowCount } = await this.pool.query(
      "UPDATE lit_alerts SET acknowledged = TRUE WHERE id = $1",
      [alertId],
    );
    return (rowCount ?? 0) > 0;
  }

  /** Get papers from the database. */
  async getPapers(opts: {
    project?: string;
    limit?: number;
    since?: string;
  }): Promise<LitPaper[]> {
    const conditions: string[] = [];
    const params: unknown[] = [];
    let idx = 1;

    if (opts.since) {
      conditions.push(`discovered_at > $${idx++}`);
      params.push(opts.since);
    }

    const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
    const limit = opts.limit ?? 50;
    params.push(limit);

    const { rows } = await this.pool.query(
      `SELECT * FROM lit_papers ${where} ORDER BY discovered_at DESC LIMIT $${idx}`,
      params,
    );

    return rows.map((r: Record<string, unknown>) => this.rowToPaper(r));
  }

  /** Get citation watches. */
  async getWatches(opts?: { project?: string; active?: boolean }): Promise<CitationWatch[]> {
    const conditions: string[] = [];
    const params: unknown[] = [];
    let idx = 1;

    if (opts?.project) {
      conditions.push(`project = $${idx++}`);
      params.push(opts.project);
    }
    if (opts?.active !== undefined) {
      conditions.push(`active = $${idx++}`);
      params.push(opts.active);
    }

    const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";

    const { rows } = await this.pool.query(
      `SELECT * FROM lit_citation_watches ${where} ORDER BY created_at DESC`,
      params,
    );

    return rows.map((r: Record<string, unknown>) => this.rowToWatch(r));
  }

  /** Get monitor statistics. */
  async getStats(): Promise<MonitorStats> {
    const [papers, alerts, unacked, watches] = await Promise.all([
      this.pool.query("SELECT COUNT(*) AS cnt FROM lit_papers"),
      this.pool.query("SELECT COUNT(*) AS cnt FROM lit_alerts"),
      this.pool.query("SELECT COUNT(*) AS cnt FROM lit_alerts WHERE acknowledged = FALSE"),
      this.pool.query("SELECT COUNT(*) AS cnt FROM lit_citation_watches WHERE active = TRUE"),
    ]);

    return {
      totalPapers: parseInt(papers.rows[0].cnt),
      totalAlerts: parseInt(alerts.rows[0].cnt),
      unacknowledgedAlerts: parseInt(unacked.rows[0].cnt),
      activeWatches: parseInt(watches.rows[0].cnt),
      lastScanAt: this.lastTickAt > 0 ? new Date(this.lastTickAt).toISOString() : null,
    };
  }

  // ============================================================
  // Helpers
  // ============================================================

  private rowToPaper(r: Record<string, unknown>): LitPaper {
    return {
      id: r.id as string,
      arxivId: r.arxiv_id as string | null,
      s2Id: r.s2_id as string | null,
      doi: r.doi as string | null,
      title: r.title as string,
      abstract: r.abstract as string | null,
      authors: (r.authors as string[]) ?? [],
      venue: r.venue as string | null,
      year: r.year as number | null,
      publishedAt: r.published_at ? (r.published_at as Date).toISOString() : null,
      categories: (r.categories as string[]) ?? [],
      citationCount: (r.citation_count as number) ?? 0,
      url: r.url as string | null,
      pdfUrl: r.pdf_url as string | null,
      source: r.source as LitPaper["source"],
      discoveredAt: (r.discovered_at as Date).toISOString(),
    };
  }

  private rowToWatch(r: Record<string, unknown>): CitationWatch {
    return {
      id: r.id as number,
      paperId: r.paper_id as string | null,
      arxivId: r.arxiv_id as string | null,
      s2Id: r.s2_id as string | null,
      title: r.title as string,
      project: r.project as string,
      reason: r.reason as string | null,
      lastChecked: r.last_checked ? (r.last_checked as Date).toISOString() : null,
      lastCitationCount: (r.last_citation_count as number) ?? 0,
      active: r.active as boolean,
      createdAt: (r.created_at as Date).toISOString(),
    };
  }
}
