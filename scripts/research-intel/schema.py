"""Shared schema for research intelligence signals."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ResearchSignal:
    """A single research intelligence signal produced by a detector."""

    detector: str                       # e.g. "gap_detector"
    signal_type: str                    # e.g. "uncovered_connection", "contradicting_claims"
    title: str                          # short human-readable title
    description: str                    # longer explanation
    confidence: float                   # 0.0 – 1.0
    source_papers: list[dict]           # [{id, title}, ...]
    topics: list[str] = field(default_factory=list)
    relevance: float = 0.0             # 0.0 – 1.0, how relevant to active projects
    timing_score: float = 0.0          # 0.0 – 1.0, urgency / timeliness
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
