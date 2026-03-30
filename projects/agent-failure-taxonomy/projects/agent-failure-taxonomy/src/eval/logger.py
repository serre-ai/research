"""
Structured logging for agent failure reproduction experiments.

Logs all trials in JSONL format for reproducibility and analysis.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import asdict

from frameworks.base import AgentTrace, AgentArchitecture


class ExperimentLogger:
    """
    Logs experimental trials in structured format.

    Each trial is logged as a single JSON line containing:
    - Experimental parameters (framework, model, scenario, seed)
    - Complete agent trace (steps, tool calls, outputs)
    - Failure classification
    - Cost and timing metrics
    """

    def __init__(self, output_path: str, experiment_name: str):
        self.output_path = Path(output_path)
        self.experiment_name = experiment_name
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create output file with header if doesn't exist
        if not self.output_path.exists():
            self._write_header()

    def _write_header(self):
        """Write JSONL header with schema information."""
        header = {
            "_schema": "agent_failure_trial_v1",
            "_experiment": self.experiment_name,
            "_created_at": datetime.utcnow().isoformat(),
            "_fields": [
                "trial_id", "framework", "model", "scenario", "seed",
                "trace", "failure_detected", "reproduction_success",
                "tokens", "cost_usd", "duration_seconds", "timestamp"
            ]
        }

        with open(self.output_path, 'a') as f:
            f.write(json.dumps(header) + '\n')

    def log_trial(
        self,
        trial_id: str,
        framework: str,
        architecture: AgentArchitecture,
        model: str,
        scenario: str,
        trace: AgentTrace,
        failure_detected: Optional[str],
        reproduction_success: bool,
        duration_seconds: float,
        seed: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a single experimental trial.

        Args:
            trial_id: Unique identifier for this trial
            framework: Framework name (e.g., "react_langchain")
            architecture: Architecture type from taxonomy
            model: Model identifier
            scenario: Failure scenario ID
            trace: Complete agent execution trace
            failure_detected: Type of failure detected, if any
            reproduction_success: Whether expected failure was reproduced
            duration_seconds: Trial execution time
            seed: Random seed used
            metadata: Additional experiment-specific data
        """
        record = {
            "trial_id": trial_id,
            "framework": framework,
            "architecture": architecture.value,
            "model": model,
            "scenario": scenario,
            "seed": seed,
            "trace": self._serialize_trace(trace),
            "failure_detected": failure_detected,
            "reproduction_success": reproduction_success,
            "metrics": {
                "total_tokens": trace.total_tokens,
                "total_cost_usd": trace.total_cost_usd,
                "duration_seconds": duration_seconds,
                "num_steps": len(trace.steps),
                "timeout": trace.timeout,
                "error": trace.error,
            },
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        with open(self.output_path, 'a') as f:
            f.write(json.dumps(record) + '\n')

    def _serialize_trace(self, trace: AgentTrace) -> Dict[str, Any]:
        """Convert AgentTrace to JSON-serializable dict."""
        return {
            "task": trace.task,
            "steps": [
                {
                    "step_number": step.step_number,
                    "observation": step.observation,
                    "thought": step.thought,
                    "action": step.action,
                    "action_input": step.action_input,
                    "tool_calls": [
                        {
                            "tool_name": tc.tool_name,
                            "parameters": tc.parameters,
                            "result": str(tc.result) if tc.result else None,
                            "error": tc.error,
                            "hallucinated": tc.hallucinated
                        }
                        for tc in step.tool_calls
                    ],
                    "tokens_used": step.tokens_used,
                    "cost_usd": step.cost_usd
                }
                for step in trace.steps
            ],
            "final_output": trace.final_output,
            "completed": trace.completed,
            "failure_detected": trace.failure_detected
        }

    def load_trials(self) -> list:
        """Load all trials from log file (excluding header)."""
        trials = []

        if not self.output_path.exists():
            return trials

        with open(self.output_path, 'r') as f:
            for line in f:
                record = json.loads(line)
                # Skip schema header
                if "_schema" not in record:
                    trials.append(record)

        return trials

    def get_checkpoint(self, scenario: str, framework: str, model: str) -> Optional[int]:
        """
        Get the last completed trial number for resuming experiments.

        Returns:
            Number of completed trials for this configuration, or 0 if none
        """
        trials = self.load_trials()
        completed = [
            t for t in trials
            if t["scenario"] == scenario
            and t["framework"] == framework
            and t["model"] == model
        ]

        return len(completed)
