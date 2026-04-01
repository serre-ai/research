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
    from .db import batch_cosine_similarity
except ImportError:
    from schema import ResearchSignal  # type: ignore
    try:
        from db import batch_cosine_similarity  # type: ignore
    except ImportError:
        batch_cosine_similarity = None  # type: ignore

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


# ── Knowledge graph contradiction detection ───────────────

def _find_kg_contradictions(papers: list[dict]) -> list[ResearchSignal]:
    """Find papers that relate to contradicting claims in the knowledge graph."""
    try:
        from .db import get_connection
    except ImportError:
        from db import get_connection

    try:
        conn = get_connection()
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get contradiction pairs from KG
        cur.execute("""
            SELECT c1.statement as claim_a, c1.project as project_a, c1.confidence as conf_a,
                   c2.statement as claim_b, c2.project as project_b, c2.confidence as conf_b
            FROM claim_relations r
            JOIN claims c1 ON c1.id = r.source_id
            JOIN claims c2 ON c2.id = r.target_id
            WHERE r.relation = 'contradicts'
            ORDER BY r.created_at DESC
            LIMIT 20
        """)
        contradictions = cur.fetchall()
        cur.close()

        # For each contradiction, check if recent papers relate to either side
        signals = []
        for contra in contradictions:
            # Find papers whose abstracts mention keywords from either claim
            claim_a_words = set(re.findall(r'[a-z]{4,}', contra['claim_a'].lower()))
            claim_b_words = set(re.findall(r'[a-z]{4,}', contra['claim_b'].lower()))

            for paper in papers:
                abstract = (paper.get('abstract') or '').lower()
                if not abstract:
                    continue
                paper_words = set(re.findall(r'[a-z]{4,}', abstract))

                overlap_a = len(claim_a_words & paper_words) / max(len(claim_a_words), 1)
                overlap_b = len(claim_b_words & paper_words) / max(len(claim_b_words), 1)

                if overlap_a > 0.3 or overlap_b > 0.3:
                    signals.append(ResearchSignal(
                        detector=DETECTOR_NAME,
                        signal_type="kg_contradiction_relevant",
                        title=f"Paper relates to KG contradiction: {contra['claim_a'][:50]} vs {contra['claim_b'][:50]}",
                        description=f"Recent paper '{paper.get('title', '')[:60]}' overlaps with a known contradiction in the knowledge graph.",
                        confidence=max(overlap_a, overlap_b),
                        source_papers=[_paper_id(paper)],
                        source_claims=[],
                        topics=list(claim_a_words & claim_b_words & paper_words)[:5],
                        timing_score=0.5,
                        metadata={"claim_a": contra['claim_a'][:100], "claim_b": contra['claim_b'][:100]},
                    ))

        return signals[:10]
    except Exception:
        # DB not available — skip KG integration silently
        return []


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


def _find_semantic_opposition_keyword(papers: list[dict]) -> list[ResearchSignal]:
    """Find opposing papers using keyword overlap as a topic-similarity proxy."""
    signals: list[ResearchSignal] = []

    claim_papers: list[tuple[int, dict, str, bool, bool]] = []
    for i, p in enumerate(papers):
        abs_text = (p.get("abstract") or "").lower()
        if not abs_text:
            continue
        pos = any(w in abs_text for w in _POSITIVE_CLAIMS)
        neg = any(w in abs_text for w in _NEGATIVE_CLAIMS)
        if pos or neg:
            claim_papers.append((i, p, abs_text, pos, neg))

    for idx_a, (i, a, abs_a, a_positive, a_negative) in enumerate(claim_papers):
        for idx_b, (j, b, abs_b, b_positive, b_negative) in enumerate(claim_papers):
            if idx_a >= idx_b:
                continue

            if not ((a_positive and b_negative) or (a_negative and b_positive)):
                continue

            topics_a = set(re.findall(r'[a-z]{4,}', abs_a)) - STOP_WORDS
            topics_b = set(re.findall(r'[a-z]{4,}', abs_b)) - STOP_WORDS
            overlap = len(topics_a & topics_b) / max(len(topics_a | topics_b), 1)

            if overlap > 0.15:
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


