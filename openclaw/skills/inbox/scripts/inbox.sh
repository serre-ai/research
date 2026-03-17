#!/usr/bin/env bash
# Inbox skill — direct agent-to-agent communication
# Usage: inbox.sh {check|send|broadcast|read|mentions|stats} ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

COMMAND="${1:?Usage: inbox.sh COMMAND ...}"
shift

case "$COMMAND" in
  check)
    AGENT="${1:?Usage: inbox.sh check <agent_name> [--unread-only] [--priority urgent]}"
    shift
    QUERY=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --unread-only) QUERY="${QUERY:+$QUERY&}unread=true"; shift ;;
        --priority) QUERY="${QUERY:+$QUERY&}priority=$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$QUERY" ]; then
      "$API_CLIENT" GET "/api/messages/inbox/$AGENT?$QUERY"
    else
      "$API_CLIENT" GET "/api/messages/inbox/$AGENT"
    fi
    ;;

  send)
    TO="${1:?Usage: inbox.sh send <to_agent> <subject> <body> [--priority urgent]}"
    SUBJECT="${2:?Usage: inbox.sh send <to_agent> <subject> <body> [--priority urgent]}"
    BODY="${3:?Usage: inbox.sh send <to_agent> <subject> <body> [--priority urgent]}"
    shift 3
    PRIORITY="normal"
    while [ $# -gt 0 ]; do
      case "$1" in
        --priority) PRIORITY="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'from_agent': sys.argv[1],
    'to_agent': sys.argv[2],
    'subject': sys.argv[3],
    'body': sys.argv[4],
    'priority': sys.argv[5]
}))
" "$AGENT" "$TO" "$SUBJECT" "$BODY" "$PRIORITY")
    "$API_CLIENT" POST /api/messages/send "$DATA"
    ;;

  broadcast)
    SUBJECT="${1:?Usage: inbox.sh broadcast <subject> <body>}"
    BODY="${2:?Usage: inbox.sh broadcast <subject> <body>}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'from_agent': sys.argv[1],
    'to_agent': '*',
    'subject': sys.argv[2],
    'body': sys.argv[3],
    'priority': 'urgent'
}))
" "$AGENT" "$SUBJECT" "$BODY")
    "$API_CLIENT" POST /api/messages/send "$DATA"
    ;;

  read)
    MESSAGE_ID="${1:?Usage: inbox.sh read <message_id>}"
    "$API_CLIENT" PATCH "/api/messages/$MESSAGE_ID/read" "{}"
    ;;

  mentions)
    AGENT="${1:?Usage: inbox.sh mentions <agent_name>}"
    "$API_CLIENT" GET "/api/messages/mentions/$AGENT"
    ;;

  stats)
    AGENT="${1:?Usage: inbox.sh stats <agent_name>}"
    "$API_CLIENT" GET "/api/messages/stats/$AGENT"
    ;;

  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: inbox.sh {check|send|broadcast|read|mentions|stats} ..." >&2
    exit 1
    ;;
esac
