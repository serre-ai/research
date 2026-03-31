"""Signal Fusion Engine — synthesize signals from all detectors into ranked opportunities.

Takes raw signals from gap_detector, trend_detector, portfolio_optimizer (and future
detectors) and clusters them by topic overlap, computing composite scores for each
research opportunity.
"""

from __future__ import annotations

from statistics import mean
from typing import Any


def _jaccard(a: list[str], b: list[str]) -> float:
    """Compute Jaccard similarity between two topic lists."""
    set_a = set(t.lower() for t in a)
    set_b = set(t.lower() for t in b)
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def _cluster_signals(signals: list[dict]) -> list[list[dict]]:
    """Greedy clustering: group signals with >0.3 topic overlap.

    Signals are sorted by confidence desc. Each signal is assigned to the first
    existing cluster with >0.3 topic overlap, or starts a new cluster.
    """
    sorted_sigs = sorted(signals, key=lambda s: s.get("confidence", 0), reverse=True)
    clusters: list[list[dict]] = []
    cluster_topics: list[set[str]] = []  # track merged topics per cluster

    for sig in sorted_sigs:
        sig_topics = [t.lower() for t in sig.get("topics", [])]
        best_cluster = -1
        best_overlap = 0.0

        for idx, ct in enumerate(cluster_topics):
            if not ct or not sig_topics:
                continue
            overlap = _jaccard(sig_topics, list(ct))
            if overlap > 0.3 and overlap > best_overlap:
                best_overlap = overlap
                best_cluster = idx

        if best_cluster >= 0:
            clusters[best_cluster].append(sig)
            cluster_topics[best_cluster].update(sig_topics)
        else:
            clusters.append([sig])
            cluster_topics.append(set(sig_topics))

    return clusters


def _merge_topics(cluster: list[dict]) -> list[str]:
    """Merge and deduplicate topics across all signals in a cluster."""
    seen: set[str] = set()
    merged: list[str] = []
    for sig in cluster:
        for t in sig.get("topics", []):
            key = t.lower()
            if key not in seen:
                seen.add(key)
                merged.append(t)
    return merged


def _build_rationale(cluster: list[dict]) -> str:
    """Build a human-readable rationale from the cluster's signals."""
    parts: list[str] = []
    for sig in cluster:
        detector = sig.get("detector", "unknown")
        desc = sig.get("description", "")
        if desc:
            # Capitalize detector name for readability
            detector_label = detector.replace("_", " ").title()
            parts.append(f"{detector_label}: {desc}")
    return " ".join(parts) if parts else "No rationale available."


def _deduplicate_opportunities(opportunities: list[dict]) -> list[dict]:
    """Merge opportunities with >0.5 topic overlap into the higher-scoring one."""
    if not opportunities:
        return []

    # Sort by composite_score desc so we keep the best one
    opps = sorted(opportunities, key=lambda o: o.get("composite_score", 0), reverse=True)
    merged: list[dict] = []
    merged_indices: set[int] = set()

    for i, opp_a in enumerate(opps):
        if i in merged_indices:
            continue
        for j in range(i + 1, len(opps)):
            if j in merged_indices:
                continue
            overlap = _jaccard(opp_a.get("topics", []), opps[j].get("topics", []))
            if overlap > 0.5:
                # Merge j into i (i has higher score)
                opp_a["signal_ids"].extend(opps[j].get("signal_ids", []))
                for d in opps[j].get("detectors_hit", []):
                    if d not in opp_a["detectors_hit"]:
                        opp_a["detectors_hit"].append(d)
                # Merge topics
                existing = set(t.lower() for t in opp_a.get("topics", []))
                for t in opps[j].get("topics", []):
                    if t.lower() not in existing:
                        opp_a["topics"].append(t)
                        existing.add(t.lower())
                # Take max scores
                opp_a["portfolio_fit"] = max(
                    opp_a.get("portfolio_fit", 0),
                    opps[j].get("portfolio_fit", 0),
                )
                opp_a["timing_urgency"] = max(
                    opp_a.get("timing_urgency", 0),
                    opps[j].get("timing_urgency", 0),
                )
                merged_indices.add(j)
        merged.append(opp_a)

    return merged


def synthesize(signals: list[dict]) -> list[dict]:
    """Synthesize signals from all detectors into ranked research opportunities.

    Args:
        signals: list of signal dicts from all detectors. Each must have at least
                 'detector', 'confidence', 'topics', 'title', 'description'.

    Returns:
        list of opportunity dicts sorted by composite_score desc, max 10.
    """
    if not signals:
        return []

    # 1. Cluster signals by topic overlap
    clusters = _cluster_signals(signals)

    # 2. Build opportunities from clusters
    # Number of distinct detector types (for cross-detector scoring)
    total_detector_types = len(set(sig.get("detector", "") for sig in signals))
    # Use at least 3 as the denominator (current expected detectors)
    detector_denominator = max(total_detector_types, 3)

    opportunities: list[dict] = []

    for cluster_idx, cluster in enumerate(clusters):
        # The highest-confidence signal drives title and thesis
        lead = max(cluster, key=lambda s: s.get("confidence", 0))

        merged_topics = _merge_topics(cluster)
        detectors_hit = list(set(sig.get("detector", "") for sig in cluster))

        portfolio_fit = max(
            (sig.get("relevance", 0) for sig in cluster), default=0.0
        )
        timing_urgency = max(
            (sig.get("timing_score", 0) for sig in cluster), default=0.0
        )
        venue_receptivity = 0.0  # Phase 3 reviewer model fills this

        # 3. Composite score
        avg_confidence = mean(sig.get("confidence", 0) for sig in cluster)
        cross_detector = len(detectors_hit)

        composite = (
            avg_confidence * 0.25
            + (cross_detector / detector_denominator) * 0.20
            + timing_urgency * 0.20
            + portfolio_fit * 0.25
            + venue_receptivity * 0.10
        )
        # Scale to 0-100
        composite_score = round(composite * 100, 1)

        # Build signal_ids from their index in the original list
        signal_ids: list[int] = []
        for sig in cluster:
            try:
                idx = signals.index(sig)
                signal_ids.append(idx)
            except ValueError:
                pass

        opportunity: dict[str, Any] = {
            "title": lead.get("title", "Untitled opportunity"),
            "thesis": lead.get("description", ""),
            "composite_score": composite_score,
            "signal_ids": signal_ids,
            "detectors_hit": detectors_hit,
            "topics": merged_topics,
            "target_venue": None,  # Phase 3 reviewer model fills this
            "portfolio_fit": round(portfolio_fit, 3),
            "timing_urgency": round(timing_urgency, 3),
            "venue_receptivity": venue_receptivity,
            "rationale": _build_rationale(cluster),
            "status": "new",
        }
        opportunity["composite_score"] = composite_score

        opportunities.append(opportunity)

    # 5. Deduplicate opportunities with >0.5 topic overlap
    opportunities = _deduplicate_opportunities(opportunities)

    # 6. Sort by composite_score desc, return top 10
    opportunities.sort(key=lambda o: o.get("composite_score", 0), reverse=True)
    return opportunities[:10]
