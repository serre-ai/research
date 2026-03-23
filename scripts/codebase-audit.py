#!/usr/bin/env python3
"""Codebase audit scanner — produces a structured JSON report of codebase health.

Scans for:
  - Code TODOs/FIXME/HACK/XXX in .ts, .py, .tex files
  - Stale project status.yaml files (>7 days old)
  - Paper TODOs in .tex files (% TODO comments)
  - Test coverage gaps (missing __tests__/*.test.ts)
  - Security patterns (hardcoded keys, tracked .env files)

Usage:
    python scripts/codebase-audit.py [--json] [--section todos|security|tests|staleness]
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

# Find repo root: walk up from this script's location to find .git
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

EXCLUDE_DIRS = {"node_modules", "dist", ".venv", ".git", ".next", "__pycache__", ".claude"}
CODE_EXTENSIONS = {".ts", ".py", ".tex"}
TODO_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
PAPER_TODO_PATTERN = re.compile(r"^%\s*TODO\b", re.IGNORECASE)

# Security patterns
SECURITY_PATTERNS = [
    (re.compile(r"\bsk-[a-zA-Z0-9]{20,}"), "Hardcoded API key (sk-...)", "critical"),
    (re.compile(r"\blin_api_[a-zA-Z0-9]{20,}"), "Hardcoded Linear API key", "critical"),
    (re.compile(r"""(?:key|token|secret|password)\s*=\s*["'][^"']{8,}["']""", re.IGNORECASE), "Hardcoded secret assignment", "warning"),
]


# ── Helpers ──────────────────────────────────────────────────────────────────


def walk_files(root, extensions=None):
    """Yield Path objects for files under root, skipping excluded dirs."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories (modifying dirnames in-place)
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if extensions is None or fpath.suffix in extensions:
                yield fpath


