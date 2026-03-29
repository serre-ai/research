"""
Base type definitions for agent failure taxonomy experiments.

These types provide a common interface across all agent frameworks,
tasks, and evaluation pipelines.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FailureCategory(Enum):
    """Taxonomy failure categories"""
    TOOL_SELECTION = "1.1"
    TOOL_EXECUTION = "1.2"
    TOOL_INTEGRATION = "1.3"
    CODE_GENERATION = "1.4"
    INPUT_GROUNDING = "2.1"
    OBSERVATION_GROUNDING = "2.2"
    API_GROUNDING = "2.3"
    PROGRESS_MONITORING = "3.1"
    INSTRUCTION_PROCESSING = "3.2"
    REASONING_QUALITY = "3.3"
    STATE_DIVERGENCE = "4.1"
    MEMORY_ISSUES = "4.2"
    CONTEXT_MANAGEMENT = "4.3"
    VERIFICATION_FAILURES = "5.1"
    REFLECTION_FAILURES = "5.2"
    ERROR_ROUTING = "5.3"
    ERROR_DETECTION = "6.1"
    ERROR_HANDLING = "6.2"
    TEMPORAL_PROPAGATION = "7.1"
    SPATIAL_PROPAGATION = "7.2"
    CAUSAL_CHAINS = "7.3"


class ScenarioType(Enum):
    """Experimental scenario types"""
    TOOL_FABRICATION = "tool_fabrication"
    AMBIGUOUS_TASK_LOOP = "ambiguous_task_loop"
    REFLECTION_ERROR_PERSISTENCE = "reflection_error_persistence"


@dataclass
class Tool:
    """Tool definition for agent use"""
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None
    is_real: bool = True  # False for decoy tools


@dataclass
class Task:
    """Task specification for agent execution"""
    instance_id: str
    scenario: ScenarioType
    instruction: str
    available_tools: List[Tool]
    ground_truth: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Configuration for agent execution"""
    framework: str  # "react", "autogpt", "reflexion", "plan_execute"
    model: str  # "gpt-4o-2024-08-06", etc.
    temperature: float = 0.7
    max_iterations: int = 20
    timeout_seconds: int = 300
    enable_reflection: bool = False
    max_reflections: int = 3
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    """Record of a single tool call"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    timestamp: datetime
    is_fabricated: bool = False


@dataclass
class AgentTrace:
    """Complete execution trace from an agent"""
    instance_id: str
    framework: str
    model: str
    scenario: ScenarioType

    # Execution metadata
    start_time: datetime
    end_time: datetime
    iteration_count: int
    timeout: bool
    error: Optional[str]

    # Agent actions
    tool_calls: List[ToolCall]
    reflections: List[str] = field(default_factory=list)
    final_answer: Any = None

    # Resource usage
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    cost_usd: float = 0.0

    # Raw trace
    full_log: str = ""


@dataclass
class FailureSignals:
    """Detected failure signals from agent execution"""
    instance_id: str

    # Tool fabrication signals (Scenario 1)
    tool_fabricated: bool = False
    fabricated_tool_name: Optional[str] = None
    selected_tool: Optional[str] = None
    correct_tool: Optional[str] = None

    # Infinite loop signals (Scenario 2)
    infinite_loop_detected: bool = False
    stagnation_detected: bool = False
    clarification_requested: bool = False
    impossibility_declared: bool = False

    # Reflection error signals (Scenario 3)
    error_persisted: bool = False
    error_reinforced: bool = False
    initial_answer: Any = None
    final_answer: Any = None
    reflection_count: int = 0

    # Cross-cutting
    correctness: bool = False
    failure_categories: List[FailureCategory] = field(default_factory=list)


@dataclass
class ExperimentResult:
    """Complete result for a single instance"""
    instance_id: str
    task: Task
    config: AgentConfig
    trace: AgentTrace
    failure_signals: FailureSignals
    timestamp: datetime


class AgentFramework(ABC):
    """Abstract base class for all agent framework wrappers"""

    @abstractmethod
    def execute(self, task: Task, config: AgentConfig) -> AgentTrace:
        """
        Execute a task with the agent and return complete trace.

        Args:
            task: Task specification
            config: Agent configuration

        Returns:
            AgentTrace with complete execution history

        Raises:
            TimeoutError: If execution exceeds config.timeout_seconds
            RuntimeError: If agent encounters unrecoverable error
        """
        pass

    @abstractmethod
    def validate_config(self, config: AgentConfig) -> bool:
        """
        Validate that this framework supports the given config.

        Args:
            config: Agent configuration to validate

        Returns:
            True if config is valid for this framework
        """
        pass


class FailureExtractor(ABC):
    """Abstract base class for failure signal extraction"""

    @abstractmethod
    def extract(self, trace: AgentTrace, task: Task) -> FailureSignals:
        """
        Extract failure signals from agent trace.

        Args:
            trace: Complete agent execution trace
            task: Original task specification (for ground truth)

        Returns:
            FailureSignals with detected failures
        """
        pass


@dataclass
class ExperimentSpec:
    """Specification loaded from spec.yaml"""
    name: str
    status: str
    hypothesis: str
    predictions: List[Dict[str, Any]]
    design: Dict[str, Any]
    canary: Dict[str, Any]
    budget: Dict[str, float]

    @classmethod
    def from_yaml(cls, path: str) -> 'ExperimentSpec':
        """Load spec from YAML file"""
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


@dataclass
class Checkpoint:
    """Checkpoint for crash recovery"""
    experiment_name: str
    timestamp: datetime
    completed_instances: List[str]
    total_cost_usd: float
    partial_results: List[ExperimentResult]

    def save(self, path: str) -> None:
        """Save checkpoint to JSON file"""
        import json
        from datetime import datetime

        data = {
            "experiment_name": self.experiment_name,
            "timestamp": self.timestamp.isoformat(),
            "completed_instances": self.completed_instances,
            "total_cost_usd": self.total_cost_usd,
            "partial_results": [
                {
                    "instance_id": r.instance_id,
                    "framework": r.config.framework,
                    "model": r.config.model,
                    "cost_usd": r.trace.cost_usd,
                }
                for r in self.partial_results
            ]
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'Checkpoint':
        """Load checkpoint from JSON file"""
        import json
        from datetime import datetime

        with open(path) as f:
            data = json.load(f)

        return cls(
            experiment_name=data["experiment_name"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            completed_instances=data["completed_instances"],
            total_cost_usd=data["total_cost_usd"],
            partial_results=[],  # Don't reload full results, just skip completed
        )
