"""
Base classes for task generators.

Task generators create test instances with deterministic ground truth.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import random
from dataclasses import dataclass

from frameworks.base import TaskSpec


class TaskGenerator(ABC):
    """
    Abstract base class for task generators.

    Each generator creates instances of a specific task type with
    deterministic ground truth and configurable difficulty.
    """

    def __init__(self, seed: int = 42):
        """
        Initialize task generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.rng = random.Random(seed)

    @abstractmethod
    def generate(
        self,
        task_id: str,
        difficulty: int = 1,
        **kwargs
    ) -> TaskSpec:
        """
        Generate a single task instance.

        Args:
            task_id: Unique identifier for this instance
            difficulty: Difficulty level (1-5 typically)
            **kwargs: Task-specific parameters

        Returns:
            TaskSpec with prompt, tools, ground truth
        """
        pass

    @abstractmethod
    def get_task_type(self) -> str:
        """Return the task type identifier (e.g., 'tool_fabrication')."""
        pass

    def generate_batch(
        self,
        num_instances: int,
        difficulty: int = 1,
        id_prefix: str = "",
        **kwargs
    ) -> List[TaskSpec]:
        """
        Generate multiple task instances.

        Args:
            num_instances: Number of instances to generate
            difficulty: Difficulty level
            id_prefix: Prefix for task IDs
            **kwargs: Task-specific parameters

        Returns:
            List of TaskSpec instances
        """
        tasks = []
        for i in range(num_instances):
            task_id = f"{id_prefix}{self.get_task_type()}_d{difficulty}_i{i}"
            task = self.generate(task_id=task_id, difficulty=difficulty, **kwargs)
            tasks.append(task)
        return tasks

    def _create_task_spec(
        self,
        task_id: str,
        prompt: str,
        ground_truth: Any,
        tools: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskSpec:
        """Helper to create TaskSpec with consistent structure."""
        return TaskSpec(
            task_id=task_id,
            task_type=self.get_task_type(),
            prompt=prompt,
            tools=tools,
            ground_truth=ground_truth,
            metadata=metadata or {}
        )
