#!/usr/bin/env bash
#
# Deepwork VPS Bootstrap Script
#
# Provisions an Ubuntu 24.04 server with all dependencies for the
# deepwork research platform: Node.js, Python, PostgreSQL, nginx.
#
# Usage:
#   ssh root@<vps-ip> 'bash -s' < setup.sh
#
# Prerequisites:
#   - Fresh Ubuntu 24.04 LTS
#   - Root or sudo access
#   - .env file ready to copy afterward
#
set -euo pipefail

REPO_URL="https://github.com/serre-ai/research.git"
INSTALL_DIR="/opt/deepwork"
DB_NAME="deepwork"
DB_USER="deepwork"
DB_PASS="$(openssl rand -base64 24)"
SERVICE_USER="deepwork"

echo "=========================================="
echo "  Deepwork VPS Setup"
echo "=========================================="
echo ""

# -----------------------------------------------
# 1. System updates and base packages
# -----------------------------------------------
echo "[1/8] Installing system packages..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    build-essential \
    curl \
    git \
    tmux \
    htop \
    jq \
    unzip \
    fail2ban \
    ufw \
    certbot \
    python3-certbot-nginx \
    nginx

# -----------------------------------------------
# 2. Firewall
# -----------------------------------------------
echo "[2/8] Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP (certbot + redirect)
ufw allow 443/tcp    # HTTPS
ufw --force enable

# -----------------------------------------------
# 3. Node.js 22 LTS
# -----------------------------------------------
echo "[3/8] Installing Node.js 22..."
if ! command -v node &>/dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y -qq nodejs
fi
echo "  Node.js $(node --version)"
echo "  npm $(npm --version)"

# -----------------------------------------------
# 4. Python 3.12+
# -----------------------------------------------
echo "[4/8] Installing Python 3.12..."
apt-get install -y -qq python3 python3-pip python3-venv
echo "  Python $(python3 --version)"

# -----------------------------------------------
# 5. PostgreSQL 16
# -----------------------------------------------
echo "[5/8] Installing PostgreSQL 16..."
if ! command -v psql &>/dev/null; then
    apt-get install -y -qq postgresql postgresql-contrib
fi
systemctl enable postgresql
systemctl start postgresql

# Create database and user
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"

echo "  PostgreSQL $(psql --version | head -1)"
echo "  Database: ${DB_NAME}"
echo "  User: ${DB_USER}"
echo "  Password: ${DB_PASS}  (save this!)"

# -----------------------------------------------
# 6. Create service user and clone repo
# -----------------------------------------------
echo "[6/8] Setting up application..."
id -u ${SERVICE_USER} &>/dev/null || useradd -r -m -d /opt/deepwork -s /bin/bash ${SERVICE_USER}

if [ ! -d "${INSTALL_DIR}/.git" ]; then
    git clone "${REPO_URL}" "${INSTALL_DIR}"
else
    cd "${INSTALL_DIR}" && git pull
fi

chown -R ${SERVICE_USER}:${SERVICE_USER} "${INSTALL_DIR}"

# Install Node.js dependencies (workspace-aware)
cd "${INSTALL_DIR}"
sudo -u ${SERVICE_USER} npm ci

# Build orchestrator
sudo -u ${SERVICE_USER} npm run build --workspace=orchestrator

# Build site-next and prepare standalone output
sudo -u ${SERVICE_USER} npm run build --workspace=site-next
STANDALONE_DIR="${INSTALL_DIR}/site-next/.next/standalone/site-next"
sudo -u ${SERVICE_USER} cp -r "${INSTALL_DIR}/site-next/public" "${STANDALONE_DIR}/public" 2>/dev/null || true
sudo -u ${SERVICE_USER} cp -r "${INSTALL_DIR}/site-next/.next/static" "${STANDALONE_DIR}/.next/static"

# Install Python dependencies for eval + backfill
cd "${INSTALL_DIR}"
sudo -u ${SERVICE_USER} python3 -m venv .venv
sudo -u ${SERVICE_USER} .venv/bin/pip install -q psycopg2-binary

# Install eval dependencies if requirements exist
if [ -f "projects/reasoning-gaps/benchmarks/requirements.txt" ]; then
    sudo -u ${SERVICE_USER} .venv/bin/pip install -q -r projects/reasoning-gaps/benchmarks/requirements.txt
fi

