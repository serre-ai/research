/**
 * LiteratureScanner — lightweight daily literature scan for scoop detection.
 *
 * Runs keyword searches against arXiv and Semantic Scholar, logs results
 * to activity_log, and notifies on potential threats. No DB schema changes.
 *
 * Designed to be called once per 24h from the daemon cycle.
 * Level 2 replaces this with the full LiteratureMonitor.
 */

import type { ArxivClient, ArxivPaper } from "./arxiv.js";
import type { SemanticScholarClient, S2Paper } from "./semantic-scholar.js";
import type { ActivityLogger } from "./logger.js";
import type { Notifier } from "./notifier.js";
import type { EventBus } from "./event-bus.js";
import type pg from "pg";

// ============================================================
// Types
// ============================================================

export interface ScanResult {
  id: string;
  title: string;
  authors: string[];
  published: string;
  source: "arxiv" | "s2";
  url: string;
  abstract: string | null;
  relevanceScore: number;
  matchedTerms: string[];
}

export interface LiteratureScanReport {
  project: string;
  scannedAt: string;
  queriesRun: number;
  totalResults: number;
  uniqueResults: number;
  threats: ScanResult[];
  allResults: ScanResult[];
}

// ============================================================
// Scanner
// ============================================================

const ARXIV_CATEGORIES = ["cs.CL", "cs.AI", "cs.LG", "cs.CC"];

export class LiteratureScanner {
  constructor(
    private s2: SemanticScholarClient,
    private arxiv: ArxivClient,
    private logger: ActivityLogger,
    private notifier: Notifier,
    private eventBus: EventBus | null,
    private dbPool: pg.Pool | null,
  ) {}

  /**
   * Called once per 24h from daemon cycle.
   * Scans for papers matching project key terms and reports threats.
   */
  async scan(projects: Array<{ project: string; key_terms?: string[] }>): Promise<void> {
    for (const project of projects) {
      const terms = project.key_terms;
      if (!terms || terms.length === 0) continue;

      try {
        const report = await this.scanProject(project.project, terms);

        if (report.uniqueResults > 0) {
          await this.logResults(report);
        }

        if (report.threats.length > 0) {
          await this.notifyThreats(report);
        }

        // Emit event
        if (this.eventBus) {
          await this.eventBus.emit("literature.scan_completed", {
            project: project.project,
            totalResults: report.uniqueResults,
            threats: report.threats.length,
          }).catch(() => {});
        }

        console.log(
          `[LitScan] ${project.project}: ${report.uniqueResults} papers found, ${report.threats.length} threats`,
        );
      } catch (err) {
        console.error(`[LitScan] Error scanning for ${project.project}:`, err);
      }
    }
  }

  private async scanProject(projectName: string, terms: string[]): Promise<LiteratureScanReport> {
    const allResults: ScanResult[] = [];
    let queriesRun = 0;

    // arXiv searches
    for (const term of terms) {
      try {
        const query = this.buildArxivQuery(term);
        const papers = await this.arxiv.search(query, {
          maxResults: 10,
          sortBy: "submittedDate",
          sortOrder: "descending",
        });
        queriesRun++;

        for (const paper of papers) {
          allResults.push(this.arxivToResult(paper, term));
        }
      } catch (err) {
        console.error(`[LitScan] arXiv query failed for "${term}":`, err);
      }
    }

    // Semantic Scholar searches
    for (const term of terms) {
      try {
        const papers = await this.s2.search(term, {
          limit: 10,
          year: "2025-",
          fieldsOfStudy: "Computer Science",
        });
        queriesRun++;

        for (const paper of papers) {
          allResults.push(this.s2ToResult(paper, term));
        }
      } catch (err) {
        console.error(`[LitScan] S2 query failed for "${term}":`, err);
      }
    }

    // Dedup by normalized title
    const unique = this.dedup(allResults);

    // Score and identify threats
    const scored = unique.map((r) => ({
      ...r,
      relevanceScore: this.scoreRelevance(r, terms),
    }));
    scored.sort((a, b) => b.relevanceScore - a.relevanceScore);

    const threats = scored.filter((r) => r.relevanceScore >= 0.6);

    return {
      project: projectName,
      scannedAt: new Date().toISOString(),
      queriesRun,
      totalResults: allResults.length,
      uniqueResults: unique.length,
      threats,
      allResults: scored,
    };
  }

