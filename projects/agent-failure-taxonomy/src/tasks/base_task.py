"""
Base task generator interface.

All task generators must inherit from BaseTaskGenerator and implement
the required methods for generating task instances with ground truth.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List
from ..frameworks import Task, Tool


@dataclass
class VerificationResult:
    """Result of verifying agent output against ground truth."""
    success: bool
    details: Dict[str, Any]
    error_message: str = ""


class BaseTaskGenerator(ABC):
    """
    Abstract base class for task generators.

    Subclasses must implement:
    - generate(): Create a task instance
    - verify(): Check agent output against ground truth
    """

    def __init__(self, seed: int = 42):
        """
        Initialize task generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self._rng = None

    @abstractmethod
    def generate(self, task_id: str, difficulty: int = 1) -> Task:
        """
        Generate a task instance.

        Args:
            task_id: Unique identifier for this task instance
            difficulty: Difficulty level (1-5, where 5 is hardest)

        Returns:
            Task with description, query, tools, and ground truth
        """
        pass

    @abstractmethod
    def verify(self, task: Task, agent_output: Any) -> VerificationResult:
        """
        Verify agent output against ground truth.

        Args:
            task: The task that was executed
            agent_output: The agent's final output

        Returns:
            VerificationResult indicating success/failure with details
        """
        pass

    def _get_rng(self):
        """Get or create random number generator."""
        if self._rng is None:
            import random
            self._rng = random.Random(self.seed)
        return self._rng
