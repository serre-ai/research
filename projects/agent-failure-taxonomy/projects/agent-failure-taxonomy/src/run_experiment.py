#!/usr/bin/env python3
"""
Main experiment runner for agent failure reproduction experiments.

Usage:
    python run_experiment.py --spec <path-to-spec.yaml> --mode <canary|full>
"""

import argparse
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from frameworks.react_agent import ReActAgent
from scenarios.tool_failures import (
    create_tool_fabrication_scenario,
    create_tool_hallucination_scenario,
    detect_tool_fabrication,
    detect_tool_hallucination
)
from eval.logger import ExperimentLogger


class ExperimentRunner:
    """
    Orchestrates experimental trials across frameworks, models, and scenarios.
    """

    def __init__(self, spec_path: str, mode: str = "canary"):
        self.spec_path = Path(spec_path)
        self.mode = mode

        # Load spec
        with open(self.spec_path) as f:
            self.spec = yaml.safe_load(f)

        # Setup logger
        output_dir = self.spec_path.parent / "data"
        output_file = output_dir / f"{mode}-results.jsonl"
        self.logger = ExperimentLogger(
            output_path=str(output_file),
            experiment_name=self.spec["name"]
        )

        # Budget tracking
        self.total_cost = 0.0
        self.max_budget = self.spec["budget"]["max_allowed_usd"]

    def run(self):
        """Execute the experiment according to spec and mode."""
        print(f"🧪 Starting {self.mode} experiment: {self.spec['name']}")
        print(f"📋 Spec: {self.spec_path}")
        print(f"💰 Budget: ${self.max_budget:.2f}")
        print()

        # Get configuration based on mode
        config = self.spec["canary"] if self.mode == "canary" else self.spec["design"]

        # Run trials
        trials_run = 0
        trials_successful = 0

        for framework_name in config.get("frameworks", ["react_langchain"]):
            for model in config.get("models", []):
                for scenario_id in config.get("failure_scenarios", []):
                    instances = config.get("instances_per_scenario", 3)

                    print(f"🔬 Testing: {scenario_id} | {framework_name} | {model}")

                    for instance_num in range(instances):
                        # Check budget
                        if self.total_cost >= self.max_budget:
                            print(f"⚠️  Budget limit reached: ${self.total_cost:.4f}")
                            return

                        # Run trial
                        success = self._run_trial(
                            framework_name=framework_name,
                            model=model,
                            scenario_id=scenario_id,
                            instance_num=instance_num,
                            seed=42 + instance_num
                        )

                        trials_run += 1
                        if success:
                            trials_successful += 1

                        print(f"  Trial {instance_num + 1}/{instances}: {'✓' if success else '✗'}")

        # Summary
        print()
        print("=" * 60)
        print(f"✅ Experiment complete!")
        print(f"📊 Trials run: {trials_run}")
        print(f"🎯 Reproductions: {trials_successful}/{trials_run} ({100*trials_successful/trials_run if trials_run else 0:.1f}%)")
        print(f"💸 Total cost: ${self.total_cost:.4f}")
        print(f"📁 Results: {self.logger.output_path}")

    def _run_trial(
        self,
        framework_name: str,
        model: str,
        scenario_id: str,
        instance_num: int,
        seed: int
    ) -> bool:
        """
        Run a single experimental trial.

        Returns:
            True if expected failure was successfully reproduced
        """
        trial_id = f"{framework_name}_{model}_{scenario_id}_{instance_num:03d}"

        # Initialize framework
        framework = self._create_framework(framework_name, model, seed)

        # Get scenario
        task, tools, expected = self._get_scenario(scenario_id)

        # Run agent
        start_time = time.time()
        try:
            trace = framework.run_task(task, tools)
            duration = time.time() - start_time

            # Detect failure
            failure_detected = self._detect_failure(scenario_id, trace, tools)
            reproduction_success = (failure_detected is not None)

            # Update cost
            self.total_cost += trace.total_cost_usd

            # Log trial
            self.logger.log_trial(
                trial_id=trial_id,
                framework=framework_name,
                architecture=framework.architecture,
                model=model,
                scenario=scenario_id,
                trace=trace,
                failure_detected=failure_detected,
                reproduction_success=reproduction_success,
                duration_seconds=duration,
                seed=seed,
                metadata={
                    "expected": expected,
                    "instance_num": instance_num
                }
            )

            return reproduction_success

        except Exception as e:
            print(f"    ⚠️  Trial error: {e}")
            return False

    def _create_framework(self, name: str, model: str, seed: int):
        """Create framework instance."""
        spec = self.spec["design"]

        if name == "react_langchain":
            return ReActAgent(
                model_name=model,
                temperature=spec.get("temperature", 0.7),
                max_iterations=spec.get("max_iterations", 20),
                timeout_seconds=spec.get("timeout_seconds", 120),
                seed=seed
            )
        else:
            raise ValueError(f"Unknown framework: {name}")

    def _get_scenario(self, scenario_id: str):
        """Get scenario definition."""
        scenarios = {
            "tool_fabrication": create_tool_fabrication_scenario,
            "tool_hallucination": create_tool_hallucination_scenario,
        }

        if scenario_id not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_id}")

        return scenarios[scenario_id]()

    def _detect_failure(self, scenario_id: str, trace: Any, tools: list):
        """Detect if expected failure occurred."""
        if scenario_id == "tool_fabrication":
            tool_names = [t.name for t in tools]
            if detect_tool_fabrication(trace, tool_names):
                return "tool_fabrication"

        elif scenario_id == "tool_hallucination":
            if detect_tool_hallucination(trace, trace.task):
                return "tool_hallucination"

        return None


def main():
    parser = argparse.ArgumentParser(
        description="Run agent failure reproduction experiments"
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="Path to experiment spec YAML file"
    )
    parser.add_argument(
        "--mode",
        choices=["canary", "full"],
        default="canary",
        help="Run mode: canary (small test) or full (complete experiment)"
    )

    args = parser.parse_args()

    runner = ExperimentRunner(args.spec, args.mode)
    runner.run()


if __name__ == "__main__":
    main()
