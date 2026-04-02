#!/usr/bin/env python3
"""Infer relations between claims using embedding similarity.

For each claim, finds similar claims via pgvector cosine distance,
then classifies the relation (supports/contradicts/related_to) using
simple heuristics on claim language.

Usage:
    python3 scripts/compass/relation_inferrer.py                    # process all
    python3 scripts/compass/relation_inferrer.py --limit 100        # first 100 claims
    python3 scripts/compass/relation_inferrer.py --min-similarity 0.75  # threshold
    python3 scripts/compass/relation_inferrer.py --dry-run          # preview only
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

try:
    from .db import get_connection, close_connection
except ImportError:
    from db import get_connection, close_connection  # type: ignore

# ── Sentiment word sets for relation classification ──────

POSITIVE = {
    "improve", "improves", "improved", "improving",
    "achieve", "achieves", "achieved", "achieving",
    "demonstrate", "demonstrates", "demonstrated", "demonstrating",
    "confirm", "confirms", "confirmed", "confirming",
    "show", "shows", "showed", "shown", "showing",
    "prove", "proves", "proved", "proven", "proving",
    "enable", "enables", "enabled", "enabling",
    "advance", "advances", "advanced", "advancing",
    "enhance", "enhances", "enhanced", "enhancing",
    "outperform", "outperforms", "outperformed", "outperforming",
}

NEGATIVE = {
    "fail", "fails", "failed", "failing",
    "not",
    "contrary",
    "challenge", "challenges", "challenged", "challenging",
    "degrade", "degrades", "degraded", "degrading",
    "contradict", "contradicts", "contradicted", "contradicting",
    "refute", "refutes", "refuted", "refuting",
    "unable",
    "cannot",
    "worse", "worsens",
}

# Negation words that flip the polarity of nearby positive words
_NEGATORS = {"not", "cannot", "unable", "no", "neither", "nor", "never", "lack", "lacks"}

# Limitation/negative-outcome phrases that override positive words
_LIMITATION_PHRASES = [
    "cannot solve", "does not", "do not", "cannot",
    "fails to", "unable to", "not reliably", "not consistently",
    "limitations of", "limits of", "bounded by",
]


# ── Relation classifier ─────────────────────────────────

def _effective_polarity(text: str) -> tuple[bool, bool]:
    """Return (is_positive, is_negative) accounting for negation.

    A claim like "We show that transformers cannot solve X" contains both
    "show" (positive) and "cannot" (negative). When a positive word appears
    near a negator or limitation phrase, it should be treated as negative.
    """
    lower = text.lower()
    word_list = lower.split()
    words = set(word_list)

    has_pos = bool(words & POSITIVE)
    has_neg = bool(words & NEGATIVE)

    # Check for limitation phrases that make the overall claim negative
    has_limitation = any(phrase in lower for phrase in _LIMITATION_PHRASES)

    # Check for negators near positive words (within a 5-word window)
    negator_near_positive = False
    for i, w in enumerate(word_list):
        if w in POSITIVE:
            window = set(word_list[max(0, i - 5) : i + 6])
            if window & _NEGATORS:
                negator_near_positive = True
                break

    if has_limitation or negator_near_positive:
        # Positive words are being used in a negative context
        return False, True

    return has_pos, has_neg


def classify_relation(claim_a: str, claim_b: str) -> str:
    """Classify the relation between two claims based on sentiment words.

    Returns one of: 'supports', 'contradicts', 'related_to'.

    Uses negation-aware polarity detection to handle cases like
    "We show that transformers cannot solve X" (negative despite "show").
    """
    a_pos, a_neg = _effective_polarity(claim_a)
    b_pos, b_neg = _effective_polarity(claim_b)

    if (a_pos and b_neg) or (a_neg and b_pos):
        return "contradicts"
    if a_pos and b_pos:
        return "supports"
    return "related_to"


# ── Database queries ─────────────────────────────────────

def fetch_unprocessed_claims(limit: int) -> list[dict]:
    """Fetch claims that don't have outgoing relations yet."""
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT c.id::text, c.statement, c.claim_type, c.source, c.source_type, c.paper_id
        FROM claims c
        WHERE c.project = '_field'
          AND NOT EXISTS (SELECT 1 FROM claim_relations r WHERE r.source_id = c.id)
        ORDER BY c.created_at DESC
        LIMIT %s
    """, (limit,))
    rows = [dict(row) for row in cur.fetchall()]
    cur.close()
    return rows


def find_similar_by_claim_embedding(
    claim_id: str, min_similarity: float
) -> list[dict]:
    """Find similar claims using claim-level embeddings (pgvector)."""
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT c2.id::text, c2.statement, c2.claim_type,
               1 - (c1.embedding <=> c2.embedding) AS similarity
        FROM claims c1, claims c2
        WHERE c1.id = %s::uuid
          AND c2.id != c1.id
          AND c1.embedding IS NOT NULL
          AND c2.embedding IS NOT NULL
          AND 1 - (c1.embedding <=> c2.embedding) > %s
        ORDER BY c1.embedding <=> c2.embedding
        LIMIT 5
    """, (claim_id, min_similarity))
    rows = [dict(row) for row in cur.fetchall()]
    cur.close()
    return rows


