#!/usr/bin/env bash
# Knowledge graph operations — used by all OpenClaw agents
# Usage: knowledge.sh <command> [args...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

CMD="${1:?Usage: knowledge.sh <add|query|list|relate|contradictions|unsupported|evidence|stats> [args...]}"
shift

case "$CMD" in
  add)
    PROJECT="${1:?Usage: knowledge.sh add <project> <claim_type> <statement> [confidence] [source]}"
    CLAIM_TYPE="${2:?Usage: knowledge.sh add <project> <claim_type> <statement> [confidence] [source]}"
    STATEMENT="${3:?Usage: knowledge.sh add <project> <claim_type> <statement> [confidence] [source]}"
    CONFIDENCE="${4:-0.5}"
    SOURCE="${5:-}"

    DATA=$(jq -n \
      --arg project "$PROJECT" \
      --arg claim_type "$CLAIM_TYPE" \
      --arg statement "$STATEMENT" \
      --argjson confidence "$CONFIDENCE" \
      --arg source "$SOURCE" \
      '{project: $project, claim_type: $claim_type, statement: $statement, confidence: $confidence} + (if $source != "" then {source: $source, source_type: "agent_session"} else {} end)')

    "$API_CLIENT" POST /api/knowledge/claims "$DATA"
    ;;

  query)
    PROJECT="${1:?Usage: knowledge.sh query <project> <question> [limit]}"
    QUESTION="${2:?Usage: knowledge.sh query <project> <question> [limit]}"
    LIMIT="${3:-10}"

    DATA=$(jq -n \
      --arg query "$QUESTION" \
      --arg project "$PROJECT" \
      --argjson limit "$LIMIT" \
      '{query: $query, project: $project, limit: $limit}')

    "$API_CLIENT" POST /api/knowledge/query "$DATA"
    ;;

  list)
    PROJECT="${1:?Usage: knowledge.sh list <project> [claim_type]}"
    TYPE="${2:-}"

    ENDPOINT="/api/knowledge/claims?project=$PROJECT"
    if [ -n "$TYPE" ]; then
      ENDPOINT="${ENDPOINT}&type=$TYPE"
    fi

    "$API_CLIENT" GET "$ENDPOINT"
    ;;

  relate)
    SOURCE_ID="${1:?Usage: knowledge.sh relate <source_id> <target_id> <relation> [evidence]}"
    TARGET_ID="${2:?Usage: knowledge.sh relate <source_id> <target_id> <relation> [evidence]}"
    RELATION="${3:?Usage: knowledge.sh relate <source_id> <target_id> <relation> [evidence]}"
    EVIDENCE="${4:-}"

    DATA=$(jq -n \
      --arg source_id "$SOURCE_ID" \
      --arg target_id "$TARGET_ID" \
      --arg relation "$RELATION" \
      --arg evidence "$EVIDENCE" \
      '{source_id: $source_id, target_id: $target_id, relation: $relation} + (if $evidence != "" then {evidence: $evidence} else {} end)')

    "$API_CLIENT" POST /api/knowledge/relations "$DATA"
    ;;

  contradictions)
    PROJECT="${1:?Usage: knowledge.sh contradictions <project>}"
    "$API_CLIENT" GET "/api/knowledge/contradictions/$PROJECT"
    ;;

  unsupported)
    PROJECT="${1:?Usage: knowledge.sh unsupported <project>}"
    "$API_CLIENT" GET "/api/knowledge/unsupported/$PROJECT"
    ;;

  evidence)
    CLAIM_ID="${1:?Usage: knowledge.sh evidence <claim_id>}"
    "$API_CLIENT" GET "/api/knowledge/evidence/$CLAIM_ID"
    ;;

  stats)
    "$API_CLIENT" GET /api/knowledge/stats
    ;;

  *)
    echo "Unknown command: $CMD"
    echo "Commands: add, query, list, relate, contradictions, unsupported, evidence, stats"
    exit 1
    ;;
esac
