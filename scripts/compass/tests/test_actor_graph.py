"""Tests for the actor_graph module (union-find grouping, name handling)."""

from datetime import datetime, timezone, timedelta

from scripts.compass.actor_graph import (
    UnionFind,
    _extract_author_names,
    _normalize_name,
    build_groups,
)


class TestUnionFind:
    def test_find_creates_new(self):
        uf = UnionFind()
        assert uf.find("a") == "a"

    def test_union_merges(self):
        uf = UnionFind()
        uf.union("a", "b")
        assert uf.find("a") == uf.find("b")

    def test_separate_sets(self):
        uf = UnionFind()
        uf.union("a", "b")
        uf.union("c", "d")
        assert uf.find("a") != uf.find("c")


class TestExtractAuthorNames:
    def test_list_of_strings(self):
        assert _extract_author_names(["Alice", "Bob"]) == ["Alice", "Bob"]

    def test_list_of_dicts(self):
        authors = [{"name": "Alice"}, {"name": "Bob"}]
        assert _extract_author_names(authors) == ["Alice", "Bob"]

    def test_empty(self):
        assert _extract_author_names(None) == []
        assert _extract_author_names([]) == []

    def test_strips_whitespace(self):
        assert _extract_author_names(["  Alice  "]) == ["Alice"]

    def test_skips_empty_names(self):
        assert _extract_author_names(["Alice", "", "  "]) == ["Alice"]


class TestNormalizeName:
    def test_lowercase(self):
        assert _normalize_name("Alice Smith") == "alice smith"

    def test_collapses_whitespace(self):
        assert _normalize_name("Alice   Smith") == "alice smith"


class TestBuildGroups:
    def _make_papers(self):
        """Create test papers where some authors share multiple papers."""
        now = datetime.now(timezone.utc)
        return [
            # Alice and Bob co-author 2 papers -> should be grouped
            {
                "id": "p1",
                "title": "Paper 1",
                "authors": [{"name": "Alice Smith"}, {"name": "Bob Jones"}],
                "categories": ["cs.AI"],
                "discovered_at": now - timedelta(days=1),
            },
            {
                "id": "p2",
                "title": "Paper 2",
                "authors": [{"name": "Alice Smith"}, {"name": "Bob Jones"}],
                "categories": ["cs.CL"],
                "discovered_at": now - timedelta(days=2),
            },
            # Carol and Dave co-author 2 papers -> separate group
            {
                "id": "p3",
                "title": "Paper 3",
                "authors": [{"name": "Carol White"}, {"name": "Dave Black"}],
                "categories": ["cs.LG"],
                "discovered_at": now - timedelta(days=3),
            },
            {
                "id": "p4",
                "title": "Paper 4",
                "authors": [{"name": "Carol White"}, {"name": "Dave Black"}],
                "categories": ["cs.AI"],
                "discovered_at": now - timedelta(days=4),
            },
            # Eve appears on ONE paper with Alice -> NOT merged (only 1 shared paper)
            {
                "id": "p5",
                "title": "Paper 5",
                "authors": [{"name": "Alice Smith"}, {"name": "Eve Green"}],
                "categories": ["cs.CL"],
                "discovered_at": now - timedelta(days=5),
            },
        ]

    def test_groups_formed(self):
        papers = self._make_papers()
        groups = build_groups(papers, min_papers=2, min_shared_papers=2)
        assert len(groups) >= 2

    def test_no_mega_group(self):
        """Eve shares only 1 paper with Alice -> they should NOT be merged."""
        papers = self._make_papers()
        groups = build_groups(papers, min_papers=2, min_shared_papers=2)
        # No group should contain all 5 authors
        for g in groups:
            norm_names = {_normalize_name(n) for n in g["author_names"]}
            assert len(norm_names) < 5, (
                f"Mega-group detected with {len(norm_names)} authors: {norm_names}"
            )

    def test_mega_group_with_shared_papers_1(self):
        """With min_shared_papers=1, Eve SHOULD be merged with Alice's group."""
        papers = self._make_papers()
        groups = build_groups(papers, min_papers=2, min_shared_papers=1)
        # Alice+Bob+Eve should be in one group
        for g in groups:
            norm_names = {_normalize_name(n) for n in g["author_names"]}
            if "alice smith" in norm_names:
                assert "eve green" in norm_names

    def test_common_name_no_false_merge(self):
        """Common names appearing on unrelated papers should not merge groups."""
        now = datetime.now(timezone.utc)
        papers = [
            # Group 1: A. Yang + Team 1, paper 1
            {
                "id": "g1p1",
                "title": "Team 1 Paper A",
                "authors": [{"name": "A. Yang"}, {"name": "X. Chen"}],
                "categories": ["cs.AI"],
                "discovered_at": now,
            },
            # Group 1: A. Yang + Team 1, paper 2
            {
                "id": "g1p2",
                "title": "Team 1 Paper B",
                "authors": [{"name": "A. Yang"}, {"name": "X. Chen"}],
                "categories": ["cs.AI"],
                "discovered_at": now,
            },
            # Group 2: same name A. Yang + Team 2, paper 1
            {
                "id": "g2p1",
                "title": "Team 2 Paper A",
                "authors": [{"name": "A. Yang"}, {"name": "Y. Li"}],
                "categories": ["cs.LG"],
                "discovered_at": now,
            },
            # Group 2: A. Yang + Team 2, paper 2
            {
                "id": "g2p2",
                "title": "Team 2 Paper B",
                "authors": [{"name": "A. Yang"}, {"name": "Y. Li"}],
                "categories": ["cs.LG"],
                "discovered_at": now,
            },
            # Group 3: Z. Wang solo papers (unrelated, shares no co-authors)
            {
                "id": "g3p1",
                "title": "Solo Paper A",
                "authors": [{"name": "Z. Wang"}],
                "categories": ["cs.CV"],
                "discovered_at": now,
            },
            {
                "id": "g3p2",
                "title": "Solo Paper B",
                "authors": [{"name": "Z. Wang"}],
                "categories": ["cs.CV"],
                "discovered_at": now,
            },
        ]
        groups = build_groups(papers, min_papers=2, min_shared_papers=2)
        # A. Yang shares 2 papers with X. Chen and 2 papers with Y. Li
        # so all three get merged. But Z. Wang should stay separate.
        for g in groups:
            norm_names = {_normalize_name(n) for n in g["author_names"]}
            if "z. wang" in norm_names:
                # Z. Wang should NOT be in a group with the others
                assert "x. chen" not in norm_names
                assert "y. li" not in norm_names

    def test_empty_papers(self):
        groups = build_groups([], min_papers=2)
        assert groups == []

    def test_group_has_required_fields(self):
        papers = self._make_papers()
        groups = build_groups(papers, min_papers=2, min_shared_papers=2)
        for g in groups:
            assert "author_names" in g
            assert "paper_count" in g
            assert "paper_ids" in g
            assert "categories" in g
            assert isinstance(g["author_names"], list)
            assert isinstance(g["paper_count"], int)

    def test_sorted_by_paper_count_desc(self):
        papers = self._make_papers()
        groups = build_groups(papers, min_papers=1, min_shared_papers=2)
        counts = [g["paper_count"] for g in groups]
        assert counts == sorted(counts, reverse=True)
