#!/usr/bin/env python3
"""Compass — run all detectors.

Usage:
    python3 -m scripts.compass.run_all --help
    python3 -m scripts.compass.run_all --api http://localhost:3001 --limit 50 --json
    python3 scripts/compass/run_all.py --api http://localhost:3001 --limit 50 --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

# Support both `python3 -m scripts.compass.run_all` and direct execution
try:
    from .gap_detector import detect as detect_gaps
    from .trend_detector import detect as detect_trends
    from .portfolio_optimizer import detect as detect_portfolio
    from .contrarian_detector import detect as detect_contrarian
    from .frontier_scanner import detect as detect_frontier
    from .reviewer_model import detect as detect_reviewer
    from .synthesize import synthesize
    from .db import fetch_papers_with_embeddings
    from .report import generate_report
except ImportError:
    # Direct script execution — add package dir to path and import directly
    import pathlib
    _pkg_dir = str(pathlib.Path(__file__).resolve().parent)
    if _pkg_dir not in sys.path:
        sys.path.insert(0, _pkg_dir)
    from gap_detector import detect as detect_gaps  # type: ignore
    from trend_detector import detect as detect_trends  # type: ignore
    from portfolio_optimizer import detect as detect_portfolio  # type: ignore
    from contrarian_detector import detect as detect_contrarian  # type: ignore
    from frontier_scanner import detect as detect_frontier  # type: ignore
    from reviewer_model import detect as detect_reviewer  # type: ignore
    from synthesize import synthesize  # type: ignore
    from db import fetch_papers_with_embeddings  # type: ignore
    from report import generate_report  # type: ignore

# Citation analyzer — optional, requires S2 API access
_detect_citation = None
try:
    try:
        from .citation_analyzer import detect as _detect_citation
    except ImportError:
        from citation_analyzer import detect as _detect_citation  # type: ignore
except Exception:
    pass


DEFAULT_API_URL = "http://localhost:3001"


def fetch_papers(api_url: str, limit: int = 200) -> list[dict]:
    """Fetch papers from the Deepwork literature API."""
    api_key = os.environ.get("DEEPWORK_API_KEY", "")
    url = f"{api_url}/api/literature/papers?limit={limit}"
    req = Request(url)
    if api_key:
        req.add_header("X-Api-Key", api_key)

    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except URLError as e:
        print(f"Error fetching papers from {url}: {e}", file=sys.stderr)
        print("Hint: set DEEPWORK_API_KEY and ensure the API is running.", file=sys.stderr)
        sys.exit(1)


def store_signals(signals: list[dict], db_url: str) -> int:
    """Write signals to the research_signals PostgreSQL table."""
    try:
        import psycopg2  # type: ignore
    except ImportError:
        # Fall back to subprocess psql
        return _store_via_psql(signals, db_url)

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    stored = 0
    for sig in signals:
        try:
            cur.execute(
                """INSERT INTO research_signals
                   (detector, signal_type, title, description, confidence,
                    source_papers, source_claims, topics, relevance, timing_score, metadata)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    sig.get("detector", ""),
                    sig.get("signal_type", ""),
                    sig.get("title", ""),
                    sig.get("description", ""),
                    sig.get("confidence", 0.5),
                    sig.get("source_papers", []),
                    sig.get("source_claims", []),
                    sig.get("topics", []),
                    sig.get("relevance", 0),
                    sig.get("timing_score", 0),
                    json.dumps(sig.get("metadata", {})),
                ),
            )
            stored += 1
        except Exception as e:
            print(f"  Warning: failed to store signal: {e}", file=sys.stderr)
    conn.commit()
    cur.close()
    conn.close()
    return stored


