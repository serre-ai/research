"""Gap detector — compass module version.

Reuses the core detection logic from scripts/gap-detector.py but exposes a
`detect(papers)` function that returns standardized ResearchSignal dicts.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

try:
    from .schema import ResearchSignal
    from .db import batch_cosine_similarity
except ImportError:
    from schema import ResearchSignal  # type: ignore
    from db import batch_cosine_similarity  # type: ignore

# ── Constants (mirrored from scripts/gap-detector.py) ─────

GAP_SIGNALS = [
    "future work", "remains open", "not yet explored", "left for future",
    "beyond the scope", "we do not address", "remains unclear",
    "has not been studied", "an open question", "warrants further",
    "preliminary", "limited to", "does not generalize", "we leave",
    "further investigation", "not been empirically", "lacks formal",
    "no theoretical", "without formal", "empirically validate",
]

THEORY_SIGNALS = [
    "theorem", "proof", "formal", "bound", "complexity", "theoretical",
    "analysis", "framework", "formalize", "axiom", "lemma", "corollary",
    "we prove", "we show that", "upper bound", "lower bound",
]

EMPIRICAL_SIGNALS = [
    "experiment", "benchmark", "evaluation", "dataset", "we evaluate",
    "empirical", "we test", "we measure", "ablation", "baseline",
    "accuracy", "f1", "performance", "results show",
]

BENCHMARK_SIGNALS = [
    "benchmark", "dataset", "evaluation suite", "test suite", "leaderboard",
    "we introduce a new dataset", "we release", "we collect",
]

CONTRADICTION_SIGNALS = [
    "contrary to", "in contrast to", "challenges the",
    "does not hold", "fails to", "overestimates", "underestimates",
    "inconsistent with", "disagrees with", "contradicts",
]

EMPIRICAL_NEED_SIGNALS = [
    "not been empirically", "empirically validate", "experimental validation",
    "remains to be tested", "needs empirical", "awaits experimental",
    "no experiments", "not yet validated",
]

THEORY_NEED_SIGNALS = [
    "no formal", "lacks formal", "without formal", "no theoretical",
    "unclear why", "not well understood", "lacks explanation",
    "no principled", "heuristic", "remains unexplained",
]

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
})

DETECTOR_NAME = "gap"


# ── Helpers ───────────────────────────────────────────────

def _tokenize(text: str) -> frozenset[str]:
    words = re.findall(r'[a-z]{3,}', text.lower())
    return frozenset(w for w in words if w not in STOP_WORDS)


def _keyword_overlap(words_a: frozenset[str], words_b: frozenset[str]) -> float:
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


def _has_signals(text: str, signals: list[str]) -> list[str]:
    if not text:
        return []
    text_lower = text.lower()
    return [s for s in signals if s in text_lower]


def _extract_gap_phrases(abstract: str) -> list[str]:
    if not abstract:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', abstract)
    return [s.strip() for s in sentences if any(sig in s.lower() for sig in GAP_SIGNALS)]


def _classify_paper(paper: dict) -> dict:
    abstract = paper.get("abstract") or ""
    theory = _has_signals(abstract, THEORY_SIGNALS)
    empirical = _has_signals(abstract, EMPIRICAL_SIGNALS)
    benchmark = _has_signals(abstract, BENCHMARK_SIGNALS)
    gaps = _extract_gap_phrases(abstract)

    if theory and not empirical:
        contribution_type = "theory"
    elif benchmark:
        contribution_type = "benchmark"
    elif empirical and not theory:
        contribution_type = "empirical"
    elif theory and empirical:
        contribution_type = "both"
    else:
        contribution_type = "unknown"

    return {
        "contribution_type": contribution_type,
        "gap_phrases": gaps,
        "theory_signals": theory,
        "empirical_signals": empirical,
        "contradiction_signals": _has_signals(abstract, CONTRADICTION_SIGNALS),
    }


def _paper_id(paper: dict) -> str:
    return paper.get("id") or paper.get("arxivId") or paper.get("title", "")


def _paper_ref(paper: dict) -> str:
    """Return paper ID string for source_papers arrays."""
    return _paper_id(paper)


def _extract_topics(paper: dict) -> list[str]:
    """Extract topic labels from a paper (categories or keywords)."""
    cats = paper.get("categories") or []
    return [c for c in cats if isinstance(c, str)]


# ── Individual gap detectors ─────────────────────────────

def _find_uncovered_connections(papers: list[dict]) -> list[ResearchSignal]:
    has_embeddings = any(p.get("embedding_str") for p in papers)

    if has_embeddings:
        return _find_uncovered_connections_embedding(papers)
    else:
        return _find_uncovered_connections_keyword(papers)


def _find_uncovered_connections_embedding(papers: list[dict]) -> list[ResearchSignal]:
    """Use pgvector cosine similarity for cross-pollination detection."""
    paper_ids = [_paper_id(p) for p in papers if p.get("embedding_str")]
    if len(paper_ids) < 2:
        return _find_uncovered_connections_keyword(papers)

    similarities = batch_cosine_similarity(paper_ids)

    # Build a lookup by paper ID for fast access
    paper_by_id: dict[str, dict] = {}
    for p in papers:
        pid = _paper_id(p)
        paper_by_id[pid] = p

    signals: list[ResearchSignal] = []
    for (id_a, id_b), similarity in similarities.items():
        if similarity < 0.7:
            continue

        paper_a = paper_by_id.get(id_a)
        paper_b = paper_by_id.get(id_b)
        if not paper_a or not paper_b:
            continue

        authors_a = set(str(x) for x in (paper_a.get("authors") or []))
        authors_b = set(str(x) for x in (paper_b.get("authors") or []))
        if authors_a & authors_b:
            continue

        title_a = paper_a.get("title", "")[:60]
        title_b = paper_b.get("title", "")[:60]
        topics = list(set(_extract_topics(paper_a) + _extract_topics(paper_b)))
        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="uncovered_connection",
            title=f"Cross-pollination: {title_a} + {title_b}",
            description=(
                f"High embedding similarity ({similarity:.0%}) between papers by different "
                f"groups — potential cross-pollination opportunity."
            ),
            confidence=min(similarity, 1.0),
            source_papers=[_paper_ref(paper_a), _paper_ref(paper_b)],
            topics=topics[:5],
            metadata={"overlap_score": round(similarity, 3), "method": "embedding"},
        ))

    signals.sort(key=lambda s: s.metadata.get("overlap_score", 0), reverse=True)
    return signals[:20]


def _find_uncovered_connections_keyword(papers: list[dict]) -> list[ResearchSignal]:
    """Fall back to Jaccard keyword overlap for cross-pollination detection."""
    tokens = [_tokenize(p.get("abstract") or "") for p in papers]
    signals: list[ResearchSignal] = []

    for i in range(len(papers)):
        if not tokens[i]:
            continue
        authors_a = set(str(x) for x in (papers[i].get("authors") or []))
        for j in range(i + 1, len(papers)):
            if not tokens[j]:
                continue
            overlap = _keyword_overlap(tokens[i], tokens[j])
            if overlap > 0.25:
                authors_b = set(str(x) for x in (papers[j].get("authors") or []))
                if authors_a & authors_b:
                    continue
                title_a = papers[i].get("title", "")[:60]
                title_b = papers[j].get("title", "")[:60]
                topics = list(set(_extract_topics(papers[i]) + _extract_topics(papers[j])))
                signals.append(ResearchSignal(
                    detector=DETECTOR_NAME,
                    signal_type="uncovered_connection",
                    title=f"Cross-pollination: {title_a} + {title_b}",
                    description=(
                        f"High topic overlap ({overlap:.0%}) between papers by different "
                        f"groups — potential cross-pollination opportunity."
                    ),
                    confidence=min(overlap * 2, 1.0),
                    source_papers=[_paper_ref(papers[i]), _paper_ref(papers[j])],
                    topics=topics[:5],
                    metadata={"overlap_score": round(overlap, 3), "method": "keyword"},
                ))

    signals.sort(key=lambda s: s.metadata.get("overlap_score", 0), reverse=True)
    return signals[:20]


def _find_contradictions(papers: list[dict]) -> list[ResearchSignal]:
    tokens: dict[str, frozenset[str]] = {}
    for p in papers:
        tokens[_paper_id(p)] = _tokenize(p.get("abstract") or "")

    contradicting = [
        (p, _has_signals(p.get("abstract", ""), CONTRADICTION_SIGNALS))
        for p in papers
        if _has_signals(p.get("abstract", ""), CONTRADICTION_SIGNALS)
    ]

    signals: list[ResearchSignal] = []
    seen_pairs: set[tuple[str, str]] = set()

    for paper, sigs in contradicting:
        pid_a = _paper_id(paper)
        if not tokens.get(pid_a):
            continue
        for other in papers:
            pid_b = _paper_id(other)
            if pid_a == pid_b:
                continue
            pair = (min(pid_a, pid_b), max(pid_a, pid_b))
            if pair in seen_pairs:
                continue
            if not tokens.get(pid_b):
                continue
            overlap = _keyword_overlap(tokens[pid_a], tokens[pid_b])
            if overlap > 0.2:
                seen_pairs.add(pair)
                topics = list(set(_extract_topics(paper) + _extract_topics(other)))
                signals.append(ResearchSignal(
                    detector=DETECTOR_NAME,
                    signal_type="contradicting_claims",
                    title=f"Contradiction: {paper.get('title', '')[:50]} vs {other.get('title', '')[:50]}",
                    description=(
                        f"Paper A contains contradiction signals ({', '.join(sigs[:3])}) and "
                        f"overlaps topically with Paper B — investigate what conditions "
                        f"differentiate their findings."
                    ),
                    confidence=min(overlap * 2, 1.0),
                    source_papers=[_paper_ref(paper), _paper_ref(other)],
                    topics=topics[:5],
                    metadata={
                        "overlap_score": round(overlap, 3),
                        "contradiction_signals": sigs,
                    },
                ))

    signals.sort(key=lambda s: s.metadata.get("overlap_score", 0), reverse=True)
    return signals[:15]


def _find_missing_empirical(papers: list[dict]) -> list[ResearchSignal]:
    signals: list[ResearchSignal] = []
    for paper in papers:
        info = _classify_paper(paper)
        if info["contribution_type"] != "theory":
            continue

        abstract = paper.get("abstract") or ""
        gap_phrases = info["gap_phrases"]

        has_empirical_gap_phrase = any(
            any(kw in phrase.lower() for kw in ["empirical", "experiment", "validate", "test", "evaluate"])
            for phrase in gap_phrases
        )
        has_empirical_need_signal = bool(_has_signals(abstract, EMPIRICAL_NEED_SIGNALS))

        if not has_empirical_gap_phrase and not has_empirical_need_signal:
            continue

        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="missing_empirical",
            title=f"Needs experiments: {paper.get('title', '')[:70]}",
            description=(
                f"Theory paper with {len(info['theory_signals'])} theoretical markers "
                f"that explicitly mentions needing empirical validation."
            ),
            confidence=0.7,
            source_papers=[_paper_ref(paper)],
            topics=_extract_topics(paper)[:5],
            metadata={
                "gap_phrases": gap_phrases[:3],
                "theory_signals": info["theory_signals"][:3],
            },
        ))

    return signals[:15]


def _find_missing_theory(papers: list[dict]) -> list[ResearchSignal]:
    signals: list[ResearchSignal] = []
    for paper in papers:
        info = _classify_paper(paper)
        if info["contribution_type"] not in ("empirical", "benchmark"):
            continue

        abstract = paper.get("abstract") or ""
        gap_phrases = info["gap_phrases"]

        has_theory_gap_phrase = any(
            any(kw in phrase.lower() for kw in ["formal", "theoretical", "explain", "principled", "theory"])
            for phrase in gap_phrases
        )
        has_theory_need_signal = bool(_has_signals(abstract, THEORY_NEED_SIGNALS))

        if not has_theory_gap_phrase and not has_theory_need_signal:
            continue

        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="missing_theory",
            title=f"Needs theory: {paper.get('title', '')[:70]}",
            description=(
                f"Empirical paper with {len(info['empirical_signals'])} empirical markers "
                f"that explicitly mentions needing formal analysis."
            ),
            confidence=0.7,
            source_papers=[_paper_ref(paper)],
            topics=_extract_topics(paper)[:5],
            metadata={
                "gap_phrases": gap_phrases[:3],
                "empirical_signals": info["empirical_signals"][:3],
            },
        ))

    return signals[:15]


def _find_benchmark_needs(papers: list[dict]) -> list[ResearchSignal]:
    classifications: dict[str, dict] = {}
    for paper in papers:
        pid = _paper_id(paper)
        if pid not in classifications:
            classifications[pid] = _classify_paper(paper)

    topic_groups: dict[str, list[dict]] = defaultdict(list)
    for paper in papers:
        for cat in (paper.get("categories") or []):
            if isinstance(cat, str):
                topic_groups[cat].append(paper)

    signals: list[ResearchSignal] = []
    for topic, group in topic_groups.items():
        if len(group) < 3:
            continue
        has_benchmark = any(
            classifications[_paper_id(p)]["contribution_type"] == "benchmark"
            for p in group
        )
        if not has_benchmark:
            paper_count = len(group)
            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="new_benchmark",
                title=f"Benchmark gap: {topic} ({paper_count} papers)",
                description=(
                    f"{paper_count} papers in '{topic}' with no benchmark contribution "
                    f"— the field may need a controlled evaluation suite."
                ),
                confidence=min(paper_count / 10, 1.0),
                source_papers=[_paper_ref(p) for p in group[:5]],
                topics=[topic],
                metadata={"paper_count": paper_count},
            ))

    signals.sort(key=lambda s: s.metadata.get("paper_count", 0), reverse=True)
    return signals[:10]


# ── Public API ────────────────────────────────────────────

def detect(papers: list[dict]) -> list[dict]:
    """Run all gap detectors on pre-fetched papers.

    Args:
        papers: list of paper dicts (must have at least 'title' and 'abstract').

    Returns:
        list of signal dicts in the standard ResearchSignal format.
    """
    all_signals: list[ResearchSignal] = []

    all_signals.extend(_find_uncovered_connections(papers))
    all_signals.extend(_find_contradictions(papers))
    all_signals.extend(_find_missing_empirical(papers))
    all_signals.extend(_find_missing_theory(papers))
    all_signals.extend(_find_benchmark_needs(papers))

    # Sort by confidence descending, then by signal_type priority
    type_priority = {
        "contradicting_claims": 0,
        "missing_empirical": 1,
        "missing_theory": 2,
        "uncovered_connection": 3,
        "new_benchmark": 4,
    }
    all_signals.sort(key=lambda s: (
        type_priority.get(s.signal_type, 5),
        -s.confidence,
    ))

    return [s.to_dict() for s in all_signals]
