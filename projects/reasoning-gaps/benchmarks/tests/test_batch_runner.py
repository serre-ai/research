"""Tests for the batch evaluation runner (run_evaluation.py)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

# Ensure benchmarks dir is on sys.path
_benchmarks_dir = str(Path(__file__).resolve().parent.parent)
if _benchmarks_dir not in sys.path:
    sys.path.insert(0, _benchmarks_dir)

from run_evaluation import (
    MODELS,
    TASKS,
    CONDITIONS,
    TASK_FILE_MAP,
    PROVIDER_ENV_KEYS,
    PROVIDER_PARALLEL,
    BatchProgress,
    RunResult,
    build_combination_list,
    check_api_keys,
    check_data_files,
    check_checkpoint_progress,
    compute_cost_estimate,
    parse_args,
    run_single_evaluation,
    write_progress_file,
    run_batch,
    _task_key_to_name,
    _format_duration,
    _extract_accuracy,
)


# ---------------------------------------------------------------------------
# Evaluation matrix completeness
# ---------------------------------------------------------------------------

class TestEvaluationMatrix:
    """Verify the evaluation matrix is complete and consistent."""

    def test_total_combinations(self):
        """12 models x 9 tasks x 3 conditions = 324 combinations."""
        combos = build_combination_list(
            list(MODELS.keys()), TASKS, CONDITIONS
        )
        assert len(combos) == 324

    def test_model_count(self):
        assert len(MODELS) == 12

    def test_task_count(self):
        assert len(TASKS) == 9

    def test_condition_count(self):
        assert len(CONDITIONS) == 3

    def test_all_tasks_in_file_map(self):
        """Every task key must have a file mapping."""
        for task in TASKS:
            assert task in TASK_FILE_MAP, f"Task {task} missing from TASK_FILE_MAP"

    def test_file_map_covers_all_tasks(self):
        """TASK_FILE_MAP should have exactly the tasks in TASKS."""
        assert set(TASK_FILE_MAP.keys()) == set(TASKS)

    def test_model_families(self):
        """Check all expected families are represented."""
        families = {info["family"] for info in MODELS.values()}
        assert families == {"claude", "gpt", "llama", "mistral", "qwen"}

    def test_model_sizes(self):
        """Check all models have a size annotation."""
        for model, info in MODELS.items():
            assert "size" in info, f"Model {model} missing 'size'"
            assert info["size"] in {"small", "medium", "large"}, (
                f"Model {model} has invalid size: {info['size']}"
            )

    def test_provider_prefixes(self):
        """All models must have a valid provider prefix."""
        valid_providers = {"anthropic", "openai", "vllm"}
        for model in MODELS:
            assert ":" in model, f"Model {model} missing provider prefix"
            provider = model.split(":", 1)[0]
            assert provider in valid_providers, (
                f"Model {model} has unknown provider: {provider}"
            )

    def test_conditions_valid(self):
        expected = ["direct", "short_cot", "budget_cot"]
        assert CONDITIONS == expected


# ---------------------------------------------------------------------------
# Task-to-file mapping
# ---------------------------------------------------------------------------

class TestTaskFileMapping:
    """Verify task-to-file resolution works for all 9 tasks."""

    @pytest.mark.parametrize("task,expected_file", [
        ("B1", "data/b1_B1_masked_majority.json"),
        ("B2", "data/b2_B2_nested_boolean.json"),
        ("B3", "data/b3_B3_permutation_composition.json"),
        ("B4", "data/b4_B4_state_machine.json"),
        ("B5", "data/b5_B5_graph_reachability.json"),
        ("B6", "data/b6_B6_longest_increasing_subsequence.json"),
        ("B7", "data/b7_B7_3sat.json"),
        ("B8", "data/b8_B8_reversal_inference.json"),
        ("B9", "data/b9_B9_negation_sensitivity.json"),
    ])
    def test_task_maps_to_correct_file(self, task, expected_file):
        assert TASK_FILE_MAP[task] == expected_file

    @pytest.mark.parametrize("task,expected_name", [
        ("B1", "B1_masked_majority"),
        ("B2", "B2_nested_boolean"),
        ("B3", "B3_permutation_composition"),
        ("B4", "B4_state_machine"),
        ("B5", "B5_graph_reachability"),
        ("B6", "B6_longest_increasing_subsequence"),
        ("B7", "B7_3sat"),
        ("B8", "B8_reversal_inference"),
        ("B9", "B9_negation_sensitivity"),
    ])
    def test_task_key_to_name(self, task, expected_name):
        assert _task_key_to_name(task) == expected_name


# ---------------------------------------------------------------------------
# Pre-flight checks: API keys
# ---------------------------------------------------------------------------

class TestApiKeyChecks:
    """Test detection of missing API keys."""

    def test_detects_missing_anthropic_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            errors = check_api_keys(["anthropic:claude-haiku-4-5-20251001"])
            assert len(errors) == 1
            assert "ANTHROPIC_API_KEY" in errors[0]

    def test_detects_missing_openai_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            errors = check_api_keys(["openai:gpt-4o-mini"])
            assert len(errors) == 1
            assert "OPENAI_API_KEY" in errors[0]

    def test_detects_missing_vllm_url(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            errors = check_api_keys(["vllm:meta-llama/Llama-3-8B"])
            assert len(errors) == 1
            assert "VLLM_BASE_URL" in errors[0]

    def test_passes_when_key_set(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}, clear=True):
            errors = check_api_keys(["anthropic:claude-haiku-4-5-20251001"])
            assert len(errors) == 0

    def test_detects_multiple_missing_keys(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            errors = check_api_keys([
                "anthropic:claude-haiku-4-5-20251001",
                "openai:gpt-4o",
                "vllm:meta-llama/Llama-3-8B",
            ])
            assert len(errors) == 3

    def test_no_errors_for_all_keys_present(self):
        with mock.patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "sk-ant",
            "OPENAI_API_KEY": "sk-oai",
            "VLLM_BASE_URL": "http://localhost:8000/v1",
        }, clear=True):
            errors = check_api_keys(list(MODELS.keys()))
            assert len(errors) == 0

    def test_deduplicates_providers(self):
        """Multiple models from same provider should produce only one error."""
        with mock.patch.dict(os.environ, {}, clear=True):
            errors = check_api_keys([
                "anthropic:claude-haiku-4-5-20251001",
                "anthropic:claude-sonnet-4-6-20250514",
                "anthropic:claude-opus-4-6-20250514",
            ])
            assert len(errors) == 1


# ---------------------------------------------------------------------------
# Pre-flight checks: data files
# ---------------------------------------------------------------------------

class TestDataFileChecks:
    """Test detection of missing benchmark data files."""

    def test_detects_missing_data_file(self, tmp_path):
        errors = check_data_files(["B1"], tmp_path)
        assert len(errors) == 1
        assert "B1" in errors[0]

    def test_passes_when_file_exists(self, tmp_path):
        # Create the expected data file
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "b1_B1_masked_majority.json").write_text("{}")
        errors = check_data_files(["B1"], tmp_path)
        assert len(errors) == 0

    def test_detects_unknown_task(self, tmp_path):
        errors = check_data_files(["B99"], tmp_path)
        assert len(errors) == 1
        assert "Unknown task" in errors[0]

    def test_checks_all_tasks(self, tmp_path):
        errors = check_data_files(TASKS, tmp_path)
        assert len(errors) == 9  # None exist in tmp_path

    def test_all_files_present(self, tmp_path):
        """Create all data files and verify no errors."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        for task in TASKS:
            filename = TASK_FILE_MAP[task]
            (tmp_path / filename).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / filename).write_text("{}")
        errors = check_data_files(TASKS, tmp_path)
        assert len(errors) == 0


