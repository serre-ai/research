"""Database access layer for Compass detectors.

Provides helpers for querying lit_papers with pgvector embeddings,
knowledge graph claims, and writing signals to research_signals.
"""

from __future__ import annotations

import json
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://deepwork:deepwork@localhost:5432/deepwork",
)


def get_connection():
    import psycopg2
    import psycopg2.extras
    return psycopg2.connect(DATABASE_URL)


def fetch_papers_with_embeddings(limit: int = 200, since_days: int = 90) -> list[dict]:
    """Fetch papers with their 1024-dim embeddings as text."""
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT id, title, abstract, authors, categories, citation_count,
               discovered_at::text, embedding::text as embedding_str
        FROM lit_papers
        WHERE discovered_at > NOW() - make_interval(days => %s)
          AND abstract IS NOT NULL
        ORDER BY discovered_at DESC
        LIMIT %s
    """, (since_days, limit))
    papers = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return papers


def batch_cosine_similarity(paper_ids: list[str]) -> dict[tuple[str, str], float]:
    """Compute pairwise cosine similarity for a set of papers.

    Returns dict mapping (id_a, id_b) -> similarity where id_a < id_b.
    Only includes pairs with similarity > 0.5 to keep the result manageable.
    """
    if len(paper_ids) < 2:
        return {}
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # Use a self-join with pgvector to compute all pairs above threshold
    # This is efficient for <500 papers
    placeholders = ",".join(["%s"] * len(paper_ids))
    cur.execute(f"""
        SELECT a.id AS id_a, b.id AS id_b,
               1 - (a.embedding <=> b.embedding) AS similarity
        FROM lit_papers a
        CROSS JOIN lit_papers b
        WHERE a.id IN ({placeholders})
          AND b.id IN ({placeholders})
          AND a.id < b.id
          AND a.embedding IS NOT NULL
          AND b.embedding IS NOT NULL
          AND 1 - (a.embedding <=> b.embedding) > 0.5
    """, paper_ids + paper_ids)
    result = {(row["id_a"], row["id_b"]): float(row["similarity"]) for row in cur.fetchall()}
    cur.close()
    conn.close()
    return result


def fetch_claims(project: str = None) -> list[dict]:
    """Fetch claims from the knowledge graph."""
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if project:
        cur.execute(
            "SELECT id::text, project, claim_type, statement, confidence FROM claims WHERE project = %s",
            (project,),
        )
    else:
        cur.execute("SELECT id::text, project, claim_type, statement, confidence FROM claims")
    claims = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return claims


def store_signals_to_db(signals: list[dict]) -> int:
    """Write signals directly to research_signals table."""
    if not signals:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    stored = 0
    for sig in signals:
        try:
            cur.execute("""
                INSERT INTO research_signals
                (detector, signal_type, title, description, confidence,
                 source_papers, source_claims, topics, relevance, timing_score, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                sig.get("detector", ""),
                sig.get("signal_type", ""),
                sig.get("title", ""),
                sig.get("description", ""),
                sig.get("confidence", 0.5),
                sig.get("source_papers", []),
                sig.get("source_claims", []),
                sig.get("topics", []),
                sig.get("relevance", 0),
                sig.get("timing_score", 0),
                json.dumps(sig.get("metadata", {})),
            ))
            stored += 1
        except Exception as e:
            print(f"Warning: failed to store signal: {e}")
    conn.commit()
    cur.close()
    conn.close()
    return stored
