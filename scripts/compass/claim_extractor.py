#!/usr/bin/env python3
"""Extract claims from paper abstracts and store in the knowledge graph.

Scans lit_papers for papers without extracted claims, extracts 1-5 claims
per abstract, classifies them, and inserts into the claims table with
project='_field'.

Usage:
    python3 scripts/compass/claim_extractor.py                    # extract all
    python3 scripts/compass/claim_extractor.py --limit 50         # first 50
    python3 scripts/compass/claim_extractor.py --dry-run          # preview only
    python3 scripts/compass/claim_extractor.py --force            # re-extract all
"""

from __future__ import annotations

import argparse
import re
import sys

try:
    from .db import get_connection, close_connection
except ImportError:
    from db import get_connection, close_connection  # type: ignore


# ── Claim extraction patterns ────────────────────────────
# Broader than contrarian_detector's patterns — tuned for recall.
# Most papers make 2-3 claims in their abstract; the old patterns
# (imported from contrarian_detector) only matched ~0.6 per paper.

CLAIM_PATTERNS = [
    # "We X that" constructions
    r"we show that\b",
    r"we find that\b",
    r"we demonstrate\b",
    r"we prove\b",
    r"we observe\b",
    r"we report\b",
    r"we establish\b",
    r"we verify\b",
    r"we confirm\b",
    # "We X" (propose/introduce/present — common in ML papers)
    r"we propose\b",
    r"we introduce\b",
    r"we present\b",
    r"we develop\b",
    # "Our X" constructions
    r"our results (?:demonstrate|show|indicate|suggest|confirm)\b",
    r"our experiments (?:show|demonstrate|confirm|reveal)\b",
    r"our method\b",
    r"our approach\b",
    r"our model\b",
    # Results / metrics
    r"achieves?\s+\d+[\.\d]*\s*%",
    r"achieves?\s+(?:state[- ]of[- ]the[- ]art|sota)\b",
    r"outperforms?\b",
    r"improves?\s+(?:over|upon|by)\b",
    r"surpass(?:es)?\b",
    r"state[- ]of[- ]the[- ]art",
    r"significant(?:ly)?\s+(?:better|improve|outperform|higher|lower|faster|reduce)",
    # Comparative claims
    r"(?:better|higher|faster|lower|fewer)\s+than\b",
    r"reduces?\s+(?:by\s+)?\d+[\.\d]*\s*%",
    r"increases?\s+(?:by\s+)?\d+[\.\d]*\s*%",
    r"\d+[\.\d]*\s*%\s+(?:improvement|reduction|increase|decrease|gain)",
    r"\d+[\.\d]*x\s+(?:faster|speedup|improvement)",
    # Numeric results with metric names
    r"(?:F1|BLEU|ROUGE|accuracy|precision|recall|perplexity|AUC)\s*(?:of|=|:)\s*\d+",
    # Discovery language
    r"(?:results?|findings?|experiments?)\s+(?:show|indicate|suggest|demonstrate|reveal)\b",
    r"this (?:paper|work|study)\s+(?:shows?|demonstrates?|presents?|introduces?|proposes?)\b",
    # Novelty claims
    r"(?:the\s+)?first\s+to\b",
    r"novel\s+(?:approach|method|framework|architecture|technique|algorithm)\b",
    r"new\s+(?:approach|method|framework|architecture|technique|algorithm)\b",
]

COMPILED_CLAIM_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CLAIM_PATTERNS]

MAX_CLAIMS_PER_PAPER = 5


# ── Claim classification ─────────────────────────────────

_FINDING_PATTERNS = re.compile(
    r"prove|theorem|bound|formal|establish|derive|verify|confirm|lemma|corollary",
    re.IGNORECASE,
)
_RESULT_PATTERNS = re.compile(
    r"achiev|%|accuracy|benchmark|F1|BLEU|ROUGE|perplexity|precision|recall"
    r"|speedup|latency|throughput|AUC|outperform|state[- ]of[- ]the[- ]art",
    re.IGNORECASE,
)
_OBSERVATION_PATTERNS = re.compile(
    r"we show|demonstrate|find|observe|note that|reveal|discover|indicate|suggest",
    re.IGNORECASE,
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
    return claims[:MAX_CLAIMS_PER_PAPER]


# ── Main extraction pipeline ─────────────────────────────

def fetch_papers(limit: int, force: bool = False) -> list[dict]:
    """Fetch papers for claim extraction.

    By default, skips papers that already have claims (NOT EXISTS).
    With force=True, fetches all papers (for re-extraction with better patterns).
    """
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if force:
        cur.execute("""
            SELECT p.id, p.title, p.abstract
            FROM lit_papers p
            WHERE p.abstract IS NOT NULL
            ORDER BY p.discovered_at DESC
            LIMIT %s
        """, (limit,))
    else:
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


def _delete_field_claims_for_paper(paper_id: str) -> int:
    """Delete existing _field claims for a paper (used in --force mode)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM claims WHERE project = '_field' AND paper_id = %s",
        (paper_id,),
    )
    deleted = cur.rowcount
    cur.close()
    return deleted


def insert_claim(
    claim_type: str,
    statement: str,
    source: str,
    paper_id: str,
) -> None:
    """Insert a single claim into the knowledge graph.

    source is the paper_id (not the title) so downstream consumers
    can look up the source paper directly.
    """
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
    force: bool = False,
    min_length: int = 20,
    batch_size: int = 50,
) -> None:
    """Main extraction loop."""
    papers = fetch_papers(limit, force=force)
    total = len(papers)
    if total == 0:
        print("No papers to process.")
        return

    print(f"Processing {total} papers...")
    total_claims = 0
    papers_with_claims = 0

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
            print(f"[{i}/{total}] \"{title[:60]}\" -> {len(claims)} claims (dry-run)")
            for c in claims:
                ct = _classify_claim(c)
                print(f"    [{ct}] {c[:100]}")
        else:
            # In force mode, delete old claims first
            if force:
                _delete_field_claims_for_paper(paper_id)

            for claim_text in claims:
                ct = _classify_claim(claim_text)
                # Store paper_id as source (not title) for reliable lookups
                insert_claim(ct, claim_text, paper_id, paper_id)

            if i % batch_size == 0:
                get_connection().commit()
                print(f"[{i}/{total}] \"{title[:60]}\" -> {len(claims)} claims (committed batch)")
            else:
                print(f"[{i}/{total}] \"{title[:60]}\" -> {len(claims)} claims")

        total_claims += len(claims)
        papers_with_claims += 1

    # Final commit for remaining papers
    if not dry_run:
        get_connection().commit()

    avg = total_claims / total if total > 0 else 0
    print(f"\nDone. {total_claims} claims {'would be ' if dry_run else ''}extracted "
          f"from {papers_with_claims}/{total} papers (avg {avg:.1f}/paper).")


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
        "--force", action="store_true",
        help="Re-extract claims for papers that already have them "
             "(deletes old _field claims first)",
    )
    parser.add_argument(
        "--min-length", type=int, default=20,
        help="Skip claims shorter than N chars (default: 20)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=50,
        help="Commit every N papers (default: 50)",
    )
    args = parser.parse_args()

    try:
        run(
            limit=args.limit,
            dry_run=args.dry_run,
            force=args.force,
            min_length=args.min_length,
            batch_size=args.batch_size,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        close_connection()


if __name__ == "__main__":
    main()
