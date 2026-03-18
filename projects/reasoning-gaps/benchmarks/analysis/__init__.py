"""ReasonGap analysis pipeline.

Transforms raw evaluation results into paper-ready tables, figures,
and statistical summaries for the NeurIPS submission.
"""

from analysis.loader import (
    load_results,
    CONDITION_LABELS,
    CONDITION_ORDER,
    MODEL_DISPLAY_NAMES,
    MODEL_DISPLAY_ORDER,
    MODEL_FAMILIES,
    TASK_GAP_TYPE,
    get_display_name,
)
from analysis.tables import (
    main_accuracy_table,
    accuracy_by_condition_table,
    cot_lift_table,
    scale_analysis_table,
    tool_use_comparison_table,
    budget_sensitivity_table,
    to_latex,
)
from analysis.plots import (
    plot_accuracy_vs_difficulty,
    plot_cot_lift_heatmap,
    plot_phase_transition,
    plot_scale_sensitivity,
    plot_intervention_comparison,
    plot_tool_use_comparison,
    plot_budget_sensitivity,
)
from analysis.statistics import (
    bootstrap_ci,
    mcnemar_test,
    compute_all_cis,
    pairwise_model_comparison,
)
from analysis.stats import generate_stats_tex

__all__ = [
    "load_results",
    "CONDITION_LABELS",
    "CONDITION_ORDER",
    "MODEL_DISPLAY_NAMES",
    "MODEL_DISPLAY_ORDER",
    "MODEL_FAMILIES",
    "TASK_GAP_TYPE",
    "get_display_name",
    "main_accuracy_table",
    "accuracy_by_condition_table",
    "cot_lift_table",
    "scale_analysis_table",
    "tool_use_comparison_table",
    "budget_sensitivity_table",
    "to_latex",
    "plot_accuracy_vs_difficulty",
    "plot_cot_lift_heatmap",
    "plot_phase_transition",
    "plot_scale_sensitivity",
    "plot_intervention_comparison",
    "plot_tool_use_comparison",
    "plot_budget_sensitivity",
    "bootstrap_ci",
    "mcnemar_test",
    "compute_all_cis",
    "pairwise_model_comparison",
    "generate_stats_tex",
]
