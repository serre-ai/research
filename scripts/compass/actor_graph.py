#!/usr/bin/env python3
"""Build author group graph from paper co-authorship.

Groups authors by co-authorship patterns, maps groups to topics,
and identifies monopoly risks and collaboration gaps.

Usage:
    python3 scripts/compass/actor_graph.py              # build graph
    python3 scripts/compass/actor_graph.py --dry-run    # preview only
    python3 scripts/compass/actor_graph.py --clear      # rebuild from scratch
    python3 scripts/compass/actor_graph.py --min-papers 3
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime
from typing import Any

try:
    from .db import get_connection, close_connection
except ImportError:
    from db import get_connection, close_connection  # type: ignore


# ── Union-Find ──────────────────────────────────────────────


class UnionFind:
    """Disjoint-set data structure with path compression."""

    def __init__(self):
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: str, y: str) -> None:
        px, py = self.find(x), self.find(y)
        if px != py:
            self.parent[px] = py


# ── Author extraction ──────────────────────────────────────


def _extract_author_names(authors_json: Any) -> list[str]:
    """Extract author name strings from JSONB, handling both formats."""
    if not authors_json:
        return []
    names: list[str] = []
    for a in authors_json:
        if isinstance(a, str):
            names.append(a.strip())
        elif isinstance(a, dict) and "name" in a:
            names.append(a["name"].strip())
    return [n for n in names if n]


def _normalize_name(name: str) -> str:
    """Normalize author name for deduplication.

    Lowercases and collapses whitespace. Keeps original casing for display
    but uses normalized form as the union-find key.
    """
    return " ".join(name.lower().split())


# ── Core logic ──────────────────────────────────────────────


def fetch_papers(conn) -> list[dict]:
    """Fetch all papers with authors from DB."""
    import psycopg2.extras

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT id, title, authors, categories, discovered_at
        FROM lit_papers
        WHERE authors IS NOT NULL
          AND authors != '[]'::jsonb
    """)
    papers = [dict(row) for row in cur.fetchall()]
    cur.close()
    return papers


def build_groups(
    papers: list[dict], min_papers: int = 2, min_shared_papers: int = 2
) -> list[dict]:
    """Build research groups from co-authorship using union-find.

    To avoid mega-groups caused by common names bridging unrelated
    collaborations, we only merge two authors if they share at least
    ``min_shared_papers`` papers (default 2). This prevents a single
    shared paper with "A. Yang" from merging hundreds of authors.

    Returns a list of group dicts with:
      - author_names: list[str] (display names)
      - paper_count: int
      - paper_ids: list[str]
      - categories: list[str] (all categories across group papers)
      - first_seen: datetime | None
      - last_seen: datetime | None
    """
    uf = UnionFind()

    # Map normalized name -> best display name (longest version seen)
    display_names: dict[str, str] = {}
    # Map normalized name -> set of paper indices
    author_papers: dict[str, set[int]] = defaultdict(set)

    # First pass: collect author-paper mappings
    paper_author_lists: list[list[str]] = []
    for idx, paper in enumerate(papers):
        raw_names = _extract_author_names(paper.get("authors"))
        norm_names = []
        for name in raw_names:
            nk = _normalize_name(name)
            norm_names.append(nk)
            # Keep the longest display form
            if nk not in display_names or len(name) > len(display_names[nk]):
                display_names[nk] = name
            author_papers[nk].add(idx)
        paper_author_lists.append(norm_names)

    # Second pass: count shared papers between each co-author pair
    # Then only union pairs that share >= min_shared_papers
    pair_shared: dict[tuple[str, str], int] = defaultdict(int)
    for norm_names in paper_author_lists:
        unique_names = list(dict.fromkeys(norm_names))  # deduplicate, preserve order
        for i in range(len(unique_names)):
            for j in range(i + 1, len(unique_names)):
                a, b = unique_names[i], unique_names[j]
                pair = (min(a, b), max(a, b))
                pair_shared[pair] += 1

    # Only merge authors with enough shared papers
    for (a, b), count in pair_shared.items():
        if count >= min_shared_papers:
            uf.union(a, b)

    # Group authors by their root
    root_to_authors: dict[str, list[str]] = defaultdict(list)
    for nk in author_papers:
        root = uf.find(nk)
        root_to_authors[root].append(nk)

    # Build group records
    groups: list[dict] = []
    for root, members in root_to_authors.items():
        # Collect all paper indices for the group
        paper_indices: set[int] = set()
        for nk in members:
            paper_indices |= author_papers[nk]

        if len(paper_indices) < min_papers:
            continue

        # Collect metadata from papers
        categories: set[str] = set()
        first_seen: datetime | None = None
        last_seen: datetime | None = None
        paper_ids: list[str] = []

        for pi in paper_indices:
            p = papers[pi]
            paper_ids.append(p["id"])
            cats = p.get("categories")
            if cats:
                if isinstance(cats, list):
                    categories.update(str(c) for c in cats)
                elif isinstance(cats, str):
                    categories.add(cats)
            dt = p.get("discovered_at")
            if dt is not None:
                if first_seen is None or dt < first_seen:
                    first_seen = dt
                if last_seen is None or dt > last_seen:
                    last_seen = dt

        groups.append({
            "author_names": sorted(
                [display_names[nk] for nk in members],
                key=lambda n: n.lower(),
            ),
            "paper_count": len(paper_indices),
            "paper_ids": paper_ids,
            "categories": sorted(categories),
            "first_seen": first_seen,
            "last_seen": last_seen,
        })

    # Sort by paper count descending
    groups.sort(key=lambda g: g["paper_count"], reverse=True)
    return groups


