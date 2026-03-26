#!/usr/bin/env python3
"""Fetch accepted paper metadata from OpenReview for conference profiling.

Uses OpenReview REST API (no auth required for public venues).
Falls back to Firecrawl for JS-rendered pages if API fails.

Output: JSON file at shared/config/venues/data/{venue}-{year}-accepted.json

Usage:
    python3 scripts/openreview-scraper.py --venue neurips --year 2025 [--limit 100]
    python3 scripts/openreview-scraper.py --venue iclr --year 2026 [--limit 100]
    python3 scripts/openreview-scraper.py --all  # fetch all configured venues
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VENUE_IDS: dict[tuple[str, int], str] = {
    ("neurips", 2025): "NeurIPS.cc/2025/Conference",
    ("neurips", 2024): "NeurIPS.cc/2024/Conference",
    ("iclr", 2025): "ICLR.cc/2025/Conference",
    ("iclr", 2026): "ICLR.cc/2026/Conference",
    ("icml", 2025): "ICML.cc/2025/Conference",
}

API_BASE = "https://api2.openreview.net"
PAGE_LIMIT = 100  # max notes per request
REQUEST_DELAY = 1.0  # seconds between requests (rate limiting)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "shared" / "config" / "venues" / "data"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# OpenReview API helpers
# ---------------------------------------------------------------------------


def _api_get(path: str, params: dict | None = None, retries: int = 3) -> dict:
    """Make a GET request to the OpenReview API with retry logic."""
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": "deepwork-scraper/1.0",
        # OpenReview API v2 requires an Authorization header even for public
        # data.  An empty Bearer token grants guest-level read access.
        "Authorization": "Bearer ",
    })
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                delay = (attempt + 1) * 2
                log.warning("HTTP %d for %s — retrying in %ds (attempt %d/%d)", exc.code, url, delay, attempt + 1, retries)
                time.sleep(delay)
                continue
            log.error("HTTP %d for %s: %s", exc.code, url, exc.reason)
            raise
        except urllib.error.URLError as exc:
            if attempt < retries - 1:
                delay = (attempt + 1) * 2
                log.warning("URL error for %s — retrying in %ds", url, delay)
                time.sleep(delay)
                continue
            log.error("URL error for %s: %s", url, exc.reason)
            raise
    return {}  # unreachable, but satisfies type checker


def _extract_paper(note: dict, venue: str, year: int) -> dict | None:
    """Extract structured paper metadata from an OpenReview note object.

    Returns None if the paper should be skipped (e.g. not accepted).
    """
    content = note.get("content", {})

    # Content values may be wrapped in {"value": ...} in API v2
    def _val(field: str, default=None):
        v = content.get(field, default)
        if isinstance(v, dict) and "value" in v:
            return v["value"]
        return v

    title = _val("title", "")
    if not title:
        return None

    # Decision filtering — accept papers whose decision/venue contains "Accept"
    decision = _val("decision", "") or ""
    venue_field = _val("venue", "") or ""
    venueid_field = _val("venueid", "") or ""

    # Some venues store acceptance in the venue string itself
    is_accepted = (
        "accept" in decision.lower()
        or "accept" in venue_field.lower()
        or "accept" in venueid_field.lower()
    )
    # If there's no decision info at all, keep the paper (it may be from an
    # accepted-papers-only listing).
    if decision and not is_accepted:
        return None

    authors = _val("authors", [])
    if isinstance(authors, str):
        authors = [authors]

    keywords = _val("keywords", [])
    if isinstance(keywords, str):
        keywords = [kw.strip() for kw in keywords.split(",")]

    abstract = _val("abstract", "") or ""
    if len(abstract) > 500:
        abstract = abstract[:500] + "..."

    # Review scores — may live in replies or separate endpoint; grab from
    # content if present.
    review_scores: list[int] = []
    raw_scores = _val("review_scores") or _val("scores")
    if isinstance(raw_scores, list):
        for s in raw_scores:
            try:
                review_scores.append(int(float(s)))
            except (ValueError, TypeError):
                pass

    return {
        "id": note.get("forum") or note.get("id", ""),
        "title": title,
        "authors": authors,
        "keywords": [kw.lower().strip() if isinstance(kw, str) else str(kw) for kw in keywords],
        "abstract": abstract,
        "decision": decision or venue_field or "Accept",
    }


def _fetch_papers_api(venue_id: str, venue: str, year: int, limit: int | None) -> list[dict]:
    """Fetch accepted papers from the OpenReview API v2, paginating as needed."""
    papers: list[dict] = []
    offset = 0
    max_papers = limit or 50_000  # safety cap

    log.info("Fetching papers for %s (venue_id=%s)", f"{venue}-{year}", venue_id)

    while len(papers) < max_papers:
        params = {
            "content.venueid": venue_id,
            "limit": min(PAGE_LIMIT, max_papers - len(papers)),
            "offset": offset,
        }
        try:
            data = _api_get("/notes", params)
        except Exception:
            log.warning("API request failed at offset %d, stopping pagination.", offset)
            break

        notes = data.get("notes", [])
        if not notes:
            log.info("No more notes at offset %d (total fetched so far: %d).", offset, len(papers))
            break

        for note in notes:
            paper = _extract_paper(note, venue, year)
            if paper:
                papers.append(paper)
                if len(papers) >= max_papers:
                    break

        log.info(
            "  offset=%d  batch=%d  accepted=%d  total_so_far=%d",
            offset,
            len(notes),
            len(papers),
            len(papers),
        )

        # If we got fewer notes than requested, we've reached the end
        if len(notes) < PAGE_LIMIT:
            break

        offset += len(notes)
        time.sleep(REQUEST_DELAY)

    log.info("Fetched %d accepted papers for %s-%d.", len(papers), venue, year)
    return papers


# ---------------------------------------------------------------------------
# Firecrawl fallback (requires FIRECRAWL_API_KEY env var)
# ---------------------------------------------------------------------------


def _fetch_papers_firecrawl(venue_id: str, venue: str, year: int, limit: int | None) -> list[dict]:
    """Fallback: scrape OpenReview via Firecrawl when the API fails.

    This handles JS-rendered pages that urllib can't parse directly.
    Requires FIRECRAWL_API_KEY environment variable.
    """
    import os

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        log.error("FIRECRAWL_API_KEY not set — cannot use Firecrawl fallback.")
        return []

    log.info("Attempting Firecrawl fallback for %s-%d", venue, year)

    # Build the OpenReview search URL for accepted papers
    search_url = f"https://openreview.net/group?id={urllib.parse.quote(venue_id)}"

    firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
    payload = json.dumps({
        "url": search_url,
        "formats": ["json"],
        "waitFor": 5000,
    }).encode()

    req = urllib.request.Request(
        firecrawl_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "deepwork-scraper/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
    except Exception as exc:
        log.error("Firecrawl request failed: %s", exc)
        return []

    # Firecrawl returns structured data; try to extract paper info
    data = result.get("data", {})
    json_data = data.get("json") if isinstance(data, dict) else None

    if not json_data:
        log.warning("Firecrawl returned no structured JSON data for %s-%d.", venue, year)
        return []

    papers: list[dict] = []
    items = json_data if isinstance(json_data, list) else [json_data]
    max_papers = limit or 50_000

    for item in items:
        if not isinstance(item, dict):
            continue
        title = item.get("title", "")
        if not title:
            continue
        papers.append({
            "id": item.get("id", ""),
            "title": title,
            "authors": item.get("authors", []),
            "keywords": [kw.lower().strip() for kw in item.get("keywords", [])],
            "abstract": (item.get("abstract", "") or "")[:500],
            "decision": item.get("decision", "Accept"),
        })
        if len(papers) >= max_papers:
            break

    log.info("Firecrawl fallback yielded %d papers for %s-%d.", len(papers), venue, year)
    return papers


# ---------------------------------------------------------------------------
# Stats computation
# ---------------------------------------------------------------------------


def _compute_stats(papers: list[dict]) -> dict:
    """Compute keyword frequency statistics from the papers list."""
    keyword_counter: Counter = Counter()
    for paper in papers:
        for kw in paper.get("keywords", []):
            kw_clean = kw.strip().lower()
            if kw_clean:
                keyword_counter[kw_clean] += 1

    by_keyword = dict(keyword_counter.most_common())
    keyword_frequency = keyword_counter.most_common()

    return {
        "total": len(papers),
        "by_keyword": by_keyword,
        "keyword_frequency": keyword_frequency,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def _write_output(venue: str, year: int, papers: list[dict]) -> Path:
    """Write the final JSON output file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{venue}-{year}-accepted.json"

    output = {
        "venue": venue,
        "year": year,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_accepted": len(papers),
        "papers": papers,
        "stats": _compute_stats(papers),
    }

    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    log.info("Wrote %d papers to %s", len(papers), out_path)
    return out_path


