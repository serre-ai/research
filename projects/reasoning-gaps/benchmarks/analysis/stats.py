"""Generate LaTeX \\newcommand macros for paper-wide statistics.

Produces a `stats.tex` file that the paper can \\input{} to reference
computed values without manual copy-paste.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from analysis.loader import (
    CONDITION_LABELS,
    CONDITION_ORDER,
    GAP_TYPE_ORDER,
    TASK_ORDER,
    TASK_SHORT_LABELS,
)


def _latex_int(n: int) -> str:
    """Format an integer for LaTeX with thousand separators using {,}."""
    s = f"{n:,}"
    return s.replace(",", "{,}")


def _safe_name(s: str) -> str:
    """Convert a string into a valid LaTeX command suffix.

    E.g. 'B3_permutation_composition' -> 'BThreePermComp',
         'short_cot' -> 'ShortCot'.
    """
    # Map task short codes
    task_name_map = {
        "B1": "BOne", "B2": "BTwo", "B3": "BThree", "B4": "BFour",
        "B5": "BFive", "B6": "BSix", "B7": "BSeven", "B8": "BEight",
        "B9": "BNine",
    }

    # Handle full task names like "B3_permutation_composition"
    for prefix, replacement in task_name_map.items():
        if s.startswith(prefix + "_") or s == prefix:
            return replacement

    # Handle condition names
    cond_map = {
        "direct": "Direct",
        "short_cot": "ShortCot",
        "budget_cot": "BudgetCot",
        "tool_use": "ToolUse",
    }
    if s in cond_map:
        return cond_map[s]

    # Generic: CamelCase conversion
    parts = s.replace("-", "_").split("_")
    return "".join(p.capitalize() for p in parts if p)


def generate_stats_tex(df: pd.DataFrame, output_path: str) -> None:
    """Generate LaTeX \\newcommand definitions for paper-wide statistics.

    The output file can be included in the paper with \\input{stats}.
    All commands are prefixed with \\stat to avoid collisions.

    Args:
        df: Full evaluation DataFrame (from loader.load_results).
        output_path: Path to write the stats.tex file.
    """
    commands: list[str] = []

    def _cmd(name: str, value: str) -> None:
        commands.append(f"\\newcommand{{\\stat{name}}}{{{value}}}")

    # -----------------------------------------------------------------------
    # Overall dataset statistics
    # -----------------------------------------------------------------------
    _cmd("TotalInstances", _latex_int(len(df)))
    _cmd("TotalModels", str(df["model"].nunique()))
    _cmd("TotalTasks", str(df["task"].nunique()))
    _cmd("TotalConditions", str(df["condition"].nunique()))

    # -----------------------------------------------------------------------
    # Overall accuracy by condition
    # -----------------------------------------------------------------------
    cond_acc = df.groupby("condition")["correct"].mean()
    for cond in CONDITION_ORDER:
        if cond in cond_acc.index:
            _cmd(f"Overall{_safe_name(cond)}", f"{cond_acc[cond]:.3f}")

    # -----------------------------------------------------------------------
    # CoT lift for Types 2,3 vs Types 5,6
    # -----------------------------------------------------------------------
    for label, types, suffix in [
        ("TypesTwoThree", ["Type 2: Depth", "Type 3: Serial"], "TypesTwoThree"),
        ("TypesFiveSix", ["Type 5: Intractability", "Type 6: Architectural"], "TypesFiveSix"),
    ]:
        type_df = df[df["gap_type"].isin(types)]
        if type_df.empty:
            continue
        type_cond = type_df.groupby("condition")["correct"].mean()
        if "direct" in type_cond.index and "short_cot" in type_cond.index:
            lift = type_cond["short_cot"] - type_cond["direct"]
            sign = "+" if lift >= 0 else ""
            _cmd(f"CotLift{suffix}", f"{sign}{lift:.3f}")
            _cmd(f"CotLift{suffix}Pct", f"{abs(lift) * 100:.1f}")

    # -----------------------------------------------------------------------
    # CoT lift per individual gap type (for Type 5/6 split in paper)
    # -----------------------------------------------------------------------
    for gap_type, suffix in [
        ("Type 1: Sensitivity", "TypeOne"),
        ("Type 2: Depth", "TypeTwo"),
        ("Type 3: Serial", "TypeThree"),
        ("Type 4: Algorithmic", "TypeFour"),
        ("Type 5: Intractability", "TypeFive"),
        ("Type 6: Architectural", "TypeSix"),
    ]:
        gt_df = df[df["gap_type"] == gap_type]
        if gt_df.empty:
            continue
        gt_cond = gt_df.groupby("condition")["correct"].mean()
        if "direct" in gt_cond.index and "short_cot" in gt_cond.index:
            lift = gt_cond["short_cot"] - gt_cond["direct"]
            sign = "+" if lift >= 0 else ""
            _cmd(f"CotLift{suffix}", f"{sign}{lift:.3f}")

    # -----------------------------------------------------------------------
    # CoT lift per task (for B8/B9 individual reporting)
    # -----------------------------------------------------------------------
    for task in TASK_ORDER:
        task_df = df[df["task"] == task]
        if task_df.empty:
            continue
        task_safe = _safe_name(task)
        task_cond = task_df.groupby("condition")["correct"].mean()
        if "direct" in task_cond.index and "short_cot" in task_cond.index:
            lift = task_cond["short_cot"] - task_cond["direct"]
            sign = "+" if lift >= 0 else ""
            _cmd(f"CotLift{task_safe}", f"{sign}{lift:.3f}")

    # -----------------------------------------------------------------------
    # Tool use lift for Type 4 (Algorithmic)
    # -----------------------------------------------------------------------
    type4_df = df[df["gap_type"] == "Type 4: Algorithmic"]
    if not type4_df.empty:
        t4_cond = type4_df.groupby("condition")["correct"].mean()
        if "direct" in t4_cond.index and "tool_use" in t4_cond.index:
            lift = t4_cond["tool_use"] - t4_cond["direct"]
            sign = "+" if lift >= 0 else ""
            _cmd("ToolUseLiftTypeFour", f"{sign}{lift:.3f}")

    # -----------------------------------------------------------------------
    # Per-task, per-condition means
    # -----------------------------------------------------------------------
    for task in TASK_ORDER:
        task_df = df[df["task"] == task]
        if task_df.empty:
            continue
        task_safe = _safe_name(task)
        for cond in CONDITION_ORDER:
            cond_df = task_df[task_df["condition"] == cond]
            if cond_df.empty:
                continue
            mean_acc = cond_df["correct"].mean()
            cond_safe = _safe_name(cond)
            _cmd(f"{task_safe}{cond_safe}Mean", f"{mean_acc:.3f}")

    # -----------------------------------------------------------------------
    # Write output
    # -----------------------------------------------------------------------
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    header = "% Auto-generated by analyze.py — do not edit manually\n"
    out.write_text(header + "\n".join(commands) + "\n")
