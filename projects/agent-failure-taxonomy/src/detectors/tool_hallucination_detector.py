"""Detector for tool hallucination failures (Category 1.1)."""

import re
from typing import List, Dict, Any


class ToolHallucinationDetector:
    """Detects when an agent attempts to use non-existent tools.

    Maps to Taxonomy Category 1.1 (Selection Failures) and root causes:
    - C6: Tool Grounding
    - C1: Factual Grounding
    """

    def __init__(self, valid_tool_names: List[str]):
        """Initialize with list of valid tool names."""
        self.valid_tool_names = set(valid_tool_names)
        self.hallucinated_tools = []
        self.failed_tool_calls = []

    def check_tool_call(self, tool_name: str, call_result: Dict[str, Any]) -> bool:
        """Check if a tool call is a hallucination.

        Args:
            tool_name: Name of tool being called
            call_result: Result dictionary from ToolRegistry.call_tool()

        Returns:
            True if hallucination detected, False otherwise
        """
        is_hallucinated = call_result.get("hallucinated", False)

        if is_hallucinated:
            self.hallucinated_tools.append(tool_name)
            self.failed_tool_calls.append({
                "tool_name": tool_name,
                "error": call_result.get("error", "Unknown error"),
            })
            return True

        return False

    def check_text_for_hallucinations(self, text: str) -> List[str]:
        """Check if text mentions non-existent tools.

        This catches cases where the agent discusses or plans to use
        tools that don't exist, even if it hasn't called them yet.

        Args:
            text: Agent's reasoning or planning text

        Returns:
            List of suspected hallucinated tool names
        """
        suspected = []

        # Common patterns for tool mentions
        patterns = [
            r"use\s+(\w+)\s+tool",
            r"call\s+(\w+)\(",
            r"(\w+)\s+function",
            r"invoke\s+(\w+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                tool_name = match.lower()
                # Check if it's not in valid tools and looks tool-like
                if (tool_name not in self.valid_tool_names and
                    not tool_name in ["the", "a", "an", "this", "that"]):
                    suspected.append(tool_name)

        return suspected

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of detected hallucinations."""
        return {
            "hallucination_detected": len(self.hallucinated_tools) > 0,
            "hallucinated_tool_count": len(self.hallucinated_tools),
            "hallucinated_tools": self.hallucinated_tools,
            "failed_calls": self.failed_tool_calls,
        }

    def reset(self):
        """Reset detector state for new run."""
        self.hallucinated_tools = []
        self.failed_tool_calls = []
