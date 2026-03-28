"""
Framework Abstraction Layer for Agent Failure Testing

Provides a unified interface for running experiments across different
agent frameworks (LangGraph, AutoGPT, OpenAI Swarm) while capturing
detailed execution traces for failure detection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import json
import time


@dataclass
class ToolCall:
    """Represents a single tool invocation by an agent."""
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: float
    success: bool
    result: Any
    error: Optional[str] = None


@dataclass
class AgentAction:
    """Represents a single action taken by an agent."""
    step_number: int
    action_type: str  # tool_call, reflection, message, completion
    content: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """Complete execution trace for an agent run."""
    task_id: str
    framework: str
    model: str
    start_time: float
    end_time: Optional[float] = None
    actions: List[AgentAction] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    final_state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    token_usage: Dict[str, int] = field(default_factory=dict)
    cost_usd: float = 0.0


class AgentFramework(ABC):
    """Abstract base class for agent framework wrappers."""

    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.trace: Optional[ExecutionTrace] = None

    @abstractmethod
    def setup(self, tools: List[Callable], system_prompt: str) -> None:
        """Initialize the agent with tools and system prompt."""
        pass

    @abstractmethod
    def run(
        self,
        task: str,
        max_iterations: int = 20,
        timeout_seconds: int = 300
    ) -> ExecutionTrace:
        """
        Execute the agent on a task and return execution trace.

        Args:
            task: The task description/goal
            max_iterations: Maximum number of agent iterations
            timeout_seconds: Maximum execution time

        Returns:
            ExecutionTrace with complete execution history
        """
        pass

    def _start_trace(self, task_id: str) -> None:
        """Initialize a new execution trace."""
        self.trace = ExecutionTrace(
            task_id=task_id,
            framework=self.__class__.__name__,
            model=self.model,
            start_time=time.time()
        )

    def _record_action(
        self,
        action_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record an action in the current trace."""
        if not self.trace:
            raise RuntimeError("Trace not initialized. Call _start_trace first.")

        action = AgentAction(
            step_number=len(self.trace.actions),
            action_type=action_type,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.trace.actions.append(action)

    def _record_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        success: bool,
        result: Any,
        error: Optional[str] = None
    ) -> None:
        """Record a tool call in the current trace."""
        if not self.trace:
            raise RuntimeError("Trace not initialized. Call _start_trace first.")

        tool_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
            timestamp=time.time(),
            success=success,
            result=result,
            error=error
        )
        self.trace.tool_calls.append(tool_call)

    def _finalize_trace(
        self,
        final_state: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> ExecutionTrace:
        """Finalize and return the execution trace."""
        if not self.trace:
            raise RuntimeError("Trace not initialized. Call _start_trace first.")

        self.trace.end_time = time.time()
        self.trace.final_state = final_state
        self.trace.error = error

        return self.trace

    def save_trace(self, filepath: str) -> None:
        """Save execution trace to JSON file."""
        if not self.trace:
            raise RuntimeError("No trace to save.")

        with open(filepath, 'w') as f:
            json.dump(self._trace_to_dict(), f, indent=2)

    def _trace_to_dict(self) -> Dict[str, Any]:
        """Convert trace to JSON-serializable dict."""
        if not self.trace:
            return {}

        return {
            'task_id': self.trace.task_id,
            'framework': self.trace.framework,
            'model': self.trace.model,
            'start_time': self.trace.start_time,
            'end_time': self.trace.end_time,
            'duration_seconds': (
                self.trace.end_time - self.trace.start_time
                if self.trace.end_time else None
            ),
            'actions': [
                {
                    'step': a.step_number,
                    'type': a.action_type,
                    'content': a.content,
                    'timestamp': a.timestamp,
                    'metadata': a.metadata
                }
                for a in self.trace.actions
            ],
            'tool_calls': [
                {
                    'tool': tc.tool_name,
                    'arguments': tc.arguments,
                    'timestamp': tc.timestamp,
                    'success': tc.success,
                    'result': str(tc.result)[:1000],  # Truncate large results
                    'error': tc.error
                }
                for tc in self.trace.tool_calls
            ],
            'final_state': self.trace.final_state,
            'error': self.trace.error,
            'token_usage': self.trace.token_usage,
            'cost_usd': self.trace.cost_usd
        }


class LangGraphWrapper(AgentFramework):
    """Wrapper for LangGraph (ReAct) agent framework."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        super().__init__(model, temperature)
        self.graph = None
        self.tools_registry = {}

    def setup(self, tools: List[Callable], system_prompt: str) -> None:
        """Initialize LangGraph agent with tools."""
        try:
            from langgraph.prebuilt import create_react_agent
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "LangGraph not installed. Run: pip install langgraph langchain-openai"
            )

        # Create LLM
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)

        # Register tools
        self.tools_registry = {tool.__name__: tool for tool in tools}

        # Create ReAct agent
        self.graph = create_react_agent(
            llm,
            tools,
            state_modifier=system_prompt
        )

    def run(
        self,
        task: str,
        max_iterations: int = 20,
        timeout_seconds: int = 300
    ) -> ExecutionTrace:
        """Execute LangGraph agent and capture trace."""
        if not self.graph:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        task_id = f"langgraph_{int(time.time())}"
        self._start_trace(task_id)

        start_time = time.time()
        iterations = 0

        try:
            # Run agent with streaming to capture intermediate steps
            config = {"recursion_limit": max_iterations}

            for event in self.graph.stream(
                {"messages": [("user", task)]},
                config=config,
                stream_mode="values"
            ):
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    self._finalize_trace(error="Timeout exceeded")
                    break

                # Record each step
                if "messages" in event:
                    last_message = event["messages"][-1]

                    # Record agent actions
                    if hasattr(last_message, 'content'):
                        self._record_action(
                            action_type="message",
                            content=str(last_message.content),
                            metadata={"message_type": type(last_message).__name__}
                        )

                    # Record tool calls
                    if hasattr(last_message, 'tool_calls'):
                        for tool_call in last_message.tool_calls:
                            self._record_tool_call(
                                tool_name=tool_call['name'],
                                arguments=tool_call.get('args', {}),
                                success=True,  # LangGraph handles tool execution
                                result=None  # Result comes in next message
                            )

                iterations += 1

                if iterations >= max_iterations:
                    self._finalize_trace(error="Max iterations reached")
                    break

        except Exception as e:
            return self._finalize_trace(error=str(e))

        return self._finalize_trace()


class AutoGPTWrapper(AgentFramework):
    """Wrapper for AutoGPT-style autonomous loop agent."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        super().__init__(model, temperature)
        self.tools_registry = {}
        self.memory = []

    def setup(self, tools: List[Callable], system_prompt: str) -> None:
        """Initialize AutoGPT agent with tools."""
        self.tools_registry = {tool.__name__: tool for tool in tools}
        self.system_prompt = system_prompt
        self.memory = []

    def run(
        self,
        task: str,
        max_iterations: int = 20,
        timeout_seconds: int = 300
    ) -> ExecutionTrace:
        """
        Execute AutoGPT-style agent loop.

        Note: This is a simplified implementation for testing purposes.
        Production AutoGPT has more sophisticated memory and planning.
        """
        task_id = f"autogpt_{int(time.time())}"
        self._start_trace(task_id)

        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")

        client = OpenAI()
        start_time = time.time()

        # Initial memory setup
        self.memory = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        for iteration in range(max_iterations):
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                return self._finalize_trace(error="Timeout exceeded")

            # Get next action from LLM
            response = client.chat.completions.create(
                model=self.model,
                messages=self.memory,
                temperature=self.temperature
            )

            message = response.choices[0].message.content

            # Record action
            self._record_action(
                action_type="reasoning",
                content=message,
                metadata={"iteration": iteration}
            )

            # Check for completion
            if "TASK_COMPLETE" in message or "FINISH" in message:
                return self._finalize_trace(
                    final_state={"completed": True, "iterations": iteration}
                )

            # Add to memory
            self.memory.append({"role": "assistant", "content": message})

            # Simple feedback (in real AutoGPT, this would be tool execution results)
            feedback = "Continue with next step."
            self.memory.append({"role": "user", "content": feedback})

        return self._finalize_trace(
            error="Max iterations reached",
            final_state={"completed": False, "iterations": max_iterations}
        )


# Factory function for easy framework instantiation
def create_agent(
    framework: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7
) -> AgentFramework:
    """
    Factory function to create agent framework wrappers.

    Args:
        framework: "langgraph", "autogpt", or "swarm"
        model: LLM model identifier
        temperature: Sampling temperature

    Returns:
        AgentFramework instance
    """
    frameworks = {
        "langgraph": LangGraphWrapper,
        "autogpt": AutoGPTWrapper,
    }

    if framework not in frameworks:
        raise ValueError(
            f"Unknown framework: {framework}. "
            f"Supported: {list(frameworks.keys())}"
        )

    return frameworks[framework](model=model, temperature=temperature)
