#!/usr/bin/env python3
"""Compass Report CLI — read JSON from stdin and emit a Markdown report.

Usage:
    python3 scripts/compass/run_all.py --json | python3 scripts/compass/report_cli.py
    python3 scripts/compass/run_all.py --json | python3 scripts/compass/report_cli.py > docs/compass/reports/2026-03-31.md
    python3 scripts/compass/report_cli.py < compass_output.json
"""

from __future__ import annotations

import json
import sys

# Support both `python3 -m scripts.compass.report_cli` and direct execution
try:
    from .report import generate_report
except ImportError:
    import pathlib
    _pkg_dir = str(pathlib.Path(__file__).resolve().parent)
    if _pkg_dir not in sys.path:
        sys.path.insert(0, _pkg_dir)
    from report import generate_report  # type: ignore


def main() -> None:
    if sys.stdin.isatty():
        print(
            "Usage: python3 scripts/compass/run_all.py --json | python3 scripts/compass/report_cli.py",
            file=sys.stderr,
        )
        print("  Reads Compass JSON from stdin and writes Markdown to stdout.", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(1)

    report = generate_report(data)
    print(report, end="")


if __name__ == "__main__":
    main()
