"""Citation graph analyzer — Compass enrichment module.

Builds citation edges from Semantic Scholar and produces signals:
  - citation_incest: mutual citations (A→B and B→A) or short cycles
  - cited_by_field: papers in lit_papers that cite our project work
  - citation_velocity: papers with fastest citation growth

Uses pure Python HTTP (no TypeScript dependency) and stores citation edges
in a `citation_edges` table.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .schema import ResearchSignal
    from .db import get_connection
except ImportError:
    from schema import ResearchSignal  # type: ignore
    from db import get_connection  # type: ignore


# ── Semantic Scholar API ──────────────────────────────────

S2_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
S2_BASE = "https://api.semanticscholar.org/graph/v1"

DETECTOR_NAME = "citation"
MAX_API_CALLS_PER_RUN = 20


def _s2_get(path: str, params: dict[str, str] | None = None) -> dict | None:
    """Make a GET request to the Semantic Scholar API.

    Returns parsed JSON on success, None on failure.
    """
    url = f"{S2_BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url)
    if S2_API_KEY:
        req.add_header("x-api-key", S2_API_KEY)
    time.sleep(0.15)  # rate limit courtesy
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"  S2 API error for {path}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  S2 API unexpected error for {path}: {e}", file=sys.stderr)
        return None


# ── DB helpers ────────────────────────────────────────────

def _ensure_citation_edges_table() -> None:
    """Create the citation_edges table if it doesn't exist."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS citation_edges (
                source_paper_id TEXT NOT NULL,
                cited_paper_id  TEXT NOT NULL,
                source_s2_id    TEXT,
                cited_s2_id     TEXT,
                discovered_at   TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (source_paper_id, cited_paper_id)
            )
        """)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"  Warning: could not ensure citation_edges table: {e}", file=sys.stderr)


def _store_edges(edges: list[dict]) -> int:
    """Insert citation edges, skipping duplicates."""
    if not edges:
        return 0
    try:
        conn = get_connection()
        cur = conn.cursor()
        stored = 0
        for edge in edges:
            try:
                cur.execute("""
                    INSERT INTO citation_edges
                        (source_paper_id, cited_paper_id, source_s2_id, cited_s2_id)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (source_paper_id, cited_paper_id) DO NOTHING
                """, (
                    edge["source_paper_id"],
                    edge["cited_paper_id"],
                    edge.get("source_s2_id"),
                    edge.get("cited_s2_id"),
                ))
                stored += 1
            except Exception:
                pass
        conn.commit()
        cur.close()
        return stored
    except Exception as e:
        print(f"  Warning: _store_edges failed: {e}", file=sys.stderr)
        return 0


def _fetch_existing_edges() -> list[tuple[str, str]]:
    """Fetch all (source, cited) pairs from citation_edges."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT source_paper_id, cited_paper_id FROM citation_edges")
        rows = cur.fetchall()
        cur.close()
        return [(r[0], r[1]) for r in rows]
    except Exception as e:
        print(f"  Warning: _fetch_existing_edges failed: {e}", file=sys.stderr)
        return []


def _fetch_papers_with_s2_id() -> list[dict]:
    """Fetch papers that have an s2_id from lit_papers."""
    try:
        conn = get_connection()
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id, s2_id, title, citation_count, discovered_at::text
            FROM lit_papers
            WHERE s2_id IS NOT NULL
        """)
        papers = [dict(row) for row in cur.fetchall()]
        cur.close()
        return papers
    except Exception as e:
        print(f"  Warning: _fetch_papers_with_s2_id failed: {e}", file=sys.stderr)
        return []


def _fetch_citation_counts_30d_ago() -> dict[str, int]:
    """Fetch historical citation counts from metadata for velocity calc.

    Looks for a 'citation_count_history' key in lit_papers.metadata,
    or falls back to the current citation_count (velocity = 0 in that case).
    """
    try:
        conn = get_connection()
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id, citation_count,
                   metadata->>'citation_count_30d_ago' AS count_30d_ago
            FROM lit_papers
            WHERE s2_id IS NOT NULL AND citation_count IS NOT NULL
        """)
        result: dict[str, int] = {}
        for row in cur.fetchall():
            old_count = row.get("count_30d_ago")
            if old_count is not None:
                try:
                    result[row["id"]] = int(old_count)
                except (ValueError, TypeError):
                    pass
        cur.close()
        return result
    except Exception as e:
        print(f"  Warning: _fetch_citation_counts_30d_ago failed: {e}", file=sys.stderr)
        return {}


# ── Project title keywords ────────────────────────────────

