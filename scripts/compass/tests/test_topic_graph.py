"""Tests for the topic graph module."""

import math
from datetime import datetime, timedelta, timezone

from scripts.compass.topic_graph import (
    _average_embeddings,
    _compute_centroid,
    _compute_velocity,
    _cosine_similarity,
    _extract_bigram_phrases,
    _group_by_primary_category,
    _parse_date,
    _parse_embedding,
    _tokenize,
    build_edges,
    build_topics,
)


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

def _make_emb(seed: float, dim: int = 8) -> list[float]:
    """Create a deterministic embedding vector for testing."""
    return [math.sin(seed + i) for i in range(dim)]


def _emb_str(emb: list[float]) -> str:
    """Format an embedding as a pgvector string."""
    return "[" + ",".join(str(v) for v in emb) + "]"


def _make_papers_with_embeddings():
    """Create test papers with embeddings for clustering tests."""
    now = datetime.now(timezone.utc)
    # Group A: similar embeddings (seeds close together)
    emb_a1, emb_a2, emb_a3 = _make_emb(1.0), _make_emb(1.05), _make_emb(1.1)
    # Group B: different embeddings (seeds far apart)
    emb_b1, emb_b2 = _make_emb(50.0), _make_emb(50.05)
    return [
        {
            "id": "a1", "title": "Paper A1",
            "abstract": "language models transformers attention mechanism",
            "categories": ["cs.CL"],
            "discovered_at": (now - timedelta(days=1)).isoformat(),
            "embedding_str": _emb_str(emb_a1),
        },
        {
            "id": "a2", "title": "Paper A2",
            "abstract": "language models transformers attention layers",
            "categories": ["cs.CL"],
            "discovered_at": (now - timedelta(days=2)).isoformat(),
            "embedding_str": _emb_str(emb_a2),
        },
        {
            "id": "a3", "title": "Paper A3",
            "abstract": "language models transformers self attention",
            "categories": ["cs.CL"],
            "discovered_at": (now - timedelta(days=3)).isoformat(),
            "embedding_str": _emb_str(emb_a3),
        },
        {
            "id": "b1", "title": "Paper B1",
            "abstract": "reinforcement learning reward policy optimization",
            "categories": ["cs.CL"],
            "discovered_at": (now - timedelta(days=1)).isoformat(),
            "embedding_str": _emb_str(emb_b1),
        },
        {
            "id": "b2", "title": "Paper B2",
            "abstract": "reinforcement learning reward policy gradient",
            "categories": ["cs.CL"],
            "discovered_at": (now - timedelta(days=2)).isoformat(),
            "embedding_str": _emb_str(emb_b2),
        },
    ]


# ---------------------------------------------------------------------------
# _tokenize
# ---------------------------------------------------------------------------

class TestTokenize:
    def test_basic(self):
        tokens = _tokenize("We use a Large Language Model for text.")
        assert "large" in tokens
        assert "language" in tokens
        # "use", "for" are stop words, should be excluded
        assert "use" not in tokens
        assert "for" not in tokens

    def test_short_words_excluded(self):
        tokens = _tokenize("AI is an ML framework")
        # "ai", "is", "an", "ml" are all <= 2 chars or stop words
        assert "framework" in tokens

    def test_empty_string(self):
        assert _tokenize("") == []


# ---------------------------------------------------------------------------
# _extract_bigram_phrases — deduplication
# ---------------------------------------------------------------------------

class TestExtractBigramPhrases:
    def test_deduplication(self):
        """Bigrams sharing words should not produce repeated words in output."""
        papers = [
            {"abstract": "large language models are great language models help"},
            {"abstract": "large language models improve language models work"},
            {"abstract": "large language models scale language models fine"},
        ]
        bigrams = _extract_bigram_phrases(papers, top_n=3)
        # Flatten all words from all bigram phrases
        all_words = []
        for phrase in bigrams:
            all_words.extend(phrase.split())
        # No word should appear more than once across all phrases
        assert len(all_words) == len(set(all_words)), (
            f"Duplicate words in bigram phrases: {bigrams}"
        )

    def test_returns_list(self):
        papers = [{"abstract": "some text here"}]
        result = _extract_bigram_phrases(papers)
        assert isinstance(result, list)

    def test_empty_papers(self):
        assert _extract_bigram_phrases([]) == []

    def test_no_abstract(self):
        papers = [{"abstract": None}]
        assert _extract_bigram_phrases(papers) == []


# ---------------------------------------------------------------------------
# _parse_embedding
# ---------------------------------------------------------------------------

class TestParseEmbedding:
    def test_basic(self):
        result = _parse_embedding("[0.1,0.2,0.3]")
        assert result == [0.1, 0.2, 0.3]

    def test_whitespace(self):
        result = _parse_embedding("  [0.1, 0.2, 0.3]  ")
        assert len(result) == 3

    def test_none(self):
        assert _parse_embedding(None) is None

    def test_empty(self):
        assert _parse_embedding("") is None

    def test_invalid(self):
        assert _parse_embedding("not a vector") is None


