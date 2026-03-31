from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ResearchSignal:
    detector: str  # gap|trend|contrarian|frontier|reviewer|portfolio
    signal_type: str
    title: str
    description: str = ""
    confidence: float = 0.5
    source_papers: list[str] = field(default_factory=list)
    source_claims: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    relevance: float = 0.0
    timing_score: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "detector": self.detector,
            "signal_type": self.signal_type,
            "title": self.title,
            "description": self.description,
            "confidence": self.confidence,
            "source_papers": self.source_papers,
            "source_claims": self.source_claims,
            "topics": self.topics,
            "relevance": self.relevance,
            "timing_score": self.timing_score,
            "metadata": self.metadata,
        }
