#!/usr/bin/env bash
# Predict skill — prediction tracking and calibration
# Usage: predict.sh {make|list|resolve|calibration|leaderboard} ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

COMMAND="${1:?Usage: predict.sh COMMAND ...}"
shift

case "$COMMAND" in
  make)
    CLAIM="${1:?Usage: predict.sh make <claim> <probability> [--category X] [--project X]}"
    PROBABILITY="${2:?Usage: predict.sh make <claim> <probability> [--category X] [--project X]}"
    shift 2
    CATEGORY=""
    PROJECT=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --category) CATEGORY="$2"; shift 2 ;;
        --project) PROJECT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
d = {
    'author': sys.argv[1],
    'claim': sys.argv[2],
    'probability': float(sys.argv[3]),
}
if sys.argv[4]:
    d['category'] = sys.argv[4]
if sys.argv[5]:
    d['project'] = sys.argv[5]
print(json.dumps(d))
" "$AGENT" "$CLAIM" "$PROBABILITY" "$CATEGORY" "$PROJECT")
    "$API_CLIENT" POST /api/predictions "$DATA"
    ;;

  list)
    QUERY=""
    # First positional arg is optional agent name
    if [ $# -gt 0 ] && [[ ! "$1" =~ ^-- ]]; then
      QUERY="author=$1"
      shift
    fi
    while [ $# -gt 0 ]; do
      case "$1" in
        --unresolved) QUERY="${QUERY:+$QUERY&}resolved=false"; shift ;;
        --resolved) QUERY="${QUERY:+$QUERY&}resolved=true"; shift ;;
        --category) QUERY="${QUERY:+$QUERY&}category=$2"; shift 2 ;;
        --project) QUERY="${QUERY:+$QUERY&}project=$2"; shift 2 ;;
        --limit) QUERY="${QUERY:+$QUERY&}limit=$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$QUERY" ]; then
      "$API_CLIENT" GET "/api/predictions?$QUERY"
    else
      "$API_CLIENT" GET /api/predictions
    fi
    ;;

  resolve)
    ID="${1:?Usage: predict.sh resolve <id> <true|false> <note>}"
    OUTCOME="${2:?Usage: predict.sh resolve <id> <true|false> <note>}"
    NOTE="${3:?Usage: predict.sh resolve <id> <true|false> <note>}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    # Convert true/false string to JSON boolean
    OUTCOME_BOOL="true"
    if [ "$OUTCOME" = "false" ]; then
      OUTCOME_BOOL="false"
    fi
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'outcome': sys.argv[1] == 'true',
    'resolved_by': sys.argv[2],
    'resolution_note': sys.argv[3]
}))
" "$OUTCOME" "$AGENT" "$NOTE")
    "$API_CLIENT" PATCH "/api/predictions/$ID/resolve" "$DATA"
    ;;

  calibration)
    AGENT="${1:?Usage: predict.sh calibration <agent>}"
    "$API_CLIENT" GET "/api/predictions/calibration/$AGENT"
    ;;

  leaderboard)
    "$API_CLIENT" GET /api/predictions/leaderboard
    ;;

  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: predict.sh {make|list|resolve|calibration|leaderboard} ..." >&2
    exit 1
    ;;
esac
