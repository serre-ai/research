#!/usr/bin/env python3
"""Research gap detector — finds research opportunities by comparing papers pairwise.

Reads papers from the Deepwork API (lit_papers table) or a local JSON file and
identifies five types of research gaps: uncovered connections, contradicting claims,
missing empirical validation, missing theory, and new benchmark needs.

Phase 1: keyword matching on abstracts (cheap, no LLM).
Phase 2: optional LLM reasoning on top matches via the Anthropic API.

Usage:
    python3 scripts/gap-detector.py                         # analyze all recent papers
    python3 scripts/gap-detector.py --limit 50              # only top 50 papers
    python3 scripts/gap-detector.py --type missing_empirical # specific gap type
    python3 scripts/gap-detector.py --json                  # JSON output to stdout
    python3 scripts/gap-detector.py --save                  # save to ideas/gaps/YYYY-MM-DD.json
    python3 scripts/gap-detector.py --llm                   # enable Phase 2 LLM reasoning
    python3 scripts/gap-detector.py --api http://localhost:3001  # custom API URL
    python3 scripts/gap-detector.py --input papers.json     # read from local file
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

# ── Constants ────────────────────────────────────────────

DEFAULT_API_URL = "http://localhost:3001"
API_KEY = os.environ.get("DEEPWORK_API_KEY", "")

# Keywords that signal a paper leaves a gap
GAP_SIGNALS = [
    "future work", "remains open", "not yet explored", "left for future",
    "beyond the scope", "we do not address", "remains unclear",
    "has not been studied", "an open question", "warrants further",
    "preliminary", "limited to", "does not generalize", "we leave",
    "further investigation", "not been empirically", "lacks formal",
    "no theoretical", "without formal", "empirically validate",
]

# Keywords that signal theoretical contribution
THEORY_SIGNALS = [
    "theorem", "proof", "formal", "bound", "complexity", "theoretical",
    "analysis", "framework", "formalize", "axiom", "lemma", "corollary",
    "we prove", "we show that", "upper bound", "lower bound",
]

# Keywords that signal empirical contribution
EMPIRICAL_SIGNALS = [
    "experiment", "benchmark", "evaluation", "dataset", "we evaluate",
    "empirical", "we test", "we measure", "ablation", "baseline",
    "accuracy", "f1", "performance", "results show",
]

# Keywords that signal a benchmark contribution
BENCHMARK_SIGNALS = [
    "benchmark", "dataset", "evaluation suite", "test suite", "leaderboard",
    "we introduce a new dataset", "we release", "we collect",
]

# Contradiction signals — phrases that indicate disagreement with prior work
CONTRADICTION_SIGNALS = [
    "contrary to", "in contrast to", "challenges the",
    "does not hold", "fails to", "overestimates", "underestimates",
    "inconsistent with", "disagrees with", "contradicts",
]

# Phrases in abstracts that explicitly call for empirical validation
EMPIRICAL_NEED_SIGNALS = [
    "not been empirically", "empirically validate", "experimental validation",
    "remains to be tested", "needs empirical", "awaits experimental",
    "no experiments", "not yet validated",
]

# Phrases in abstracts that explicitly call for formal analysis
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


# ── Helpers ──────────────────────────────────────────────

def fetch_papers(api_url: str, limit: int = 200) -> list[dict]:
    """Fetch papers from the Deepwork literature API."""
    url = f"{api_url}/api/literature/papers?limit={limit}"
    req = Request(url)
    if API_KEY:
        req.add_header("X-Api-Key", API_KEY)

    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except URLError as e:
        print(f"Error fetching papers from {url}: {e}", file=sys.stderr)
        print("Hint: set DEEPWORK_API_KEY and ensure the API is running.", file=sys.stderr)
        sys.exit(1)


def load_papers_from_file(path: str) -> list[dict]:
    """Load papers from a local JSON file."""
    try:
        with open(path) as f:
            data = json.load(f)
        # Support both raw array and {papers: [...]} wrapper
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "papers" in data:
            return data["papers"]
        if isinstance(data, dict) and "gaps" in data:
            print(f"Error: {path} looks like a gap-detector output, not a papers file.", file=sys.stderr)
            sys.exit(1)
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {path}: {e}", file=sys.stderr)
        sys.exit(1)


def tokenize(text: str) -> frozenset[str]:
    """Tokenize text into significant words (lowercase, 3+ chars, no stop words)."""
    words = re.findall(r'[a-z]{3,}', text.lower())
    return frozenset(w for w in words if w not in STOP_WORDS)


def keyword_overlap_sets(words_a: frozenset[str], words_b: frozenset[str]) -> float:
    """Compute Jaccard similarity between pre-tokenized word sets."""
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


def has_signals(text: str, signals: list[str]) -> list[str]:
    """Return which signal phrases appear in the text."""
    if not text:
        return []
    text_lower = text.lower()
    return [s for s in signals if s in text_lower]


def extract_gap_phrases(abstract: str) -> list[str]:
    """Extract sentences from abstract that mention gaps or limitations."""
    if not abstract:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', abstract)
    gap_sentences = []
    for sent in sentences:
        if any(sig in sent.lower() for sig in GAP_SIGNALS):
            gap_sentences.append(sent.strip())
    return gap_sentences


def classify_paper(paper: dict) -> dict:
    """Classify a paper's contribution type and extract gap information from its abstract."""
    abstract = paper.get("abstract") or ""

    theory = has_signals(abstract, THEORY_SIGNALS)
    empirical = has_signals(abstract, EMPIRICAL_SIGNALS)
    benchmark = has_signals(abstract, BENCHMARK_SIGNALS)
    gaps = extract_gap_phrases(abstract)

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
        "contradiction_signals": has_signals(abstract, CONTRADICTION_SIGNALS),
    }


