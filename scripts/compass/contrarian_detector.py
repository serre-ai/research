"""Contrarian detector — consensus fragility analysis.

Finds claims where field consensus is forming but evidence is thin:
papers that everyone cites but nobody independently verifies.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

try:
    from .schema import ResearchSignal
except ImportError:
    from schema import ResearchSignal  # type: ignore

# ── Constants ─────────────────────────────────────────────

DETECTOR_NAME = "contrarian"

# Patterns that indicate an empirical claim
CLAIM_PATTERNS = [
    r"we show that\b",
    r"we find that\b",
    r"we demonstrate\b",
    r"our results demonstrate\b",
    r"our results show\b",
    r"our experiments show\b",
    r"achieves?\s+\d+[\.\d]*\s*%",
    r"outperforms?",
    r"improves?\s+over",
    r"surpass(?:es)?",
    r"state[- ]of[- ]the[- ]art",
    r"significant(?:ly)?\s+(?:better|improve|outperform|higher|lower)",
]

COMPILED_CLAIM_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CLAIM_PATTERNS]

# Patterns indicating contradiction / contrarian stance
CONTRADICTION_PATTERNS = [
    r"contrary to",
    r"in contrast to",
    r"challenges?\s+the\s+assumption",
    r"does not hold",
    r"fails? to",
    r"we challenge",
    r"contradicts?",
    r"inconsistent with",
    r"overestimates?",
    r"underestimates?",
    r"disagrees? with",
    r"we refute",
    r"does not generalize",
    r"commonly believed",
    r"widely assumed",
    r"prevailing (?:view|wisdom|assumption)",
]

COMPILED_CONTRADICTION_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CONTRADICTION_PATTERNS]

# Hedging language that weakens a consensus
HEDGING_WORDS = [
    "may", "might", "suggests", "preliminary", "initial",
    "appears to", "seems to", "potentially", "likely",
    "could", "we conjecture", "we hypothesize",
    "tentatively", "it is possible",
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


# ── Helpers ───────────────────────────────────────────────

def _tokenize(text: str) -> frozenset[str]:
    """Tokenize text into a frozenset of meaningful words."""
    words = re.findall(r'[a-z]{3,}', text.lower())
    return frozenset(w for w in words if w not in STOP_WORDS)


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    """Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union) if union else 0.0


def _paper_id(paper: dict) -> str:
    """Extract a stable paper identifier."""
    return paper.get("id") or paper.get("arxivId") or paper.get("title", "")


def _extract_topics(paper: dict) -> list[str]:
    """Extract topic labels from a paper (categories or keywords)."""
    cats = paper.get("categories") or []
    return [c for c in cats if isinstance(c, str)]


def _extract_claims(abstract: str) -> list[str]:
    """Extract sentences that make empirical claims from an abstract."""
    if not abstract:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', abstract)
    claims: list[str] = []
    for sentence in sentences:
        for pattern in COMPILED_CLAIM_PATTERNS:
            if pattern.search(sentence):
                claims.append(sentence.strip())
                break
    return claims


def _has_contradiction_signals(text: str) -> list[str]:
    """Return list of contradiction patterns found in text."""
    if not text:
        return []
    found: list[str] = []
    for pattern in COMPILED_CONTRADICTION_PATTERNS:
        if pattern.search(text):
            found.append(pattern.pattern)
    return found


def _has_hedging(text: str) -> bool:
    """Check if text contains hedging language."""
    if not text:
        return False
    text_lower = text.lower()
    return any(h in text_lower for h in HEDGING_WORDS)


def _author_group_key(paper: dict) -> frozenset[str]:
    """Return a frozenset of author names for grouping."""
    authors = paper.get("authors") or []
    return frozenset(str(a) for a in authors)


def _summarize_claim(claim: str, max_len: int = 80) -> str:
    """Shorten a claim sentence for display."""
    claim = claim.strip()
    if len(claim) <= max_len:
        return claim
    return claim[:max_len - 3] + "..."


# ── Consensus cluster detection ──────────────────────────

