#!/usr/bin/env bash
# Ritual manager skill — schedule and run collective rituals
# Usage: ritual-manager.sh {schedule|start|complete|upcoming|list|history|get} ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

ALL_AGENTS="sol,noor,vera,kit,maren,eli,lev,rho,sage"

COMMAND="${1:?Usage: ritual-manager.sh COMMAND ...}"
shift

case "$COMMAND" in
  schedule)
    TYPE="${1:?Usage: ritual-manager.sh schedule <type> <datetime> [--facilitator X] [--participants X]}"
    DATETIME="${2:?Usage: ritual-manager.sh schedule <type> <datetime> [--facilitator X] [--participants X]}"
    shift 2
    FACILITATOR="sage"
    PARTICIPANTS="$ALL_AGENTS"
    while [ $# -gt 0 ]; do
      case "$1" in
        --facilitator) FACILITATOR="$2"; shift 2 ;;
        --participants)
          if [ "$2" = "all" ]; then
            PARTICIPANTS="$ALL_AGENTS"
          else
            PARTICIPANTS="$2"
          fi
          shift 2
          ;;
        *) shift ;;
      esac
    done
    # Convert comma-separated to JSON array
    DATA=$(python3 -c "
import json, sys
participants = sys.argv[4].split(',')
print(json.dumps({
    'ritual_type': sys.argv[1],
    'scheduled_for': sys.argv[2],
    'facilitator': sys.argv[3],
    'participants': participants
}))
" "$TYPE" "$DATETIME" "$FACILITATOR" "$PARTICIPANTS")
    "$API_CLIENT" POST /api/rituals "$DATA"
    ;;

  start)
    ID="${1:?Usage: ritual-manager.sh start <ritual_id> [--thread_id X]}"
    shift
    THREAD_ID=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --thread_id) THREAD_ID="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$THREAD_ID" ]; then
      DATA="{\"thread_id\": \"$THREAD_ID\"}"
    else
      DATA="{}"
    fi
    "$API_CLIENT" PATCH "/api/rituals/$ID/start" "$DATA"
    ;;

  complete)
    ID="${1:?Usage: ritual-manager.sh complete <ritual_id> <outcome>}"
    OUTCOME="${2:?Usage: ritual-manager.sh complete <ritual_id> <outcome>}"
    DATA=$(python3 -c "
import json, sys
print(json.dumps({'outcome': sys.argv[1]}))
" "$OUTCOME")
    "$API_CLIENT" PATCH "/api/rituals/$ID/complete" "$DATA"
    ;;

  upcoming)
    "$API_CLIENT" GET /api/rituals/upcoming
    ;;

  list)
    QUERY=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --type) QUERY="${QUERY:+$QUERY&}type=$2"; shift 2 ;;
        --status) QUERY="${QUERY:+$QUERY&}status=$2"; shift 2 ;;
        --limit) QUERY="${QUERY:+$QUERY&}limit=$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$QUERY" ]; then
      "$API_CLIENT" GET "/api/rituals?$QUERY"
    else
      "$API_CLIENT" GET /api/rituals
    fi
    ;;

  history)
    QUERY=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --type) QUERY="${QUERY:+$QUERY&}type=$2"; shift 2 ;;
        --limit) QUERY="${QUERY:+$QUERY&}limit=$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$QUERY" ]; then
      "$API_CLIENT" GET "/api/rituals/history?$QUERY"
    else
      "$API_CLIENT" GET /api/rituals/history
    fi
    ;;

  get)
    ID="${1:?Usage: ritual-manager.sh get <ritual_id>}"
    "$API_CLIENT" GET "/api/rituals/$ID"
    ;;

  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: ritual-manager.sh {schedule|start|complete|upcoming|list|history|get} ..." >&2
    exit 1
    ;;
esac