def paper_id(paper: dict) -> str:
    """Extract a stable identifier for a paper."""
    return paper.get("id") or paper.get("arxivId") or paper.get("title", "")


def paper_ref(paper: dict) -> dict:
    """Build a compact paper reference for gap output."""
    return {"id": paper_id(paper), "title": paper.get("title", "")}


# ── Gap Detectors ────────────────────────────────────────

def find_uncovered_connections(papers: list[dict]) -> list[dict]:
    """Find papers whose topics overlap but are by different author groups."""
    # Pre-tokenize all abstracts
    tokens: list[frozenset[str]] = []
    for p in papers:
        abstract = p.get("abstract") or ""
        tokens.append(tokenize(abstract) if abstract else frozenset())

    gaps = []
    for i in range(len(papers)):
        if not tokens[i]:
            continue
        authors_a = set(str(x) for x in (papers[i].get("authors") or []))
        for j in range(i + 1, len(papers)):
            if not tokens[j]:
                continue

            overlap = keyword_overlap_sets(tokens[i], tokens[j])
            if overlap > 0.25:
                # Check they're from different author groups
                authors_b = set(str(x) for x in (papers[j].get("authors") or []))
                if authors_a & authors_b:
                    continue

                gaps.append({
                    "gap_type": "uncovered_connection",
                    "paper_a": paper_ref(papers[i]),
                    "paper_b": paper_ref(papers[j]),
                    "overlap_score": round(overlap, 3),
                    "description": f"High topic overlap ({overlap:.0%}) between papers by different groups — potential cross-pollination opportunity.",
                })

    gaps.sort(key=lambda g: g["overlap_score"], reverse=True)
    return gaps[:20]


