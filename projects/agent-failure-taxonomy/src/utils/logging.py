"""Structured logging for agent experiments."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class ExperimentLogger:
    """Logs agent execution traces with structured data."""

    def __init__(self, log_dir: Path, instance_id: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.instance_id = instance_id
        self.log_file = self.log_dir / f"{instance_id}.jsonl"
        self.start_time = time.time()

        # Initialize log with metadata
        self._write_log({
            "type": "metadata",
            "instance_id": instance_id,
            "timestamp": datetime.now().isoformat(),
            "start_time": self.start_time
        })

    def log_task_start(self, task_description: str, tools: List[str], ground_truth: Any):
        """Log task initialization."""
        self._write_log({
            "type": "task_start",
            "timestamp": self._get_timestamp(),
            "task": task_description,
            "available_tools": tools,
            "ground_truth": ground_truth
        })

    def log_llm_call(self, prompt: str, response: str, model: str, tokens: Dict[str, int], cost: float):
        """Log LLM API call."""
        self._write_log({
            "type": "llm_call",
            "timestamp": self._get_timestamp(),
            "model": model,
            "prompt": prompt,
            "response": response,
            "tokens": tokens,
            "cost_usd": cost
        })

    def log_tool_call(self, tool_name: str, args: Dict[str, Any], result: Any, is_valid: bool):
        """Log tool execution."""
        self._write_log({
            "type": "tool_call",
            "timestamp": self._get_timestamp(),
            "tool": tool_name,
            "args": args,
            "result": str(result),
            "valid_tool": is_valid  # whether tool exists
        })

    def log_reasoning(self, thought: str, iteration: int):
        """Log agent reasoning step."""
        self._write_log({
            "type": "reasoning",
            "timestamp": self._get_timestamp(),
            "iteration": iteration,
            "thought": thought
        })

    def log_action(self, action: str, iteration: int):
        """Log agent action decision."""
        self._write_log({
            "type": "action",
            "timestamp": self._get_timestamp(),
            "iteration": iteration,
            "action": action
        })

    def log_completion(self, success: bool, reason: str, final_answer: Any, metrics: Dict[str, Any]):
        """Log task completion."""
        self._write_log({
            "type": "completion",
            "timestamp": self._get_timestamp(),
            "elapsed_seconds": time.time() - self.start_time,
            "success": success,
            "reason": reason,
            "answer": final_answer,
            "metrics": metrics
        })

    def _write_log(self, entry: Dict[str, Any]):
        """Write log entry to file."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def _get_timestamp(self) -> float:
        """Get elapsed time since start."""
        return time.time() - self.start_time


def read_log(log_file: Path) -> List[Dict[str, Any]]:
    """Read structured log file."""
    entries = []
    with open(log_file, 'r') as f:
        for line in f:
            entries.append(json.loads(line))
    return entries


def extract_metrics(log_file: Path) -> Dict[str, Any]:
    """Extract key metrics from log."""
    entries = read_log(log_file)

    # Find metadata and completion
    metadata = next((e for e in entries if e["type"] == "metadata"), None)
    completion = next((e for e in entries if e["type"] == "completion"), None)

    # Count tool calls
    tool_calls = [e for e in entries if e["type"] == "tool_call"]
    invalid_tool_calls = [e for e in tool_calls if not e["valid_tool"]]

    # Count LLM calls
    llm_calls = [e for e in entries if e["type"] == "llm_call"]
    total_cost = sum(e["cost_usd"] for e in llm_calls)
    total_tokens = sum(e["tokens"]["total"] for e in llm_calls if "total" in e["tokens"])

    # Count iterations
    reasoning_steps = [e for e in entries if e["type"] == "reasoning"]
    max_iteration = max((e["iteration"] for e in reasoning_steps), default=0)

    return {
        "instance_id": metadata["instance_id"] if metadata else "unknown",
        "success": completion["success"] if completion else False,
        "completion_reason": completion["reason"] if completion else "unknown",
        "total_iterations": max_iteration,
        "total_tool_calls": len(tool_calls),
        "invalid_tool_calls": len(invalid_tool_calls),
        "fabrication_rate": len(invalid_tool_calls) / len(tool_calls) if tool_calls else 0.0,
        "total_llm_calls": len(llm_calls),
        "total_tokens": total_tokens,
        "total_cost_usd": total_cost,
        "elapsed_seconds": completion["elapsed_seconds"] if completion else 0.0
    }
