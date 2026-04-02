"""Tests for the trend detector module."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from scripts.compass.trend_detector import (
    detect,
    _detect_from_topic_graph,
    _CONFIDENCE_VELOCITY_CAP,
)


class TestDetectReturnType:
    def test_returns_list(self, synthetic_papers):
        signals = detect(synthetic_papers)
        assert isinstance(signals, list)

    def test_returns_list_of_dicts(self, synthetic_papers):
        signals = detect(synthetic_papers)
        for sig in signals:
            assert isinstance(sig, dict)


class TestSignalSchema:
    def test_required_fields_present(self, synthetic_papers):
        signals = detect(synthetic_papers)
        for sig in signals:
            assert "detector" in sig
            assert "signal_type" in sig
            assert "title" in sig
            assert "description" in sig
            assert "confidence" in sig
            assert "source_papers" in sig

    def test_detector_name(self, synthetic_papers):
        signals = detect(synthetic_papers)
        for sig in signals:
            assert sig["detector"] == "trend"

    def test_confidence_range(self, synthetic_papers):
        signals = detect(synthetic_papers)
        for sig in signals:
            assert 0 <= sig["confidence"] <= 1, (
                f"Confidence {sig['confidence']} out of range for {sig['signal_type']}"
            )


class TestAcceleratingTopics:
    def test_accelerating_detected(self, synthetic_papers):
        """cs.AI has 4 recent papers (p7-p10) plus p11 as old baseline -> acceleration."""
        signals = detect(synthetic_papers)
        types = [s["signal_type"] for s in signals]
        # Should detect either accelerating_no_theory or accelerating_emerging
        has_accel = any(t.startswith("accelerating_") for t in types)
        assert has_accel, f"Expected accelerating signal, got types: {types}"

    def test_velocity_in_metadata(self, synthetic_papers):
        signals = detect(synthetic_papers)
        accel = [s for s in signals if s["signal_type"].startswith("accelerating_")]
        for sig in accel:
            assert "velocity" in sig["metadata"]
            assert sig["metadata"]["velocity"] > 0

    def test_timing_score_set(self, synthetic_papers):
        signals = detect(synthetic_papers)
        accel = [s for s in signals if s["signal_type"].startswith("accelerating_")]
        for sig in accel:
            assert sig["timing_score"] > 0


class TestEdgeCases:
    def test_empty_input(self):
        assert detect([]) == []

    def test_no_dates(self):
        papers = [
            {"id": "x1", "title": "No Date", "abstract": "Some research", "categories": ["cs.AI"]},
        ]
        result = detect(papers)
        assert isinstance(result, list)

    def test_single_paper(self, synthetic_papers):
        result = detect([synthetic_papers[0]])
        assert isinstance(result, list)

    def test_papers_with_no_abstract(self):
        now = datetime.now(timezone.utc)
        papers = [
            {
                "id": "x1", "title": "No Abstract", "abstract": None,
                "categories": ["cs.AI"], "authors": [],
                "discovered_at": (now - timedelta(days=1)).isoformat(),
            },
        ]
        result = detect(papers)
        assert isinstance(result, list)

    def test_invalid_dates_skipped(self):
        papers = [
            {
                "id": "x1", "title": "Bad Date", "abstract": "Some research",
                "categories": ["cs.AI"], "discovered_at": "not-a-date",
            },
        ]
        result = detect(papers)
        assert isinstance(result, list)


# -- Topic-graph detection tests ------------------------------------------

def _make_mock_topic_rows(rows):
    """Create a mock connection that returns topic rows from research_topics."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = rows
    mock_conn.cursor.return_value = mock_cur
    return mock_conn


class TestTopicGraphFiltering:
    """Verify that _detect_from_topic_graph filters unknown labels."""

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=["p1", "p2"])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_unknown_topics_filtered(self, mock_get_conn, _mock_theory, _mock_papers):
        """Topics labeled 'unknown: ...' should be excluded."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "unknown: artificial intelligence | real time", "paper_count": 5, "velocity": 3.3, "claim_count": 0},
            {"id": "t2", "label": "cs.AI: safety alignment", "paper_count": 8, "velocity": 2.5, "claim_count": 3},
        ])
        signals = _detect_from_topic_graph()
        labels = [s.topics[0] for s in signals]
        assert "unknown: artificial intelligence | real time" not in labels
        assert "cs.AI: safety alignment" in labels
        assert len(signals) == 1

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=["p1", "p2"])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_bare_unknown_label_filtered(self, mock_get_conn, _mock_theory, _mock_papers):
        """Topic with label exactly 'unknown' should be excluded."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "unknown", "paper_count": 3, "velocity": 2.0, "claim_count": 0},
        ])
        signals = _detect_from_topic_graph()
        assert len(signals) == 0


