"""
Automated failure detection for agent experiments.

Classifies agent runs into failure categories from the taxonomy:
- Tool hallucination (1.1)
- Infinite loops (3.1)
- False completion (5.1)
- Timeout
- Success
"""

from typing import Any, Dict, List, Optional, Tuple


class FailureDetector:
    """Detects failure patterns in agent execution traces."""

    @staticmethod
    def detect_tool_hallucination(
        trace: List[Dict[str, Any]], valid_tools: List[str]
    ) -> bool:
        """
        Detect if agent used non-existent tools.

        Args:
            trace: Agent execution trace
            valid_tools: List of valid tool names

        Returns:
            True if tool hallucination detected
        """
        for step in trace:
            action = step.get("action", "")
            # Check if action is a tool name that doesn't exist
            if action and action not in valid_tools and action != "Final Answer":
                return True
        return False

    @staticmethod
    def detect_infinite_loop(
        trace: List[Dict[str, Any]], repeat_threshold: int = 3
    ) -> bool:
        """
        Detect if agent repeated the same action multiple times.

        Args:
            trace: Agent execution trace
            repeat_threshold: Number of repeats to consider a loop

        Returns:
            True if infinite loop detected
        """
        if len(trace) < repeat_threshold:
            return False

        # Check for exact action repetition
        for i in range(len(trace) - repeat_threshold + 1):
            actions = [
                trace[i + j].get("action") for j in range(repeat_threshold)
            ]
            if len(set(actions)) == 1 and actions[0] != "Final Answer":
                return True

        # Check for action-observation cycles (e.g., search -> read same page -> search again)
        if len(trace) >= 6:
            for i in range(len(trace) - 5):
                # Pattern: action1, action2, action1, action2, action1, action2
                a1 = trace[i].get("action")
                a2 = trace[i + 1].get("action")
                if (
                    a1
                    and a2
                    and a1 != a2
                    and trace[i + 2].get("action") == a1
                    and trace[i + 3].get("action") == a2
                    and trace[i + 4].get("action") == a1
                ):
                    return True

        return False

    @staticmethod
    def detect_no_progress(
        trace: List[Dict[str, Any]], window_size: int = 5
    ) -> bool:
        """
        Detect if agent made no meaningful progress.

        Args:
            trace: Agent execution trace
            window_size: Number of steps to check for stagnation

        Returns:
            True if no progress detected
        """
        if len(trace) < window_size:
            return False

        # Check if observations are identical (agent doing same thing with same result)
        recent_obs = [
            step.get("observation", "")
            for step in trace[-window_size:]
            if step.get("observation")
        ]

        if len(recent_obs) >= window_size - 1:
            # More than 80% identical observations = no progress
            unique_obs = len(set(recent_obs))
            if unique_obs <= 2:
                return True

        return False

    @staticmethod
    def check_task_completion(
        final_output: Optional[str],
        ground_truth: Any,
        success_criteria: callable,
    ) -> bool:
        """
        Check if task was actually completed correctly.

        Args:
            final_output: Agent's final answer
            ground_truth: Expected answer or state
            success_criteria: Function that returns True if task completed

        Returns:
            True if task completed successfully
        """
        try:
            return success_criteria(final_output, ground_truth)
        except Exception as e:
            print(f"Error checking success criteria: {e}")
            return False

    @staticmethod
    def classify_outcome(
        trace: List[Dict[str, Any]],
        final_output: Optional[str],
        ground_truth: Any,
        success_criteria: callable,
        valid_tools: List[str],
        max_iterations: int,
    ) -> Tuple[str, Optional[str]]:
        """
        Classify agent run outcome and failure type.

        Args:
            trace: Agent execution trace
            final_output: Agent's final answer
            ground_truth: Expected answer
            success_criteria: Function to check completion
            valid_tools: List of valid tool names
            max_iterations: Maximum allowed iterations

        Returns:
            (outcome, failure_type) tuple
            outcome: success | failure | timeout | error
            failure_type: tool_hallucination | infinite_loop | false_completion | no_progress | None
        """
        if not trace:
            return ("error", None)

        # Check for timeout
        if len(trace) >= max_iterations:
            # Still check if it succeeded despite timeout
            if FailureDetector.check_task_completion(
                final_output, ground_truth, success_criteria
            ):
                return ("success", None)
            # Timeout with failure - determine why
            if FailureDetector.detect_infinite_loop(trace):
                return ("timeout", "infinite_loop")
            if FailureDetector.detect_no_progress(trace):
                return ("timeout", "no_progress")
            return ("timeout", "max_iterations")

        # Check for success
        if FailureDetector.check_task_completion(
            final_output, ground_truth, success_criteria
        ):
            return ("success", None)

        # Failed - determine failure type
        if FailureDetector.detect_tool_hallucination(trace, valid_tools):
            return ("failure", "tool_hallucination")

        if FailureDetector.detect_infinite_loop(trace):
            return ("failure", "infinite_loop")

        if FailureDetector.detect_no_progress(trace):
            return ("failure", "no_progress")

        # Agent gave final answer but it was wrong = false completion
        if final_output is not None:
            return ("failure", "false_completion")

        return ("failure", "unknown")


def analyze_trace(
    trace: List[Dict[str, Any]],
    final_output: Optional[str],
    ground_truth: Any,
    success_criteria: callable,
    valid_tools: List[str],
    max_iterations: int = 15,
) -> Dict[str, Any]:
    """
    Comprehensive trace analysis.

    Returns:
        Dictionary with outcome, failure_type, and detailed diagnostics
    """
    outcome, failure_type = FailureDetector.classify_outcome(
        trace=trace,
        final_output=final_output,
        ground_truth=ground_truth,
        success_criteria=success_criteria,
        valid_tools=valid_tools,
        max_iterations=max_iterations,
    )

    return {
        "outcome": outcome,
        "failure_type": failure_type,
        "diagnostics": {
            "total_steps": len(trace),
            "tool_hallucination": FailureDetector.detect_tool_hallucination(
                trace, valid_tools
            ),
            "infinite_loop": FailureDetector.detect_infinite_loop(trace),
            "no_progress": FailureDetector.detect_no_progress(trace),
            "task_completed": FailureDetector.check_task_completion(
                final_output, ground_truth, success_criteria
            ),
        },
    }