def map_topics(conn, groups: list[dict]) -> dict[str, int]:
    """Try to map category strings to research_topics IDs.

    Returns a mapping of category -> topic_id.
    If the research_topics table doesn't exist yet, returns empty.
    """
    try:
        import psycopg2.extras

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, slug, label FROM research_topics")
        topics = {row["slug"]: row["id"] for row in cur.fetchall()}
        # Also index by label (lowercased)
        cur.execute("SELECT id, label FROM research_topics")
        for row in cur.fetchall():
            topics[row["label"].lower()] = row["id"]
        cur.close()
        return topics
    except Exception:
        # Table doesn't exist yet — that's fine
        try:
            conn.rollback()
        except Exception:
            pass
        return {}


def store_groups(conn, groups: list[dict], topic_map: dict[str, int]) -> int:
    """Insert groups into research_groups and group_topic_edges.

    The research_groups.author_names column is TEXT[], so we pass a Python
    list directly (psycopg2 adapts it to a PostgreSQL array). Previously
    used json.dumps() which produced a JSON string — wrong type for TEXT[].
    """
    cur = conn.cursor()
    stored = 0

    for g in groups:
        # Resolve topic IDs from categories
        topic_ids: list[str] = []
        for cat in g["categories"]:
            cat_lower = cat.lower()
            if cat_lower in topic_map:
                topic_ids.append(topic_map[cat_lower])

        try:
            cur.execute("""
                INSERT INTO research_groups
                    (author_names, paper_count, topic_ids, first_seen, last_seen)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                g["author_names"],          # Python list -> TEXT[]
                g["paper_count"],
                topic_ids if topic_ids else None,
                g["first_seen"],
                g["last_seen"],
            ))
            row = cur.fetchone()
            group_id = row[0] if row else None

            # Build group-topic edges
            if group_id and topic_ids:
                # Count papers per topic for this group
                topic_paper_counts: dict[str, int] = defaultdict(int)
                for cat in g["categories"]:
                    cat_lower = cat.lower()
                    if cat_lower in topic_map:
                        tid = topic_map[cat_lower]
                        topic_paper_counts[tid] += 1

                for tid, count in topic_paper_counts.items():
                    try:
                        cur.execute("""
                            INSERT INTO group_topic_edges
                                (group_id, topic_id, paper_count)
                            VALUES (%s, %s, %s)
                        """, (group_id, tid, count))
                    except Exception as e:
                        conn.rollback()
                        print(
                            f"  Warning: edge insert failed "
                            f"(group={group_id}, topic={tid}): {e}",
                            file=sys.stderr,
                        )

            stored += 1
        except Exception as e:
            conn.rollback()
            print(
                f"  Warning: group insert failed: {e}",
                file=sys.stderr,
            )

    conn.commit()
    cur.close()
    return stored


def clear_groups(conn) -> None:
    """Delete all existing research groups and edges."""
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM group_topic_edges")
    except Exception:
        conn.rollback()
    try:
        cur.execute("DELETE FROM research_groups")
        conn.commit()
    except Exception:
        conn.rollback()
    cur.close()


# ── Analysis ────────────────────────────────────────────────


def detect_signals(
    groups: list[dict],
) -> tuple[list[str], list[str]]:
    """Detect monopoly risks and collaboration gaps.

    Returns (monopoly_warnings, collaboration_gaps).
    """
    # Track which groups work on which categories
    topic_groups: dict[str, list[int]] = defaultdict(list)
    for idx, g in enumerate(groups):
        for cat in g["categories"]:
            topic_groups[cat].append(idx)

    # Monopoly risks: topics with <= 2 groups
    monopoly_warnings: list[str] = []
    for topic, gids in sorted(topic_groups.items()):
        if len(gids) <= 2:
            group_names = []
            for gi in gids:
                top_authors = groups[gi]["author_names"][:3]
                group_names.append(
                    f"[{', '.join(top_authors)}"
                    + (f", +{len(groups[gi]['author_names']) - 3}" if len(groups[gi]["author_names"]) > 3 else "")
                    + "]"
                )
            monopoly_warnings.append(
                f"Monopoly risk: topic '{topic}' has only "
                f"{len(gids)} active group(s): {', '.join(group_names)}"
            )

    # Collaboration gaps: groups on overlapping topics with no shared authors
    collaboration_gaps: list[str] = []
    seen_pairs: set[tuple[int, int]] = set()
    for topic, gids in topic_groups.items():
        if len(gids) < 2:
            continue
        for i in range(len(gids)):
            for j in range(i + 1, len(gids)):
                gi, gj = gids[i], gids[j]
                pair = (min(gi, gj), max(gi, gj))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                # Check for shared authors (normalized)
                names_i = {_normalize_name(n) for n in groups[gi]["author_names"]}
                names_j = {_normalize_name(n) for n in groups[gj]["author_names"]}
                shared = names_i & names_j
                if not shared:
                    # Count overlapping topics
                    cats_i = set(groups[gi]["categories"])
                    cats_j = set(groups[gj]["categories"])
                    overlap = cats_i & cats_j
                    if len(overlap) >= 2:
                        g1_label = groups[gi]["author_names"][0]
                        g2_label = groups[gj]["author_names"][0]
                        collaboration_gaps.append(
                            f"Potential collaboration gap: "
                            f"groups led by '{g1_label}' and '{g2_label}' "
                            f"share {len(overlap)} topics but no co-authors"
                        )

    return monopoly_warnings, collaboration_gaps


# ── CLI ─────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build author group graph from paper co-authorship."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview groups without writing to DB.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete existing groups before rebuilding.",
    )
    parser.add_argument(
        "--min-papers",
        type=int,
        default=2,
        help="Minimum papers to form a group (default: 2).",
    )
    parser.add_argument(
        "--min-shared-papers",
        type=int,
        default=2,
        help="Minimum co-authored papers to merge two authors (default: 2).",
    )
    args = parser.parse_args()

    try:
        conn = get_connection()
    except Exception as e:
        print(f"Error: cannot connect to database: {e}", file=sys.stderr)
        sys.exit(1)

    # Fetch papers
    print("Fetching papers with authors...")
    papers = fetch_papers(conn)
    if not papers:
        print("No papers with authors found. Nothing to do.")
        close_connection()
        return

    print(f"  Found {len(papers)} papers with author data.")

    # Collect unique author count
    all_authors: set[str] = set()
    for p in papers:
        for name in _extract_author_names(p.get("authors")):
            all_authors.add(_normalize_name(name))

    print(f"  {len(all_authors)} unique authors.")

    # Build groups
    print(
        f"Building co-authorship groups "
        f"(min_papers={args.min_papers}, min_shared_papers={args.min_shared_papers})..."
    )
    groups = build_groups(
        papers,
        min_papers=args.min_papers,
        min_shared_papers=args.min_shared_papers,
    )
    print(f"  Built {len(groups)} research groups.")

    if not groups:
        print("No groups meet the minimum paper threshold.")
        close_connection()
        return

    # Show largest groups
    print("\nTop groups:")
    for g in groups[:10]:
        authors_preview = g["author_names"][:5]
        extra = len(g["author_names"]) - 5
        label = ", ".join(authors_preview)
        if extra > 0:
            label += f", +{extra} more"
        print(f"  [{label}] — {g['paper_count']} papers, {len(g['categories'])} categories")

    # Detect signals
    monopoly_warnings, collab_gaps = detect_signals(groups)

    if monopoly_warnings:
        print(f"\nMonopoly risks ({len(monopoly_warnings)}):")
        for w in monopoly_warnings[:20]:
            print(f"  {w}")
        if len(monopoly_warnings) > 20:
            print(f"  ... and {len(monopoly_warnings) - 20} more")

    if collab_gaps:
        print(f"\nCollaboration gaps ({len(collab_gaps)}):")
        for g in collab_gaps[:10]:
            print(f"  {g}")
        if len(collab_gaps) > 10:
            print(f"  ... and {len(collab_gaps) - 10} more")

    # Count topics with few groups
    topic_groups: dict[str, int] = defaultdict(int)
    for g in groups:
        for cat in g["categories"]:
            topic_groups[cat] += 1
    few_group_topics = sum(1 for c in topic_groups.values() if c <= 2)

    if args.dry_run:
        print("\n[DRY RUN] No changes written to database.")
    else:
        # Clear if requested
        if args.clear:
            print("\nClearing existing groups...")
            clear_groups(conn)

        # Map topics
        topic_map = map_topics(conn, groups)
        if topic_map:
            print(f"  Mapped {len(topic_map)} topic slugs/labels to IDs.")
        else:
            print("  No research_topics table found — skipping topic mapping.")

        # Store
        print("Writing groups to database...")
        stored = store_groups(conn, groups, topic_map)
        print(f"  Stored {stored} groups.")

    # Summary
    largest = groups[0] if groups else None
    largest_label = "none"
    if largest:
        preview = largest["author_names"][:5]
        extra = len(largest["author_names"]) - 5
        largest_label = '["' + '", "'.join(preview) + '"'
        if extra > 0:
            largest_label += f", +{extra} more"
        largest_label += f"] ({largest['paper_count']} papers)"

    print(
        f"\nBuilt {len(groups)} research groups from {len(all_authors)} unique authors. "
        f"Largest: {largest_label}. "
        f"{few_group_topics} topics have <=2 active groups."
    )

    close_connection()


if __name__ == "__main__":
    main()
