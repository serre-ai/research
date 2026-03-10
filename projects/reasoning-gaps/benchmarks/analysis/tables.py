"""Generate paper-ready tables for the NeurIPS submission."""

from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.loader import (
    TASK_GAP_TYPE,
    TASK_ORDER,
    TASK_SHORT_LABELS,
    GAP_TYPE_ORDER,
    CONDITION_ORDER,
)
from analysis.statistics import bootstrap_ci


def main_accuracy_table(df: pd.DataFrame) -> pd.DataFrame:
    """Table 1: Overall accuracy by task and model.

    Rows: tasks (B1-B9) in canonical order.
    Columns: models (sorted alphabetically).
    Values: overall accuracy (float).
    """
    # Filter to 'direct' condition for the main table
    # If no condition filter is desired, remove the filter below
    pivot = df.pivot_table(
        values="correct",
        index="task",
        columns="model",
        aggfunc="mean",
    )

    # Reindex rows to canonical task order (only tasks present in data)
    task_order = [t for t in TASK_ORDER if t in pivot.index]
    pivot = pivot.reindex(task_order)

    # Sort columns alphabetically
    pivot = pivot[sorted(pivot.columns)]

    # Rename index for display
    pivot.index = [TASK_SHORT_LABELS.get(t, t) for t in pivot.index]

    return pivot


def accuracy_by_condition_table(df: pd.DataFrame) -> pd.DataFrame:
    """Accuracy for each task broken down by condition.

    Rows: tasks (B1-B9).
    Columns: MultiIndex of (condition, model) or just conditions if
    aggregating across models.

    Returns a table with rows=tasks, columns=conditions, values=mean accuracy
    across all models (to show intervention effect independent of model).
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

    pivot.index = [TASK_SHORT_LABELS.get(t, t) for t in pivot.index]

    return pivot


def cot_lift_table(df: pd.DataFrame) -> pd.DataFrame:
    """CoT lift = (CoT accuracy - direct accuracy) grouped by gap type.

    Rows: gap types (Type 1-6).
    Columns: conditions (short_cot, budget_cot, tool).
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

    # Sort columns
    col_order = [c for c in CONDITION_ORDER if c in lift.columns and c != "direct"]
    lift = lift[col_order]

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


def to_latex(
    df: pd.DataFrame,
    caption: str,
    label: str,
    float_format: str = ".2f",
    highlight_max: bool = False,
    highlight_min: bool = False,
) -> str:
    """Convert a DataFrame to NeurIPS-formatted LaTeX table.

    Uses booktabs style with proper formatting for camera-ready papers.

    Args:
        df: DataFrame to convert.
        caption: Table caption.
        label: LaTeX label for referencing.
        float_format: Format string for float values (default: '.2f').
        highlight_max: Bold the maximum value in each row.
        highlight_min: Bold the minimum value in each row.

    Returns:
        LaTeX string for the table.
    """
    n_cols = len(df.columns) + (1 if df.index.name or True else 0)

    # Format numeric values
    # Convert to object dtype so we can mix strings and NaN freely
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
                    fmt_val = f"{val:{float_format}}"
                    if is_extreme:
                        formatted.at[idx, col] = f"\\textbf{{{fmt_val}}}"
                    else:
                        formatted.at[idx, col] = fmt_val
            else:
                formatted[col] = df[col].apply(
                    lambda v: f"{v:{float_format}}" if pd.notna(v) else "--"
                )

    # Build LaTeX
    lines = []
    lines.append("\\begin{table}[t]")
    lines.append("\\centering")
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{{label}}}")
    lines.append("\\small")

    # Column spec: left-aligned index, centered data columns
    col_spec = "l" + "c" * len(df.columns)
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append("\\toprule")

    # Header row
    header_parts = [""]  # index column
    for col in df.columns:
        # Escape underscores in column names
        col_str = str(col).replace("_", "\\_")
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
    lines.append("\\end{table}")

    return "\n".join(lines)
