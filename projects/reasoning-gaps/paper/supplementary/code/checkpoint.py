"""Checkpoint/resume system for long-running evaluation runs.

Persists individual EvalResult records to JSONL files keyed by
(model, task, condition). This allows 48-72 hour evaluation runs
to survive crashes and resume from the last completed instance.
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _sanitize_key(s: str) -> str:
    """Replace characters unsafe for filenames."""
    return s.replace("/", "_").replace(":", "_").replace(" ", "_")


class CheckpointManager:
    """Manages checkpoint files for evaluation runs.

    Each (model, task, condition) combination gets its own JSONL file.
    Results are appended one-at-a-time with fsync for crash safety.

    Args:
        output_dir: Directory to store checkpoint JSONL files.
    """

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # In-memory cache of completed IDs per checkpoint file
        self._completed_cache: dict[str, set[str]] = {}

    def _checkpoint_path(self, model: str, task: str, condition: str) -> Path:
        """Return the JSONL file path for a given (model, task, condition)."""
        key = f"{_sanitize_key(model)}_{_sanitize_key(task)}_{_sanitize_key(condition)}"
        return self.output_dir / f"{key}.jsonl"

    def _cache_key(self, model: str, task: str, condition: str) -> str:
        return f"{model}|{task}|{condition}"

    def save(self, result: Any) -> None:
        """Append a single EvalResult to the appropriate checkpoint file.

        Uses file locking and fsync for crash safety. Updates the in-memory
        cache before writing to prevent duplicate writes from concurrent
        coroutines. Rolls back the cache entry if the write fails.

        Args:
            result: An EvalResult dataclass instance (or any object with
                    model, task, condition, instance_id attributes).
        """
        data = asdict(result) if hasattr(result, '__dataclass_fields__') else result
        instance_id = result.instance_id if hasattr(result, 'instance_id') else data["instance_id"]
        cache_key = self._cache_key(result.model, result.task, result.condition)

        # Check if already saved (prevents duplicate writes)
        if cache_key in self._completed_cache and instance_id in self._completed_cache[cache_key]:
            return

        # Update cache FIRST to prevent concurrent duplicate writes
        if cache_key not in self._completed_cache:
            self._completed_cache[cache_key] = set()
        self._completed_cache[cache_key].add(instance_id)

        # Write to file
        path = self._checkpoint_path(result.model, result.task, result.condition)
        line = json.dumps(data, default=str) + "\n"

        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            os.write(fd, line.encode("utf-8"))
            os.fsync(fd)
            fcntl.flock(fd, fcntl.LOCK_UN)
        except Exception:
            # Roll back cache on write failure
            self._completed_cache[cache_key].discard(instance_id)
            raise
        finally:
            os.close(fd)

    def load(self, model: str, task: str, condition: str) -> list[dict]:
        """Load all results from a checkpoint file.

        Args:
            model: Model identifier.
            task: Task name.
            condition: Evaluation condition.

        Returns:
            List of result dicts parsed from the JSONL file.
        """
        path = self._checkpoint_path(model, task, condition)
        if not path.exists():
            return []

        results = []
        with open(path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning(
                        "Corrupt line %d in checkpoint %s, skipping", line_num, path
                    )
        return results

    def get_completed_ids(self, model: str, task: str, condition: str) -> set[str]:
        """Return set of instance IDs already evaluated.

        Uses an in-memory cache that is populated on first call and
        updated as new results are saved.

        Args:
            model: Model identifier.
            task: Task name.
            condition: Evaluation condition.

        Returns:
            Set of completed instance ID strings.
        """
        cache_key = self._cache_key(model, task, condition)

        if cache_key not in self._completed_cache:
            results = self.load(model, task, condition)
            self._completed_cache[cache_key] = {r["instance_id"] for r in results}

        return self._completed_cache[cache_key]

    def is_complete(
        self, model: str, task: str, condition: str, total_expected: int
    ) -> bool:
        """Check if all instances for a (model, task, condition) are done.

        Args:
            model: Model identifier.
            task: Task name.
            condition: Evaluation condition.
            total_expected: Total number of instances expected.

        Returns:
            True if the number of completed instances >= total_expected.
        """
        completed = self.get_completed_ids(model, task, condition)
        return len(completed) >= total_expected

    def summary(self, model: str, task: str, condition: str) -> dict[str, int]:
        """Return a brief summary of checkpoint state.

        Returns:
            Dict with 'completed' count and 'correct' count.
        """
        results = self.load(model, task, condition)
        correct = sum(1 for r in results if r.get("correct", False))
        return {"completed": len(results), "correct": correct}
