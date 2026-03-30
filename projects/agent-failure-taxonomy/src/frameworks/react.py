"""
ReAct agent implementation.

Implements the ReAct (Reasoning + Acting) pattern: the agent alternates between
reasoning about the task and taking actions, with explicit reasoning traces.

Reference: Yao et al. (2023) - ReAct: Synergizing Reasoning and Acting in Language Models
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import re

from .base import BaseAgent, AgentStep, AgentResult, Tool


class ReActAgent(BaseAgent):
    """
    ReAct agent implementation.

    The agent follows a simple loop:
    1. Reason about the current state and what to do next
    2. Select and execute an action
    3. Observe the result
    4. Repeat until task is complete or max steps reached
    """

    def get_framework_name(self) -> str:
        return "react"

    def run(
        self,
        task_description: str,
        tools: List[Dict[str, Any]],
        task_id: str,
    ) -> AgentResult:
        """Execute ReAct agent on the task."""
        start_time = datetime.now().isoformat()
        steps = []
        completion_claimed = False

        # Convert tool dicts to Tool objects
        tool_objects = {}
        for tool_dict in tools:
            # For this prototype, tools are mock functions
            # In full implementation, these would be actual callable functions
            tool_name = tool_dict["name"]
            tool_objects[tool_name] = tool_dict

        # Build initial prompt
        prompt = self._build_prompt(task_description, tools, steps)

        for step_num in range(1, self.max_steps + 1):
            # Get LLM response (mock for now - will integrate actual API calls)
            reasoning, action, action_input, is_final = self._parse_llm_response(
                self._mock_llm_call(prompt, step_num)
            )

            # Execute action
            observation, error = self._execute_action(
                action, action_input, tool_objects
            )

            # Check for completion claim
            if "task complete" in reasoning.lower() or "finished" in reasoning.lower():
                completion_claimed = True
                is_final = True

            # Create step record
            step = AgentStep(
                step_number=step_num,
                timestamp=datetime.now().isoformat(),
                reasoning=reasoning,
                action=action,
                action_input=action_input,
                observation=observation,
                is_final=is_final,
                error=error,
                metadata={"tokens": 500, "cost": 0.01},  # Mock values
            )

            steps.append(step)
            self._log_step(step)

            # Check termination conditions
            if is_final or error:
                break

            # Update prompt with new step
            prompt = self._build_prompt(task_description, tools, steps)

        end_time = datetime.now().isoformat()
        success = is_final and not error

        return self._create_result(
            task_id=task_id,
            steps=steps,
            start_time=start_time,
            end_time=end_time,
            success=success,
            completion_claimed=completion_claimed,
            error=error if error else None,
        )

    def _build_prompt(
        self,
        task_description: str,
        tools: List[Dict[str, Any]],
        steps: List[AgentStep],
    ) -> str:
        """Build prompt for LLM call."""
        prompt = f"""You are a ReAct agent. Your task is: {task_description}

Available tools:
"""
        for tool in tools:
            prompt += f"- {tool['name']}: {tool['description']}\n"

        prompt += """
Follow this format:
Thought: [Your reasoning about what to do next]
Action: [Tool name to use]
Action Input: [Parameters for the tool]

After seeing the observation, either continue with another thought-action pair or conclude.
To indicate completion, include "Task complete" in your thought.

"""

        # Add previous steps to prompt
        for step in steps:
            prompt += f"\nThought: {step.reasoning}"
            prompt += f"\nAction: {step.action}"
            prompt += f"\nAction Input: {step.action_input}"
            prompt += f"\nObservation: {step.observation}\n"

        return prompt

    def _mock_llm_call(self, prompt: str, step_num: int) -> str:
        """
        Mock LLM response for testing.

        In full implementation, this would call the actual LLM API.
        """
        # Simple mock that varies based on step number
        if step_num == 1:
            return """Thought: I need to start working on this task. Let me use the first available tool.
Action: search
Action Input: {"query": "relevant information"}"""
        elif step_num == 2:
            return """Thought: Based on the search results, I should verify the information.
Action: verify
Action Input: {"item": "search result"}"""
        else:
            return """Thought: I have completed the necessary steps. Task complete.
Action: finish
Action Input: {"result": "task completed"}"""

    def _parse_llm_response(
        self, response: str
    ) -> tuple[str, str, Dict[str, Any], bool]:
        """
        Parse LLM response into reasoning, action, and action input.

        Returns:
            (reasoning, action, action_input, is_final)
        """
        # Extract thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|$)", response, re.DOTALL)
        reasoning = thought_match.group(1).strip() if thought_match else "No reasoning provided"

        # Extract action
        action_match = re.search(r"Action:\s*(\w+)", response)
        action = action_match.group(1).strip() if action_match else "unknown"

        # Extract action input
        input_match = re.search(r"Action Input:\s*(.+?)(?=\n|$)", response, re.DOTALL)
        action_input_str = input_match.group(1).strip() if input_match else "{}"

        # Try to parse as JSON, fallback to dict with raw string
        try:
            import json
            action_input = json.loads(action_input_str)
        except:
            action_input = {"raw": action_input_str}

        # Check if final
        is_final = action.lower() == "finish" or "complete" in reasoning.lower()

        return reasoning, action, action_input, is_final

    def _execute_action(
        self,
        action: str,
        action_input: Dict[str, Any],
        tool_objects: Dict[str, Any],
    ) -> tuple[str, Optional[str]]:
        """
        Execute the specified action.

        Returns:
            (observation, error)
        """
        # Check if action corresponds to a real tool
        if action not in tool_objects and action != "finish":
            # Tool fabrication detected!
            error = f"Tool '{action}' does not exist in the available tool set"
            observation = f"Error: {error}"
            return observation, error

        if action == "finish":
            return "Task execution finished", None

        # Mock execution for prototype
        # In full implementation, this would call the actual tool function
        observation = f"Executed {action} with input {action_input}. Result: [mock result]"
        return observation, None


def create_react_agent(
    model: str = "claude-haiku-4-5-20251001",
    temperature: float = 1.0,
    max_steps: int = 50,
    verbose: bool = False,
) -> ReActAgent:
    """
    Factory function to create a ReAct agent.

    Args:
        model: LLM model identifier
        temperature: Sampling temperature
        max_steps: Maximum steps before forced termination
        verbose: Whether to print execution progress

    Returns:
        Configured ReActAgent instance
    """
    return ReActAgent(
        model=model,
        temperature=temperature,
        max_steps=max_steps,
        verbose=verbose,
    )