def _load_project_keywords() -> list[list[str]]:
    """Extract title keywords from each project's BRIEF.md.

    Returns a list of keyword sets (one per project) for matching
    against citing paper titles.
    """
    projects_dir = Path(__file__).resolve().parent.parent.parent / "projects"
    keyword_sets: list[list[str]] = []
    if not projects_dir.is_dir():
        return keyword_sets

    stop_words = frozenset({
        "the", "a", "an", "of", "on", "in", "for", "and", "to", "is",
        "with", "by", "from", "as", "at", "or", "not", "its", "are",
        "vs", "across",
    })

    for proj_dir in sorted(projects_dir.iterdir()):
        brief = proj_dir / "BRIEF.md"
        if not brief.is_file():
            continue
        try:
            text = brief.read_text()
            # Extract the title line (first heading or ## Title line)
            title = ""
            for line in text.splitlines():
                if line.startswith("## Title"):
                    # The title is on this line or the next
                    rest = line.replace("## Title", "").strip()
                    if rest:
                        title = rest
                    continue
                if title == "" and line.startswith("# "):
                    title = line.lstrip("# ").strip()
                    continue
                # If we just saw "## Title", the next non-empty line is the title
                if not title and line.strip():
                    continue

            if not title:
                # Fall back to first heading
                for line in text.splitlines():
                    if line.startswith("# "):
                        title = line.lstrip("# ").strip()
                        break

            if title:
                words = re.findall(r'[a-z]{3,}', title.lower())
                keywords = [w for w in words if w not in stop_words]
                if len(keywords) >= 2:
                    keyword_sets.append(keywords)
        except Exception:
            continue

    return keyword_sets


def _title_matches_project(title: str, project_keywords: list[str], threshold: int = 3) -> bool:
    """Check if a paper title matches a project by keyword overlap."""
    if not title:
        return False
    title_lower = title.lower()
    matched = sum(1 for kw in project_keywords if kw in title_lower)
    return matched >= threshold


# ── Helpers ───────────────────────────────────────────────

def _paper_id(paper: dict) -> str:
    return paper.get("id") or paper.get("s2_id") or paper.get("title", "")


def _paper_ref(paper: dict) -> str:
    return _paper_id(paper)


# ── Step 1: Build citation edges ─────────────────────────

def _build_citation_edges(papers: list[dict]) -> list[dict]:
    """Fetch citations for papers with s2_id and return edge dicts.

    Limits to MAX_API_CALLS_PER_RUN API calls per invocation.
    """
    db_papers = _fetch_papers_with_s2_id()
    if not db_papers:
        # Fall back to papers argument for s2_id info
        db_papers = [p for p in papers if p.get("s2_id")]

    if not db_papers:
        return []

    # Build s2_id -> paper_id mapping
    s2_to_id: dict[str, str] = {}
    for p in db_papers:
        s2_to_id[p["s2_id"]] = p.get("id") or p["s2_id"]

    edges: list[dict] = []
    api_calls = 0

    for paper in db_papers:
        if api_calls >= MAX_API_CALLS_PER_RUN:
            break

        s2_id = paper["s2_id"]
        paper_id = paper.get("id") or s2_id

        data = _s2_get(
            f"/paper/{s2_id}/citations",
            {"fields": "title,authors,year,citationCount", "limit": "50"},
        )
        api_calls += 1

        if data is None:
            continue

        citing_papers = data.get("data", [])
        for entry in citing_papers:
            citing = entry.get("citingPaper", {})
            cited_s2_id = citing.get("paperId")
            if not cited_s2_id:
                continue

            # If the citing paper is also in our DB, use its internal ID
            cited_paper_id = s2_to_id.get(cited_s2_id, cited_s2_id)

            edges.append({
                "source_paper_id": cited_paper_id,  # the citing paper
                "cited_paper_id": paper_id,          # the paper being cited (ours)
                "source_s2_id": cited_s2_id,
                "cited_s2_id": s2_id,
            })

    return edges


# ── Step 2: Detect citation incest ───────────────────────

