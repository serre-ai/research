"""ReAct agent implementation for controlled experiments."""

import re
import time
from typing import Any, Dict, List, Optional

from .base import BaseAgent, AgentExecution, AgentStep, AgentOutcome
from ..tools.simulated import ToolRegistry


REACT_PROMPT = """You are an agent that solves tasks by thinking step-by-step and using tools.

You MUST use this exact format for each step:

Thought: [your reasoning about what to do next]
Action: [tool name]
Action Input: {{"param1": "value1", "param2": "value2"}}
Observation: [will be filled in by tool execution]

After receiving the observation, you can continue with another Thought/Action/Action Input cycle, or finish:

Thought: [final reasoning]
Final Answer: [your final answer to the task]

Available tools:
{tool_descriptions}

Task: {task}

Begin!

"""


class ReActAgent(BaseAgent):
    """
    ReAct agent: Reason + Act in iterative loop.

    Based on Yao et al. (2023) - ReAct: Synergizing Reasoning and Acting.
    Tight observation-action loop without explicit planning phase.
    """

    def __init__(
        self,
        model: str = "gpt-4-0125-preview",
        temperature: float = 0.0,
        max_iterations: int = 20,
        tools: Optional[ToolRegistry] = None,
    ):
        super().__init__(model, temperature, max_iterations)
        self.tools = tools or ToolRegistry()

    def get_framework_name(self) -> str:
        return "react"

    def run(self, task: str, **kwargs) -> AgentExecution:
        """Execute ReAct agent on task."""
        start_time = time.time()

        execution = AgentExecution(
            framework=self.get_framework_name(),
            scenario=kwargs.get("scenario", "unknown"),
            instance_id=kwargs.get("instance_id", "unknown"),
            model=self.model,
            temperature=self.temperature,
            max_iterations=self.max_iterations,
        )

        # Build initial prompt
        tool_descriptions = self.tools.get_tool_descriptions()
        prompt = REACT_PROMPT.format(
            tool_descriptions=tool_descriptions,
            task=task
        )

        conversation_history = prompt
        iteration = 0
        completed = False
        final_answer = None
        error = None

        try:
            while iteration < self.max_iterations and not completed:
                iteration += 1

                # Get LLM response
                response, tokens_in, tokens_out, cost = self._call_llm(conversation_history)

                # Parse response for Thought/Action/Action Input
                parsed = self._parse_react_response(response)

                if parsed.get("final_answer"):
                    # Agent finished
                    final_answer = parsed["final_answer"]
                    completed = True

                    # Record final step
                    execution.trace.append(AgentStep(
                        step=iteration,
                        thought=parsed.get("thought", ""),
                        action="Final Answer",
                        action_input={},
                        observation=final_answer,
                        tokens_in=tokens_in,
                        tokens_out=tokens_out,
                        cost=cost,
                    ))
                    break

                # Execute action
                action = parsed.get("action", "")
                action_input = parsed.get("action_input", {})
                thought = parsed.get("thought", "")

                observation = self._execute_action(action, action_input)

                # Record step
                execution.trace.append(AgentStep(
                    step=iteration,
                    thought=thought,
                    action=action,
                    action_input=action_input,
                    observation=observation,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    cost=cost,
                ))

                # Update conversation history
                conversation_history += f"\n\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"

        except Exception as e:
            error = str(e)
            completed = False

        # Calculate outcome
        total_tokens = sum(step.tokens_in + step.tokens_out for step in execution.trace)
        total_cost = sum(step.cost for step in execution.trace)
        wall_time = time.time() - start_time

        execution.outcome = AgentOutcome(
            completed=completed,
            iterations_used=iteration,
            total_tokens=total_tokens,
            total_cost=total_cost,
            wall_time_seconds=wall_time,
            final_answer=final_answer,
            error=error,
        )

        return execution

    def _call_llm(self, prompt: str) -> tuple[str, int, int, float]:
        """
        Call LLM API.

        For now, returns simulated response. In real implementation,
        would call OpenAI API.

        Returns: (response_text, tokens_in, tokens_out, cost)
        """
        # PLACEHOLDER: In real implementation, call OpenAI API here
        # For now, simulate response for infrastructure testing

        tokens_in = len(prompt.split())  # rough approximation
        tokens_out = 100  # simulated
        cost = (tokens_in / 1000 * 0.01) + (tokens_out / 1000 * 0.03)

        # Simulated response (this will be replaced with real API calls)
        response = """Thought: I need to analyze this task and determine what action to take.
Action: search_web
Action Input: {"query": "relevant search query"}"""

        return response, tokens_in, tokens_out, cost

    def _parse_react_response(self, response: str) -> Dict[str, Any]:
        """Parse ReAct-formatted response."""
        parsed = {}

        # Extract Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\n(?:Action|Final Answer))", response, re.DOTALL)
        if thought_match:
            parsed["thought"] = thought_match.group(1).strip()

        # Extract Final Answer
        final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
        if final_match:
            parsed["final_answer"] = final_match.group(1).strip()
            return parsed

        # Extract Action
        action_match = re.search(r"Action:\s*(\w+)", response)
        if action_match:
            parsed["action"] = action_match.group(1).strip()

        # Extract Action Input (JSON-like)
        input_match = re.search(r"Action Input:\s*(\{.+?\})", response, re.DOTALL)
        if input_match:
            try:
                # Simple JSON parsing (in production, use json.loads with error handling)
                import json
                parsed["action_input"] = json.loads(input_match.group(1))
            except:
                parsed["action_input"] = {}

        return parsed

    def _execute_action(self, action: str, action_input: Dict[str, Any]) -> str:
        """Execute action using tool registry."""
        tool = self.tools.get(action)

        if tool is None:
            # Tool not found - this is the tool fabrication failure!
            return f"Error: Tool '{action}' not found. Available tools: {', '.join(t.name for t in self.tools.list_tools())}"

        try:
            observation = tool.run(**action_input)
            return observation
        except Exception as e:
            return f"Error executing {action}: {str(e)}"
