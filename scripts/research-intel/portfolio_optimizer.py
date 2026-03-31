"""Portfolio optimizer — research identity coherence detector.

Builds a "research identity vector" from the project portfolio on disk,
then scores incoming papers against it to surface:
  - portfolio_gap: topics matching identity but with no active project
  - portfolio_deepening: papers that directly extend an existing project
  - citation_opportunity: papers likely to cite our work
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from .schema import ResearchSignal
except ImportError:
    from schema import ResearchSignal  # type: ignore

# ── Constants ─────────────────────────────────────────────

DETECTOR_NAME = "portfolio"

SKIP_PROJECTS = frozenset({"platform-engineering"})

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

# High-leverage phases: projects in these phases have completed
# substantial theory/experiments, making related papers high-value.
HIGH_LEVERAGE_PHASES = frozenset({
    "complete", "submission-prep", "camera-ready", "published",
})


# ── Helpers ───────────────────────────────────────────────

def _tokenize(text: str) -> frozenset[str]:
    """Extract keywords from text, filtering stopwords and short tokens."""
    words = re.findall(r'[a-z]{3,}', text.lower())
    return frozenset(w for w in words if w not in STOP_WORDS)


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    """Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union) if union else 0.0


def _extract_first_paragraph(text: str) -> str:
    """Extract the first non-heading paragraph from Markdown text."""
    lines = text.strip().split("\n")
    paragraph_lines: list[str] = []
    found_content = False
    for line in lines:
        stripped = line.strip()
        # Skip headings and blank lines before first paragraph
        if not found_content:
            if not stripped or stripped.startswith("#"):
                continue
            found_content = True
        if found_content:
            if not stripped and paragraph_lines:
                break  # end of first paragraph
            if stripped.startswith("#"):
                break  # next heading
            paragraph_lines.append(stripped)
    return " ".join(paragraph_lines)


def _parse_status_yaml(text: str) -> dict[str, str]:
    """Extract key fields from status.yaml using regex (no PyYAML dependency).

    Looks for top-level scalar fields: title, venue, phase, current_focus.
    """
    result: dict[str, str] = {}
    for key in ("title", "venue", "phase", "current_focus"):
        # Match lines like `key: "value"` or `key: value`
        match = re.search(
            rf'^{key}:\s*"?([^"\n]+)"?\s*$',
            text,
            re.MULTILINE,
        )
        if match:
            result[key] = match.group(1).strip().strip('"')
    return result


def _paper_id(paper: dict) -> str:
    """Return a stable string identifier for a paper."""
    return paper.get("id") or paper.get("arxivId") or paper.get("title", "")


def _extract_paper_topics(paper: dict) -> frozenset[str]:
    """Extract topic keywords from a paper's title, abstract, and categories."""
    text_parts: list[str] = []
    title = paper.get("title") or ""
    abstract = paper.get("abstract") or ""
    text_parts.append(title)
    text_parts.append(abstract)

    tokens = _tokenize(" ".join(text_parts))

    # Also include categories as-is (lowercased, cleaned)
    categories = paper.get("categories") or []
    cat_tokens: set[str] = set()
    for cat in categories:
        if isinstance(cat, str):
            # e.g. "cs.AI" -> "ai", "cs.CL" -> "cl"
            for part in re.findall(r'[a-z]{2,}', cat.lower()):
                cat_tokens.add(part)

    return tokens | frozenset(cat_tokens)


# ── Project scanning ─────────────────────────────────────

def _build_research_identity(portfolio_path: str) -> tuple[
    frozenset[str],                          # core_identity topics (appear in 2+ projects)
    dict[str, dict[str, Any]],               # project_info: name -> {title, venue, phase, topics, ...}
]:
    """Scan project directories to build a research identity vector.

    Returns:
        core_identity: set of topic keywords appearing in 2+ projects
        project_info: per-project metadata dict
    """
    base = Path(portfolio_path)
    if not base.is_dir():
        return frozenset(), {}

    topic_counts: dict[str, int] = {}  # keyword -> number of projects it appears in
    project_info: dict[str, dict[str, Any]] = {}

    for project_dir in sorted(base.iterdir()):
        if not project_dir.is_dir():
            continue
        name = project_dir.name
        if name in SKIP_PROJECTS:
            continue

        info: dict[str, Any] = {"name": name, "topics": frozenset()}
        all_text_parts: list[str] = []

        # Read BRIEF.md
        brief_path = project_dir / "BRIEF.md"
        if brief_path.is_file():
            try:
                brief_text = brief_path.read_text(encoding="utf-8")
                first_para = _extract_first_paragraph(brief_text)
                info["research_question"] = first_para
                all_text_parts.append(first_para)
                all_text_parts.append(brief_text)  # full text for keyword extraction
            except OSError:
                pass

        # Read status.yaml
        status_path = project_dir / "status.yaml"
        if status_path.is_file():
            try:
                status_text = status_path.read_text(encoding="utf-8")
                parsed = _parse_status_yaml(status_text)
                info["title"] = parsed.get("title", "")
                info["venue"] = parsed.get("venue", "")
                info["phase"] = parsed.get("phase", "")
                info["current_focus"] = parsed.get("current_focus", "")

                if parsed.get("title"):
                    all_text_parts.append(parsed["title"])
                if parsed.get("current_focus"):
                    all_text_parts.append(parsed["current_focus"])
            except OSError:
                pass

        # Build topic set for this project
        project_topics = _tokenize(" ".join(all_text_parts))
        info["topics"] = project_topics
        project_info[name] = info

        # Count each topic across projects
        for topic in project_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # Core identity = topics appearing in 2+ projects
    core_identity = frozenset(
        topic for topic, count in topic_counts.items() if count >= 2
    )

    return core_identity, project_info


