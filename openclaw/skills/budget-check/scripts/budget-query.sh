#!/usr/bin/env bash
# Budget query helper — used by Sol and Kit via OpenClaw
# Usage: budget-query.sh {status|daily|projection}

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

COMMAND="${1:?Usage: budget-query.sh {status|daily|projection}}"

MONTHLY_LIMIT=1000
DAILY_LIMIT=40

case "$COMMAND" in
  status)
    "$API_CLIENT" GET /api/budget
    ;;
  daily)
    "$API_CLIENT" GET /api/budget/history
    ;;
  projection)
    # Fetch budget and calculate projection
    BUDGET=$("$API_CLIENT" GET /api/budget)
    echo "$BUDGET"
    echo ""
    echo "--- Limits ---"
    echo "Monthly: \$$MONTHLY_LIMIT"
    echo "Daily:   \$$DAILY_LIMIT"
    ;;
  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: budget-query.sh {status|daily|projection}" >&2
    exit 1
    ;;
esac
