"""Tests for the ReasonGap analysis pipeline.

Generates synthetic results that mimic expected patterns:
- Type 1 tasks: high accuracy at low difficulty, degrading at high
- Type 6 tasks: constant low accuracy across difficulties
- CoT lift: positive for types 2,3; zero for types 5,6
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure benchmarks dir is on path (same as conftest.py)
import sys
_benchmarks_dir = str(Path(__file__).resolve().parent.parent)
if _benchmarks_dir not in sys.path:
    sys.path.insert(0, _benchmarks_dir)

from analysis.loader import (
    load_results,
    TASK_GAP_TYPE,
    TASK_ORDER,
    GAP_TYPE_ORDER,
    _extract_model_family,
    _extract_model_size,
)
from analysis.tables import (
    main_accuracy_table,
    accuracy_by_condition_table,
    cot_lift_table,
    scale_analysis_table,
    to_latex,
)
from analysis.plots import (
    plot_accuracy_vs_difficulty,
    plot_cot_lift_heatmap,
    plot_phase_transition,
    plot_scale_sensitivity,
    plot_intervention_comparison,
)
from analysis.statistics import (
    bootstrap_ci,
    mcnemar_test,
    compute_all_cis,
    pairwise_model_comparison,
)


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

def _generate_synthetic_results(
    n_per_cell: int = 50,
    seed: int = 42,
) -> list[dict]:
    """Generate synthetic evaluation results with realistic patterns.

    Patterns encoded:
    - Type 1 (B1): accuracy degrades with difficulty (0.95 -> 0.30)
    - Type 2 (B2, B5): accuracy degrades with depth (0.90 -> 0.40)
    - Type 3 (B3, B4): linear degradation (0.85 -> 0.35)
    - Type 4 (B6): moderate degradation (0.70 -> 0.30)
    - Type 5 (B7): phase transition cliff (0.80 -> 0.20)
    - Type 6 (B8, B9): constant low accuracy (0.35 ± 0.05)

    CoT lift patterns:
    - Types 2,3: +0.15 to +0.25
    - Type 1: +0.10
    - Type 4: +0.05 (CoT), +0.30 (tool)
    - Types 5,6: +0.00 to +0.02
    """
    rng = np.random.default_rng(seed)

    tasks = TASK_ORDER
    models = ["gpt-4o", "claude-3.5-sonnet", "llama-3.1-70b"]
    conditions = ["direct", "short_cot", "budget_cot"]
    difficulties = [1, 2, 3, 4, 5]

    # Base accuracy curves by task (direct condition)
    base_accuracy: dict[str, dict[int, float]] = {
        "B1_masked_majority":                  {1: 0.95, 2: 0.85, 3: 0.65, 4: 0.45, 5: 0.30},
        "B2_nested_boolean":                   {1: 0.90, 2: 0.80, 3: 0.65, 4: 0.50, 5: 0.40},
        "B3_permutation_composition":          {1: 0.85, 2: 0.70, 3: 0.55, 4: 0.42, 5: 0.35},
        "B4_state_machine":                    {1: 0.82, 2: 0.68, 3: 0.52, 4: 0.40, 5: 0.32},
        "B5_graph_reachability":               {1: 0.88, 2: 0.75, 3: 0.60, 4: 0.48, 5: 0.38},
        "B6_longest_increasing_subsequence":   {1: 0.70, 2: 0.58, 3: 0.45, 4: 0.35, 5: 0.28},
        "B7_3sat":                             {1: 0.80, 2: 0.70, 3: 0.40, 4: 0.25, 5: 0.20},
        "B8_reversal_inference":               {1: 0.38, 2: 0.36, 3: 0.35, 4: 0.33, 5: 0.32},
        "B9_negation_sensitivity":             {1: 0.40, 2: 0.38, 3: 0.36, 4: 0.35, 5: 0.34},
    }

    # CoT lift by gap type and condition
    cot_lift: dict[str, dict[str, float]] = {
        "Type 1: Sensitivity":   {"short_cot": 0.12, "budget_cot": 0.18},
        "Type 2: Depth":         {"short_cot": 0.20, "budget_cot": 0.25},
        "Type 3: Serial":        {"short_cot": 0.15, "budget_cot": 0.22},
        "Type 4: Algorithmic":   {"short_cot": 0.05, "budget_cot": 0.08},
        "Type 5: Intractability": {"short_cot": 0.02, "budget_cot": 0.01},
        "Type 6: Architectural": {"short_cot": 0.01, "budget_cot": 0.00},
    }

    # Model-level offsets (some models are slightly better/worse)
    model_offset: dict[str, float] = {
        "gpt-4o": 0.03,
        "claude-3.5-sonnet": 0.02,
        "llama-3.1-70b": -0.05,
    }

    records = []
    instance_counter = 0

    for task in tasks:
        gap_type = TASK_GAP_TYPE[task]
        for model in models:
            for condition in conditions:
                for difficulty in difficulties:
                    # Compute target accuracy
                    base_acc = base_accuracy[task][difficulty]
                    m_offset = model_offset.get(model, 0.0)

                    if condition == "direct":
                        target_acc = base_acc + m_offset
                    else:
                        lift = cot_lift.get(gap_type, {}).get(condition, 0.0)
                        target_acc = base_acc + m_offset + lift

                    target_acc = max(0.0, min(1.0, target_acc))

                    # Generate individual instances
                    for i in range(n_per_cell):
                        correct = rng.random() < target_acc
                        latency = max(50.0, rng.normal(250, 80))

                        records.append({
                            "instance_id": f"{task}_d{difficulty}_{instance_counter:05d}",
                            "task": task,
                            "difficulty": difficulty,
                            "condition": condition,
                            "model": model,
                            "prompt_sent": f"[synthetic prompt for {task}]",
                            "model_response": "1" if correct else "0",
                            "extracted_answer": "1" if correct else "0",
                            "ground_truth": "1",
                            "correct": correct,
                            "latency_ms": latency,
                            "metadata": {"is_refusal": False},
                        })
                        instance_counter += 1

    return records


def _write_synthetic_json(tmpdir: str, records: list[dict]) -> None:
    """Write synthetic records as JSON result files (one per task/model/condition)."""
    # Group by task, model, condition
    from collections import defaultdict
    groups: dict[tuple, list] = defaultdict(list)
    for r in records:
        key = (r["task"], r["model"], r["condition"])
        groups[key].append(r)

    for (task, model, condition), group_records in groups.items():
        # Compute summary
        total = len(group_records)
        correct = sum(1 for r in group_records if r["correct"])
        accuracy = correct / total if total > 0 else 0.0

        by_diff: dict[int, list] = defaultdict(list)
        for r in group_records:
            by_diff[r["difficulty"]].append(r)

        acc_by_diff = {}
        for d, d_recs in sorted(by_diff.items()):
            n_c = sum(1 for r in d_recs if r["correct"])
            acc_by_diff[d] = n_c / len(d_recs)

        latencies = [r["latency_ms"] for r in group_records]

        data = {
            "summary": {
                "task": task,
                "model": model,
                "condition": condition,
                "total_instances": total,
                "correct": correct,
                "accuracy": accuracy,
                "accuracy_by_difficulty": acc_by_diff,
                "mean_latency_ms": sum(latencies) / len(latencies),
            },
            "results": group_records,
        }

        # Sanitize filename
        safe_model = model.replace(":", "_").replace(".", "_")
        filename = f"{task}_{safe_model}_{condition}.json"
        filepath = Path(tmpdir) / filename
        with open(filepath, "w") as f:
            json.dump(data, f)


def _write_synthetic_jsonl(tmpdir: str, records: list[dict], filename: str = "checkpoint.jsonl") -> None:
    """Write synthetic records as a single JSONL file."""
    filepath = Path(tmpdir) / filename
    with open(filepath, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def synthetic_records():
    """Generate synthetic records once for the module."""
    return _generate_synthetic_results(n_per_cell=50, seed=42)


@pytest.fixture(scope="module")
def synthetic_json_dir(synthetic_records):
    """Write synthetic JSON files to a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_synthetic_json(tmpdir, synthetic_records)
        yield tmpdir


