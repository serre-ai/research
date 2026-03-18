"""Generate paper-ready tables for the NeurIPS submission."""

from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.loader import (
    CONDITION_LABELS,
    CONDITION_ORDER,
    GAP_TYPE_ORDER,
    MODEL_DISPLAY_NAMES,
    MODEL_DISPLAY_ORDER,
    TASK_GAP_TYPE,
    TASK_ORDER,
    TASK_SHORT_LABELS,
    get_display_name,
)
from analysis.statistics import bootstrap_ci


def main_accuracy_table(df: pd.DataFrame) -> pd.DataFrame:
    """Table 1: Overall accuracy by task and model.

    Rows: tasks (B1-B9) in canonical order.
    Columns: models using display names, in MODEL_DISPLAY_ORDER.
    Values: overall accuracy (float).
    """
    pivot = df.pivot_table(
        values="correct",
        index="task",
        columns="model",
        aggfunc="mean",
    )

    # Reindex rows to canonical task order (only tasks present in data)
    task_order = [t for t in TASK_ORDER if t in pivot.index]
    pivot = pivot.reindex(task_order)

    # Rename columns to display names
    pivot = pivot.rename(columns=get_display_name)

    # Reorder columns by MODEL_DISPLAY_ORDER (only those present)
    col_order = [c for c in MODEL_DISPLAY_ORDER if c in pivot.columns]
    # Append any remaining columns not in MODEL_DISPLAY_ORDER
    remaining = [c for c in pivot.columns if c not in col_order]
    pivot = pivot[col_order + remaining]

    # Rename index for display
    pivot.index = [TASK_SHORT_LABELS.get(t, t) for t in pivot.index]

    return pivot


def accuracy_by_condition_table(df: pd.DataFrame) -> pd.DataFrame:
    """Accuracy for each task broken down by condition.

    Rows: tasks (B1-B9).
    Columns: all conditions present in data, with display labels.
    Values: mean accuracy across all models.
    """
    pivot = df.pivot_table(
        values="correct",
        index="task",
        columns="condition",
        aggfunc="mean",
    )

    # Reindex
    task_order = [t for t in TASK_ORDER if t in pivot.index]
    pivot = pivot.reindex(task_order)

    cond_order = [c for c in CONDITION_ORDER if c in pivot.columns]
    pivot = pivot[cond_order]

    # Rename columns to display labels
    pivot = pivot.rename(columns=CONDITION_LABELS)

    pivot.index = [TASK_SHORT_LABELS.get(t, t) for t in pivot.index]

    return pivot


def cot_lift_table(df: pd.DataFrame) -> pd.DataFrame:
    """CoT lift = (CoT accuracy - direct accuracy) grouped by gap type.

    Rows: gap types (Type 1-6).
    Columns: conditions (short_cot, budget_cot, tool_use if present).
    Values: mean lift over direct condition.

    Key result: Types 2,3 benefit most; Types 5,6 don't.
    """
    # Compute accuracy per (gap_type, condition) aggregated across all models
    acc = df.pivot_table(
        values="correct",
        index="gap_type",
        columns="condition",
        aggfunc="mean",
    )

    if "direct" not in acc.columns:
        return pd.DataFrame()

    # Compute lift relative to direct
    lift = pd.DataFrame(index=acc.index)
    for cond in acc.columns:
        if cond != "direct":
            lift[cond] = acc[cond] - acc["direct"]

    # Reindex to canonical gap type order
    gap_order = [g for g in GAP_TYPE_ORDER if g in lift.index]
    lift = lift.reindex(gap_order)

    # Sort columns by CONDITION_ORDER (excluding direct)
    col_order = [c for c in CONDITION_ORDER if c in lift.columns and c != "direct"]
    lift = lift[col_order]

    # Rename columns to display labels
    lift = lift.rename(columns=CONDITION_LABELS)

    return lift


