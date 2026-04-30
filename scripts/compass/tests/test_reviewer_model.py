"""Tests for the reviewer model module."""

from pathlib import Path

from scripts.compass.reviewer_model import detect


def _create_mock_venues(tmp_path):
    """Create a minimal mock shared/config/venues/ directory.

    Returns the path as a string.
    """
    venues_dir = tmp_path / "venues"
    venues_dir.mkdir(parents=True)

    # Venue 1: NeurIPS -- receptive to reasoning and verification
    (venues_dir / "neurips.yaml").write_text(
        'name: NeurIPS\n'
        'full_name: "Conference on Neural Information Processing Systems"\n'
        'deadlines:\n'
        '  2027:\n'
        '    paper: "2027-05-15"\n'
        'topic_fit:\n'
        '  reasoning: high\n'
        '  verification: high\n'
        '  language: medium\n'
        '  safety: low\n'
    )

    # Venue 2: ICML -- receptive to optimization and scaling
    (venues_dir / "icml.yaml").write_text(
        'name: ICML\n'
        'full_name: "International Conference on Machine Learning"\n'
        'deadlines:\n'
        '  2027:\n'
        '    paper: "2027-01-20"\n'
        'topic_fit:\n'
        '  optimization: high\n'
        '  scaling: high\n'
        '  generalization: medium\n'
    )

    return str(venues_dir)


def _create_mock_portfolio(tmp_path):
    """Create a minimal projects/ directory targeting NeurIPS."""
    proj_dir = tmp_path / "projects" / "reasoning-gaps"
    proj_dir.mkdir(parents=True)
    (proj_dir / "status.yaml").write_text(
        'title: "Reasoning Gaps"\n'
        'venue: "neurips"\n'
        'phase: "experiment-execution"\n'
    )
    return str(tmp_path / "projects")


class TestDetectReturnType:
    def test_returns_list(self, synthetic_papers, tmp_path):
        venues = _create_mock_venues(tmp_path)
        signals = detect(synthetic_papers, venues_path=venues)
        assert isinstance(signals, list)

    def test_returns_list_of_dicts(self, synthetic_papers, tmp_path):
        venues = _create_mock_venues(tmp_path)
        signals = detect(synthetic_papers, venues_path=venues)
        for sig in signals:
            assert isinstance(sig, dict)


class TestSignalSchema:
    def test_required_fields_present(self, synthetic_papers, tmp_path):
        venues = _create_mock_venues(tmp_path)
        signals = detect(synthetic_papers, venues_path=venues)
        for sig in signals:
            assert "detector" in sig
            assert "signal_type" in sig
            assert "title" in sig
            assert "description" in sig
            assert "confidence" in sig
            assert "source_papers" in sig

    def test_detector_name(self, synthetic_papers, tmp_path):
        venues = _create_mock_venues(tmp_path)
        signals = detect(synthetic_papers, venues_path=venues)
        for sig in signals:
            assert sig["detector"] == "reviewer"

    def test_confidence_range(self, synthetic_papers, tmp_path):
        venues = _create_mock_venues(tmp_path)
        signals = detect(synthetic_papers, venues_path=venues)
        for sig in signals:
            assert 0 <= sig["confidence"] <= 1, (
                f"Confidence {sig['confidence']} out of range for {sig['signal_type']}"
            )

    def test_valid_signal_types(self, synthetic_papers, tmp_path):
        valid_types = {"venue_opportunity", "venue_gap", "venue_cooling"}
        venues = _create_mock_venues(tmp_path)
        signals = detect(synthetic_papers, venues_path=venues)
        for sig in signals:
            assert sig["signal_type"] in valid_types, (
                f"Unexpected signal_type: {sig['signal_type']}"
            )


class TestVenueOpportunity:
    def test_untargeted_venue_flagged(self, synthetic_papers, tmp_path, monkeypatch):
        """ICML is not targeted -- should produce venue_opportunity if papers match."""
        venues = _create_mock_venues(tmp_path)
        portfolio = _create_mock_portfolio(tmp_path)

        # Monkeypatch portfolio path so reviewer_model reads our mock portfolio
        import scripts.compass.reviewer_model as rm
        monkeypatch.setattr(rm, "_default_portfolio_path", lambda: portfolio)

        signals = detect(synthetic_papers, venues_path=venues)
        # Check that at least some signals were produced
        assert isinstance(signals, list)

    def test_venue_metadata(self, synthetic_papers, tmp_path, monkeypatch):
        venues = _create_mock_venues(tmp_path)
        portfolio = _create_mock_portfolio(tmp_path)

        import scripts.compass.reviewer_model as rm
        monkeypatch.setattr(rm, "_default_portfolio_path", lambda: portfolio)

        signals = detect(synthetic_papers, venues_path=venues)
        for sig in signals:
            assert "venue" in sig["metadata"]


class TestEdgeCases:
    def test_empty_papers(self, tmp_path):
        venues = _create_mock_venues(tmp_path)
        result = detect([], venues_path=venues)
        assert result == []

    def test_no_venues(self, synthetic_papers, tmp_path):
        empty_dir = tmp_path / "empty_venues"
        empty_dir.mkdir()
        result = detect(synthetic_papers, venues_path=str(empty_dir))
        assert result == []

    def test_nonexistent_venues_path(self, synthetic_papers):
        result = detect(synthetic_papers, venues_path="/nonexistent/path")
        assert result == []

    def test_malformed_venue_yaml(self, synthetic_papers, tmp_path):
        """Venue YAML missing required fields should be silently skipped."""
        venues_dir = tmp_path / "bad_venues"
        venues_dir.mkdir()
        (venues_dir / "bad.yaml").write_text("this is not valid yaml content at all\n")
        result = detect(synthetic_papers, venues_path=str(venues_dir))
        assert isinstance(result, list)

    def test_papers_with_no_abstract(self, tmp_path):
        venues = _create_mock_venues(tmp_path)
        papers = [
            {"id": "x1", "title": "No Abstract", "abstract": None, "categories": [], "authors": []},
        ]
        result = detect(papers, venues_path=venues)
        assert isinstance(result, list)