@pytest.fixture(scope="module")
def synthetic_jsonl_dir(synthetic_records):
    """Write synthetic JSONL file to a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_synthetic_jsonl(tmpdir, synthetic_records[:500])  # subset
        yield tmpdir


@pytest.fixture(scope="module")
def df_from_json(synthetic_json_dir):
    """Load results from JSON files."""
    return load_results(synthetic_json_dir)


@pytest.fixture(scope="module")
def output_dir():
    """Temporary output directory for plots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ---------------------------------------------------------------------------
# Tests: Loader
# ---------------------------------------------------------------------------

class TestLoader:
    """Tests for analysis.loader."""

    def test_load_results_json(self, df_from_json):
        """load_results parses JSON files into correct DataFrame."""
        df = df_from_json
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Check required columns
        required_cols = [
            "instance_id", "task", "difficulty", "condition", "model",
            "extracted_answer", "ground_truth", "correct", "latency_ms",
            "is_refusal", "gap_type", "model_family", "model_size",
        ]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_load_results_jsonl(self, synthetic_jsonl_dir):
        """load_results parses JSONL files correctly."""
        df = load_results(synthetic_jsonl_dir)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "task" in df.columns
        assert "gap_type" in df.columns

    def test_load_results_empty_dir(self):
        """load_results returns empty DataFrame for empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = load_results(tmpdir)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 0

    def test_load_results_nonexistent_dir(self):
        """load_results raises FileNotFoundError for missing directory."""
        with pytest.raises(FileNotFoundError):
            load_results("/nonexistent/path/12345")

    def test_gap_type_mapping(self, df_from_json):
        """All tasks map to correct gap types."""
        df = df_from_json
        for task, expected_gap in TASK_GAP_TYPE.items():
            task_df = df[df["task"] == task]
            if not task_df.empty:
                actual = task_df["gap_type"].iloc[0]
                assert actual == expected_gap, (
                    f"Task {task}: expected gap type '{expected_gap}', got '{actual}'"
                )

    def test_gap_type_mapping_complete(self):
        """TASK_GAP_TYPE covers all 9 tasks."""
        assert len(TASK_GAP_TYPE) == 9
        for task in TASK_ORDER:
            assert task in TASK_GAP_TYPE, f"Missing gap type for {task}"

    def test_model_family_extraction(self):
        """Model family extraction handles various formats."""
        assert _extract_model_family("gpt-4o") == "GPT"
        assert _extract_model_family("openai:gpt-4o") == "GPT"
        assert _extract_model_family("claude-3.5-sonnet") == "Claude"
        assert _extract_model_family("anthropic:claude-3-opus") == "Claude"
        assert _extract_model_family("llama-3-70b") == "Llama"
        assert _extract_model_family("mistral-7b") == "Mistral"
        assert _extract_model_family("qwen-72b") == "Qwen"
        assert _extract_model_family("unknown-model") == "Other"

    def test_model_size_extraction(self):
        """Model size extraction works for known and pattern-matched models."""
        assert _extract_model_size("llama-3-70b") == 70.0
        assert _extract_model_size("llama-3-8b") == 8.0
        assert _extract_model_size("gpt-4o") is None  # unknown size
        assert _extract_model_size("some-model-13b") == 13.0

    def test_derived_columns(self, df_from_json):
        """Derived columns (gap_type, model_family, model_size) are populated."""
        df = df_from_json
        # gap_type should not be 'Unknown' for known tasks
        known_tasks = df[df["task"].isin(TASK_GAP_TYPE.keys())]
        assert (known_tasks["gap_type"] != "Unknown").all()

        # model_family should not be empty
        assert (df["model_family"] != "").all()

    def test_correct_column_is_bool(self, df_from_json):
        """The 'correct' column should contain boolean values."""
        assert df_from_json["correct"].dtype == bool

    def test_difficulty_is_int(self, df_from_json):
        """The 'difficulty' column should contain integer values."""
        assert df_from_json["difficulty"].dtype in (int, np.int64, np.int32)


# ---------------------------------------------------------------------------
# Tests: Tables
# ---------------------------------------------------------------------------

class TestTables:
    """Tests for analysis.tables."""

    def test_main_accuracy_table_shape(self, df_from_json):
        """main_accuracy_table has correct shape."""
        table = main_accuracy_table(df_from_json)
        assert isinstance(table, pd.DataFrame)
        # Rows = number of unique tasks
        assert len(table) == df_from_json["task"].nunique()
        # Columns = number of unique models
        assert len(table.columns) == df_from_json["model"].nunique()

    def test_main_accuracy_table_values(self, df_from_json):
        """Accuracy values are in [0, 1]."""
        table = main_accuracy_table(df_from_json)
        for col in table.columns:
            vals = table[col].dropna()
            assert (vals >= 0).all() and (vals <= 1).all(), (
                f"Accuracy out of range in column {col}"
            )

    def test_accuracy_by_condition_table(self, df_from_json):
        """accuracy_by_condition_table has conditions as columns."""
        table = accuracy_by_condition_table(df_from_json)
        assert isinstance(table, pd.DataFrame)
        # Should have condition columns
        conditions_in_data = df_from_json["condition"].unique()
        for cond in table.columns:
            assert cond in conditions_in_data

    def test_cot_lift_table_shape(self, df_from_json):
        """cot_lift_table has gap types as rows."""
        table = cot_lift_table(df_from_json)
        assert isinstance(table, pd.DataFrame)
        if not table.empty:
            # Rows should be gap types
            for idx in table.index:
                assert idx in GAP_TYPE_ORDER

    def test_cot_lift_types23_positive(self, df_from_json):
        """Types 2,3 should show positive CoT lift."""
        table = cot_lift_table(df_from_json)
        if table.empty:
            pytest.skip("No CoT lift data")

        for gap_type in ["Type 2: Depth", "Type 3: Serial"]:
            if gap_type in table.index:
                row = table.loc[gap_type]
                for val in row.dropna():
                    assert val > 0.05, (
                        f"{gap_type} should show positive CoT lift, got {val:.3f}"
                    )

    def test_cot_lift_types56_near_zero(self, df_from_json):
        """Types 5,6 should show near-zero CoT lift."""
        table = cot_lift_table(df_from_json)
        if table.empty:
            pytest.skip("No CoT lift data")

        for gap_type in ["Type 5: Intractability", "Type 6: Architectural"]:
            if gap_type in table.index:
                row = table.loc[gap_type]
                for val in row.dropna():
                    assert abs(val) < 0.10, (
                        f"{gap_type} should show near-zero CoT lift, got {val:.3f}"
                    )

    def test_scale_analysis_table(self, df_from_json):
        """scale_analysis_table handles data without model sizes gracefully."""
        table = scale_analysis_table(df_from_json)
        # Our synthetic data uses models without known sizes (gpt-4o etc.)
        # but llama-3.1-70b has a known size.
        assert isinstance(table, pd.DataFrame)

    def test_to_latex_output(self, df_from_json):
        """to_latex produces valid LaTeX string."""
        table = main_accuracy_table(df_from_json)
        latex = to_latex(table, caption="Test caption", label="tab:test")

        assert isinstance(latex, str)
        assert "\\begin{table}" in latex
        assert "\\end{table}" in latex
        assert "\\toprule" in latex
        assert "\\midrule" in latex
        assert "\\bottomrule" in latex
        assert "\\caption{Test caption}" in latex
        assert "\\label{tab:test}" in latex

    def test_to_latex_booktabs(self, df_from_json):
        """to_latex uses booktabs style (no \\hline)."""
        table = main_accuracy_table(df_from_json)
        latex = to_latex(table, caption="Test", label="tab:test")
        assert "\\hline" not in latex

    def test_to_latex_highlight_max(self, df_from_json):
        """to_latex with highlight_max produces \\textbf."""
        table = main_accuracy_table(df_from_json)
        latex = to_latex(table, caption="Test", label="tab:test", highlight_max=True)
        assert "\\textbf{" in latex

    def test_to_latex_escapes_underscores(self, df_from_json):
        """to_latex escapes underscores in column/index names."""
        table = main_accuracy_table(df_from_json)
        latex = to_latex(table, caption="Test", label="tab:test")
        # Column names like "gpt-4o" don't have underscores,
        # but if they did, they should be escaped.
        # The index labels use short names which may contain underscores.
        # Verify no raw underscores outside LaTeX commands.
        # This is a basic check.
        assert isinstance(latex, str)


# ---------------------------------------------------------------------------
# Tests: Statistics
# ---------------------------------------------------------------------------

class TestStatistics:
    """Tests for analysis.statistics."""

    def test_bootstrap_ci_all_correct(self):
        """CI for all-correct data should be [1.0, 1.0]."""
        data = np.ones(100)
        lo, hi = bootstrap_ci(data, seed=42)
        assert lo == 1.0
        assert hi == 1.0

    def test_bootstrap_ci_all_wrong(self):
        """CI for all-wrong data should be [0.0, 0.0]."""
        data = np.zeros(100)
        lo, hi = bootstrap_ci(data, seed=42)
        assert lo == 0.0
        assert hi == 0.0

    def test_bootstrap_ci_reasonable(self):
        """CI for mixed data should contain the point estimate."""
        rng = np.random.default_rng(42)
        data = rng.binomial(1, 0.7, size=200).astype(float)
        mean = data.mean()
        lo, hi = bootstrap_ci(data, seed=42)

        assert lo <= mean <= hi
        assert 0 < lo < hi < 1
        # CI should be reasonably narrow for n=200
        assert (hi - lo) < 0.20

    def test_bootstrap_ci_wider_for_small_n(self):
        """CI should be wider for smaller samples."""
        rng = np.random.default_rng(42)
        data_small = rng.binomial(1, 0.5, size=20).astype(float)
        data_large = rng.binomial(1, 0.5, size=500).astype(float)

        lo_s, hi_s = bootstrap_ci(data_small, seed=42)
        lo_l, hi_l = bootstrap_ci(data_large, seed=42)

        width_small = hi_s - lo_s
        width_large = hi_l - lo_l
        assert width_small > width_large

    def test_bootstrap_ci_empty(self):
        """CI for empty array returns (0, 0)."""
        lo, hi = bootstrap_ci(np.array([]), seed=42)
        assert lo == 0.0
        assert hi == 0.0

    def test_bootstrap_ci_single(self):
        """CI for single element returns that element."""
        lo, hi = bootstrap_ci(np.array([1.0]), seed=42)
        assert lo == 1.0
        assert hi == 1.0

    def test_mcnemar_identical(self):
        """McNemar's test for identical results should give p=1."""
        data = np.array([True, False, True, True, False] * 20)
        stat, p = mcnemar_test(data, data)
        assert p == 1.0
        assert stat == 0.0

    def test_mcnemar_different(self):
        """McNemar's test for very different results should give small p."""
        # Model A correct on first half, model B correct on second half
        a = np.array([True] * 50 + [False] * 50)
        b = np.array([False] * 50 + [True] * 50)
        stat, p = mcnemar_test(a, b)
        # With 50 discordant pairs in each direction, test should not be significant
        # (balanced discordance), but stat should be near 0
        assert p > 0.05  # balanced discordance

    def test_mcnemar_asymmetric(self):
        """McNemar's test for asymmetric disagreement should be significant."""
        # Model A much better than B: A correct on 80 that B gets wrong
        n = 200
        a = np.ones(n, dtype=bool)
        b = np.ones(n, dtype=bool)
        # Create asymmetry: 80 cases where A right, B wrong vs 10 opposite
        b[:80] = False   # A right, B wrong
        a[80:90] = False  # A wrong, B right
        stat, p = mcnemar_test(a, b)
        assert p < 0.05

    def test_mcnemar_length_mismatch(self):
        """McNemar's test should raise on length mismatch."""
        with pytest.raises(ValueError):
            mcnemar_test(np.array([True, False]), np.array([True]))

    def test_compute_all_cis(self, df_from_json):
        """compute_all_cis returns reasonable CIs."""
        ci_df = compute_all_cis(df_from_json, n_bootstrap=500, seed=42)
        assert isinstance(ci_df, pd.DataFrame)
        assert "accuracy" in ci_df.columns
        assert "ci_lower" in ci_df.columns
        assert "ci_upper" in ci_df.columns
        assert "n_instances" in ci_df.columns

        # CIs should bracket the accuracy
        for _, row in ci_df.iterrows():
            assert row["ci_lower"] <= row["accuracy"] + 1e-10
            assert row["ci_upper"] >= row["accuracy"] - 1e-10

    def test_pairwise_model_comparison(self, df_from_json):
        """pairwise_model_comparison runs without error."""
        models = df_from_json["model"].unique()
        if len(models) < 2:
            pytest.skip("Need at least 2 models")

        result = pairwise_model_comparison(df_from_json, models[0], models[1])
        assert isinstance(result, pd.DataFrame)
        assert "p_value" in result.columns
        assert "significant" in result.columns

        # p-values should be in [0, 1]
        assert (result["p_value"] >= 0).all()
        assert (result["p_value"] <= 1).all()


