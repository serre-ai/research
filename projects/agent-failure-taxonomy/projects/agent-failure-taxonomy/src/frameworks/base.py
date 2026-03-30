"""Base agent interface for controlled experiments."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class AgentStep:
    """Single step in agent execution trace."""
    step: int
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AgentOutcome:
    """Outcome of agent execution."""
    completed: bool
    iterations_used: int
    total_tokens: int
    total_cost: float
    wall_time_seconds: float
    final_answer: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AgentExecution:
    """Complete agent execution record."""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework: str = ""
    scenario: str = ""
    instance_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model: str = ""
    temperature: float = 0.0
    max_iterations: int = 20

    trace: List[AgentStep] = field(default_factory=list)
    outcome: Optional[AgentOutcome] = None
    failure_analysis: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "execution_id": self.execution_id,
            "framework": self.framework,
            "scenario": self.scenario,
            "instance_id": self.instance_id,
            "timestamp": self.timestamp,
            "model": self.model,
            "temperature": self.temperature,
            "max_iterations": self.max_iterations,
            "trace": [
                {
                    "step": step.step,
                    "thought": step.thought,
                    "action": step.action,
                    "action_input": step.action_input,
                    "observation": step.observation,
                    "tokens_in": step.tokens_in,
                    "tokens_out": step.tokens_out,
                    "cost": step.cost,
                    "timestamp": step.timestamp,
                }
                for step in self.trace
            ],
            "outcome": {
                "completed": self.outcome.completed,
                "iterations_used": self.outcome.iterations_used,
                "total_tokens": self.outcome.total_tokens,
                "total_cost": self.outcome.total_cost,
                "wall_time_seconds": self.outcome.wall_time_seconds,
                "final_answer": self.outcome.final_answer,
                "error": self.outcome.error,
            } if self.outcome else None,
            "failure_analysis": self.failure_analysis,
        }


class BaseAgent(ABC):
    """Base class for all agent implementations."""

    def __init__(
        self,
        model: str = "gpt-4-0125-preview",
        temperature: float = 0.0,
        max_iterations: int = 20,
        tools: Optional[List[Any]] = None,
    ):
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.tools = tools or []

    @abstractmethod
    def run(self, task: str, **kwargs) -> AgentExecution:
        """
        Execute agent on given task.

        Args:
            task: Task description/instruction
            **kwargs: Additional task-specific parameters

        Returns:
            AgentExecution record with full trace and outcome
        """
        pass

    @abstractmethod
    def get_framework_name(self) -> str:
        """Return framework identifier (e.g., 'react', 'plan_execute')."""
        pass
