"""Reviewer model — venue receptivity and coverage analysis.

Analyzes which topics venues are receptive to and identifies gaps in venue
coverage across the research portfolio. Reads venue configs from
shared/config/venues/*.yaml on disk.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .schema import ResearchSignal
except ImportError:
    from schema import ResearchSignal  # type: ignore

# ── Constants ─────────────────────────────────────────────

DETECTOR_NAME = "reviewer"

# Map venue YAML string values to numeric scores
TOPIC_FIT_SCORES: dict[str, float] = {
    "high": 0.9,
    "medium": 0.5,
    "low": 0.2,
}

STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "and", "but", "or", "nor", "not", "so", "yet", "both",
    "each", "few", "more", "most", "other", "some", "such", "no",
    "only", "own", "same", "than", "too", "very", "just", "because",
    "this", "that", "these", "those", "it", "its", "we", "our",
    "they", "their", "them", "which", "what", "who", "whom",
    "how", "when", "where", "why", "all", "any", "every",
    "about", "also", "many", "much", "new", "one", "two", "three",
    "first", "second", "third", "using", "based", "show", "shows",
    "shown", "paper", "propose", "proposed", "approach", "method",
    "methods", "results", "result", "work", "demonstrate", "demonstrates",
    "present", "presents", "study", "studies", "use", "used", "model",
    "models", "large", "across", "however", "provide", "provides",
})


# ── Helpers ───────────────────────────────────────────────

def _tokenize(text: str) -> frozenset[str]:
    """Extract keywords from text, filtering stopwords and short tokens."""
    words = re.findall(r'[a-z]{3,}', text.lower())
    return frozenset(w for w in words if w not in STOP_WORDS)


def _paper_id(paper: dict) -> str:
    """Return a stable string identifier for a paper."""
    return paper.get("id") or paper.get("arxivId") or paper.get("title", "")


def _extract_paper_topics(paper: dict) -> frozenset[str]:
    """Extract topic keywords from a paper's title, abstract, and categories."""
    text_parts: list[str] = []
    text_parts.append(paper.get("title") or "")
    text_parts.append(paper.get("abstract") or "")
    tokens = _tokenize(" ".join(text_parts))

    categories = paper.get("categories") or []
    cat_tokens: set[str] = set()
    for cat in categories:
        if isinstance(cat, str):
            for part in re.findall(r'[a-z]{2,}', cat.lower()):
                cat_tokens.add(part)

    return tokens | frozenset(cat_tokens)


def _default_venues_path() -> str:
    """Derive shared/config/venues path relative to repo root."""
    return str(Path(__file__).resolve().parent.parent.parent / "shared" / "config" / "venues")


def _default_portfolio_path() -> str:
    """Derive projects/ path relative to repo root."""
    return str(Path(__file__).resolve().parent.parent.parent / "projects")


