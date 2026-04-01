#!/usr/bin/env python3
"""Extract claims from paper abstracts and store in the knowledge graph.

Scans lit_papers for papers without extracted claims, extracts 1-3 claims
per abstract, classifies them, and inserts into the claims table with
project='_field'.

Usage:
    python3 scripts/compass/claim_extractor.py                    # extract all
    python3 scripts/compass/claim_extractor.py --limit 50         # first 50
    python3 scripts/compass/claim_extractor.py --dry-run          # preview only
"""

from __future__ import annotations

import argparse
import re
import sys

# Reuse CLAIM_PATTERNS from contrarian_detector
try:
    from .contrarian_detector import COMPILED_CLAIM_PATTERNS
    from .db import get_connection, close_connection
except ImportError:
    from contrarian_detector import COMPILED_CLAIM_PATTERNS  # type: ignore
    from db import get_connection, close_connection  # type: ignore


# ── Claim classification ─────────────────────────────────

_FINDING_PATTERNS = re.compile(
    r"prove|theorem|bound|formal", re.IGNORECASE
)
_RESULT_PATTERNS = re.compile(
    r"achiev|%|accuracy|benchmark", re.IGNORECASE
)
_OBSERVATION_PATTERNS = re.compile(
    r"we show|demonstrate|find", re.IGNORECASE
)


def _classify_claim(sentence: str) -> str:
    """Classify a claim sentence into a claim_type."""
    if _FINDING_PATTERNS.search(sentence):
        return "finding"
    if _RESULT_PATTERNS.search(sentence):
        return "result"
    if _OBSERVATION_PATTERNS.search(sentence):
        return "observation"
    return "observation"


def _extract_claims(abstract: str) -> list[str]:
    """Extract sentences that make empirical claims from an abstract."""
    if not abstract:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', abstract)
    claims: list[str] = []
    for sentence in sentences:
        for pattern in COMPILED_CLAIM_PATTERNS:
            if pattern.search(sentence):
                claims.append(sentence.strip())
                break
    return claims[:3]  # top 3 matches


# ── Main extraction pipeline ─────────────────────────────

def fetch_papers_without_claims(limit: int) -> list[dict]:
    """Fetch papers that don't have claims yet."""
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT p.id, p.title, p.abstract
        FROM lit_papers p
        WHERE p.abstract IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM claims c WHERE c.paper_id = p.id)
        ORDER BY p.discovered_at DESC
        LIMIT %s
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    return rows


def insert_claim(
    claim_type: str,
    statement: str,
    source: str,
    paper_id: str,
) -> None:
    """Insert a single claim into the knowledge graph."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO claims (project, claim_type, statement, confidence, source, source_type, paper_id)
        VALUES ('_field', %s, %s, 0.5, %s, 'paper', %s)
    """, (claim_type, statement, source, paper_id))
    cur.close()


def run(
    limit: int = 5000,
    dry_run: bool = False,
    min_length: int = 20,
) -> None:
    """Main extraction loop."""
    papers = fetch_papers_without_claims(limit)
    total = len(papers)
    if total == 0:
        print("No papers without claims found.")
        return

    print(f"Processing {total} papers...")
    total_claims = 0

    for i, paper in enumerate(papers, 1):
        abstract = paper["abstract"] or ""
        title = paper["title"] or "(untitled)"
        paper_id = paper["id"]

        claims = _extract_claims(abstract)
        # Filter by min length
        claims = [c for c in claims if len(c) >= min_length]

        if not claims:
            continue

        if dry_run:
            print(f"[{i}/{total}] \"{title[:60]}\" → {len(claims)} claims (dry-run)")
            for c in claims:
                ct = _classify_claim(c)
                print(f"    [{ct}] {c[:100]}")
        else:
            for claim_text in claims:
                ct = _classify_claim(claim_text)
                insert_claim(ct, claim_text, title, paper_id)
            # Commit per paper to avoid losing everything on error
            get_connection().commit()
            print(f"[{i}/{total}] \"{title[:60]}\" → {len(claims)} claims extracted")

        total_claims += len(claims)

    print(f"\nDone. {total_claims} claims {'would be ' if dry_run else ''}extracted from {total} papers.")


# ── CLI ──────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract claims from paper abstracts into the knowledge graph."
    )
    parser.add_argument(
        "--limit", type=int, default=5000,
        help="Process at most N papers (default: 5000)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview what would be extracted without writing to DB",
    )
    parser.add_argument(
        "--min-length", type=int, default=20,
        help="Skip claims shorter than N chars (default: 20)",
    )
    args = parser.parse_args()

    try:
        run(limit=args.limit, dry_run=args.dry_run, min_length=args.min_length)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        close_connection()


if __name__ == "__main__":
    main()
