"""Tests for the trend detector module."""

from datetime import datetime, timedelta, timezone

from scripts.compass.trend_detector import detect


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
