#!/usr/bin/env python3
"""Research Intelligence Engine — run all detectors.

Usage:
    python3 -m scripts.research-intel.run_all --help
    python3 -m scripts.research-intel.run_all --api http://localhost:3001 --limit 50 --json
    python3 scripts/research-intel/run_all.py --api http://localhost:3001 --limit 50 --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

# Support both `python3 -m scripts.research-intel.run_all` and direct execution
try:
    from .gap_detector import detect as detect_gaps
except ImportError:
    # Direct script execution — add package dir to path and import directly
    import pathlib
    _pkg_dir = str(pathlib.Path(__file__).resolve().parent)
    if _pkg_dir not in sys.path:
        sys.path.insert(0, _pkg_dir)
    from gap_detector import detect as detect_gaps  # type: ignore


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Research Intelligence Engine — run all detectors."
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
        "--input", metavar="FILE",
        help="Read papers from a local JSON file instead of the API",
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
    else:
        papers = fetch_papers(args.api, args.limit)

    if not papers:
        print("No papers found.", file=sys.stderr)
        sys.exit(1)

    print(f"Running research-intel detectors on {len(papers)} papers...", file=sys.stderr)

    # Run all detectors
    all_signals: list[dict] = []

    gap_signals = detect_gaps(papers)
    all_signals.extend(gap_signals)
    print(f"  gap_detector: {len(gap_signals)} signals", file=sys.stderr)

    # Future detectors:
    # trend_signals = detect_trends(papers)
    # all_signals.extend(trend_signals)
    # contrarian_signals = detect_contrarian(papers)
    # all_signals.extend(contrarian_signals)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "papers_analyzed": len(papers),
        "total_signals": len(all_signals),
        "detectors_run": ["gap_detector"],
        "signals": all_signals,
    }

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable summary
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Research Intelligence: {len(all_signals)} signals from {len(papers)} papers", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)

        by_type: dict[str, int] = {}
        for sig in all_signals:
            st = sig.get("signal_type", "unknown")
            by_type[st] = by_type.get(st, 0) + 1

        for st, count in sorted(by_type.items()):
            print(f"  {st}: {count}", file=sys.stderr)

        print(f"\nUse --json for full output.", file=sys.stderr)


if __name__ == "__main__":
    main()
