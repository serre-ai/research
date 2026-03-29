"""
Abstract base class for agent framework wrappers.

All framework implementations (LangGraph, AutoGPT, etc.) inherit from this
to ensure consistent interface for experiments.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time
import uuid


@dataclass
class AgentTrace:
    """Single step in agent execution trace."""
    step: int
    thought: Optional[str]
    action: str
    action_input: Any
    observation: str
    timestamp: float


@dataclass
class AgentResult:
    """Complete result of agent execution."""
    run_id: str
    success: bool
    final_answer: Optional[str]
    trace: List[AgentTrace]
    error: Optional[str]

    # Metrics
    steps: int
    tokens_input: int
    tokens_output: int
    cost_usd: float
    duration_seconds: float

    # Failure detection flags
    tool_fabrication_detected: bool = False
    fabricated_tools: List[str] = None
    infinite_loop_detected: bool = False
    loop_start_step: Optional[int] = None
    false_completion_detected: bool = False

    def __post_init__(self):
        if self.fabricated_tools is None:
            self.fabricated_tools = []


class AgentFramework(ABC):
    """
    Abstract base class for agent framework wrappers.

    Each framework implementation must:
    1. Initialize with model and temperature
    2. Implement run() method that executes task and returns AgentResult
    3. Implement failure detection for relevant failure types
    4. Track tokens and costs
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
        max_iterations: Optional[int] = None,
        timeout_seconds: Optional[int] = None
    ):
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations or 50  # default safety limit
        self.timeout_seconds = timeout_seconds or 300  # 5 min default

    @abstractmethod
    def run(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute agent on given task.

        Args:
            task: Task specification dict with:
                - instruction: str (what the agent should do)
                - tools: List[Dict] (available tools)
                - initial_state: Dict (starting state)
                - success_criteria: str (how to know when done)

        Returns:
            AgentResult with full trace and failure detection flags
        """
        pass

    @abstractmethod
    def _detect_tool_fabrication(
        self,
        trace: List[AgentTrace],
        available_tools: List[str]
    ) -> tuple[bool, List[str]]:
        """
        Detect if agent fabricated (hallucinated) any tools.

        Args:
            trace: Full agent execution trace
            available_tools: List of actual available tool names

        Returns:
            (fabrication_detected: bool, fabricated_tool_names: List[str])
        """
        pass

    @abstractmethod
    def _detect_infinite_loop(
        self,
        trace: List[AgentTrace]
    ) -> tuple[bool, Optional[int]]:
        """
        Detect if agent is in an infinite loop.

        Loop detection criteria:
        - Same action repeated >3 times with no state change
        - No progress toward goal for >5 steps

        Args:
            trace: Full agent execution trace

        Returns:
            (loop_detected: bool, loop_start_step: Optional[int])
        """
        pass

    def _generate_run_id(self) -> str:
        """Generate unique run ID."""
        return str(uuid.uuid4())

    def _calculate_cost(
        self,
        tokens_input: int,
        tokens_output: int
    ) -> float:
        """
        Calculate API cost in USD.

        Cost estimates (per 1M tokens):
        - GPT-4o: $2.50 input, $10.00 output
        - Claude Sonnet 3.5: $3.00 input, $15.00 output
        """
        # Pricing table (USD per 1M tokens)
        pricing = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        }

        if self.model not in pricing:
            # Default to GPT-4o pricing as conservative estimate
            rates = pricing["gpt-4o"]
        else:
            rates = pricing[self.model]

        cost_input = (tokens_input / 1_000_000) * rates["input"]
        cost_output = (tokens_output / 1_000_000) * rates["output"]

        return cost_input + cost_output

    def _extract_tool_calls(self, trace: List[AgentTrace]) -> List[str]:
        """
        Extract all tool names called in the trace.

        Args:
            trace: Agent execution trace

        Returns:
            List of tool names (with duplicates)
        """
        tool_calls = []
        for step in trace:
            # Action is typically "tool_name" or "tool_name(args)"
            action = step.action.split("(")[0].strip()
            if action and action != "Final Answer":
                tool_calls.append(action)
        return tool_calls