# ---------------------------------------------------------------------------
# Fetch orchestration
# ---------------------------------------------------------------------------


def fetch_venue(venue: str, year: int, limit: int | None = None) -> Path | None:
    """Fetch accepted papers for a single venue/year combo.

    Tries the OpenReview API first; falls back to Firecrawl if the API
    returns no results.
    """
    key = (venue.lower(), year)
    venue_id = VENUE_IDS.get(key)
    if not venue_id:
        log.error("No venue ID configured for %s-%d. Known venues: %s", venue, year,
                  ", ".join(f"{v}-{y}" for v, y in sorted(VENUE_IDS.keys())))
        return None

    # Try API first
    papers = _fetch_papers_api(venue_id, venue, year, limit)

    # Fallback to Firecrawl if API returned nothing
    if not papers:
        log.warning("API returned 0 papers for %s-%d, trying Firecrawl fallback...", venue, year)
        papers = _fetch_papers_firecrawl(venue_id, venue, year, limit)

    if not papers:
        log.warning("No accepted papers found for %s-%d.", venue, year)
        return None

    return _write_output(venue, year, papers)


def fetch_all(limit: int | None = None) -> list[Path]:
    """Fetch accepted papers for all configured venues."""
    results: list[Path] = []
    for (venue, year) in sorted(VENUE_IDS.keys()):
        path = fetch_venue(venue, year, limit)
        if path:
            results.append(path)
        # Rate limit between venues
        time.sleep(REQUEST_DELAY)
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch accepted paper metadata from OpenReview.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--venue", type=str, help="Conference name (e.g. neurips, iclr, icml)")
    parser.add_argument("--year", type=int, help="Conference year (e.g. 2025)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Maximum number of papers to fetch (default: all)")
    parser.add_argument("--all", action="store_true", dest="fetch_all",
                        help="Fetch all configured venues")
    parser.add_argument("--list-venues", action="store_true",
                        help="List all configured venue/year combos and exit")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable debug logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.list_venues:
        print("Configured venues:")
        for (v, y), vid in sorted(VENUE_IDS.items()):
            print(f"  {v}-{y}  ->  {vid}")
        return 0

    if args.fetch_all:
        results = fetch_all(args.limit)
        if results:
            print(f"\nFetched {len(results)} venue(s):")
            for p in results:
                print(f"  {p}")
            return 0
        else:
            print("No papers fetched for any venue.", file=sys.stderr)
            return 1

    if not args.venue or not args.year:
        parser.error("Provide --venue and --year, or use --all")

    path = fetch_venue(args.venue.lower(), args.year, args.limit)
    if path:
        print(f"\nOutput: {path}")
        return 0
    else:
        print("No papers fetched.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