# ---------------------------------------------------------------------------
# Progress tracking
# ---------------------------------------------------------------------------

class TestProgressTracking:
    """Test BatchProgress state management."""

    def test_initial_state(self):
        p = BatchProgress(total_combinations=324)
        assert p.completed == 0
        assert p.succeeded == 0
        assert p.failed == 0
        assert p.skipped == 0
        assert p.eta_seconds is None

    def test_record_success(self):
        p = BatchProgress(total_combinations=10)
        result = RunResult(
            model="test:model", task="B1", condition="direct",
            success=True, duration_seconds=5.0, accuracy=0.85,
        )
        p.record(result)
        assert p.completed == 1
        assert p.succeeded == 1
        assert p.failed == 0
        assert len(p.results) == 1

    def test_record_failure(self):
        p = BatchProgress(total_combinations=10)
        result = RunResult(
            model="test:model", task="B1", condition="direct",
            success=False, duration_seconds=2.0,
            error_message="API error",
        )
        p.record(result)
        assert p.completed == 1
        assert p.succeeded == 0
        assert p.failed == 1

    def test_record_skip(self):
        p = BatchProgress(total_combinations=10)
        p.record_skip()
        assert p.completed == 1
        assert p.skipped == 1
        assert p.succeeded == 0

    def test_eta_calculation(self):
        p = BatchProgress(total_combinations=10)
        # Manually set start_time so we can compute ETA
        p.start_time = p.start_time - 10.0  # pretend 10s elapsed
        result = RunResult(
            model="test:model", task="B1", condition="direct",
            success=True, duration_seconds=10.0,
        )
        p.record(result)
        # 1 done in 10s -> 9 remaining -> ~90s ETA
        eta = p.eta_seconds
        assert eta is not None
        assert 85 < eta < 95  # allow small timing variance

    def test_format_eta_minutes(self):
        p = BatchProgress(total_combinations=10)
        p.start_time = p.start_time - 60.0
        for _ in range(5):
            p.record(RunResult(
                model="m", task="B1", condition="d",
                success=True, duration_seconds=1.0,
            ))
        # 5 done in 60s -> 5 remaining -> ~60s ETA
        eta_str = p.format_eta()
        assert "m" in eta_str

    def test_multiple_records(self):
        p = BatchProgress(total_combinations=5)
        for i in range(5):
            p.record(RunResult(
                model=f"m{i}", task="B1", condition="d",
                success=(i % 2 == 0), duration_seconds=float(i),
            ))
        assert p.completed == 5
        assert p.succeeded == 3  # i=0,2,4
        assert p.failed == 2     # i=1,3


