"""Comprehensive tests for answer_extraction module.

Covers all 9 task types (B1-B9), edge cases, and refusal detection.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the parent benchmarks directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from answer_extraction import extract_answer, is_refusal


# ===================================================================
# B1 — Binary ("0" or "1")
# ===================================================================

class TestB1Binary:
    """B1: Masked majority — answer is '0' or '1'."""

    def test_direct_zero(self):
        assert extract_answer("0", "B1") == "0"

    def test_direct_one(self):
        assert extract_answer("1", "B1") == "1"

    def test_majority_is_one(self):
        assert extract_answer("The majority is 1", "B1") == "1"

    def test_markdown_bold_zero(self):
        assert extract_answer("**0**", "B1") == "0"

    def test_answer_prefix_with_punctuation(self):
        assert extract_answer("After counting, the answer is 0.", "B1") == "0"

    def test_parenthetical_explanation(self):
        assert extract_answer("1 (since there are more 1s)", "B1") == "1"

    def test_spelled_out_zero(self):
        assert extract_answer("zero", "B1") == "0"

    def test_spelled_out_one(self):
        assert extract_answer("one", "B1") == "1"

    def test_cot_multiline(self):
        response = "Let me count...\nThere are 5 ones and 3 zeros.\n\n0"
        assert extract_answer(response, "B1") == "0"

    def test_inline_code(self):
        assert extract_answer("`1`", "B1") == "1"


# ===================================================================
# B2 — Boolean ("True" or "False")
# ===================================================================

class TestB2Boolean:
    """B2: Parity check — answer is 'True' or 'False'."""

    def test_direct_true(self):
        assert extract_answer("True", "B2") == "True"

    def test_direct_false(self):
        assert extract_answer("False", "B2") == "False"

    def test_markdown_bold_false(self):
        assert extract_answer("**False**", "B2") == "False"

    def test_lowercase_true(self):
        assert extract_answer("true", "B2") == "True"

    def test_uppercase_false(self):
        assert extract_answer("FALSE", "B2") == "False"

    def test_result_prefix(self):
        assert extract_answer("The result is True.", "B2") == "True"

    def test_cot_with_answer_last_line(self):
        response = "Let me evaluate...\n\nTrue"
        assert extract_answer(response, "B2") == "True"

    def test_abbreviation_t(self):
        assert extract_answer("T", "B2") == "True"

    def test_abbreviation_f(self):
        assert extract_answer("F", "B2") == "False"

    def test_all_caps_true(self):
        assert extract_answer("TRUE", "B2") == "True"


# ===================================================================
# B9 — Boolean ("True" or "False") — same type as B2
# ===================================================================

class TestB9Boolean:
    """B9: Quantifier scope — answer is 'True' or 'False'."""

    def test_direct_true(self):
        assert extract_answer("True", "B9") == "True"

    def test_false_with_explanation(self):
        assert extract_answer("False, because not all elements satisfy the condition", "B9") == "False"

    def test_answer_prefix(self):
        assert extract_answer("Answer: True", "B9") == "True"

    def test_final_answer_prefix(self):
        assert extract_answer("Final answer: False", "B9") == "False"

    def test_cot_self_correction(self):
        response = "Initially I think True.\n\nWait, let me reconsider.\n\nFalse"
        assert extract_answer(response, "B9") == "False"


# ===================================================================
# B3 — Numeric (position, 1-5)
# ===================================================================

class TestB3Numeric:
    """B3: Hidden permutation — answer is an integer (position 1-5)."""

    def test_direct_number(self):
        assert extract_answer("3", "B3") == "3"

    def test_position_prefix(self):
        assert extract_answer("Position 4", "B3") == "4"

    def test_markdown_bold(self):
        assert extract_answer("**5**", "B3") == "5"

    def test_answer_is_prefix(self):
        assert extract_answer("The answer is 2.", "B3") == "2"

    def test_after_computation(self):
        assert extract_answer("After computation, 1", "B3") == "1"

    def test_spelled_out_three(self):
        assert extract_answer("three", "B3") == "3"

    def test_spelled_out_five(self):
        assert extract_answer("five", "B3") == "5"

    def test_cot_multiline(self):
        response = "Comparing the elements...\nPosition 1 is a=5.\nPosition 2 is b=3.\n\n2"
        assert extract_answer(response, "B3") == "2"


# ===================================================================
# B6 — Numeric (LIS length)
# ===================================================================

class TestB6Numeric:
    """B6: Longest increasing subsequence — answer is a number."""

    def test_direct_number(self):
        assert extract_answer("7", "B6") == "7"

    def test_length_prefix(self):
        assert extract_answer("The length is 4.", "B6") == "4"

    def test_large_number(self):
        assert extract_answer("After computation, 12", "B6") == "12"

    def test_lis_label(self):
        assert extract_answer("The LIS length is 5.", "B6") == "5"

    def test_self_correction(self):
        response = "3\n\nWait, let me reconsider...\n\n4"
        assert extract_answer(response, "B6") == "4"

    def test_spelled_out_seven(self):
        assert extract_answer("seven", "B6") == "7"


# ===================================================================
# B4 — Letter (state name, A-D)
# ===================================================================

class TestB4Letter:
    """B4: Finite automaton — answer is a single letter A-D."""

    def test_direct_b(self):
        assert extract_answer("B", "B4") == "B"

    def test_final_state_is(self):
        assert extract_answer("The final state is C.", "B4") == "C"

    def test_state_prefix(self):
        assert extract_answer("State A", "B4") == "A"

    def test_markdown_bold(self):
        assert extract_answer("**D**", "B4") == "D"

    def test_lowercase_letter(self):
        assert extract_answer("b", "B4") == "B"

    def test_answer_prefix(self):
        assert extract_answer("Answer: C", "B4") == "C"

    def test_cot_with_states(self):
        response = "Starting at A, input 1 -> B, input 0 -> C.\n\nC"
        assert extract_answer(response, "B4") == "C"


# ===================================================================
# B5 — Yes/No
# ===================================================================

class TestB5YesNo:
    """B5: Reachability — answer is 'Yes' or 'No'."""

    def test_direct_yes(self):
        assert extract_answer("Yes", "B5") == "Yes"

    def test_direct_no(self):
        assert extract_answer("No", "B5") == "No"

    def test_no_with_explanation(self):
        assert extract_answer("No, there is no path.", "B5") == "No"

    def test_markdown_bold_yes(self):
        assert extract_answer("**Yes**", "B5") == "Yes"

    def test_lowercase_yes(self):
        assert extract_answer("yes", "B5") == "Yes"

    def test_uppercase_no(self):
        assert extract_answer("NO", "B5") == "No"

    def test_yes_with_detail(self):
        assert extract_answer("Yes, there is a path from 1 to 5.", "B5") == "Yes"

    def test_abbreviation_y(self):
        assert extract_answer("Y", "B5") == "Yes"

    def test_abbreviation_n(self):
        assert extract_answer("N", "B5") == "No"


# ===================================================================
# B7 — Yes/No
# ===================================================================

class TestB7YesNo:
    """B7: Graph property — answer is 'Yes' or 'No'."""

    def test_direct_yes(self):
        assert extract_answer("Yes", "B7") == "Yes"

    def test_answer_prefix_no(self):
        assert extract_answer("The answer is: No", "B7") == "No"

    def test_therefore_yes(self):
        assert extract_answer("Therefore, yes", "B7") == "Yes"

    def test_cot_with_answer(self):
        response = "Checking the graph...\nEdge (1,2) exists.\nEdge (2,3) exists.\n\nYes"
        assert extract_answer(response, "B7") == "Yes"

    def test_self_correction(self):
        response = "Yes\n\nActually, no.\n\nNo"
        assert extract_answer(response, "B7") == "No"


# ===================================================================
# B8 — Entity name (fictional country)
# ===================================================================

class TestB8Entity:
    """B8: Fictional geography — answer is a country name like 'Lunheim'."""

    def test_direct_name(self):
        assert extract_answer("Lunheim", "B8", expected="Lunheim") == "Lunheim"

    def test_embedded_in_sentence(self):
        assert extract_answer("The country is Lunheim.", "B8", expected="Lunheim") == "Lunheim"

    def test_case_insensitive(self):
        assert extract_answer("lunheim", "B8", expected="Lunheim") == "Lunheim"

    def test_mixed_case(self):
        assert extract_answer("LUNHEIM", "B8", expected="Lunheim") == "Lunheim"

    def test_in_explanation(self):
        assert extract_answer("It must be Lunheim, since...", "B8", expected="Lunheim") == "Lunheim"

    def test_different_name(self):
        assert extract_answer("Valdris", "B8", expected="Valdris") == "Valdris"

    def test_name_in_long_response(self):
        response = (
            "Looking at the clues:\n"
            "- The capital is in the north\n"
            "- The currency is the Krone\n\n"
            "The country is Valdris."
        )
        assert extract_answer(response, "B8", expected="Valdris") == "Valdris"

    def test_markdown_bold_name(self):
        assert extract_answer("**Lunheim**", "B8", expected="Lunheim") == "Lunheim"

    def test_no_expected_fallback(self):
        """Without expected answer, extract best-guess proper noun."""
        result = extract_answer("Lunheim", "B8")
        assert result == "Lunheim"


# ===================================================================
# Edge cases
# ===================================================================

class TestEdgeCases:
    """Edge cases and tricky inputs."""

    def test_empty_string(self):
        assert extract_answer("", "B1") == ""

    def test_only_whitespace(self):
        assert extract_answer("   \n\n  ", "B2") == ""

    def test_none_like_empty(self):
        """Empty response returns empty string for all tasks."""
        for task in ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]:
            assert extract_answer("", task) == ""

    def test_trailing_whitespace_newlines(self):
        assert extract_answer("True\n\n", "B2") == "True"

    def test_leading_whitespace(self):
        assert extract_answer("  Yes  ", "B5") == "Yes"

    def test_markdown_code_block(self):
        response = "```\nTrue\n```"
        assert extract_answer(response, "B2") == "True"

    def test_multiple_lines_self_correction_numeric(self):
        """Self-correction: should take the last valid answer."""
        response = "3\n\nWait, let me reconsider...\n\n4"
        assert extract_answer(response, "B6") == "4"

    def test_multiple_lines_self_correction_boolean(self):
        response = "True\n\nActually, upon reflection...\n\nFalse"
        assert extract_answer(response, "B2") == "False"

    def test_very_long_cot_response(self):
        """Long chain-of-thought with answer at the end."""
        cot = "Let me think about this step by step.\n" * 50
        cot += "\nAfter careful analysis, I conclude that the answer is 3."
        assert extract_answer(cot, "B3") == "3"

    def test_answer_with_colon(self):
        assert extract_answer("Answer: True", "B2") == "True"

    def test_final_answer_with_colon(self):
        assert extract_answer("Final answer: No", "B5") == "No"

    def test_therefore_prefix(self):
        assert extract_answer("Therefore, 5", "B6") == "5"

    def test_so_prefix(self):
        assert extract_answer("So, True", "B2") == "True"

    def test_thus_prefix(self):
        assert extract_answer("Thus, B", "B4") == "B"

    def test_inline_code_answer(self):
        assert extract_answer("`False`", "B9") == "False"

    def test_task_case_insensitive(self):
        """Task identifiers should be case-insensitive."""
        assert extract_answer("True", "b2") == "True"
        assert extract_answer("3", "b3") == "3"

    def test_unknown_task_fallback(self):
        """Unknown task type falls back to generic preprocessing."""
        result = extract_answer("The answer is 42.", "B99")
        assert result == "42"


# ===================================================================
# Refusal detection
# ===================================================================

class TestRefusalDetection:
    """Test is_refusal() function."""

    def test_i_cannot(self):
        assert is_refusal("I cannot determine the answer") is True

    def test_i_cant(self):
        assert is_refusal("I can't figure this out") is True

    def test_im_unable(self):
        assert is_refusal("I'm unable to solve this problem") is True

    def test_i_dont_know(self):
        assert is_refusal("I don't know the answer") is True

    def test_im_not_sure(self):
        assert is_refusal("I'm not sure about this") is True

    def test_impossible_to_determine(self):
        assert is_refusal("It's impossible to determine the correct answer") is True

    def test_empty_string_is_refusal(self):
        assert is_refusal("") is True

    def test_whitespace_only_is_refusal(self):
        assert is_refusal("   \n  ") is True

    def test_normal_answer_not_refusal(self):
        assert is_refusal("True") is False

    def test_numeric_answer_not_refusal(self):
        assert is_refusal("3") is False

    def test_cot_with_answer_not_refusal(self):
        assert is_refusal("Let me think...\n\nThe answer is True") is False

    def test_cannot_determine(self):
        assert is_refusal("This cannot be determined from the given information") is True

    def test_not_enough_information(self):
        assert is_refusal("There is not enough information to answer") is True


# ===================================================================
# Integration: extract_answer with refusal
# ===================================================================

class TestExtractionWithRefusal:
    """Verify that refusals produce empty extraction."""

    def test_refusal_returns_empty_b1(self):
        response = ""
        assert extract_answer(response, "B1") == ""
        assert is_refusal(response) is True

    def test_refusal_returns_empty_b2(self):
        response = "   "
        assert extract_answer(response, "B2") == ""
        assert is_refusal(response) is True

    def test_non_refusal_extracts_correctly(self):
        response = "True"
        assert extract_answer(response, "B2") == "True"
        assert is_refusal(response) is False