def find_contradictions(papers: list[dict]) -> list[dict]:
    """Find papers that contain contradiction signals and overlap topically."""
    # Pre-tokenize all abstracts
    tokens: dict[str, frozenset[str]] = {}
    for p in papers:
        pid = paper_id(p)
        abstract = p.get("abstract") or ""
        tokens[pid] = tokenize(abstract) if abstract else frozenset()

    # Papers with contradiction signals
    contradicting = [
        (p, has_signals(p.get("abstract", ""), CONTRADICTION_SIGNALS))
        for p in papers
        if has_signals(p.get("abstract", ""), CONTRADICTION_SIGNALS)
    ]

    gaps = []
    seen_pairs: set[tuple[str, str]] = set()

    for paper, signals in contradicting:
        pid_a = paper_id(paper)
        if not tokens.get(pid_a):
            continue
        for other in papers:
            pid_b = paper_id(other)
            if pid_a == pid_b:
                continue

            # Deduplicate: normalize pair order
            pair = (min(pid_a, pid_b), max(pid_a, pid_b))
            if pair in seen_pairs:
                continue

            if not tokens.get(pid_b):
                continue
            overlap = keyword_overlap_sets(tokens[pid_a], tokens[pid_b])
            if overlap > 0.2:
                seen_pairs.add(pair)
                gaps.append({
                    "gap_type": "contradicting_claims",
                    "paper_a": paper_ref(paper),
                    "paper_b": paper_ref(other),
                    "overlap_score": round(overlap, 3),
                    "contradiction_signals": signals,
                    "description": f"Paper A contains contradiction signals ({', '.join(signals[:3])}) and overlaps topically with Paper B — investigate what conditions differentiate their findings.",
                })

    gaps.sort(key=lambda g: g["overlap_score"], reverse=True)
    return gaps[:15]


def find_missing_empirical(papers: list[dict]) -> list[dict]:
    """Find theory papers that explicitly mention needing empirical validation."""
    gaps = []
    for paper in papers:
        info = classify_paper(paper)
        if info["contribution_type"] != "theory":
            continue

        abstract = paper.get("abstract") or ""
        gap_phrases = info["gap_phrases"]

        # Only flag if the paper itself signals a need for empirical work:
        # either gap phrases mention empirical needs, or the abstract contains
        # explicit empirical-need signals
        has_empirical_gap_phrase = any(
            any(kw in phrase.lower() for kw in ["empirical", "experiment", "validate", "test", "evaluate"])
            for phrase in gap_phrases
        )
        has_empirical_need_signal = bool(has_signals(abstract, EMPIRICAL_NEED_SIGNALS))

        if not has_empirical_gap_phrase and not has_empirical_need_signal:
            continue

        gaps.append({
            "gap_type": "missing_empirical",
            "paper": paper_ref(paper),
            "gap_phrases": gap_phrases[:3],
            "theory_signals": info["theory_signals"][:3],
            "description": f"Theory paper with {len(info['theory_signals'])} theoretical markers that explicitly mentions needing empirical validation.",
        })

    return gaps[:15]


def find_missing_theory(papers: list[dict]) -> list[dict]:
    """Find empirical papers that explicitly mention needing formal analysis."""
    gaps = []
    for paper in papers:
        info = classify_paper(paper)
        if info["contribution_type"] not in ("empirical", "benchmark"):
            continue

        abstract = paper.get("abstract") or ""
        gap_phrases = info["gap_phrases"]

        # Only flag if the paper itself signals a need for theory:
        # either gap phrases mention formal/theoretical needs, or the abstract
        # contains explicit theory-need signals
        has_theory_gap_phrase = any(
            any(kw in phrase.lower() for kw in ["formal", "theoretical", "explain", "principled", "theory"])
            for phrase in gap_phrases
        )
        has_theory_need_signal = bool(has_signals(abstract, THEORY_NEED_SIGNALS))

        if not has_theory_gap_phrase and not has_theory_need_signal:
            continue

        gaps.append({
            "gap_type": "missing_theory",
            "paper": paper_ref(paper),
            "gap_phrases": gap_phrases[:3],
            "empirical_signals": info["empirical_signals"][:3],
            "description": f"Empirical paper with {len(info['empirical_signals'])} empirical markers that explicitly mentions needing formal analysis.",
        })

    return gaps[:15]


