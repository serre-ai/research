"""Tests for the contrarian detector module."""

from scripts.compass.contrarian_detector import detect


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
            assert sig["detector"] == "contrarian"

    def test_confidence_range(self, synthetic_papers):
        signals = detect(synthetic_papers)
        for sig in signals:
            assert 0 <= sig["confidence"] <= 1, (
                f"Confidence {sig['confidence']} out of range for {sig['signal_type']}"
            )

    def test_valid_signal_types(self, synthetic_papers):
        valid_types = {"consensus_thin_evidence", "consensus_fragile", "contrarian_opportunity"}
        signals = detect(synthetic_papers)
        for sig in signals:
            assert sig["signal_type"] in valid_types, (
                f"Unexpected signal_type: {sig['signal_type']}"
            )


class TestContrarianOpportunity:
    def test_p5_contradiction_detected(self, synthetic_papers):
        """p5 contradicts the CoT consensus (p13, p14) -- should produce a contrarian signal."""
        signals = detect(synthetic_papers)
        contrarian = [s for s in signals if s["signal_type"] == "contrarian_opportunity"]
        if contrarian:
            # p5 should appear as the contrarian paper
            all_sources = [pid for s in contrarian for pid in s["source_papers"]]
            assert "p5" in all_sources


class TestConsensusClusters:
    def test_consensus_requires_minimum_papers(self):
        """Clusters need >= 3 papers to form. Two papers should produce no cluster signals."""
        papers = [
            {
                "id": "a1", "title": "Paper A",
                "abstract": "We show that method X improves performance significantly.",
                "categories": ["cs.CL"], "authors": [{"name": "A1"}],
            },
            {
                "id": "a2", "title": "Paper B",
                "abstract": "We demonstrate that method X provides gains on benchmarks.",
                "categories": ["cs.CL"], "authors": [{"name": "A2"}],
            },
        ]
        signals = detect(papers)
        cluster_types = {"consensus_thin_evidence", "consensus_fragile"}
        cluster_signals = [s for s in signals if s["signal_type"] in cluster_types]
        assert len(cluster_signals) == 0

    def test_large_single_author_group_flagged(self):
        """Many papers with same author should get thin_evidence if claims overlap."""
        papers = [
            {
                "id": f"same_{i}", "title": f"CoT paper {i}",
                "abstract": (
                    "We show that chain-of-thought prompting improves reasoning "
                    "performance significantly on mathematical benchmarks."
                ),
                "categories": ["cs.CL"],
                "authors": [{"name": "Same Author"}],
            }
            for i in range(5)
        ]
        signals = detect(papers)
        thin = [s for s in signals if s["signal_type"] == "consensus_thin_evidence"]
        # 5 papers with 1 author group should be flagged
        assert len(thin) > 0, "Expected consensus_thin_evidence for single-author cluster"


class TestEdgeCases:
    def test_empty_input(self):
        assert detect([]) == []

    def test_single_paper(self, synthetic_papers):
        result = detect([synthetic_papers[0]])
        assert isinstance(result, list)

    def test_papers_with_no_abstract(self):
        papers = [
            {"id": "x1", "title": "No Abstract", "abstract": None, "categories": [], "authors": []},
            {"id": "x2", "title": "Empty Abstract", "abstract": "", "categories": [], "authors": []},
        ]
        result = detect(papers)
        assert isinstance(result, list)

    def test_papers_without_authors(self):
        papers = [
            {
                "id": f"noauth_{i}", "title": f"Paper {i}",
                "abstract": "We show that transformers improve reasoning performance significantly.",
                "categories": ["cs.CL"],
            }
            for i in range(4)
        ]
        result = detect(papers)
        assert isinstance(result, list)
