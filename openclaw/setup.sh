#!/usr/bin/env bash
# OpenClaw setup script for Deepwork Research
# Run on VPS after initial deployment

set -euo pipefail

echo "=== OpenClaw Setup for Deepwork Research ==="

# Check Node.js version
NODE_VERSION=$(node -v 2>/dev/null | sed 's/v//' | cut -d. -f1)
if [ "${NODE_VERSION:-0}" -lt 22 ]; then
  echo "Error: Node.js 22+ required (found: $(node -v 2>/dev/null || echo 'none'))" >&2
  exit 1
fi
echo "Node.js: $(node -v)"

# Install OpenClaw if not present
if ! command -v openclaw &>/dev/null; then
  echo "Installing OpenClaw..."
  curl -fsSL https://openclaw.ai/install.sh | bash
  echo "OpenClaw installed: $(openclaw --version)"
else
  echo "OpenClaw already installed: $(openclaw --version)"
fi

# Check required environment variables
REQUIRED_VARS=(DEEPWORK_API_KEY SLACK_BOT_TOKEN SLACK_APP_TOKEN SLACK_SIGNING_SECRET ANTHROPIC_API_KEY)
MISSING=()
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    MISSING+=("$var")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo ""
  echo "Warning: Missing environment variables:"
  for var in "${MISSING[@]}"; do
    echo "  - $var"
  done
  echo ""
  echo "Add these to /home/deepwork/deepwork/.env before starting the gateway."
  echo "Slack variables are required for Slack integration."
  echo "Continuing setup without them..."
fi

# Make scripts executable
echo "Setting script permissions..."
find "$(dirname "$0")/skills" -name "*.sh" -exec chmod +x {} \;
echo "Done."

# Validate gateway config
echo "Validating gateway.json..."
if node -e "JSON.parse(require('fs').readFileSync('$(dirname "$0")/gateway.json', 'utf-8')); console.log('Valid JSON')"; then
  echo "Gateway config OK"
else
  echo "Error: Invalid gateway.json" >&2
  exit 1
fi

# Check Deepwork API connectivity
echo "Checking Deepwork API..."
if curl -sf -o /dev/null http://localhost:3001/api/health; then
  echo "Deepwork API: reachable"
else
  echo "Warning: Deepwork API not reachable at localhost:3001"
  echo "Make sure deepwork-daemon.service is running."
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Add Slack tokens to .env (if not already done)"
echo "  2. Install systemd service:"
echo "     sudo cp deploy/openclaw-gateway.service /etc/systemd/system/"
echo "     sudo systemctl daemon-reload"
echo "     sudo systemctl enable --now openclaw-gateway"
echo "  3. Check status:"
echo "     sudo systemctl status openclaw-gateway"
echo "     journalctl -u openclaw-gateway -f"
