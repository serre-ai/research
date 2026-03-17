#!/usr/bin/env bash
# Forum skill — structured collective communication
# Usage: forum.sh {threads|read|propose|debate|signal|reply|vote|synthesize|feed|stats} ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

COMMAND="${1:?Usage: forum.sh COMMAND ...}"
shift

case "$COMMAND" in
  threads)
    QUERY=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --status) QUERY="${QUERY:+$QUERY&}status=$2"; shift 2 ;;
        --type) QUERY="${QUERY:+$QUERY&}type=$2"; shift 2 ;;
        --author) QUERY="${QUERY:+$QUERY&}author=$2"; shift 2 ;;
        --limit) QUERY="${QUERY:+$QUERY&}limit=$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$QUERY" ]; then
      "$API_CLIENT" GET "/api/forum/threads?$QUERY"
    else
      "$API_CLIENT" GET /api/forum/threads
    fi
    ;;

  read)
    THREAD_ID="${1:?Usage: forum.sh read <thread_id>}"
    "$API_CLIENT" GET "/api/forum/threads/$THREAD_ID"
    ;;

  propose)
    TITLE="${1:?Usage: forum.sh propose <title> <body>}"
    BODY="${2:?Usage: forum.sh propose <title> <body>}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    # Use python for safe JSON encoding
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'author': sys.argv[1],
    'post_type': 'proposal',
    'title': sys.argv[2],
    'body': sys.argv[3]
}))
" "$AGENT" "$TITLE" "$BODY")
    "$API_CLIENT" POST /api/forum/threads "$DATA"
    ;;

  debate)
    TITLE="${1:?Usage: forum.sh debate <title> <body>}"
    BODY="${2:?Usage: forum.sh debate <title> <body>}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'author': sys.argv[1],
    'post_type': 'debate',
    'title': sys.argv[2],
    'body': sys.argv[3]
}))
" "$AGENT" "$TITLE" "$BODY")
    "$API_CLIENT" POST /api/forum/threads "$DATA"
    ;;

  signal)
    TITLE="${1:?Usage: forum.sh signal <title> <body>}"
    BODY="${2:?Usage: forum.sh signal <title> <body>}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'author': sys.argv[1],
    'post_type': 'signal',
    'title': sys.argv[2],
    'body': sys.argv[3]
}))
" "$AGENT" "$TITLE" "$BODY")
    "$API_CLIENT" POST /api/forum/threads "$DATA"
    ;;

  reply)
    THREAD_ID="${1:?Usage: forum.sh reply <thread_id> <body>}"
    BODY="${2:?Usage: forum.sh reply <thread_id> <body>}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'author': sys.argv[1],
    'body': sys.argv[2]
}))
" "$AGENT" "$BODY")
    "$API_CLIENT" POST "/api/forum/threads/$THREAD_ID/reply" "$DATA"
    ;;

  vote)
    THREAD_ID="${1:?Usage: forum.sh vote <thread_id> <position> [rationale] [confidence]}"
    POSITION="${2:?Usage: forum.sh vote <thread_id> <position> [rationale] [confidence]}"
    RATIONALE="${3:-}"
    CONFIDENCE="${4:-}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
d = {
    'voter': sys.argv[1],
    'position': sys.argv[2],
}
if sys.argv[3]:
    d['rationale'] = sys.argv[3]
if sys.argv[4]:
    d['confidence'] = float(sys.argv[4])
print(json.dumps(d))
" "$AGENT" "$POSITION" "$RATIONALE" "$CONFIDENCE")
    "$API_CLIENT" POST "/api/forum/threads/$THREAD_ID/vote" "$DATA"
    ;;

  synthesize)
    THREAD_ID="${1:?Usage: forum.sh synthesize <thread_id> <body>}"
    BODY="${2:?Usage: forum.sh synthesize <thread_id> <body>}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'author': sys.argv[1],
    'body': sys.argv[2]
}))
" "$AGENT" "$BODY")
    "$API_CLIENT" POST "/api/forum/threads/$THREAD_ID/synthesize" "$DATA"
    ;;

  feed)
    AGENT="${1:?Usage: forum.sh feed <agent_name>}"
    "$API_CLIENT" GET "/api/forum/feed/$AGENT"
    ;;

  stats)
    "$API_CLIENT" GET /api/forum/stats
    ;;

  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: forum.sh {threads|read|propose|debate|signal|reply|vote|synthesize|feed|stats} ..." >&2
    exit 1
    ;;
esac
