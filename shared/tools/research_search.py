#!/usr/bin/env python3
"""Academic research search tool for the Deepwork platform.

Queries Semantic Scholar and arXiv APIs, performs citation chaining,
generates structured notes and BibTeX entries.

Usage:
    python research_search.py search "verification complexity language model" --limit 20
    python research_search.py cite <paper_id> --depth 2
    python research_search.py bibtex <paper_id>
    python research_search.py survey --queries-file queries.yaml --output-dir notes/
    python research_search.py read <arxiv_id>   # fetch and summarize a paper's PDF

Requires: S2_API_KEY in environment (free from semanticscholar.org/product/api)

Rate limits:
    Semantic Scholar: 1 req/sec (unauthenticated), 10 req/sec (with API key)
    arXiv: 1 req/3sec (be polite)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

S2_API_KEY = os.environ.get("S2_API_KEY", "")
S2_BASE = "https://api.semanticscholar.org/graph/v1"
ARXIV_BASE = "http://export.arxiv.org/api/query"

# Rate limiting
_last_s2_call = 0.0
_last_arxiv_call = 0.0

S2_FIELDS = "paperId,externalIds,title,year,authors,citationCount,influentialCitationCount,abstract,venue,publicationTypes,openAccessPdf"
S2_CITE_FIELDS = "paperId,title,year,authors,citationCount,venue"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Paper:
    id: str
    title: str
    year: Optional[int] = None
    authors: list[str] = field(default_factory=list)
    venue: str = ""
    abstract: str = ""
    citation_count: int = 0
    influential_citations: int = 0
    arxiv_id: str = ""
    doi: str = ""
    pdf_url: str = ""
    source: str = ""  # "s2" or "arxiv"

    @property
    def first_author_last(self) -> str:
        if self.authors:
            parts = self.authors[0].split()
            return parts[-1] if parts else "Unknown"
        return "Unknown"

    @property
    def bibtex_key(self) -> str:
        return f"{self.first_author_last.lower()}{self.year or ''}"

    def to_bibtex(self) -> str:
        entry_type = "article"
        if self.venue and any(k in self.venue.lower() for k in ["conference", "proc", "neurips", "icml", "iclr", "aaai", "acl"]):
            entry_type = "inproceedings"

        authors_bib = " and ".join(self.authors[:10])
        if len(self.authors) > 10:
            authors_bib += " and others"

        lines = [f"@{entry_type}{{{self.bibtex_key},"]
        lines.append(f"  title = {{{self.title}}},")
        lines.append(f"  author = {{{authors_bib}}},")
        if self.year:
            lines.append(f"  year = {{{self.year}}},")
        if self.venue:
            field_name = "booktitle" if entry_type == "inproceedings" else "journal"
            lines.append(f"  {field_name} = {{{self.venue}}},")
        if self.doi:
            lines.append(f"  doi = {{{self.doi}}},")
        if self.arxiv_id:
            lines.append(f"  eprint = {{{self.arxiv_id}}},")
            lines.append(f"  archivePrefix = {{arXiv}},")
        if self.pdf_url:
            lines.append(f"  url = {{{self.pdf_url}}},")
        lines.append("}")
        return "\n".join(lines)

    def to_markdown(self, include_abstract: bool = False) -> str:
        authors_short = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_short += " et al."
        line = f"- **{self.title}** ({self.year}). {authors_short}. *{self.venue}*. [{self.citation_count} citations]"
        if self.arxiv_id:
            line += f" [arXiv:{self.arxiv_id}]"
        if include_abstract and self.abstract:
            wrapped = textwrap.fill(self.abstract, width=100, initial_indent="  > ", subsequent_indent="  > ")
            line += f"\n{wrapped}"
        return line


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _rate_limit_s2():
    global _last_s2_call
    min_interval = 0.1 if S2_API_KEY else 1.0
    elapsed = time.time() - _last_s2_call
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    _last_s2_call = time.time()


def _rate_limit_arxiv():
    global _last_arxiv_call
    elapsed = time.time() - _last_arxiv_call
    if elapsed < 3.0:
        time.sleep(3.0 - elapsed)
    _last_arxiv_call = time.time()


def _s2_request(path: str, params: dict | None = None) -> dict:
    """Make a Semantic Scholar API request."""
    _rate_limit_s2()
    url = f"{S2_BASE}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {"User-Agent": "DeepworkResearch/1.0"}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY

    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"  [rate limited, waiting 2s...]", file=sys.stderr)
            time.sleep(2)
            return _s2_request(path, params)
        raise


def _parse_s2_paper(data: dict) -> Paper:
    """Parse a Semantic Scholar paper response into a Paper object."""
    ext = data.get("externalIds") or {}
    authors = [a.get("name", "") for a in (data.get("authors") or [])]
    pdf = data.get("openAccessPdf") or {}

    return Paper(
        id=data.get("paperId", ""),
        title=data.get("title", ""),
        year=data.get("year"),
        authors=authors,
        venue=data.get("venue", ""),
        abstract=data.get("abstract", ""),
        citation_count=data.get("citationCount", 0),
        influential_citations=data.get("influentialCitationCount", 0),
        arxiv_id=ext.get("ArXiv", ""),
        doi=ext.get("DOI", ""),
        pdf_url=pdf.get("url", ""),
        source="s2",
    )


# ---------------------------------------------------------------------------
# Semantic Scholar search
# ---------------------------------------------------------------------------

def s2_search(query: str, limit: int = 20, year_range: str = "", fields_of_study: str = "") -> list[Paper]:
    """Search Semantic Scholar for papers matching a query."""
    params = {
        "query": query,
        "limit": min(limit, 100),
        "fields": S2_FIELDS,
    }
    if year_range:
        params["year"] = year_range
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study

    print(f"  S2 search: \"{query}\" (limit={limit})", file=sys.stderr)
    data = _s2_request("paper/search", params)
    papers = [_parse_s2_paper(p) for p in (data.get("data") or [])]
    print(f"  → {len(papers)} results (total: {data.get('total', '?')})", file=sys.stderr)
    return papers


def s2_paper(paper_id: str) -> Paper:
    """Get a single paper by ID (S2 ID, DOI, ArXiv ID, etc.)."""
    print(f"  S2 paper: {paper_id}", file=sys.stderr)
    data = _s2_request(f"paper/{paper_id}", {"fields": S2_FIELDS})
    return _parse_s2_paper(data)


def s2_citations(paper_id: str, limit: int = 50) -> list[Paper]:
    """Get papers that cite this paper (forward citations)."""
    print(f"  S2 citations of: {paper_id} (limit={limit})", file=sys.stderr)
    data = _s2_request(f"paper/{paper_id}/citations", {
        "fields": S2_CITE_FIELDS,
        "limit": min(limit, 1000),
    })
    papers = []
    for item in (data.get("data") or []):
        citing = item.get("citingPaper", {})
        if citing.get("title"):
            papers.append(Paper(
                id=citing.get("paperId", ""),
                title=citing.get("title", ""),
                year=citing.get("year"),
                authors=[a.get("name", "") for a in (citing.get("authors") or [])],
                venue=citing.get("venue", ""),
                citation_count=citing.get("citationCount", 0),
                source="s2",
            ))
    print(f"  → {len(papers)} citing papers", file=sys.stderr)
    return papers


def s2_references(paper_id: str, limit: int = 50) -> list[Paper]:
    """Get papers that this paper cites (backward references)."""
    print(f"  S2 references from: {paper_id} (limit={limit})", file=sys.stderr)
    data = _s2_request(f"paper/{paper_id}/references", {
        "fields": S2_CITE_FIELDS,
        "limit": min(limit, 1000),
    })
    papers = []
    for item in (data.get("data") or []):
        ref = item.get("citedPaper", {})
        if ref.get("title"):
            papers.append(Paper(
                id=ref.get("paperId", ""),
                title=ref.get("title", ""),
                year=ref.get("year"),
                authors=[a.get("name", "") for a in (ref.get("authors") or [])],
                venue=ref.get("venue", ""),
                citation_count=ref.get("citationCount", 0),
                source="s2",
            ))
    print(f"  → {len(papers)} referenced papers", file=sys.stderr)
    return papers


def s2_recommendations(paper_id: str, limit: int = 20) -> list[Paper]:
    """Get recommended papers based on a seed paper."""
    _rate_limit_s2()
    url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}?limit={limit}&fields={S2_CITE_FIELDS}"
    headers = {"User-Agent": "DeepworkResearch/1.0"}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY

    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        papers = []
        for p in (data.get("recommendedPapers") or []):
            if p.get("title"):
                papers.append(Paper(
                    id=p.get("paperId", ""),
                    title=p.get("title", ""),
                    year=p.get("year"),
                    authors=[a.get("name", "") for a in (p.get("authors") or [])],
                    venue=p.get("venue", ""),
                    citation_count=p.get("citationCount", 0),
                    source="s2",
                ))
        print(f"  → {len(papers)} recommendations", file=sys.stderr)
        return papers
    except Exception as e:
        print(f"  → recommendations failed: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# arXiv search
# ---------------------------------------------------------------------------

def arxiv_search(query: str, limit: int = 20, categories: str = "") -> list[Paper]:
    """Search arXiv for papers matching a query."""
    _rate_limit_arxiv()

    search_query = f"all:{query}"
    if categories:
        cat_filter = " OR ".join(f"cat:{c}" for c in categories.split(","))
        search_query = f"({search_query}) AND ({cat_filter})"

    params = {
        "search_query": search_query,
        "max_results": min(limit, 100),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    url = f"{ARXIV_BASE}?{urllib.parse.urlencode(params)}"
    print(f"  arXiv search: \"{query}\" (limit={limit})", file=sys.stderr)

    req = urllib.request.Request(url, headers={"User-Agent": "DeepworkResearch/1.0"})
    resp = urllib.request.urlopen(req, timeout=15)
    root = ET.fromstring(resp.read())

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    papers = []

    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)
        entry_id = entry.find("atom:id", ns)

        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None and name.text:
                authors.append(name.text)

        arxiv_id = ""
        if entry_id is not None and entry_id.text:
            arxiv_id = entry_id.text.split("/abs/")[-1]

        year = None
        if published is not None and published.text:
            year = int(published.text[:4])

        categories = []
        for cat in entry.findall("arxiv:primary_category", ns):
            term = cat.get("term", "")
            if term:
                categories.append(term)

        papers.append(Paper(
            id=arxiv_id,
            title=(title.text or "").strip().replace("\n", " "),
            year=year,
            authors=authors,
            venue=", ".join(categories),
            abstract=(summary.text or "").strip().replace("\n", " "),
            arxiv_id=arxiv_id,
            pdf_url=f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else "",
            source="arxiv",
        ))

    print(f"  → {len(papers)} results", file=sys.stderr)
    return papers


# ---------------------------------------------------------------------------
# Citation chaining
# ---------------------------------------------------------------------------

def citation_chain(seed_id: str, depth: int = 1, direction: str = "both", top_k: int = 10) -> dict:
    """Follow citation chains from a seed paper.

    Args:
        seed_id: Semantic Scholar paper ID or identifier (DOI, ArXiv ID, etc.)
        depth: How many hops to follow (1 = direct citations only)
        direction: "forward" (who cites this), "backward" (what this cites), or "both"
        top_k: Return top-k papers by citation count at each level

    Returns:
        Dict with seed paper, forward citations, backward references, organized by depth.
    """
    seed = s2_paper(seed_id)
    result = {
        "seed": seed,
        "forward": {},  # depth -> list[Paper]
        "backward": {},  # depth -> list[Paper]
    }

    if direction in ("forward", "both"):
        current_ids = [seed.id]
        for d in range(1, depth + 1):
            level_papers = []
            for pid in current_ids[:5]:  # limit fan-out
                citations = s2_citations(pid, limit=50)
                level_papers.extend(citations)
            # Deduplicate and sort by citation count
            seen = set()
            unique = []
            for p in sorted(level_papers, key=lambda p: p.citation_count, reverse=True):
                if p.id not in seen:
                    seen.add(p.id)
                    unique.append(p)
            result["forward"][d] = unique[:top_k]
            current_ids = [p.id for p in unique[:5]]

    if direction in ("backward", "both"):
        current_ids = [seed.id]
        for d in range(1, depth + 1):
            level_papers = []
            for pid in current_ids[:5]:
                refs = s2_references(pid, limit=50)
                level_papers.extend(refs)
            seen = set()
            unique = []
            for p in sorted(level_papers, key=lambda p: p.citation_count, reverse=True):
                if p.id not in seen:
                    seen.add(p.id)
                    unique.append(p)
            result["backward"][d] = unique[:top_k]
            current_ids = [p.id for p in unique[:5]]

    return result


# ---------------------------------------------------------------------------
# Survey mode — structured multi-query search
# ---------------------------------------------------------------------------

def run_survey(queries: list[dict], output_dir: Path) -> None:
    """Run a structured survey across multiple queries.

    Each query dict has:
        - query: search string
        - topic: topic label for organization
        - year_range: optional year filter (e.g., "2023-2026")
        - seed_papers: optional list of S2 IDs for citation chaining
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    all_papers: dict[str, Paper] = {}  # id -> Paper (deduplication)
    topic_papers: dict[str, list[Paper]] = {}  # topic -> papers

    for q in queries:
        topic = q.get("topic", "general")
        query = q["query"]
        year_range = q.get("year_range", "")
        seed_papers = q.get("seed_papers", [])

        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Topic: {topic}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        papers = []

        # Semantic Scholar search
        try:
            s2_results = s2_search(query, limit=20, year_range=year_range)
            papers.extend(s2_results)
        except Exception as e:
            print(f"  S2 search failed: {e}", file=sys.stderr)

        # arXiv search
        try:
            arxiv_results = arxiv_search(query, limit=10)
            papers.extend(arxiv_results)
        except Exception as e:
            print(f"  arXiv search failed: {e}", file=sys.stderr)

        # Citation chaining from seed papers
        for seed_id in seed_papers:
            try:
                chain = citation_chain(seed_id, depth=1, direction="forward", top_k=10)
                for level_papers in chain["forward"].values():
                    papers.extend(level_papers)
            except Exception as e:
                print(f"  Citation chain failed for {seed_id}: {e}", file=sys.stderr)

        # Deduplicate
        topic_list = []
        for p in papers:
            key = p.id or p.title.lower().strip()
            if key not in all_papers:
                all_papers[key] = p
                topic_list.append(p)

        # Sort by citation count
        topic_list.sort(key=lambda p: p.citation_count, reverse=True)
        topic_papers[topic] = topic_list
        print(f"  Total unique papers for topic: {len(topic_list)}", file=sys.stderr)

    # Write output files
    _write_survey_notes(topic_papers, output_dir)
    _write_bibtex(all_papers, output_dir)
    _write_coverage_report(topic_papers, all_papers, output_dir)

    print(f"\nSurvey complete.", file=sys.stderr)
    print(f"  Total unique papers: {len(all_papers)}", file=sys.stderr)
    print(f"  Output: {output_dir}/", file=sys.stderr)