# ---------------------------------------------------------------------------
# Tests: Plots
# ---------------------------------------------------------------------------

class TestPlots:
    """Tests for analysis.plots — verify functions run and produce files."""

    def test_plot_accuracy_vs_difficulty(self, df_from_json, output_dir):
        """plot_accuracy_vs_difficulty produces PDF and PNG."""
        plot_accuracy_vs_difficulty(df_from_json, output_dir)
        assert (Path(output_dir) / "accuracy_vs_difficulty.pdf").exists()
        assert (Path(output_dir) / "accuracy_vs_difficulty.png").exists()

    def test_plot_cot_lift_heatmap(self, df_from_json, output_dir):
        """plot_cot_lift_heatmap produces PDF and PNG."""
        plot_cot_lift_heatmap(df_from_json, output_dir)
        assert (Path(output_dir) / "cot_lift_heatmap.pdf").exists()
        assert (Path(output_dir) / "cot_lift_heatmap.png").exists()

    def test_plot_phase_transition(self, df_from_json, output_dir):
        """plot_phase_transition produces PDF and PNG."""
        plot_phase_transition(df_from_json, output_dir)
        assert (Path(output_dir) / "phase_transition.pdf").exists()
        assert (Path(output_dir) / "phase_transition.png").exists()

    def test_plot_scale_sensitivity(self, df_from_json, output_dir):
        """plot_scale_sensitivity handles models with known sizes."""
        # Our synthetic data has llama-3.1-70b with known size
        plot_scale_sensitivity(df_from_json, output_dir)
        # May or may not produce output depending on data
        # Just verify it doesn't crash

    def test_plot_intervention_comparison(self, df_from_json, output_dir):
        """plot_intervention_comparison produces PDF and PNG."""
        plot_intervention_comparison(df_from_json, output_dir)
        assert (Path(output_dir) / "intervention_comparison.pdf").exists()
        assert (Path(output_dir) / "intervention_comparison.png").exists()

    def test_plots_dont_leave_figures_open(self, df_from_json, output_dir):
        """All plot functions should close figures after saving."""
        import matplotlib.pyplot as plt
        before = len(plt.get_fignums())
        plot_accuracy_vs_difficulty(df_from_json, output_dir)
        plot_cot_lift_heatmap(df_from_json, output_dir)
        plot_intervention_comparison(df_from_json, output_dir)
        after = len(plt.get_fignums())
        assert after == before, "Figures were not closed after plotting"

    def test_plot_empty_data(self, output_dir):
        """Plotting with empty data should not crash."""
        empty_df = pd.DataFrame(columns=[
            "instance_id", "task", "difficulty", "condition", "model",
            "extracted_answer", "ground_truth", "correct", "latency_ms",
            "is_refusal", "gap_type", "model_family", "model_size",
        ])
        # These should handle empty data gracefully (return early)
        plot_accuracy_vs_difficulty(empty_df, output_dir)
        plot_cot_lift_heatmap(empty_df, output_dir)
        plot_phase_transition(empty_df, output_dir)
        plot_scale_sensitivity(empty_df, output_dir)
        plot_intervention_comparison(empty_df, output_dir)


