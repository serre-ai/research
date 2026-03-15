#!/usr/bin/env bash
# Session dispatch — used by Sol and Vera via OpenClaw
# Usage: dispatch.sh <project> <agent_type> <priority> <reason> <triggered_by>
#        dispatch.sh --queue

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

if [ "${1:-}" = "--queue" ]; then
  "$API_CLIENT" GET /api/sessions/dispatch/queue
  exit 0
fi

PROJECT="${1:?Usage: dispatch.sh <project> <agent_type> <priority> <reason> <triggered_by>}"
AGENT_TYPE="${2:?Usage: dispatch.sh <project> <agent_type> <priority> <reason> <triggered_by>}"
PRIORITY="${3:-normal}"
REASON="${4:?Usage: dispatch.sh <project> <agent_type> <priority> <reason> <triggered_by>}"
TRIGGERED_BY="${5:?Usage: dispatch.sh <project> <agent_type> <priority> <reason> <triggered_by>}"

DATA=$(cat <<EOF
{
  "project": "$PROJECT",
  "agent_type": "$AGENT_TYPE",
  "priority": "$PRIORITY",
  "reason": "$REASON",
  "triggered_by": "$TRIGGERED_BY"
}
EOF
)

"$API_CLIENT" POST /api/sessions/dispatch "$DATA"
