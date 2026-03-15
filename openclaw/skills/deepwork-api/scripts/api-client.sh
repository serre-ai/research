#!/usr/bin/env bash
# Deepwork API client — used by OpenClaw agents
# Usage: api-client.sh METHOD ENDPOINT [DATA]
# Example: api-client.sh GET /api/projects
#          api-client.sh POST /api/sessions '{"project":"reasoning-gaps"}'

set -euo pipefail

METHOD="${1:?Usage: api-client.sh METHOD ENDPOINT [DATA]}"
ENDPOINT="${2:?Usage: api-client.sh METHOD ENDPOINT [DATA]}"
DATA="${3:-}"

API_BASE="http://localhost:3001"
API_KEY="${DEEPWORK_API_KEY:?DEEPWORK_API_KEY not set}"

CURL_ARGS=(
  -s
  -X "$METHOD"
  -H "Content-Type: application/json"
  -H "X-Api-Key: $API_KEY"
)

if [ -n "$DATA" ]; then
  CURL_ARGS+=(-d "$DATA")
fi

curl "${CURL_ARGS[@]}" "${API_BASE}${ENDPOINT}"
