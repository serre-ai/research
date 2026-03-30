"""Base agent wrapper interface for agent failure experiments."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Action:
    """A single action taken by the agent.

    Attributes:
        type: Action type (e.g., "tool_call", "finish", "message")
        name: Action name (e.g., tool name or action identifier)
        parameters: Action parameters (e.g., tool arguments)
        thought: Agent's reasoning before action (if available)
        timestamp: When action was taken
    """

    type: str
    name: str
    parameters: Dict[str, Any]
    thought: Optional[str] = None
    timestamp: Optional[float] = None


@dataclass
class Observation:
    """Observation received after an action.

    Attributes:
        content: Observation content (e.g., tool output)
        success: Whether action succeeded
        error: Error message if action failed
        timestamp: When observation was received
    """

    content: Any
    success: bool = True
    error: Optional[str] = None
    timestamp: Optional[float] = None


@dataclass
class AgentTrace:
    """Complete trace of agent execution on a task.

    Attributes:
        instance_id: Task instance ID
        framework: Framework name (e.g., "react", "plan_execute")
        model: Model identifier (e.g., "gpt-4o-mini")
        actions: List of (Action, Observation) pairs
        final_answer: Agent's final answer or completion claim
        iterations: Number of reasoning iterations
        cost_usd: Total API cost in USD
        metadata: Framework-specific metadata
        completed: Whether agent claimed task completion
        timed_out: Whether agent hit iteration limit
    """

    instance_id: int
    framework: str
    model: str
    actions: List[Tuple[Action, Observation]] = field(default_factory=list)
    final_answer: Optional[str] = None
    iterations: int = 0
    cost_usd: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False
    timed_out: bool = False


class AgentWrapper(ABC):
    """Base class for agent framework wrappers.

    Wrappers provide a unified interface for different agent frameworks
    (ReAct, plan-execute, autonomous loops, etc.) to enable controlled
    comparison experiments.

    Each wrapper must:
    - Implement the agent pattern faithfully
    - Log all actions and observations
    - Track API costs
    - Support iteration limits
    - Be deterministic (same task + seed → same behavior)
    """

    def __init__(self, model: str, temperature: float = 0.0, **kwargs):
        """Initialize agent wrapper.

        Args:
            model: Model identifier (e.g., "gpt-4o-mini", "claude-3-5-sonnet-20241022")
            temperature: Sampling temperature (0.0 for deterministic)
            **kwargs: Framework-specific configuration
        """
        self.model = model
        self.temperature = temperature
        self.config = kwargs

    @abstractmethod
    def run(
        self,
        task: "Task",  # type: ignore
        max_iterations: int = 20,
        seed: Optional[int] = None,
    ) -> AgentTrace:
        """Execute agent on a task.

        Args:
            task: Task object to execute
            max_iterations: Maximum reasoning iterations before timeout
            seed: Random seed for reproducibility

        Returns:
            AgentTrace with complete execution history

        Raises:
            ValueError: If task is malformed
            RuntimeError: If agent execution fails critically
        """
        pass

    @abstractmethod
    def get_framework_name(self) -> str:
        """Return the framework identifier.

        Returns:
            String like "react", "plan_execute", "autonomous_loop"
        """
        pass

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost for a model call.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Pricing as of 2026-03-30
        pricing = {
            "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
            "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
            "claude-3-5-sonnet-20241022": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
            "claude-3-opus-20240229": {"input": 15.00 / 1_000_000, "output": 75.00 / 1_000_000},
        }

        if self.model not in pricing:
            # Default to GPT-4o pricing for unknown models
            rates = pricing["gpt-4o"]
        else:
            rates = pricing[self.model]

        cost = (input_tokens * rates["input"]) + (output_tokens * rates["output"])
        return cost