# ---------------------------------------------------------------------------
# Progress file writing
# ---------------------------------------------------------------------------

class TestProgressFile:
    """Test progress.json writes."""

    def test_write_progress_file(self, tmp_path):
        progress_path = tmp_path / "progress.json"
        progress = BatchProgress(total_combinations=10)
        progress.record(RunResult(
            model="test:model", task="B1", condition="direct",
            success=True, duration_seconds=5.0, accuracy=0.9,
        ))

        write_progress_file(progress, progress_path)

        assert progress_path.exists()
        data = json.loads(progress_path.read_text())
        assert data["total_combinations"] == 10
        assert data["completed"] == 1
        assert data["succeeded"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["accuracy"] == 0.9

    def test_progress_file_overwrite(self, tmp_path):
        """Progress file should be overwritten on each update."""
        progress_path = tmp_path / "progress.json"
        progress = BatchProgress(total_combinations=10)

        write_progress_file(progress, progress_path)
        assert json.loads(progress_path.read_text())["completed"] == 0

        progress.record(RunResult(
            model="m", task="B1", condition="d",
            success=True, duration_seconds=1.0,
        ))
        write_progress_file(progress, progress_path)
        assert json.loads(progress_path.read_text())["completed"] == 1


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------

class TestDryRun:
    """Test that dry-run mode doesn't execute anything."""

    def test_dry_run_no_subprocess_calls(self, tmp_path, capsys):
        """Dry run should not call subprocess.run."""
        with mock.patch("run_evaluation.subprocess.run") as mock_run:
            progress = run_batch(
                models=["anthropic:claude-haiku-4-5-20251001"],
                tasks=["B1"],
                conditions=["direct"],
                benchmarks_dir=tmp_path,
                checkpoint_dir=tmp_path / "ckpt",
                log_dir=tmp_path / "logs",
                progress_path=tmp_path / "progress.json",
                python_executable=sys.executable,
                dry_run=True,
            )
            mock_run.assert_not_called()

        assert progress.completed == 0
        assert progress.succeeded == 0

    def test_dry_run_lists_combinations(self, tmp_path, capsys):
        run_batch(
            models=["anthropic:claude-haiku-4-5-20251001", "openai:gpt-4o-mini"],
            tasks=["B1", "B2"],
            conditions=["direct"],
            benchmarks_dir=tmp_path,
            checkpoint_dir=tmp_path / "ckpt",
            log_dir=tmp_path / "logs",
            progress_path=tmp_path / "progress.json",
            python_executable=sys.executable,
            dry_run=True,
        )
        output = capsys.readouterr().out
        assert "DRY RUN" in output
        assert "4 combinations" in output


# ---------------------------------------------------------------------------
# Subprocess failure handling
# ---------------------------------------------------------------------------

class TestSubprocessFailures:
    """Test that subprocess failures don't crash the batch runner."""

    def test_subprocess_failure_continues(self, tmp_path):
        """If one subprocess fails, the runner should continue."""
        # Create minimal data files
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        for task in ["B1", "B2"]:
            filepath = tmp_path / TASK_FILE_MAP[task]
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(json.dumps({
                "task": task,
                "task_name": _task_key_to_name(task),
                "instances": [{"id": "test_1", "prompt": "test", "answer": "1", "task": task, "difficulty": 1}],
            }))

        # Mock subprocess.run to always fail
        with mock.patch("run_evaluation.subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=1)

            progress = run_batch(
                models=["anthropic:claude-haiku-4-5-20251001"],
                tasks=["B1", "B2"],
                conditions=["direct"],
                benchmarks_dir=tmp_path,
                checkpoint_dir=tmp_path / "ckpt",
                log_dir=tmp_path / "logs",
                progress_path=tmp_path / "progress.json",
                python_executable=sys.executable,
            )

        # Both should have been attempted
        assert progress.completed == 2
        assert progress.failed == 2
        assert progress.succeeded == 0

    def test_subprocess_timeout_continues(self, tmp_path):
        """If subprocess times out, runner should continue."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        filepath = tmp_path / TASK_FILE_MAP["B1"]
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(json.dumps({
            "task": "B1",
            "task_name": "B1_masked_majority",
            "instances": [],
        }))

        with mock.patch("run_evaluation.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=7200)

            progress = run_batch(
                models=["anthropic:claude-haiku-4-5-20251001"],
                tasks=["B1"],
                conditions=["direct"],
                benchmarks_dir=tmp_path,
                checkpoint_dir=tmp_path / "ckpt",
                log_dir=tmp_path / "logs",
                progress_path=tmp_path / "progress.json",
                python_executable=sys.executable,
            )

        assert progress.completed == 1
        assert progress.failed == 1
        result = progress.results[0]
        assert "timed out" in result.error_message.lower()

    def test_subprocess_exception_continues(self, tmp_path):
        """Unexpected exceptions should be caught and logged."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        filepath = tmp_path / TASK_FILE_MAP["B1"]
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text("{}")

        with mock.patch("run_evaluation.subprocess.run") as mock_run:
            mock_run.side_effect = OSError("Disk full")

            progress = run_batch(
                models=["anthropic:claude-haiku-4-5-20251001"],
                tasks=["B1"],
                conditions=["direct"],
                benchmarks_dir=tmp_path,
                checkpoint_dir=tmp_path / "ckpt",
                log_dir=tmp_path / "logs",
                progress_path=tmp_path / "progress.json",
                python_executable=sys.executable,
            )

        assert progress.completed == 1
        assert progress.failed == 1
        assert "Disk full" in progress.results[0].error_message


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

class TestArgParsing:
    """Test command-line argument parsing."""

    def test_all_flag(self):
        args = parse_args(["--all"])
        assert len(args.models) == 12
        assert len(args.tasks) == 9
        assert len(args.conditions) == 3

    def test_specific_models(self):
        args = parse_args([
            "--models", "anthropic:claude-haiku-4-5-20251001", "openai:gpt-4o-mini",
        ])
        assert len(args.models) == 2
        assert args.tasks == TASKS
        assert args.conditions == CONDITIONS

    def test_specific_tasks(self):
        args = parse_args([
            "--models", "anthropic:claude-haiku-4-5-20251001",
            "--tasks", "B1", "B2", "B9",
        ])
        assert args.tasks == ["B1", "B2", "B9"]

    def test_specific_conditions(self):
        args = parse_args([
            "--models", "anthropic:claude-haiku-4-5-20251001",
            "--conditions", "direct", "short_cot",
        ])
        assert args.conditions == ["direct", "short_cot"]

    def test_dry_run_flag(self):
        args = parse_args(["--all", "--dry-run"])
        assert args.dry_run is True

    def test_yes_flag(self):
        args = parse_args(["--all", "--yes"])
        assert args.yes is True

    def test_max_instances(self):
        args = parse_args(["--all", "--max-instances", "10"])
        assert args.max_instances == 10

    def test_models_required_without_all(self):
        with pytest.raises(SystemExit):
            parse_args(["--tasks", "B1"])

    def test_invalid_task_rejected(self):
        with pytest.raises(SystemExit):
            parse_args(["--models", "anthropic:claude-haiku-4-5-20251001", "--tasks", "B99"])

    def test_invalid_condition_rejected(self):
        with pytest.raises(SystemExit):
            parse_args([
                "--models", "anthropic:claude-haiku-4-5-20251001",
                "--conditions", "invalid",
            ])

    def test_all_with_model_override(self):
        """--all should set defaults, but --models should override."""
        args = parse_args([
            "--all",
            "--models", "openai:gpt-4o-mini",
        ])
        assert args.models == ["openai:gpt-4o-mini"]
        assert len(args.tasks) == 9


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

class TestUtilities:
    """Test helper functions."""

    def test_format_duration_seconds(self):
        assert _format_duration(45) == "45s"

    def test_format_duration_minutes(self):
        assert _format_duration(150) == "2m 30s"

    def test_format_duration_hours(self):
        result = _format_duration(3700)
        assert "1h" in result

    def test_extract_accuracy_valid(self, tmp_path):
        result_file = tmp_path / "result.json"
        result_file.write_text(json.dumps({
            "summary": {"accuracy": 0.87},
            "results": [],
        }))
        assert _extract_accuracy(result_file) == 0.87

    def test_extract_accuracy_missing(self, tmp_path):
        result_file = tmp_path / "result.json"
        result_file.write_text(json.dumps({"summary": {}}))
        assert _extract_accuracy(result_file) is None

    def test_extract_accuracy_no_file(self, tmp_path):
        assert _extract_accuracy(tmp_path / "nonexistent.json") is None

    def test_provider_parallel_settings(self):
        assert PROVIDER_PARALLEL["anthropic"] == 5
        assert PROVIDER_PARALLEL["openai"] == 5
        assert PROVIDER_PARALLEL["vllm"] == 1


# ---------------------------------------------------------------------------
# Combination building
# ---------------------------------------------------------------------------

class TestCombinationBuilding:
    """Test build_combination_list."""

    def test_full_matrix(self):
        combos = build_combination_list(
            list(MODELS.keys()), TASKS, CONDITIONS
        )
        assert len(combos) == 12 * 9 * 3

    def test_ordering(self):
        """Combinations should be model-major, then task, then condition."""
        combos = build_combination_list(
            ["a:m1", "a:m2"], ["B1", "B2"], ["direct", "short_cot"]
        )
        assert combos[0] == ("a:m1", "B1", "direct")
        assert combos[1] == ("a:m1", "B1", "short_cot")
        assert combos[2] == ("a:m1", "B2", "direct")
        assert combos[3] == ("a:m1", "B2", "short_cot")
        assert combos[4] == ("a:m2", "B1", "direct")

    def test_empty_models(self):
        assert build_combination_list([], TASKS, CONDITIONS) == []

    def test_single_combination(self):
        combos = build_combination_list(["a:m1"], ["B1"], ["direct"])
        assert len(combos) == 1
        assert combos[0] == ("a:m1", "B1", "direct")


# ---------------------------------------------------------------------------
# Checkpoint progress check
# ---------------------------------------------------------------------------

class TestCheckpointProgress:
    """Test check_checkpoint_progress."""

    def test_empty_checkpoint_dir(self, tmp_path):
        result = check_checkpoint_progress(
            models=["anthropic:claude-haiku-4-5-20251001"],
            tasks=["B1"],
            conditions=["direct"],
            checkpoint_dir=tmp_path / "nonexistent",
            benchmarks_dir=tmp_path,
        )
        assert result["complete"] == 0
        assert result["resumable"] == 0

    def test_with_partial_checkpoint(self, tmp_path):
        """Create a checkpoint file with some results and verify detection."""
        ckpt_dir = tmp_path / "checkpoints"
        ckpt_dir.mkdir()

        # Create a data file
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        data_file = data_dir / "b1_B1_masked_majority.json"
        instances = [{"id": f"inst_{i}", "prompt": "test", "answer": "1"} for i in range(10)]
        data_file.write_text(json.dumps({
            "task": "B1",
            "task_name": "B1_masked_majority",
            "instances": instances,
        }))

        # Create a checkpoint JSONL with 5 of 10 instances
        # Checkpoint key: model_task_condition.jsonl
        ckpt_file = ckpt_dir / "claude-haiku-4-5-20251001_B1_masked_majority_direct.jsonl"
        lines = []
        for i in range(5):
            lines.append(json.dumps({
                "instance_id": f"inst_{i}",
                "model": "claude-haiku-4-5-20251001",
                "task": "B1_masked_majority",
                "condition": "direct",
                "correct": True,
            }))
        ckpt_file.write_text("\n".join(lines) + "\n")

        result = check_checkpoint_progress(
            models=["anthropic:claude-haiku-4-5-20251001"],
            tasks=["B1"],
            conditions=["direct"],
            checkpoint_dir=ckpt_dir,
            benchmarks_dir=tmp_path,
        )
        assert result["resumable"] == 1
        assert result["complete"] == 0


# ---------------------------------------------------------------------------
# Run single evaluation
# ---------------------------------------------------------------------------

class TestRunSingleEvaluation:
    """Test the subprocess runner with mocks."""

    def test_successful_run(self, tmp_path):
        """Mocked successful subprocess run."""
        # Create data file
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "b1_B1_masked_majority.json").write_text("{}")

        # Create a results file that the "subprocess" would produce
        results_dir = tmp_path / "results"
        results_dir.mkdir()

        with mock.patch("run_evaluation.subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0)

            result = run_single_evaluation(
                model="anthropic:claude-haiku-4-5-20251001",
                task="B1",
                condition="direct",
                benchmarks_dir=tmp_path,
                checkpoint_dir=tmp_path / "ckpt",
                log_dir=tmp_path / "logs",
                python_executable=sys.executable,
            )

        assert result.success is True
        assert result.model == "anthropic:claude-haiku-4-5-20251001"
        assert result.task == "B1"
        assert result.condition == "direct"
        assert result.duration_seconds >= 0

    def test_failed_run(self, tmp_path):
        """Mocked failed subprocess run."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "b1_B1_masked_majority.json").write_text("{}")

        with mock.patch("run_evaluation.subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=1)

            result = run_single_evaluation(
                model="anthropic:claude-haiku-4-5-20251001",
                task="B1",
                condition="direct",
                benchmarks_dir=tmp_path,
                checkpoint_dir=tmp_path / "ckpt",
                log_dir=tmp_path / "logs",
                python_executable=sys.executable,
            )

        assert result.success is False

    def test_passes_correct_arguments(self, tmp_path):
        """Verify subprocess is called with the right flags."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "b1_B1_masked_majority.json").write_text("{}")

        with mock.patch("run_evaluation.subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0)

            run_single_evaluation(
                model="openai:gpt-4o",
                task="B1",
                condition="short_cot",
                benchmarks_dir=tmp_path,
                checkpoint_dir=tmp_path / "ckpt",
                log_dir=tmp_path / "logs",
                python_executable="/usr/bin/python3",
                max_instances=10,
            )

            call_args = mock_run.call_args
            cmd = call_args[0][0] if call_args[0] else call_args[1].get("args", [])

            assert "/usr/bin/python3" in cmd[0]
            assert "--model" in cmd
            model_idx = cmd.index("--model")
            assert cmd[model_idx + 1] == "openai:gpt-4o"

            assert "--condition" in cmd
            cond_idx = cmd.index("--condition")
            assert cmd[cond_idx + 1] == "short_cot"

            assert "--resume" in cmd
            assert "--parallel" in cmd
            assert "--max-instances" in cmd

    def test_vllm_parallel_1(self, tmp_path):
        """vLLM models should use parallel=1."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "b1_B1_masked_majority.json").write_text("{}")

        with mock.patch("run_evaluation.subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0)

            run_single_evaluation(
                model="vllm:meta-llama/Llama-3-8B",
                task="B1",
                condition="direct",
                benchmarks_dir=tmp_path,
                checkpoint_dir=tmp_path / "ckpt",
                log_dir=tmp_path / "logs",
                python_executable=sys.executable,
            )

            cmd = mock_run.call_args[0][0]
            parallel_idx = cmd.index("--parallel")
            assert cmd[parallel_idx + 1] == "1"
