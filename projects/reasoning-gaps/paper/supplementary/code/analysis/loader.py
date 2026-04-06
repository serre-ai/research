"""Load and unify evaluation results from JSON/JSONL files into a DataFrame."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

import pandas as pd


# ---------------------------------------------------------------------------
# Task-to-gap-type mapping (from the formal framework)
# ---------------------------------------------------------------------------

TASK_GAP_TYPE: dict[str, str] = {
    "B1_masked_majority": "Type 1: Sensitivity",
    "B2_nested_boolean": "Type 2: Depth",
    "B3_permutation_composition": "Type 3: Serial",
    "B4_state_machine": "Type 3: Serial",
    "B5_graph_reachability": "Type 2: Depth",
    "B6_longest_increasing_subsequence": "Type 4: Algorithmic",
    "B7_3sat": "Type 5: Intractability",
    "B8_reversal_inference": "Type 6: Architectural",
    "B9_negation_sensitivity": "Type 6: Architectural",
}

# Short labels for compact display
TASK_SHORT_LABELS: dict[str, str] = {
    "B1_masked_majority": "B1: Majority",
    "B2_nested_boolean": "B2: Bool Eval",
    "B3_permutation_composition": "B3: Perm Comp",
    "B4_state_machine": "B4: State Track",
    "B5_graph_reachability": "B5: Graph Reach",
    "B6_longest_increasing_subsequence": "B6: LIS",
    "B7_3sat": "B7: 3-SAT",
    "B8_reversal_inference": "B8: Reversal",
    "B9_negation_sensitivity": "B9: Negation",
}

# Canonical task ordering for tables/plots
TASK_ORDER: list[str] = [
    "B1_masked_majority",
    "B2_nested_boolean",
    "B3_permutation_composition",
    "B4_state_machine",
    "B5_graph_reachability",
    "B6_longest_increasing_subsequence",
    "B7_3sat",
    "B8_reversal_inference",
    "B9_negation_sensitivity",
]

# Gap type ordering
GAP_TYPE_ORDER: list[str] = [
    "Type 1: Sensitivity",
    "Type 2: Depth",
    "Type 3: Serial",
    "Type 4: Algorithmic",
    "Type 5: Intractability",
    "Type 6: Architectural",
]

# Condition ordering
CONDITION_ORDER: list[str] = ["direct", "short_cot", "budget_cot", "tool_use"]

# Condition display labels
CONDITION_LABELS: dict[str, str] = {
    "direct": "Direct",
    "short_cot": "Short CoT",
    "budget_cot": "Budget CoT",
    "tool_use": "Tool Use",
}

# ---------------------------------------------------------------------------
# Model display names and ordering (for paper tables/figures)
# ---------------------------------------------------------------------------

MODEL_DISPLAY_NAMES: dict[str, str] = {
    "claude-haiku-4-5-20251001": "Haiku 4.5",
    "claude-sonnet-4-20250514": "Sonnet 4.6",
    "claude-opus-4-6": "Opus 4.6",
    "gpt-4o": "GPT-4o",
    "gpt-4o-mini": "GPT-4o-m",
    "o3": "o3",
    "meta-llama/llama-3.1-8b-instruct": "Llama 8B",
    "meta-llama/llama-3.1-70b-instruct": "Llama 70B",
    "mistralai/ministral-8b-2512": "Ministral 8B",
    "mistralai/mistral-small-24b-instruct-2501": "Mistral 24B",
    "qwen/qwen-2.5-7b-instruct": "Qwen 7B",
    "qwen/qwen-2.5-72b-instruct": "Qwen 72B",
}

MODEL_DISPLAY_ORDER: list[str] = [
    "Haiku 4.5", "Sonnet 4.6", "Opus 4.6",
    "GPT-4o-m", "GPT-4o", "o3",
    "Llama 8B", "Llama 70B",
    "Ministral 8B", "Mistral 24B",
    "Qwen 7B", "Qwen 72B",
]


def get_display_name(model: str) -> str:
    """Look up the human-readable display name for a model.

    Falls back to the raw model name if no mapping exists.
    """
    return MODEL_DISPLAY_NAMES.get(model, model)

# ---------------------------------------------------------------------------
# Model family extraction
# ---------------------------------------------------------------------------

MODEL_FAMILIES: dict[str, str] = {
    # OpenAI models
    "gpt-4o": "GPT",
    "gpt-4o-mini": "GPT",
    "gpt-4-turbo": "GPT",
    "o3": "GPT",
    "o3-mini": "GPT",
    "o1": "GPT",
    "o1-mini": "GPT",
    # Anthropic models
    "claude-3-opus": "Claude",
    "claude-3-sonnet": "Claude",
    "claude-3-haiku": "Claude",
    "claude-3.5-sonnet": "Claude",
    "claude-3.5-haiku": "Claude",
    "claude-4-opus": "Claude",
    "claude-4-sonnet": "Claude",
    "claude-opus-4-6": "Claude",
    # Meta models
    "llama-3-8b": "Llama",
    "llama-3-70b": "Llama",
    "llama-3.1-8b": "Llama",
    "llama-3.1-70b": "Llama",
    "llama-3.1-405b": "Llama",
    "llama-3.3-70b": "Llama",
    # Mistral models
    "mistral-7b": "Mistral",
    "mistral-large": "Mistral",
    "mixtral-8x7b": "Mistral",
    "ministral-8b-2512": "Mistral",
    "mistral-small-24b-instruct-2501": "Mistral",
    # Qwen models
    "qwen-7b": "Qwen",
    "qwen-72b": "Qwen",
    "qwen-2.5-7b": "Qwen",
    "qwen-2.5-72b": "Qwen",
    "qwen-2.5-7b-instruct": "Qwen",
    "qwen-2.5-72b-instruct": "Qwen",
    # Full-path model names (from OpenRouter)
    "claude-haiku-4-5-20251001": "Claude",
    "claude-sonnet-4-20250514": "Claude",
    "claude-opus-4-6": "Claude",
    "meta-llama/llama-3.1-8b-instruct": "Llama",
    "meta-llama/llama-3.1-70b-instruct": "Llama",
    "mistralai/ministral-8b-2512": "Mistral",
    "mistralai/mistral-small-24b-instruct-2501": "Mistral",
    "qwen/qwen-2.5-7b-instruct": "Qwen",
    "qwen/qwen-2.5-72b-instruct": "Qwen",
}

# Approximate parameter counts (billions) for scale analysis
MODEL_SIZES: dict[str, float | None] = {
    "gpt-4o": None,  # unknown
    "gpt-4o-mini": None,
    "gpt-4-turbo": None,
    "o3": None,
    "o3-mini": None,
    "o1": None,
    "o1-mini": None,
    "claude-3-opus": None,
    "claude-3-sonnet": None,
    "claude-3-haiku": None,
    "claude-3.5-sonnet": None,
    "claude-3.5-haiku": None,
    "claude-4-opus": None,
    "claude-4-sonnet": None,
    "claude-opus-4-6": None,
    "llama-3-8b": 8.0,
    "llama-3-70b": 70.0,
    "llama-3.1-8b": 8.0,
    "llama-3.1-70b": 70.0,
    "llama-3.1-405b": 405.0,
    "llama-3.3-70b": 70.0,
    "mistral-7b": 7.0,
    "mistral-large": 123.0,
    "mixtral-8x7b": 46.7,
    "qwen-7b": 7.0,
    "qwen-72b": 72.0,
    "qwen-2.5-7b": 7.0,
    "qwen-2.5-72b": 72.0,
    # Full-path model names (from OpenRouter/eval runner)
    "claude-haiku-4-5-20251001": None,
    "claude-sonnet-4-20250514": None,
    "meta-llama/llama-3.1-8b-instruct": 8.0,
    "meta-llama/llama-3.1-70b-instruct": 70.0,
    "mistralai/ministral-8b-2512": 8.0,
    "mistralai/mistral-small-24b-instruct-2501": 24.0,
    "qwen/qwen-2.5-7b-instruct": 7.0,
    "qwen/qwen-2.5-72b-instruct": 72.0,
}


def _extract_model_family(model_name: str) -> str:
    """Extract model family from model name string.

    Handles formats like 'openai:gpt-4o', 'anthropic:claude-3-opus',
    or bare names like 'gpt-4o'.
    """
    # Strip provider prefix if present
    if ":" in model_name:
        model_name = model_name.split(":", 1)[1]

    # Direct lookup
    if model_name in MODEL_FAMILIES:
        return MODEL_FAMILIES[model_name]

    # Pattern matching fallback
    name_lower = model_name.lower()
    if "gpt" in name_lower or name_lower.startswith("o1") or name_lower.startswith("o3"):
        return "GPT"
    if "claude" in name_lower:
        return "Claude"
    if "llama" in name_lower:
        return "Llama"
    if "mistral" in name_lower or "mixtral" in name_lower:
        return "Mistral"
    if "qwen" in name_lower:
        return "Qwen"

    return "Other"


def _extract_model_size(model_name: str) -> float | None:
    """Extract approximate model size in billions of parameters."""
    if ":" in model_name:
        model_name = model_name.split(":", 1)[1]

    if model_name in MODEL_SIZES:
        return MODEL_SIZES[model_name]

    # Try to extract number from name (e.g., 'llama-3-70b' -> 70)
    match = re.search(r"(\d+)[bB]", model_name)
    if match:
        return float(match.group(1))

    return None


def _parse_json_file(path: Path) -> list[dict]:
    """Parse a single JSON results file.

    Expected format:
    {
        "summary": {...},
        "results": [{"instance_id": ..., "task": ..., ...}, ...]
    }
    """
    with open(path) as f:
        data = json.load(f)

    if "results" in data:
        return data["results"]
    elif isinstance(data, list):
        return data
    else:
        return [data]


def _parse_jsonl_file(path: Path) -> list[dict]:
    """Parse a JSONL checkpoint file (one JSON object per line)."""
    results = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def _strip_provider_prefix(model_name: str) -> str:
    """Strip provider prefix (e.g., 'openai:', 'anthropic:') from model name."""
    if ":" in model_name:
        return model_name.split(":", 1)[1]
    return model_name


def _extract_condition_from_filename(filename: str, record_condition: str) -> str:
    """Extract condition from filename, preserving budget multiplier suffixes.

    Budget sweep files are named like 'model_B2_budget_cot_0.25x.json' but the
    condition field inside the JSON is just 'budget_cot'. This function extracts
    the full condition including the multiplier suffix from the filename.
    """
    # Match budget_cot_<number>x pattern in filename
    match = re.search(r"budget_cot_(\d+\.?\d*)x", filename)
    if match:
        return f"budget_cot_{match.group(1)}x"
    return record_condition


def _normalize_record(record: dict, source_filename: str = "") -> dict:
    """Normalize a single result record to canonical column names."""
    # Handle nested metadata
    metadata = record.get("metadata", {})
    is_refusal = metadata.get("is_refusal", False) if isinstance(metadata, dict) else False

    condition = record.get("condition", "")
    if source_filename:
        condition = _extract_condition_from_filename(source_filename, condition)

    return {
        "instance_id": record.get("instance_id", ""),
        "task": record.get("task", ""),
        "difficulty": int(record.get("difficulty", 0)),
        "condition": condition,
        "model": _strip_provider_prefix(record.get("model", "")),
        "extracted_answer": str(record.get("extracted_answer", "")),
        "ground_truth": str(record.get("ground_truth", "")),
        "correct": bool(record.get("correct", False)),
        "latency_ms": float(record.get("latency_ms", 0.0)),
        "is_refusal": is_refusal,
    }


def load_results(results_dir: str) -> pd.DataFrame:
    """Load all evaluation results from a directory into a unified DataFrame.

    Scans for .json and .jsonl files, parses each, and returns a single
    DataFrame with derived columns for gap type, model family, and model size.

    Args:
        results_dir: Path to directory containing result files.

    Returns:
        DataFrame with columns: instance_id, task, difficulty, condition,
        model, extracted_answer, ground_truth, correct, latency_ms,
        is_refusal, gap_type, model_family, model_size.
    """
    results_path = Path(results_dir)
    if not results_path.exists():
        raise FileNotFoundError(f"Results directory not found: {results_dir}")

    all_records: list[dict] = []

    # Collect all JSON files
    json_files = sorted(results_path.glob("**/*.json"))
    jsonl_files = sorted(results_path.glob("**/*.jsonl"))

    for path in json_files:
        try:
            records = _parse_json_file(path)
            all_records.extend(
                _normalize_record(r, source_filename=path.name) for r in records
            )
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Skipping %s: %s", path, exc)

    for path in jsonl_files:
        try:
            records = _parse_jsonl_file(path)
            all_records.extend(
                _normalize_record(r, source_filename=path.name) for r in records
            )
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Skipping %s: %s", path, exc)

    if not all_records:
        return pd.DataFrame(columns=[
            "instance_id", "task", "difficulty", "condition", "model",
            "extracted_answer", "ground_truth", "correct", "latency_ms",
            "is_refusal", "gap_type", "model_family", "model_size",
        ])

    df = pd.DataFrame(all_records)

    # Add derived columns
    df["gap_type"] = df["task"].map(TASK_GAP_TYPE).fillna("Unknown")
    df["model_family"] = df["model"].apply(_extract_model_family)
    df["model_size"] = df["model"].apply(_extract_model_size)

    # Sort for consistent ordering
    df = df.sort_values(["task", "model", "condition", "difficulty", "instance_id"])
    df = df.reset_index(drop=True)

    return df
