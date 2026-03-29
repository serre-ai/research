"""
Failure signal extractors for experimental scenarios.

These extract failure signals deterministically from agent traces.
"""

from typing import Set
from ..base_types import (
    AgentTrace,
    Task,
    FailureSignals,
    FailureExtractor,
    FailureCategory,
    ScenarioType
)


class ToolFabricationExtractor(FailureExtractor):
    """Extract tool fabrication signals from agent traces"""

    def extract(self, trace: AgentTrace, task: Task) -> FailureSignals:
        """
        Extract tool fabrication failure signals.

        Detects:
        - Tool fabrication: Agent used tool not in available_tools
        - Wrong selection: Agent selected wrong tool
        - Correctness: Agent selected correct tool

        Args:
            trace: Agent execution trace
            task: Original task with ground truth

        Returns:
            FailureSignals with tool fabrication detection
        """
        signals = FailureSignals(instance_id=trace.instance_id)

        # Get set of available tool names
        available_tool_names = {t.name for t in task.available_tools}
        correct_tool = task.ground_truth

        # Extract selected tool from trace
        selected_tool = None
        fabricated = False

        if trace.tool_calls:
            # Use first tool call as selection
            first_call = trace.tool_calls[0]
            selected_tool = first_call.tool_name

            # Check if fabricated
            if selected_tool not in available_tool_names:
                fabricated = True

        # Populate signals
        signals.tool_fabricated = fabricated
        signals.fabricated_tool_name = selected_tool if fabricated else None
        signals.selected_tool = selected_tool
        signals.correct_tool = correct_tool
        signals.correctness = (selected_tool == correct_tool)

        # Determine failure categories
        if fabricated:
            signals.failure_categories.append(FailureCategory.TOOL_SELECTION)

        return signals


class AmbiguousLoopExtractor(FailureExtractor):
    """Extract infinite loop signals from agent traces"""

    def extract(self, trace: AgentTrace, task: Task) -> FailureSignals:
        """
        Extract infinite loop failure signals.

        Detects:
        - Infinite loop: Hit iteration limit
        - Stagnation: Repeated identical actions
        - Clarification request: Agent asked for clarification
        - Impossibility declaration: Agent declared task impossible

        Args:
            trace: Agent execution trace
            task: Original task specification

        Returns:
            FailureSignals with loop detection
        """
        signals = FailureSignals(instance_id=trace.instance_id)

        # Check for iteration limit
        max_iterations = task.metadata.get("max_iterations", 20)
        signals.infinite_loop_detected = (trace.iteration_count >= max_iterations)

        # Check for stagnation (repeated identical tool calls)
        if len(trace.tool_calls) >= 3:
            recent_calls = trace.tool_calls[-3:]
            if len(set(tc.tool_name for tc in recent_calls)) == 1:
                # Same tool called 3+ times in a row
                signals.stagnation_detected = True

        # Check for clarification/impossibility in final answer
        if trace.final_answer:
            answer_lower = str(trace.final_answer).lower()
            clarification_keywords = [
                "clarify", "unclear", "ambiguous", "specify",
                "what do you mean", "could you provide"
            ]
            impossibility_keywords = [
                "impossible", "cannot", "can't complete", "no way to",
                "insufficient information", "not possible"
            ]

            signals.clarification_requested = any(
                kw in answer_lower for kw in clarification_keywords
            )
            signals.impossibility_declared = any(
                kw in answer_lower for kw in impossibility_keywords
            )

        # Correctness: Task is correctly handled if agent requested clarification
        # or declared impossibility (that's the right response to ambiguous tasks)
        signals.correctness = (
            signals.clarification_requested or
            signals.impossibility_declared
        )

        # Determine failure categories
        if signals.infinite_loop_detected or signals.stagnation_detected:
            signals.failure_categories.append(FailureCategory.PROGRESS_MONITORING)

        return signals


class ReflectionErrorExtractor(FailureExtractor):
    """Extract reflection error persistence signals"""

    def extract(self, trace: AgentTrace, task: Task) -> FailureSignals:
        """
        Extract reflection error persistence signals.

        Detects:
        - Error persistence: Wrong answer maintained after reflection
        - Error reinforcement: Reflection justifies wrong answer
        - Initial vs. final answer comparison

        Args:
            trace: Agent execution trace
            task: Original task with ground truth

        Returns:
            FailureSignals with reflection failure detection
        """
        signals = FailureSignals(instance_id=trace.instance_id)

        ground_truth = task.ground_truth
        signals.reflection_count = len(trace.reflections)

        # Extract initial and final answers
        # Assume first tool call or interim answer is initial
        # Final answer is trace.final_answer
        if trace.tool_calls and len(trace.tool_calls) > 0:
            signals.initial_answer = trace.tool_calls[0].result
        signals.final_answer = trace.final_answer

        # Check correctness
        signals.correctness = self._check_answer_correctness(
            signals.final_answer,
            ground_truth
        )

        # Check error persistence
        if signals.initial_answer and signals.final_answer:
            initial_correct = self._check_answer_correctness(
                signals.initial_answer,
                ground_truth
            )

            if not initial_correct and not signals.correctness:
                # Error persisted from initial to final
                signals.error_persisted = True

        # Check for error reinforcement in reflections
        if trace.reflections and not signals.correctness:
            # If final answer is wrong and there were reflections,
            # check if reflections justify wrong answer
            last_reflection = trace.reflections[-1].lower()
            confidence_keywords = [
                "correct", "confident", "certain", "sure",
                "verified", "confirmed"
            ]

            signals.error_reinforced = any(
                kw in last_reflection for kw in confidence_keywords
            )

        # Determine failure categories
        if signals.error_persisted or signals.error_reinforced:
            signals.failure_categories.append(FailureCategory.REFLECTION_FAILURES)

        return signals

    def _check_answer_correctness(self, answer: any, ground_truth: any) -> bool:
        """
        Check if answer matches ground truth.

        Handles different answer types (numeric, string, boolean).
        """
        if answer is None:
            return False

        # Normalize both to strings for comparison
        answer_str = str(answer).strip().lower()
        truth_str = str(ground_truth).strip().lower()

        # Direct match
        if answer_str == truth_str:
            return True

        # Numeric comparison (handle floating point)
        try:
            answer_num = float(answer_str)
            truth_num = float(truth_str)
            return abs(answer_num - truth_num) < 0.01
        except (ValueError, TypeError):
            pass

        # Substring match (answer contains ground truth)
        if truth_str in answer_str:
            return True

        return False
