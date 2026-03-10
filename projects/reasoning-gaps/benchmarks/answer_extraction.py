"""Robust answer extraction for ReasonGap benchmark evaluation.

Extracts final answers from model responses across all 9 task types (B1-B9),
handling markdown formatting, chain-of-thought prefixes, trailing punctuation,
self-correction, and refusal detection.
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Mapping from spelled-out number words to digits
WORD_TO_NUM: dict[str, str] = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20",
}

# Common prefixes models use before stating their answer
ANSWER_PREFIXES: list[str] = [
    "final answer:",
    "the final answer is",
    "answer:",
    "the answer is:",
    "the answer is",
    "result:",
    "the result is",
    "therefore,",
    "therefore:",
    "so,",
    "so:",
    "thus,",
    "thus:",
    "hence,",
    "hence:",
    "in conclusion,",
    "my answer is",
    "my answer:",
    "output:",
    "the output is",
]

# Phrases that indicate a refusal or inability to answer
REFUSAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bi cannot\b", re.IGNORECASE),
    re.compile(r"\bi can't\b", re.IGNORECASE),
    re.compile(r"\bi'm unable\b", re.IGNORECASE),
    re.compile(r"\bi am unable\b", re.IGNORECASE),
    re.compile(r"\bi don't know\b", re.IGNORECASE),
    re.compile(r"\bi do not know\b", re.IGNORECASE),
    re.compile(r"\bi'm not sure\b", re.IGNORECASE),
    re.compile(r"\bi am not sure\b", re.IGNORECASE),
    re.compile(r"\bit's impossible to determine\b", re.IGNORECASE),
    re.compile(r"\bit is impossible to determine\b", re.IGNORECASE),
    re.compile(r"\bcannot determine\b", re.IGNORECASE),
    re.compile(r"\bcannot be determined\b", re.IGNORECASE),
    re.compile(r"\bnot enough information\b", re.IGNORECASE),
    re.compile(r"\binsufficient information\b", re.IGNORECASE),
]

# Task type classification
BINARY_TASKS = {"B1"}        # "0" or "1"
BOOLEAN_TASKS = {"B2", "B9"} # "True" or "False"
YESNO_TASKS = {"B5", "B7"}   # "Yes" or "No"
NUMERIC_TASKS = {"B3", "B6"} # integer answers
LETTER_TASKS = {"B4"}        # single uppercase letter (A-D)
ENTITY_TASKS = {"B8"}        # fictional country name


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def _strip_markdown(text: str) -> str:
    """Remove common markdown formatting from text.

    Handles bold (**text**), italic (*text*), inline code (`text`),
    and code blocks (```text```).
    """
    # Remove code blocks first (``` ... ```)
    text = re.sub(r"```[^`]*```", lambda m: m.group(0).strip("`").strip(), text)
    # Remove bold (**text** or __text__)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    # Remove italic (*text* or _text_) -- be careful not to match within words
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", text)
    # Remove inline code (`text`)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text


def _strip_answer_prefixes(text: str) -> str:
    """Remove common answer prefixes (case-insensitive)."""
    lower = text.lower()
    for prefix in ANSWER_PREFIXES:
        if lower.startswith(prefix):
            text = text[len(prefix):].strip()
            lower = text.lower()
    return text


def _strip_trailing_punctuation(text: str) -> str:
    """Remove trailing punctuation marks."""
    return text.rstrip(".!;,:")


def _get_last_nonempty_line(text: str) -> str:
    """Return the last non-empty line from a multi-line string."""
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    return lines[-1] if lines else ""


def preprocess(response: str) -> str:
    """Apply general preprocessing to a model response.

    Steps:
    1. Strip leading/trailing whitespace
    2. Remove markdown formatting
    3. Handle empty responses
    4. Take the last non-empty line (for CoT responses)
    5. Strip answer prefixes
    6. Strip trailing punctuation
    """
    text = response.strip()
    if not text:
        return ""

    text = _strip_markdown(text)

    # Take last non-empty line
    text = _get_last_nonempty_line(text)
    if not text:
        return ""

    # Strip answer prefixes
    text = _strip_answer_prefixes(text)

    # Strip trailing punctuation
    text = _strip_trailing_punctuation(text)

    return text.strip()


# ---------------------------------------------------------------------------
# Refusal detection
# ---------------------------------------------------------------------------

def is_refusal(response: str) -> bool:
    """Detect whether a model response is a refusal or inability to answer.

    Returns True for:
    - Empty or whitespace-only responses
    - Responses containing refusal phrases like "I cannot", "I don't know", etc.
    """
    text = response.strip()
    if not text:
        return True

    for pattern in REFUSAL_PATTERNS:
        if pattern.search(text):
            return True

    return False


# ---------------------------------------------------------------------------
# Task-specific extractors
# ---------------------------------------------------------------------------

def _extract_binary(text: str) -> str:
    """Extract answer for B1 (binary: '0' or '1').

    Handles:
    - Direct digits: "0", "1"
    - Spelled out: "zero", "one"
    - Embedded: "The majority is 1" -> "1"
    """
    preprocessed = preprocess(text)
    if not preprocessed:
        return ""

    # Check for spelled-out words first (case-insensitive)
    lower = preprocessed.lower()
    if re.search(r"\bzero\b", lower):
        return "0"
    if re.search(r"\bone\b", lower):
        return "1"

    # Find first 0 or 1 digit in the cleaned text
    match = re.search(r"\b([01])\b", preprocessed)
    if match:
        return match.group(1)

    # Fallback: any 0 or 1 character
    match = re.search(r"[01]", preprocessed)
    if match:
        return match.group(0)

    return preprocessed


def _extract_boolean(text: str) -> str:
    """Extract answer for B2, B9 (boolean: 'True' or 'False').

    Handles:
    - Case variants: "true", "TRUE", "True"
    - Abbreviations: "T", "F"
    - Embedded: "yes it's true" -> "True"
    """
    preprocessed = preprocess(text)
    if not preprocessed:
        return ""

    lower = preprocessed.lower().strip()

    # Direct match
    if lower in ("true", "t"):
        return "True"
    if lower in ("false", "f"):
        return "False"

    # Search for true/false keywords in the text
    # Look for the last occurrence to handle self-correction
    true_pos = -1
    false_pos = -1
    for m in re.finditer(r"\btrue\b", lower):
        true_pos = m.start()
    for m in re.finditer(r"\bfalse\b", lower):
        false_pos = m.start()

    if true_pos >= 0 or false_pos >= 0:
        if true_pos > false_pos:
            return "True"
        return "False"

    # Handle "yes it's true" / "no it's false" patterns
    if re.search(r"\byes\b", lower):
        return "True"
    if re.search(r"\bno\b", lower):
        return "False"

    return preprocessed


def _extract_yesno(text: str) -> str:
    """Extract answer for B5, B7 (yes/no).

    Handles:
    - Case variants: "yes", "YES", "Yes"
    - Abbreviations: "Y", "N"
    - Embedded: "No, there is no path." -> "No"
    """
    preprocessed = preprocess(text)
    if not preprocessed:
        return ""

    lower = preprocessed.lower().strip()

    # Direct match
    if lower in ("yes", "y"):
        return "Yes"
    if lower in ("no", "n"):
        return "No"

    # Search for yes/no keywords -- take last occurrence for self-correction
    yes_pos = -1
    no_pos = -1
    for m in re.finditer(r"\byes\b", lower):
        yes_pos = m.start()
    for m in re.finditer(r"\bno\b", lower):
        no_pos = m.start()

    if yes_pos >= 0 or no_pos >= 0:
        if yes_pos > no_pos:
            return "Yes"
        return "No"

    return preprocessed


def _extract_numeric(text: str) -> str:
    """Extract answer for B3, B6 (numeric).

    Handles:
    - Direct numbers: "3", "12"
    - Prefixed: "Position 3" -> "3", "The length is 4" -> "4"
    - Spelled out: "three" -> "3"
    """
    preprocessed = preprocess(text)
    if not preprocessed:
        return ""

    lower = preprocessed.lower()

    # Check spelled-out numbers first
    for word, digit in WORD_TO_NUM.items():
        if re.search(r"\b" + word + r"\b", lower):
            return digit

    # Find the last number in the text (to handle self-correction)
    matches = list(re.finditer(r"\b(\d+)\b", preprocessed))
    if matches:
        return matches[-1].group(1)

    return preprocessed


def _extract_letter(text: str) -> str:
    """Extract answer for B4 (single uppercase letter A-D, state name).

    Handles:
    - Direct: "B"
    - Prefixed: "State B" -> "B", "The final state is C" -> "C"
    """
    preprocessed = preprocess(text)
    if not preprocessed:
        return ""

    # Look for patterns like "state X" or "is X"
    match = re.search(r"\bstate\s+([A-Da-d])\b", preprocessed, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    # Look for "is X" at the end
    match = re.search(r"\bis\s+([A-Da-d])\b", preprocessed, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    # Find the last standalone uppercase letter A-D
    matches = list(re.finditer(r"\b([A-Da-d])\b", preprocessed))
    if matches:
        return matches[-1].group(1).upper()

    # Fallback: if preprocessed is a single character
    if len(preprocessed) == 1 and preprocessed.upper() in "ABCD":
        return preprocessed.upper()

    return preprocessed


def _extract_entity(text: str, expected: str | None = None) -> str:
    """Extract answer for B8 (fictional country name).

    Handles:
    - Direct: "Lunheim"
    - Embedded: "The country is Lunheim." -> "Lunheim"
    - Case-insensitive matching against expected answer

    Args:
        text: Raw model response.
        expected: The ground truth answer for case-insensitive matching.
    """
    preprocessed = preprocess(text)
    if not preprocessed:
        return ""

    # If we have an expected answer, do case-insensitive search in the
    # original response (not just last line) for maximum recall
    if expected:
        # Search in the full response text (after markdown stripping)
        full_text = _strip_markdown(text.strip())
        pattern = re.compile(re.escape(expected), re.IGNORECASE)
        match = pattern.search(full_text)
        if match:
            return expected  # Return the canonical form

    # Fallback: return the preprocessed last line, trying to extract a
    # capitalized word that looks like a proper noun
    words = preprocessed.split()
    # Look for capitalized words (likely proper nouns)
    proper_nouns = [w for w in words if w and w[0].isupper() and w.isalpha()]
    if proper_nouns:
        # Return the last proper noun (most likely to be the answer)
        return proper_nouns[-1]

    return preprocessed


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------

def extract_answer(response: str, task: str, expected: str | None = None) -> str:
    """Extract the final answer from a model response.

    Dispatches to task-specific extractors based on the task type.

    Args:
        response: Raw model response text.
        task: Task identifier (e.g., "B1", "B2", ..., "B9").
        expected: Optional ground truth (used for entity matching in B8).

    Returns:
        Extracted and normalized answer string, or "" if extraction fails.
    """
    if not response or not response.strip():
        return ""

    task_upper = task.upper()

    if task_upper in BINARY_TASKS:
        return _extract_binary(response)
    elif task_upper in BOOLEAN_TASKS:
        return _extract_boolean(response)
    elif task_upper in YESNO_TASKS:
        return _extract_yesno(response)
    elif task_upper in NUMERIC_TASKS:
        return _extract_numeric(response)
    elif task_upper in LETTER_TASKS:
        return _extract_letter(response)
    elif task_upper in ENTITY_TASKS:
        return _extract_entity(response, expected=expected)
    else:
        # Unknown task: fall back to generic preprocessing
        return preprocess(response)