# -----------------------------------------------
# 7. Apply database schema
# -----------------------------------------------
echo "[7/8] Running database migrations..."
cd "${INSTALL_DIR}"
DATABASE_URL="postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}" \
    sudo -u ${SERVICE_USER} node orchestrator/dist/migrate.js

# -----------------------------------------------
# 8. Install systemd services and nginx
# -----------------------------------------------
echo "[8/8] Installing services..."

# Copy systemd units
cp "${INSTALL_DIR}/orchestrator/deploy/forge-daemon.service" /etc/systemd/system/
cp "${INSTALL_DIR}/orchestrator/deploy/deepwork-eval@.service" /etc/systemd/system/
cp "${INSTALL_DIR}/site-next/deploy/deepwork-site.service" /etc/systemd/system/

# Create .env template if it doesn't exist
if [ ! -f "${INSTALL_DIR}/.env" ]; then
    cat > "${INSTALL_DIR}/.env" << ENVEOF
# Deepwork Environment Variables
# Copy your actual keys here

# Database
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}

# API
DEEPWORK_API_KEY=$(openssl rand -hex 32)
API_PORT=3001
CORS_ORIGIN=https://deepwork.site

# Budget
DAILY_BUDGET_USD=40
MONTHLY_BUDGET_USD=1000

# Anthropic
ANTHROPIC_API_KEY=

# OpenAI
OPENAI_API_KEY=

# Modal
MODAL_TOKEN_ID=
MODAL_TOKEN_SECRET=

# Slack (optional)
SLACK_WEBHOOK_URL=

# Poll interval
POLL_INTERVAL_MINUTES=30
MAX_CONCURRENT_SESSIONS=2
ENVEOF
    chown ${SERVICE_USER}:${SERVICE_USER} "${INSTALL_DIR}/.env"
    chmod 600 "${INSTALL_DIR}/.env"
    echo "  Created .env template — fill in API keys!"
fi

# Create site-next .env.local template if it doesn't exist
if [ ! -f "${INSTALL_DIR}/site-next/.env.local" ]; then
    SITE_API_KEY=$(grep DEEPWORK_API_KEY "${INSTALL_DIR}/.env" | cut -d= -f2)
    cat > "${INSTALL_DIR}/site-next/.env.local" << ENVEOF
AUTH_SECRET=$(openssl rand -base64 32)
AUTH_GITHUB_ID=
AUTH_GITHUB_SECRET=
AUTH_ALLOWED_USERS=oddurs
AUTH_TRUST_HOST=true
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}
VPS_API_URL=http://localhost:3001
VPS_API_KEY=${SITE_API_KEY}
ENVEOF
    chown ${SERVICE_USER}:${SERVICE_USER} "${INSTALL_DIR}/site-next/.env.local"
    chmod 600 "${INSTALL_DIR}/site-next/.env.local"
    # Symlink into standalone
    ln -sf "${INSTALL_DIR}/site-next/.env.local" "${STANDALONE_DIR}/.env.local"
    echo "  Created site-next .env.local — fill in GitHub OAuth credentials!"
fi

# nginx config
cp "${INSTALL_DIR}/orchestrator/deploy/nginx.conf" /etc/nginx/sites-available/deepwork-api
ln -sf /etc/nginx/sites-available/deepwork-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

# Reload services
systemctl daemon-reload
systemctl enable forge-daemon
systemctl enable deepwork-site
systemctl restart nginx

echo ""
echo "=========================================="
echo "  Setup Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit /opt/deepwork/.env with your API keys"
echo "  2. Create GitHub OAuth App at https://github.com/settings/developers"
echo "     Homepage URL: https://forge.serre.ai"
echo "     Callback URL: https://forge.serre.ai/api/auth/callback/github"
echo "  3. Edit /opt/deepwork/site-next/.env.local with OAuth credentials"
echo "  4. Set up SSL:  certbot --nginx -d forge.serre.ai"
echo "  5. Start services: systemctl start forge-daemon deepwork-site"
echo "  6. Check status:   systemctl status forge-daemon deepwork-site"
echo "  7. View logs:      journalctl -u forge-daemon -f"
echo "                     journalctl -u deepwork-site -f"
echo "  6. Backfill eval data:"
echo "     cd /opt/deepwork && .venv/bin/python orchestrator/sql/backfill_checkpoints.py"
echo ""
echo "Database credentials (save these!):"
echo "  DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}"
echo ""
echo "API key (save this!):"
grep DEEPWORK_API_KEY "${INSTALL_DIR}/.env" || true
echo ""