def scale_analysis_table(df: pd.DataFrame) -> pd.DataFrame:
    """Accuracy by model size within each family, grouped by gap type.

    Rows: gap types.
    Columns: model sizes (small, medium, large) or actual parameter counts.
    Shows which gap types narrow with scale.
    """
    # Filter to models with known sizes
    df_sized = df[df["model_size"].notna()].copy()

    if df_sized.empty:
        return pd.DataFrame()

    # Bin model sizes into categories
    def _size_bin(size: float) -> str:
        if size <= 10:
            return "Small (<=10B)"
        elif size <= 80:
            return "Medium (10-80B)"
        else:
            return "Large (>80B)"

    df_sized["size_bin"] = df_sized["model_size"].apply(_size_bin)

    pivot = df_sized.pivot_table(
        values="correct",
        index="gap_type",
        columns="size_bin",
        aggfunc="mean",
    )

    # Reindex
    gap_order = [g for g in GAP_TYPE_ORDER if g in pivot.index]
    pivot = pivot.reindex(gap_order)

    # Order columns by size
    size_order = ["Small (<=10B)", "Medium (10-80B)", "Large (>80B)"]
    col_order = [c for c in size_order if c in pivot.columns]
    pivot = pivot[col_order]

    return pivot


def tool_use_comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    """Accuracy comparison for tasks with tool_use data.

    Rows: tasks that have tool_use data (e.g. B5, B6).
    Columns: conditions (Direct, Short CoT, Budget CoT, Tool Use).
    Values: mean accuracy across models that have tool_use data.

    Returns empty DataFrame if no tool_use data exists.
    """
    if "tool_use" not in df["condition"].unique():
        return pd.DataFrame()

    # Find models that have tool_use data
    tool_use_models = df[df["condition"] == "tool_use"]["model"].unique()
    # Find tasks that have tool_use data
    tool_use_tasks = df[df["condition"] == "tool_use"]["task"].unique()

    if len(tool_use_models) == 0 or len(tool_use_tasks) == 0:
        return pd.DataFrame()

    # Filter to tool_use models and tool_use tasks only
    mask = (df["model"].isin(tool_use_models)) & (df["task"].isin(tool_use_tasks))
    df_sub = df[mask]

    pivot = df_sub.pivot_table(
        values="correct",
        index="task",
        columns="condition",
        aggfunc="mean",
    )

    # Reindex rows
    task_order = [t for t in TASK_ORDER if t in pivot.index]
    pivot = pivot.reindex(task_order)

    # Reindex columns
    cond_order = [c for c in CONDITION_ORDER if c in pivot.columns]
    pivot = pivot[cond_order]

    # Rename
    pivot = pivot.rename(columns=CONDITION_LABELS)
    pivot.index = [TASK_SHORT_LABELS.get(t, t) for t in pivot.index]

    return pivot


def budget_sensitivity_table(df: pd.DataFrame) -> pd.DataFrame:
    """Accuracy by budget multiplier for B2 and B3.

    Budget sweep conditions are encoded in the condition field as
    'budget_cot_<mult>x' (e.g., 'budget_cot_0.25x').

    Rows: tasks (B2, B3).
    Columns: budget multipliers (0.25x, 0.5x, 1.0x, 2.0x, 4.0x).
    Values: accuracy averaged across all models.

    Returns empty DataFrame if no budget sweep data exists.
    """
    # Identify budget sweep conditions
    budget_sweep_conds = sorted(
        c for c in df["condition"].unique()
        if c.startswith("budget_cot_") and c.endswith("x")
    )

    if not budget_sweep_conds:
        return pd.DataFrame()

    target_tasks = ["B2_nested_boolean", "B3_permutation_composition"]
    tasks_present = [t for t in target_tasks if t in df["task"].unique()]

    if not tasks_present:
        return pd.DataFrame()

    # Filter to budget sweep data and target tasks
    mask = (df["condition"].isin(budget_sweep_conds)) & (df["task"].isin(tasks_present))
    df_sub = df[mask]

    pivot = df_sub.pivot_table(
        values="correct",
        index="task",
        columns="condition",
        aggfunc="mean",
    )

    # Sort columns by multiplier value
    def _parse_mult(cond: str) -> float:
        return float(cond.replace("budget_cot_", "").rstrip("x"))

    col_order = sorted(
        [c for c in pivot.columns if c in budget_sweep_conds],
        key=_parse_mult,
    )
    pivot = pivot[col_order]

    # Rename columns to display format (e.g., "0.25x")
    col_rename = {c: c.replace("budget_cot_", "") for c in col_order}
    pivot = pivot.rename(columns=col_rename)

    # Reindex rows
    task_order = [t for t in TASK_ORDER if t in pivot.index]
    pivot = pivot.reindex(task_order)

    pivot.index = [TASK_SHORT_LABELS.get(t, t) for t in pivot.index]

    return pivot


