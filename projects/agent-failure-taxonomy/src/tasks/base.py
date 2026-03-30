"""Base task generator interface for agent failure experiments."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class Task:
    """A task instance for agent evaluation.

    Attributes:
        instance_id: Unique identifier for this task instance
        description: Natural language description of the task
        ground_truth: Expected correct behavior or outcome
        verification_fn: Function to check if agent behavior matches expectations
        metadata: Additional context (tools available, constraints, etc.)
        failure_type: Which failure mode this task is designed to elicit
    """

    instance_id: int
    description: str
    ground_truth: Dict[str, Any]
    verification_fn: Callable
    metadata: Dict[str, Any]
    failure_type: str


class TaskGenerator(ABC):
    """Base class for generating tasks that test specific failure modes.

    Each TaskGenerator creates instances of a specific task type designed
    to elicit a particular failure mode (e.g., tool fabrication, infinite loops).

    Implementations must be deterministic: same instance_id and seed must
    produce identical tasks for reproducibility.
    """

    def __init__(self, **config):
        """Initialize task generator with configuration.

        Args:
            **config: Generator-specific configuration parameters
        """
        self.config = config

    @abstractmethod
    def generate(self, instance_id: int, seed: int) -> Task:
        """Generate a task instance.

        Args:
            instance_id: Unique identifier for this instance (0-indexed)
            seed: Random seed for deterministic generation

        Returns:
            Task object with all required fields populated

        Raises:
            ValueError: If instance_id or seed are invalid
        """
        pass

    @abstractmethod
    def get_failure_type(self) -> str:
        """Return the failure type this generator targets.

        Returns:
            String identifier like "tool_fabrication" or "infinite_loop"
        """
        pass

    def generate_batch(self, num_instances: int, seed_base: int = 0) -> list[Task]:
        """Generate multiple task instances.

        Args:
            num_instances: Number of instances to generate
            seed_base: Base seed (each instance gets seed_base + instance_id)

        Returns:
            List of Task objects
        """
        return [
            self.generate(instance_id=i, seed=seed_base + i)
            for i in range(num_instances)
        ]