def _parse_venue_yaml(text: str) -> dict[str, Any]:
    """Extract venue fields from YAML using regex (no PyYAML dependency).

    Parses: name, full_name, deadlines (next paper deadline), topic_fit section.
    """
    result: dict[str, Any] = {}

    # Name
    name_match = re.search(r'^name:\s*(\S+)', text, re.MULTILINE)
    if name_match:
        result["name"] = name_match.group(1).strip()

    full_name_match = re.search(r'^full_name:\s*"?([^"\n]+)"?', text, re.MULTILINE)
    if full_name_match:
        result["full_name"] = full_name_match.group(1).strip().strip('"')

    # Topic fit section — extract key: value pairs under topic_fit:
    topic_fit: dict[str, float] = {}
    in_topic_fit = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped == "topic_fit:":
            in_topic_fit = True
            continue
        if in_topic_fit:
            # End of section if we hit a non-indented line (top-level key)
            if stripped and not line.startswith(" ") and not line.startswith("\t"):
                in_topic_fit = False
                continue
            match = re.match(r'^\s+(\w+):\s+(\w+)', line)
            if match:
                key = match.group(1)
                val_str = match.group(2).lower()
                topic_fit[key] = TOPIC_FIT_SCORES.get(val_str, 0.0)
    result["topic_fit"] = topic_fit

    # Extract next upcoming paper deadline
    # Look for paper: "YYYY-MM-DD" patterns
    deadline_matches = re.findall(r'paper:\s*"?(\d{4}-\d{2}-\d{2})"?', text)
    if deadline_matches:
        now = datetime.now(timezone.utc)
        future_deadlines: list[str] = []
        for d_str in deadline_matches:
            try:
                d = datetime.strptime(d_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if d > now:
                    future_deadlines.append(d_str)
            except ValueError:
                pass
        if future_deadlines:
            # Earliest future deadline
            future_deadlines.sort()
            result["next_deadline"] = future_deadlines[0]

    return result


def _load_venue_profiles(venues_path: str) -> list[dict[str, Any]]:
    """Load all venue YAML files from the venues directory."""
    base = Path(venues_path)
    if not base.is_dir():
        return []

    venues: list[dict[str, Any]] = []
    for yaml_file in sorted(base.glob("*.yaml")):
        if yaml_file.name == "index.yaml":
            continue
        try:
            text = yaml_file.read_text(encoding="utf-8")
            venue = _parse_venue_yaml(text)
            if venue.get("name") and venue.get("topic_fit"):
                venues.append(venue)
        except OSError:
            pass

    return venues


def _parse_status_yaml(text: str) -> dict[str, str]:
    """Extract key fields from status.yaml using regex (no PyYAML dependency)."""
    result: dict[str, str] = {}
    for key in ("title", "venue", "phase", "current_focus"):
        match = re.search(
            rf'^{key}:\s*"?([^"\n]+)"?\s*$',
            text,
            re.MULTILINE,
        )
        if match:
            result[key] = match.group(1).strip().strip('"')
    return result


def _load_portfolio_venues(portfolio_path: str) -> set[str]:
    """Scan projects/ to find which venues we already target."""
    base = Path(portfolio_path)
    if not base.is_dir():
        return set()

    targeted_venues: set[str] = set()
    for project_dir in sorted(base.iterdir()):
        if not project_dir.is_dir():
            continue
        status_path = project_dir / "status.yaml"
        if status_path.is_file():
            try:
                text = status_path.read_text(encoding="utf-8")
                parsed = _parse_status_yaml(text)
                venue = parsed.get("venue", "").lower().strip()
                if venue:
                    targeted_venues.add(venue)
            except OSError:
                pass

    return targeted_venues


def _compute_timing_score(deadline_str: str | None) -> float:
    """Compute timing score based on deadline proximity.

    Within 60 days -> 0.8, within 120 days -> 0.5, beyond -> 0.2.
    No deadline -> 0.0.
    """
    if not deadline_str:
        return 0.0
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return 0.0

    now = datetime.now(timezone.utc)
    days_until = (deadline - now).days
    if days_until < 0:
        return 0.0
    if days_until <= 60:
        return 0.8
    if days_until <= 120:
        return 0.5
    return 0.2


def _topic_to_keywords(topic: str) -> frozenset[str]:
    """Convert a topic_fit key like 'llm_reasoning' to a set of matchable keywords."""
    # Split on underscore and return individual words
    parts = topic.lower().split("_")
    return frozenset(p for p in parts if len(p) >= 2)


# ── Signal generators ────────────────────────────────────

def _analyze_venue_receptivity(
    papers: list[dict],
    venues: list[dict[str, Any]],
    targeted_venues: set[str],
) -> list[ResearchSignal]:
    """Analyze paper-venue alignment and find venue gaps/opportunities.

    For each venue, compute how many recent papers match its top topics.
    If a venue has high paper activity in its preferred topics AND we have
    no project targeting it, emit a signal.
    """
    signals: list[ResearchSignal] = []

    # Pre-compute paper topic sets
    paper_topics_list: list[tuple[dict, frozenset[str]]] = []
    for paper in papers:
        topics = _extract_paper_topics(paper)
        if topics:
            paper_topics_list.append((paper, topics))

    for venue in venues:
        venue_name = venue.get("name", "unknown")
        full_name = venue.get("full_name", venue_name)
        topic_fit = venue.get("topic_fit", {})
        deadline_str = venue.get("next_deadline")

        # Get high-scoring topics for this venue (score > 0.5)
        top_topics: dict[str, float] = {
            t: score for t, score in topic_fit.items() if score > 0.5
        }
        if not top_topics:
            continue

        # Build keyword set from venue's top topics
        venue_keywords: frozenset[str] = frozenset()
        for topic in top_topics:
            venue_keywords = venue_keywords | _topic_to_keywords(topic)

        # Find papers matching this venue's top topics
        matching_papers: list[dict] = []
        for paper, paper_kw in paper_topics_list:
            overlap = paper_kw & venue_keywords
            if len(overlap) >= 2:  # at least 2 keyword matches
                matching_papers.append(paper)

        n_matching = len(matching_papers)
        if n_matching < 3:
            continue

        # Check if we already target this venue
        venue_targeted = any(
            venue_name.lower() in tv or tv in venue_name.lower()
            for tv in targeted_venues
        )

        timing = _compute_timing_score(deadline_str)
        top_topic_names = sorted(top_topics.keys())[:3]
        topic_label = ", ".join(t.replace("_", " ") for t in top_topic_names)

        # Compute average topic fit score for matching topics
        avg_fit = sum(top_topics.values()) / len(top_topics) if top_topics else 0.0

        if not venue_targeted:
            # venue_opportunity: active topic area + no submission planned
            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="venue_opportunity",
                title=f"{full_name} receptive to {topic_label} — aligns with our portfolio",
                description=(
                    f"{n_matching} recent papers match {full_name}'s top topics. "
                    f"We have relevant expertise but no planned submission."
                ),
                confidence=min(avg_fit, 1.0),
                source_papers=[_paper_id(p) for p in matching_papers[:5]],
                topics=top_topic_names,
                relevance=0.5,
                timing_score=timing,
                metadata={
                    "venue": venue_name,
                    "deadline": deadline_str or "",
                    "topic_fit_score": round(avg_fit, 3),
                    "matching_paper_count": n_matching,
                },
            ))

        # venue_gap: papers active in venue topics but we have no project there
        if not venue_targeted and n_matching >= 5:
            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="venue_gap",
                title=f"Venue gap: {n_matching} papers active in {full_name} topics",
                description=(
                    f"High activity ({n_matching} papers) in {topic_label} "
                    f"matching {full_name}'s preferences. No project targets this venue."
                ),
                confidence=min(n_matching / 20, 1.0),
                source_papers=[_paper_id(p) for p in matching_papers[:5]],
                topics=top_topic_names,
                relevance=0.4,
                timing_score=timing,
                metadata={
                    "venue": venue_name,
                    "deadline": deadline_str or "",
                    "topic_fit_score": round(avg_fit, 3),
                    "matching_paper_count": n_matching,
                },
            ))

    return signals