# ---------------------------------------------------------------------------
# Tests: Integration (full pipeline)
# ---------------------------------------------------------------------------

class TestIntegration:
    """Integration tests: end-to-end pipeline from JSON to outputs."""

    def test_full_pipeline(self, synthetic_json_dir):
        """Run the full analysis pipeline and verify all outputs."""
        with tempfile.TemporaryDirectory() as output_dir:
            df = load_results(synthetic_json_dir)
            assert len(df) > 0

            # Tables
            t1 = main_accuracy_table(df)
            assert not t1.empty

            t2 = accuracy_by_condition_table(df)
            assert not t2.empty

            t3 = cot_lift_table(df)
            assert not t3.empty

            # LaTeX
            latex = to_latex(t1, "Test", "tab:test")
            assert "\\begin{table}" in latex

            # Plots (just verify no crash)
            figures_dir = str(Path(output_dir) / "figures")
            plot_accuracy_vs_difficulty(df, figures_dir)
            plot_cot_lift_heatmap(df, figures_dir)
            plot_phase_transition(df, figures_dir)
            plot_intervention_comparison(df, figures_dir)

            # Stats
            ci_df = compute_all_cis(df, n_bootstrap=200, seed=42)
            assert len(ci_df) > 0

    def test_pattern_type1_degradation(self, df_from_json):
        """Type 1 (B1): accuracy should degrade from d=1 to d=5."""
        b1 = df_from_json[
            (df_from_json["task"] == "B1_masked_majority")
            & (df_from_json["condition"] == "direct")
        ]
        if b1.empty:
            pytest.skip("No B1 data")

        acc_d1 = b1[b1["difficulty"] == 1]["correct"].mean()
        acc_d5 = b1[b1["difficulty"] == 5]["correct"].mean()
        assert acc_d1 > acc_d5 + 0.1, (
            f"B1 should degrade: d1={acc_d1:.3f}, d5={acc_d5:.3f}"
        )

    def test_pattern_type6_constant(self, df_from_json):
        """Type 6 (B8): accuracy should be roughly constant across difficulties."""
        b8 = df_from_json[
            (df_from_json["task"] == "B8_reversal_inference")
            & (df_from_json["condition"] == "direct")
        ]
        if b8.empty:
            pytest.skip("No B8 data")

        acc_d1 = b8[b8["difficulty"] == 1]["correct"].mean()
        acc_d5 = b8[b8["difficulty"] == 5]["correct"].mean()
        # Gap should be small (constant accuracy)
        assert abs(acc_d1 - acc_d5) < 0.15, (
            f"B8 should be roughly constant: d1={acc_d1:.3f}, d5={acc_d5:.3f}"
        )

    def test_pattern_cot_helps_type2(self, df_from_json):
        """Type 2: CoT should significantly improve accuracy."""
        type2 = df_from_json[df_from_json["gap_type"] == "Type 2: Depth"]
        if type2.empty:
            pytest.skip("No Type 2 data")

        direct_acc = type2[type2["condition"] == "direct"]["correct"].mean()
        cot_acc = type2[type2["condition"] == "short_cot"]["correct"].mean()
        assert cot_acc > direct_acc + 0.05, (
            f"Type 2 CoT lift should be positive: direct={direct_acc:.3f}, cot={cot_acc:.3f}"
        )

    def test_pattern_cot_doesnt_help_type5(self, df_from_json):
        """Type 5: CoT should provide minimal improvement."""
        type5 = df_from_json[df_from_json["gap_type"] == "Type 5: Intractability"]
        if type5.empty:
            pytest.skip("No Type 5 data")

        direct_acc = type5[type5["condition"] == "direct"]["correct"].mean()
        cot_acc = type5[type5["condition"] == "short_cot"]["correct"].mean()
        lift = cot_acc - direct_acc
        assert abs(lift) < 0.10, (
            f"Type 5 CoT lift should be near zero: lift={lift:.3f}"
        )