def _detect_citation_incest(
    papers: list[dict],
    edges: list[tuple[str, str]],
) -> list[ResearchSignal]:
    """Find mutual citations (A cites B AND B cites A) or short cycles."""
    if not edges:
        return []

    # Build adjacency set
    edge_set = set(edges)

    # Build paper lookup
    paper_by_id: dict[str, dict] = {}
    for p in papers:
        pid = _paper_id(p)
        paper_by_id[pid] = p

    signals: list[ResearchSignal] = []
    seen_pairs: set[tuple[str, str]] = set()

    # Check for mutual citations (A→B and B→A)
    for src, dst in edge_set:
        if (dst, src) in edge_set:
            pair = (min(src, dst), max(src, dst))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            title_a = paper_by_id.get(src, {}).get("title", src)[:60]
            title_b = paper_by_id.get(dst, {}).get("title", dst)[:60]

            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="citation_incest",
                title=f"Mutual citation: {title_a} <-> {title_b}",
                description=(
                    f"Papers cite each other with no independent verification chain. "
                    f"This may indicate citation trading or a closed research bubble."
                ),
                confidence=0.7,
                source_papers=[src, dst],
                metadata={
                    "cycle_type": "mutual",
                    "cycle_length": 2,
                    "paper_a_title": title_a,
                    "paper_b_title": title_b,
                },
            ))

    # Check for 3-cycles (A→B→C→A)
    adj: dict[str, set[str]] = defaultdict(set)
    for src, dst in edge_set:
        adj[src].add(dst)

    for a in adj:
        for b in adj.get(a, set()):
            if b == a:
                continue
            for c in adj.get(b, set()):
                if c == a or c == b:
                    continue
                if a in adj.get(c, set()):
                    cycle = tuple(sorted([a, b, c]))
                    if cycle in seen_pairs:
                        continue
                    seen_pairs.add(cycle)

                    titles = [
                        paper_by_id.get(x, {}).get("title", x)[:40]
                        for x in [a, b, c]
                    ]

                    signals.append(ResearchSignal(
                        detector=DETECTOR_NAME,
                        signal_type="citation_incest",
                        title=f"Citation cycle: {' -> '.join(titles)}",
                        description=(
                            f"3-paper citation loop detected. Papers form a closed "
                            f"citation circle with no independent verification."
                        ),
                        confidence=0.8,
                        source_papers=list(cycle),
                        metadata={
                            "cycle_type": "triangle",
                            "cycle_length": 3,
                            "papers": titles,
                        },
                    ))

    signals.sort(key=lambda s: -s.confidence)
    return signals[:15]


# ── Step 3: Find papers citing our work ───────────────────

def _detect_cited_by_field(
    papers: list[dict],
    edges: list[tuple[str, str]],
) -> list[ResearchSignal]:
    """Find papers that cite work related to our projects."""
    project_keywords = _load_project_keywords()
    if not project_keywords or not edges:
        return []

    # Build paper lookup
    paper_by_id: dict[str, dict] = {}
    for p in papers:
        pid = _paper_id(p)
        paper_by_id[pid] = p

    # Also get DB papers for title lookups
    db_papers = _fetch_papers_with_s2_id()
    for p in db_papers:
        pid = p.get("id") or p.get("s2_id", "")
        if pid not in paper_by_id:
            paper_by_id[pid] = p

    signals: list[ResearchSignal] = []

    # For each paper in our DB, check if its title matches a project
    for pid, paper in paper_by_id.items():
        title = paper.get("title", "")
        for kw_set in project_keywords:
            if _title_matches_project(title, kw_set, threshold=3):
                # This paper is related to one of our projects.
                # Find papers that cite it.
                citers = [src for (src, dst) in edges if dst == pid]
                for citer_id in citers:
                    citer = paper_by_id.get(citer_id, {})
                    citer_title = citer.get("title", citer_id)[:70]
                    matched_keywords = [kw for kw in kw_set if kw in title.lower()]

                    signals.append(ResearchSignal(
                        detector=DETECTOR_NAME,
                        signal_type="cited_by_field",
                        title=f"Cited by: {citer_title}",
                        description=(
                            f"Paper '{citer_title}' cites work matching our project "
                            f"keywords ({', '.join(matched_keywords[:5])}). "
                            f"Worth checking for related results or competition."
                        ),
                        confidence=0.6,
                        source_papers=[citer_id, pid],
                        topics=matched_keywords[:5],
                        relevance=0.7,
                        metadata={
                            "cited_paper_title": title[:80],
                            "citing_paper_title": citer_title,
                            "matched_keywords": matched_keywords,
                        },
                    ))
                break  # Don't double-count across keyword sets

    signals.sort(key=lambda s: -s.relevance)
    return signals[:20]


# ── Step 4: Citation velocity ─────────────────────────────

