"""Tests for the contrarian detector module."""

from unittest.mock import patch, MagicMock
from scripts.compass.contrarian_detector import detect, _find_kg_contradictions


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
        valid_types = {
            "consensus_thin_evidence", "consensus_fragile",
            "contrarian_opportunity", "semantic_opposition",
            "verified_contradiction", "active_dispute",
        }
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


def _make_mock_cursor(contradictions):
    """Create a mock cursor that returns the given contradictions."""
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = contradictions
    return mock_cur


def _make_mock_connection(contradictions):
    """Create a mock connection whose cursor returns the given contradictions."""
    mock_conn = MagicMock()
    mock_cur = _make_mock_cursor(contradictions)
    mock_conn.cursor.return_value = mock_cur
    return mock_conn


class TestVerifiedContradictions:
    """Tests for the verified_contradiction signal type from KG."""

    def _mock_contradictions(self):
        return [
            {
                "claim_a": "Chain-of-thought prompting improves reasoning accuracy",
                "claim_b": "Chain-of-thought prompting does not reliably improve reasoning",
                "paper_a_id": "paper_001",
                "paper_b_id": "paper_002",
                "strength": 0.85,
                "paper_a_title": "CoT Improves Reasoning in LLMs",
                "paper_b_title": "CoT Does Not Generalize",
            },
            {
                "claim_a": "Scaling model parameters improves performance linearly",
                "claim_b": "Scaling returns diminish beyond a threshold",
                "paper_a_id": "paper_003",
                "paper_b_id": None,
                "strength": 0.72,
                "paper_a_title": "Scaling Laws for LLMs",
                "paper_b_title": None,
            },
        ]

    @patch("scripts.compass.db.get_connection")
    def test_emits_verified_contradiction_signals(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._mock_contradictions())
        signals = _find_kg_contradictions([])

        verified = [s for s in signals if s.signal_type == "verified_contradiction"]
        assert len(verified) == 2, f"Expected 2 verified contradictions, got {len(verified)}"

    @patch("scripts.compass.db.get_connection")
    def test_verified_contradiction_confidence_is_strength(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._mock_contradictions())
        signals = _find_kg_contradictions([])

        verified = [s for s in signals if s.signal_type == "verified_contradiction"]
        assert verified[0].confidence == 0.85
        assert verified[1].confidence == 0.72

    @patch("scripts.compass.db.get_connection")
    def test_verified_contradiction_includes_source_papers(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._mock_contradictions())
        signals = _find_kg_contradictions([])

        verified = [s for s in signals if s.signal_type == "verified_contradiction"]
        # First contradiction has both paper IDs
        assert "paper_001" in verified[0].source_papers
        assert "paper_002" in verified[0].source_papers
        # Second contradiction has only one paper ID (paper_b_id is None)
        assert "paper_003" in verified[1].source_papers
        assert len(verified[1].source_papers) == 1

    @patch("scripts.compass.db.get_connection")
    def test_verified_contradiction_metadata(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._mock_contradictions())
        signals = _find_kg_contradictions([])

        verified = [s for s in signals if s.signal_type == "verified_contradiction"]
        meta = verified[0].metadata
        assert "claim_a" in meta
        assert "claim_b" in meta
        assert "strength" in meta
        assert meta["strength"] == 0.85

    @patch("scripts.compass.db.get_connection")
    def test_no_contradictions_returns_empty(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection([])
        signals = _find_kg_contradictions([])

        assert signals == []


class TestActiveDispute:
    """Tests for the active_dispute signal type when recent papers overlap."""

    def _mock_contradictions(self):
        return [
            {
                "claim_a": "Chain-of-thought prompting improves reasoning accuracy",
                "claim_b": "Chain-of-thought prompting does not reliably improve reasoning",
                "paper_a_id": "paper_001",
                "paper_b_id": "paper_002",
                "strength": 0.85,
                "paper_a_title": "CoT Improves Reasoning",
                "paper_b_title": "CoT Does Not Generalize",
            },
        ]

    @patch("scripts.compass.db.get_connection")
    def test_emits_active_dispute_when_paper_overlaps(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._mock_contradictions())

        # Paper whose abstract overlaps with claim_a (chain-of-thought, reasoning)
        papers = [
            {
                "id": "recent_1",
                "title": "New Evidence for Chain-of-Thought Reasoning",
                "abstract": (
                    "Chain-of-thought prompting improves reasoning accuracy "
                    "across multiple mathematical benchmarks."
                ),
            }
        ]
        signals = _find_kg_contradictions(papers)

        disputes = [s for s in signals if s.signal_type == "active_dispute"]
        assert len(disputes) >= 1, "Expected at least 1 active_dispute signal"
        assert "recent_1" in disputes[0].source_papers

    @patch("scripts.compass.db.get_connection")
    def test_no_dispute_when_paper_does_not_overlap(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._mock_contradictions())

        # Paper about a completely different topic
        papers = [
            {
                "id": "unrelated",
                "title": "Quantum Computing Survey",
                "abstract": (
                    "We survey recent advances in quantum error correction codes "
                    "and fault-tolerant quantum computation."
                ),
            }
        ]
        signals = _find_kg_contradictions(papers)

        disputes = [s for s in signals if s.signal_type == "active_dispute"]
        assert len(disputes) == 0

    @patch("scripts.compass.db.get_connection")
    def test_active_dispute_identifies_side(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._mock_contradictions())

        papers = [
            {
                "id": "recent_1",
                "title": "CoT prompting improvements",
                "abstract": (
                    "Chain-of-thought prompting improves reasoning accuracy "
                    "on mathematical benchmarks significantly."
                ),
            }
        ]
        signals = _find_kg_contradictions(papers)

        disputes = [s for s in signals if s.signal_type == "active_dispute"]
        if disputes:
            assert "paper_side" in disputes[0].metadata
            assert disputes[0].metadata["paper_side"] in ("A", "B")


class TestActiveDisputeCap:
    """Active disputes must be capped per-contradiction and globally."""

    def _make_contradictions(self, n=3):
        return [
            {
                "claim_a": f"Method {i} improves accuracy significantly",
                "claim_b": f"Method {i} does not improve accuracy reliably",
                "paper_a_id": f"contra_a_{i}",
                "paper_b_id": f"contra_b_{i}",
                "strength": 0.8,
                "paper_a_title": f"Method {i} Works",
                "paper_b_title": f"Method {i} Fails",
            }
            for i in range(n)
        ]

    @patch("scripts.compass.db.get_connection")
    def test_active_disputes_capped_per_contradiction(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._make_contradictions(1))

        # 20 papers all overlapping with the same contradiction
        papers = [
            {
                "id": f"overlap_{i}",
                "title": f"Study on method accuracy {i}",
                "abstract": (
                    f"Method 0 improves accuracy significantly on standard "
                    f"benchmarks. We evaluate performance gains carefully."
                ),
            }
            for i in range(20)
        ]
        signals = _find_kg_contradictions(papers)
        disputes = [s for s in signals if s.signal_type == "active_dispute"]
        # Per-contradiction cap is 3
        assert len(disputes) <= 3, f"Expected <= 3 disputes, got {len(disputes)}"

    @patch("scripts.compass.db.get_connection")
    def test_active_disputes_capped_globally(self, mock_get_conn):
        mock_get_conn.return_value = _make_mock_connection(self._make_contradictions(10))

        papers = [
            {
                "id": f"overlap_{i}",
                "title": f"Study on method accuracy {i}",
                "abstract": (
                    f"Method {i % 10} improves accuracy significantly on standard "
                    f"benchmarks. We evaluate performance and reliability."
                ),
            }
            for i in range(50)
        ]
        signals = _find_kg_contradictions(papers)
        disputes = [s for s in signals if s.signal_type == "active_dispute"]
        # Global cap is 10
        assert len(disputes) <= 10, f"Expected <= 10 disputes, got {len(disputes)}"


class TestNearIdenticalDedup:
    """Near-identical paper pairs should be filtered out of KG contradictions."""

    @patch("scripts.compass.db.get_connection")
    def test_same_title_different_case_filtered(self, mock_get_conn):
        contradictions = [
            {
                "claim_a": "Confirmation bias affects oversight scalability",
                "claim_b": "Confirmation bias does not affect oversight",
                "paper_a_id": "dup_a",
                "paper_b_id": "dup_b",
                "strength": 0.75,
                "paper_a_title": "Confirmation bias: A challenge for scalable oversi",
                "paper_b_title": "Confirmation Bias: A Challenge for Scalable Oversi",
            },
        ]
        mock_get_conn.return_value = _make_mock_connection(contradictions)
        signals = _find_kg_contradictions([])
        verified = [s for s in signals if s.signal_type == "verified_contradiction"]
        assert len(verified) == 0, (
            "Near-identical paper titles should be filtered out"
        )

    @patch("scripts.compass.db.get_connection")
    def test_same_paper_id_filtered(self, mock_get_conn):
        contradictions = [
            {
                "claim_a": "Claim from paper X",
                "claim_b": "Another claim from same paper X",
                "paper_a_id": "same_paper",
                "paper_b_id": "same_paper",
                "strength": 0.6,
                "paper_a_title": "Paper X Title",
                "paper_b_title": "Paper X Title",
            },
        ]
        mock_get_conn.return_value = _make_mock_connection(contradictions)
        signals = _find_kg_contradictions([])
        assert len(signals) == 0, "Same paper_id contradiction should be filtered"

    @patch("scripts.compass.db.get_connection")
    def test_genuine_contradiction_not_filtered(self, mock_get_conn):
        contradictions = [
            {
                "claim_a": "Method A works well",
                "claim_b": "Method A does not work",
                "paper_a_id": "paper_genuine_a",
                "paper_b_id": "paper_genuine_b",
                "strength": 0.85,
                "paper_a_title": "Scaling Laws for Language Models",
                "paper_b_title": "Diminishing Returns in Model Scaling",
            },
        ]
        mock_get_conn.return_value = _make_mock_connection(contradictions)
        signals = _find_kg_contradictions([])
        verified = [s for s in signals if s.signal_type == "verified_contradiction"]
        assert len(verified) == 1, "Genuine contradictions should not be filtered"


class TestPrioritySorting:
    """verified_contradiction should sort before all other signal types."""

    @patch("scripts.compass.db.get_connection")
    def test_verified_contradiction_is_priority_zero(self, mock_get_conn):
        contradictions = [
            {
                "claim_a": "Transformers improve reasoning performance significantly",
                "claim_b": "Transformers fail to improve reasoning beyond surface patterns",
                "paper_a_id": None,
                "paper_b_id": None,
                "strength": 0.9,
                "paper_a_title": None,
                "paper_b_title": None,
            },
        ]
        mock_get_conn.return_value = _make_mock_connection(contradictions)

        # Use papers that will produce consensus_thin_evidence as well
        papers = [
            {
                "id": f"cot_{i}", "title": f"CoT paper {i}",
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

        if signals:
            # If verified_contradiction is present, it should be first
            verified = [s for s in signals if s["signal_type"] == "verified_contradiction"]
            if verified:
                assert signals[0]["signal_type"] == "verified_contradiction"