def _build_consensus_clusters(
    papers: list[dict],
) -> list[dict[str, Any]]:
    """Find clusters of papers making similar claims.

    Returns list of cluster dicts with keys:
        claim_tokens, claim_summary, papers, author_groups, has_hedging
    """
    # Step 1: Extract claims per paper
    paper_claims: list[tuple[dict, str, frozenset[str]]] = []
    for paper in papers:
        abstract = paper.get("abstract") or ""
        claims = _extract_claims(abstract)
        for claim in claims:
            tokens = _tokenize(claim)
            if len(tokens) >= 3:  # need at least 3 meaningful words
                paper_claims.append((paper, claim, tokens))

    if not paper_claims:
        return []

    # Step 2: Build clusters via greedy merging
    # Each cluster starts as a single (paper, claim) pair
    clusters: list[dict[str, Any]] = []
    assigned: set[int] = set()

    for i, (paper_i, claim_i, tokens_i) in enumerate(paper_claims):
        if i in assigned:
            continue

        cluster_papers: list[dict] = [paper_i]
        cluster_claims: list[str] = [claim_i]
        cluster_claim_tokens: list[frozenset[str]] = [tokens_i]
        cluster_tokens = tokens_i
        assigned.add(i)

        for j in range(i + 1, len(paper_claims)):
            if j in assigned:
                continue
            paper_j, claim_j, tokens_j = paper_claims[j]

            # Compare against each existing claim in the cluster (any-match)
            # rather than the expanding union, to avoid Jaccard dilution
            best_overlap = max(
                _jaccard(ct, tokens_j) for ct in cluster_claim_tokens
            )
            if best_overlap > 0.3:
                cluster_papers.append(paper_j)
                cluster_claims.append(claim_j)
                cluster_claim_tokens.append(tokens_j)
                # Keep union for contrarian matching later
                cluster_tokens = cluster_tokens | tokens_j
                assigned.add(j)

        # Only keep clusters with 3+ papers (lowered threshold for small corpora)
        if len(cluster_papers) >= 3:
            # Deduplicate papers by ID
            seen_ids: set[str] = set()
            unique_papers: list[dict] = []
            for p in cluster_papers:
                pid = _paper_id(p)
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    unique_papers.append(p)

            author_groups: list[frozenset[str]] = []
            for p in unique_papers:
                ag = _author_group_key(p)
                if ag and ag not in author_groups:
                    author_groups.append(ag)

            # Check if any of the claims contain hedging
            hedging = any(_has_hedging(c) for c in cluster_claims)

            clusters.append({
                "claim_tokens": cluster_tokens,
                "claim_summary": _summarize_claim(cluster_claims[0]),
                "papers": unique_papers,
                "author_groups": author_groups,
                "has_hedging": hedging,
                "claims": cluster_claims,
            })

    return clusters


# ── Individual signal detectors ──────────────────────────

def _find_thin_consensus(clusters: list[dict[str, Any]]) -> list[ResearchSignal]:
    """Find consensus clusters where many papers cite but few groups verify."""
    signals: list[ResearchSignal] = []

    for cluster in clusters:
        n_papers = len(cluster["papers"])
        n_groups = len(cluster["author_groups"])
        claim_summary = cluster["claim_summary"]

        # Flag: many papers but few independent author groups
        # With small corpora (314 papers), even 3 papers with 1 group is notable
        if n_papers >= 3 and n_groups <= 2:
            all_topics: list[str] = []
            for p in cluster["papers"]:
                all_topics.extend(_extract_topics(p))
            topics = list(set(all_topics))[:5]

            signals.append(ResearchSignal(
                detector=DETECTOR_NAME,
                signal_type="consensus_thin_evidence",
                title=(
                    f"Thin consensus: '{claim_summary}' "
                    f"— {n_papers} papers, only {n_groups} independent groups"
                ),
                description=(
                    f"A claim appears across {n_papers} papers but is backed by only "
                    f"{n_groups} independent author group(s). This may indicate citation "
                    f"incest — the consensus looks broad but rests on a narrow evidential "
                    f"base. Independent replication would be high-impact."
                ),
                confidence=min(n_papers / 10, 0.9),
                source_papers=[_paper_id(p) for p in cluster["papers"]],
                topics=topics,
                relevance=0.0,
                timing_score=0.3,
                metadata={
                    "n_papers": n_papers,
                    "n_author_groups": n_groups,
                    "claim_summary": claim_summary,
                },
            ))

    signals.sort(key=lambda s: s.metadata.get("n_papers", 0), reverse=True)
    return signals[:15]


