"""Venue enricher — empirical topic profiles from OpenReview acceptance data.

Replaces static YAML topic_fit scores (high/medium/low) with normalized
frequency scores computed from actual accepted paper keywords.

Also detects year-over-year topic shifts: topics gaining frequency indicate
a venue becoming more receptive; topics losing frequency indicate cooling.

Data source: JSON files in shared/config/venues/data/ produced by
scripts/openreview-scraper.py.

Usage:
    # First, populate acceptance data:
    python3 scripts/openreview-scraper.py --venue neurips --year 2025
    python3 scripts/openreview-scraper.py --venue neurips --year 2024

    # Then the reviewer_model will automatically use empirical scores
    # when data files exist.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Minimum number of accepted papers required to trust empirical scores
MIN_PAPERS_FOR_EMPIRICAL = 20

# Topic shift thresholds
SHIFT_GAINING_THRESHOLD = 0.10   # +10% normalized delta = gaining
SHIFT_COOLING_THRESHOLD = -0.10  # -10% normalized delta = cooling


# ── Data loading ──────────────────────────────────────────


def _default_venues_data_path() -> str:
    """Derive shared/config/venues/data path relative to repo root."""
    return str(
        Path(__file__).resolve().parent.parent.parent
        / "shared" / "config" / "venues" / "data"
    )


def load_venue_data(venues_data_path: str = "") -> dict[str, dict]:
    """Load accepted paper data from shared/config/venues/data/*.json.

    Returns a dict keyed by "{venue}-{year}", e.g. "neurips-2025",
    containing the full JSON structure produced by openreview-scraper.py.
    """
    if not venues_data_path:
        venues_data_path = _default_venues_data_path()

    venue_data: dict[str, dict] = {}
    base = Path(venues_data_path)
    if not base.is_dir():
        return {}

    for f in sorted(base.glob("*-accepted.json")):
        # Parse venue name and year from filename: neurips-2025-accepted.json
        parts = f.stem.replace("-accepted", "").rsplit("-", 1)
        if len(parts) == 2:
            venue, year = parts[0], parts[1]
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                venue_data[f"{venue}-{year}"] = data
                log.debug("Loaded venue data: %s (%d papers)", f.name,
                          data.get("total_accepted", 0))
            except (json.JSONDecodeError, OSError) as exc:
                log.warning("Failed to load %s: %s", f, exc)

    return venue_data


# ── Empirical topic scores ────────────────────────────────


def compute_empirical_topic_scores(venue_data: dict) -> dict[str, float]:
    """From accepted paper keywords, compute normalized topic scores (0-1).

    Uses the by_keyword counts from the stats section. Each keyword's
    frequency is normalized by the maximum keyword count, producing
    a 0-1 score where 1.0 = the most frequent keyword.

    Args:
        venue_data: A single venue-year dict from load_venue_data().

    Returns:
        Dict mapping keyword -> normalized score (0-1).
    """
    stats = venue_data.get("stats", {})
    by_keyword = stats.get("by_keyword", {})
    total_papers = venue_data.get("total_accepted", 0)

    if not by_keyword or total_papers < MIN_PAPERS_FOR_EMPIRICAL:
        return {}

    max_count = max(by_keyword.values()) if by_keyword else 1
    if max_count == 0:
        return {}

    return {k: round(v / max_count, 4) for k, v in by_keyword.items()}


# ── Topic shift detection ─────────────────────────────────


def detect_topic_shifts(
    current_data: dict,
    previous_data: dict,
) -> list[dict[str, Any]]:
    """Compare topic frequencies between years to detect shifts.

    For each keyword present in either year, computes the normalized
    frequency delta. Topics with large positive deltas are "gaining";
    large negative deltas are "cooling".

    Args:
        current_data: Venue data for the more recent year.
        previous_data: Venue data for the earlier year.

    Returns:
        List of shift dicts with keys:
          - topic: str
          - direction: "gaining" | "cooling"
          - delta: float (current - previous normalized score)
          - current_score: float
          - previous_score: float
    """
    current_scores = compute_empirical_topic_scores(current_data)
    previous_scores = compute_empirical_topic_scores(previous_data)

    if not current_scores or not previous_scores:
        return []

    all_topics = set(current_scores) | set(previous_scores)
    shifts: list[dict[str, Any]] = []

    for topic in sorted(all_topics):
        cur = current_scores.get(topic, 0.0)
        prev = previous_scores.get(topic, 0.0)
        delta = cur - prev

        if delta >= SHIFT_GAINING_THRESHOLD:
            shifts.append({
                "topic": topic,
                "direction": "gaining",
                "delta": round(delta, 4),
                "current_score": round(cur, 4),
                "previous_score": round(prev, 4),
            })
        elif delta <= SHIFT_COOLING_THRESHOLD:
            shifts.append({
                "topic": topic,
                "direction": "cooling",
                "delta": round(delta, 4),
                "current_score": round(cur, 4),
                "previous_score": round(prev, 4),
            })

    # Sort by absolute delta descending (biggest shifts first)
    shifts.sort(key=lambda s: abs(s["delta"]), reverse=True)
    return shifts


# ── Integration helpers ───────────────────────────────────


def get_latest_venue_year(
    venue_name: str,
    venue_data: dict[str, dict],
) -> tuple[dict | None, dict | None]:
    """Find the latest and second-latest year data for a venue.

    Args:
        venue_name: Lowercase venue name (e.g. "neurips").
        venue_data: Full dict from load_venue_data().

    Returns:
        (latest_data, previous_data) — either may be None if not found.
    """
    matching: list[tuple[int, dict]] = []
    for key, data in venue_data.items():
        parts = key.rsplit("-", 1)
        if len(parts) == 2 and parts[0] == venue_name:
            try:
                year = int(parts[1])
                matching.append((year, data))
            except ValueError:
                pass

    if not matching:
        return None, None

    matching.sort(key=lambda x: x[0], reverse=True)
    latest = matching[0][1]
    previous = matching[1][1] if len(matching) > 1 else None
    return latest, previous


def merge_empirical_into_venue(
    venue_profile: dict[str, Any],
    empirical_scores: dict[str, float],
    topic_shifts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Merge empirical topic scores into a venue profile from YAML.

    Empirical scores supplement (and when available, override) the
    static YAML topic_fit values. The original YAML scores are preserved
    under "topic_fit_yaml" for reference.

    Args:
        venue_profile: Parsed venue dict from _parse_venue_yaml().
        empirical_scores: Normalized keyword scores from compute_empirical_topic_scores().
        topic_shifts: Optional shift data from detect_topic_shifts().

    Returns:
        The venue_profile dict, mutated with enriched topic_fit and metadata.
    """
    yaml_scores = venue_profile.get("topic_fit", {})

    # Preserve original YAML scores
    venue_profile["topic_fit_yaml"] = dict(yaml_scores)

    # Build merged topic_fit: start with YAML, overlay empirical
    merged: dict[str, float] = dict(yaml_scores)

    # Map empirical keyword scores to existing YAML topic keys where
    # keywords match. Also add new topics not in YAML.
    for keyword, score in empirical_scores.items():
        # Check if keyword matches any existing topic key (with underscore variants)
        normalized_kw = keyword.replace(" ", "_").replace("-", "_")
        if normalized_kw in merged:
            # Override YAML score with empirical
            merged[normalized_kw] = score
        else:
            # Add as new topic from empirical data
            merged[normalized_kw] = score

    venue_profile["topic_fit"] = merged
    venue_profile["empirical_enriched"] = True
    venue_profile["empirical_topic_count"] = len(empirical_scores)

    if topic_shifts:
        venue_profile["topic_shifts"] = topic_shifts

    return venue_profile


def enrich_venues(
    venues: list[dict[str, Any]],
    venues_data_path: str = "",
) -> list[dict[str, Any]]:
    """Enrich a list of venue profiles with empirical data.

    This is the main integration point called from reviewer_model.detect().
    For each venue that has acceptance data on disk, it computes empirical
    topic scores and detects year-over-year shifts.

    Args:
        venues: List of parsed venue profile dicts (from _load_venue_profiles).
        venues_data_path: Path to shared/config/venues/data/ directory.

    Returns:
        The same list of venues, enriched in-place with empirical data.
    """
    venue_data = load_venue_data(venues_data_path)
    if not venue_data:
        log.debug("No venue acceptance data found — using YAML scores only.")
        return venues

    enriched_count = 0
    for venue_profile in venues:
        venue_name = (venue_profile.get("name") or "").lower()
        if not venue_name:
            continue

        latest, previous = get_latest_venue_year(venue_name, venue_data)
        if latest is None:
            continue

        empirical_scores = compute_empirical_topic_scores(latest)
        if not empirical_scores:
            continue

        # Detect topic shifts if we have two years of data
        topic_shifts = None
        if previous is not None:
            topic_shifts = detect_topic_shifts(latest, previous)

        merge_empirical_into_venue(venue_profile, empirical_scores, topic_shifts)
        enriched_count += 1

        log.info(
            "Enriched %s with %d empirical topics%s",
            venue_name,
            len(empirical_scores),
            f" ({len(topic_shifts)} shifts)" if topic_shifts else "",
        )

    if enriched_count:
        log.info("Enriched %d/%d venues with OpenReview data.", enriched_count, len(venues))

    return venues
