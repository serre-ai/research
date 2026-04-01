"""Tests for the signal fusion / synthesis engine."""

from scripts.compass.synthesize import synthesize


def _make_signal(
    detector="gap",
    signal_type="missing_empirical",
    title="Test signal",
    description="Test description",
    confidence=0.7,
    topics=None,
    source_papers=None,
    relevance=0.0,
    timing_score=0.0,
):
    """Helper to build a minimal signal dict."""
    return {
        "detector": detector,
        "signal_type": signal_type,
        "title": title,
        "description": description,
        "confidence": confidence,
        "topics": topics or ["cs.CL"],
        "source_papers": source_papers or ["p1"],
        "source_claims": [],
        "relevance": relevance,
        "timing_score": timing_score,
        "metadata": {},
    }


class TestSynthesizeReturnType:
    def test_returns_list(self):
        signals = [_make_signal()]
        result = synthesize(signals)
        assert isinstance(result, list)

    def test_returns_list_of_dicts(self):
        signals = [_make_signal()]
        result = synthesize(signals)
        for opp in result:
            assert isinstance(opp, dict)


class TestOpportunitySchema:
    def test_required_fields(self):
        signals = [_make_signal()]
        result = synthesize(signals)
        assert len(result) > 0
        for opp in result:
            assert "title" in opp
            assert "thesis" in opp
            assert "composite_score" in opp
            assert "signal_ids" in opp
            assert "detectors_hit" in opp
            assert "topics" in opp
            assert "portfolio_fit" in opp
            assert "timing_urgency" in opp
            assert "rationale" in opp
            assert "status" in opp

    def test_composite_score_is_numeric(self):
        signals = [_make_signal()]
        result = synthesize(signals)
        for opp in result:
            assert isinstance(opp["composite_score"], (int, float))

    def test_composite_score_range(self):
        signals = [_make_signal(confidence=1.0, relevance=1.0, timing_score=1.0)]
        result = synthesize(signals)
        for opp in result:
            assert 0 <= opp["composite_score"] <= 100


class TestClustering:
    def test_same_topic_signals_cluster(self):
        """Signals with overlapping topics should merge into fewer opportunities."""
        signals = [
            _make_signal(detector="gap", topics=["cs.CL", "reasoning"]),
            _make_signal(detector="trend", signal_type="accelerating_no_theory",
                         topics=["cs.CL", "reasoning"]),
        ]
        result = synthesize(signals)
        # Both signals share topics, so they should cluster into 1 opportunity
        assert len(result) == 1
        assert len(result[0]["detectors_hit"]) == 2

    def test_different_topic_signals_separate(self):
        """Signals with non-overlapping topics should produce separate opportunities."""
        signals = [
            _make_signal(detector="gap", topics=["cs.CL"]),
            _make_signal(detector="trend", signal_type="accelerating_no_theory",
                         topics=["cs.CV"]),
        ]
        result = synthesize(signals)
        assert len(result) == 2

    def test_cross_detector_scoring(self):
        """Opportunities hit by multiple detectors should list all of them."""
        multi = synthesize([
            _make_signal(detector="gap", topics=["cs.CL"], confidence=0.5),
            _make_signal(detector="trend", signal_type="accel",
                         topics=["cs.CL"], confidence=0.5),
        ])
        # Both detectors should be listed in the clustered opportunity
        assert len(multi) == 1
        assert set(multi[0]["detectors_hit"]) == {"gap", "trend"}

    def test_multi_signal_cluster_has_more_signal_ids(self):
        """Cluster with 2 signals should have 2 signal_ids."""
        result = synthesize([
            _make_signal(detector="gap", topics=["cs.CL"], confidence=0.5),
            _make_signal(detector="trend", signal_type="accel",
                         topics=["cs.CL"], confidence=0.5),
        ])
        assert len(result[0]["signal_ids"]) == 2


class TestDeduplication:
    def test_high_overlap_merged(self):
        """Opportunities with >0.5 topic overlap should be merged."""
        signals = [
            _make_signal(detector="gap", topics=["cs.CL", "reasoning", "language"]),
            _make_signal(detector="trend", topics=["cs.CV", "vision"]),
            _make_signal(detector="contrarian", topics=["cs.CL", "reasoning", "language", "models"]),
        ]
        result = synthesize(signals)
        # gap and contrarian share high topic overlap -> should merge
        assert len(result) <= 2


class TestSorting:
    def test_sorted_by_composite_score_desc(self):
        signals = [
            _make_signal(detector="gap", topics=["cs.CL"], confidence=0.3),
            _make_signal(detector="trend", topics=["cs.CV"], confidence=0.9),
        ]
        result = synthesize(signals)
        scores = [opp["composite_score"] for opp in result]
        assert scores == sorted(scores, reverse=True)


class TestMaxResults:
    def test_max_10_opportunities(self):
        signals = [
            _make_signal(detector="gap", topics=[f"topic_{i}"], confidence=0.5 + i * 0.01)
            for i in range(20)
        ]
        result = synthesize(signals)
        assert len(result) <= 10


class TestEdgeCases:
    def test_empty_input(self):
        assert synthesize([]) == []

    def test_single_signal(self):
        signals = [_make_signal()]
        result = synthesize(signals)
        assert len(result) == 1

    def test_signal_with_no_topics(self):
        signals = [_make_signal(topics=[])]
        result = synthesize(signals)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_signal_with_empty_description(self):
        signals = [_make_signal(description="")]
        result = synthesize(signals)
        assert isinstance(result, list)


class TestIntegrationWithDetectors:
    """Test synthesize with signals from the actual gap detector."""

    def test_synthesize_gap_signals(self, synthetic_papers):
        from scripts.compass.gap_detector import detect as gap_detect
        signals = gap_detect(synthetic_papers)
        if signals:
            result = synthesize(signals)
            assert isinstance(result, list)
            assert len(result) > 0
            for opp in result:
                assert opp["composite_score"] >= 0

    def test_synthesize_multi_detector(self, synthetic_papers):
        """Combine signals from gap and frontier detectors."""
        from scripts.compass.gap_detector import detect as gap_detect
        from scripts.compass.frontier_scanner import detect as frontier_detect

        all_signals = gap_detect(synthetic_papers) + frontier_detect(synthetic_papers)
        if all_signals:
            result = synthesize(all_signals)
            assert isinstance(result, list)
            assert len(result) > 0