def relative(path):
    """Return path relative to repo root."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# ── Scanners ─────────────────────────────────────────────────────────────────


def scan_code_todos():
    """Find TODO/FIXME/HACK/XXX in code files."""
    findings = []
    severity_map = {
        "todo": "info",
        "fixme": "warning",
        "hack": "warning",
        "xxx": "warning",
    }

    for fpath in walk_files(REPO_ROOT, CODE_EXTENSIONS):
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    match = TODO_PATTERN.search(line)
                    if match:
                        tag = match.group(1).lower()
                        findings.append({
                            "file": relative(fpath),
                            "line": lineno,
                            "text": line.strip(),
                            "severity": severity_map.get(tag, "info"),
                        })
        except OSError:
            continue

    return findings


def scan_stale_projects():
    """Check status.yaml freshness in each project."""
    findings = []
    projects_dir = REPO_ROOT / "projects"
    if not projects_dir.is_dir():
        return findings

    now = datetime.datetime.now(datetime.timezone.utc)

    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        status_file = project_dir / "status.yaml"
        if not status_file.exists():
            findings.append({
                "project": project_dir.name,
                "last_updated": None,
                "days_stale": None,
                "note": "No status.yaml found",
            })
            continue

        # Parse the updated field without importing yaml
        updated_str = None
        try:
            with open(status_file, "r") as f:
                for line in f:
                    line_stripped = line.strip()
                    if line_stripped.startswith("updated:"):
                        val = line_stripped.split(":", 1)[1].strip().strip("'\"")
                        updated_str = val
                        break
        except OSError:
            continue

        if not updated_str:
            findings.append({
                "project": project_dir.name,
                "last_updated": None,
                "days_stale": None,
                "note": "No 'updated:' field in status.yaml",
            })
            continue

        # Try parsing the date
        try:
            # Handle YYYY-MM-DD or ISO datetime
            if "T" in updated_str:
                updated = datetime.datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
            else:
                updated = datetime.datetime.strptime(updated_str[:10], "%Y-%m-%d").replace(
                    tzinfo=datetime.timezone.utc
                )
        except (ValueError, TypeError):
            findings.append({
                "project": project_dir.name,
                "last_updated": updated_str,
                "days_stale": None,
                "note": f"Could not parse date: {updated_str}",
            })
            continue

        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=datetime.timezone.utc)

        days_stale = (now - updated).days
        if days_stale > 7:
            findings.append({
                "project": project_dir.name,
                "last_updated": updated_str,
                "days_stale": days_stale,
            })

    return findings


def scan_paper_todos():
    """Find % TODO comments in .tex files."""
    findings = []
    for fpath in walk_files(REPO_ROOT, {".tex"}):
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    if PAPER_TODO_PATTERN.search(line):
                        findings.append({
                            "file": relative(fpath),
                            "line": lineno,
                            "text": line.strip(),
                        })
        except OSError:
            continue

    return findings


def scan_test_coverage():
    """Check for missing test files in orchestrator and site-next."""
    results = {"covered": 0, "uncovered": 0, "files": []}

    scan_dirs = [
        REPO_ROOT / "orchestrator" / "src",
        REPO_ROOT / "site-next" / "src",
    ]

    for src_dir in scan_dirs:
        if not src_dir.is_dir():
            continue

        for fpath in walk_files(src_dir, {".ts"}):
            # Skip test files, type files, and index re-exports
            rel = relative(fpath)
            if "__tests__" in rel or ".test." in fpath.name or ".spec." in fpath.name:
                continue
            if fpath.suffix != ".ts" and fpath.suffix != ".tsx":
                continue

            # Check for corresponding test file
            # Look in __tests__ dir relative to the file's parent
            test_dir = fpath.parent / "__tests__"
            stem = fpath.stem
            has_tests = False

            if test_dir.is_dir():
                for test_candidate in [f"{stem}.test.ts", f"{stem}.test.tsx", f"{stem}.spec.ts"]:
                    if (test_dir / test_candidate).exists():
                        has_tests = True
                        break

            entry = {"file": rel, "has_tests": has_tests}
            results["files"].append(entry)
            if has_tests:
                results["covered"] += 1
            else:
                results["uncovered"] += 1

    return results


def scan_security():
    """Check for hardcoded secrets and tracked .env files."""
    findings = []

    # Check for security patterns in code files
    for fpath in walk_files(REPO_ROOT, CODE_EXTENSIONS):
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    for pattern, description, severity in SECURITY_PATTERNS:
                        if pattern.search(line):
                            findings.append({
                                "file": relative(fpath),
                                "line": lineno,
                                "pattern": description,
                                "severity": severity,
                            })
        except OSError:
            continue

    # Check for .env files tracked in git
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            for tracked_file in result.stdout.strip().split("\n"):
                if tracked_file and (
                    tracked_file.endswith(".env")
                    or "/.env" in tracked_file
                    or tracked_file == ".env"
                ):
                    findings.append({
                        "file": tracked_file,
                        "line": None,
                        "pattern": ".env file tracked in git",
                        "severity": "critical",
                    })
    except OSError:
        pass

    return findings


# ── Main ─────────────────────────────────────────────────────────────────────

SECTION_MAP = {
    "todos": ("code_todos", scan_code_todos),
    "security": ("security", scan_security),
    "tests": ("test_coverage", scan_test_coverage),
    "staleness": ("stale_projects", scan_stale_projects),
    "paper-todos": ("paper_todos", scan_paper_todos),
}


def main():
    parser = argparse.ArgumentParser(description="Codebase health audit scanner")
    parser.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Output as JSON (default)",
    )
    parser.add_argument(
        "--section",
        choices=["todos", "security", "tests", "staleness", "paper-todos"],
        help="Run only a specific section",
    )
    args = parser.parse_args()

    report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
    }

    sections_to_run = [args.section] if args.section else list(SECTION_MAP.keys())
    total = 0
    critical = 0
    warning = 0
    info = 0

    for section_name in sections_to_run:
        key, scanner = SECTION_MAP[section_name]
        result = scanner()
        report[key] = result

        # Count findings
        if isinstance(result, list):
            total += len(result)
            for item in result:
                sev = item.get("severity", "info")
                if sev == "critical":
                    critical += 1
                elif sev == "warning":
                    warning += 1
                else:
                    info += 1
        elif isinstance(result, dict) and "uncovered" in result:
            # test_coverage
            total += result["uncovered"]
            info += result["uncovered"]

    report["summary"] = {
        "total_findings": total,
        "critical": critical,
        "warning": warning,
        "info": info,
    }

    # Move summary to front by rebuilding dict
    ordered = {
        "timestamp": report["timestamp"],
        "repo_root": report["repo_root"],
        "summary": report["summary"],
    }
    for k, v in report.items():
        if k not in ordered:
            ordered[k] = v

    print(json.dumps(ordered, indent=2))


if __name__ == "__main__":
    main()
