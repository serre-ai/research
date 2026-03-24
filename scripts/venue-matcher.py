#!/usr/bin/env python3
"""Venue matcher — scores project-venue fit and reports deadlines.

Usage:
    python3 scripts/venue-matcher.py                           # all projects
    python3 scripts/venue-matcher.py --project reasoning-gaps  # single project
    python3 scripts/venue-matcher.py --json                    # JSON output
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Minimal YAML loader — used only when PyYAML is not available.
# Handles the subset of YAML used by our venue and status files:
#   scalar values, nested dicts (indentation-based), lists (- item).
# ---------------------------------------------------------------------------

def _mini_yaml_load(text: str) -> dict:
    """Parse a *very* simple YAML document into a Python dict.

    Supports:
      - key: value scalars (strings, numbers, booleans)
      - nested dicts via indentation (2-space)
      - sequences with ``- item`` syntax
      - quoted strings
      - comments (# ...)
      - multi-line block scalars (|) treated as single string
    Does NOT support anchors, aliases, flow style, or complex keys.
    """
    lines = text.splitlines()
    root: dict = {}
    stack: list[tuple[int, dict | list]] = [(-1, root)]

    i = 0
    while i < len(lines):
        raw = lines[i]
        # strip trailing comment only if not inside quotes
        line = raw.split(" #")[0].rstrip() if " #" in raw and raw.count('"') % 2 == 0 else raw.rstrip()
        stripped = line.lstrip()
        i += 1

        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(stripped)

        # pop stack to current indent
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        _, parent = stack[-1]

        # list item
        if stripped.startswith("- "):
            value = _yaml_scalar(stripped[2:].strip())
            if isinstance(parent, list):
                parent.append(value)
            elif isinstance(parent, dict):
                # find the key that owns this list
                # the list should already be created; append to it
                # This case shouldn't happen if structure is correct
                pass
            continue

        # key: value
        m = re.match(r'^([A-Za-z0-9_.#-]+)\s*:\s*(.*)', stripped)
        if not m:
            continue

        key = m.group(1)
        val_str = m.group(2).strip()

        if val_str == "" or val_str == "|":
            # Could be a nested dict or list — peek ahead
            if i < len(lines):
                next_stripped = lines[i].lstrip()
                next_indent = len(lines[i]) - len(lines[i].lstrip())
                if next_stripped.startswith("- "):
                    child: dict | list = []
                else:
                    child = {}
                if isinstance(parent, dict):
                    parent[key] = child
                stack.append((indent, child))
            else:
                if isinstance(parent, dict):
                    parent[key] = None
        else:
            if isinstance(parent, dict):
                parent[key] = _yaml_scalar(val_str)

    return root


def _yaml_scalar(s: str):
    """Convert a YAML scalar string to a Python value."""
    if not s:
        return None
    # strip quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    low = s.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~"):
        return None
    # try number
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


# ---------------------------------------------------------------------------
# YAML loading — prefer PyYAML, fall back to mini parser
# ---------------------------------------------------------------------------

try:
    import yaml as _yaml

    def load_yaml(path: Path) -> dict:
        with open(path) as f:
            return _yaml.safe_load(f) or {}
except ImportError:
    def load_yaml(path: Path) -> dict:
        return _mini_yaml_load(path.read_text())


# ---------------------------------------------------------------------------
# Resolve repo root — works from any subdirectory
# ---------------------------------------------------------------------------

def find_repo_root() -> Path:
    """Walk up from cwd (or script location) to find the repo root."""
    # try from cwd first
    p = Path.cwd()
    for _ in range(10):
        if (p / "shared").is_dir() and (p / "projects").is_dir():
            return p
        p = p.parent
    # try from script location
    p = Path(__file__).resolve().parent.parent
    if (p / "shared").is_dir() and (p / "projects").is_dir():
        return p
    print("Error: cannot find repo root (expected shared/ and projects/ dirs)", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Load venues
# ---------------------------------------------------------------------------

def load_venues(root: Path) -> list[dict]:
    """Load all venue YAML files from shared/config/venues/."""
    venues_dir = root / "shared" / "config" / "venues"
    if not venues_dir.is_dir():
        print(f"Error: venues directory not found: {venues_dir}", file=sys.stderr)
        sys.exit(1)

    venues = []
    for yf in sorted(venues_dir.glob("*.yaml")):
        if yf.name in ("index.yaml", "research-topics.yaml"):
            continue
        data = load_yaml(yf)
        if not data or "name" not in data:
            continue
        venues.append(data)
    return venues


# ---------------------------------------------------------------------------
# Load research-topic taxonomy
# ---------------------------------------------------------------------------

def load_topic_taxonomy(root: Path) -> dict[str, list[str]]:
    """Return {topic_key: [keyword, ...]} from research-topics.yaml."""
    path = root / "shared" / "config" / "research-topics.yaml"
    if not path.exists():
        return {}
    data = load_yaml(path)
    topics = data.get("topics", {})
    result = {}
    for key, info in topics.items():
        if isinstance(info, dict):
            result[key] = [kw.lower() for kw in info.get("keywords", [])]
        else:
            result[key] = []
    return result


# ---------------------------------------------------------------------------
# Load projects
# ---------------------------------------------------------------------------

def load_projects(root: Path, project_filter: str | None = None) -> list[dict]:
    """Load project status.yaml files."""
    projects_dir = root / "projects"
    projects = []
    for status_file in sorted(projects_dir.glob("*/status.yaml")):
        pname = status_file.parent.name
        if project_filter and pname != project_filter:
            continue
        data = load_yaml(status_file)
        if not data:
            continue
        data["_name"] = pname
        # skip non-research projects (e.g. platform-engineering)
        is_research = (
            data.get("key_terms")
            or data.get("venue")
            or data.get("key_references")
            or data.get("paper_status")
        )
        if not is_research:
            continue
        projects.append(data)
    return projects


# ---------------------------------------------------------------------------
# Topic matching
# ---------------------------------------------------------------------------

def match_topics(project: dict, venue: dict, taxonomy: dict[str, list[str]]) -> int:
    """Score topic overlap (0-2 points).

    Maps project key_terms against the research-topics taxonomy, then counts
    how many of the matched topic keys have ``high`` in the venue's topic_fit.
    """
    key_terms = project.get("key_terms", [])
    if not key_terms:
        # Fall back: use title words
        title = project.get("title", "")
        key_terms = [title.lower()]

    # Determine which taxonomy topics the project matches
    project_topics: set[str] = set()
    terms_lower = [t.lower() if isinstance(t, str) else "" for t in key_terms]
    joined = " ".join(terms_lower)

    for topic_key, keywords in taxonomy.items():
        for kw in keywords:
            if kw in joined:
                project_topics.add(topic_key)
                break

    # Count matches with venue's high-fit topics
    venue_fit = venue.get("topic_fit", {})
    high_matches = 0
    for topic_key in project_topics:
        if venue_fit.get(topic_key) == "high":
            high_matches += 1

    if high_matches >= 3:
        return 2
    elif high_matches >= 1:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Contribution style matching
# ---------------------------------------------------------------------------

def match_contribution(project: dict, venue: dict) -> int:
    """Score contribution style fit (0-1 point).

    Infers project contribution type from its phase/status and matches
    against venue contribution_preferences.
    """
    prefs = venue.get("contribution_preferences", {})
    if not prefs:
        return 0

    # Build a rich text corpus from all available project fields
    parts = [
        str(project.get("phase", "")),
        str(project.get("title", "")),
        str(project.get("notes", "")),
        str(project.get("current_focus", "")),
    ]
    # Include progress section keys and notes
    progress = project.get("progress", {})
    if isinstance(progress, dict):
        parts.extend(str(k) for k in progress.keys())
        for v in progress.values():
            if isinstance(v, dict):
                parts.append(str(v.get("notes", "")))
    # Include key_terms
    for term in project.get("key_terms", []):
        parts.append(str(term))
    corpus = " ".join(parts).lower()

    # Infer contribution style
    styles: list[str] = []

    # Check for theory + empirical (most of our projects)
    has_theory = any(w in corpus for w in
                     ["theorem", "formal", "proof", "theory", "impossibility", "complexity"])
    has_empirical = any(w in corpus for w in
                        ["experiment", "empirical", "benchmark", "evaluation", "eval"])
    has_survey = any(w in corpus for w in
                     ["taxonomy", "survey", "categoriz", "failure mode"])
    has_benchmark = any(w in corpus for w in
                        ["benchmark", "diagnostic task", "suite"])

    if has_theory and has_empirical:
        styles.append("theory_with_empirical")
    elif has_theory:
        styles.append("pure_theory")
    if has_empirical and not has_theory:
        styles.append("empirical_study")
    if has_survey:
        styles.append("survey_taxonomy")
    if has_benchmark:
        styles.append("benchmark_paper")

    # Best match
    for style in styles:
        if prefs.get(style) == "high":
            return 1

    return 0


# ---------------------------------------------------------------------------
# Deadline feasibility
# ---------------------------------------------------------------------------

def parse_deadline(venue: dict) -> tuple[date | None, bool]:
    """Return (deadline_date, is_estimated) from a venue dict."""
    dl = venue.get("deadline")
    if not dl:
        return None, False
    estimated = venue.get("deadline_estimated", False)
    try:
        d = datetime.strptime(str(dl), "%Y-%m-%d").date()
        return d, estimated
    except ValueError:
        return None, estimated


def score_deadline(days: int) -> int:
    """Score deadline feasibility (0-2 points).

    30-60 days  -> 2 (urgent but feasible)
    60-180 days -> 2 (comfortable)
    180-365 days -> 1 (plan ahead)
    >365 or passed -> 0
    """
    if days < 0:
        return 0  # passed
    if 30 <= days <= 180:
        return 2
    if 180 < days <= 365:
        return 1
    if 0 <= days < 30:
        return 0  # too close — probably can't submit
    return 0  # > 365


def deadline_label(days: int) -> str:
    """Return a human-readable deadline annotation."""
    if days < 0:
        return "[PASSED]"
    if days <= 14:
        return "[CRITICAL]"
    if days <= 60:
        return "[URGENT]"
    if days <= 180:
        return ""
    return ""


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_match(project: dict, venue: dict, taxonomy: dict[str, list[str]], today: date) -> dict:
    """Compute a full match record for a project-venue pair."""
    topic_score = match_topics(project, venue, taxonomy)
    contrib_score = match_contribution(project, venue)

    dl_date, estimated = parse_deadline(venue)
    if dl_date:
        days = (dl_date - today).days
        dl_score = score_deadline(days)
    else:
        days = 9999
        dl_score = 0

    total = topic_score + contrib_score + dl_score

    return {
        "project": project["_name"],
        "venue": venue.get("name", venue.get("key", "?")),
        "venue_key": venue.get("key", "?"),
        "stars": total,
        "topic_score": topic_score,
        "contribution_score": contrib_score,
        "deadline_score": dl_score,
        "deadline": str(dl_date) if dl_date else None,
        "deadline_estimated": estimated,
        "days_to_deadline": days if dl_date else None,
        "deadline_label": deadline_label(days) if dl_date else "",
    }


def stars_str(n: int) -> str:
    """Return star display like ★★★★☆."""
    filled = min(n, 5)
    return "★" * filled + "☆" * (5 - filled)


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_text(matches_by_project: dict[str, list[dict]], today: date) -> str:
    """Format the text report."""
    lines = [
        f"VENUE MATCH REPORT — {today.isoformat()}",
        "═" * 52,
        "",
    ]

    for project_name, matches in matches_by_project.items():
        lines.append(project_name)
        for m in matches:
            dl_str = ""
            if m["deadline"]:
                prefix = "~" if m["deadline_estimated"] else ""
                dl_parts = m["deadline"].split("-")
                # Format: Mon DD or ~Mon DD
                try:
                    dl_date = datetime.strptime(m["deadline"], "%Y-%m-%d").date()
                    dl_str = f"  deadline: {prefix}{dl_date.strftime('%b %-d')}"
                except ValueError:
                    dl_str = f"  deadline: {prefix}{m['deadline']}"
                if m["days_to_deadline"] is not None:
                    dl_str += f" ({m['days_to_deadline']} days)"
            label = f"  {m['deadline_label']}" if m["deadline_label"] else ""
            lines.append(f"  {m['venue']:<16}{stars_str(m['stars'])}{dl_str}{label}")
        lines.append("")

    return "\n".join(lines)


def format_json(matches_by_project: dict[str, list[dict]], today: date) -> str:
    """Format the JSON report."""
    output = {
        "date": today.isoformat(),
        "projects": {},
    }
    for project_name, matches in matches_by_project.items():
        output["projects"][project_name] = [
            {
                "venue": m["venue"],
                "venue_key": m["venue_key"],
                "stars": m["stars"],
                "scores": {
                    "topic": m["topic_score"],
                    "contribution": m["contribution_score"],
                    "deadline": m["deadline_score"],
                },
                "deadline": m["deadline"],
                "deadline_estimated": m["deadline_estimated"],
                "days_to_deadline": m["days_to_deadline"],
                "label": m["deadline_label"],
            }
            for m in matches
        ]
    return json.dumps(output, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Match research projects to publication venues.")
    parser.add_argument("--project", "-p", help="Filter to a single project by name")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    root = find_repo_root()
    today = date.today()

    venues = load_venues(root)
    if not venues:
        print("No venue profiles found in shared/config/venues/", file=sys.stderr)
        sys.exit(1)

    taxonomy = load_topic_taxonomy(root)
    projects = load_projects(root, args.project)

    if not projects:
        if args.project:
            print(f"Project not found: {args.project}", file=sys.stderr)
        else:
            print("No research projects found in projects/*/status.yaml", file=sys.stderr)
        sys.exit(1)

    # Compute matches
    matches_by_project: dict[str, list[dict]] = {}
    for proj in projects:
        pname = proj["_name"]
        matches = []
        for venue in venues:
            m = compute_match(proj, venue, taxonomy, today)
            if m["stars"] > 0:
                matches.append(m)
        # Sort: highest stars first, then by soonest deadline
        matches.sort(key=lambda x: (-x["stars"], x.get("days_to_deadline") or 9999))
        matches_by_project[pname] = matches

    # Output
    if args.json:
        print(format_json(matches_by_project, today))
    else:
        print(format_text(matches_by_project, today))


if __name__ == "__main__":
    main()
