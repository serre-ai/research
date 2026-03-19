#!/usr/bin/env bash
# Deploy site-next to VPS
# Usage: ./deploy.sh
set -euo pipefail

VPS_USER="deepwork-vps"
VPS_ROOT="deepwork-vps-root"
REMOTE_DIR="~/deepwork/site-next"
STANDALONE_DIR="${REMOTE_DIR}/.next/standalone/site-next"

echo "==> Building locally..."
npm run build

echo "==> Pushing latest code..."
git push

echo "==> Pulling on VPS..."
ssh "$VPS_USER" "cd $REMOTE_DIR && git pull"

echo "==> Building on VPS..."
ssh "$VPS_USER" "cd $REMOTE_DIR && npm run build"

echo "==> Copying static assets into standalone..."
ssh "$VPS_USER" "cp -r ${REMOTE_DIR}/public ${STANDALONE_DIR}/public 2>/dev/null || true"
ssh "$VPS_USER" "cp -r ${REMOTE_DIR}/.next/static ${STANDALONE_DIR}/.next/static 2>/dev/null || true"

echo "==> Symlinking .env.local..."
ssh "$VPS_USER" "ln -sf ${REMOTE_DIR}/.env.local ${STANDALONE_DIR}/.env.local"

echo "==> Restarting Next.js service..."
ssh "$VPS_ROOT" "systemctl restart deepwork-next"

echo "==> Verifying..."
sleep 2
STATUS=$(ssh "$VPS_USER" "curl -s -o /dev/null -w '%{http_code}' https://research.oddurs.com/sign-in")
if [ "$STATUS" = "200" ]; then
  echo "==> Deploy successful! (HTTP $STATUS)"
else
  echo "==> WARNING: Got HTTP $STATUS — check logs with: ssh $VPS_ROOT journalctl -u deepwork-next -n 50"
fi
