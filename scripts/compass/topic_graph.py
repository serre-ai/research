#!/usr/bin/env python3
"""Build topic graph from paper embeddings.

Clusters papers by embedding similarity, labels clusters, computes
velocity, and stores in research_topics + topic_edges tables.

Usage:
    python3 scripts/compass/topic_graph.py                      # build graph
    python3 scripts/compass/topic_graph.py --min-cluster-size 3  # min papers per topic
    python3 scripts/compass/topic_graph.py --dry-run             # preview only
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from .db import get_connection, close_connection, batch_cosine_similarity
except ImportError:
    from db import get_connection, close_connection, batch_cosine_similarity  # type: ignore


# ---------------------------------------------------------------------------
# Helpers (reuse patterns from trend_detector.py)
# ---------------------------------------------------------------------------

STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "and", "but", "or", "nor", "not", "so", "yet", "both",
    "each", "few", "more", "most", "other", "some", "such", "no",
    "only", "own", "same", "than", "too", "very", "just", "because",
    "this", "that", "these", "those", "it", "its", "we", "our",
    "they", "their", "them", "which", "what", "who", "whom",
    "also", "using", "based", "propose", "proposed", "show", "shows",
    "paper", "approach", "method", "methods", "results", "model", "models",
    "new", "use", "used", "two", "one", "first", "however", "work",
})


def _tokenize(text: str) -> list[str]:
    """Extract lowercased non-stopword tokens (3+ chars) from text."""
    words = re.findall(r"[a-z]{3,}", text.lower())
    return [w for w in words if w not in STOP_WORDS]


def _extract_bigram_phrases(papers: list[dict], top_n: int = 3) -> list[str]:
    """Extract the most frequent non-stopword bigrams from paper abstracts."""
    bigram_counts: dict[str, int] = defaultdict(int)
    for paper in papers:
        abstract = paper.get("abstract") or ""
        tokens = _tokenize(abstract)
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i + 1]}"
            bigram_counts[bigram] += 1

    filtered = [(bg, count) for bg, count in bigram_counts.items() if count >= 2]
    filtered.sort(key=lambda x: x[1], reverse=True)
    return [bg for bg, _ in filtered[:top_n]]


def _parse_embedding(embedding_str: str) -> list[float] | None:
    """Parse a pgvector embedding string like '[0.1,0.2,...]' into a float list."""
    if not embedding_str:
        return None
    try:
        cleaned = embedding_str.strip().strip("[]")
        return [float(x) for x in cleaned.split(",")]
    except (ValueError, AttributeError):
        return None


def _average_embeddings(embeddings: list[list[float]]) -> list[float]:
    """Compute element-wise average of a list of embedding vectors."""
    if not embeddings:
        return []
    dim = len(embeddings[0])
    avg = [0.0] * dim
    for emb in embeddings:
        for i in range(dim):
            avg[i] += emb[i]
    n = len(embeddings)
    return [v / n for v in avg]


def _parse_date(date_str: str) -> datetime | None:
    """Parse an ISO timestamp string into a timezone-aware datetime."""
    if not date_str:
        return None
    try:
        cleaned = date_str.strip()
        if cleaned.endswith("Z"):
            cleaned = cleaned[:-1] + "+00:00"
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Step 1: Fetch papers
# ---------------------------------------------------------------------------

def fetch_papers() -> list[dict]:
    """Fetch all papers with embeddings from the database."""
    conn = get_connection()
    import psycopg2.extras
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT id, title, abstract, categories, discovered_at::text,
               embedding::text as embedding_str
        FROM lit_papers
        WHERE embedding IS NOT NULL
    """)
    papers = [dict(row) for row in cur.fetchall()]
    cur.close()
    return papers


# ---------------------------------------------------------------------------
# Step 2: Group by category, sub-cluster with embeddings (union-find)
# ---------------------------------------------------------------------------

