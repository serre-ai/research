"""
Base failure detector interface.

All failure detectors must inherit from BaseDetector and implement
the detect() method to identify specific failure modes from agent traces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from ..frameworks import AgentStep, Task


@dataclass
class FailureReport:
    """Report of detected failure."""
    failure_detected: bool
    failure_type: str
    confidence: float  # 0.0 to 1.0
    evidence: List[AgentStep]
    details: Dict[str, Any]
    description: str = ""


class BaseDetector(ABC):
    """
    Abstract base class for failure detectors.

    Subclasses must implement:
    - detect(): Analyze trace and identify failure mode
    """

    def __init__(self, **kwargs):
        """
        Initialize detector.

        Args:
            **kwargs: Detector-specific configuration
        """
        self.config = kwargs

    @abstractmethod
    def detect(
        self,
        trace: List[AgentStep],
        task: Task,
        agent_output: Any
    ) -> FailureReport:
        """
        Detect failure mode from agent trace.

        Args:
            trace: Complete agent execution trace
            task: The task that was executed
            agent_output: The agent's final output

        Returns:
            FailureReport with detection results
        """
        pass

    def _find_steps_by_type(
        self,
        trace: List[AgentStep],
        step_type: str
    ) -> List[AgentStep]:
        """Helper to filter steps by type."""
        from ..frameworks import StepType
        target_type = StepType(step_type)
        return [s for s in trace if s.step_type == target_type]

    def _extract_tool_calls(self, trace: List[AgentStep]) -> List[Dict[str, Any]]:
        """
        Extract all tool calls from trace.

        Returns:
            List of dicts with 'tool_name' and 'arguments' keys
        """
        from ..frameworks import StepType

        tool_calls = []
        for step in trace:
            if step.step_type == StepType.ACTION:
                # Try to extract tool call from step content
                # This is framework-specific, but we'll try common patterns
                if "tool_name" in step.metadata:
                    tool_calls.append({
                        "tool_name": step.metadata["tool_name"],
                        "arguments": step.metadata.get("arguments", {}),
                        "step_num": step.step_num
                    })
        return tool_calls
