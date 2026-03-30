"""Simple ReAct agent implementation for failure taxonomy experiments.

This is a minimal, controlled ReAct implementation designed for reproducible
experiments, not a production agent system.
"""

import json
import re
from typing import Any, Dict, List, Optional
from anthropic import Anthropic

from ..config import ANTHROPIC_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE, MAX_ITERATIONS
from ..tools.standard_tools import ToolRegistry


class ReActAgent:
    """Minimal ReAct agent for controlled experiments.

    Implements the ReAct pattern: Thought → Action → Observation loop.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_iterations: int = MAX_ITERATIONS,
    ):
        """Initialize ReAct agent.

        Args:
            model: Anthropic model identifier
            temperature: Sampling temperature
            max_iterations: Maximum reasoning-action loops before stopping
        """
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.tool_registry = ToolRegistry()

        # Tracking
        self.trajectory = []
        self.total_tokens = 0
        self.api_calls = 0
        self.cost_usd = 0.0

    def run(self, task: str) -> Dict[str, Any]:
        """Run the agent on a task.

        Args:
            task: Task description

        Returns:
            Dictionary with outcome, trajectory, and metrics
        """
        self.trajectory = []
        self.total_tokens = 0
        self.api_calls = 0
        self.cost_usd = 0.0

        system_prompt = self._build_system_prompt()
        messages = [{"role": "user", "content": task}]

        for iteration in range(self.max_iterations):
            # Get agent's thought and action
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages,
            )

            self.api_calls += 1
            self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
            self.cost_usd += self._calculate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            response_text = response.content[0].text

            # Parse thought and action
            thought, action, action_input = self._parse_response(response_text)

            step = {
                "iteration": iteration + 1,
                "thought": thought,
                "action": action,
                "action_input": action_input,
                "raw_response": response_text,
            }

            # Check for completion
            if action == "finish" or action == "final_answer":
                step["observation"] = "Task complete"
                self.trajectory.append(step)
                return {
                    "status": "completed",
                    "final_answer": action_input,
                    "trajectory": self.trajectory,
                    "iterations": iteration + 1,
                    "metrics": self._get_metrics(),
                }

            # Execute action
            observation = self._execute_action(action, action_input)
            step["observation"] = observation

            self.trajectory.append(step)

            # Add observation to messages
            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": f"Observation: {observation}"})

        # Max iterations reached
        return {
            "status": "max_iterations",
            "final_answer": None,
            "trajectory": self.trajectory,
            "iterations": self.max_iterations,
            "metrics": self._get_metrics(),
        }

    def _build_system_prompt(self) -> str:
        """Build system prompt with ReAct format and available tools."""
        tools_description = self.tool_registry.get_tool_descriptions()

        return f"""You are a ReAct agent that solves tasks by reasoning and taking actions.

Available tools:
{tools_description}

You must respond in this exact format:

Thought: [Your reasoning about what to do next]
Action: [The tool name to use, or "finish" when task is complete]
Action Input: [The input to the tool, or your final answer if finishing]

After each action, you will receive an observation with the result. Continue the Thought/Action/Observation cycle until you can provide a final answer.

When you have the final answer, use:
Action: finish
Action Input: [Your final answer]

Important:
- Only use tools that are explicitly listed above
- If a tool you need doesn't exist, explain why you cannot complete the task
- Be precise with tool names and inputs
"""

    def _parse_response(self, text: str) -> tuple[str, str, str]:
        """Parse agent response into thought, action, and action input.

        Args:
            text: Agent's response text

        Returns:
            (thought, action, action_input) tuple
        """
        thought = ""
        action = ""
        action_input = ""

        # Extract Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\n(?:Action:|$))", text, re.DOTALL | re.IGNORECASE)
        if thought_match:
            thought = thought_match.group(1).strip()

        # Extract Action
        action_match = re.search(r"Action:\s*(\w+)", text, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip().lower()

        # Extract Action Input
        input_match = re.search(r"Action Input:\s*(.+?)(?=\n(?:Thought:|Action:|$)|$)", text, re.DOTALL | re.IGNORECASE)
        if input_match:
            action_input = input_match.group(1).strip()

        return thought, action, action_input

    def _execute_action(self, action: str, action_input: str) -> str:
        """Execute an action and return observation.

        Args:
            action: Tool name
            action_input: Tool input

        Returns:
            Observation string
        """
        if action in ["finish", "final_answer"]:
            return "Task complete"

        # Try to parse action_input as JSON if it looks like structured input
        try:
            # Simple heuristic: if action_input has key=value or is JSON, parse it
            if "=" in action_input or (action_input.startswith("{") and action_input.endswith("}")):
                # Try JSON first
                try:
                    kwargs = json.loads(action_input)
                except:
                    # Parse key=value format
                    kwargs = {}
                    parts = action_input.split(",")
                    for part in parts:
                        if "=" in part:
                            key, value = part.split("=", 1)
                            kwargs[key.strip()] = value.strip().strip("'\"")
            else:
                # Single string argument
                kwargs = {"query": action_input} if action == "search" else \
                         {"city": action_input} if action == "weather" else \
                         {"expression": action_input} if action == "calculator" else \
                         {"filename": action_input} if action == "file_read" else \
                         {"text": action_input}  # Default for string operations
        except:
            # Fallback: treat as single argument
            kwargs = {list(self.tool_registry.tools.keys())[0]: action_input}

        result = self.tool_registry.call_tool(action, **kwargs)

        if result["success"]:
            return str(result["result"])
        else:
            return f"Error: {result['error']}"

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for API call."""
        # Claude 3.5 Sonnet: $3/M input, $15/M output
        return (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000

    def _get_metrics(self) -> Dict[str, Any]:
        """Get metrics for this run."""
        return {
            "total_tokens": self.total_tokens,
            "api_calls": self.api_calls,
            "cost_usd": round(self.cost_usd, 4),
        }
