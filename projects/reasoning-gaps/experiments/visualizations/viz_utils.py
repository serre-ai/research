"""Visualization utilities for ReasonGap benchmark.

Thin wrapper around pub_style — the single source of truth for all styling.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

# Ensure project root is on path so pub_style can be imported
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pub_style  # noqa: E402

# Re-export palettes for backward compatibility
GAP_TYPE_COLORS = pub_style.GAP_TYPE_COLORS
CONDITION_COLORS = pub_style.CONDITION_COLORS
MODEL_FAMILY_COLORS = pub_style.FAMILY_COLORS
MODEL_SIZE_MARKERS = pub_style.SIZE_MARKERS


def get_gap_type_color(gap_type: str) -> str:
    return GAP_TYPE_COLORS.get(gap_type, pub_style.FAMILY_COLORS["Other"])


def get_condition_color(condition: str) -> str:
    return CONDITION_COLORS.get(condition, pub_style.FAMILY_COLORS["Other"])


def get_family_color(family: str) -> str:
    return MODEL_FAMILY_COLORS.get(family, pub_style.FAMILY_COLORS["Other"])


def get_size_marker(size: str) -> str:
    return MODEL_SIZE_MARKERS.get(size, "o")


# Delegate to pub_style
save_figure = pub_style.savefig
add_significance_bars = pub_style.add_significance_bracket
format_p_value = pub_style.format_p
add_effect_size_text = pub_style.effect_size_annotation


def add_gridlines(
    ax: plt.Axes,
    which: str = "major",
    axis: str = "y",
    alpha: float = 0.25,
):
    """Add gridlines (y-only by default, matching pub_style)."""
    ax.grid(True, which=which, axis=axis, alpha=alpha)


def create_subplot_grid(
    n_plots: int,
    ncols: int = 3,
    figsize_per_plot: Tuple[float, float] = (4, 3),
    **subplot_kwargs,
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Create grid of subplots with NeurIPS-compliant total width."""
    nrows = int(np.ceil(n_plots / ncols))
    # Clamp total width to NeurIPS full width
    w = min(figsize_per_plot[0] * ncols, pub_style.FULL_W)
    h = figsize_per_plot[1] * nrows
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, h), **subplot_kwargs)

    if nrows == 1 and ncols == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)

    return fig, axes


def add_correlation_line(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    color: str = "0.4",
    linestyle: str = "--",
    label: Optional[str] = None,
):
    """Add OLS trend line to scatter plot."""
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, p(x_line), color=color, linestyle=linestyle,
            linewidth=1.0, label=label, alpha=0.6)


# Initialize style on import
pub_style.setup(usetex=True)
