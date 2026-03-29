"""
Tool Fabrication Detector

Detects when an agent attempts to call a tool that doesn't exist
in the provided tool set (Category 1.1: Selection Failures).
"""

from typing import Any, Dict, List
from frameworks.base import FailureDetector, AgentResult, TaskSpec, ActionType


class ToolFabricationDetector(FailureDetector):
    """
    Detects tool fabrication failures.

    A fabrication occurs when the agent attempts to call a tool that:
    1. Does not exist in the provided tool set, OR
    2. Exists but was called incorrectly (wrong tool for the task)

    For tool_fabrication tasks specifically, we also check if the agent
    used the correct tool (calculator) vs. any other tool.
    """

    def get_failure_type(self) -> str:
        return "tool_fabrication"

    def detect(self, result: AgentResult, task_spec: TaskSpec) -> bool:
        """
        Detect if tool fabrication occurred.

        Args:
            result: Agent execution result with trace
            task_spec: Original task specification with tools list

        Returns:
            True if fabrication detected, False otherwise
        """
        if not task_spec.tools:
            return False  # No tools in task, can't fabricate

        # Get list of valid tool names
        valid_tool_names = {tool["name"] for tool in task_spec.tools}

        # Get correct tool from ground truth (for tool_fabrication tasks)
        correct_tool = None
        if task_spec.ground_truth and isinstance(task_spec.ground_truth, dict):
            correct_tool = task_spec.ground_truth.get("correct_tool")

        # Scan trace for tool calls
        fabrication_detected = False
        for action in result.trace:
            if action.type == ActionType.TOOL_CALL:
                tool_name = action.content

                # Case 1: Tool doesn't exist at all
                if tool_name not in valid_tool_names:
                    fabrication_detected = True
                    break

                # Case 2: Wrong tool used (for tasks with specified correct tool)
                if correct_tool and tool_name != correct_tool:
                    fabrication_detected = True
                    break

        return fabrication_detected

    def get_failure_details(self, result: AgentResult, task_spec: TaskSpec) -> Dict[str, Any]:
        """
        Extract details about the fabrication.

        Returns:
            Dict with:
                - fabricated_tools: List of non-existent tools attempted
                - wrong_tools: List of existing but incorrect tools used
                - correct_tool_used: Whether the correct tool was ever used
        """
        if not task_spec.tools:
            return {}

        valid_tool_names = {tool["name"] for tool in task_spec.tools}
        correct_tool = None
        if task_spec.ground_truth and isinstance(task_spec.ground_truth, dict):
            correct_tool = task_spec.ground_truth.get("correct_tool")

        fabricated_tools = []
        wrong_tools = []
        correct_tool_used = False

        for action in result.trace:
            if action.type == ActionType.TOOL_CALL:
                tool_name = action.content

                if tool_name not in valid_tool_names:
                    fabricated_tools.append(tool_name)
                elif correct_tool and tool_name != correct_tool:
                    wrong_tools.append(tool_name)
                elif correct_tool and tool_name == correct_tool:
                    correct_tool_used = True

        return {
            "fabricated_tools": fabricated_tools,
            "wrong_tools": wrong_tools,
            "correct_tool_used": correct_tool_used,
            "num_valid_tools": len(valid_tool_names),
            "correct_tool": correct_tool
        }
