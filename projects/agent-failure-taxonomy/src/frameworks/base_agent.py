"""
Base agent interface for unified framework wrappers.

All agent implementations must inherit from BaseAgent and implement
the required methods. This enables framework-agnostic evaluation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class StepType(Enum):
    """Types of agent steps."""
    REASONING = "reasoning"
    ACTION = "action"
    OBSERVATION = "observation"
    REFLECTION = "reflection"
    COMPLETION = "completion"
    ERROR = "error"


@dataclass
class AgentStep:
    """Single step in an agent trace."""
    step_num: int
    step_type: StepType
    content: str
    metadata: Dict[str, Any]
    timestamp: float
    cost_usd: float = 0.0


@dataclass
class AgentRun:
    """Complete agent run with trace and outcome."""
    run_id: str
    task_id: str
    framework: str
    llm: str
    trace: List[AgentStep]
    final_output: Any
    success: bool
    total_cost_usd: float
    total_time_seconds: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class Tool:
    """Tool definition for agent."""
    name: str
    description: str
    parameters: Dict[str, Any]
    implementation: Optional[callable] = None
    is_placeholder: bool = False  # For tool hallucination tasks


@dataclass
class Task:
    """Task definition with ground truth."""
    task_id: str
    description: str
    query: str
    tools: List[Tool]
    ground_truth: Dict[str, Any]
    success_criteria: Dict[str, Any]
    metadata: Dict[str, Any]


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations.

    Subclasses must implement:
    - run_task(): Execute a task and return complete trace
    - get_trace(): Get current execution trace
    - reset(): Reset agent state
    """

    def __init__(
        self,
        llm: str,
        temperature: float = 0.0,
        max_iterations: int = 15,
        timeout_seconds: int = 300,
        **kwargs
    ):
        """
        Initialize agent.

        Args:
            llm: LLM identifier (e.g., "gpt-4-turbo", "claude-3-5-sonnet")
            temperature: Sampling temperature
            max_iterations: Maximum iterations before forced termination
            timeout_seconds: Timeout in seconds
            **kwargs: Framework-specific configuration
        """
        self.llm = llm
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.config = kwargs
        self._trace: List[AgentStep] = []
        self._total_cost = 0.0

    @abstractmethod
    def run_task(self, task: Task) -> AgentRun:
        """
        Execute a task and return the complete run with trace.

        Args:
            task: Task to execute

        Returns:
            AgentRun with complete trace and outcome

        Raises:
            TimeoutError: If task exceeds timeout
            RuntimeError: If framework encounters unrecoverable error
        """
        pass

    @abstractmethod
    def get_trace(self) -> List[AgentStep]:
        """
        Get the current execution trace.

        Returns:
            List of agent steps in execution order
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset agent state for next run.

        Clears trace, memory, and any other stateful components.
        """
        pass

    def _add_step(
        self,
        step_type: StepType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        cost_usd: float = 0.0
    ):
        """Helper to add step to trace."""
        import time

        step = AgentStep(
            step_num=len(self._trace) + 1,
            step_type=step_type,
            content=content,
            metadata=metadata or {},
            timestamp=time.time(),
            cost_usd=cost_usd
        )
        self._trace.append(step)
        self._total_cost += cost_usd

    def _check_iteration_limit(self) -> bool:
        """Check if iteration limit reached."""
        action_steps = [s for s in self._trace if s.step_type == StepType.ACTION]
        return len(action_steps) >= self.max_iterations

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for an LLM call.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Cost per 1K tokens (approximate as of 2026-03-29)
        costs = {
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
        }

        # Find matching cost entry
        cost_entry = None
        for key in costs:
            if key in self.llm.lower():
                cost_entry = costs[key]
                break

        if not cost_entry:
            # Default to GPT-4 pricing
            cost_entry = costs["gpt-4"]

        input_cost = (input_tokens / 1000) * cost_entry["input"]
        output_cost = (output_tokens / 1000) * cost_entry["output"]

        return input_cost + output_cost
