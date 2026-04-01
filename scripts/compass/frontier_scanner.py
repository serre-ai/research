"""Frontier scanner — capability jump detection.

Detects when models suddenly get much better at something and no theory
explains why.  Scans paper abstracts for performance claims, builds a
per-benchmark timeline, and flags unexplained jumps.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

try:
    from .schema import ResearchSignal
except ImportError:
    from schema import ResearchSignal  # type: ignore

# ── Constants ────────────────────────────────────────────

DETECTOR_NAME = "frontier"

# Matches "achieves 92.3% accuracy on GSM8K" and similar phrasing.
# Group 1 = numeric score, Group 2 = benchmark name.
PERF_PATTERN = re.compile(
    r'(?:achiev|obtain|reach|attain|report|record)\w*\s+'
    r'(?:an?\s+)?'
    r'(\d+\.?\d*)\s*%'
    r'\s+(?:accuracy|F1|BLEU|ROUGE|score|performance)'
    r'\s+on\s+([A-Z][\w-]*(?:\s+[\w-]+){0,2})',
    re.IGNORECASE,
)

# Simpler pattern: "X% accuracy on Y" without a leading verb.
PERF_PATTERN_SHORT = re.compile(
    r'(\d+\.?\d*)\s*%'
    r'\s+(?:accuracy|F1|BLEU|ROUGE|score|performance)'
    r'\s+on\s+([A-Z][\w-]*(?:\s+[\w-]+){0,2})',
    re.IGNORECASE,
)

SOTA_PATTERN = re.compile(
    r'state[- ]of[- ]the[- ]art|SOTA|new record|best[\s-]known',
    re.IGNORECASE,
)

THEORY_SIGNALS = [
    "theorem", "proof", "formal", "bound", "we prove",
    "we show that", "upper bound", "lower bound", "lemma", "corollary",
]

# Words that indicate a genuinely new capability (not just a score bump).
NEW_CAPABILITY_SIGNALS = [
    "for the first time",
    "first model to",
    "first to demonstrate",
    "previously impossible",
    "not been achieved",
    "new capability",
    "emergent capability",
    "emergent ability",
    "zero-shot without any training",
]

# Words that should not appear in benchmark names — used to trim noisy captures.
_BENCH_STOP_WORDS = frozenset({
    "is", "are", "was", "were", "and", "or", "the", "a", "an", "by", "to",
    "in", "on", "of", "for", "with", "from", "as", "at", "our", "their",
    "its", "we", "not", "be", "has", "had", "have", "this", "that",
    "which", "compared", "reaches", "attained", "using", "via", "over",
    "across", "through", "while", "when", "after", "before",
    "benchmark", "dataset", "task", "test", "evaluation", "math",
})

# ── Helpers ──────────────────────────────────────────────


def _clean_benchmark_name(raw: str) -> str:
    """Strip trailing stop words from a captured benchmark name."""
    words = raw.strip().split()
    # Trim from the right while last word is a stop word
    while words and words[-1].lower() in _BENCH_STOP_WORDS:
        words.pop()
    return " ".join(words) if words else raw.strip()


def _paper_id(paper: dict) -> str:
    return paper.get("id") or paper.get("arxivId") or paper.get("title", "")


def _extract_topics(paper: dict) -> list[str]:
    cats = paper.get("categories") or []
    return [c for c in cats if isinstance(c, str)]


def _discovered_sort_key(paper: dict) -> str:
    """Return a sortable date string (ISO) for ordering papers chronologically."""
    return paper.get("discovered_at") or paper.get("published") or ""


def _normalize_benchmark(name: str) -> str:
    """Normalize benchmark name for grouping (lowercase, strip trailing whitespace)."""
    return name.strip().lower()


# ── Extraction ───────────────────────────────────────────


def _extract_performance_claims(paper: dict) -> list[dict[str, Any]]:
    """Extract (benchmark, score) pairs from a paper's abstract.

    Returns list of dicts with keys: benchmark, score, paper_id.
    Only keeps matches where the context word (accuracy/F1/etc.) is present,
    filtering out stray percentages like "reduces compute by 40%".
    """
    abstract = paper.get("abstract") or ""
    if not abstract:
        return []

    claims: list[dict[str, Any]] = []
    seen: set[tuple[str, float]] = set()

    for pattern in (PERF_PATTERN, PERF_PATTERN_SHORT):
        for m in pattern.finditer(abstract):
            try:
                score = float(m.group(1))
            except ValueError:
                continue
            benchmark = _clean_benchmark_name(m.group(2))
            if not benchmark:
                continue
            key = (_normalize_benchmark(benchmark), score)
            if key not in seen:
                seen.add(key)
                claims.append({
                    "benchmark": benchmark,
                    "benchmark_norm": _normalize_benchmark(benchmark),
                    "score": score,
                    "paper_id": _paper_id(paper),
                })

    return claims


def _has_sota_claim(paper: dict) -> bool:
    abstract = paper.get("abstract") or ""
    return bool(SOTA_PATTERN.search(abstract))


def _has_theory_explanation(abstract: str, benchmark_norm: str) -> bool:
    """Check if an abstract provides a theoretical explanation for a benchmark."""
    text_lower = abstract.lower()
    if benchmark_norm not in text_lower:
        return False
    return any(sig in text_lower for sig in THEORY_SIGNALS)


def _has_new_capability_signal(paper: dict) -> bool:
    abstract = (paper.get("abstract") or "").lower()
    return any(sig in abstract for sig in NEW_CAPABILITY_SIGNALS)


# ── Detection logic ─────────────────────────────────────


def _detect_capability_jumps(papers: list[dict]) -> list[ResearchSignal]:
    """Detect large accuracy jumps on benchmarks with no theoretical explanation."""

    # Step 1: Extract all performance claims
    all_claims: list[dict[str, Any]] = []
    for paper in papers:
        all_claims.extend(_extract_performance_claims(paper))

    if not all_claims:
        return []

    # Step 2: Build per-benchmark timeline
    # Group by normalized benchmark name, ordered by paper discovery date
    paper_by_id: dict[str, dict] = {_paper_id(p): p for p in papers}
    benchmark_timeline: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in all_claims:
        benchmark_timeline[claim["benchmark_norm"]].append(claim)

    # Sort each benchmark timeline by paper discovery date
    for bench in benchmark_timeline:
        benchmark_timeline[bench].sort(
            key=lambda c: _discovered_sort_key(paper_by_id.get(c["paper_id"], {}))
        )

    # Step 3: Detect jumps
    signals: list[ResearchSignal] = []
    jump_threshold = 15.0  # percentage points

    for bench_norm, claims in benchmark_timeline.items():
        if len(claims) < 2:
            continue

        # Find the biggest jump: compare each entry to the previous best
        running_best = claims[0]["score"]
        for i in range(1, len(claims)):
            current = claims[i]
            delta = current["score"] - running_best
            if delta > jump_threshold:
                # Check if any paper explains this jump theoretically
                has_explanation = any(
                    _has_theory_explanation(p.get("abstract") or "", bench_norm)
                    for p in papers
                    if _paper_id(p) != current["paper_id"]
                )
                if not has_explanation:
                    prev_best = running_best
                    new_best = current["score"]
                    # Use the display name from the claim (not normalized)
                    display_bench = current["benchmark"]
                    source_ids = list({c["paper_id"] for c in claims[:i + 1]})
                    topics = [display_bench]
                    # Add paper topics
                    paper = paper_by_id.get(current["paper_id"], {})
                    topics.extend(_extract_topics(paper)[:3])

                    signals.append(ResearchSignal(
                        detector=DETECTOR_NAME,
                        signal_type="frontier_jump_unexplained",
                        title=(
                            f"Capability jump on {display_bench}: "
                            f"{prev_best}% \u2192 {new_best}% \u2014 no theory"
                        ),
                        description=(
                            f"Performance on {display_bench} jumped {delta:.1f}pp. "
                            f"No paper provides formal explanation."
                        ),
                        confidence=min(delta / 30, 0.95),
                        source_papers=source_ids[:10],
                        topics=topics[:5],
                        relevance=0.0,
                        timing_score=0.8,
                        metadata={
                            "benchmark": display_bench,
                            "previous_best": prev_best,
                            "new_best": new_best,
                            "delta": round(delta, 1),
                        },
                    ))

            running_best = max(running_best, current["score"])

    signals.sort(key=lambda s: s.metadata.get("delta", 0), reverse=True)
    return signals[:20]


def _detect_sota_clusters(papers: list[dict]) -> list[ResearchSignal]:
    """Detect multiple SOTA claims on the same benchmark in a short period."""

    # Find papers with SOTA claims and extract their benchmarks
    sota_papers: list[dict] = [p for p in papers if _has_sota_claim(p)]
    if not sota_papers:
        return []

    # Group SOTA-claiming papers by benchmark
    bench_sota: dict[str, list[str]] = defaultdict(list)
    for paper in sota_papers:
        claims = _extract_performance_claims(paper)
        if claims:
            for claim in claims:
                bench_sota[claim["benchmark_norm"]].append(claim["paper_id"])
        else:
            # Paper claims SOTA but we can't extract a benchmark — skip
            pass

    signals: list[ResearchSignal] = []
    for bench_norm, paper_ids in bench_sota.items():
        if len(paper_ids) < 2:
            continue
        unique_ids = list(set(paper_ids))
        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="frontier_sota_cluster",
            title=f"SOTA cluster on {bench_norm}: {len(unique_ids)} papers competing",
            description=(
                f"{len(unique_ids)} papers claim state-of-the-art on {bench_norm} "
                f"in the same period — field is converging, opportunity to explain why."
            ),
            confidence=min(len(unique_ids) / 5, 0.9),
            source_papers=unique_ids[:10],
            topics=[bench_norm],
            relevance=0.0,
            timing_score=0.7,
            metadata={
                "benchmark": bench_norm,
                "num_sota_papers": len(unique_ids),
            },
        ))

    signals.sort(key=lambda s: s.metadata.get("num_sota_papers", 0), reverse=True)
    return signals[:10]


def _detect_new_capabilities(papers: list[dict]) -> list[ResearchSignal]:
    """Detect papers demonstrating genuinely new capabilities."""

    signals: list[ResearchSignal] = []
    for paper in papers:
        if not _has_new_capability_signal(paper):
            continue

        abstract = (paper.get("abstract") or "").lower()
        matched = [sig for sig in NEW_CAPABILITY_SIGNALS if sig in abstract]

        # Check if any other paper provides theory for this
        paper_tokens = set(re.findall(r'[a-z]{4,}', abstract))
        has_explanation = False
        for other in papers:
            if _paper_id(other) == _paper_id(paper):
                continue
            other_abstract = (other.get("abstract") or "").lower()
            if not any(t in other_abstract for t in THEORY_SIGNALS):
                continue
            other_tokens = set(re.findall(r'[a-z]{4,}', other_abstract))
            overlap = len(paper_tokens & other_tokens) / max(len(paper_tokens | other_tokens), 1)
            if overlap > 0.2:
                has_explanation = True
                break

        if not has_explanation:
            title = paper.get("title", "")[:70]
            topics = _extract_topics(paper)[:5]
            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="frontier_new_capability",
                title=f"New capability: {title}",
                description=(
                    f"Paper demonstrates a previously unseen capability "
                    f"(signals: {', '.join(matched[:3])}). No theoretical explanation found."
                ),
                confidence=0.6,
                source_papers=[_paper_id(paper)],
                topics=topics,
                relevance=0.0,
                timing_score=0.8,
                metadata={
                    "capability_signals": matched,
                },
            ))

    return signals[:15]


# ── Public API ───────────────────────────────────────────


def detect(papers: list[dict]) -> list[dict]:
    """Run all frontier detectors on pre-fetched papers.

    Args:
        papers: list of paper dicts (must have at least 'title' and 'abstract').

    Returns:
        list of signal dicts in the standard ResearchSignal format.
    """
    all_signals: list[ResearchSignal] = []

    all_signals.extend(_detect_capability_jumps(papers))
    all_signals.extend(_detect_sota_clusters(papers))
    all_signals.extend(_detect_new_capabilities(papers))

    # Sort by priority: unexplained jumps first, then clusters, then new capabilities
    type_priority = {
        "frontier_jump_unexplained": 0,
        "frontier_sota_cluster": 1,
        "frontier_new_capability": 2,
    }
    all_signals.sort(key=lambda s: (
        type_priority.get(s.signal_type, 5),
        -s.confidence,
    ))

    return [s.to_dict() for s in all_signals]