def _store_via_psql(signals: list[dict], db_url: str) -> int:
    """Fallback: store signals via psql subprocess (no psycopg2 needed)."""
    import subprocess
    stored = 0
    for sig in signals:
        sql = (
            f"INSERT INTO research_signals "
            f"(detector, signal_type, title, description, confidence, "
            f"source_papers, topics, relevance, timing_score, metadata) "
            f"VALUES ("
            f"'{sig.get('detector', '')}', "
            f"'{sig.get('signal_type', '')}', "
            f"$${sig.get('title', '')}$$, "
            f"$${sig.get('description', '')}$$, "
            f"{sig.get('confidence', 0.5)}, "
            f"ARRAY{sig.get('source_papers', [])}::TEXT[], "
            f"ARRAY{sig.get('topics', [])}::TEXT[], "
            f"{sig.get('relevance', 0)}, "
            f"{sig.get('timing_score', 0)}, "
            f"'{json.dumps(sig.get('metadata', {}))}'::jsonb"
            f");"
        )
        result = subprocess.run(
            ["psql", db_url, "-c", sql],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            stored += 1
    return stored


def store_opportunities(opportunities: list[dict], db_url: str) -> int:
    """Write synthesized opportunities to the research_opportunities PostgreSQL table."""
    try:
        import psycopg2  # type: ignore
    except ImportError:
        return _store_opportunities_via_psql(opportunities, db_url)

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    stored = 0
    for opp in opportunities:
        try:
            cur.execute(
                """INSERT INTO research_opportunities
                   (title, thesis, composite_score, signal_ids, detectors_hit, topics,
                    target_venue, portfolio_fit, timing_urgency, venue_receptivity,
                    rationale, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    opp.get("title", ""),
                    opp.get("thesis", ""),
                    opp.get("composite_score", 0),
                    opp.get("signal_ids", []),
                    opp.get("detectors_hit", []),
                    opp.get("topics", []),
                    opp.get("target_venue"),
                    opp.get("portfolio_fit", 0),
                    opp.get("timing_urgency", 0),
                    opp.get("venue_receptivity", 0),
                    opp.get("rationale", ""),
                    opp.get("status", "new"),
                ),
            )
            stored += 1
        except Exception as e:
            print(f"  Warning: failed to store opportunity: {e}", file=sys.stderr)
    conn.commit()
    cur.close()
    conn.close()
    return stored


def _store_opportunities_via_psql(opportunities: list[dict], db_url: str) -> int:
    """Fallback: store opportunities via psql subprocess (no psycopg2 needed)."""
    import subprocess
    stored = 0
    for opp in opportunities:
        signal_ids = opp.get('signal_ids', [])
        sql = (
            f"INSERT INTO research_opportunities "
            f"(title, thesis, composite_score, signal_ids, detectors_hit, topics, "
            f"target_venue, portfolio_fit, timing_urgency, venue_receptivity, "
            f"rationale, status) "
            f"VALUES ("
            f"$${opp.get('title', '')}$$, "
            f"$${opp.get('thesis', '')}$$, "
            f"{opp.get('composite_score', 0)}, "
            f"ARRAY{signal_ids}::TEXT[], "
            f"ARRAY{opp.get('detectors_hit', [])}::TEXT[], "
            f"ARRAY{opp.get('topics', [])}::TEXT[], "
            f"{'NULL' if opp.get('target_venue') is None else repr(opp['target_venue'])}, "
            f"{opp.get('portfolio_fit', 0)}, "
            f"{opp.get('timing_urgency', 0)}, "
            f"{opp.get('venue_receptivity', 0)}, "
            f"$${opp.get('rationale', '')}$$, "
            f"'{opp.get('status', 'new')}'"
            f");"
        )
        result = subprocess.run(
            ["psql", db_url, "-c", sql],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            stored += 1
    return stored


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compass — run all detectors."
    )
    parser.add_argument(
        "--api", default=DEFAULT_API_URL,
        help=f"API base URL (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--limit", type=int, default=200,
        help="Max papers to fetch (default: 200)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output signals as JSON to stdout",
    )
    parser.add_argument(
        "--store", action="store_true",
        help="Write signals to the research_signals DB table",
    )
    parser.add_argument(
        "--db-url", metavar="URL",
        help="PostgreSQL connection URL (default: DATABASE_URL env var)",
    )
    parser.add_argument(
        "--input", metavar="FILE",
        help="Read papers from a local JSON file instead of the API",
    )
    parser.add_argument(
        "--embeddings", action="store_true",
        help="Use pgvector embeddings for similarity (requires DATABASE_URL)",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Generate a Markdown narrative report (to stdout and docs/compass/reports/)",
    )

    args = parser.parse_args()

    # Fetch papers
    if args.input:
        try:
            with open(args.input) as f:
                data = json.load(f)
            if isinstance(data, list):
                papers = data
            elif isinstance(data, dict) and "papers" in data:
                papers = data["papers"]
            else:
                papers = data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {args.input}: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.embeddings:
        papers = fetch_papers_with_embeddings(limit=args.limit)
    else:
        papers = fetch_papers(args.api, args.limit)

    if not papers:
        print("No papers found.", file=sys.stderr)
        sys.exit(1)

    print(f"Running compass detectors on {len(papers)} papers...", file=sys.stderr)

    # Run all detectors
    all_signals: list[dict] = []

    gap_signals = detect_gaps(papers)
    all_signals.extend(gap_signals)
    print(f"  gap_detector: {len(gap_signals)} signals", file=sys.stderr)

    trend_signals = detect_trends(papers)
    all_signals.extend(trend_signals)
    print(f"  trend_detector: {len(trend_signals)} signals", file=sys.stderr)

    portfolio_signals = detect_portfolio(papers)
    all_signals.extend(portfolio_signals)
    print(f"  portfolio_optimizer: {len(portfolio_signals)} signals", file=sys.stderr)

    contrarian_signals = detect_contrarian(papers)
    all_signals.extend(contrarian_signals)
    print(f"  contrarian_detector: {len(contrarian_signals)} signals", file=sys.stderr)

    frontier_signals = detect_frontier(papers)
    all_signals.extend(frontier_signals)
    print(f"  frontier_scanner: {len(frontier_signals)} signals", file=sys.stderr)

    reviewer_signals = detect_reviewer(papers)
    all_signals.extend(reviewer_signals)
    print(f"  reviewer_model: {len(reviewer_signals)} signals", file=sys.stderr)

    # Citation graph analysis (optional — needs S2 API)
    if _detect_citation is not None:
        try:
            citation_signals = _detect_citation(papers)
            all_signals.extend(citation_signals)
            print(f"  citation_analyzer: {len(citation_signals)} signals", file=sys.stderr)
        except Exception as e:
            print(f"  citation_analyzer: skipped ({e})", file=sys.stderr)
    else:
        print("  citation_analyzer: not available (import failed)", file=sys.stderr)

    # Synthesize opportunities
    opportunities = synthesize(all_signals)
    print(f"  synthesized: {len(opportunities)} opportunities", file=sys.stderr)

    # Store to DB if requested
    if args.store and all_signals:
        db_url = args.db_url or os.environ.get("DATABASE_URL", "")
        if not db_url:
            print("Error: --store requires --db-url or DATABASE_URL env var", file=sys.stderr)
            sys.exit(1)
        stored = store_signals(all_signals, db_url)
        print(f"  stored {stored} signals to research_signals table", file=sys.stderr)
        if opportunities:
            opp_stored = store_opportunities(opportunities, db_url)
            print(f"  stored {opp_stored} opportunities to research_opportunities table", file=sys.stderr)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "papers_analyzed": len(papers),
        "total_signals": len(all_signals),
        "detectors_run": ["gap_detector", "trend_detector", "portfolio_optimizer", "contrarian_detector", "frontier_scanner", "reviewer_model", "citation_analyzer"],
        "signals": all_signals,
        "opportunities": opportunities,
    }

    if args.report:
        report_md = generate_report(result)
        # Save to docs/compass/reports/YYYY-MM-DD.md
        report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        report_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "docs", "compass", "reports",
        )
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"{report_date}.md")
        with open(report_path, "w") as f:
            f.write(report_md)
        print(report_md, end="")
        print(f"\nReport saved to {report_path}", file=sys.stderr)
    elif args.json_output:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable summary
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Compass: {len(all_signals)} signals from {len(papers)} papers", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)

        by_type: dict[str, int] = {}
        for sig in all_signals:
            st = sig.get("signal_type", "unknown")
            by_type[st] = by_type.get(st, 0) + 1

        for st, count in sorted(by_type.items()):
            print(f"  {st}: {count}", file=sys.stderr)

        if opportunities:
            print(f"\nTop opportunities:", file=sys.stderr)
            for i, opp in enumerate(opportunities[:3], 1):
                score = opp.get("composite_score", 0)
                title = opp.get("title", "Untitled")
                detectors = ", ".join(opp.get("detectors_hit", []))
                print(f"  {i}. [{score}] {title}", file=sys.stderr)
                print(f"     Detectors: {detectors}", file=sys.stderr)

        print(f"\nUse --json for full output.", file=sys.stderr)


if __name__ == "__main__":
    main()
