#!/usr/bin/env bash
# Daily digest read/write — used by Archivist and Sol via OpenClaw
# Usage: digest.sh write <date> <filed_by> <digest_text> [key_events]
#        digest.sh latest
#        digest.sh read <date>
#        digest.sh list

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_CLIENT="$SCRIPT_DIR/../../deepwork-api/scripts/api-client.sh"

COMMAND="${1:?Usage: digest.sh {write|latest|read|list} ...}"
shift

case "$COMMAND" in
  write)
    DATE="${1:?Usage: digest.sh write <date> <filed_by> <digest_text> [key_events]}"
    FILED_BY="${2:?}"
    DIGEST="${3:?}"
    KEY_EVENTS="${4:-}"

    # Convert comma-separated key_events to JSON array
    if [ -n "$KEY_EVENTS" ]; then
      EVENTS_JSON=$(echo "$KEY_EVENTS" | tr ',' '\n' | sed 's/^/"/;s/$/"/' | paste -sd, - | sed 's/^/[/;s/$/]/')
    else
      EVENTS_JSON="[]"
    fi

    DATA=$(cat <<EOF
{
  "date": "$DATE",
  "digest": "$DIGEST",
  "key_events": $EVENTS_JSON,
  "filed_by": "$FILED_BY"
}
EOF
)
    "$API_CLIENT" POST /api/memory/digest "$DATA"
    ;;
  latest)
    "$API_CLIENT" GET /api/memory/digest/latest
    ;;
  read)
    DATE="${1:?Usage: digest.sh read <date>}"
    "$API_CLIENT" GET "/api/memory/digest/$DATE"
    ;;
  list)
    "$API_CLIENT" GET /api/memory/digest
    ;;
  *)
    echo "Unknown command: $COMMAND" >&2
    echo "Usage: digest.sh {write|latest|read|list} ..." >&2
    exit 1
    ;;
esac