class TestTopicGraphSourcePapers:
    """Verify that topic graph signals include source paper IDs."""

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=["p10", "p11", "p12"])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_source_papers_populated(self, mock_get_conn, _mock_theory, _mock_papers):
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "cs.CL: language reasoning", "paper_count": 10, "velocity": 2.0, "claim_count": 5},
        ])
        signals = _detect_from_topic_graph()
        assert len(signals) == 1
        assert signals[0].source_papers == ["p10", "p11", "p12"]

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=[])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_source_papers_empty_gracefully(self, mock_get_conn, _mock_theory, _mock_papers):
        """When fetch fails, source_papers should be an empty list, not crash."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "cs.LG: neural scaling", "paper_count": 4, "velocity": 1.8, "claim_count": 0},
        ])
        signals = _detect_from_topic_graph()
        assert len(signals) == 1
        assert signals[0].source_papers == []


class TestTheoryDetectionFromClaims:
    """Verify that theory detection queries claims table, not just labels."""

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=["p1"])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=True)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_theory_from_claims_marks_emerging(self, mock_get_conn, _mock_theory, _mock_papers):
        """Topic whose label has NO theory words but claims have proofs -> accelerating_emerging."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "cs.CL: chain thought reasoning", "paper_count": 6, "velocity": 2.5, "claim_count": 4},
        ])
        signals = _detect_from_topic_graph()
        assert len(signals) == 1
        assert signals[0].signal_type == "accelerating_emerging"

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=["p1"])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_no_theory_anywhere_marks_no_theory(self, mock_get_conn, _mock_theory, _mock_papers):
        """Topic with no theory in claims or label -> accelerating_no_theory."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "cs.CL: chain thought reasoning", "paper_count": 6, "velocity": 2.5, "claim_count": 4},
        ])
        signals = _detect_from_topic_graph()
        assert len(signals) == 1
        assert signals[0].signal_type == "accelerating_no_theory"

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=["p1"])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_label_fallback_detects_proof(self, mock_get_conn, _mock_theory, _mock_papers):
        """Topic label with 'proof' should still trigger theory even if claims query fails."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "cs.CC: proof complexity", "paper_count": 4, "velocity": 2.0, "claim_count": 0},
        ])
        signals = _detect_from_topic_graph()
        assert len(signals) == 1
        assert signals[0].signal_type == "accelerating_emerging"


class TestConfidenceCalibration:
    """Verify that confidence uses the recalibrated cap (3.0x, not 5.0x)."""

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=[])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_confidence_caps_at_3x(self, mock_get_conn, _mock_theory, _mock_papers):
        """Velocity 3.0 should give confidence 1.0 (not 0.6 as with old /5.0)."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "cs.AI: safety", "paper_count": 5, "velocity": 3.0, "claim_count": 0},
        ])
        signals = _detect_from_topic_graph()
        assert len(signals) == 1
        assert signals[0].confidence == 1.0

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=[])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_confidence_proportional_below_cap(self, mock_get_conn, _mock_theory, _mock_papers):
        """Velocity 1.5 should give confidence 0.5 (1.5/3.0)."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "cs.AI: safety", "paper_count": 5, "velocity": 1.5, "claim_count": 0},
        ])
        signals = _detect_from_topic_graph()
        assert len(signals) == 1
        assert abs(signals[0].confidence - 0.5) < 0.01

    def test_confidence_velocity_cap_is_3(self):
        """The module-level constant should be 3.0."""
        assert _CONFIDENCE_VELOCITY_CAP == 3.0


class TestCombinedDetection:
    """Verify that detect() combines topic-graph and per-paper signals."""

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=["p1"])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_combines_both_sources(self, mock_get_conn, _mock_theory, _mock_papers, synthetic_papers):
        """Both topic-graph and per-paper signals should appear."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "stat.ML: bayesian optimization", "paper_count": 5, "velocity": 2.5, "claim_count": 0},
        ])
        signals = detect(synthetic_papers)
        sources = [s["metadata"].get("source") for s in signals]
        has_topic_graph = any(s == "topic_graph" for s in sources)
        has_per_paper = any(s != "topic_graph" for s in signals)
        assert has_topic_graph, "Should include topic-graph signals"
        assert has_per_paper, "Should include per-paper signals"

    @patch("scripts.compass.trend_detector._fetch_topic_source_papers", return_value=["p1"])
    @patch("scripts.compass.trend_detector._topic_has_theory_claims", return_value=False)
    @patch("scripts.compass.trend_detector.get_connection")
    def test_deduplicates_same_topic(self, mock_get_conn, _mock_theory, _mock_papers, synthetic_papers):
        """If both sources produce signals for 'cs.AI', the topic-graph version wins."""
        mock_get_conn.return_value = _make_mock_topic_rows([
            {"id": "t1", "label": "cs.AI", "paper_count": 10, "velocity": 2.5, "claim_count": 0},
        ])
        signals = detect(synthetic_papers)
        # Find all cs.AI signals
        csai_signals = [s for s in signals if "cs.AI" in s.get("topics", [])]
        # Should only have the topic-graph version, not duplicated
        csai_topic_graph = [s for s in csai_signals if s["metadata"].get("source") == "topic_graph"]
        csai_per_paper = [s for s in csai_signals if s["metadata"].get("source") != "topic_graph"]
        assert len(csai_topic_graph) == 1, "Should have exactly one topic-graph signal for cs.AI"
        assert len(csai_per_paper) == 0, "Per-paper cs.AI signal should be deduped"

    @patch("scripts.compass.trend_detector.get_connection", return_value=None)
    def test_fallback_when_no_db(self, _mock_conn, synthetic_papers):
        """When DB is unavailable, only per-paper signals should appear."""
        signals = detect(synthetic_papers)
        sources = [s["metadata"].get("source") for s in signals]
        assert all(s != "topic_graph" for s in sources)