def find_benchmark_needs(papers: list[dict]) -> list[dict]:
    """Find topic clusters with 3+ papers but no benchmark."""
    # Pre-compute classifications once per paper
    classifications: dict[str, dict] = {}
    for paper in papers:
        pid = paper_id(paper)
        if pid not in classifications:
            classifications[pid] = classify_paper(paper)

    # Group papers by categories
    topic_groups: dict[str, list[dict]] = defaultdict(list)
    for paper in papers:
        categories = paper.get("categories") or []
        for cat in categories:
            if isinstance(cat, str):
                topic_groups[cat].append(paper)

    gaps = []
    for topic, group in topic_groups.items():
        if len(group) < 3:
            continue

        has_benchmark = any(
            classifications[paper_id(p)]["contribution_type"] == "benchmark"
            for p in group
        )

        if not has_benchmark:
            gaps.append({
                "gap_type": "new_benchmark",
                "topic": topic,
                "paper_count": len(group),
                "papers": [paper_ref(p) for p in group[:5]],
                "description": f"{len(group)} papers in '{topic}' with no benchmark contribution — the field may need a controlled evaluation suite.",
            })

    gaps.sort(key=lambda g: g["paper_count"], reverse=True)
    return gaps[:10]


# ── Phase 2: LLM Reasoning ──────────────────────────────

def llm_enrich(gaps: list[dict], top_n: int = 10) -> list[dict]:
    """Enrich top gap candidates with LLM reasoning via the Anthropic API."""
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        print("Warning: ANTHROPIC_API_KEY not set, skipping LLM enrichment.", file=sys.stderr)
        return gaps

    enriched = []
    for gap in gaps[:top_n]:
        prompt = build_llm_prompt(gap)
        try:
            response = call_anthropic(anthropic_key, prompt)
            gap["llm_analysis"] = response
            enriched.append(gap)
        except Exception as e:
            print(f"LLM enrichment failed for gap: {e}", file=sys.stderr)
            enriched.append(gap)

    # Keep remaining gaps without enrichment
    enriched.extend(gaps[top_n:])
    return enriched


def build_llm_prompt(gap: dict) -> str:
    """Build a concise prompt for LLM gap analysis."""
    gap_type = gap.get("gap_type", "unknown")

    if gap_type in ("uncovered_connection", "contradicting_claims"):
        return (
            f"Gap type: {gap_type}\n"
            f"Paper A: {gap['paper_a']['title']}\n"
            f"Paper B: {gap['paper_b']['title']}\n"
            f"Overlap score: {gap.get('overlap_score', 'N/A')}\n\n"
            "Is there a genuine research opportunity connecting these papers? "
            "If so, describe it in 2-3 sentences: what the opportunity is, "
            "why it hasn't been explored, and what approach would work."
        )
    elif gap_type in ("missing_empirical", "missing_theory"):
        paper = gap.get("paper", {})
        return (
            f"Gap type: {gap_type}\n"
            f"Paper: {paper.get('title', 'Unknown')}\n"
            f"Gap phrases: {'; '.join(gap.get('gap_phrases', []))}\n\n"
            "What specific empirical or theoretical work would fill this gap? "
            "Describe the opportunity in 2-3 sentences."
        )
    else:
        return (
            f"Gap type: {gap_type}\n"
            f"Description: {gap.get('description', '')}\n\n"
            "Is this a real research opportunity? Describe it in 2-3 sentences."
        )


def call_anthropic(api_key: str, prompt: str) -> str:
    """Call the Anthropic Messages API directly for LLM reasoning."""
    url = "https://api.anthropic.com/v1/messages"
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 200,
        "temperature": 0.3,
        "system": "You are a research gap analyst. Be concise and specific.",
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }).encode()

    req = Request(url, data=payload, method="POST")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("Content-Type", "application/json")

    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        return data["content"][0]["text"]