def _find_fragile_consensus(clusters: list[dict[str, Any]]) -> list[ResearchSignal]:
    """Find consensus clusters where claims are hedged / preliminary."""
    signals: list[ResearchSignal] = []

    for cluster in clusters:
        if not cluster["has_hedging"]:
            continue

        n_papers = len(cluster["papers"])
        n_groups = len(cluster["author_groups"])
        claim_summary = cluster["claim_summary"]

        all_topics: list[str] = []
        for p in cluster["papers"]:
            all_topics.extend(_extract_topics(p))
        topics = list(set(all_topics))[:5]

        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="consensus_fragile",
            title=(
                f"Fragile consensus: '{claim_summary}' "
                f"— hedged language in {n_papers}-paper cluster"
            ),
            description=(
                f"Multiple papers ({n_papers}) converge on a similar claim, but the "
                f"language is hedged ('may', 'suggests', 'preliminary'). The consensus "
                f"may be premature — a rigorous study could either solidify or overturn it."
            ),
            confidence=min(n_papers / 10, 0.9),
            source_papers=[_paper_id(p) for p in cluster["papers"]],
            topics=topics,
            relevance=0.0,
            timing_score=0.3,
            metadata={
                "n_papers": n_papers,
                "n_author_groups": n_groups,
                "claim_summary": claim_summary,
                "hedging_detected": True,
            },
        ))

    signals.sort(key=lambda s: s.metadata.get("n_papers", 0), reverse=True)
    return signals[:15]


def _find_contrarian_opportunities(
    papers: list[dict],
    clusters: list[dict[str, Any]],
) -> list[ResearchSignal]:
    """Find papers that contradict a consensus cluster — potential breakthroughs."""
    signals: list[ResearchSignal] = []

    # Identify papers with contradiction signals
    contrarian_papers: list[tuple[dict, list[str]]] = []
    for paper in papers:
        abstract = paper.get("abstract") or ""
        contra_sigs = _has_contradiction_signals(abstract)
        if contra_sigs:
            contrarian_papers.append((paper, contra_sigs))

    if not contrarian_papers or not clusters:
        return signals

    for paper, contra_sigs in contrarian_papers:
        paper_tokens = _tokenize(paper.get("abstract") or "")
        if not paper_tokens:
            continue

        for cluster in clusters:
            overlap = _jaccard(paper_tokens, cluster["claim_tokens"])
            if overlap > 0.2:
                n_papers = len(cluster["papers"])
                claim_summary = cluster["claim_summary"]
                paper_title = paper.get("title", "")[:60]

                all_topics = list(set(
                    _extract_topics(paper)
                    + [t for p in cluster["papers"] for t in _extract_topics(p)]
                ))[:5]

                signals.append(ResearchSignal(
                    detector=DETECTOR_NAME,
                    signal_type="contrarian_opportunity",
                    title=(
                        f"Contrarian: '{paper_title}' challenges "
                        f"{n_papers}-paper consensus"
                    ),
                    description=(
                        f"Paper contradicts a consensus cluster around "
                        f"'{claim_summary}'. Contradiction signals: "
                        f"{', '.join(contra_sigs[:3])}. "
                        f"If the contrarian view is correct, this is a "
                        f"high-impact research direction."
                    ),
                    confidence=min(overlap * 2, 0.9),
                    source_papers=(
                        [_paper_id(paper)]
                        + [_paper_id(p) for p in cluster["papers"]]
                    ),
                    topics=all_topics,
                    relevance=0.0,
                    timing_score=0.3,
                    metadata={
                        "contrarian_paper": _paper_id(paper),
                        "n_consensus_papers": n_papers,
                        "claim_summary": claim_summary,
                        "contradiction_signals": contra_sigs[:3],
                        "overlap_score": round(overlap, 3),
                    },
                ))

    signals.sort(key=lambda s: s.metadata.get("overlap_score", 0), reverse=True)
    return signals[:15]


