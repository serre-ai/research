#!/usr/bin/env bash
# Backlog manager — used by all OpenClaw agents
# Usage: backlog.sh list [--status X] [--priority X] [--category X]
#        backlog.sh create <title> <priority> <category> <filed_by> [description]
#        backlog.sh update <id> <field> <value>
#        backlog.sh get <id>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

COMMAND="${1:?Usage: backlog.sh {list|create|update|get} ...}"
shift

case "$COMMAND" in
  list)
    QUERY=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --status) QUERY="${QUERY:+$QUERY&}status=$2"; shift 2 ;;
        --priority) QUERY="${QUERY:+$QUERY&}priority=$2"; shift 2 ;;
        --category) QUERY="${QUERY:+$QUERY&}category=$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$QUERY" ]; then
      "$API_CLIENT" GET "/api/backlog?$QUERY"
    else
      "$API_CLIENT" GET /api/backlog
    fi
    ;;
  create)
    TITLE="${1:?Usage: backlog.sh create <title> <priority> <category> <filed_by> [description]}"
    PRIORITY="${2:?}"
    CATEGORY="${3:?}"
    FILED_BY="${4:?}"
    DESCRIPTION="${5:-}"
    DATA=$(cat <<EOF
{
  "title": "$TITLE",
  "priority": "$PRIORITY",
  "category": "$CATEGORY",
  "filed_by": "$FILED_BY",
  "description": "$DESCRIPTION"
}
EOF
)
    "$API_CLIENT" POST /api/backlog "$DATA"
    ;;
  update)
    ID="${1:?Usage: backlog.sh update <id> <field> <value>}"
    FIELD="${2:?}"
    VALUE="${3:?}"
    DATA="{\"$FIELD\": \"$VALUE\"}"
    "$API_CLIENT" PATCH "/api/backlog/$ID" "$DATA"
    ;;
  get)
    ID="${1:?Usage: backlog.sh get <id>}"
    "$API_CLIENT" GET "/api/backlog/$ID"
    ;;
  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: backlog.sh {list|create|update|get} ..." >&2
    exit 1
    ;;
esac