def find_similar_by_paper_embedding(
    claim_id: str, paper_id: str, min_similarity: float
) -> list[dict]:
    """Find similar claims using paper-level embedding as proxy.

    When claims don't have their own embeddings, we fall back to the
    embedding of the paper they were extracted from (stored in lit_papers).

    Excludes claims from the same paper — otherwise all claims sharing a
    paper embedding would match with similarity 1.0.
    """
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT c2.id::text, c2.statement, c2.claim_type,
               1 - (p1.embedding <=> p2.embedding) AS similarity
        FROM lit_papers p1
        JOIN claims c2 ON c2.id != %s::uuid
                       AND c2.source_type = 'paper'
                       AND (c2.paper_id IS NULL OR c2.paper_id != %s)
        JOIN lit_papers p2 ON p2.id = c2.paper_id
        WHERE p1.id = %s
          AND p1.embedding IS NOT NULL
          AND p2.embedding IS NOT NULL
          AND p2.id != p1.id
          AND 1 - (p1.embedding <=> p2.embedding) > %s
        ORDER BY p1.embedding <=> p2.embedding
        LIMIT 5
    """, (claim_id, paper_id, paper_id, min_similarity))
    rows = [dict(row) for row in cur.fetchall()]
    cur.close()
    return rows


def claim_has_embedding(claim_id: str) -> bool:
    """Check whether a claim has its own embedding vector."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT embedding IS NOT NULL FROM claims WHERE id = %s::uuid",
        (claim_id,),
    )
    row = cur.fetchone()
    cur.close()
    return bool(row and row[0])


def insert_relation(
    source_id: str,
    target_id: str,
    relation: str,
    strength: float,
) -> bool:
    """Insert a claim relation, skipping on conflict.

    The claim_relations table has UNIQUE(source_id, target_id, relation),
    so we target that constraint explicitly.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO claim_relations (source_id, target_id, relation, strength)
            VALUES (%s::uuid, %s::uuid, %s, %s)
            ON CONFLICT (source_id, target_id, relation) DO NOTHING
        """, (source_id, target_id, relation, strength))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        conn.rollback()
        cur.close()
        print(f"  Warning: insert failed: {e}", file=sys.stderr)
        return False


# ── Main processing ──────────────────────────────────────

def process_claims(
    limit: int = 200,
    min_similarity: float = 0.75,
    batch_size: int = 50,
    dry_run: bool = False,
) -> dict:
    """Process claims and infer relations.

    Returns summary stats dict.
    """
    claims = fetch_unprocessed_claims(limit)
    total = len(claims)

    if total == 0:
        print("No unprocessed claims found.")
        return {"processed": 0, "relations": 0}

    print(f"Found {total} claims without outgoing relations.\n")

    total_relations = 0
    relation_counts: Counter = Counter()

    for idx, claim in enumerate(claims, 1):
        claim_id = claim["id"]
        statement = claim["statement"]
        short = statement[:60] + "..." if len(statement) > 60 else statement

        # Try claim-level embeddings first, fall back to paper-level
        has_own_embedding = claim_has_embedding(claim_id)

        if has_own_embedding:
            similar = find_similar_by_claim_embedding(claim_id, min_similarity)
        elif claim.get("source_type") == "paper" and claim.get("paper_id"):
            similar = find_similar_by_paper_embedding(
                claim_id, claim["paper_id"], min_similarity
            )
        else:
            # No embedding available at all — skip
            print(f"[{idx}/{total}] Claim \"{short}\" — skipped (no embedding)")
            continue

        if not similar:
            print(f"[{idx}/{total}] Claim \"{short}\" — 0 relations")
            continue

        # Classify and insert relations (both directions for symmetric relations)
        batch_counts: Counter = Counter()
        for match in similar:
            relation = classify_relation(statement, match["statement"])
            strength = float(match["similarity"])
            batch_counts[relation] += 1

            if not dry_run:
                insert_relation(claim_id, match["id"], relation, strength)
                # Store reverse direction — contradicts/supports/related_to
                # are all symmetric relations
                insert_relation(match["id"], claim_id, relation, strength)

        n_rels = sum(batch_counts.values())
        total_relations += n_rels
        relation_counts += batch_counts

        parts = ", ".join(
            f"{count} {rel}" for rel, count in sorted(batch_counts.items())
        )
        print(
            f"[{idx}/{total}] Claim \"{short}\" "
            f"→ {n_rels} relations ({parts})"
        )

        # Commit in batches
        if not dry_run and idx % batch_size == 0:
            try:
                conn = get_connection()
                conn.commit()
            except Exception:
                pass

    # Final commit
    if not dry_run:
        try:
            conn = get_connection()
            conn.commit()
        except Exception:
            pass

    print(f"\nDone. Processed {total} claims, created {total_relations} relations.")
    if relation_counts:
        for rel, count in sorted(relation_counts.items()):
            print(f"  {rel}: {count}")

    return {
        "processed": total,
        "relations": total_relations,
        "by_type": dict(relation_counts),
    }


# ── CLI ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Infer relations between claims via embedding similarity."
    )
    parser.add_argument(
        "--limit", type=int, default=200,
        help="Max claims to process (default: 200)",
    )
    parser.add_argument(
        "--min-similarity", type=float, default=0.75,
        help="Cosine similarity threshold (default: 0.75)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=50,
        help="Commit every N claims (default: 50)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview relations without writing to DB",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN — no relations will be written ===\n")

    try:
        process_claims(
            limit=args.limit,
            min_similarity=args.min_similarity,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
        )
    finally:
        close_connection()


if __name__ == "__main__":
    main()
