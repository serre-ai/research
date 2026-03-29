"""Simple ReAct agent implementation for controlled experiments.

Based on: Yao et al. (2023) - ReAct: Synergizing Reasoning and Acting in Language Models
Architecture: Iterative loop of Thought → Action → Observation
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Mock LLM call for now - will use real API in actual run
USE_MOCK = os.getenv("AGENT_FAILURE_MOCK", "1") == "1"


class ReActAgent:
    """ReAct agent with configurable tool set."""

    def __init__(self, tools: List[str], model: str = "gpt-4o-2024-11-20", max_iterations: int = 20):
        self.tools = tools
        self.model = model
        self.max_iterations = max_iterations
        self.iteration = 0

    def run(self, task: str, logger) -> Tuple[bool, str, Any]:
        """Execute task using ReAct loop.

        Returns:
            (success, reason, final_answer)
        """
        logger.log_task_start(task, self.tools, ground_truth=None)

        prompt = self._build_initial_prompt(task)
        observation = "Task started."

        for i in range(self.max_iterations):
            self.iteration = i + 1

            # Get thought + action from LLM
            response = self._call_llm(prompt + f"\nObservation {i}: {observation}\n", logger)

            # Parse thought and action
            thought = self._extract_thought(response)
            action = self._extract_action(response)

            logger.log_reasoning(thought, self.iteration)
            logger.log_action(action, self.iteration)

            # Check for completion
            if action.startswith("Finish["):
                answer = self._extract_answer(action)
                logger.log_completion(True, "agent_finished", answer, {
                    "iterations": self.iteration
                })
                return True, "agent_finished", answer

            # Execute action
            observation, is_valid_tool = self._execute_action(action, logger)

            # Check timeout
            if self.iteration >= self.max_iterations:
                logger.log_completion(False, "max_iterations", None, {
                    "iterations": self.iteration
                })
                return False, "max_iterations", None

        return False, "timeout", None

    def _build_initial_prompt(self, task: str) -> str:
        """Build ReAct prompt with task and tools."""
        tool_list = "\n".join(f"- {tool}" for tool in self.tools)

        return f"""You are an autonomous agent. Solve the following task by reasoning and acting.

Task: {task}

Available tools:
{tool_list}

You can also use:
- Finish[answer]: Submit your final answer

Format your response as:
Thought: [your reasoning]
Action: [tool_name[args] or Finish[answer]]

Begin!
"""

    def _call_llm(self, prompt: str, logger) -> str:
        """Call LLM API (or mock for testing)."""
        if USE_MOCK:
            # Mock response for testing infrastructure
            response = f"Thought: I should use the first available tool.\nAction: {self.tools[0]}[test]"
        else:
            # Real API call would go here
            # For now, also mock - will implement OpenAI API later
            response = f"Thought: I should use the first available tool.\nAction: {self.tools[0]}[test]"

        # Log the call (mock tokens/cost for now)
        logger.log_llm_call(
            prompt=prompt,
            response=response,
            model=self.model,
            tokens={"prompt": len(prompt) // 4, "completion": len(response) // 4, "total": (len(prompt) + len(response)) // 4},
            cost=0.001  # mock cost
        )

        return response

    def _extract_thought(self, response: str) -> str:
        """Extract thought from response."""
        match = re.search(r"Thought:\s*(.+?)(?:\nAction:|$)", response, re.DOTALL)
        return match.group(1).strip() if match else "No thought extracted"

    def _extract_action(self, response: str) -> str:
        """Extract action from response."""
        match = re.search(r"Action:\s*(.+?)(?:\n|$)", response)
        return match.group(1).strip() if match else "No action extracted"

    def _extract_answer(self, action: str) -> str:
        """Extract answer from Finish[...] action."""
        match = re.search(r"Finish\[(.+?)\]", action)
        return match.group(1).strip() if match else "No answer"

    def _execute_action(self, action: str, logger) -> Tuple[str, bool]:
        """Execute action and return observation.

        Returns:
            (observation, is_valid_tool)
        """
        # Parse tool name
        match = re.match(r"(\w+)\[(.+?)\]", action)
        if not match:
            return "Error: Invalid action format. Use tool_name[args]", False

        tool_name, args = match.groups()

        # Check if tool exists
        is_valid = tool_name in self.tools or tool_name == "Finish"

        # Log tool call
        logger.log_tool_call(tool_name, {"args": args}, "mock_result", is_valid)

        if not is_valid:
            # TOOL FABRICATION DETECTED
            return f"Error: Tool '{tool_name}' does not exist. Available tools: {', '.join(self.tools[:5])}...", False

        # Mock execution (actual tools would have real implementations)
        return f"Tool {tool_name} executed successfully with args: {args}", True


# Test harness
if __name__ == "__main__":
    from utils.logging import ExperimentLogger
    from pathlib import Path

    # Test agent
    tools = ["get_data", "process_data", "save_data"]
    agent = ReActAgent(tools, max_iterations=5)

    logger = ExperimentLogger(Path("test_logs"), "test_instance")
    success, reason, answer = agent.run("Get some data and save it", logger)

    print(f"Success: {success}")
    print(f"Reason: {reason}")
    print(f"Answer: {answer}")
