"""
Infinite loop detector for agent experiments.

Detects when an agent is repeating similar actions without making progress.
Used for validating Category 3.1 (Planning - Progress Monitoring) failures.
"""

from typing import Dict, List, Any
from collections import Counter


class LoopDetector:
    """Detects infinite loops and stagnation in agent execution."""

    def __init__(self, similarity_threshold: int = 5, window_size: int = 10):
        """
        Initialize loop detector.

        Args:
            similarity_threshold: Number of similar consecutive actions to trigger loop detection
            window_size: Number of recent actions to analyze for patterns
        """
        self.similarity_threshold = similarity_threshold
        self.window_size = window_size

    def detect(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze action sequence for loops.

        Args:
            actions: List of action dictionaries from experiment log

        Returns:
            Detection result with loop status, iteration info, repeated action
        """
        if not actions:
            return {
                "loop_detected": False,
                "loop_start_iteration": None,
                "repeated_action": None,
                "repetition_count": 0,
                "pattern_type": None
            }

        # Extract action strings (normalize to compare)
        action_strs = [self._normalize_action(a.get("action", "")) for a in actions]

        # Check for exact repetition pattern
        loop_info = self._detect_exact_repetition(action_strs)
        if loop_info["loop_detected"]:
            return loop_info

        # Check for cyclic pattern (A -> B -> A -> B)
        cycle_info = self._detect_cycle(action_strs)
        if cycle_info["loop_detected"]:
            return cycle_info

        # No loop detected
        return {
            "loop_detected": False,
            "loop_start_iteration": None,
            "repeated_action": None,
            "repetition_count": 0,
            "pattern_type": None
        }

    def _normalize_action(self, action: str) -> str:
        """Normalize action string for comparison (lowercase, strip whitespace)."""
        return action.strip().lower()

    def _detect_exact_repetition(self, actions: List[str]) -> Dict[str, Any]:
        """
        Detect when same action is repeated consecutively.

        Returns loop info if >=similarity_threshold consecutive identical actions found.
        """
        if len(actions) < self.similarity_threshold:
            return {"loop_detected": False}

        # Look for runs of identical actions
        max_run_length = 1
        max_run_action = None
        max_run_start = 0

        current_run_length = 1
        current_run_action = actions[0]
        current_run_start = 0

        for i in range(1, len(actions)):
            if actions[i] == current_run_action:
                current_run_length += 1
            else:
                # Run ended, check if it's the longest
                if current_run_length > max_run_length:
                    max_run_length = current_run_length
                    max_run_action = current_run_action
                    max_run_start = current_run_start

                # Start new run
                current_run_action = actions[i]
                current_run_length = 1
                current_run_start = i

        # Check final run
        if current_run_length > max_run_length:
            max_run_length = current_run_length
            max_run_action = current_run_action
            max_run_start = current_run_start

        if max_run_length >= self.similarity_threshold:
            return {
                "loop_detected": True,
                "loop_start_iteration": max_run_start + 1,  # 1-indexed
                "repeated_action": max_run_action,
                "repetition_count": max_run_length,
                "pattern_type": "exact_repetition"
            }

        return {"loop_detected": False}

    def _detect_cycle(self, actions: List[str]) -> Dict[str, Any]:
        """
        Detect cyclic patterns (e.g., A -> B -> A -> B -> A -> B).

        Returns loop info if pattern repeats >=3 times.
        """
        if len(actions) < 6:  # Need at least 3 cycles of 2-action pattern
            return {"loop_detected": False}

        # Try different cycle lengths (2 to window_size)
        for cycle_len in range(2, min(self.window_size, len(actions) // 3) + 1):
            pattern = actions[-cycle_len:]

            # Count how many times this pattern repeats at the end
            repetitions = 1
            pos = len(actions) - cycle_len * 2

            while pos >= 0 and actions[pos:pos + cycle_len] == pattern:
                repetitions += 1
                pos -= cycle_len

            if repetitions >= 3:  # Pattern repeated at least 3 times
                cycle_start = pos + cycle_len + 1  # 1-indexed
                return {
                    "loop_detected": True,
                    "loop_start_iteration": cycle_start,
                    "repeated_action": " -> ".join(pattern),
                    "repetition_count": repetitions,
                    "pattern_type": f"cycle_length_{cycle_len}"
                }

        return {"loop_detected": False}

    def compute_stagnation_score(self, actions: List[Dict[str, Any]]) -> float:
        """
        Compute a stagnation score (0-1) based on action diversity in recent window.

        Lower score = more repetitive = more stagnation.
        """
        if not actions:
            return 0.0

        # Get last window_size actions
        recent_actions = actions[-self.window_size:]
        action_strs = [self._normalize_action(a.get("action", "")) for a in recent_actions]

        # Count unique actions
        unique_count = len(set(action_strs))
        total_count = len(action_strs)

        # Diversity score: unique / total (high = diverse, low = repetitive)
        diversity = unique_count / total_count if total_count > 0 else 0.0

        # Stagnation is inverse of diversity
        return 1.0 - diversity