  private buildArxivQuery(term: string): string {
    // If term contains AND/OR/cat:, use as-is (advanced query)
    if (/\b(AND|OR|cat:)\b/.test(term)) return term;
    // Otherwise wrap in all: search across categories
    const catQuery = ARXIV_CATEGORIES.map((c) => `cat:${c}`).join(" OR ");
    return `all:"${term}" AND (${catQuery})`;
  }

  private arxivToResult(paper: ArxivPaper, matchedTerm: string): ScanResult {
    return {
      id: `arxiv:${paper.id}`,
      title: paper.title,
      authors: paper.authors,
      published: paper.published,
      source: "arxiv",
      url: `https://arxiv.org/abs/${paper.id}`,
      abstract: paper.abstract,
      relevanceScore: 0,
      matchedTerms: [matchedTerm],
    };
  }

  private s2ToResult(paper: S2Paper, matchedTerm: string): ScanResult {
    return {
      id: `s2:${paper.paperId}`,
      title: paper.title,
      authors: paper.authors.map((a) => a.name),
      published: paper.publicationDate ?? String(paper.year ?? ""),
      source: "s2",
      url: paper.url,
      abstract: paper.abstract,
      relevanceScore: 0,
      matchedTerms: [matchedTerm],
    };
  }

  private dedup(results: ScanResult[]): ScanResult[] {
    const seen = new Map<string, ScanResult>();
    for (const r of results) {
      const key = this.normalizeTitle(r.title);
      const existing = seen.get(key);
      if (existing) {
        // Merge matched terms
        for (const t of r.matchedTerms) {
          if (!existing.matchedTerms.includes(t)) {
            existing.matchedTerms.push(t);
          }
        }
      } else {
        seen.set(key, { ...r });
      }
    }
    return Array.from(seen.values());
  }

  private normalizeTitle(title: string): string {
    return title.toLowerCase().replace(/[^a-z0-9]/g, "").slice(0, 80);
  }

  /**
   * Score relevance based on keyword overlap with project terms.
   * Returns 0.0-1.0 where higher = more likely a scoop threat.
   */
  private scoreRelevance(result: ScanResult, terms: string[]): number {
    const text = `${result.title} ${result.abstract ?? ""}`.toLowerCase();
    let score = 0;

    // Core concept matches (high weight)
    const coreTerms = [
      "reasoning gap", "reasoning gaps",
      "chain of thought", "cot",
      "complexity class", "circuit complexity",
      "transformer expressiveness",
      "tc0", "nc1", "tc^0", "nc^1",
    ];
    const coreMatches = coreTerms.filter((t) => text.includes(t)).length;
    score += Math.min(coreMatches / 3, 0.5);

    // Project-specific term matches
    const termMatches = terms.filter((t) => text.includes(t.toLowerCase())).length;
    score += Math.min(termMatches / terms.length, 0.3);

    // Multiple matched search queries = higher relevance
    score += Math.min(result.matchedTerms.length * 0.1, 0.2);

    // Recency boost: papers from 2026 score higher
    if (result.published.startsWith("2026")) {
      score += 0.1;
    }

    return Math.min(score, 1.0);
  }

  private async logResults(report: LiteratureScanReport): Promise<void> {
    await this.logger.log({
      type: "session_end", // Reuse existing type for activity_log compat
      project: report.project,
      data: {
        source: "literature_scan",
        scannedAt: report.scannedAt,
        queriesRun: report.queriesRun,
        uniqueResults: report.uniqueResults,
        threats: report.threats.length,
        topResults: report.allResults.slice(0, 10).map((r) => ({
          title: r.title,
          authors: r.authors.slice(0, 3),
          published: r.published,
          relevance: r.relevanceScore,
          url: r.url,
        })),
      },
    });
  }

  private async notifyThreats(report: LiteratureScanReport): Promise<void> {
    const threatList = report.threats
      .slice(0, 5)
      .map((t) => `• ${t.title} (${t.authors[0] ?? "?"} et al., rel=${t.relevanceScore.toFixed(2)})`)
      .join("\n");

    await this.notifier.notify({
      event: "Literature Threat Detected",
      project: report.project,
      summary: `${report.threats.length} potential scoop(s) detected:\n${threatList}`,
      level: report.threats.some((t) => t.relevanceScore >= 0.8) ? "error" : "warning",
    });

    if (this.eventBus) {
      for (const threat of report.threats.slice(0, 5)) {
        await this.eventBus.emit("literature.threat_detected", {
          project: report.project,
          paperId: threat.id,
          title: threat.title,
          relevanceScore: threat.relevanceScore,
          url: threat.url,
        }).catch(() => {});
      }
    }
  }
}
