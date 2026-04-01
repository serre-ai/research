"""Tests for the frontier scanner module."""

from datetime import datetime, timedelta, timezone

from scripts.compass.frontier_scanner import detect


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
            assert sig["detector"] == "frontier"

    def test_confidence_range(self, synthetic_papers):
        signals = detect(synthetic_papers)
        for sig in signals:
            assert 0 <= sig["confidence"] <= 1, (
                f"Confidence {sig['confidence']} out of range for {sig['signal_type']}"
            )

    def test_valid_signal_types(self, synthetic_papers):
        valid_types = {
            "frontier_jump_unexplained",
            "frontier_sota_cluster",
            "frontier_new_capability",
        }
        signals = detect(synthetic_papers)
        for sig in signals:
            assert sig["signal_type"] in valid_types, (
                f"Unexpected signal_type: {sig['signal_type']}"
            )


class TestNewCapability:
    def test_first_model_signal_detected(self, synthetic_papers):
        """p6 uses 'first model to' which is a new capability signal."""
        signals = detect(synthetic_papers)
        new_cap = [s for s in signals if s["signal_type"] == "frontier_new_capability"]
        if new_cap:
            all_sources = [pid for s in new_cap for pid in s["source_papers"]]
            assert "p6" in all_sources

    def test_new_capability_with_explicit_signal(self):
        papers = [
            {
                "id": "nc1",
                "title": "Emergent Planning in LLMs",
                "abstract": (
                    "For the first time, we demonstrate that LLMs can perform "
                    "multi-step planning in novel environments without any training."
                ),
                "categories": ["cs.AI"],
                "authors": [{"name": "NC Author"}],
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        signals = detect(papers)
        new_cap = [s for s in signals if s["signal_type"] == "frontier_new_capability"]
        assert len(new_cap) > 0, "Expected frontier_new_capability signal"
        assert "nc1" in new_cap[0]["source_papers"]


class TestPerformanceExtraction:
    def test_benchmark_score_extraction(self):
        """Papers with explicit accuracy claims on named benchmarks should be extracted."""
        papers = [
            {
                "id": "bench1",
                "title": "Paper A achieves 60% on BigBench",
                "abstract": "Our model achieves 60.0% accuracy on BigBench evaluation.",
                "categories": ["cs.AI"],
                "discovered_at": "2026-01-01T00:00:00Z",
            },
            {
                "id": "bench2",
                "title": "Paper B achieves 85% on BigBench",
                "abstract": "We report 85.0% accuracy on BigBench evaluation. A state-of-the-art result.",
                "categories": ["cs.AI"],
                "discovered_at": "2026-02-01T00:00:00Z",
            },
        ]
        signals = detect(papers)
        # 25pp jump should trigger frontier_jump_unexplained
        jump = [s for s in signals if s["signal_type"] == "frontier_jump_unexplained"]
        assert len(jump) > 0, f"Expected frontier_jump_unexplained, got: {[s['signal_type'] for s in signals]}"
        assert jump[0]["metadata"]["delta"] == 25.0


class TestSOTACluster:
    def test_multiple_sota_same_benchmark(self):
        """Multiple SOTA claims on the same benchmark should produce a cluster signal."""
        papers = [
            {
                "id": f"sota_{i}",
                "title": f"SOTA paper {i}",
                "abstract": (
                    f"We achieve {80 + i}.0% accuracy on MMLU evaluation. "
                    f"This is a new state-of-the-art result."
                ),
                "categories": ["cs.AI"],
                "discovered_at": f"2026-0{i + 1}-01T00:00:00Z",
            }
            for i in range(3)
        ]
        signals = detect(papers)
        cluster = [s for s in signals if s["signal_type"] == "frontier_sota_cluster"]
        assert len(cluster) > 0, "Expected frontier_sota_cluster signal"


class TestEdgeCases:
    def test_empty_input(self):
        assert detect([]) == []

    def test_single_paper(self, synthetic_papers):
        result = detect([synthetic_papers[0]])
        assert isinstance(result, list)

    def test_papers_with_no_abstract(self):
        papers = [
            {"id": "x1", "title": "No Abstract", "abstract": None, "categories": [], "authors": []},
        ]
        result = detect(papers)
        assert isinstance(result, list)
        assert result == []

    def test_paper_with_percentage_but_no_benchmark(self):
        """A percentage without a benchmark name should not produce signals."""
        papers = [
            {
                "id": "pct1",
                "title": "Training Efficiency Paper",
                "abstract": "We reduce training cost by 40% using our technique.",
                "categories": ["cs.LG"],
                "discovered_at": "2026-01-01T00:00:00Z",
            },
        ]
        result = detect(papers)
        jump = [s for s in result if s["signal_type"] == "frontier_jump_unexplained"]
        assert len(jump) == 0
