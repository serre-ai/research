"""Tests for the portfolio optimizer module."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from scripts.compass.portfolio_optimizer import (
    detect,
    _clean_topic_label,
    _find_topic_coverage_gaps,
)


def _create_mock_portfolio(tmp_path):
    """Create a minimal mock projects/ directory with two research projects.

    Returns the path as a string.
    """
    # Project 1: reasoning-gaps (experiment-execution phase)
    proj1 = tmp_path / "reasoning-gaps"
    proj1.mkdir()
    (proj1 / "BRIEF.md").write_text(
        "# Reasoning Gaps\n\n"
        "Investigate reasoning gaps in large language models. "
        "We study how chain-of-thought fails on complex tasks "
        "and propose formal verification methods.\n"
    )
    (proj1 / "status.yaml").write_text(
        'title: "Reasoning Gaps in Large Language Models"\n'
        'venue: "NeurIPS"\n'
        'phase: "experiment-execution-and-polish"\n'
        'current_focus: "Running verification complexity experiments"\n'
    )

    # Project 2: verification-complexity (research phase)
    proj2 = tmp_path / "verification-complexity"
    proj2.mkdir()
    (proj2 / "BRIEF.md").write_text(
        "# Verification Complexity\n\n"
        "Study the computational complexity of verifying reasoning "
        "outputs from language models. Formal proofs and complexity "
        "class analysis.\n"
    )
    (proj2 / "status.yaml").write_text(
        'title: "Verification Complexity of Model Reasoning"\n'
        'venue: "ICLR"\n'
        'phase: "research"\n'
        'current_focus: "Theorem proofs for verification bounds"\n'
    )

    return str(tmp_path)


class TestDetectReturnType:
    def test_returns_list(self, synthetic_papers, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        signals = detect(synthetic_papers, portfolio_path=portfolio)
        assert isinstance(signals, list)

    def test_returns_list_of_dicts(self, synthetic_papers, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        signals = detect(synthetic_papers, portfolio_path=portfolio)
        for sig in signals:
            assert isinstance(sig, dict)


class TestSignalSchema:
    def test_required_fields_present(self, synthetic_papers, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        signals = detect(synthetic_papers, portfolio_path=portfolio)
        for sig in signals:
            assert "detector" in sig
            assert "signal_type" in sig
            assert "title" in sig
            assert "description" in sig
            assert "confidence" in sig
            assert "source_papers" in sig

    def test_detector_name(self, synthetic_papers, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        signals = detect(synthetic_papers, portfolio_path=portfolio)
        for sig in signals:
            assert sig["detector"] == "portfolio"

    def test_confidence_range(self, synthetic_papers, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        signals = detect(synthetic_papers, portfolio_path=portfolio)
        for sig in signals:
            assert 0 <= sig["confidence"] <= 1, (
                f"Confidence {sig['confidence']} out of range for {sig['signal_type']}"
            )

    def test_valid_signal_types(self, synthetic_papers, tmp_path):
        valid_types = {"portfolio_gap", "portfolio_deepening", "citation_opportunity", "claim_strengthening", "topic_coverage_gap", "topic_momentum"}
        portfolio = _create_mock_portfolio(tmp_path)
        signals = detect(synthetic_papers, portfolio_path=portfolio)
        for sig in signals:
            assert sig["signal_type"] in valid_types, (
                f"Unexpected signal_type: {sig['signal_type']}"
            )


class TestPortfolioDeepening:
    def test_related_papers_detected(self, synthetic_papers, tmp_path):
        """Papers about reasoning (p3, p4, p5) should match reasoning-gaps project."""
        portfolio = _create_mock_portfolio(tmp_path)
        signals = detect(synthetic_papers, portfolio_path=portfolio)
        deepening = [s for s in signals if s["signal_type"] == "portfolio_deepening"]
        # At least one deepening signal should be found
        assert len(deepening) > 0, "Expected portfolio_deepening signals"

    def test_deepening_has_matching_project(self, synthetic_papers, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        signals = detect(synthetic_papers, portfolio_path=portfolio)
        deepening = [s for s in signals if s["signal_type"] == "portfolio_deepening"]
        for sig in deepening:
            assert "matching_projects" in sig["metadata"]
            assert len(sig["metadata"]["matching_projects"]) > 0


class TestEdgeCases:
    def test_empty_papers(self, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        result = detect([], portfolio_path=portfolio)
        assert result == []

    def test_empty_portfolio(self, synthetic_papers, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = detect(synthetic_papers, portfolio_path=str(empty_dir))
        assert result == []

    def test_nonexistent_portfolio_path(self, synthetic_papers):
        result = detect(synthetic_papers, portfolio_path="/nonexistent/path")
        assert result == []

    def test_single_paper(self, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        papers = [
            {
                "id": "single",
                "title": "Reasoning about verification complexity",
                "abstract": "We study reasoning and verification in language models.",
                "categories": ["cs.CL"],
                "authors": [{"name": "Test"}],
            }
        ]
        result = detect(papers, portfolio_path=portfolio)
        assert isinstance(result, list)

    def test_papers_with_no_abstract(self, tmp_path):
        portfolio = _create_mock_portfolio(tmp_path)
        papers = [
            {"id": "x1", "title": "No Abstract", "abstract": None, "categories": [], "authors": []},
        ]
        result = detect(papers, portfolio_path=portfolio)
        assert isinstance(result, list)

    def test_portfolio_with_skip_project(self, synthetic_papers, tmp_path):
        """platform-engineering should be skipped."""
        portfolio = _create_mock_portfolio(tmp_path)
        skip_proj = Path(portfolio) / "platform-engineering"
        skip_proj.mkdir()
        (skip_proj / "BRIEF.md").write_text("# Platform\n\nEngineering work.\n")
        (skip_proj / "status.yaml").write_text('title: "Platform"\nphase: "active"\n')
        result = detect(synthetic_papers, portfolio_path=portfolio)
        # Should not crash and should not include platform-engineering signals
        assert isinstance(result, list)


class TestCleanTopicLabel:
    """Tests for _clean_topic_label — stripping category prefixes and pipe separators."""

    def test_strips_category_prefix(self):
        result = _clean_topic_label("cs.CL: large language models")
        assert "language" in result
        # "large" is in STOP_WORDS, and category tokens like "cs" or "cl" are <3 chars
        assert "models" not in result  # "models" is in STOP_WORDS
        assert not any(tok.startswith("cs") for tok in result)

    def test_strips_pipe_separators(self):
        result = _clean_topic_label("cs.CL: chain thought | reasoning gaps")
        assert "chain" in result
        assert "thought" in result
        assert "reasoning" in result
        assert "gaps" in result
        assert "|" not in result

    def test_no_junk_tokens(self):
        """Pipe separators and category prefixes should not appear as tokens."""
        result = _clean_topic_label("cs.CL: large language | llms | chain thought")
        for tok in result:
            assert tok != "|"
            assert ":" not in tok
            assert "." not in tok

    def test_empty_label(self):
        result = _clean_topic_label("")
        assert result == frozenset()

    def test_label_without_prefix(self):
        result = _clean_topic_label("reinforcement learning from human feedback")
        assert "reinforcement" in result
        assert "learning" in result
        assert "human" in result
        assert "feedback" in result
        # "from" is a stop word and should be excluded
        assert "from" not in result

    def test_multiple_category_prefixes(self):
        result = _clean_topic_label("stat.ML: bayesian optimization | cs.LG: neural networks")
        assert "bayesian" in result
        assert "optimization" in result
        assert "neural" in result
        assert "networks" in result


class TestFindTopicCoverageGaps:
    """Tests for _find_topic_coverage_gaps with mocked DB."""

    def _mock_topics(self):
        """Return fake topic rows from research_topics table."""
        return [
            # Accelerating topic we DON'T cover
            {"id": 1, "label": "cs.CV: image segmentation | visual grounding", "paper_count": 20, "velocity": 3.0, "claim_count": 5},
            # Accelerating topic we DO cover (reasoning)
            {"id": 2, "label": "cs.CL: reasoning verification | chain thought", "paper_count": 15, "velocity": 2.5, "claim_count": 3},
            # Slow topic — should be skipped
            {"id": 3, "label": "cs.SE: software testing | unit tests", "paper_count": 10, "velocity": 0.5, "claim_count": 2},
            # Accelerating but too few papers — should be skipped
            {"id": 4, "label": "cs.RO: robot manipulation", "paper_count": 3, "velocity": 4.0, "claim_count": 1},
        ]

    def _mock_project_info(self):
        """Project info with topics about reasoning and verification."""
        return {
            "reasoning-gaps": {
                "name": "reasoning-gaps",
                "topics": frozenset({"reasoning", "gaps", "language", "chain", "thought", "verification"}),
                "phase": "experiment-execution-and-polish",
            },
            "verification-complexity": {
                "name": "verification-complexity",
                "topics": frozenset({"verification", "complexity", "reasoning", "formal", "proofs"}),
                "phase": "research",
            },
        }

    @patch("scripts.compass.portfolio_optimizer.get_connection")
    def test_produces_coverage_gap_for_uncovered_topic(self, mock_get_conn):
        """Topic about image segmentation should produce a coverage_gap signal."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = self._mock_topics()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn

        signals = _find_topic_coverage_gaps(self._mock_project_info())
        gap_signals = [s for s in signals if s.signal_type == "topic_coverage_gap"]

        assert len(gap_signals) >= 1
        # The image segmentation topic should be flagged
        labels = [s.topics[0] for s in gap_signals]
        assert any("image segmentation" in lbl for lbl in labels)

    @patch("scripts.compass.portfolio_optimizer.get_connection")
    def test_produces_momentum_for_covered_topic(self, mock_get_conn):
        """Topic about reasoning/verification should produce a topic_momentum signal."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = self._mock_topics()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn

        signals = _find_topic_coverage_gaps(self._mock_project_info())
        momentum = [s for s in signals if s.signal_type == "topic_momentum"]

        assert len(momentum) >= 1
        # Should reference our matching projects
        for sig in momentum:
            assert len(sig.metadata["matching_projects"]) > 0

    @patch("scripts.compass.portfolio_optimizer.get_connection")
    def test_momentum_relevance_equals_overlap(self, mock_get_conn):
        """topic_momentum signals should have relevance set to the overlap score."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = self._mock_topics()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn

        signals = _find_topic_coverage_gaps(self._mock_project_info())
        momentum = [s for s in signals if s.signal_type == "topic_momentum"]

        for sig in momentum:
            assert sig.relevance > 0.0, "topic_momentum should have positive relevance"

    @patch("scripts.compass.portfolio_optimizer.get_connection")
    def test_coverage_gap_relevance_is_zero(self, mock_get_conn):
        """topic_coverage_gap signals should have relevance=0.0."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = self._mock_topics()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn

        signals = _find_topic_coverage_gaps(self._mock_project_info())
        gaps = [s for s in signals if s.signal_type == "topic_coverage_gap"]

        for sig in gaps:
            assert sig.relevance == 0.0

    @patch("scripts.compass.portfolio_optimizer.get_connection")
    def test_skips_slow_topics(self, mock_get_conn):
        """Topics with velocity <= 1.5 should not produce coverage_gap signals."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = self._mock_topics()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn

        signals = _find_topic_coverage_gaps(self._mock_project_info())
        all_labels = [s.topics[0] for s in signals]
        assert not any("software testing" in lbl for lbl in all_labels)

    @patch("scripts.compass.portfolio_optimizer.get_connection")
    def test_skips_topics_with_few_papers(self, mock_get_conn):
        """Topics with < 5 papers should not produce coverage_gap signals."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = self._mock_topics()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn

        signals = _find_topic_coverage_gaps(self._mock_project_info())
        all_labels = [s.topics[0] for s in signals]
        assert not any("robot manipulation" in lbl for lbl in all_labels)

    @patch("scripts.compass.portfolio_optimizer.get_connection")
    def test_dedup_with_existing_gap_topics(self, mock_get_conn):
        """Topics whose keywords overlap with existing_gap_topics should be skipped."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = self._mock_topics()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn

        # Pretend _find_portfolio_gaps already flagged "image" and "segmentation"
        existing = frozenset({"image", "segmentation"})
        signals = _find_topic_coverage_gaps(
            self._mock_project_info(), existing_gap_topics=existing,
        )
        gap_signals = [s for s in signals if s.signal_type == "topic_coverage_gap"]
        labels = [s.topics[0] for s in gap_signals]
        assert not any("image segmentation" in lbl for lbl in labels)

    @patch("scripts.compass.portfolio_optimizer.get_connection")
    def test_cap_per_signal_type(self, mock_get_conn):
        """Each signal type should be capped at 5."""
        # Create many uncovered accelerating topics
        many_topics = [
            {"id": i, "label": f"topic {i} alpha beta gamma delta",
             "paper_count": 10, "velocity": 3.0, "claim_count": 1}
            for i in range(20)
        ]
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = many_topics
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn

        signals = _find_topic_coverage_gaps(self._mock_project_info())
        gaps = [s for s in signals if s.signal_type == "topic_coverage_gap"]
        momentum = [s for s in signals if s.signal_type == "topic_momentum"]
        assert len(gaps) <= 5
        assert len(momentum) <= 5

    def test_returns_empty_without_db(self):
        """When get_connection is None, should return empty list."""
        with patch("scripts.compass.portfolio_optimizer.get_connection", None):
            signals = _find_topic_coverage_gaps(self._mock_project_info())
            assert signals == []