def _write_survey_notes(topic_papers: dict[str, list[Paper]], output_dir: Path) -> None:
    """Write structured markdown notes organized by topic."""
    notes_path = output_dir / "survey_results.md"
    lines = [
        f"# Literature Survey Results",
        f"",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
    ]

    for topic, papers in topic_papers.items():
        lines.append(f"## {topic}")
        lines.append(f"")
        lines.append(f"*{len(papers)} papers found*")
        lines.append(f"")

        for p in papers[:30]:  # cap per topic
            lines.append(p.to_markdown(include_abstract=False))

        lines.append(f"")

    notes_path.write_text("\n".join(lines))
    print(f"  Wrote: {notes_path}", file=sys.stderr)


def _write_bibtex(all_papers: dict[str, Paper], output_dir: Path) -> None:
    """Write BibTeX file for all discovered papers."""
    bib_path = output_dir / "references.bib"
    entries = []
    seen_keys = set()

    for p in all_papers.values():
        if not p.title or not p.year:
            continue
        key = p.bibtex_key
        # Handle duplicate keys
        if key in seen_keys:
            suffix = "b"
            while f"{key}{suffix}" in seen_keys:
                suffix = chr(ord(suffix) + 1)
            key = f"{key}{suffix}"
        seen_keys.add(key)
        # Temporarily override the key
        entry = p.to_bibtex()
        entry = entry.replace(f"@article{{{p.bibtex_key},", f"@article{{{key},", 1)
        entry = entry.replace(f"@inproceedings{{{p.bibtex_key},", f"@inproceedings{{{key},", 1)
        entries.append(entry)

    bib_path.write_text("\n\n".join(entries))
    print(f"  Wrote: {bib_path} ({len(entries)} entries)", file=sys.stderr)