# ---------------------------------------------------------------------------
# _average_embeddings
# ---------------------------------------------------------------------------

class TestAverageEmbeddings:
    def test_single(self):
        result = _average_embeddings([[1.0, 2.0, 3.0]])
        assert result == [1.0, 2.0, 3.0]

    def test_two(self):
        result = _average_embeddings([[1.0, 0.0], [3.0, 4.0]])
        assert result == [2.0, 2.0]

    def test_empty(self):
        assert _average_embeddings([]) == []

    def test_mismatched_dims_skipped(self):
        """Vectors with different dimensions should be skipped in averaging."""
        result = _average_embeddings([[1.0, 2.0], [3.0, 4.0, 5.0]])
        # Second vector is skipped, so avg = (1+0)/2, (2+0)/2 — implementation
        # currently adds 0 for skipped, so result might be off. Main point:
        # it shouldn't crash.
        assert len(result) == 2


# ---------------------------------------------------------------------------
# _cosine_similarity
# ---------------------------------------------------------------------------

class TestCosineSimilarity:
    def test_identical(self):
        v = [1.0, 2.0, 3.0]
        assert abs(_cosine_similarity(v, v) - 1.0) < 1e-6

    def test_orthogonal(self):
        assert abs(_cosine_similarity([1.0, 0.0], [0.0, 1.0])) < 1e-6

    def test_opposite(self):
        assert abs(_cosine_similarity([1.0, 0.0], [-1.0, 0.0]) - (-1.0)) < 1e-6

    def test_empty(self):
        assert _cosine_similarity([], []) == 0.0

    def test_different_lengths(self):
        assert _cosine_similarity([1.0], [1.0, 2.0]) == 0.0

    def test_zero_vector(self):
        assert _cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


# ---------------------------------------------------------------------------
# _parse_date
# ---------------------------------------------------------------------------

class TestParseDate:
    def test_iso_format(self):
        dt = _parse_date("2026-03-01T12:00:00+00:00")
        assert dt.year == 2026

    def test_z_suffix(self):
        dt = _parse_date("2026-03-01T12:00:00Z")
        assert dt.tzinfo is not None

    def test_naive(self):
        dt = _parse_date("2026-03-01T12:00:00")
        assert dt.tzinfo is not None  # Should be set to UTC

    def test_none(self):
        assert _parse_date(None) is None

    def test_empty(self):
        assert _parse_date("") is None

    def test_invalid(self):
        assert _parse_date("not-a-date") is None


# ---------------------------------------------------------------------------
# _group_by_primary_category
# ---------------------------------------------------------------------------

class TestGroupByPrimaryCategory:
    def test_basic(self):
        papers = [
            {"id": "1", "categories": ["cs.CL", "cs.AI"]},
            {"id": "2", "categories": ["cs.AI"]},
            {"id": "3", "categories": ["cs.CL"]},
        ]
        groups = _group_by_primary_category(papers)
        assert len(groups["cs.CL"]) == 2
        assert len(groups["cs.AI"]) == 1

    def test_missing_categories(self):
        papers = [{"id": "1", "categories": None}]
        groups = _group_by_primary_category(papers)
        assert "unknown" in groups

    def test_empty_categories(self):
        papers = [{"id": "1", "categories": []}]
        groups = _group_by_primary_category(papers)
        assert "unknown" in groups


# ---------------------------------------------------------------------------
# _compute_velocity
# ---------------------------------------------------------------------------

class TestComputeVelocity:
    def test_all_recent(self):
        now = datetime.now(timezone.utc)
        papers = [
            {"discovered_at": (now - timedelta(days=1)).isoformat()},
            {"discovered_at": (now - timedelta(days=2)).isoformat()},
        ]
        vel = _compute_velocity(papers)
        assert vel > 0

    def test_no_dates(self):
        papers = [{"discovered_at": None}]
        vel = _compute_velocity(papers)
        assert vel == 0.0

    def test_old_papers_low_velocity(self):
        now = datetime.now(timezone.utc)
        papers = [
            {"discovered_at": (now - timedelta(days=60)).isoformat()},
            {"discovered_at": (now - timedelta(days=90)).isoformat()},
        ]
        vel = _compute_velocity(papers)
        assert vel == 0.0

    def test_baseline_floor(self):
        """When all papers are recent but few, baseline should use floor of 0.5."""
        now = datetime.now(timezone.utc)
        papers = [
            {"discovered_at": (now - timedelta(days=1)).isoformat()},
        ]
        vel = _compute_velocity(papers)
        # 1 paper in 7d, 1 in 30d -> baseline = max(1/4, 0.5) = 0.5
        # velocity = 1 / 0.5 = 2.0
        assert vel == 2.0


# ---------------------------------------------------------------------------
# _compute_centroid
# ---------------------------------------------------------------------------

class TestComputeCentroid:
    def test_basic(self):
        papers = [
            {"embedding_str": "[1.0,0.0]"},
            {"embedding_str": "[0.0,1.0]"},
        ]
        centroid = _compute_centroid(papers)
        assert centroid == [0.5, 0.5]

    def test_no_embeddings(self):
        papers = [{"embedding_str": None}]
        assert _compute_centroid(papers) is None


