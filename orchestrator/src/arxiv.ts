/**
 * arXiv API client.
 * No auth required. Rate limit: 1 req/3sec (be respectful).
 * Docs: https://info.arxiv.org/help/api/
 * Returns Atom XML — parsed manually to avoid adding a dependency.
 */

const BASE_URL = "http://export.arxiv.org/api/query";
const MIN_REQUEST_INTERVAL_MS = 3100; // just over 3 sec per arXiv guidelines

// ============================================================
// Types
// ============================================================

export interface ArxivPaper {
  id: string;             // e.g. "2401.12345"
  title: string;
  abstract: string;
  authors: string[];
  categories: string[];
  primaryCategory: string;
  published: string;      // ISO date
  updated: string;        // ISO date
  pdfUrl: string;
  doi: string | null;
}

export interface ArxivSearchOptions {
  maxResults?: number;
  start?: number;
  sortBy?: "relevance" | "lastUpdatedDate" | "submittedDate";
  sortOrder?: "ascending" | "descending";
}

// ============================================================
// Client
// ============================================================

export class ArxivClient {
  private lastRequestAt = 0;

  /**
   * Search papers by query string.
   * Query syntax: https://info.arxiv.org/help/api/user-manual.html#query_details
   * Examples:
   *   "all:reasoning gaps"
   *   "ti:chain of thought AND cat:cs.CL"
   *   "au:merrill AND ti:transformers"
   */
  async search(query: string, opts: ArxivSearchOptions = {}): Promise<ArxivPaper[]> {
    // Build URL manually — URLSearchParams encodes + signs which breaks arXiv boolean syntax
    const parts = [
      `search_query=${encodeURIComponent(query)}`,
      `max_results=${opts.maxResults ?? 20}`,
      `start=${opts.start ?? 0}`,
      `sortBy=${opts.sortBy ?? "submittedDate"}`,
      `sortOrder=${opts.sortOrder ?? "descending"}`,
    ];

    const xml = await this.fetch(`${BASE_URL}?${parts.join("&")}`);
    return this.parseAtom(xml);
  }

  /**
   * Get recent papers from specified categories.
   * Categories: cs.CL, cs.AI, cs.LG, cs.CC, etc.
   */
  async recent(
    categories: string[],
    maxResults = 50,
  ): Promise<ArxivPaper[]> {
    const catQuery = categories.map((c) => `cat:${c}`).join(" OR ");
    return this.search(catQuery, {
      maxResults,
      sortBy: "submittedDate",
      sortOrder: "descending",
    });
  }

  /** Get a single paper by arXiv ID (e.g. "2401.12345"). */
  async getPaper(arxivId: string): Promise<ArxivPaper | null> {
    const xml = await this.fetch(`${BASE_URL}?id_list=${encodeURIComponent(arxivId)}`);
    const papers = this.parseAtom(xml);
    return papers[0] ?? null;
  }

  // --------------------------------------------------------
  // Internals
  // --------------------------------------------------------

  private async fetch(url: string): Promise<string> {
    const elapsed = Date.now() - this.lastRequestAt;
    if (elapsed < MIN_REQUEST_INTERVAL_MS) {
      await new Promise((r) => setTimeout(r, MIN_REQUEST_INTERVAL_MS - elapsed));
    }
    this.lastRequestAt = Date.now();

    const res = await globalThis.fetch(url);
    if (!res.ok) {
      throw new Error(`arXiv error: ${res.status} ${res.statusText}`);
    }
    return res.text();
  }

  /** Parse Atom XML feed into ArxivPaper array. */
  private parseAtom(xml: string): ArxivPaper[] {
    const papers: ArxivPaper[] = [];
    const entries = xml.split("<entry>");

    // First chunk is the feed header, skip it
    for (let i = 1; i < entries.length; i++) {
      const entry = entries[i];
      const paper = this.parseEntry(entry);
      if (paper) papers.push(paper);
    }

    return papers;
  }

  private parseEntry(entry: string): ArxivPaper | null {
    const id = this.extractTag(entry, "id");
    if (!id) return null;

    // Extract arXiv ID from URL: http://arxiv.org/abs/2401.12345v1 → 2401.12345
    const arxivId = id.replace(/^.*\/abs\//, "").replace(/v\d+$/, "");

    const title = this.extractTag(entry, "title")?.replace(/\s+/g, " ").trim() ?? "";
    const abstract = this.extractTag(entry, "summary")?.replace(/\s+/g, " ").trim() ?? "";
    const published = this.extractTag(entry, "published") ?? "";
    const updated = this.extractTag(entry, "updated") ?? "";

    // Authors
    const authors: string[] = [];
    const authorMatches = entry.matchAll(/<author>\s*<name>([^<]+)<\/name>/g);
    for (const m of authorMatches) {
      authors.push(m[1].trim());
    }

    // Categories
    const categories: string[] = [];
    const catMatches = entry.matchAll(/category[^>]*term="([^"]+)"/g);
    for (const m of catMatches) {
      categories.push(m[1]);
    }
    const primaryCategory =
      this.extractAttr(entry, "arxiv:primary_category", "term") ?? categories[0] ?? "";

    // PDF link
    const pdfMatch = entry.match(/<link[^>]*title="pdf"[^>]*href="([^"]+)"/);
    const pdfUrl = pdfMatch?.[1] ?? `https://arxiv.org/pdf/${arxivId}`;

    // DOI
    const doi = this.extractTag(entry, "arxiv:doi") ?? null;

    return {
      id: arxivId,
      title,
      abstract,
      authors,
      categories,
      primaryCategory,
      published,
      updated,
      pdfUrl,
      doi,
    };
  }

  private extractTag(xml: string, tag: string): string | null {
    // Handle both <tag>content</tag> and namespaced tags
    const regex = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, "i");
    const match = xml.match(regex);
    return match?.[1]?.trim() ?? null;
  }

  private extractAttr(xml: string, tag: string, attr: string): string | null {
    const regex = new RegExp(`<${tag}[^>]*${attr}="([^"]+)"`, "i");
    const match = xml.match(regex);
    return match?.[1] ?? null;
  }
}
