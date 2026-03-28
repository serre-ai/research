"""
Failure Detection Modules

Automated detection of specific failure modes from agent execution traces.
Each detector implements a specific test from the taxonomy validation protocol.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from difflib import SequenceMatcher


@dataclass
class FailureDetectionResult:
    """Result of a failure detection test."""
    failure_detected: bool
    confidence: float  # 0.0 to 1.0
    evidence: List[str]
    metrics: Dict[str, Any]


class FailureDetector:
    """Base class for failure detectors."""

    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category

    def detect(self, trace: Dict[str, Any]) -> FailureDetectionResult:
        """Analyze trace and detect failure. Must be implemented by subclasses."""
        raise NotImplementedError


class ToolFabricationDetector(FailureDetector):
    """
    Detects fabricated tool calls (Category 1.1: Tool-Use Selection Failures).

    A tool call is fabricated if:
    1. The tool name doesn't exist in the tools registry
    2. The tool name is plausible (not random characters)
    3. The arguments follow expected patterns
    """

    def __init__(self, tools_registry: List[str]):
        super().__init__(
            name="Tool Fabrication",
            category="1.1 Tool-Use Selection Failures"
        )
        self.tools_registry = set(tools_registry)

    def detect(self, trace: Dict[str, Any]) -> FailureDetectionResult:
        """Detect fabricated tool calls in execution trace."""
        tool_calls = trace.get('tool_calls', [])
        fabrications = []
        evidence = []

        for idx, call in enumerate(tool_calls):
            tool_name = call['tool']

            # Check if tool exists in registry
            if tool_name not in self.tools_registry:
                # Verify it's a plausible fabrication (not a typo or error)
                if self._is_plausible_tool_name(tool_name):
                    fabrications.append(call)
                    evidence.append(
                        f"Step {idx}: Fabricated tool '{tool_name}' "
                        f"(not in registry: {sorted(self.tools_registry)})"
                    )

        metrics = {
            'total_tool_calls': len(tool_calls),
            'fabricated_calls': len(fabrications),
            'fabrication_rate': len(fabrications) / len(tool_calls) if tool_calls else 0,
            'fabricated_tool_names': [f['tool'] for f in fabrications]
        }

        return FailureDetectionResult(
            failure_detected=len(fabrications) > 0,
            confidence=1.0 if len(fabrications) > 0 else 1.0,  # High confidence (automated)
            evidence=evidence,
            metrics=metrics
        )

    def _is_plausible_tool_name(self, name: str) -> bool:
        """Check if a tool name looks plausible (not random/error)."""
        # Must be valid identifier format
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            return False

        # Must be reasonable length (not too short/long)
        if len(name) < 3 or len(name) > 50:
            return False

        # Must have some similarity to real tool names (but not exact match)
        for real_tool in self.tools_registry:
            similarity = SequenceMatcher(None, name.lower(), real_tool.lower()).ratio()
            if 0.3 < similarity < 1.0:  # Similar but not identical
                return True

        # If no similar tools, still plausible if follows naming convention
        return '_' in name or any(c.isupper() for c in name[1:])


class InfiniteLoopDetector(FailureDetector):
    """
    Detects infinite loops (Category 3.1: Planning Progress Monitoring).

    A loop is detected if:
    1. Agent repeats similar actions multiple times
    2. No progress toward goal is evident
    3. Pattern occurs ≥3 consecutive times
    """

    def __init__(self, similarity_threshold: float = 0.8, min_repetitions: int = 3):
        super().__init__(
            name="Infinite Loop",
            category="3.1 Planning Progress Monitoring"
        )
        self.similarity_threshold = similarity_threshold
        self.min_repetitions = min_repetitions

    def detect(self, trace: Dict[str, Any]) -> FailureDetectionResult:
        """Detect infinite loops by analyzing action similarity."""
        actions = trace.get('actions', [])

        if len(actions) < self.min_repetitions:
            return FailureDetectionResult(
                failure_detected=False,
                confidence=1.0,
                evidence=["Too few actions to detect loop"],
                metrics={'total_actions': len(actions)}
            )

        loops = []
        evidence = []

        # Sliding window to detect repeated patterns
        for i in range(len(actions) - self.min_repetitions + 1):
            window = actions[i:i + self.min_repetitions]
            similarities = self._compute_action_similarities(window)

            avg_similarity = sum(similarities) / len(similarities)

            if avg_similarity >= self.similarity_threshold:
                loops.append({
                    'start_step': i,
                    'end_step': i + self.min_repetitions - 1,
                    'similarity': avg_similarity,
                    'actions': [a['content'][:100] for a in window]
                })

                evidence.append(
                    f"Loop detected at steps {i}-{i + self.min_repetitions - 1}: "
                    f"similarity={avg_similarity:.2f}"
                )

        metrics = {
            'total_actions': len(actions),
            'loops_detected': len(loops),
            'max_similarity': max([l['similarity'] for l in loops]) if loops else 0,
            'loop_details': loops[:3]  # First 3 loops only
        }

        return FailureDetectionResult(
            failure_detected=len(loops) > 0,
            confidence=1.0 if loops else 1.0,
            evidence=evidence,
            metrics=metrics
        )

    def _compute_action_similarities(self, actions: List[Dict]) -> List[float]:
        """Compute pairwise similarity between consecutive actions."""
        similarities = []

        for i in range(len(actions) - 1):
            content1 = actions[i]['content']
            content2 = actions[i + 1]['content']

            # Use SequenceMatcher for text similarity
            similarity = SequenceMatcher(None, content1, content2).ratio()
            similarities.append(similarity)

        return similarities


class ContextDegradationDetector(FailureDetector):
    """
    Detects context degradation (Category 4.3: State Tracking Context Management).

    Context degradation occurs when:
    1. Accuracy drops significantly from beginning to middle/end of context
    2. Agent fails to recall information from earlier in the conversation
    3. Performance drops by ≥30% from baseline
    """

    def __init__(self, degradation_threshold: float = 0.30):
        super().__init__(
            name="Context Degradation",
            category="4.3 State Tracking Context Management"
        )
        self.degradation_threshold = degradation_threshold

    def detect(self, trace: Dict[str, Any]) -> FailureDetectionResult:
        """
        Detect context degradation from position-based accuracy.

        Expects trace to have 'position_accuracy' metadata:
        {
            'beginning': accuracy_at_4k_tokens,
            'middle': accuracy_at_16k_tokens,
            'end': accuracy_at_32k_tokens
        }
        """
        if 'position_accuracy' not in trace.get('final_state', {}):
            return FailureDetectionResult(
                failure_detected=False,
                confidence=0.0,
                evidence=["No position_accuracy data in trace"],
                metrics={}
            )

        accuracy = trace['final_state']['position_accuracy']

        beginning_acc = accuracy.get('beginning', 0)
        middle_acc = accuracy.get('middle', 0)
        end_acc = accuracy.get('end', 0)

        # Compute degradation
        mid_degradation = beginning_acc - middle_acc
        end_degradation = beginning_acc - end_acc
        max_degradation = max(mid_degradation, end_degradation)

        evidence = [
            f"Beginning accuracy: {beginning_acc:.1%}",
            f"Middle accuracy: {middle_acc:.1%} (drop: {mid_degradation:.1%})",
            f"End accuracy: {end_acc:.1%} (drop: {end_degradation:.1%})"
        ]

        metrics = {
            'beginning_accuracy': beginning_acc,
            'middle_accuracy': middle_acc,
            'end_accuracy': end_acc,
            'mid_degradation': mid_degradation,
            'end_degradation': end_degradation,
            'max_degradation': max_degradation
        }

        return FailureDetectionResult(
            failure_detected=max_degradation >= self.degradation_threshold,
            confidence=1.0,
            evidence=evidence,
            metrics=metrics
        )


class ReflexionBiasDetector(FailureDetector):
    """
    Detects confirmation bias in self-reflection (Category 5.2: Self-Correction Failures).

    Reflexion bias occurs when:
    1. Agent makes the same mistake multiple times
    2. Self-reflection doesn't identify the error
    3. Reflection reinforces the wrong answer
    """

    def __init__(self, min_repetitions: int = 3):
        super().__init__(
            name="Reflexion Confirmation Bias",
            category="5.2 Self-Correction Reflection Failures"
        )
        self.min_repetitions = min_repetitions

    def detect(self, trace: Dict[str, Any]) -> FailureDetectionResult:
        """Detect repeated wrong answers despite reflection."""
        actions = trace.get('actions', [])

        # Extract answer attempts and reflections
        attempts = []
        reflections = []

        for action in actions:
            if action['type'] == 'answer':
                attempts.append(action['content'])
            elif action['type'] == 'reflection':
                reflections.append(action['content'])

        # Check for repeated wrong answers
        if len(attempts) < self.min_repetitions:
            return FailureDetectionResult(
                failure_detected=False,
                confidence=1.0,
                evidence=["Too few attempts to detect bias"],
                metrics={'attempts': len(attempts)}
            )

        # Find most common answer
        from collections import Counter
        answer_counts = Counter(attempts)
        most_common = answer_counts.most_common(1)[0]
        repeated_answer, count = most_common

        evidence = []
        if count >= self.min_repetitions:
            evidence.append(
                f"Answer '{repeated_answer[:50]}' repeated {count} times"
            )

            # Check if reflections mentioned the repeated answer
            for idx, reflection in enumerate(reflections):
                if repeated_answer[:20] in reflection:
                    evidence.append(
                        f"Reflection {idx} reinforced wrong answer"
                    )

        metrics = {
            'total_attempts': len(attempts),
            'total_reflections': len(reflections),
            'repeated_answer': repeated_answer[:100],
            'repetition_count': count,
            'unique_answers': len(answer_counts)
        }

        return FailureDetectionResult(
            failure_detected=count >= self.min_repetitions,
            confidence=1.0 if count >= self.min_repetitions else 0.5,
            evidence=evidence,
            metrics=metrics
        )


class JSONRecoveryDetector(FailureDetector):
    """
    Detects JSON parsing failures without recovery (Category 6.2: Error Recovery).

    Failure occurs when:
    1. JSON parsing error is encountered
    2. Agent doesn't retry or handle error
    3. Execution halts or continues with corrupted state
    """

    def __init__(self):
        super().__init__(
            name="JSON Non-Recovery",
            category="6.2 Error Recovery Error Handling"
        )

    def detect(self, trace: Dict[str, Any]) -> FailureDetectionResult:
        """Detect JSON errors without recovery attempts."""
        actions = trace.get('actions', [])
        tool_calls = trace.get('tool_calls', [])

        json_errors = []
        recovery_attempts = []

        # Find JSON parsing errors
        for idx, action in enumerate(actions):
            content = action.get('content', '')

            if any(keyword in content.lower() for keyword in [
                'json', 'parse', 'decode', 'invalid', 'syntax error'
            ]):
                # Check if this is an error
                if any(err in content.lower() for err in ['error', 'failed', 'exception']):
                    json_errors.append({
                        'step': idx,
                        'content': content[:200]
                    })

                    # Check for recovery in next few actions
                    recovery_window = actions[idx+1:idx+4]
                    if any('retry' in a['content'].lower() for a in recovery_window):
                        recovery_attempts.append(idx)

        # Also check tool_calls for errors
        for call in tool_calls:
            if call.get('error') and 'json' in call['error'].lower():
                json_errors.append({
                    'tool': call['tool'],
                    'error': call['error'][:200]
                })

        evidence = []
        for err in json_errors:
            evidence.append(f"JSON error at step {err.get('step', 'unknown')}")

        if recovery_attempts:
            evidence.append(f"Recovery attempted {len(recovery_attempts)} times")
        else:
            evidence.append("No recovery attempts detected")

        metrics = {
            'json_errors': len(json_errors),
            'recovery_attempts': len(recovery_attempts),
            'recovery_rate': len(recovery_attempts) / len(json_errors) if json_errors else 1.0
        }

        return FailureDetectionResult(
            failure_detected=len(json_errors) > 0 and len(recovery_attempts) == 0,
            confidence=0.8,  # Medium confidence (heuristic-based)
            evidence=evidence,
            metrics=metrics
        )


# Factory function
def create_detector(
    failure_type: str,
    **kwargs
) -> FailureDetector:
    """
    Create a failure detector instance.

    Args:
        failure_type: Type of failure to detect
        **kwargs: Detector-specific configuration

    Returns:
        FailureDetector instance
    """
    detectors = {
        'tool_fabrication': ToolFabricationDetector,
        'infinite_loop': InfiniteLoopDetector,
        'context_degradation': ContextDegradationDetector,
        'reflexion_bias': ReflexionBiasDetector,
        'json_recovery': JSONRecoveryDetector,
    }

    if failure_type not in detectors:
        raise ValueError(
            f"Unknown failure type: {failure_type}. "
            f"Supported: {list(detectors.keys())}"
        )

    return detectors[failure_type](**kwargs)
