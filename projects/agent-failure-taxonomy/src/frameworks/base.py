"""
Base classes for agent framework wrappers.

Provides uniform interface across different agent frameworks (LangGraph, custom Plan-Execute, Reflexion).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class ActionType(Enum):
    """Types of actions an agent can take."""
    TOOL_CALL = "tool_call"
    REASONING = "reasoning"
    PLANNING = "planning"
    COMPLETION = "completion"
    ERROR = "error"


@dataclass
class Action:
    """
    Represents a single action taken by an agent.

    Attributes:
        type: Type of action
        content: Action content (e.g., tool name, reasoning text)
        parameters: Parameters for the action (e.g., tool arguments)
        timestamp: When the action occurred
        metadata: Additional action metadata
    """
    type: ActionType
    content: str
    parameters: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentResult:
    """
    Result of running an agent on a task.

    Attributes:
        success: Whether agent reported task completion
        output: Agent's final output
        trace: Sequence of actions taken
        cost: Total API cost in USD
        token_counts: Dict of token counts (prompt, completion, total)
        metadata: Additional result metadata (e.g., iterations, errors)
    """
    success: bool
    output: str
    trace: List[Action]
    cost: float
    token_counts: Dict[str, int]
    metadata: Dict[str, Any]


@dataclass
class TaskSpec:
    """
    Specification for a task instance.

    Attributes:
        task_id: Unique identifier for this task instance
        task_type: Type of task (e.g., "tool_fabrication", "infinite_loop")
        prompt: Task prompt for the agent
        tools: List of available tools (for tool-use tasks)
        ground_truth: Expected correct outcome
        metadata: Additional task metadata (e.g., difficulty, condition)
    """
    task_id: str
    task_type: str
    prompt: str
    tools: Optional[List[Dict[str, Any]]] = None
    ground_truth: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentFrameworkWrapper(ABC):
    """
    Abstract base class for agent framework wrappers.

    All framework-specific implementations must inherit from this class
    and implement the required methods.
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.0,
        max_iterations: int = 20,
        **kwargs
    ):
        """
        Initialize the agent framework.

        Args:
            model: Model identifier (e.g., "claude-3-5-sonnet-20241022")
            temperature: Sampling temperature
            max_iterations: Maximum number of agent iterations before timeout
            **kwargs: Additional framework-specific parameters
        """
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.config = kwargs

    @abstractmethod
    def run_task(self, task_spec: TaskSpec) -> AgentResult:
        """
        Run the agent on a task instance.

        Args:
            task_spec: Task specification

        Returns:
            AgentResult with trace, cost, and outcome
        """
        pass

    @abstractmethod
    def get_framework_name(self) -> str:
        """Return the name of this framework (e.g., 'langraph', 'plan_execute')."""
        pass

    @abstractmethod
    def get_architecture_type(self) -> str:
        """
        Return the architecture pattern (e.g., 'react', 'plan_then_execute', 'reflection').
        """
        pass

    def reset(self):
        """Reset any stateful components (e.g., memory, conversation history)."""
        pass  # Default: no state to reset

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model}, temp={self.temperature})"


class FailureDetector(ABC):
    """
    Abstract base class for failure pattern detectors.

    Each detector implements logic to identify a specific failure pattern
    from an agent's execution trace.
    """

    @abstractmethod
    def detect(self, result: AgentResult, task_spec: TaskSpec) -> bool:
        """
        Detect whether the failure pattern occurred.

        Args:
            result: Agent execution result
            task_spec: Original task specification (for ground truth)

        Returns:
            True if failure detected, False otherwise
        """
        pass

    @abstractmethod
    def get_failure_type(self) -> str:
        """Return the failure type this detector identifies (e.g., 'tool_fabrication')."""
        pass

    def get_failure_details(self, result: AgentResult, task_spec: TaskSpec) -> Dict[str, Any]:
        """
        Extract detailed information about the failure (optional).

        Args:
            result: Agent execution result
            task_spec: Original task specification

        Returns:
            Dict with failure details (e.g., which tool was fabricated, loop iteration count)
        """
        return {}
