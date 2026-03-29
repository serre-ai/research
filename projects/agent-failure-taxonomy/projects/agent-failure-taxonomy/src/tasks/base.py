"""
Abstract base class for task generators.

Each failure type (tool fabrication, infinite loops, etc.) has a task generator
that creates instances designed to trigger that specific failure.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import random


@dataclass
class Task:
    """
    A single task instance for agent execution.

    This is the interface between task generators and agent frameworks.
    """
    task_id: str
    instance_id: int
    failure_type: str

    # Core task definition
    instruction: str
    tools: List[Dict[str, Any]]
    initial_state: Dict[str, Any]
    success_criteria: str

    # Ground truth for validation
    ground_truth_answer: Optional[str] = None
    expected_tool_sequence: Optional[List[str]] = None

    # Metadata
    difficulty: str = "medium"  # easy | medium | hard
    reproducibility: str = "high"  # easy | high | medium | hard

    # Experimental parameters
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "instance_id": self.instance_id,
            "failure_type": self.failure_type,
            "instruction": self.instruction,
            "tools": self.tools,
            "initial_state": self.initial_state,
            "success_criteria": self.success_criteria,
            "ground_truth_answer": self.ground_truth_answer,
            "expected_tool_sequence": self.expected_tool_sequence,
            "difficulty": self.difficulty,
            "reproducibility": self.reproducibility,
            "parameters": self.parameters,
        }


class TaskGenerator(ABC):
    """
    Abstract base class for task generators.

    Each failure type has a generator that creates task instances designed
    to trigger that specific failure mode.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize task generator.

        Args:
            seed: Random seed for reproducible task generation
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    @abstractmethod
    def generate(
        self,
        instance_id: int,
        difficulty: str = "medium",
        **kwargs
    ) -> Task:
        """
        Generate a single task instance.

        Args:
            instance_id: Unique identifier for this instance
            difficulty: Task difficulty level
            **kwargs: Generator-specific parameters

        Returns:
            Task instance
        """
        pass

    @abstractmethod
    def get_failure_type(self) -> str:
        """Return the failure type this generator targets."""
        pass

    @abstractmethod
    def get_taxonomy_category(self) -> str:
        """Return the taxonomy category (e.g., '1.1 Tool-Use: Selection')."""
        pass

    def generate_batch(
        self,
        num_instances: int,
        difficulty: str = "medium",
        **kwargs
    ) -> List[Task]:
        """
        Generate multiple task instances.

        Args:
            num_instances: Number of instances to generate
            difficulty: Task difficulty level
            **kwargs: Generator-specific parameters

        Returns:
            List of Task instances
        """
        return [
            self.generate(instance_id=i, difficulty=difficulty, **kwargs)
            for i in range(num_instances)
        ]

    def _create_tool_spec(
        self,
        name: str,
        description: str,
        parameters: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Create standardized tool specification.

        Args:
            name: Tool name
            description: What the tool does
            parameters: List of parameter specs, each with:
                - name: parameter name
                - type: parameter type
                - description: what it's for

        Returns:
            Tool specification dict
        """
        return {
            "name": name,
            "description": description,
            "parameters": parameters,
        }

    def _validate_tool_coverage(
        self,
        tools: List[Dict[str, Any]],
        required_tools: List[str]
    ) -> bool:
        """
        Verify that required tools are in the tool set.

        Args:
            tools: List of tool specs
            required_tools: List of required tool names

        Returns:
            True if all required tools present
        """
        tool_names = {tool["name"] for tool in tools}
        return all(name in tool_names for name in required_tools)
