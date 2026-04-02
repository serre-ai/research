"""Trend detector — topic velocity analysis for research-intel.

Detects accelerating, warming, and cooling research topics by analyzing
paper publication rates over time windows. Flags accelerating topics
that lack theoretical contributions as high-value research opportunities.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from .schema import ResearchSignal
    from .db import batch_cosine_similarity, get_connection
except ImportError:
    from schema import ResearchSignal  # type: ignore
    try:
        from db import batch_cosine_similarity, get_connection  # type: ignore
    except ImportError:
        batch_cosine_similarity = None  # type: ignore
        get_connection = None  # type: ignore

# Reuse theory signals from gap_detector (same list, kept in sync)
THEORY_SIGNALS = [
    "theorem", "proof", "formal", "bound", "complexity", "theoretical",
    "analysis", "framework", "formalize", "axiom", "lemma", "corollary",
    "we prove", "we show that", "upper bound", "lower bound",
]

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

DETECTOR_NAME = "trend"


# -- Helpers ---------------------------------------------------------------

def _parse_date(date_str: str) -> datetime | None:
    """Parse an ISO timestamp string into a timezone-aware datetime."""
    if not date_str:
        return None
    try:
        # Handle various ISO formats
        cleaned = date_str.strip()
        if cleaned.endswith("Z"):
            cleaned = cleaned[:-1] + "+00:00"
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _paper_id(paper: dict) -> str:
    """Return a stable paper identifier."""
    return paper.get("id") or paper.get("arxivId") or paper.get("title", "")


def _has_theory(text: str) -> bool:
    """Check if text contains any theory signals."""
    if not text:
        return False
    text_lower = text.lower()
    return any(sig in text_lower for sig in THEORY_SIGNALS)


def _tokenize(text: str) -> list[str]:
    """Extract lowercased non-stopword tokens (3+ chars) from text."""
    words = re.findall(r"[a-z]{3,}", text.lower())
    return [w for w in words if w not in STOP_WORDS]


def _extract_bigram_phrases(papers: list[dict], top_n: int = 5) -> list[str]:
    """Extract the most frequent non-stopword bigrams from paper abstracts.

    Returns up to top_n bigram phrases like "language model", "graph neural".
    """
    bigram_counts: dict[str, int] = defaultdict(int)
    for paper in papers:
        abstract = paper.get("abstract") or ""
        tokens = _tokenize(abstract)
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i + 1]}"
            bigram_counts[bigram] += 1

    # Only keep bigrams that appear in at least 2 papers
    filtered = [(bg, count) for bg, count in bigram_counts.items() if count >= 2]
    filtered.sort(key=lambda x: x[1], reverse=True)
    return [bg for bg, _ in filtered[:top_n]]


def _cluster_by_embedding(
    papers_with_dates: list[tuple[dict, datetime]],
    similarity_threshold: float = 0.7,
) -> dict[str, list[tuple[dict, datetime]]]:
    """Group papers into topic clusters using embedding cosine similarity.

    Papers with similarity > threshold are placed in the same cluster.
    Uses union-find to build transitive clusters, then labels each cluster
    with representative bigram phrases from its papers.

    Falls back to category-based grouping on failure.
    """
    if batch_cosine_similarity is None:
        return _group_papers_by_topic_keyword(papers_with_dates)

    # Collect paper IDs that have embeddings
    id_to_idx: dict[str, int] = {}
    paper_ids: list[str] = []
    for i, (paper, _dt) in enumerate(papers_with_dates):
        if paper.get("embedding_str"):
            pid = _paper_id(paper)
            if pid and pid not in id_to_idx:
                id_to_idx[pid] = i
                paper_ids.append(pid)

    if len(paper_ids) < 2:
        return _group_papers_by_topic_keyword(papers_with_dates)

    try:
        similarities = batch_cosine_similarity(paper_ids)
    except Exception:
        return _group_papers_by_topic_keyword(papers_with_dates)

    if not similarities:
        return _group_papers_by_topic_keyword(papers_with_dates)

    # Union-find for transitive clustering
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

    for (id_a, id_b), sim in similarities.items():
        if sim >= similarity_threshold:
            union(id_a, id_b)

    # Build clusters
    clusters: dict[str, list[int]] = defaultdict(list)
    for pid in paper_ids:
        root = find(pid)
        clusters[root].append(id_to_idx[pid])

    # Also include non-embedding papers via category fallback
    topic_groups: dict[str, list[tuple[dict, datetime]]] = defaultdict(list)

    for cluster_root, indices in clusters.items():
        # Build a label from the top bigrams of cluster papers
        cluster_papers = [papers_with_dates[i][0] for i in indices]
        bigrams = _extract_bigram_phrases(cluster_papers, top_n=2)
        label = "emb:" + (", ".join(bigrams) if bigrams else cluster_root[:20])
        for i in indices:
            topic_groups[label].append(papers_with_dates[i])

    # For papers without embeddings, fall back to category grouping
    embedded_indices = set()
    for indices in clusters.values():
        embedded_indices.update(indices)

    non_embedded = [
        (paper, dt) for i, (paper, dt) in enumerate(papers_with_dates)
        if i not in embedded_indices
    ]
    if non_embedded:
        keyword_groups = _group_papers_by_topic_keyword(non_embedded)
        for key, group in keyword_groups.items():
            topic_groups[key].extend(group)

    return topic_groups


def _group_papers_by_topic_keyword(
    papers_with_dates: list[tuple[dict, datetime]],
) -> dict[str, list[tuple[dict, datetime]]]:
    """Group papers by topic using categories and bigrams (keyword mode)."""
    topic_groups: dict[str, list[tuple[dict, datetime]]] = defaultdict(list)

    # Group by arXiv category
    cat_papers: dict[str, list[dict]] = defaultdict(list)
    for paper, dt in papers_with_dates:
        categories = paper.get("categories") or []
        for cat in categories:
            if isinstance(cat, str):
                topic_groups[cat].append((paper, dt))
                cat_papers[cat].append(paper)

    # Extract bigram-based topics per category
    for cat, cat_paper_list in cat_papers.items():
        if len(cat_paper_list) >= 3:
            bigrams = _extract_bigram_phrases(cat_paper_list, top_n=3)
            for bigram in bigrams:
                topic_key = f"{cat}:{bigram}"
                for paper, dt in papers_with_dates:
                    abstract = (paper.get("abstract") or "").lower()
                    paper_cats = paper.get("categories") or []
                    if cat in paper_cats and bigram in abstract:
                        topic_groups[topic_key].append((paper, dt))

    return topic_groups


def _group_papers_by_topic(
    papers_with_dates: list[tuple[dict, datetime]],
) -> dict[str, list[tuple[dict, datetime]]]:
    """Group papers by topic. Uses embedding clustering when available,
    falls back to category+bigram grouping otherwise."""
    has_embeddings = any(p.get("embedding_str") for p, _dt in papers_with_dates)
    if has_embeddings:
        try:
            return _cluster_by_embedding(papers_with_dates)
        except Exception:
            return _group_papers_by_topic_keyword(papers_with_dates)
    else:
        return _group_papers_by_topic_keyword(papers_with_dates)


# -- Core detection --------------------------------------------------------

def _compute_velocity(
    papers_with_dates: list[tuple[dict, datetime]],
    reference_date: datetime,
) -> dict[str, Any]:
    """Compute velocity metrics for a list of dated papers.

    Returns dict with recent_7d, recent_30d, baseline_weekly_avg, velocity.
    """
    recent_7d = 0
    recent_30d = 0

    cutoff_7d = reference_date - timedelta(days=7)
    cutoff_30d = reference_date - timedelta(days=30)

    for _, dt in papers_with_dates:
        if dt >= cutoff_7d:
            recent_7d += 1
        if dt >= cutoff_30d:
            recent_30d += 1

    # Compute baseline: use 30-day window divided by 4, or all data if <30 days
    dates = [dt for _, dt in papers_with_dates]
    if not dates:
        return {
            "recent_7d": 0,
            "recent_30d": 0,
            "baseline_weekly_avg": 0.0,
            "velocity": 0.0,
        }

    earliest = min(dates)
    data_span_days = (reference_date - earliest).total_seconds() / 86400.0

    if data_span_days < 30:
        # Use all available data for baseline
        weeks = max(data_span_days / 7.0, 1.0)
        baseline_weekly_avg = len(papers_with_dates) / weeks
    else:
        baseline_weekly_avg = recent_30d / 4.0

    velocity = recent_7d / max(baseline_weekly_avg, 0.5)

    return {
        "recent_7d": recent_7d,
        "recent_30d": recent_30d,
        "baseline_weekly_avg": round(baseline_weekly_avg, 2),
        "velocity": round(velocity, 2),
        "data_span_days": round(data_span_days, 1),
    }


def _detect_trends(
    papers_with_dates: list[tuple[dict, datetime]],
) -> list[ResearchSignal]:
    """Run trend detection on dated papers."""
    if not papers_with_dates:
        return []

    # Reference date = most recent paper
    reference_date = max(dt for _, dt in papers_with_dates)
    earliest_date = min(dt for _, dt in papers_with_dates)
    data_span_days = (reference_date - earliest_date).total_seconds() / 86400.0
    low_data = data_span_days < 14

    # Group by topic
    topic_groups = _group_papers_by_topic(papers_with_dates)

    signals: list[ResearchSignal] = []

    for topic, group in topic_groups.items():
        if len(group) < 2:
            continue

        metrics = _compute_velocity(group, reference_date)
        velocity = metrics["velocity"]
        recent_7d = metrics["recent_7d"]
        baseline_weekly_avg = metrics["baseline_weekly_avg"]

        if recent_7d == 0:
            continue

        # Determine trend direction
        if velocity > 2.0:
            # Accelerating — check for theory presence
            recent_cutoff = reference_date - timedelta(days=7)
            recent_papers = [p for p, dt in group if dt >= recent_cutoff]
            recent_ids = [_paper_id(p) for p in recent_papers]

            has_theory = any(
                _has_theory(p.get("abstract") or "")
                for p in recent_papers
            )

            confidence = min(velocity / 5.0, 1.0)
            if low_data:
                confidence = min(confidence, 0.5)

            metadata: dict[str, Any] = {
                "velocity": velocity,
                "recent_7d": recent_7d,
                "baseline_weekly_avg": baseline_weekly_avg,
            }
            if low_data:
                metadata["low_data"] = True

            if not has_theory:
                signals.append(ResearchSignal(
                    detector=DETECTOR_NAME,
                    signal_type="accelerating_no_theory",
                    title=f"Accelerating topic: {topic} ({velocity:.1f}x normal, no theory)",
                    description=(
                        f"{recent_7d} papers in 7 days vs "
                        f"{baseline_weekly_avg:.1f}/week average. "
                        f"No paper with formal/theoretical contribution found."
                    ),
                    confidence=confidence,
                    source_papers=recent_ids[:10],
                    topics=[topic],
                    relevance=0.0,
                    timing_score=min(velocity / 4.0, 1.0),
                    metadata=metadata,
                ))
            else:
                signals.append(ResearchSignal(
                    detector=DETECTOR_NAME,
                    signal_type="accelerating_emerging",
                    title=f"Emerging theory opportunity: {topic} ({velocity:.1f}x normal)",
                    description=(
                        f"{recent_7d} papers in 7 days vs "
                        f"{baseline_weekly_avg:.1f}/week average. "
                        f"Some theoretical work present — emerging theory opportunity."
                    ),
                    confidence=confidence,
                    source_papers=recent_ids[:10],
                    topics=[topic],
                    relevance=0.0,
                    timing_score=min(velocity / 4.0, 1.0),
                    metadata=metadata,
                ))

        elif velocity < 0.5 and len(group) >= 3:
            # Cooling — only flag if there was previous activity
            all_ids = [_paper_id(p) for p, _ in group]

            confidence = min((1.0 - velocity) / 2.0, 1.0)
            if low_data:
                confidence = min(confidence, 0.5)

            metadata = {
                "velocity": velocity,
                "recent_7d": recent_7d,
                "baseline_weekly_avg": baseline_weekly_avg,
            }
            if low_data:
                metadata["low_data"] = True

            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="decelerating_warning",
                title=f"Decelerating topic: {topic} ({velocity:.1f}x normal)",
                description=(
                    f"Topic {topic} declining — {recent_7d} papers in 7 days vs "
                    f"{baseline_weekly_avg:.1f}/week average. Consider deprioritizing."
                ),
                confidence=confidence,
                source_papers=all_ids[:10],
                topics=[topic],
                relevance=0.0,
                timing_score=0.0,
                metadata=metadata,
            ))

    # Sort: accelerating_no_theory first (highest value), then by velocity
    type_priority = {
        "accelerating_no_theory": 0,
        "accelerating_emerging": 1,
        "decelerating_warning": 2,
    }
    signals.sort(key=lambda s: (
        type_priority.get(s.signal_type, 5),
        -s.confidence,
    ))

    return signals


# -- Topic-graph velocity --------------------------------------------------

def _detect_from_topic_graph() -> list[ResearchSignal]:
    """Query research_topics table for accelerating topics.

    Returns signals derived from pre-computed topic velocity in the
    topic_graph builder, which is more accurate than per-paper velocity
    when we only have a short data window.
    """
    if get_connection is None:
        return []
    try:
        conn = get_connection()
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id, label, paper_count, velocity, claim_count
            FROM research_topics
            WHERE velocity > 1.5
            ORDER BY velocity DESC
            LIMIT 20
        """)
        topics = cur.fetchall()
        cur.close()
    except Exception:
        return []

    signals: list[ResearchSignal] = []
    for topic in topics:
        # Check label for theory-related terms
        has_theory = any(
            t in topic["label"].lower()
            for t in ["proof", "theorem", "formal", "bound", "complexity"]
        )

        velocity = float(topic["velocity"])
        signal_type = "accelerating_no_theory" if not has_theory else "accelerating_emerging"

        # Confidence from velocity (higher = more confident)
        confidence = min(velocity / 5.0, 1.0)

        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type=signal_type,
            title=f"Accelerating: {topic['label']} ({velocity:.1f}x, {topic['paper_count']} papers)",
            description=(
                f"Topic cluster '{topic['label']}' has velocity {velocity:.1f}x normal "
                f"activity with {topic['paper_count']} papers."
            ),
            confidence=confidence,
            source_papers=[],
            topics=[topic["label"]],
            timing_score=min(velocity / 4.0, 1.0),
            metadata={
                "velocity": velocity,
                "paper_count": topic["paper_count"],
                "topic_id": topic["id"],
                "source": "topic_graph",
            },
        ))

    return signals


# -- Public API ------------------------------------------------------------

def detect(papers: list[dict]) -> list[dict]:
    """Run trend detection on pre-fetched papers.

    Tries pre-computed topic velocity from the research_topics table first
    (populated by the topic_graph builder). Falls back to per-paper velocity
    when the topic graph is unavailable or returns no signals.

    Args:
        papers: list of paper dicts with fields: id, title, abstract,
                categories (list[str]), discovered_at (ISO timestamp).

    Returns:
        list of signal dicts in the standard ResearchSignal format.
    """
    # Try pre-computed topic velocity first (more accurate with short data windows)
    topic_graph_signals = _detect_from_topic_graph()
    if topic_graph_signals:
        return [s.to_dict() for s in topic_graph_signals]

    # Fall back to per-paper velocity computation
    papers_with_dates: list[tuple[dict, datetime]] = []
    for paper in papers:
        dt = _parse_date(paper.get("discovered_at") or "")
        if dt is not None:
            papers_with_dates.append((paper, dt))

    if not papers_with_dates:
        return []

    all_signals = _detect_trends(papers_with_dates)
    return [s.to_dict() for s in all_signals]
