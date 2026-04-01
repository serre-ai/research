"""Tests for the gap detector module."""

from scripts.compass.gap_detector import detect


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
        assert len(signals) > 0, "Expected at least one signal"
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
            assert sig["detector"] == "gap"

    def test_confidence_range(self, synthetic_papers):
        signals = detect(synthetic_papers)
        for sig in signals:
            assert 0 <= sig["confidence"] <= 1, (
                f"Confidence {sig['confidence']} out of range for {sig['signal_type']}"
            )

    def test_source_papers_are_strings(self, synthetic_papers):
        signals = detect(synthetic_papers)
        for sig in signals:
            assert isinstance(sig["source_papers"], list)
            for pid in sig["source_papers"]:
                assert isinstance(pid, str)


class TestMissingEmpirical:
    def test_detected(self, synthetic_papers):
        """p1 is a theory paper that explicitly calls for empirical validation."""
        signals = detect(synthetic_papers)
        types = [s["signal_type"] for s in signals]
        assert "missing_empirical" in types

    def test_source_paper_is_p1(self, synthetic_papers):
        signals = detect(synthetic_papers)
        empirical = [s for s in signals if s["signal_type"] == "missing_empirical"]
        source_ids = [pid for s in empirical for pid in s["source_papers"]]
        assert "p1" in source_ids


class TestMissingTheory:
    def test_detected(self, synthetic_papers):
        """p2 is an empirical paper that explicitly lacks formal theory."""
        signals = detect(synthetic_papers)
        types = [s["signal_type"] for s in signals]
        assert "missing_theory" in types

    def test_source_paper_is_p2(self, synthetic_papers):
        signals = detect(synthetic_papers)
        theory = [s for s in signals if s["signal_type"] == "missing_theory"]
        source_ids = [pid for s in theory for pid in s["source_papers"]]
        assert "p2" in source_ids


class TestUncoveredConnection:
    def test_detected(self, synthetic_papers):
        """p3 and p4 have high topic overlap by different authors."""
        signals = detect(synthetic_papers)
        types = [s["signal_type"] for s in signals]
        assert "uncovered_connection" in types

    def test_p3_p4_pair(self, synthetic_papers):
        signals = detect(synthetic_papers)
        connections = [s for s in signals if s["signal_type"] == "uncovered_connection"]
        # At least one connection should involve p3 and p4
        found = any(
            "p3" in s["source_papers"] and "p4" in s["source_papers"]
            for s in connections
        )
        assert found, "Expected p3+p4 pair in uncovered_connection signals"


class TestContradictingClaims:
    def test_detected(self, synthetic_papers):
        """p5 has contradiction signals and overlaps with other papers."""
        signals = detect(synthetic_papers)
        types = [s["signal_type"] for s in signals]
        assert "contradicting_claims" in types

    def test_p5_in_source(self, synthetic_papers):
        signals = detect(synthetic_papers)
        contras = [s for s in signals if s["signal_type"] == "contradicting_claims"]
        source_ids = [pid for s in contras for pid in s["source_papers"]]
        assert "p5" in source_ids


class TestEdgeCases:
    def test_empty_input(self):
        assert detect([]) == []

    def test_single_paper(self, synthetic_papers):
        # Single paper should not crash
        result = detect([synthetic_papers[0]])
        assert isinstance(result, list)

    def test_papers_with_no_abstract(self):
        papers = [
            {"id": "x1", "title": "No Abstract", "abstract": None, "categories": [], "authors": []},
            {"id": "x2", "title": "Empty Abstract", "abstract": "", "categories": [], "authors": []},
        ]
        result = detect(papers)
        assert isinstance(result, list)

    def test_papers_missing_fields(self):
        """Papers with minimal fields should not crash."""
        papers = [{"title": "Bare paper"}]
        result = detect(papers)
        assert isinstance(result, list)
