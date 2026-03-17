#!/usr/bin/env bash
# Governance skill — self-governance proposals and voting
# Usage: governance.sh {propose|list|get|vote|tally|resolve} ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

COMMAND="${1:?Usage: governance.sh COMMAND ...}"
shift

case "$COMMAND" in
  propose)
    TITLE="${1:?Usage: governance.sh propose <title> <proposal> <type>}"
    PROPOSAL="${2:?Usage: governance.sh propose <title> <proposal> <type>}"
    TYPE="${3:?Usage: governance.sh propose <title> <proposal> <type>}"
    AGENT="${OPENCLAW_AGENT:?OPENCLAW_AGENT not set}"
    DATA=$(python3 -c "
import json, sys
print(json.dumps({
    'proposer': sys.argv[1],
    'title': sys.argv[2],
    'proposal': sys.argv[3],
    'proposal_type': sys.argv[4]
}))
" "$AGENT" "$TITLE" "$PROPOSAL" "$TYPE")
    "$API_CLIENT" POST /api/governance "$DATA"
    ;;

  list)
    QUERY=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --status) QUERY="${QUERY:+$QUERY&}status=$2"; shift 2 ;;
        --type) QUERY="${QUERY:+$QUERY&}type=$2"; shift 2 ;;
        --limit) QUERY="${QUERY:+$QUERY&}limit=$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$QUERY" ]; then
      "$API_CLIENT" GET "/api/governance?$QUERY"
    else
      "$API_CLIENT" GET /api/governance
    fi
    ;;

  get)
    ID="${1:?Usage: governance.sh get <id>}"
    "$API_CLIENT" GET "/api/governance/$ID"
    ;;

  vote)
    ID="${1:?Usage: governance.sh vote <id> <position> [rationale] [confidence]}"
    POSITION="${2:?Usage: governance.sh vote <id> <position> [rationale] [confidence]}"
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
    "$API_CLIENT" POST "/api/governance/$ID/vote" "$DATA"
    ;;

  tally)
    ID="${1:?Usage: governance.sh tally <id>}"
    "$API_CLIENT" GET "/api/governance/$ID/tally"
    ;;

  resolve)
    ID="${1:?Usage: governance.sh resolve <id>}"
    "$API_CLIENT" PATCH "/api/governance/$ID/resolve" "{}"
    ;;

  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: governance.sh {propose|list|get|vote|tally|resolve} ..." >&2
    exit 1
    ;;
esac
