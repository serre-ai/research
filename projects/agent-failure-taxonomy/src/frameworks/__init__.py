"""Agent framework wrappers.

Provides unified interface for running agents across different frameworks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AgentFramework(ABC):
    """Abstract base class for agent framework wrappers."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
        max_iterations: int = 10,
        timeout_seconds: int = 300,
    ):
        """Initialize framework wrapper.

        Args:
            model: Model identifier (e.g., "gpt-4o-mini-2024-07-18")
            temperature: Sampling temperature
            max_iterations: Maximum agent iterations before timeout
            timeout_seconds: Wall-clock timeout
        """
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    def run(
        self,
        task_description: str,
        tools: List[Dict[str, Any]],
        initial_observation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run agent on a task.

        Args:
            task_description: Natural language task description
            tools: List of available tools (each with name, description, parameters, function)
            initial_observation: Optional initial observation to start with

        Returns:
            Dictionary with:
                - trajectory: List of steps (observation, reasoning, action, result)
                - final_answer: Agent's final answer
                - completion_status: success | failure | timeout
                - iterations: Number of iterations taken
                - token_counts: {"input": int, "output": int}
                - cost_usd: Estimated cost
        """
        pass

    @abstractmethod
    def get_framework_name(self) -> str:
        """Get framework identifier.

        Returns:
            Framework name (e.g., "langgraph", "react_direct", "anthropic_mcp")
        """
        pass
