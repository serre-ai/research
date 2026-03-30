"""
Logging utilities for agent failure experiments.
Captures full agent transcripts with structured metadata.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class TranscriptLogger:
    """Logs agent transcripts with structured format for analysis."""

    def __init__(self, experiment_name: str, output_dir: str = "experiments/data"):
        self.experiment_name = experiment_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_run(self,
                   run_id: str,
                   failure_instance: str,
                   framework: str,
                   model: str,
                   task: str) -> Dict[str, Any]:
        """Initialize a new run with metadata."""
        return {
            "run_id": run_id,
            "failure_instance": failure_instance,
            "framework": framework,
            "model": model,
            "task": task,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "cost_usd": 0.0,
            "turns": 0,
            "tokens_total": 0,
            "outcome": {},
            "transcript": [],
            "annotations": {}
        }

    def add_turn(self,
                 run_data: Dict[str, Any],
                 turn: int,
                 observation: str,
                 thought: str,
                 action: str,
                 tokens: Optional[int] = None,
                 cost: Optional[float] = None) -> None:
        """Add a single turn to the transcript."""
        turn_data = {
            "turn": turn,
            "observation": observation,
            "thought": thought,
            "action": action
        }

        if tokens:
            turn_data["tokens"] = tokens
        if cost:
            turn_data["cost_usd"] = cost
            run_data["cost_usd"] += cost

        run_data["transcript"].append(turn_data)
        run_data["turns"] = turn

        if tokens:
            run_data["tokens_total"] += tokens

    def set_outcome(self,
                    run_data: Dict[str, Any],
                    failure_reproduced: bool,
                    failure_category: str,
                    task_completed: bool,
                    **kwargs) -> None:
        """Set the outcome of the run."""
        run_data["outcome"] = {
            "failure_reproduced": failure_reproduced,
            "failure_category": failure_category,
            "task_completed": task_completed,
            **kwargs
        }

    def add_annotations(self,
                       run_data: Dict[str, Any],
                       llm_limitation: str,
                       severity: str,
                       notes: str = "") -> None:
        """Add human annotations about the failure."""
        run_data["annotations"] = {
            "llm_limitation": llm_limitation,
            "severity": severity,
            "notes": notes
        }

    def save_run(self, run_data: Dict[str, Any]) -> str:
        """Save run to JSON file."""
        filename = f"{run_data['run_id']}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(run_data, f, indent=2)

        return str(filepath)

    def load_run(self, run_id: str) -> Dict[str, Any]:
        """Load a previously saved run."""
        filename = f"{run_id}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'r') as f:
            return json.load(f)


class BatchLogger:
    """Aggregates results across multiple runs."""

    def __init__(self, output_dir: str = "experiments/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def aggregate_runs(self, run_files: List[str]) -> Dict[str, Any]:
        """Aggregate multiple run files into summary statistics."""
        runs = []
        for filepath in run_files:
            with open(filepath, 'r') as f:
                runs.append(json.load(f))

        if not runs:
            return {}

        # Group by failure instance
        by_failure = {}
        for run in runs:
            fi = run["failure_instance"]
            if fi not in by_failure:
                by_failure[fi] = []
            by_failure[fi].append(run)

        # Compute aggregates
        results = {}
        for fi, fi_runs in by_failure.items():
            total_runs = len(fi_runs)
            reproduced = sum(1 for r in fi_runs if r["outcome"].get("failure_reproduced", False))
            total_cost = sum(r["cost_usd"] for r in fi_runs)

            # Average turns to failure (only for runs where failure occurred)
            failure_turns = [r["outcome"].get("turns_to_failure", 0)
                           for r in fi_runs
                           if r["outcome"].get("failure_reproduced", False)]

            results[fi] = {
                "failure_instance": fi,
                "total_runs": total_runs,
                "reproduction_rate": reproduced / total_runs if total_runs > 0 else 0,
                "mean_turns_to_failure": sum(failure_turns) / len(failure_turns) if failure_turns else 0,
                "mean_cost_per_run": total_cost / total_runs if total_runs > 0 else 0,
                "total_cost_usd": total_cost
            }

            # Framework breakdown
            by_framework = {}
            for run in fi_runs:
                fw = run["framework"]
                if fw not in by_framework:
                    by_framework[fw] = {"runs": 0, "reproduced": 0}
                by_framework[fw]["runs"] += 1
                if run["outcome"].get("failure_reproduced", False):
                    by_framework[fw]["reproduced"] += 1

            for fw, stats in by_framework.items():
                stats["reproduction_rate"] = stats["reproduced"] / stats["runs"] if stats["runs"] > 0 else 0

            results[fi]["framework_breakdown"] = by_framework

        return results

    def save_aggregates(self, results: Dict[str, Any], filename: str = "aggregated_results.json") -> str:
        """Save aggregated results to file."""
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        return str(filepath)


def print_run_summary(run_data: Dict[str, Any]) -> None:
    """Print a human-readable summary of a run."""
    print(f"\n{'='*60}")
    print(f"Run: {run_data['run_id']}")
    print(f"Failure: {run_data['failure_instance']}")
    print(f"Framework: {run_data['framework']}")
    print(f"Model: {run_data['model']}")
    print(f"{'='*60}")
    print(f"Turns: {run_data['turns']}")
    print(f"Total tokens: {run_data['tokens_total']}")
    print(f"Total cost: ${run_data['cost_usd']:.3f}")
    print(f"\nOutcome:")
    print(f"  Failure reproduced: {run_data['outcome'].get('failure_reproduced', 'N/A')}")
    print(f"  Task completed: {run_data['outcome'].get('task_completed', 'N/A')}")
    print(f"  Category: {run_data['outcome'].get('failure_category', 'N/A')}")
    if run_data.get('annotations'):
        print(f"\nAnnotations:")
        print(f"  LLM limitation: {run_data['annotations'].get('llm_limitation', 'N/A')}")
        print(f"  Severity: {run_data['annotations'].get('severity', 'N/A')}")
        if run_data['annotations'].get('notes'):
            print(f"  Notes: {run_data['annotations']['notes']}")
    print(f"{'='*60}\n")