def _detect_venue_cooling(
    papers: list[dict],
    venues: list[dict[str, Any]],
    targeted_venues: set[str],
) -> list[ResearchSignal]:
    """Detect venues where activity in their top topics is declining.

    If a venue we target has few matching papers, that could indicate
    the field is cooling or shifting away from that venue's strengths.
    """
    signals: list[ResearchSignal] = []

    paper_topics_list: list[tuple[dict, frozenset[str]]] = []
    for paper in papers:
        topics = _extract_paper_topics(paper)
        if topics:
            paper_topics_list.append((paper, topics))

    for venue in venues:
        venue_name = venue.get("name", "unknown")
        full_name = venue.get("full_name", venue_name)
        topic_fit = venue.get("topic_fit", {})
        deadline_str = venue.get("next_deadline")

        # Only check venues we target
        venue_targeted = any(
            venue_name.lower() in tv or tv in venue_name.lower()
            for tv in targeted_venues
        )
        if not venue_targeted:
            continue

        # Get high-scoring topics
        top_topics = {t: s for t, s in topic_fit.items() if s > 0.5}
        if not top_topics:
            continue

        venue_keywords: frozenset[str] = frozenset()
        for topic in top_topics:
            venue_keywords = venue_keywords | _topic_to_keywords(topic)

        # Count matching papers
        matching_count = 0
        for _, paper_kw in paper_topics_list:
            overlap = paper_kw & venue_keywords
            if len(overlap) >= 2:
                matching_count += 1

        # If very few papers match our targeted venue, signal cooling
        if matching_count < 3 and len(paper_topics_list) >= 10:
            top_topic_names = sorted(top_topics.keys())[:3]
            topic_label = ", ".join(t.replace("_", " ") for t in top_topic_names)

            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="venue_cooling",
                title=f"Cooling: {full_name} topics underrepresented in recent papers",
                description=(
                    f"Only {matching_count} of {len(paper_topics_list)} papers match "
                    f"{full_name}'s top topics ({topic_label}). Field may be shifting."
                ),
                confidence=0.4,
                source_papers=[],
                topics=top_topic_names,
                relevance=0.3,
                timing_score=_compute_timing_score(deadline_str),
                metadata={
                    "venue": venue_name,
                    "deadline": deadline_str or "",
                    "matching_paper_count": matching_count,
                    "total_papers": len(paper_topics_list),
                },
            ))

    return signals


# ── Public API ────────────────────────────────────────────

def detect(papers: list[dict], venues_path: str = "") -> list[dict]:
    """Run reviewer model on pre-fetched papers.

    Analyzes venue receptivity and identifies gaps in venue coverage.

    Args:
        papers: list of paper dicts (must have at least 'title' and 'abstract').
        venues_path: path to shared/config/venues/ directory.

    Returns:
        list of signal dicts in the standard ResearchSignal format.
    """
    if not venues_path:
        venues_path = _default_venues_path()

    venues = _load_venue_profiles(venues_path)
    if not venues:
        return []

    portfolio_path = _default_portfolio_path()
    targeted_venues = _load_portfolio_venues(portfolio_path)

    all_signals: list[ResearchSignal] = []

    all_signals.extend(_analyze_venue_receptivity(papers, venues, targeted_venues))
    all_signals.extend(_detect_venue_cooling(papers, venues, targeted_venues))

    # Sort by signal type priority, then confidence descending
    type_priority = {
        "venue_gap": 0,
        "venue_opportunity": 1,
        "venue_cooling": 2,
    }
    all_signals.sort(key=lambda s: (
        type_priority.get(s.signal_type, 5),
        -s.confidence,
    ))

    # Annotate signals with embedding availability for downstream consumers
    has_embeddings = any(p.get("embedding_str") for p in papers)
    results = []
    for s in all_signals:
        d = s.to_dict()
        d["metadata"]["embeddings_available"] = has_embeddings
        results.append(d)

    return results