def _group_by_primary_category(papers: list[dict]) -> dict[str, list[dict]]:
    """Group papers by their primary arXiv category."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for paper in papers:
        categories = paper.get("categories") or []
        if isinstance(categories, list) and categories:
            primary = categories[0] if isinstance(categories[0], str) else "unknown"
        else:
            primary = "unknown"
        groups[primary].append(paper)
    return groups


def _subcluster_by_embedding(
    papers: list[dict],
    similarity_threshold: float = 0.6,
) -> list[list[dict]]:
    """Sub-cluster papers within a category using embedding similarity.

    Uses union-find (same pattern as trend_detector._cluster_by_embedding).
    Processes paper IDs in batches of 100 for the pairwise similarity query.
    """
    paper_ids = [p["id"] for p in papers if p.get("id")]
    id_to_paper = {p["id"]: p for p in papers if p.get("id")}

    if len(paper_ids) < 2:
        return [papers]

    # Build union-find
    parent: dict[str, str] = {pid: pid for pid in paper_ids}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # Process in batches of 100 to avoid huge cross-join queries
    batch_size = 100
    for i in range(0, len(paper_ids), batch_size):
        batch = paper_ids[i : i + batch_size]
        if len(batch) < 2:
            continue
        try:
            similarities = batch_cosine_similarity(batch)
            for (id_a, id_b), sim in similarities.items():
                if sim >= similarity_threshold:
                    union(id_a, id_b)
        except Exception as e:
            print(f"Warning: batch similarity failed: {e}", file=sys.stderr)

    # Also compute cross-batch similarities for adjacent batches
    for i in range(0, len(paper_ids) - batch_size, batch_size):
        batch_a = paper_ids[i : i + batch_size]
        batch_b = paper_ids[i + batch_size : i + 2 * batch_size]
        combined = batch_a + batch_b
        if len(combined) < 2:
            continue
        try:
            similarities = batch_cosine_similarity(combined)
            for (id_a, id_b), sim in similarities.items():
                if sim >= similarity_threshold:
                    union(id_a, id_b)
        except Exception as e:
            print(f"Warning: cross-batch similarity failed: {e}", file=sys.stderr)

    # Collect clusters
    clusters: dict[str, list[dict]] = defaultdict(list)
    for pid in paper_ids:
        root = find(pid)
        clusters[root].append(id_to_paper[pid])

    return list(clusters.values())


# ---------------------------------------------------------------------------
# Step 3: Build topics with labels, centroids, velocity
# ---------------------------------------------------------------------------

def _compute_velocity(papers: list[dict]) -> float:
    """Compute velocity: papers in last 7 days / (papers in last 30 days / 4)."""
    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    recent_7d = 0
    recent_30d = 0

    for paper in papers:
        dt = _parse_date(paper.get("discovered_at") or "")
        if dt is None:
            continue
        if dt >= cutoff_7d:
            recent_7d += 1
        if dt >= cutoff_30d:
            recent_30d += 1

    baseline = recent_30d / 4.0
    if baseline < 0.5:
        baseline = 0.5

    return round(recent_7d / baseline, 2)


def _compute_centroid(papers: list[dict]) -> list[float] | None:
    """Compute centroid embedding by averaging paper embeddings in Python."""
    embeddings = []
    for paper in papers:
        emb = _parse_embedding(paper.get("embedding_str") or "")
        if emb:
            embeddings.append(emb)
    if not embeddings:
        return None
    return _average_embeddings(embeddings)


def _count_claims_for_papers(paper_ids: list[str]) -> int:
    """Count claims that reference any of the given paper IDs."""
    if not paper_ids:
        return 0
    try:
        conn = get_connection()
        cur = conn.cursor()
        placeholders = ",".join(["%s"] * len(paper_ids))
        cur.execute(f"""
            SELECT COUNT(*) FROM claims
            WHERE source IN ({placeholders})
        """, paper_ids)
        count = cur.fetchone()[0]
        cur.close()
        return count
    except Exception:
        return 0


def build_topics(
    papers: list[dict],
    min_cluster_size: int = 2,
) -> list[dict]:
    """Build topic clusters from papers.

    Groups by primary arXiv category, sub-clusters by embedding similarity,
    then labels each cluster with "{category}: {top bigrams}".

    Returns list of topic dicts ready for DB insertion.
    """
    category_groups = _group_by_primary_category(papers)
    topics: list[dict] = []

    for category, cat_papers in category_groups.items():
        # Sub-cluster within the category
        subclusters = _subcluster_by_embedding(cat_papers, similarity_threshold=0.6)

        for cluster_papers in subclusters:
            if len(cluster_papers) < min_cluster_size:
                continue

            # Label: "{category}: {most frequent bigrams}"
            bigrams = _extract_bigram_phrases(cluster_papers, top_n=3)
            bigram_str = " ".join(bigrams) if bigrams else "general"
            label = f"{category}: {bigram_str}"

            # Centroid embedding
            centroid = _compute_centroid(cluster_papers)

            # Velocity
            velocity = _compute_velocity(cluster_papers)

            # Claim count
            paper_ids = [p["id"] for p in cluster_papers if p.get("id")]
            claim_count = _count_claims_for_papers(paper_ids)

            topics.append({
                "label": label,
                "description": f"{len(cluster_papers)} papers in {category}",
                "embedding": centroid,
                "paper_count": len(cluster_papers),
                "claim_count": claim_count,
                "velocity": velocity,
                "paper_ids": paper_ids,
                "papers": cluster_papers,
            })

    return topics


# ---------------------------------------------------------------------------
# Step 4: Build topic edges (shared papers across categories)
# ---------------------------------------------------------------------------

def build_edges(topics: list[dict]) -> list[dict]:
    """Build edges between topics based on shared papers.

    Papers with multiple categories can appear in multiple topics.
    Edge strength = shared papers / min(topic_a_papers, topic_b_papers).
    """
    # Map paper_id -> list of topic indices
    paper_to_topics: dict[str, list[int]] = defaultdict(list)
    for i, topic in enumerate(topics):
        for pid in topic.get("paper_ids", []):
            paper_to_topics[pid].append(i)

    # Count shared papers between topic pairs
    shared_counts: dict[tuple[int, int], int] = defaultdict(int)
    for pid, topic_indices in paper_to_topics.items():
        for a_idx in range(len(topic_indices)):
            for b_idx in range(a_idx + 1, len(topic_indices)):
                i, j = topic_indices[a_idx], topic_indices[b_idx]
                key = (min(i, j), max(i, j))
                shared_counts[key] += 1

    edges: list[dict] = []
    for (i, j), shared in shared_counts.items():
        min_size = min(topics[i]["paper_count"], topics[j]["paper_count"])
        if min_size == 0:
            continue
        strength = round(shared / min_size, 3)
        edges.append({
            "source_idx": i,
            "target_idx": j,
            "strength": strength,
            "edge_type": "co_occurrence",
        })

    return edges


# ---------------------------------------------------------------------------
# Step 5: Store to database
# ---------------------------------------------------------------------------

def store_topics(topics: list[dict], edges: list[dict], clear: bool = False) -> None:
    """Write topics and edges to research_topics + topic_edges tables."""
    conn = get_connection()
    cur = conn.cursor()

    if clear:
        cur.execute("DELETE FROM topic_edges")
        cur.execute("DELETE FROM group_topic_edges")
        cur.execute("DELETE FROM research_topics")

    # Insert topics and collect generated IDs
    topic_ids: list[str] = []
    for topic in topics:
        embedding_val = None
        if topic.get("embedding"):
            embedding_val = "[" + ",".join(str(v) for v in topic["embedding"]) + "]"

        cur.execute("""
            INSERT INTO research_topics (label, description, embedding, paper_count,
                                         claim_count, velocity, batch_date)
            VALUES (%s, %s, %s::vector, %s, %s, %s, CURRENT_DATE)
            RETURNING id
        """, (
            topic["label"],
            topic.get("description"),
            embedding_val,
            topic["paper_count"],
            topic.get("claim_count", 0),
            topic.get("velocity", 0),
        ))
        row = cur.fetchone()
        topic_ids.append(row[0])

    # Insert edges
    for edge in edges:
        source_id = topic_ids[edge["source_idx"]]
        target_id = topic_ids[edge["target_idx"]]
        cur.execute("""
            INSERT INTO topic_edges (source_id, target_id, strength, edge_type)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (source_id, target_id) DO UPDATE SET
                strength = EXCLUDED.strength,
                edge_type = EXCLUDED.edge_type
        """, (source_id, target_id, edge["strength"], edge["edge_type"]))

    conn.commit()
    cur.close()
    return topic_ids


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build topic graph from paper embeddings."
    )
    parser.add_argument(
        "--min-cluster-size",
        type=int,
        default=2,
        help="Minimum papers to form a topic (default: 2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview topics without writing to DB",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete existing topics before rebuilding",
    )
    args = parser.parse_args()

    # Fetch papers
    print("Fetching papers with embeddings...")
    papers = fetch_papers()
    if not papers:
        print("No papers with embeddings found. Nothing to do.")
        return

    print(f"Found {len(papers)} papers with embeddings.")

    # Build topics
    print("Clustering papers into topics...")
    topics = build_topics(papers, min_cluster_size=args.min_cluster_size)
    if not topics:
        print("No topics formed (try lowering --min-cluster-size).")
        return

    # Build edges
    edges = build_edges(topics)

    # Find largest and fastest
    largest = max(topics, key=lambda t: t["paper_count"])
    fastest = max(topics, key=lambda t: t["velocity"])

    if args.dry_run:
        print(f"\n[DRY RUN] Would create {len(topics)} topics, {len(edges)} edges.")
        print(f"  Largest: \"{largest['label']}\" ({largest['paper_count']} papers)")
        print(f"  Fastest: \"{fastest['label']}\" (velocity {fastest['velocity']}x)")
        print("\nTop topics by paper count:")
        for topic in sorted(topics, key=lambda t: t["paper_count"], reverse=True)[:10]:
            print(f"  {topic['label']:60s}  {topic['paper_count']:4d} papers  vel={topic['velocity']:.1f}x")
        return

    # Store
    print("Writing topics to database...")
    topic_ids = store_topics(topics, edges, clear=args.clear)

    print(
        f"Built {len(topics)} topics, {len(edges)} edges. "
        f"Largest: \"{largest['label']}\" ({largest['paper_count']} papers). "
        f"Fastest: \"{fastest['label']}\" (velocity {fastest['velocity']}x)"
    )

    close_connection()


if __name__ == "__main__":
    main()