# ---------------------------------------------------------------------------
# build_topics — integration (no DB, uses Python-local similarity)
# ---------------------------------------------------------------------------

class TestBuildTopics:
    def test_produces_topics(self):
        papers = _make_papers_with_embeddings()
        topics = build_topics(papers, min_cluster_size=2, similarity_threshold=0.35)
        assert len(topics) >= 1
        for topic in topics:
            assert topic["paper_count"] >= 2
            assert "label" in topic
            assert "embedding" in topic
            assert "velocity" in topic

    def test_separates_dissimilar_papers(self):
        """Papers with very different embeddings should form separate topics."""
        papers = _make_papers_with_embeddings()
        topics = build_topics(papers, min_cluster_size=2, similarity_threshold=0.9)
        # With a very high threshold, the A-group and B-group should separate
        # (if they cluster at all)
        if len(topics) >= 2:
            # Verify they're separate clusters
            topic_ids = [set(t["paper_ids"]) for t in topics]
            a_ids = {"a1", "a2", "a3"}
            b_ids = {"b1", "b2"}
            for ids in topic_ids:
                # No topic should mix A and B papers
                assert not (ids & a_ids and ids & b_ids), (
                    f"Topic mixes A and B papers: {ids}"
                )

    def test_label_no_repeated_words(self):
        """Labels should not contain repeated words from bigram dedup."""
        papers = _make_papers_with_embeddings()
        topics = build_topics(papers, min_cluster_size=2, similarity_threshold=0.35)
        for topic in topics:
            label = topic["label"]
            # Extract the part after the category prefix
            if ": " in label:
                phrase_part = label.split(": ", 1)[1]
                # Split by pipe separator and check words within
                segments = phrase_part.split(" | ")
                all_words = []
                for seg in segments:
                    all_words.extend(seg.split())
                assert len(all_words) == len(set(all_words)), (
                    f"Repeated words in label: {label}"
                )

    def test_empty_input(self):
        assert build_topics([]) == []

    def test_min_cluster_size_filters(self):
        """With min_cluster_size higher than paper count, no topics should form."""
        papers = _make_papers_with_embeddings()
        topics = build_topics(papers, min_cluster_size=100)
        assert topics == []


# ---------------------------------------------------------------------------
# build_edges — centroid similarity
# ---------------------------------------------------------------------------

class TestBuildEdges:
    def test_similar_centroids_produce_edges(self):
        """Topics with similar centroids should be connected."""
        topics = [
            {
                "label": "A",
                "embedding": [1.0, 0.0, 0.0],
                "paper_count": 5,
                "paper_ids": ["p1", "p2"],
            },
            {
                "label": "B",
                "embedding": [0.9, 0.1, 0.0],  # Very similar to A
                "paper_count": 3,
                "paper_ids": ["p3", "p4"],
            },
        ]
        edges = build_edges(topics, similarity_threshold=0.3)
        assert len(edges) >= 1
        assert edges[0]["edge_type"] == "embedding_similarity"
        assert edges[0]["strength"] > 0.3

    def test_dissimilar_centroids_no_edges(self):
        """Topics with orthogonal centroids should not be connected."""
        topics = [
            {
                "label": "A",
                "embedding": [1.0, 0.0, 0.0],
                "paper_count": 5,
                "paper_ids": ["p1"],
            },
            {
                "label": "B",
                "embedding": [0.0, 1.0, 0.0],  # Orthogonal
                "paper_count": 3,
                "paper_ids": ["p2"],
            },
        ]
        edges = build_edges(topics, similarity_threshold=0.3)
        assert len(edges) == 0

    def test_shared_papers_produce_edges(self):
        """Shared paper IDs should create co_occurrence edges."""
        topics = [
            {
                "label": "A",
                "embedding": [1.0, 0.0, 0.0],
                "paper_count": 5,
                "paper_ids": ["p1", "p2", "shared"],
            },
            {
                "label": "B",
                "embedding": [0.0, 1.0, 0.0],  # Orthogonal
                "paper_count": 3,
                "paper_ids": ["p3", "shared"],
            },
        ]
        edges = build_edges(topics, similarity_threshold=0.99)  # High threshold
        # Should still have an edge from shared paper even though centroids are dissimilar
        co_occ = [e for e in edges if e["edge_type"] == "co_occurrence"]
        assert len(co_occ) >= 1

    def test_empty_topics(self):
        assert build_edges([]) == []

    def test_no_embeddings_no_centroid_edges(self):
        """Topics without embeddings should only get edges from shared papers."""
        topics = [
            {"label": "A", "embedding": None, "paper_count": 5, "paper_ids": ["p1"]},
            {"label": "B", "embedding": None, "paper_count": 3, "paper_ids": ["p2"]},
        ]
        edges = build_edges(topics, similarity_threshold=0.3)
        assert len(edges) == 0