# ── Embedding-based opposition detection ─────────────────

# Claim-direction keywords for semantic opposition heuristic
_POSITIVE_CLAIMS = frozenset([
    "improves", "achieves", "outperforms", "demonstrates",
    "confirms", "validates", "advances", "enables",
])
_NEGATIVE_CLAIMS = frozenset([
    "fails", "does not", "contrary to", "challenges",
    "refutes", "contradicts", "unreliable", "degrades",
])


def _find_semantic_opposition(papers: list[dict]) -> list[ResearchSignal]:
    """Find papers that are semantically similar but make opposing claims.

    Looks for paper pairs where:
    1. High topic overlap — they address the same research area
    2. One uses positive claim language, the other uses negative/contradicting language

    When embeddings are available (paper.embedding_str), this will use cosine
    similarity > 0.8 to detect same-topic pairs (DW-395).  Until then, uses
    keyword overlap as a proxy.
    """
    signals: list[ResearchSignal] = []

    # Only run if embeddings are available (signals embedding-ready path)
    has_embeddings = any(p.get("embedding_str") for p in papers)
    if not has_embeddings:
        return signals

    for i, a in enumerate(papers):
        abs_a = (a.get("abstract") or "").lower()
        if not abs_a:
            continue
        a_positive = any(w in abs_a for w in _POSITIVE_CLAIMS)
        a_negative = any(w in abs_a for w in _NEGATIVE_CLAIMS)

        for j, b in enumerate(papers):
            if i >= j:
                continue
            abs_b = (b.get("abstract") or "").lower()
            if not abs_b:
                continue
            b_positive = any(w in abs_b for w in _POSITIVE_CLAIMS)
            b_negative = any(w in abs_b for w in _NEGATIVE_CLAIMS)

            # One positive, other negative = opposition
            if not ((a_positive and b_negative) or (a_negative and b_positive)):
                continue

            # Check topic overlap (high overlap + opposition = contrarian signal)
            # Phase 2 (DW-395): replace with embedding cosine similarity > 0.8
            topics_a = set(re.findall(r'[a-z]{4,}', abs_a)) - STOP_WORDS
            topics_b = set(re.findall(r'[a-z]{4,}', abs_b)) - STOP_WORDS
            overlap = len(topics_a & topics_b) / max(len(topics_a | topics_b), 1)

            if overlap > 0.15:  # modest overlap + opposition
                signals.append(ResearchSignal(
                    detector=DETECTOR_NAME,
                    signal_type="semantic_opposition",
                    title=(
                        f"Opposing views: {a.get('title', '')[:50]} "
                        f"vs {b.get('title', '')[:50]}"
                    ),
                    description=(
                        f"These papers address similar topics (overlap {overlap:.0%}) "
                        f"but reach opposing conclusions."
                    ),
                    confidence=min(overlap * 2, 0.9),
                    source_papers=[_paper_id(a), _paper_id(b)],
                    topics=list(topics_a & topics_b)[:5],
                    timing_score=0.4,
                    metadata={"overlap": round(overlap, 3)},
                ))

    return signals[:10]


# ── Public API ────────────────────────────────────────────

def detect(papers: list[dict]) -> list[dict]:
    """Run all contrarian detectors on pre-fetched papers.

    Args:
        papers: list of paper dicts (must have at least 'title' and 'abstract').

    Returns:
        list of signal dicts in the standard ResearchSignal format.
    """
    clusters = _build_consensus_clusters(papers)

    all_signals: list[ResearchSignal] = []
    all_signals.extend(_find_thin_consensus(clusters))
    all_signals.extend(_find_fragile_consensus(clusters))
    all_signals.extend(_find_contrarian_opportunities(papers, clusters))
    all_signals.extend(_find_semantic_opposition(papers))

    # Sort by signal_type priority, then confidence descending
    type_priority = {
        "contrarian_opportunity": 0,
        "semantic_opposition": 1,
        "consensus_thin_evidence": 2,
        "consensus_fragile": 3,
    }
    all_signals.sort(key=lambda s: (
        type_priority.get(s.signal_type, 5),
        -s.confidence,
    ))

    return [s.to_dict() for s in all_signals]