def _detect_citation_velocity(papers: list[dict]) -> list[ResearchSignal]:
    """Find papers with fastest citation growth in the last 30 days.

    Uses metadata->citation_count_30d_ago if available, otherwise
    estimates from discovered_at and current count.
    """
    historical = _fetch_citation_counts_30d_ago()

    # Build candidate list from papers with citation_count
    candidates: list[dict] = []
    for p in papers:
        count = p.get("citation_count")
        if count is None or not isinstance(count, (int, float)):
            continue
        count = int(count)
        pid = _paper_id(p)

        old_count = historical.get(pid)
        if old_count is not None:
            velocity = count - old_count
        else:
            # Estimate: if discovered recently, use days since discovery
            discovered = p.get("discovered_at", "")
            if discovered:
                try:
                    disc_dt = datetime.fromisoformat(
                        discovered.replace("Z", "+00:00")
                    )
                    days_since = max(
                        (datetime.now(timezone.utc) - disc_dt).days, 1
                    )
                    # Normalize to 30-day velocity
                    velocity = int(count * 30 / days_since) if days_since < 90 else 0
                except (ValueError, TypeError):
                    velocity = 0
            else:
                velocity = 0

        if velocity > 0:
            candidates.append({
                **p,
                "_velocity": velocity,
                "_current_count": count,
                "_old_count": old_count,
            })

    # Sort by velocity descending
    candidates.sort(key=lambda c: c["_velocity"], reverse=True)

    signals: list[ResearchSignal] = []
    for c in candidates[:10]:
        title = c.get("title", "")[:70]
        velocity = c["_velocity"]
        current = c["_current_count"]

        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="citation_velocity",
            title=f"High velocity: {title}",
            description=(
                f"Paper gained ~{velocity} citations in the last 30 days "
                f"(now at {current} total). Rapidly growing attention — "
                f"may indicate a breakout result."
            ),
            confidence=min(velocity / 50, 1.0),
            source_papers=[_paper_ref(c)],
            timing_score=min(velocity / 30, 1.0),
            metadata={
                "velocity_30d": velocity,
                "current_citations": current,
                "old_citations": c.get("_old_count"),
            },
        ))

    return signals


# ── Public API ────────────────────────────────────────────

def detect(papers: list[dict]) -> list[dict]:
    """Run citation graph analysis on papers.

    Args:
        papers: list of paper dicts (should have 's2_id' for API enrichment).

    Returns:
        list of signal dicts in the standard ResearchSignal format.
        Returns [] gracefully when S2 API is unavailable or no papers have s2_id.
    """
    # Only proceed if we have papers with s2_id
    s2_papers = [p for p in papers if p.get("s2_id")]
    if not s2_papers:
        return []

    all_signals: list[ResearchSignal] = []

    # Ensure the citation_edges table exists
    try:
        _ensure_citation_edges_table()
    except Exception as e:
        print(f"  Warning: citation_edges table setup failed: {e}", file=sys.stderr)

    # Step 1: Build citation edges from S2 API
    try:
        new_edges = _build_citation_edges(papers)
        if new_edges:
            stored = _store_edges(new_edges)
            print(f"  citation_analyzer: stored {stored} new edges", file=sys.stderr)
    except Exception as e:
        print(f"  Warning: edge building failed: {e}", file=sys.stderr)
        new_edges = []

    # Load all edges (existing + new) for analysis
    try:
        all_edge_tuples = _fetch_existing_edges()
    except Exception:
        # Convert new_edges to tuples as fallback
        all_edge_tuples = [
            (e["source_paper_id"], e["cited_paper_id"]) for e in new_edges
        ]

    # Step 2: Citation incest detection
    try:
        incest_signals = _detect_citation_incest(papers, all_edge_tuples)
        all_signals.extend(incest_signals)
    except Exception as e:
        print(f"  Warning: citation incest detection failed: {e}", file=sys.stderr)

    # Step 3: Papers citing our work
    try:
        cited_signals = _detect_cited_by_field(papers, all_edge_tuples)
        all_signals.extend(cited_signals)
    except Exception as e:
        print(f"  Warning: cited_by_field detection failed: {e}", file=sys.stderr)

    # Step 4: Citation velocity
    try:
        velocity_signals = _detect_citation_velocity(papers)
        all_signals.extend(velocity_signals)
    except Exception as e:
        print(f"  Warning: citation velocity detection failed: {e}", file=sys.stderr)

    # Sort: incest first (highest priority), then cited_by_field, then velocity
    type_priority = {
        "citation_incest": 0,
        "cited_by_field": 1,
        "citation_velocity": 2,
    }
    all_signals.sort(key=lambda s: (
        type_priority.get(s.signal_type, 5),
        -s.confidence,
    ))

    return [s.to_dict() for s in all_signals]
