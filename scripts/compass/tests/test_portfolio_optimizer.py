"""Tests for the portfolio optimizer module."""

import os
from pathlib import Path

from scripts.compass.portfolio_optimizer import detect


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
        valid_types = {"portfolio_gap", "portfolio_deepening", "citation_opportunity", "claim_strengthening"}
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