# ── Signal generators ────────────────────────────────────

def _find_portfolio_gaps(
    papers: list[dict],
    core_identity: frozenset[str],
    project_info: dict[str, dict[str, Any]],
) -> list[ResearchSignal]:
    """Find topics in papers that match core identity but have no active project."""
    # Collect all topics covered by existing projects
    covered_topics: frozenset[str] = frozenset()
    for info in project_info.values():
        covered_topics = covered_topics | info.get("topics", frozenset())

    # Group papers by their topic clusters
    topic_paper_map: dict[str, list[dict]] = {}
    for paper in papers:
        paper_topics = _extract_paper_topics(paper)
        identity_overlap = paper_topics & core_identity
        if not identity_overlap:
            continue

        # Check if any overlapping topic is NOT covered by existing projects
        uncovered = identity_overlap - covered_topics
        if not uncovered:
            continue

        # Use the largest uncovered cluster as the key
        cluster_key = ", ".join(sorted(uncovered)[:5])
        if cluster_key not in topic_paper_map:
            topic_paper_map[cluster_key] = []
        topic_paper_map[cluster_key].append(paper)

    signals: list[ResearchSignal] = []
    for cluster, matching_papers in topic_paper_map.items():
        # Compute coherence as overlap between cluster topics and identity
        cluster_topics = frozenset(cluster.split(", "))
        coherence = _jaccard(cluster_topics, core_identity)

        # Boost coherence by paper count (more papers = more important gap)
        paper_boost = min(len(matching_papers) / 10, 0.3)
        adjusted_coherence = min(coherence + paper_boost, 1.0)

        if adjusted_coherence < 0.05:
            continue

        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="portfolio_gap",
            title=f"Portfolio gap: {cluster} aligns with identity but has no project",
            description=(
                f"Recent papers on {cluster} have {adjusted_coherence:.0%} overlap "
                f"with core identity. No active project covers this."
            ),
            confidence=adjusted_coherence,
            source_papers=[_paper_id(p) for p in matching_papers[:5]],
            topics=list(cluster_topics)[:5],
            relevance=adjusted_coherence,
            timing_score=0.5,
            metadata={
                "coherence": round(adjusted_coherence, 3),
                "matching_projects": [],
                "identity_overlap_topics": list(cluster_topics)[:10],
                "paper_count": len(matching_papers),
            },
        ))

    signals.sort(key=lambda s: s.confidence, reverse=True)
    return signals[:15]


def _find_portfolio_deepening(
    papers: list[dict],
    core_identity: frozenset[str],
    project_info: dict[str, dict[str, Any]],
) -> list[ResearchSignal]:
    """Find papers that directly extend an existing project."""
    signals: list[ResearchSignal] = []

    for paper in papers:
        paper_topics = _extract_paper_topics(paper)
        if not paper_topics:
            continue

        best_project: str | None = None
        best_overlap: float = 0.0
        best_project_info: dict[str, Any] = {}

        for proj_name, info in project_info.items():
            proj_topics = info.get("topics", frozenset())
            if not proj_topics:
                continue
            overlap = _jaccard(paper_topics, proj_topics)
            if overlap > best_overlap:
                best_overlap = overlap
                best_project = proj_name
                best_project_info = info

        # Threshold: at least 15% Jaccard overlap with a project
        if best_overlap < 0.15 or best_project is None:
            continue

        # Capability leverage: boost if the matching project has completed
        # experiments/theory (high-leverage phase)
        leverage = 0.0
        phase = best_project_info.get("phase", "")
        if phase in HIGH_LEVERAGE_PHASES:
            leverage = 1.0
        elif phase in ("experiment-execution-and-polish", "experiment-execution"):
            leverage = 0.7
        elif phase in ("research", "literature-review"):
            leverage = 0.3

        coherence = _jaccard(paper_topics, core_identity)
        combined_score = (best_overlap * 0.6) + (coherence * 0.2) + (leverage * 0.2)

        title = paper.get("title", "")[:80]
        proj_title = best_project_info.get("title", best_project)

        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="portfolio_deepening",
            title=f"Deepening: '{title}' extends {best_project}",
            description=(
                f"Paper has {best_overlap:.0%} topic overlap with '{proj_title}'. "
                f"Capability leverage: {leverage:.0%} (phase: {phase})."
            ),
            confidence=combined_score,
            source_papers=[_paper_id(paper)],
            topics=list(paper_topics & (best_project_info.get("topics", frozenset())))[:5],
            relevance=combined_score,
            timing_score=0.5 + (leverage * 0.3),  # more urgent if project is mature
            metadata={
                "coherence": round(coherence, 3),
                "matching_projects": [best_project],
                "identity_overlap_topics": list(
                    paper_topics & core_identity
                )[:10],
                "project_overlap": round(best_overlap, 3),
                "capability_leverage": round(leverage, 3),
                "project_phase": phase,
            },
        ))

    signals.sort(key=lambda s: s.confidence, reverse=True)
    return signals[:20]


