#!/bin/bash
# Run evaluation for specified model, then ingest results into PostgreSQL
set -e

cd /opt/deepwork/projects/reasoning-gaps/benchmarks
source /opt/deepwork/.env

echo "[$(date)] Starting eval: $@"
/opt/deepwork/.venv/bin/python3 run_evaluation.py "$@"

echo "[$(date)] Eval complete. Ingesting results..."
/opt/deepwork/.venv/bin/python3 ingest_results.py

echo "[$(date)] Done."
