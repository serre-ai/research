"""Pytest configuration for benchmark tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the benchmarks directory is on sys.path so that
# ``import evaluate`` and ``from clients import ...`` resolve correctly.
_benchmarks_dir = str(Path(__file__).resolve().parent.parent)
if _benchmarks_dir not in sys.path:
    sys.path.insert(0, _benchmarks_dir)
