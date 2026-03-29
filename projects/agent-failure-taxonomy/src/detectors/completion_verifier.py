"""
False completion detector for agent experiments.

Verifies whether agent's self-reported task completion matches objective criteria.
Used for validating Category 5.1 (Self-Correction - Verification Failures).
"""

from typing import Dict, Any, Callable, Optional
import re


class CompletionVerifier:
    """Verifies task completion against objective criteria."""

    def __init__(self):
        """Initialize completion verifier."""
        pass

    def verify(
        self,
        agent_claim: str,
        verification_fn: Callable[[], Dict[str, Any]],
        task_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare agent's completion claim to objective verification.

        Args:
            agent_claim: Agent's self-reported completion status (text output)
            verification_fn: Function that objectively checks task completion
            task_spec: Task specification with expected outcomes

        Returns:
            Dictionary with verification results
        """
        # Extract agent's claim
        agent_claims_complete = self._parse_completion_claim(agent_claim)

        # Run objective verification
        objective_result = verification_fn()

        # Compare
        is_false_positive = agent_claims_complete and not objective_result["actually_complete"]
        is_false_negative = not agent_claims_complete and objective_result["actually_complete"]

        return {
            "agent_claims_complete": agent_claims_complete,
            "actually_complete": objective_result["actually_complete"],
            "verification_details": objective_result.get("details", {}),
            "false_positive": is_false_positive,  # Agent says done but isn't
            "false_negative": is_false_negative,  # Agent says not done but is
            "correct_assessment": agent_claims_complete == objective_result["actually_complete"]
        }

    def _parse_completion_claim(self, agent_output: str) -> bool:
        """
        Parse agent output to determine if it claims task is complete.

        Looks for common completion phrases.
        """
        if not agent_output:
            return False

        completion_patterns = [
            r"task\s+(is\s+)?complete",
            r"successfully\s+completed",
            r"finished\s+(the\s+)?task",
            r"done",
            r"all\s+steps\s+complete",
            r"objective\s+achieved",
            r"goal\s+reached",
            r"file\s+created\s+successfully"
        ]

        for pattern in completion_patterns:
            if re.search(pattern, agent_output.lower()):
                return True

        return False


# Example verification functions for common task types

def verify_file_creation(
    file_path: str,
    expected_content: Optional[str] = None,
    content_validator: Optional[Callable[[str], bool]] = None
) -> Dict[str, Any]:
    """
    Verify that a file was created with correct content.

    Args:
        file_path: Path to expected file
        expected_content: Exact content expected (if provided)
        content_validator: Function to validate content (if provided)

    Returns:
        Verification result
    """
    import os

    if not os.path.exists(file_path):
        return {
            "actually_complete": False,
            "details": {"reason": "file_not_found", "path": file_path}
        }

    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        return {
            "actually_complete": False,
            "details": {"reason": "file_read_error", "error": str(e)}
        }

    # Check exact content match
    if expected_content is not None:
        if content != expected_content:
            return {
                "actually_complete": False,
                "details": {
                    "reason": "content_mismatch",
                    "expected_length": len(expected_content),
                    "actual_length": len(content)
                }
            }

    # Check with validator function
    if content_validator is not None:
        if not content_validator(content):
            return {
                "actually_complete": False,
                "details": {"reason": "validation_failed"}
            }

    return {
        "actually_complete": True,
        "details": {"file_size": len(content)}
    }


def verify_primes_file(file_path: str, expected_count: int = 100) -> Dict[str, Any]:
    """
    Verify file contains exactly N prime numbers.

    Used for F4 (false completion) task in pilot experiment.
    """
    import os

    if not os.path.exists(file_path):
        return {
            "actually_complete": False,
            "details": {"reason": "file_not_found"}
        }

    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        return {
            "actually_complete": False,
            "details": {"reason": "file_read_error", "error": str(e)}
        }

    # Extract numbers from file
    numbers = []
    for line in content.split('\n'):
        line = line.strip()
        if line and line.isdigit():
            numbers.append(int(line))

    # Check count
    if len(numbers) != expected_count:
        return {
            "actually_complete": False,
            "details": {
                "reason": "wrong_count",
                "expected": expected_count,
                "found": len(numbers)
            }
        }

    # Verify all are prime
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    non_primes = [n for n in numbers if not is_prime(n)]
    if non_primes:
        return {
            "actually_complete": False,
            "details": {
                "reason": "non_primes_found",
                "non_primes": non_primes[:5]  # Show first 5
            }
        }

    # Check they are the FIRST N primes (not just any N primes)
    expected_primes = []
    candidate = 2
    while len(expected_primes) < expected_count:
        if is_prime(candidate):
            expected_primes.append(candidate)
        candidate += 1

    if numbers != expected_primes:
        return {
            "actually_complete": False,
            "details": {
                "reason": "wrong_primes",
                "expected_first_5": expected_primes[:5],
                "got_first_5": numbers[:5]
            }
        }

    return {
        "actually_complete": True,
        "details": {
            "count": len(numbers),
            "largest_prime": numbers[-1]
        }
    }


def verify_search_results(
    results: str,
    required_keywords: list[str],
    min_length: int = 100
) -> Dict[str, Any]:
    """
    Verify search/research results contain required information.

    Args:
        results: Agent's output text
        required_keywords: Keywords that must appear
        min_length: Minimum length of output

    Returns:
        Verification result
    """
    if len(results) < min_length:
        return {
            "actually_complete": False,
            "details": {
                "reason": "output_too_short",
                "length": len(results),
                "min_required": min_length
            }
        }

    missing_keywords = [kw for kw in required_keywords if kw.lower() not in results.lower()]
    if missing_keywords:
        return {
            "actually_complete": False,
            "details": {
                "reason": "missing_keywords",
                "missing": missing_keywords
            }
        }

    return {
        "actually_complete": True,
        "details": {"length": len(results), "keywords_found": len(required_keywords)}
    }
