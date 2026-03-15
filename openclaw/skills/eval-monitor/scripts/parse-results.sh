#!/usr/bin/env bash
# Eval result parser — used by Kit via OpenClaw
# Usage: parse-results.sh {status|results|compare} [project] [task]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

COMMAND="${1:?Usage: parse-results.sh {status|results|compare} [project] [task]}"
PROJECT="${2:-}"
TASK="${3:-}"

case "$COMMAND" in
  status)
    "$API_CLIENT" GET /api/evals
    ;;
  results)
    if [ -z "$PROJECT" ]; then
      echo "Error: project name required for results command" >&2
      exit 1
    fi
    "$API_CLIENT" GET "/api/evals/results?project=$PROJECT"
    ;;
  compare)
    if [ -z "$PROJECT" ] || [ -z "$TASK" ]; then
      echo "Error: project and task required for compare command" >&2
      exit 1
    fi
    "$API_CLIENT" GET "/api/evals/results?project=$PROJECT&task=$TASK"
    ;;
  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: parse-results.sh {status|results|compare} [project] [task]" >&2
    exit 1
    ;;
esac