def _find_citation_opportunities(
    papers: list[dict],
    core_identity: frozenset[str],
    project_info: dict[str, dict[str, Any]],
) -> list[ResearchSignal]:
    """Find papers that reference topics we've published on (or are publishing).

    Papers about reasoning gaps, verification complexity, etc. would likely
    cite our work if we publish in that area.
    """
    # Only consider projects that are far enough along to be citable
    citable_projects: dict[str, dict[str, Any]] = {}
    for proj_name, info in project_info.items():
        phase = info.get("phase", "")
        if phase in HIGH_LEVERAGE_PHASES or phase in (
            "experiment-execution-and-polish", "experiment-execution",
            "submission-prep",
        ):
            citable_projects[proj_name] = info

    if not citable_projects:
        return []

    signals: list[ResearchSignal] = []

    for paper in papers:
        paper_topics = _extract_paper_topics(paper)
        if not paper_topics:
            continue

        for proj_name, info in citable_projects.items():
            proj_topics = info.get("topics", frozenset())
            if not proj_topics:
                continue

            overlap = _jaccard(paper_topics, proj_topics)
            if overlap < 0.10:
                continue

            # Check for specific high-signal keywords from our project titles
            title_tokens = _tokenize(info.get("title", ""))
            title_overlap = paper_topics & title_tokens
            if len(title_overlap) < 2:
                continue

            coherence = _jaccard(paper_topics, core_identity)
            confidence = min((overlap * 0.5) + (len(title_overlap) * 0.1) + (coherence * 0.2), 1.0)

            paper_title = paper.get("title", "")[:80]
            proj_title = info.get("title", proj_name)

            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="citation_opportunity",
                title=f"Citation opportunity: '{paper_title}' may cite {proj_name}",
                description=(
                    f"Paper overlaps {overlap:.0%} with '{proj_title}' and shares "
                    f"title keywords: {', '.join(sorted(title_overlap)[:5])}. "
                    f"Likely to cite our work if published."
                ),
                confidence=confidence,
                source_papers=[_paper_id(paper)],
                topics=list(title_overlap)[:5],
                relevance=confidence,
                timing_score=0.7,  # citation opportunities are time-sensitive
                metadata={
                    "coherence": round(coherence, 3),
                    "matching_projects": [proj_name],
                    "identity_overlap_topics": list(
                        paper_topics & core_identity
                    )[:10],
                    "title_keyword_overlap": list(title_overlap),
                    "project_phase": info.get("phase", ""),
                },
            ))

    signals.sort(key=lambda s: s.confidence, reverse=True)
    return signals[:15]


# ── Public API ────────────────────────────────────────────

def detect(papers: list[dict], portfolio_path: str = "projects/") -> list[dict]:
    """Run portfolio optimization detectors on pre-fetched papers.

    Builds a research identity from project files on disk, then scores
    each paper's topics against the identity to find gaps, deepening
    opportunities, and citation leads.

    Args:
        papers: list of paper dicts (must have at least 'title' and 'abstract').
        portfolio_path: path to the projects directory (default: "projects/").

    Returns:
        list of signal dicts in the standard ResearchSignal format.
    """
    core_identity, project_info = _build_research_identity(portfolio_path)

    if not core_identity:
        return []

    all_signals: list[ResearchSignal] = []

    all_signals.extend(_find_portfolio_gaps(papers, core_identity, project_info))
    all_signals.extend(_find_portfolio_deepening(papers, core_identity, project_info))
    all_signals.extend(_find_citation_opportunities(papers, core_identity, project_info))

    # Sort by signal type priority, then confidence descending
    type_priority = {
        "portfolio_gap": 0,
        "portfolio_deepening": 1,
        "citation_opportunity": 2,
    }
    all_signals.sort(key=lambda s: (
        type_priority.get(s.signal_type, 5),
        -s.confidence,
    ))

    return [s.to_dict() for s in all_signals]