# ── Main ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Research gap detector — finds opportunities by comparing papers pairwise."
    )
    parser.add_argument("--limit", type=int, default=200, help="Max papers to analyze (default: 200)")
    parser.add_argument("--type", choices=[
        "uncovered_connection", "contradicting_claims",
        "missing_empirical", "missing_theory", "new_benchmark",
    ], help="Only detect a specific gap type")
    parser.add_argument("--json", action="store_true", help="JSON output to stdout")
    parser.add_argument("--save", action="store_true", help="Save results to ideas/gaps/YYYY-MM-DD.json")
    parser.add_argument("--llm", action="store_true", help="Enable Phase 2 LLM enrichment on top matches")
    parser.add_argument("--api", default=DEFAULT_API_URL, help=f"API base URL (default: {DEFAULT_API_URL})")
    parser.add_argument("--input", metavar="FILE", help="Read papers from a local JSON file instead of the API")

    args = parser.parse_args()

    # Fetch papers
    if args.input:
        papers = load_papers_from_file(args.input)
    else:
        papers = fetch_papers(args.api, args.limit)

    if not papers:
        print("No papers found. Ensure the literature monitor has run at least once.", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing {len(papers)} papers...", file=sys.stderr)

    # Run gap detection
    all_gaps: list[dict] = []
    detectors = {
        "uncovered_connection": find_uncovered_connections,
        "contradicting_claims": find_contradictions,
        "missing_empirical": find_missing_empirical,
        "missing_theory": find_missing_theory,
        "new_benchmark": find_benchmark_needs,
    }

    if args.type:
        gaps = detectors[args.type](papers)
        all_gaps.extend(gaps)
    else:
        for gap_type, detector in detectors.items():
            gaps = detector(papers)
            all_gaps.extend(gaps)
            print(f"  {gap_type}: {len(gaps)} gaps found", file=sys.stderr)

    # Phase 2: optional LLM enrichment
    if args.llm and all_gaps:
        print(f"Running LLM enrichment on top 10 gaps...", file=sys.stderr)
        all_gaps = llm_enrich(all_gaps, top_n=10)

    # Sort by overlap score where available, then by gap type priority
    type_priority = {
        "contradicting_claims": 0,
        "missing_empirical": 1,
        "missing_theory": 2,
        "uncovered_connection": 3,
        "new_benchmark": 4,
    }
    all_gaps.sort(key=lambda g: (
        type_priority.get(g.get("gap_type", ""), 5),
        -(g.get("overlap_score", 0)),
    ))

    # Output
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "papers_analyzed": len(papers),
        "total_gaps": len(all_gaps),
        "gaps": all_gaps,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    elif args.save:
        repo_root = Path(__file__).resolve().parent.parent
        out_dir = repo_root / "ideas" / "gaps"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        out_file.write_text(json.dumps(result, indent=2))
        print(f"Saved {len(all_gaps)} gaps to {out_file}", file=sys.stderr)
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f"Gap Analysis: {len(all_gaps)} opportunities from {len(papers)} papers")
        print(f"{'='*60}\n")

        for i, gap in enumerate(all_gaps, 1):
            gt = gap.get("gap_type", "unknown")
            print(f"[{i}] {gt.upper().replace('_', ' ')}")
            if "paper_a" in gap and "paper_b" in gap:
                print(f"    Paper A: {gap['paper_a']['title'][:80]}")
                print(f"    Paper B: {gap['paper_b']['title'][:80]}")
                print(f"    Overlap: {gap.get('overlap_score', 'N/A')}")
            elif "paper" in gap:
                print(f"    Paper: {gap['paper']['title'][:80]}")
            elif "topic" in gap:
                print(f"    Topic: {gap['topic']} ({gap['paper_count']} papers)")
            print(f"    {gap.get('description', '')}")
            if gap.get("llm_analysis"):
                print(f"    LLM: {gap['llm_analysis'][:200]}")
            print()


if __name__ == "__main__":
    main()