def _write_coverage_report(topic_papers: dict, all_papers: dict, output_dir: Path) -> None:
    """Write coverage metrics."""
    report_path = output_dir / "coverage.json"
    report = {
        "generated": datetime.now().isoformat(),
        "total_unique_papers": len(all_papers),
        "topics": {
            topic: {
                "count": len(papers),
                "top_cited": [
                    {"title": p.title, "citations": p.citation_count, "year": p.year}
                    for p in papers[:5]
                ],
            }
            for topic, papers in topic_papers.items()
        },
        "year_distribution": {},
    }
    for p in all_papers.values():
        if p.year:
            y = str(p.year)
            report["year_distribution"][y] = report["year_distribution"].get(y, 0) + 1

    report_path.write_text(json.dumps(report, indent=2))
    print(f"  Wrote: {report_path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    global S2_API_KEY
    # Load API key from .env if not in environment
    if not S2_API_KEY:
        env_path = Path(__file__).resolve().parents[2] / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("S2_API_KEY="):
                    S2_API_KEY = line.split("=", 1)[1].strip()
                    break

    parser = argparse.ArgumentParser(description="Academic research search tool")
    subparsers = parser.add_subparsers(dest="command")

    # search command
    sp = subparsers.add_parser("search", help="Search for papers")
    sp.add_argument("query", help="Search query")
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--year", default="", help="Year range, e.g., '2023-2026'")
    sp.add_argument("--source", default="both", choices=["s2", "arxiv", "both"])
    sp.add_argument("--abstracts", action="store_true", help="Include abstracts")

    # cite command
    sp = subparsers.add_parser("cite", help="Citation chain from a paper")
    sp.add_argument("paper_id", help="Paper ID (S2, DOI, ArXiv:XXXX.XXXXX)")
    sp.add_argument("--depth", type=int, default=1)
    sp.add_argument("--direction", default="both", choices=["forward", "backward", "both"])
    sp.add_argument("--top-k", type=int, default=10)

    # bibtex command
    sp = subparsers.add_parser("bibtex", help="Generate BibTeX for a paper")
    sp.add_argument("paper_id", help="Paper ID")

    # recommend command
    sp = subparsers.add_parser("recommend", help="Get paper recommendations")
    sp.add_argument("paper_id", help="Seed paper ID")
    sp.add_argument("--limit", type=int, default=10)

    # survey command
    sp = subparsers.add_parser("survey", help="Run structured multi-query survey")
    sp.add_argument("--queries-file", type=Path, required=True, help="YAML file with search queries")
    sp.add_argument("--output-dir", type=Path, required=True, help="Output directory")

    args = parser.parse_args()

    if args.command == "search":
        papers = []
        if args.source in ("s2", "both"):
            papers.extend(s2_search(args.query, limit=args.limit, year_range=args.year))
        if args.source in ("arxiv", "both"):
            papers.extend(arxiv_search(args.query, limit=args.limit))

        # Deduplicate by title
        seen = set()
        unique = []
        for p in papers:
            key = p.title.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(p)

        unique.sort(key=lambda p: p.citation_count, reverse=True)
        for p in unique:
            print(p.to_markdown(include_abstract=args.abstracts))

    elif args.command == "cite":
        result = citation_chain(args.paper_id, depth=args.depth, direction=args.direction, top_k=args.top_k)
        seed = result["seed"]
        print(f"# Citation Chain: {seed.title} ({seed.year})")
        print(f"Citations: {seed.citation_count}")
        print()

        if result["forward"]:
            for d, papers in result["forward"].items():
                print(f"## Forward Citations (depth {d})")
                for p in papers:
                    print(p.to_markdown())
                print()

        if result["backward"]:
            for d, papers in result["backward"].items():
                print(f"## Backward References (depth {d})")
                for p in papers:
                    print(p.to_markdown())
                print()

    elif args.command == "bibtex":
        paper = s2_paper(args.paper_id)
        print(paper.to_bibtex())

    elif args.command == "recommend":
        papers = s2_recommendations(args.paper_id, limit=args.limit)
        for p in papers:
            print(p.to_markdown())

    elif args.command == "survey":
        import yaml
        queries = yaml.safe_load(args.queries_file.read_text())
        if isinstance(queries, dict):
            queries = queries.get("queries", [])
        run_survey(queries, args.output_dir)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