def _find_semantic_opposition_embedding(papers: list[dict]) -> list[ResearchSignal]:
    """Find opposing papers using embedding cosine similarity > 0.8.

    Uses batch_cosine_similarity() from db.py to find high-similarity pairs,
    then checks for opposing claim language to identify contrarian signals.
    """
    signals: list[ResearchSignal] = []

    if batch_cosine_similarity is None:
        return _find_semantic_opposition_keyword(papers)

    # Pre-filter: only consider papers with claim language AND embeddings
    claim_papers: list[tuple[dict, str, bool, bool]] = []
    paper_ids: list[str] = []
    id_to_paper: dict[str, tuple[dict, str, bool, bool]] = {}

    for p in papers:
        if not p.get("embedding_str"):
            continue
        abs_text = (p.get("abstract") or "").lower()
        if not abs_text:
            continue
        pos = any(w in abs_text for w in _POSITIVE_CLAIMS)
        neg = any(w in abs_text for w in _NEGATIVE_CLAIMS)
        if pos or neg:
            pid = _paper_id(p)
            claim_papers.append((p, abs_text, pos, neg))
            paper_ids.append(pid)
            id_to_paper[pid] = (p, abs_text, pos, neg)

    if len(paper_ids) < 2:
        return signals

    # Get pairwise similarities — batch_cosine_similarity only returns > 0.5
    similarities = batch_cosine_similarity(paper_ids)

    for (id_a, id_b), sim in similarities.items():
        if sim < 0.8:
            continue

        if id_a not in id_to_paper or id_b not in id_to_paper:
            continue

        a, abs_a, a_pos, a_neg = id_to_paper[id_a]
        b, abs_b, b_pos, b_neg = id_to_paper[id_b]

        # One positive, other negative = opposition
        if not ((a_pos and b_neg) or (a_neg and b_pos)):
            continue

        signals.append(ResearchSignal(
            detector=DETECTOR_NAME,
            signal_type="semantic_opposition",
            title=(
                f"Opposing views: {a.get('title', '')[:50]} "
                f"vs {b.get('title', '')[:50]}"
            ),
            description=(
                f"These papers are semantically similar (cosine {sim:.0%}) "
                f"but reach opposing conclusions."
            ),
            confidence=min(sim, 0.9),
            source_papers=[_paper_id(a), _paper_id(b)],
            topics=list(
                (set(re.findall(r'[a-z]{4,}', abs_a)) - STOP_WORDS)
                & (set(re.findall(r'[a-z]{4,}', abs_b)) - STOP_WORDS)
            )[:5],
            timing_score=0.4,
            metadata={"embedding_similarity": round(sim, 3)},
        ))

    return signals[:10]


def _find_semantic_opposition(papers: list[dict]) -> list[ResearchSignal]:
    """Find papers that are semantically similar but make opposing claims.

    Looks for paper pairs where:
    1. High topic overlap — they address the same research area
    2. One uses positive claim language, the other uses negative/contradicting language

    When embeddings are available (paper.embedding_str), uses cosine similarity
    > 0.8 via batch_cosine_similarity() for accurate same-topic detection.
    Falls back to keyword overlap otherwise.
    """
    # Only run if embeddings are available
    has_embeddings = any(p.get("embedding_str") for p in papers)
    if not has_embeddings:
        return []

    try:
        return _find_semantic_opposition_embedding(papers)
    except Exception:
        return _find_semantic_opposition_keyword(papers)


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
    all_signals.extend(_find_kg_contradictions(papers))

    # Sort by signal_type priority, then confidence descending
    type_priority = {
        "contrarian_opportunity": 0,
        "kg_contradiction_relevant": 1,
        "semantic_opposition": 2,
        "consensus_thin_evidence": 3,
        "consensus_fragile": 4,
    }
    all_signals.sort(key=lambda s: (
        type_priority.get(s.signal_type, 5),
        -s.confidence,
    ))

    return [s.to_dict() for s in all_signals]
