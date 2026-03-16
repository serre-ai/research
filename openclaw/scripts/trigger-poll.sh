#!/usr/bin/env bash
# trigger-poll.sh — Poll /api/triggers/pending every 5 min (via cron)
# and invoke triggered agents via the openclaw gateway.
#
# Cron entry: */5 * * * * /opt/deepwork/openclaw/scripts/trigger-poll.sh

set -euo pipefail

API_BASE="${DEEPWORK_API_URL:-http://127.0.0.1:3001}"
API_KEY="${DEEPWORK_API_KEY:?DEEPWORK_API_KEY must be set}"
GATEWAY="${OPENCLAW_GATEWAY:-/opt/deepwork/openclaw}"
LOG_FILE="${OPENCLAW_LOG:-/tmp/trigger-poll.log}"

# Fetch pending triggers
RESPONSE=$(curl -sf -H "X-Api-Key: ${API_KEY}" "${API_BASE}/api/triggers/pending" 2>/dev/null || echo "[]")

# Parse trigger count
COUNT=$(echo "${RESPONSE}" | jq 'length' 2>/dev/null || echo "0")

if [ "${COUNT}" -eq 0 ]; then
  exit 0
fi

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Found ${COUNT} trigger(s)" >> "${LOG_FILE}"

# Process each trigger
echo "${RESPONSE}" | jq -c '.[]' | while read -r trigger; do
  TRIGGER_ID=$(echo "${trigger}" | jq -r '.id')
  AGENT=$(echo "${trigger}" | jq -r '.agent')
  TRIGGER_TYPE=$(echo "${trigger}" | jq -r '.trigger_type')
  CONTEXT=$(echo "${trigger}" | jq -c '.context')

  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Firing trigger #${TRIGGER_ID}: ${TRIGGER_TYPE} → ${AGENT}" >> "${LOG_FILE}"

  # Invoke the agent via gateway
  if [ -x "${GATEWAY}/gateway" ]; then
    "${GATEWAY}/gateway" trigger "${AGENT}" --trigger-type "${TRIGGER_TYPE}" --context "${CONTEXT}" >> "${LOG_FILE}" 2>&1 &
  else
    # Fallback: dispatch via API
    curl -sf -X POST \
      -H "X-Api-Key: ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d "{\"project\":\"openclaw-collective\",\"agent_type\":\"${AGENT}\",\"reason\":\"trigger:${TRIGGER_TYPE}\",\"triggered_by\":\"trigger-poll\"}" \
      "${API_BASE}/api/sessions/dispatch" >> "${LOG_FILE}" 2>&1 || true
  fi

  # Acknowledge the trigger
  curl -sf -X POST \
    -H "X-Api-Key: ${API_KEY}" \
    "${API_BASE}/api/triggers/${TRIGGER_ID}/ack" >> "${LOG_FILE}" 2>&1 || true
done
