"""
Base agent interface for experimental framework.

This module defines the abstract interface that all agent framework wrappers
must implement, ensuring consistent execution, logging, and evaluation across
different agent architectures (ReAct, AutoGPT, Reflexion, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


@dataclass
class AgentStep:
    """Single step in agent execution trace."""

    step_number: int
    timestamp: str
    reasoning: str  # Agent's internal reasoning/thought
    action: str  # Action to execute (e.g., "search", "create_file")
    action_input: Dict[str, Any]  # Parameters for the action
    observation: str  # Result of action execution
    is_final: bool = False  # Whether this is the final step
    error: Optional[str] = None  # Error message if action failed
    metadata: Dict[str, Any] = field(default_factory=dict)  # Framework-specific data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "step_number": self.step_number,
            "timestamp": self.timestamp,
            "reasoning": self.reasoning,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "is_final": self.is_final,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class AgentResult:
    """Complete agent execution result."""

    task_id: str
    framework: str  # "react", "autogpt", etc.
    model: str  # LLM model used
    success: bool  # Whether agent claimed task completion
    steps: List[AgentStep]
    start_time: str
    end_time: str
    total_tokens: int = 0
    total_cost: float = 0.0
    completion_claimed: bool = False  # Did agent explicitly claim completion?
    error: Optional[str] = None  # Fatal error that stopped execution
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "framework": self.framework,
            "model": self.model,
            "success": self.success,
            "steps": [step.to_dict() for step in self.steps],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "completion_claimed": self.completion_claimed,
            "error": self.error,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @property
    def num_steps(self) -> int:
        """Number of steps executed."""
        return len(self.steps)

    @property
    def duration_seconds(self) -> float:
        """Execution duration in seconds."""
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        return (end - start).total_seconds()


class BaseAgent(ABC):
    """
    Abstract base class for agent framework wrappers.

    All framework implementations (ReAct, AutoGPT, etc.) must inherit from
    this class and implement the abstract methods.
    """

    def __init__(
        self,
        model: str,
        temperature: float = 1.0,
        max_steps: int = 50,
        verbose: bool = False,
    ):
        """
        Initialize agent.

        Args:
            model: LLM model identifier (e.g., "claude-haiku-4-5-20251001")
            temperature: Sampling temperature for LLM calls
            max_steps: Maximum number of steps before forced termination
            verbose: Whether to print execution progress
        """
        self.model = model
        self.temperature = temperature
        self.max_steps = max_steps
        self.verbose = verbose

    @abstractmethod
    def run(
        self,
        task_description: str,
        tools: List[Dict[str, Any]],
        task_id: str,
    ) -> AgentResult:
        """
        Execute agent on a task.

        Args:
            task_description: Natural language description of the task
            tools: List of available tools (each tool is a dict with name, description, parameters)
            task_id: Unique identifier for this task instance

        Returns:
            AgentResult containing execution trace and metadata
        """
        pass

    @abstractmethod
    def get_framework_name(self) -> str:
        """Return framework name (e.g., 'react', 'autogpt')."""
        pass

    def _log_step(self, step: AgentStep) -> None:
        """Log a step if verbose mode is enabled."""
        if self.verbose:
            print(f"\n[Step {step.step_number}]")
            print(f"Reasoning: {step.reasoning[:100]}...")
            print(f"Action: {step.action}")
            print(f"Observation: {step.observation[:100]}...")

    def _create_result(
        self,
        task_id: str,
        steps: List[AgentStep],
        start_time: str,
        end_time: str,
        success: bool = False,
        completion_claimed: bool = False,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Helper to create AgentResult with computed fields."""
        total_tokens = sum(step.metadata.get("tokens", 0) for step in steps)
        total_cost = sum(step.metadata.get("cost", 0.0) for step in steps)

        return AgentResult(
            task_id=task_id,
            framework=self.get_framework_name(),
            model=self.model,
            success=success,
            steps=steps,
            start_time=start_time,
            end_time=end_time,
            total_tokens=total_tokens,
            total_cost=total_cost,
            completion_claimed=completion_claimed,
            error=error,
            metadata=metadata or {},
        )


class Tool:
    """
    Tool definition for agent execution.

    Tools provide the interface between agents and external functionality
    (file operations, web search, calculations, etc.).
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: callable,
    ):
        """
        Initialize tool.

        Args:
            name: Tool name (e.g., "search", "create_file")
            description: Natural language description of what the tool does
            parameters: JSON schema describing tool parameters
            function: Callable that executes the tool action
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function

    def execute(self, **kwargs) -> str:
        """
        Execute the tool with given parameters.

        Returns:
            String observation of the tool execution result
        """
        try:
            result = self.function(**kwargs)
            return str(result)
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM prompt."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
