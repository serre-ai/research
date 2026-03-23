#!/usr/bin/env bash
# Deploy site-next to VPS
# Usage: ./deploy.sh (from site-next/ directory)
set -euo pipefail

VPS_USER="deepwork-vps"
VPS_ROOT="deepwork-vps-root"
REMOTE_DIR="~/deepwork"

echo "==> Pushing latest code..."
git push

echo "==> Pulling on VPS..."
ssh "$VPS_USER" "cd $REMOTE_DIR && git pull"

echo "==> Building on VPS..."
ssh "$VPS_USER" "cd $REMOTE_DIR && npm ci && npm run build --workspace=site-next"

echo "==> Preparing standalone output..."
ssh "$VPS_USER" "cd $REMOTE_DIR && \
  STANDALONE_DIR=site-next/.next/standalone/site-next && \
  cp -r site-next/public \$STANDALONE_DIR/public 2>/dev/null || true && \
  cp -r site-next/.next/static \$STANDALONE_DIR/.next/static && \
  ln -sf /opt/deepwork/site-next/.env.local \$STANDALONE_DIR/.env.local"

echo "==> Restarting deepwork-site service..."
ssh "$VPS_ROOT" "systemctl restart deepwork-site"

echo "==> Verifying..."
sleep 3
STATUS=$(ssh "$VPS_USER" "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000")
if [ "$STATUS" = "200" ]; then
  echo "==> Deploy successful! (HTTP $STATUS)"
else
  echo "==> WARNING: Got HTTP $STATUS — check logs with: ssh $VPS_ROOT journalctl -u deepwork-site -n 50"
fi
