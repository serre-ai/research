"""Atomic file write utilities for experiment pipelines.

Provides crash-safe write operations:
- atomic_jsonl_append: append one JSON line with fsync
- atomic_json_write: write JSON via temp-file + fsync + rename
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_jsonl_append(path: Path | str, data: dict) -> None:
    """Append a single JSON line to a JSONL file with fsync.

    Serializes to string first (catches ValueError/TypeError before
    touching the file). Uses O_APPEND for write atomicity.
    """
    line = json.dumps(data, default=str) + "\n"
    encoded = line.encode("utf-8")

    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, encoded)
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json_write(path: Path | str, data: Any, indent: int = 2) -> None:
    """Write JSON to a file atomically using temp-file + fsync + rename.

    Serializes to string first so serialization errors never corrupt
    the target file. Uses the same directory for the temp file to
    ensure rename is atomic (same filesystem).
    """
    path = Path(path)
    # No default=str here — strict serialization catches bad data before writing
    content = json.dumps(data, indent=indent)

    # Write to temp file in same directory (ensures same filesystem for rename)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        os.write(fd, content.encode("utf-8"))
        os.fsync(fd)
        os.close(fd)
        fd = -1  # mark as closed
        os.rename(tmp_path, str(path))
    except BaseException:
        if fd >= 0:
            os.close(fd)
        # Clean up temp file on any failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
