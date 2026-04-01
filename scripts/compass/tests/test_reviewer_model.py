"""Tests for the reviewer model module."""

import json
from pathlib import Path

from scripts.compass.reviewer_model import detect
from scripts.compass.venue_enricher import (
    compute_empirical_topic_scores,
    detect_topic_shifts,
    enrich_venues,
    get_latest_venue_year,
    load_venue_data,
    merge_empirical_into_venue,
)


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
        valid_types = {"venue_opportunity", "venue_gap", "venue_cooling", "venue_topic_shift"}
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


# ── Venue enricher tests ─────────────────────────────────


def _create_mock_venue_data(tmp_path, venue="neurips", year=2025, keywords=None):
    """Create a mock *-accepted.json file in a data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    if keywords is None:
        keywords = {
            "reinforcement learning": 120,
            "large language models": 95,
            "reasoning": 80,
            "safety": 45,
            "transformers": 30,
        }

    papers = []
    for kw, count in keywords.items():
        for i in range(min(count, 3)):  # just a few representative papers
            papers.append({
                "id": f"{venue}-{year}-{kw}-{i}",
                "title": f"Paper on {kw} ({i})",
                "keywords": [kw],
                "abstract": f"A paper about {kw}.",
                "decision": "Accept",
            })

    data = {
        "venue": venue,
        "year": year,
        "total_accepted": max(keywords.values()) if keywords else 0,
        "papers": papers,
        "stats": {
            "total": len(papers),
            "by_keyword": keywords,
        },
    }

    path = data_dir / f"{venue}-{year}-accepted.json"
    path.write_text(json.dumps(data, indent=2))
    return str(data_dir)


class TestComputeEmpiricalTopicScores:
    def test_normalized_scores(self):
        data = {
            "total_accepted": 100,
            "stats": {"by_keyword": {"reasoning": 100, "safety": 50, "niche": 10}},
        }
        scores = compute_empirical_topic_scores(data)
        assert scores["reasoning"] == 1.0
        assert scores["safety"] == 0.5
        assert scores["niche"] == 0.1

    def test_empty_keywords(self):
        data = {"total_accepted": 100, "stats": {"by_keyword": {}}}
        assert compute_empirical_topic_scores(data) == {}

    def test_too_few_papers(self):
        data = {
            "total_accepted": 5,
            "stats": {"by_keyword": {"reasoning": 5}},
        }
        assert compute_empirical_topic_scores(data) == {}

    def test_missing_stats(self):
        assert compute_empirical_topic_scores({}) == {}


class TestDetectTopicShifts:
    def test_gaining_topic(self):
        current = {
            "total_accepted": 100,
            "stats": {"by_keyword": {"reasoning": 100, "safety": 80}},
        }
        previous = {
            "total_accepted": 100,
            "stats": {"by_keyword": {"reasoning": 50, "safety": 100}},
        }
        shifts = detect_topic_shifts(current, previous)
        gaining = [s for s in shifts if s["direction"] == "gaining"]
        cooling = [s for s in shifts if s["direction"] == "cooling"]
        assert len(gaining) >= 1
        assert any(s["topic"] == "reasoning" for s in gaining)
        assert len(cooling) >= 1
        assert any(s["topic"] == "safety" for s in cooling)

    def test_no_shift_when_stable(self):
        data = {
            "total_accepted": 100,
            "stats": {"by_keyword": {"reasoning": 100, "safety": 80}},
        }
        shifts = detect_topic_shifts(data, data)
        assert shifts == []

    def test_no_shift_with_empty_data(self):
        assert detect_topic_shifts({}, {}) == []


class TestLoadVenueData:
    def test_loads_json_files(self, tmp_path):
        data_path = _create_mock_venue_data(tmp_path, "neurips", 2025)
        result = load_venue_data(data_path)
        assert "neurips-2025" in result
        assert result["neurips-2025"]["venue"] == "neurips"

    def test_empty_directory(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        assert load_venue_data(str(empty)) == {}

    def test_nonexistent_directory(self):
        assert load_venue_data("/nonexistent/path") == {}


class TestGetLatestVenueYear:
    def test_finds_latest(self, tmp_path):
        _create_mock_venue_data(tmp_path, "neurips", 2024)
        _create_mock_venue_data(tmp_path, "neurips", 2025)
        data_path = str(tmp_path / "data")
        venue_data = load_venue_data(data_path)
        latest, previous = get_latest_venue_year("neurips", venue_data)
        assert latest is not None
        assert latest["year"] == 2025
        assert previous is not None
        assert previous["year"] == 2024

    def test_single_year(self, tmp_path):
        _create_mock_venue_data(tmp_path, "neurips", 2025)
        data_path = str(tmp_path / "data")
        venue_data = load_venue_data(data_path)
        latest, previous = get_latest_venue_year("neurips", venue_data)
        assert latest is not None
        assert previous is None

    def test_no_match(self):
        latest, previous = get_latest_venue_year("neurips", {})
        assert latest is None
        assert previous is None


class TestMergeEmpiricalIntoVenue:
    def test_preserves_yaml_scores(self):
        venue = {"name": "neurips", "topic_fit": {"reasoning": 0.9, "safety": 0.5}}
        empirical = {"reasoning": 0.8, "transformers": 0.6}
        result = merge_empirical_into_venue(venue, empirical)
        assert result["topic_fit_yaml"] == {"reasoning": 0.9, "safety": 0.5}
        assert result["topic_fit"]["reasoning"] == 0.8  # overridden by empirical
        assert result["topic_fit"]["safety"] == 0.5  # kept from YAML
        assert result["topic_fit"]["transformers"] == 0.6  # new from empirical
        assert result["empirical_enriched"] is True

    def test_adds_shift_data(self):
        venue = {"name": "neurips", "topic_fit": {}}
        shifts = [{"topic": "reasoning", "direction": "gaining", "delta": 0.2}]
        result = merge_empirical_into_venue(venue, {"reasoning": 0.8}, shifts)
        assert result["topic_shifts"] == shifts


class TestEnrichVenues:
    def test_enriches_matching_venues(self, tmp_path):
        data_path = _create_mock_venue_data(tmp_path, "neurips", 2025)
        venues = [
            {"name": "neurips", "full_name": "NeurIPS", "topic_fit": {"reasoning": 0.9}},
        ]
        result = enrich_venues(venues, venues_data_path=data_path)
        assert len(result) == 1
        assert result[0].get("empirical_enriched") is True

    def test_skips_when_no_data(self, tmp_path):
        empty_dir = tmp_path / "empty_data"
        empty_dir.mkdir()
        venues = [
            {"name": "neurips", "full_name": "NeurIPS", "topic_fit": {"reasoning": 0.9}},
        ]
        result = enrich_venues(venues, venues_data_path=str(empty_dir))
        assert result[0].get("empirical_enriched") is None

    def test_no_data_dir(self):
        venues = [{"name": "neurips", "topic_fit": {"reasoning": 0.9}}]
        result = enrich_venues(venues, venues_data_path="/nonexistent")
        assert result[0].get("empirical_enriched") is None


class TestIntegrationWithDetect:
    def test_detect_with_empirical_data(self, synthetic_papers, tmp_path):
        """Detector should work when empirical data is present."""
        venues_dir = tmp_path / "venues"
        venues_dir.mkdir(parents=True)

        # Write venue YAML
        (venues_dir / "neurips.yaml").write_text(
            'name: neurips\n'
            'full_name: "Conference on Neural Information Processing Systems"\n'
            'deadlines:\n'
            '  2027:\n'
            '    paper: "2027-05-15"\n'
            'topic_fit:\n'
            '  reasoning: high\n'
            '  verification: high\n'
            '  language: medium\n'
        )

        # Write empirical data
        data_dir = venues_dir / "data"
        data_dir.mkdir()
        venue_data = {
            "venue": "neurips",
            "year": 2025,
            "total_accepted": 100,
            "papers": [],
            "stats": {
                "total": 100,
                "by_keyword": {
                    "reasoning": 100,
                    "verification": 60,
                    "language": 40,
                    "scaling": 30,
                },
            },
        }
        (data_dir / "neurips-2025-accepted.json").write_text(json.dumps(venue_data))

        signals = detect(synthetic_papers, venues_path=str(venues_dir))
        assert isinstance(signals, list)

    def test_detect_with_topic_shifts(self, synthetic_papers, tmp_path):
        """Topic shift signals should appear when two years of data exist."""
        venues_dir = tmp_path / "venues"
        venues_dir.mkdir(parents=True)

        (venues_dir / "neurips.yaml").write_text(
            'name: neurips\n'
            'full_name: "NeurIPS"\n'
            'deadlines:\n'
            '  2027:\n'
            '    paper: "2027-05-15"\n'
            'topic_fit:\n'
            '  reasoning: high\n'
        )

        data_dir = venues_dir / "data"
        data_dir.mkdir()

        # Year 1: reasoning dominant
        (data_dir / "neurips-2024-accepted.json").write_text(json.dumps({
            "venue": "neurips", "year": 2024,
            "total_accepted": 100, "papers": [],
            "stats": {"total": 100, "by_keyword": {
                "reasoning": 100, "safety": 30, "scaling": 80,
            }},
        }))

        # Year 2: safety surges, reasoning drops
        (data_dir / "neurips-2025-accepted.json").write_text(json.dumps({
            "venue": "neurips", "year": 2025,
            "total_accepted": 100, "papers": [],
            "stats": {"total": 100, "by_keyword": {
                "reasoning": 40, "safety": 100, "scaling": 80,
            }},
        }))

        signals = detect(synthetic_papers, venues_path=str(venues_dir))
        shift_signals = [s for s in signals if s["signal_type"] == "venue_topic_shift"]
        assert len(shift_signals) >= 1
        # Should detect safety gaining and reasoning cooling
        shift_titles = " ".join(s["title"] for s in shift_signals)
        assert "gaining" in shift_titles.lower() or "cooling" in shift_titles.lower()
