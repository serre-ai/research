"""Database access layer for Compass detectors.

Provides helpers for querying lit_papers with pgvector embeddings,
knowledge graph claims, and writing signals to research_signals.

Uses a module-level connection that's created on first use and reused.
"""

from __future__ import annotations

import json
import os
import sys

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://deepwork:deepwork@localhost:5432/deepwork",
)

_conn = None


def get_connection():
    """Get or create a reusable database connection."""
    global _conn
    if _conn is not None:
        try:
            _conn.cursor().execute("SELECT 1")
            return _conn
        except Exception:
            # Connection is stale — reconnect
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None
    import psycopg2
    _conn = psycopg2.connect(DATABASE_URL)
    return _conn


def close_connection():
    """Explicitly close the shared connection."""
    global _conn
    if _conn is not None:
        try:
            _conn.close()
        except Exception:
            pass
        _conn = None


def fetch_papers_with_embeddings(limit: int = 200, since_days: int = 90) -> list[dict]:
    """Fetch papers with their 1024-dim embeddings as text."""
    try:
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
        return papers
    except Exception as e:
        print(f"Warning: DB fetch failed, returning empty: {e}", file=sys.stderr)
        return []


def batch_cosine_similarity(paper_ids: list[str]) -> dict[tuple[str, str], float]:
    """Compute pairwise cosine similarity for a set of papers.

    Returns dict mapping (id_a, id_b) -> similarity where id_a < id_b.
    Only includes pairs with similarity > 0.5 to keep the result manageable.

    Uses parameterized query — the f-string only builds the placeholder
    count (%s, %s, ...), not user data. Paper IDs are passed as parameters.
    """
    if len(paper_ids) < 2:
        return {}
    try:
        conn = get_connection()
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
        return result
    except Exception as e:
        print(f"Warning: batch_cosine_similarity failed: {e}", file=sys.stderr)
        return {}


def fetch_claims(project: str = None) -> list[dict]:
    """Fetch claims from the knowledge graph."""
    try:
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
        return claims
    except Exception as e:
        print(f"Warning: fetch_claims failed: {e}", file=sys.stderr)
        return []


def store_signals_to_db(signals: list[dict]) -> int:
    """Write signals directly to research_signals table."""
    if not signals:
        return 0
    try:
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
                print(f"Warning: failed to store signal: {e}", file=sys.stderr)
        conn.commit()
        cur.close()
        return stored
    except Exception as e:
        print(f"Warning: store_signals_to_db failed: {e}", file=sys.stderr)
        return 0
