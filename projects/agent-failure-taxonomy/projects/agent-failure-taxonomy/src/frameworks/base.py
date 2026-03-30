"""
Base interface for agent framework wrappers.

All framework implementations must conform to this interface to ensure
consistent evaluation across architectures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class AgentArchitecture(Enum):
    """Agent architecture types from taxonomy."""
    REACT = "ReAct"
    AUTONOMOUS_LOOP = "Autonomous loop"
    PLAN_THEN_EXECUTE = "Plan-then-execute"
    REFLEXION = "Reflexion"
    TREE_OF_THOUGHT = "Tree-of-Thought"


@dataclass
class ToolCall:
    """Structured representation of a tool call."""
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    hallucinated: bool = False  # True if tool was called but doesn't actually exist


@dataclass
class AgentStep:
    """Single step in agent execution."""
    step_number: int
    observation: str
    thought: str
    action: str
    action_input: Dict[str, Any]
    tool_calls: List[ToolCall]
    tokens_used: int
    cost_usd: float


@dataclass
class AgentTrace:
    """Complete execution trace for a single trial."""
    task: str
    steps: List[AgentStep]
    final_output: str
    completed: bool
    failure_detected: Optional[str] = None  # Type of failure if detected
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    timeout: bool = False
    error: Optional[str] = None


class AgentFramework(ABC):
    """
    Abstract base class for agent framework wrappers.

    Each implementation represents one agent architecture (ReAct, AutoGPT, etc.)
    and provides a uniform interface for running trials and collecting traces.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_iterations: int = 20,
        timeout_seconds: int = 120,
        seed: Optional[int] = None
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.seed = seed
        self._current_cost = 0.0

    @property
    @abstractmethod
    def architecture(self) -> AgentArchitecture:
        """Return the architecture type this framework implements."""
        pass

    @abstractmethod
    def run_task(
        self,
        task: str,
        tools: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentTrace:
        """
        Execute a task with the agent framework.

        Args:
            task: Natural language task description
            tools: List of available tools (framework-specific format)
            context: Optional context/memory for the agent

        Returns:
            AgentTrace containing complete execution history
        """
        pass

    @abstractmethod
    def detect_failure(self, trace: AgentTrace) -> Optional[str]:
        """
        Analyze trace to detect if expected failure occurred.

        Args:
            trace: Complete execution trace

        Returns:
            Failure type if detected (e.g., "tool_fabrication", "infinite_loop"),
            None if no failure detected
        """
        pass

    def reset(self):
        """Reset framework state between trials."""
        self._current_cost = 0.0

    def get_total_cost(self) -> float:
        """Get cumulative cost for all trials run with this framework."""
        return self._current_cost

    def _estimate_cost(self, tokens: int) -> float:
        """
        Estimate cost for a given token count.

        Model-specific pricing. Update as needed.
        """
        # Rough estimates (input + output averaged)
        pricing = {
            "claude-haiku-4-5-20251001": 0.000001,  # ~$1/MTok
            "gpt-4o-mini": 0.000001,  # Similar pricing
        }

        return tokens * pricing.get(self.model_name, 0.000002)
