#!/usr/bin/env python3
"""ReasonGap Benchmark Suite -- Batch Evaluation Runner.

Orchestrates the full 216K evaluation across all models, tasks, and conditions
with a single command. Designed to run unattended for 72+ hours with crash
recovery via the checkpoint/resume system.

Usage:
    # Full run (all models, all tasks, all conditions)
    python run_evaluation.py --all

    # Subset run
    python run_evaluation.py --models anthropic:claude-haiku-4-5-20251001 openai:gpt-4o-mini --tasks B1 B2 B9

    # Dry run (estimate only)
    python run_evaluation.py --all --dry-run

    # Resume after crash (automatic via checkpoint system)
    python run_evaluation.py --all

    # Skip confirmation prompt
    python run_evaluation.py --all --yes
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from io_utils import atomic_json_write

# ---------------------------------------------------------------------------
# Evaluation matrix
# ---------------------------------------------------------------------------

MODELS: dict[str, dict[str, str]] = {
    # Proprietary (API)
    "anthropic:claude-haiku-4-5-20251001": {"family": "claude", "size": "small"},
    "anthropic:claude-sonnet-4-20250514": {"family": "claude", "size": "medium"},
    "anthropic:claude-opus-4-6": {"family": "claude", "size": "large"},
    "openai:gpt-4o-mini": {"family": "gpt", "size": "small"},
    "openai:gpt-4o": {"family": "gpt", "size": "medium"},
    "openai:o3": {"family": "gpt", "size": "large"},
    # Open-source (OpenRouter API — fast iteration)
    "openrouter:meta-llama/llama-3.1-8b-instruct": {"family": "llama", "size": "small"},
    "openrouter:meta-llama/llama-3.1-70b-instruct": {"family": "llama", "size": "large"},
    "openrouter:mistralai/ministral-8b-2512": {"family": "mistral", "size": "small"},
    "openrouter:mistralai/mistral-small-24b-instruct-2501": {"family": "mistral", "size": "large"},
    "openrouter:qwen/qwen-2.5-7b-instruct": {"family": "qwen", "size": "small"},
    "openrouter:qwen/qwen-2.5-72b-instruct": {"family": "qwen", "size": "large"},
    # Open-source (vLLM on Modal — reproducibility validation)
    "vllm:meta-llama/Meta-Llama-3.1-8B-Instruct": {"family": "llama", "size": "small"},
    "vllm:meta-llama/Meta-Llama-3.1-70B-Instruct": {"family": "llama", "size": "large"},
    "vllm:mistralai/Mistral-7B-Instruct-v0.3": {"family": "mistral", "size": "small"},
    "vllm:mistralai/Mistral-Small-24B-Instruct-2501": {"family": "mistral", "size": "large"},
    "vllm:Qwen/Qwen2.5-7B-Instruct": {"family": "qwen", "size": "small"},
    "vllm:Qwen/Qwen2.5-72B-Instruct": {"family": "qwen", "size": "large"},
}

# vLLM endpoint URLs per model (populated from vllm_endpoints.json or env).
# Each Modal deployment gets its own URL.
VLLM_ENDPOINTS: dict[str, str] = {}

def _load_vllm_endpoints() -> dict[str, str]:
    """Load vLLM endpoint URLs from config file or environment.

    Checks (in order):
    1. VLLM_ENDPOINTS_FILE env var pointing to a JSON file
    2. vllm_endpoints.json in the benchmarks directory
    3. VLLM_BASE_URL env var (single URL for all models)
    """
    global VLLM_ENDPOINTS

    # Try config file
    endpoints_file = os.environ.get("VLLM_ENDPOINTS_FILE")
    if not endpoints_file:
        default_path = Path(__file__).resolve().parent / "vllm_endpoints.json"
        if default_path.exists():
            endpoints_file = str(default_path)

    if endpoints_file and Path(endpoints_file).exists():
        with open(endpoints_file) as f:
            VLLM_ENDPOINTS = json.load(f)
        return VLLM_ENDPOINTS

    # Fallback: single URL for all models
    base_url = os.environ.get("VLLM_BASE_URL")
    if base_url:
        for model_spec in MODELS:
            if model_spec.startswith("vllm:"):
                model_name = model_spec.split(":", 1)[1]
                VLLM_ENDPOINTS[model_name] = base_url

    return VLLM_ENDPOINTS

TASKS: list[str] = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"]

CONDITIONS: list[str] = ["direct", "short_cot", "budget_cot", "tool_use"]

# Task key -> benchmark data filename (relative to benchmarks/ directory)
TASK_FILE_MAP: dict[str, str] = {
    "B1": "data/b1_B1_masked_majority.json",
    "B2": "data/b2_B2_nested_boolean.json",
    "B3": "data/b3_B3_permutation_composition.json",
    "B4": "data/b4_B4_state_machine.json",
    "B5": "data/b5_B5_graph_reachability.json",
    "B6": "data/b6_B6_longest_increasing_subsequence.json",
    "B7": "data/b7_B7_3sat.json",
    "B8": "data/b8_B8_reversal_inference.json",
    "B9": "data/b9_B9_negation_sensitivity.json",
}

# Provider -> required env var
PROVIDER_ENV_KEYS: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "vllm": "VLLM_BASE_URL",
}

# Concurrency settings by provider
PROVIDER_PARALLEL: dict[str, int] = {
    "anthropic": 5,
    "openai": 5,
    "openrouter": 5,
    "vllm": 1,
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    """Result of a single subprocess evaluation run."""
    model: str
    task: str
    condition: str
    success: bool
    duration_seconds: float
    accuracy: float | None = None
    error_message: str | None = None
    log_file: str | None = None


@dataclass
class BatchProgress:
    """Tracks overall batch progress."""
    total_combinations: int
    completed: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: float = field(default_factory=time.monotonic)
    results: list[RunResult] = field(default_factory=list)

    def record(self, result: RunResult) -> None:
        self.results.append(result)
        self.completed += 1
        if result.success:
            self.succeeded += 1
        else:
            self.failed += 1

    def record_skip(self) -> None:
        self.completed += 1
        self.skipped += 1

    @property
    def elapsed_seconds(self) -> float:
        return time.monotonic() - self.start_time

    @property
    def eta_seconds(self) -> float | None:
        if self.completed == 0:
            return None
        rate = self.elapsed_seconds / self.completed
        remaining = self.total_combinations - self.completed
        return rate * remaining

    def format_eta(self) -> str:
        eta = self.eta_seconds
        if eta is None:
            return "unknown"
        hours = int(eta // 3600)
        minutes = int((eta % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes:02d}m"
        return f"{minutes}m"

    def format_elapsed(self) -> str:
        elapsed = self.elapsed_seconds
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        if hours > 0:
            return f"{hours}h {minutes:02d}m {seconds:02d}s"
        return f"{minutes}m {seconds:02d}s"


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def check_data_files(
    tasks: list[str],
    benchmarks_dir: Path,
) -> list[str]:
    """Verify benchmark data files exist. Returns list of errors."""
    errors = []
    for task in tasks:
        if task not in TASK_FILE_MAP:
            errors.append(f"Unknown task: {task}")
            continue
        data_path = benchmarks_dir / TASK_FILE_MAP[task]
        if not data_path.exists():
            errors.append(f"Missing data file for {task}: {data_path}")
    return errors


def check_api_keys(models: list[str]) -> list[str]:
    """Check that required API keys/env vars are set. Returns list of errors."""
    errors = []
    providers_needed = set()
    for model in models:
        if ":" not in model:
            continue
        provider = model.split(":", 1)[0]
        providers_needed.add(provider)

    for provider in providers_needed:
        env_key = PROVIDER_ENV_KEYS.get(provider)
        if env_key and not os.environ.get(env_key):
            errors.append(
                f"Missing environment variable {env_key} "
                f"(required for {provider} models)"
            )

    return errors


def check_checkpoint_progress(
    models: list[str],
    tasks: list[str],
    conditions: list[str],
    checkpoint_dir: Path,
    benchmarks_dir: Path,
) -> dict[str, Any]:
    """Scan checkpoint directory for resumable progress.

    Returns dict with 'resumable' count, 'complete' count, and details.
    """
    # Add benchmarks dir to sys.path so we can import checkpoint module
    bench_str = str(benchmarks_dir)
    if bench_str not in sys.path:
        sys.path.insert(0, bench_str)

    try:
        from checkpoint import CheckpointManager
    except ImportError:
        return {"resumable": 0, "complete": 0, "details": []}

    if not checkpoint_dir.exists():
        return {"resumable": 0, "complete": 0, "details": []}

    mgr = CheckpointManager(str(checkpoint_dir))
    complete = 0
    resumable = 0
    details = []

    for model in models:
        # The checkpoint uses the model name without provider prefix
        model_key = model.split(":", 1)[1] if ":" in model else model
        for task in tasks:
            task_name = _task_key_to_name(task)
            for condition in conditions:
                completed_ids = mgr.get_completed_ids(model_key, task_name, condition)
                n_done = len(completed_ids)
                if n_done > 0:
                    # Load the benchmark to get total count
                    data_path = benchmarks_dir / TASK_FILE_MAP.get(task, "")
                    total = 500  # default assumption: 5 difficulties * 100 instances
                    if data_path.exists():
                        try:
                            with open(data_path) as f:
                                bm = json.load(f)
                            total = len(bm.get("instances", []))
                        except (json.JSONDecodeError, OSError):
                            pass

                    if n_done >= total:
                        complete += 1
                        details.append({
                            "model": model, "task": task, "condition": condition,
                            "status": "complete", "done": n_done, "total": total,
                        })
                    else:
                        resumable += 1
                        details.append({
                            "model": model, "task": task, "condition": condition,
                            "status": "partial", "done": n_done, "total": total,
                        })

    return {"resumable": resumable, "complete": complete, "details": details}


def _task_key_to_name(task_key: str) -> str:
    """Convert B1 -> B1_masked_majority, etc."""
    name_map = {
        "B1": "B1_masked_majority",
        "B2": "B2_nested_boolean",
        "B3": "B3_permutation_composition",
        "B4": "B4_state_machine",
        "B5": "B5_graph_reachability",
        "B6": "B6_longest_increasing_subsequence",
        "B7": "B7_3sat",
        "B8": "B8_reversal_inference",
        "B9": "B9_negation_sensitivity",
    }
    return name_map.get(task_key, task_key)


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

def compute_cost_estimate(
    models: list[str],
    tasks: list[str],
    conditions: list[str],
    benchmarks_dir: Path,
) -> dict[str, Any]:
    """Compute cost estimate using the cost_estimator module."""
    bench_str = str(benchmarks_dir)
    if bench_str not in sys.path:
        sys.path.insert(0, bench_str)

    from cost_estimator import estimate_cost, format_estimate

    # Determine instances per task from first available data file
    instances_per_task = 100  # default per (task, difficulty)
    for task in tasks:
        data_path = benchmarks_dir / TASK_FILE_MAP.get(task, "")
        if data_path.exists():
            try:
                with open(data_path) as f:
                    bm = json.load(f)
                # instances_per_task is per difficulty level
                n_per_diff = bm.get("n_instances_per_difficulty", 100)
                instances_per_task = n_per_diff
                break
            except (json.JSONDecodeError, OSError):
                pass

    estimate = estimate_cost(
        models=models,
        tasks=tasks,
        conditions=conditions,
        instances_per_task=instances_per_task,
    )
    return estimate


# ---------------------------------------------------------------------------
# Subprocess execution
# ---------------------------------------------------------------------------

def run_single_evaluation(
    model: str,
    task: str,
    condition: str,
    benchmarks_dir: Path,
    checkpoint_dir: Path,
    log_dir: Path,
    python_executable: str,
    max_instances: int | None = None,
    budget_multiplier: float | None = None,
) -> RunResult:
    """Run a single evaluate.py subprocess for one (model, task, condition).

    Args:
        model: Full model spec (e.g., "anthropic:claude-haiku-4-5-20251001").
        task: Task key (e.g., "B1").
        condition: Evaluation condition (base condition without multiplier suffix).
        benchmarks_dir: Path to benchmarks/ directory.
        checkpoint_dir: Shared checkpoint directory.
        log_dir: Directory for stdout/stderr logs.
        python_executable: Python interpreter path.
        max_instances: Optional limit on instances (for testing).
        budget_multiplier: Optional budget multiplier for budget_cot condition.

    Returns:
        RunResult with success/failure status.
    """
    data_file = TASK_FILE_MAP[task]
    benchmark_path = benchmarks_dir / data_file

    # Determine parallelism
    provider = model.split(":", 1)[0] if ":" in model else "unknown"
    parallel = PROVIDER_PARALLEL.get(provider, 5)

    # Build output path -- include multiplier suffix for budget sweep runs
    model_safe = model.replace(":", "_").replace("/", "_")
    condition_label = condition
    if budget_multiplier is not None and condition == "budget_cot":
        condition_label = f"budget_cot_{budget_multiplier}x"
    output_file = (
        benchmarks_dir / "results"
        / f"{model_safe}_{task}_{condition_label}.json"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Use a separate checkpoint directory for multiplier runs to avoid conflicts
    effective_checkpoint_dir = checkpoint_dir
    if budget_multiplier is not None and condition == "budget_cot":
        effective_checkpoint_dir = checkpoint_dir / f"budget_{budget_multiplier}x"
        effective_checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Build command
    cmd = [
        python_executable,
        str(benchmarks_dir / "evaluate.py"),
        "--benchmark", str(benchmark_path),
        "--model", model,
        "--condition", condition,
        "--output", str(output_file),
        "--resume",
        "--checkpoint-dir", str(effective_checkpoint_dir),
        "--parallel", str(parallel),
    ]

    if max_instances is not None:
        cmd.extend(["--max-instances", str(max_instances)])

    if budget_multiplier is not None:
        cmd.extend(["--budget-multiplier", str(budget_multiplier)])

    # Set up log files
    log_dir.mkdir(parents=True, exist_ok=True)
    log_stem = f"{model_safe}_{task}_{condition_label}"
    stdout_log = log_dir / f"{log_stem}.stdout.log"
    stderr_log = log_dir / f"{log_stem}.stderr.log"

    start = time.monotonic()

    # Set per-model VLLM_BASE_URL for vLLM models
    env = os.environ.copy()
    if provider == "vllm":
        model_name = model.split(":", 1)[1]
        endpoint_url = VLLM_ENDPOINTS.get(model_name)
        if endpoint_url:
            env["VLLM_BASE_URL"] = endpoint_url
        elif not env.get("VLLM_BASE_URL"):
            print(f"  WARNING: No endpoint URL for {model_name}")

    try:
        with open(stdout_log, "w") as out_f, open(stderr_log, "w") as err_f:
            result = subprocess.run(
                cmd,
                stdout=out_f,
                stderr=err_f,
                timeout=7200,  # 2 hour timeout per combination
                cwd=str(benchmarks_dir),
                env=env,
            )

        duration = time.monotonic() - start

        if result.returncode != 0:
            # Read the last few lines of stderr for the error message
            error_msg = _read_tail(stderr_log, 10)
            return RunResult(
                model=model,
                task=task,
                condition=condition,
                success=False,
                duration_seconds=duration,
                error_message=error_msg,
                log_file=str(stderr_log),
            )

        # Try to extract accuracy from output file
        accuracy = _extract_accuracy(output_file)

        return RunResult(
            model=model,
            task=task,
            condition=condition,
            success=True,
            duration_seconds=duration,
            accuracy=accuracy,
            log_file=str(stdout_log),
        )

    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return RunResult(
            model=model,
            task=task,
            condition=condition,
            success=False,
            duration_seconds=duration,
            error_message="Subprocess timed out after 2 hours",
            log_file=str(stderr_log),
        )
    except Exception as exc:
        duration = time.monotonic() - start
        return RunResult(
            model=model,
            task=task,
            condition=condition,
            success=False,
            duration_seconds=duration,
            error_message=str(exc),
        )


def _read_tail(path: Path, n_lines: int = 10) -> str:
    """Read the last n lines of a file."""
    try:
        with open(path) as f:
            lines = f.readlines()
        return "".join(lines[-n_lines:]).strip()
    except (OSError, UnicodeDecodeError):
        return "(could not read log file)"


def _extract_accuracy(output_file: Path) -> float | None:
    """Extract accuracy from a results JSON file."""
    try:
        with open(output_file) as f:
            data = json.load(f)
        return data.get("summary", {}).get("accuracy")
    except (json.JSONDecodeError, OSError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Progress file
# ---------------------------------------------------------------------------

def write_progress_file(
    progress: BatchProgress,
    progress_path: Path,
) -> None:
    """Write a progress.json file for external monitoring."""
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_combinations": progress.total_combinations,
        "completed": progress.completed,
        "succeeded": progress.succeeded,
        "failed": progress.failed,
        "skipped": progress.skipped,
        "elapsed_seconds": progress.elapsed_seconds,
        "eta_seconds": progress.eta_seconds,
        "results": [
            {
                "model": r.model,
                "task": r.task,
                "condition": r.condition,
                "success": r.success,
                "duration_seconds": r.duration_seconds,
                "accuracy": r.accuracy,
                "error_message": r.error_message,
            }
            for r in progress.results
        ],
    }

    try:
        atomic_json_write(progress_path, data)
    except Exception:
        pass  # Progress file is best-effort; don't crash the batch


# ---------------------------------------------------------------------------
# Main batch runner
# ---------------------------------------------------------------------------

def build_combination_list(
    models: list[str],
    tasks: list[str],
    conditions: list[str],
    budget_multipliers: list[float] | None = None,
) -> list[tuple[str, str, str, float | None]]:
    """Build the full list of (model, task, condition, budget_multiplier) combinations.

    When budget_multipliers is provided, budget_cot runs are expanded into
    one combination per multiplier value.
    """
    combos: list[tuple[str, str, str, float | None]] = []
    for model in models:
        for task in tasks:
            for condition in conditions:
                if condition == "budget_cot" and budget_multipliers:
                    for mult in budget_multipliers:
                        combos.append((model, task, condition, mult))
                else:
                    combos.append((model, task, condition, None))
    return combos


def run_batch(
    models: list[str],
    tasks: list[str],
    conditions: list[str],
    benchmarks_dir: Path,
    checkpoint_dir: Path,
    log_dir: Path,
    progress_path: Path,
    python_executable: str,
    max_instances: int | None = None,
    dry_run: bool = False,
    budget_multipliers: list[float] | None = None,
) -> BatchProgress:
    """Execute the full batch evaluation.

    Args:
        models: List of model specs.
        tasks: List of task keys.
        conditions: List of conditions.
        benchmarks_dir: Path to benchmarks/ directory.
        checkpoint_dir: Shared checkpoint directory.
        log_dir: Directory for per-run log files.
        progress_path: Path to write progress.json.
        python_executable: Python interpreter path.
        max_instances: Optional limit per task (for testing).
        dry_run: If True, only estimate costs and exit.
        budget_multipliers: Optional list of multipliers for budget_cot sweep.

    Returns:
        BatchProgress with all results.
    """
    combinations = build_combination_list(
        models, tasks, conditions, budget_multipliers
    )
    progress = BatchProgress(total_combinations=len(combinations))

    if dry_run:
        print(f"\n[DRY RUN] Would execute {len(combinations)} combinations:")
        for model, task, condition, mult in combinations:
            mult_str = f" ({mult}x)" if mult is not None else ""
            print(f"  {model} / {task} / {condition}{mult_str}")
        return progress

    print(f"\nStarting batch evaluation: {len(combinations)} combinations")
    print(f"Checkpoint dir: {checkpoint_dir}")
    print(f"Log dir: {log_dir}")
    print()

    for model, task, condition, budget_mult in combinations:
        mult_str = f" ({budget_mult}x)" if budget_mult is not None else ""
        combo_label = f"{model} / {task} / {condition}{mult_str}"
        idx = progress.completed + 1
        print(f"[{idx}/{progress.total_combinations}] {combo_label} ...", flush=True)

        result = run_single_evaluation(
            model=model,
            task=task,
            condition=condition,
            benchmarks_dir=benchmarks_dir,
            checkpoint_dir=checkpoint_dir,
            log_dir=log_dir,
            python_executable=python_executable,
            max_instances=max_instances,
            budget_multiplier=budget_mult,
        )

        progress.record(result)

        # Print result line
        duration_str = _format_duration(result.duration_seconds)
        if result.success:
            acc_str = (
                f"{result.accuracy * 100:.0f}% accuracy"
                if result.accuracy is not None
                else "completed"
            )
            print(
                f"[{progress.completed}/{progress.total_combinations}] "
                f"{combo_label} -- {acc_str} ({duration_str})"
            )
        else:
            print(
                f"[{progress.completed}/{progress.total_combinations}] "
                f"{combo_label} -- FAILED ({duration_str})"
            )
            if result.error_message:
                # Print first line of error
                first_line = result.error_message.split("\n")[0][:120]
                print(f"  Error: {first_line}")

        # Progress summary
        print(
            f"Overall: {progress.completed}/{progress.total_combinations} "
            f"({progress.succeeded} ok, {progress.failed} failed) | "
            f"ETA: {progress.format_eta()} | "
            f"Elapsed: {progress.format_elapsed()}"
        )
        print()

        # Update progress file
        write_progress_file(progress, progress_path)

    return progress


def _format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m {secs:02d}s"
    hours = int(minutes // 60)
    mins = minutes % 60
    return f"{hours}h {mins:02d}m"


def run_analysis(
    benchmarks_dir: Path,
    results_dir: Path,
    python_executable: str,
) -> bool:
    """Run the analysis pipeline on collected results.

    Returns True on success, False on failure.
    """
    analyze_script = benchmarks_dir / "analyze.py"
    if not analyze_script.exists():
        print("Warning: analyze.py not found, skipping analysis.")
        return False

    output_dir = benchmarks_dir / "analysis_output"
    cmd = [
        python_executable,
        str(analyze_script),
        "--results-dir", str(results_dir),
        "--output-dir", str(output_dir),
    ]

    print(f"\nRunning analysis pipeline...")
    print(f"Results: {results_dir}")
    print(f"Output:  {output_dir}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(benchmarks_dir),
        )
        if result.returncode == 0:
            print("Analysis complete.")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"Analysis failed (exit code {result.returncode}):")
            if result.stderr:
                print(result.stderr[:500])
            return False
    except subprocess.TimeoutExpired:
        print("Analysis timed out after 5 minutes.")
        return False
    except Exception as exc:
        print(f"Analysis failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the full ReasonGap evaluation across all models, tasks, and conditions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python run_evaluation.py --all\n"
            "  python run_evaluation.py --all --dry-run\n"
            "  python run_evaluation.py --models anthropic:claude-haiku-4-5-20251001 --tasks B1 B2\n"
            "  python run_evaluation.py --all --yes --max-instances 10\n"
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all models, tasks, and conditions.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Specific model(s) to evaluate (e.g., anthropic:claude-haiku-4-5-20251001 openai:gpt-4o-mini).",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=None,
        help="Specific task(s) to evaluate (e.g., B1 B2 B9).",
    )
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=None,
        help="Specific condition(s) (e.g., direct short_cot).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Estimate cost and list combinations without running.",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt.",
    )
    parser.add_argument(
        "--max-instances",
        type=int,
        default=None,
        help="Limit instances per task (for testing).",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default=None,
        help="Checkpoint directory (default: results/checkpoints/).",
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip running the analysis pipeline after evaluation.",
    )
    parser.add_argument(
        "--budget-multipliers",
        type=str,
        default=None,
        help=(
            "Comma-separated list of budget multipliers for budget_cot sensitivity sweep "
            "(e.g., '0.25,0.5,1.0,2.0,4.0'). When specified, budget_cot runs once per "
            "multiplier with separate result/checkpoint files."
        ),
    )
    parser.add_argument(
        "--instance",
        type=str,
        default=None,
        help=(
            "Systemd instance specifier: model::task::condition "
            "(e.g., 'openai:o3::B5::budget_cot'). "
            "Uses '::' as delimiter to avoid ambiguity with model names containing colons/underscores."
        ),
    )

    args = parser.parse_args(argv)

    # Parse --instance into --models, --tasks, --conditions
    if args.instance:
        parts = args.instance.split("::")
        if len(parts) != 3:
            parser.error(
                f"--instance must be 'model::task::condition', got: {args.instance}"
            )
        args.models = [parts[0]]
        args.tasks = [parts[1]]
        args.conditions = [parts[2]]
        args.yes = True
        args.skip_analysis = True

    # Resolve models/tasks/conditions
    if args.all:
        if args.models is None:
            args.models = list(MODELS.keys())
        if args.tasks is None:
            args.tasks = list(TASKS)
        if args.conditions is None:
            args.conditions = list(CONDITIONS)
    elif args.instance:
        pass  # Already set above
    else:
        if args.models is None:
            parser.error("--models is required unless --all or --instance is set")
        if args.tasks is None:
            args.tasks = list(TASKS)
        if args.conditions is None:
            args.conditions = list(CONDITIONS)

    # Validate task keys
    for task in args.tasks:
        if task not in TASK_FILE_MAP:
            parser.error(f"Unknown task: {task}. Valid: {', '.join(TASKS)}")

    # Validate condition names
    for cond in args.conditions:
        if cond not in CONDITIONS:
            parser.error(f"Unknown condition: {cond}. Valid: {', '.join(CONDITIONS)}")

    return args


def main(argv: list[str] | None = None) -> int:
    """Main entry point. Returns exit code."""
    args = parse_args(argv)

    # Parse budget multipliers if provided
    budget_multipliers: list[float] | None = None
    if args.budget_multipliers:
        try:
            budget_multipliers = [
                float(x.strip()) for x in args.budget_multipliers.split(",")
            ]
        except ValueError as exc:
            print(f"ERROR: Invalid --budget-multipliers value: {exc}")
            return 1
        print(f"Budget sensitivity sweep: {budget_multipliers}")

    benchmarks_dir = Path(__file__).resolve().parent
    checkpoint_dir = Path(
        args.checkpoint_dir
        or str(benchmarks_dir / "results" / "checkpoints")
    )
    log_dir = benchmarks_dir / "results" / "logs"
    results_dir = benchmarks_dir / "results"
    progress_path = benchmarks_dir / "results" / "progress.json"

    # Determine python executable (use the same one running this script)
    python_exe = sys.executable

    # Load vLLM endpoint URLs
    _load_vllm_endpoints()

    # Compute combination count (accounting for budget multipliers)
    combos_preview = build_combination_list(
        args.models, args.tasks, args.conditions, budget_multipliers
    )
    n_combos = len(combos_preview)

    # Print header
    print("=" * 60)
    print("ReasonGap Batch Evaluation Runner")
    print("=" * 60)
    print(f"Models:      {len(args.models)}")
    print(f"Tasks:       {len(args.tasks)}")
    print(f"Conditions:  {len(args.conditions)}")
    if budget_multipliers:
        print(f"Budget mult: {', '.join(f'{m}x' for m in budget_multipliers)}")
    print(f"Combinations: {n_combos}")
    print()

    # Pre-flight: data files
    print("Pre-flight checks...")
    data_errors = check_data_files(args.tasks, benchmarks_dir)
    if data_errors:
        print("\nERROR: Missing benchmark data files:")
        for err in data_errors:
            print(f"  - {err}")
        print("\nRun 'python generate.py --all' to create them.")
        return 1

    print("  [OK] All benchmark data files present")

    # Pre-flight: API keys
    key_errors = check_api_keys(args.models)
    if key_errors:
        print("\nWARNING: Missing API credentials:")
        for err in key_errors:
            print(f"  - {err}")
        if not args.dry_run and not args.yes:
            resp = input("\nContinue anyway? Models without keys will fail. [y/N] ")
            if resp.lower() not in ("y", "yes"):
                return 1
    else:
        print("  [OK] API credentials configured")

    # Pre-flight: checkpoint state
    ckpt_state = check_checkpoint_progress(
        args.models, args.tasks, args.conditions,
        checkpoint_dir, benchmarks_dir,
    )
    if ckpt_state["complete"] > 0 or ckpt_state["resumable"] > 0:
        print(
            f"  [OK] Checkpoint state: {ckpt_state['complete']} complete, "
            f"{ckpt_state['resumable']} resumable"
        )
    else:
        print("  [OK] No existing checkpoints (fresh start)")

    # Cost estimation
    print()
    try:
        estimate = compute_cost_estimate(
            args.models, args.tasks, args.conditions, benchmarks_dir,
        )
        bench_str = str(benchmarks_dir)
        if bench_str not in sys.path:
            sys.path.insert(0, bench_str)
        from cost_estimator import format_estimate
        print(format_estimate(estimate))
    except Exception as exc:
        print(f"Warning: Could not compute cost estimate: {exc}")
        estimate = None

    # Dry run exits here
    if args.dry_run:
        combos = build_combination_list(
            args.models, args.tasks, args.conditions, budget_multipliers
        )
        print(f"\n[DRY RUN] Would execute {len(combos)} combinations.")
        return 0

    # Confirmation
    if not args.yes:
        resp = input("\nProceed with evaluation? [y/N] ")
        if resp.lower() not in ("y", "yes"):
            print("Aborted.")
            return 0

    # Ensure directories exist
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Run the batch
    progress = run_batch(
        models=args.models,
        tasks=args.tasks,
        conditions=args.conditions,
        benchmarks_dir=benchmarks_dir,
        checkpoint_dir=checkpoint_dir,
        log_dir=log_dir,
        progress_path=progress_path,
        python_executable=python_exe,
        max_instances=args.max_instances,
        dry_run=False,
        budget_multipliers=budget_multipliers,
    )

    # Final summary
    print("=" * 60)
    print("BATCH EVALUATION COMPLETE")
    print("=" * 60)
    print(f"Total:     {progress.total_combinations}")
    print(f"Succeeded: {progress.succeeded}")
    print(f"Failed:    {progress.failed}")
    print(f"Skipped:   {progress.skipped}")
    print(f"Elapsed:   {progress.format_elapsed()}")
    print()

    if progress.failed > 0:
        print("Failed runs:")
        for r in progress.results:
            if not r.success:
                print(f"  {r.model} / {r.task} / {r.condition}")
                if r.error_message:
                    first_line = r.error_message.split("\n")[0][:120]
                    print(f"    {first_line}")
                if r.log_file:
                    print(f"    Log: {r.log_file}")
        print()

    # Run analysis
    if not args.skip_analysis and progress.succeeded > 0:
        run_analysis(benchmarks_dir, results_dir, python_exe)

    # Final progress write
    write_progress_file(progress, progress_path)

    return 0 if progress.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