def to_latex(
    df: pd.DataFrame,
    caption: str = "",
    label: str = "",
    float_format: str = ".2f",
    highlight_max: bool = False,
    highlight_min: bool = False,
    tabular_only: bool = False,
    rotated_headers: bool = False,
    strip_leading_zero: bool = False,
    sign_prefix: bool = False,
) -> str:
    """Convert a DataFrame to NeurIPS-formatted LaTeX table.

    Uses booktabs style with proper formatting for camera-ready papers.

    Args:
        df: DataFrame to convert.
        caption: Table caption (ignored when tabular_only=True).
        label: LaTeX label for referencing (ignored when tabular_only=True).
        float_format: Format string for float values (default: '.2f').
        highlight_max: Bold the maximum value in each row.
        highlight_min: Bold the minimum value in each row.
        tabular_only: If True, output only the tabular environment (no
            table wrapper, caption, or label). The paper can wrap it.
        rotated_headers: If True, rotate column headers with rotatebox{70}.
        strip_leading_zero: If True, format '.83' instead of '0.83'.
        sign_prefix: If True, prepend +/- sign to values.

    Returns:
        LaTeX string for the table (or tabular fragment).
    """

    def _fmt_val(val: float) -> str:
        """Format a single float value with all active options."""
        if pd.isna(val):
            return "--"
        s = f"{val:{float_format}}"
        if strip_leading_zero:
            if s.startswith("0."):
                s = s[1:]
            elif s.startswith("-0."):
                s = "-" + s[2:]
        if sign_prefix and val >= 0:
            s = "+" + s
        return s

    # Format numeric values
    formatted = df.astype(object).copy()
    for col in df.columns:
        if df[col].dtype in (np.float64, np.float32, float):
            if highlight_max or highlight_min:
                for idx in df.index:
                    val = df.at[idx, col]
                    if pd.isna(val):
                        formatted.at[idx, col] = "--"
                        continue
                    row_vals = df.loc[idx].dropna()
                    is_extreme = False
                    if highlight_max and len(row_vals) > 0 and val == row_vals.max():
                        is_extreme = True
                    if highlight_min and len(row_vals) > 0 and val == row_vals.min():
                        is_extreme = True
                    fmt_val = _fmt_val(val)
                    if is_extreme:
                        formatted.at[idx, col] = f"\\textbf{{{fmt_val}}}"
                    else:
                        formatted.at[idx, col] = fmt_val
            else:
                formatted[col] = df[col].apply(_fmt_val)

    # Build LaTeX
    lines = []

    if not tabular_only:
        lines.append("\\begin{table}[t]")
        lines.append("\\centering")
        if caption:
            lines.append(f"\\caption{{{caption}}}")
        if label:
            lines.append(f"\\label{{{label}}}")
        lines.append("\\small")

    if rotated_headers:
        lines.append("\\setlength{\\tabcolsep}{2pt}")

    # Column spec: left-aligned index, centered data columns
    col_spec = "l" + "c" * len(df.columns)
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append("\\toprule")

    # Header row
    header_parts = [""]  # index column
    for col in df.columns:
        col_str = str(col).replace("_", "\\_")
        if rotated_headers:
            col_str = f"\\rotatebox{{70}}{{{col_str}}}"
        header_parts.append(col_str)
    lines.append(" & ".join(header_parts) + " \\\\")
    lines.append("\\midrule")

    # Data rows
    for idx in formatted.index:
        row_parts = [str(idx).replace("_", "\\_")]
        for col in formatted.columns:
            val = formatted.at[idx, col]
            row_parts.append(str(val))
        lines.append(" & ".join(row_parts) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")

    if not tabular_only:
        lines.append("\\end{table}")

    return "\n".join(lines)
