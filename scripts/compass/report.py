"""Compass Report Generator — template-based narrative from signals + opportunities.

Generates a structured Markdown report from Compass output. No LLM required;
all prose is template-driven from the data.

Usage:
    from scripts.compass.report import generate_report

    report_md = generate_report(compass_output)
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Signal type → detector mapping (for section routing)
# ---------------------------------------------------------------------------

_TREND_SIGNAL_TYPES = {
    "accelerating_no_theory",
    "accelerating_emerging",
    "decelerating_warning",
}

_FRONTIER_SIGNAL_TYPES = {
    "frontier_new_capability",
    "frontier_jump_unexplained",
    "frontier_sota_cluster",
}

_CONTRARIAN_SIGNAL_TYPES = {
    "consensus_thin_evidence",
    "consensus_fragile",
    "contrarian_opportunity",
    "kg_contradiction_relevant",
    "semantic_opposition",
}

_REVIEWER_SIGNAL_TYPES = {
    "venue_opportunity",
    "venue_gap",
    "venue_cooling",
}

_PORTFOLIO_SIGNAL_TYPES = {
    "portfolio_gap",
    "portfolio_deepening",
    "citation_opportunity",
    "claim_strengthening",
}

_GAP_SIGNAL_TYPES = {
    "uncovered_connection",
    "contradicting_claims",
    "missing_empirical",
    "missing_theory",
    "new_benchmark",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_confidence(c: float) -> str:
    """Format confidence as 0.XX."""
    return f"{c:.2f}"


def _signal_bullet(sig: dict) -> str:
    """Render a single signal as a Markdown bullet."""
    title = sig.get("title", "Untitled")
    stype = sig.get("signal_type", "unknown")
    conf = _fmt_confidence(sig.get("confidence", 0))
    desc = sig.get("description", "")
    # Truncate description to first sentence for brevity
    if desc and ". " in desc:
        desc = desc[: desc.index(". ") + 1]
    line = f'- "{title}" ({stype}, confidence: {conf})'
    if desc:
        line += f" -- {desc}"
    return line


def _section_accelerating(signals: list[dict]) -> str:
    """Render the Accelerating Topics subsection."""
    accel = [
        s for s in signals
        if s.get("signal_type") in ("accelerating_no_theory", "accelerating_emerging")
    ]
    if not accel:
        return "No significant acceleration detected (data accumulating).\n"

    lines: list[str] = []
    for sig in sorted(accel, key=lambda s: s.get("confidence", 0), reverse=True):
        topics = ", ".join(sig.get("topics", [])) or "general"
        conf = _fmt_confidence(sig.get("confidence", 0))
        title = sig.get("title", "Untitled")
        lines.append(f"- **{topics}**: {title} (confidence: {conf})")
    return "\n".join(lines) + "\n"


def _section_emerging_capabilities(signals: list[dict]) -> str:
    """Render the Emerging Capabilities subsection."""
    frontier = [s for s in signals if s.get("signal_type") in _FRONTIER_SIGNAL_TYPES]
    if not frontier:
        return "No new frontier capabilities detected.\n"

    lines: list[str] = []
    sorted_frontier = sorted(frontier, key=lambda s: s.get("confidence", 0), reverse=True)
    for sig in sorted_frontier[:5]:
        lines.append(_signal_bullet(sig))
    if len(sorted_frontier) > 5:
        lines.append(f"*... and {len(sorted_frontier) - 5} more*\n")
    return "\n".join(lines) + "\n"


def _section_consensus_watch(signals: list[dict]) -> str:
    """Render the Consensus Watch subsection."""
    contrarian = [s for s in signals if s.get("signal_type") in _CONTRARIAN_SIGNAL_TYPES]
    if not contrarian:
        return "No consensus fragility detected.\n"

    lines: list[str] = []
    sorted_contrarian = sorted(contrarian, key=lambda s: s.get("confidence", 0), reverse=True)
    for sig in sorted_contrarian[:5]:
        lines.append(_signal_bullet(sig))
    if len(sorted_contrarian) > 5:
        lines.append(f"*... and {len(sorted_contrarian) - 5} more*\n")
    return "\n".join(lines) + "\n"


def _section_opportunities(opportunities: list[dict], max_items: int = 5) -> str:
    """Render the Top Opportunities section."""
    if not opportunities:
        return "No opportunities synthesized.\n"

    lines: list[str] = []
    for i, opp in enumerate(opportunities[:max_items], 1):
        score = opp.get("composite_score", 0)
        title = opp.get("title", "Untitled")
        detectors = ", ".join(opp.get("detectors_hit", []))
        pf = opp.get("portfolio_fit", 0)
        tu = opp.get("timing_urgency", 0)
        rationale = opp.get("rationale", "No rationale available.")

        lines.append(f"### {i}. [{score}] {title}")
        lines.append(f"**Detectors**: {detectors}")
        lines.append(f"**Portfolio fit**: {pf:.2f} | **Timing**: {tu:.2f}")
        lines.append(f"**Rationale**: {rationale}")
        lines.append("")  # blank line between entries

    return "\n".join(lines) + "\n"


def _section_venue_landscape(signals: list[dict]) -> str:
    """Render the Venue Landscape section."""
    venue_signals = [s for s in signals if s.get("signal_type") in _REVIEWER_SIGNAL_TYPES]
    if not venue_signals:
        return "No venue signals detected (reviewer model data accumulating).\n"

    lines: list[str] = []
    sorted_venue = sorted(venue_signals, key=lambda s: s.get("confidence", 0), reverse=True)
    for sig in sorted_venue[:5]:
        stype = sig.get("signal_type", "unknown")
        title = sig.get("title", "Untitled")
        conf = _fmt_confidence(sig.get("confidence", 0))
        desc = sig.get("description", "")
        if desc and ". " in desc:
            desc = desc[: desc.index(". ") + 1]
        label = stype.replace("_", " ").title()
        line = f"- **{label}**: {title} (confidence: {conf})"
        if desc:
            line += f" -- {desc}"
        lines.append(line)
    if len(sorted_venue) > 5:
        lines.append(f"*... and {len(sorted_venue) - 5} more*\n")
    return "\n".join(lines) + "\n"


def _section_portfolio_alignment(signals: list[dict]) -> str:
    """Render the Portfolio Alignment section."""
    portfolio = [s for s in signals if s.get("signal_type") in _PORTFOLIO_SIGNAL_TYPES]
    if not portfolio:
        return "No portfolio alignment signals detected.\n"

    lines: list[str] = []
    sorted_portfolio = sorted(portfolio, key=lambda s: s.get("confidence", 0), reverse=True)
    for sig in sorted_portfolio[:5]:
        lines.append(_signal_bullet(sig))
    return "\n".join(lines) + "\n"


def _section_signal_breakdown(signals: list[dict]) -> str:
    """Render the Signal Breakdown table."""
    if not signals:
        return "No signals to summarize.\n"

    # Group by detector
    by_detector: dict[str, list[dict]] = defaultdict(list)
    for sig in signals:
        det = sig.get("detector", "unknown")
        by_detector[det].append(sig)

    lines: list[str] = [
        "| Detector | Signals | Top Type |",
        "|----------|---------|----------|",
    ]

    for det in sorted(by_detector.keys()):
        sigs = by_detector[det]
        count = len(sigs)
        # Find most common signal_type
        type_counts: dict[str, int] = defaultdict(int)
        for s in sigs:
            type_counts[s.get("signal_type", "unknown")] += 1
        top_type = max(type_counts, key=type_counts.get)  # type: ignore[arg-type]
        top_count = type_counts[top_type]
        lines.append(f"| {det} | {count} | {top_type} ({top_count}) |")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_report(compass_output: dict) -> str:
    """Generate a Markdown report from Compass run_all output.

    Args:
        compass_output: dict with keys: papers_analyzed, total_signals,
                       signals (list), opportunities (list), detectors_run

    Returns:
        Markdown string
    """
    generated_at = compass_output.get("generated_at", "")
    if generated_at:
        # Parse ISO format and display as YYYY-MM-DD
        try:
            dt = datetime.fromisoformat(generated_at)
            date_str = dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            date_str = generated_at[:10] if len(generated_at) >= 10 else generated_at
    else:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    papers_analyzed = compass_output.get("papers_analyzed", 0)
    total_signals = compass_output.get("total_signals", 0)
    signals = compass_output.get("signals", [])
    opportunities = compass_output.get("opportunities", [])
    detectors_run = compass_output.get("detectors_run", [])

    num_detectors = len(detectors_run) if detectors_run else len(
        set(s.get("detector", "") for s in signals)
    )
    num_opportunities = len(opportunities)

    # Build the report
    sections: list[str] = []

    # Header
    sections.append(f"# Compass Report — {date_str}\n")

    # Summary
    sections.append("## Summary")
    sections.append(f"- **Papers analyzed**: {papers_analyzed}")
    sections.append(f"- **Signals detected**: {total_signals} (across {num_detectors} detectors)")
    sections.append(f"- **Opportunities ranked**: {num_opportunities}")
    sections.append("")

    # Field Dynamics
    sections.append("## Field Dynamics\n")

    sections.append("### Accelerating Topics")
    sections.append(_section_accelerating(signals))

    sections.append("### Emerging Capabilities")
    sections.append(_section_emerging_capabilities(signals))

    sections.append("### Consensus Watch")
    sections.append(_section_consensus_watch(signals))

    # Top Opportunities
    sections.append("## Top 5 Opportunities\n")
    sections.append(_section_opportunities(opportunities, max_items=5))

    # Venue Landscape
    sections.append("## Venue Landscape\n")
    sections.append(_section_venue_landscape(signals))

    # Portfolio Alignment
    sections.append("## Portfolio Alignment\n")
    sections.append(_section_portfolio_alignment(signals))

    # Signal Breakdown
    sections.append("## Signal Breakdown\n")
    sections.append(_section_signal_breakdown(signals))

    # Footer
    sections.append("---")
    sections.append("*Generated by Compass — Serre AI Research Intelligence Engine*")

    return "\n".join(sections) + "\n"
