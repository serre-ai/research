/**
 * Semantic Scholar API client.
 * Works unauthenticated at 1 req/sec. With API key: 10 req/sec.
 * Docs: https://api.semanticscholar.org/api-docs/
 */

const BASE_URL = "https://api.semanticscholar.org/graph/v1";
const RECS_URL = "https://api.semanticscholar.org/recommendations/v1";
const MIN_REQUEST_INTERVAL_MS = 1050; // just over 1 req/sec for unauthenticated

// ============================================================
// Types
// ============================================================

export interface S2Paper {
  paperId: string;
  title: string;
  abstract: string | null;
  year: number | null;
  citationCount: number;
  venue: string | null;
  authors: S2Author[];
  externalIds: Record<string, string> | null;
  fieldsOfStudy: string[] | null;
  url: string;
  publicationDate: string | null;
}

export interface S2Author {
  authorId: string;
  name: string;
}

export interface S2Citation {
  citingPaper: S2Paper;
}

export interface S2Reference {
  citedPaper: S2Paper;
}

export interface S2SearchOptions {
  limit?: number;
  offset?: number;
  year?: string;            // e.g. "2024-" for 2024 onwards
  fieldsOfStudy?: string;   // e.g. "Computer Science"
}

const DEFAULT_PAPER_FIELDS = [
  "paperId", "title", "abstract", "year", "citationCount",
  "venue", "authors", "externalIds", "fieldsOfStudy", "url", "publicationDate",
].join(",");

// ============================================================
// Client
// ============================================================

export class SemanticScholarClient {
  private apiKey: string | null;
  private lastRequestAt = 0;
  private minInterval: number;

  constructor(apiKey?: string) {
    this.apiKey = apiKey ?? process.env.SEMANTIC_SCHOLAR_API_KEY ?? null;
    // Authenticated: 10 req/sec, unauthenticated: 1 req/sec
    this.minInterval = this.apiKey ? 105 : MIN_REQUEST_INTERVAL_MS;
  }

  /** Search for papers by keyword query. */
  async search(query: string, opts: S2SearchOptions = {}): Promise<S2Paper[]> {
    const params = new URLSearchParams({
      query,
      fields: DEFAULT_PAPER_FIELDS,
      limit: String(opts.limit ?? 20),
      offset: String(opts.offset ?? 0),
    });
    if (opts.year) params.set("year", opts.year);
    if (opts.fieldsOfStudy) params.set("fieldsOfStudy", opts.fieldsOfStudy);

    const data = await this.get(`${BASE_URL}/paper/search?${params}`);
    return data?.data ?? [];
  }

  /** Get a single paper by Semantic Scholar ID, DOI, or arXiv ID. */
  async getPaper(id: string): Promise<S2Paper | null> {
    // Accepts: S2 paper ID, DOI:xxx, ArXiv:xxx, CorpusId:xxx
    const data = await this.get(
      `${BASE_URL}/paper/${encodeURIComponent(id)}?fields=${DEFAULT_PAPER_FIELDS}`,
    );
    return data ?? null;
  }

  /** Get papers that cite the given paper. */
  async getCitations(paperId: string, limit = 50): Promise<S2Citation[]> {
    const params = new URLSearchParams({
      fields: DEFAULT_PAPER_FIELDS,
      limit: String(limit),
    });
    const data = await this.get(
      `${BASE_URL}/paper/${encodeURIComponent(paperId)}/citations?${params}`,
    );
    return data?.data ?? [];
  }

  /** Get papers referenced by the given paper. */
  async getReferences(paperId: string, limit = 50): Promise<S2Reference[]> {
    const params = new URLSearchParams({
      fields: DEFAULT_PAPER_FIELDS,
      limit: String(limit),
    });
    const data = await this.get(
      `${BASE_URL}/paper/${encodeURIComponent(paperId)}/references?${params}`,
    );
    return data?.data ?? [];
  }

  /** Batch lookup papers by ID (up to 500). */
  async batchGetPapers(ids: string[]): Promise<S2Paper[]> {
    if (ids.length === 0) return [];
    if (ids.length > 500) {
      throw new Error("Batch limit is 500 papers");
    }
    await this.rateLimit();
    const res = await fetch(`${BASE_URL}/paper/batch?fields=${DEFAULT_PAPER_FIELDS}`, {
      method: "POST",
      headers: this.headers({ "Content-Type": "application/json" }),
      body: JSON.stringify({ ids }),
    });
    if (!res.ok) {
      throw new Error(`S2 batch error: ${res.status} ${res.statusText}`);
    }
    return (await res.json()) as S2Paper[];
  }

  /** Get recommended papers similar to the given paper. */
  async getRecommendations(paperId: string, limit = 20): Promise<S2Paper[]> {
    const params = new URLSearchParams({
      fields: DEFAULT_PAPER_FIELDS,
      limit: String(limit),
    });
    const data = await this.get(
      `${RECS_URL}/papers/forpaper/${encodeURIComponent(paperId)}?${params}`,
    );
    return data?.recommendedPapers ?? [];
  }

  // --------------------------------------------------------
  // Internals
  // --------------------------------------------------------

  private headers(extra: Record<string, string> = {}): Record<string, string> {
    const h: Record<string, string> = { ...extra };
    if (this.apiKey) h["x-api-key"] = this.apiKey;
    return h;
  }

  private async rateLimit(): Promise<void> {
    const elapsed = Date.now() - this.lastRequestAt;
    if (elapsed < this.minInterval) {
      await new Promise((r) => setTimeout(r, this.minInterval - elapsed));
    }
    this.lastRequestAt = Date.now();
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private async get(url: string, attempt = 0): Promise<any> {
    await this.rateLimit();
    const res = await fetch(url, { headers: this.headers() });

    if (res.status === 429) {
      if (attempt >= 3) {
        throw new Error("S2 rate limited after 3 retries");
      }
      const backoff = Math.max(
        parseInt(res.headers.get("retry-after") ?? "0") * 1000,
        (attempt + 1) * 3000,
      );
      console.warn(`[S2] Rate limited, retry ${attempt + 1}/3 in ${backoff}ms`);
      await new Promise((r) => setTimeout(r, backoff));
      this.lastRequestAt = Date.now();
      return this.get(url, attempt + 1);
    }

    if (res.status === 404) return null;

    if (!res.ok) {
      throw new Error(`S2 error: ${res.status} ${res.statusText}`);
    }

    return res.json();
  }
}
