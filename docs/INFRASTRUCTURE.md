# Infrastructure and Deployment Guide

This document covers everything needed to run the Deepwork research platform: server setup, process management, API configuration, disk planning, and security.

Related documents:
- [Research Operations](OPERATIONS.md) -- project lifecycle, sessions, monitoring
- [Scaling Strategy](SCALING.md) -- budget allocation, concurrent capacity, growth plan

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Environment Setup](#environment-setup)
3. [Running the Orchestrator as a Daemon](#running-the-orchestrator-as-a-daemon)
4. [Daemon Mode Architecture](#daemon-mode-architecture)
5. [GPU Compute](#gpu-compute)
6. [API Keys and Rate Limits](#api-keys-and-rate-limits)
7. [Worktree Disk Layout](#worktree-disk-layout)
8. [Monitoring Infrastructure](#monitoring-infrastructure)
9. [Backup Strategy](#backup-strategy)
10. [Multi-Machine Setup](#multi-machine-setup)
11. [Network Requirements](#network-requirements)
12. [Security](#security)

---

## Architecture Overview

```
+-----------------------------+
|    Human (laptop/desktop)   |
|  - Reviews PRs on GitHub    |
|  - Runs CLI dashboard       |
|  - Interactive Claude Code  |
|  - Submits papers           |
+-------------+---------------+
              |
              | git push/pull, gh CLI
              v
+-----------------------------+
|         GitHub              |
|  - Repository hosting       |
|  - PR workflow              |
|  - Branch protection        |
+-------------+---------------+
              |
              | git push/pull, gh CLI
              v
+-----------------------------+
|    Orchestrator Server      |
|  (VPS or local machine)     |
|  - Node.js orchestrator     |
|  - Claude Code sessions     |
|  - Git worktrees            |
|  - API calls                |
+-------------+---------------+
              |
              | SSH (on-demand)
              v
+-----------------------------+
|    GPU Compute (Modal)      |
|  - Scale-to-zero GPUs       |
|  - Experiment execution     |
|  - Model evaluation         |
+-----------------------------+
```

### Components

| Component | Technology | Location |
|-----------|-----------|----------|
| Orchestrator | TypeScript/Node.js | VPS or local machine |
| CLI Dashboard | Ink/React (terminal UI) | Any machine with repo access |
| Session Management | Claude Code CLI + Claude Agent SDK | Orchestrator server |
| Git Engine | Native git + GitHub CLI | Orchestrator server |
| Project Storage | Git repo + YAML status files | GitHub + local worktrees |

---

## Environment Setup

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Linux (Ubuntu 22.04+) or macOS 13+ | Ubuntu 24.04 LTS |
| Node.js | 22.0+ | Latest LTS (22.x) |
| Git | 2.40+ | Latest stable |
| GitHub CLI (`gh`) | 2.40+ | Latest stable |
| RAM | 2 GB | 4 GB |
| Disk | 10 GB free | 50 GB free |
| CPU | 2 cores | 4 cores |

The orchestrator itself is lightweight. The disk and RAM requirements are driven by the number of concurrent git worktrees and the size of project artifacts.

### Install Dependencies

**Ubuntu/Debian:**

```bash
# Node.js 22 via NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Git (usually pre-installed, but ensure it's recent)
sudo apt-get install -y git

# GitHub CLI
(type -p wget >/dev/null || sudo apt install wget -y) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y

# Authenticate GitHub CLI
gh auth login
```

**macOS:**

```bash
# Node.js via Homebrew
brew install node@22

# Git (Xcode command line tools or Homebrew)
brew install git

# GitHub CLI
brew install gh

# Authenticate GitHub CLI
gh auth login
```

### Clone and Build

```bash
# Clone the repository
git clone git@github.com:<org>/deepwork.git
cd deepwork

# Install orchestrator dependencies
cd orchestrator && npm install && npm run build && cd ..

# Install CLI dependencies
cd cli && npm install && npm run build && cd ..
```

### Environment Variables (.env)

Create a `.env` file in the repository root. This file is gitignored and must be managed separately on each machine.

```bash
# .env -- Deepwork platform configuration

# Anthropic API (for Claude Agent SDK sessions)
ANTHROPIC_API_KEY=sk-ant-...

# Firecrawl (web scraping for literature review)
FIRECRAWL_API_KEY=fc-...

# GitHub token (if not using gh auth login)
# GITHUB_TOKEN=ghp_...

# Modal (GPU compute — modal.com)
MODAL_TOKEN_ID=ak-...
MODAL_TOKEN_SECRET=as-...
```

**Critical:** The `.env` file contains secrets. Never commit it. See [Security](#security) for handling.

---

## Running the Orchestrator as a Daemon

For continuous operation, the orchestrator should run as a system daemon that survives reboots and restarts on failure.

### Linux: systemd Service

Create the service file:

```ini
# /etc/systemd/system/deepwork.service

[Unit]
Description=Deepwork Research Platform Orchestrator
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=deepwork
Group=deepwork
WorkingDirectory=/home/deepwork/deepwork
ExecStart=/usr/bin/node orchestrator/dist/index.js daemon
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=deepwork

# Environment
EnvironmentFile=/home/deepwork/deepwork/.env

# Resource limits
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=200%

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/home/deepwork/deepwork

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable deepwork
sudo systemctl start deepwork

# Check status
sudo systemctl status deepwork

# View logs
journalctl -u deepwork -f
```

### macOS: launchd Plist

Create the plist:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.deepwork.orchestrator</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>/Users/oddurs/Code/deepwork/orchestrator/dist/index.js</string>
        <string>daemon</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/oddurs/Code/deepwork</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>/Users/oddurs</string>
    </dict>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/oddurs/Code/deepwork/logs/orchestrator.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/oddurs/Code/deepwork/logs/orchestrator.error.log</string>

    <key>ThrottleInterval</key>
    <integer>30</integer>
</dict>
</plist>
```

Save as `~/Library/LaunchAgents/com.deepwork.orchestrator.plist` and load:

```bash
# Create logs directory
mkdir -p /Users/oddurs/Code/deepwork/logs

# Load the daemon
launchctl load ~/Library/LaunchAgents/com.deepwork.orchestrator.plist

# Check if running
launchctl list | grep deepwork

# View logs
tail -f /Users/oddurs/Code/deepwork/logs/orchestrator.log

# Stop
launchctl unload ~/Library/LaunchAgents/com.deepwork.orchestrator.plist
```

### Note on the .env File with Daemons

Daemons do not inherit shell environment variables. For systemd, use the `EnvironmentFile` directive (shown above). For launchd, either:
- Add variables to the plist's `EnvironmentVariables` dict (not recommended for secrets), or
- Have the orchestrator load `.env` at startup using `dotenv` or a manual file read, or
- Source `.env` in a wrapper script that the plist calls

Recommended approach: Add a startup routine to the orchestrator that reads `.env` from the working directory.

---

## Daemon Mode Architecture

When the orchestrator runs in daemon mode (the `daemon` subcommand, to be implemented), it operates a continuous scheduling loop.

### The Scheduling Loop

```
┌──────────────────────────────────────────┐
│              Scheduling Loop             │
│                                          │
│  1. Read all project status.yaml files   │
│  2. Filter to active projects            │
│  3. Check resource availability          │
│     - Budget remaining this month        │
│     - API rate limit headroom            │
│     - Number of concurrent sessions      │
│  4. Prioritize projects                  │
│     - Deadline proximity                 │
│     - Phase (final > revision > draft)   │
│     - Time since last session            │
│  5. Start sessions for top-N projects    │
│  6. Monitor running sessions             │
│  7. Handle session completion            │
│     - Commit pending changes             │
│     - Clean up worktrees                 │
│     - Update status                      │
│  8. Sleep for interval (5-15 minutes)    │
│  9. Repeat                               │
└──────────────────────────────────────────┘
```

### Session Cycling

Not all projects run simultaneously. The scheduler cycles through projects:

- **Maximum concurrent sessions:** Limited by Claude Code Max accounts (currently 2) and API rate limits
- **Session duration target:** 30-60 minutes per session (adjustable)
- **Round-robin with priority:** Higher-priority projects (closer to deadline, in revision phase) get more frequent sessions
- **Cool-down period:** After a session ends, a project waits at least 15 minutes before the next session to allow for status file propagation

### Resource Awareness

The scheduler checks before starting any session:

| Resource | Check | Threshold |
|----------|-------|-----------|
| Monthly budget | `budget.yaml` current month total | Must be below `monthly_limit_usd` |
| API rate limits | Recent request count per minute | Must have >20% headroom |
| Disk space | Available space on worktree partition | Must have >1 GB free |
| Concurrent sessions | Active session count | Must be below account limit |

If any resource is exhausted, the scheduler pauses and logs a warning.

---

## GPU Compute (Modal)

GPU compute is needed for experiment phases — running model evaluations, training small models, or executing benchmarks. We use **Modal** (modal.com) as the GPU provider.

### Why Modal

- **Native TypeScript SDK** — the Node.js orchestrator can create GPU sandboxes, call functions, manage volumes, and stream logs directly from TypeScript
- **No Docker build cycle** — experiment code changes are instant. No image rebuild, no push, no redeploy
- **Scale-to-zero** — $0 when idle. Pay only for actual GPU seconds used
- **Infrastructure-as-code** — GPU specs, images, volumes, and secrets defined in Python scripts versioned in the repo
- **Sandboxes** — dynamically create GPU environments with custom dependencies per experiment, all from the orchestrator

### When GPU Is Needed

| Activity | GPU Required | Typical Duration |
|----------|-------------|-----------------|
| Literature review | No | N/A |
| Framework development | No | N/A |
| Benchmark design | No | N/A |
| API-based model evaluation | No (uses Anthropic/OpenAI APIs) | N/A |
| Open-source model evaluation | Yes | 2-8 hours per model |
| Custom training experiments | Yes | 4-24 hours |
| Fine-tuning experiments | Yes | 2-12 hours |

### GPU Pricing

| GPU | $/hr | $500/mo gets you | Best for |
|-----|------|------------------|----------|
| T4 | $0.59 | ~847 hours | Light inference, prototyping |
| A10G | $1.10 | ~454 hours | Medium inference, small fine-tuning |
| L4 | $0.80 | ~625 hours | Inference-optimized workloads |
| A100 80GB | $2.50 | ~200 hours | LLM evaluation, training (sweet spot) |
| H100 | $3.95 | ~127 hours | Maximum throughput, large models |

**Recommended default: A100 80GB** — best balance of capability and cost for LLM benchmarking.

### Setup

```bash
# Install Modal CLI and Python SDK
pip install modal

# Authenticate
modal setup
# → Opens browser for auth, stores token locally

# Install Modal JS SDK in orchestrator
cd orchestrator && npm install modal
```

### Environment Variables

```bash
# .env additions for Modal
MODAL_TOKEN_ID=ak-...
MODAL_TOKEN_SECRET=as-...
```

### How Experiments Run

**From the orchestrator (TypeScript, using Modal JS SDK):**

```typescript
import { ModalClient } from "modal";
const modal = new ModalClient();

// Option 1: Call a pre-deployed experiment function
const runBenchmark = await modal.functions.fromName("deepwork-experiments", "run_benchmark");
const call = await runBenchmark.spawn([experimentConfig]);
const result = await call.get(); // Wait for completion

// Option 2: Create a sandbox on the fly
const app = await modal.apps.fromName("deepwork", { createIfMissing: true });
const image = modal.images.fromRegistry("nvidia/cuda:12.4.0-devel-ubuntu22.04");
const sb = await modal.sandboxes.create(app, image, { gpu: "A100-80GB" });
const proc = await sb.exec(["python", "eval.py", "--config", "benchmark.json"], { stdout: "pipe" });
const output = await proc.stdout.readText();
await sb.terminate();
```

**From the CLI (fallback, for manual runs):**

```bash
# Run an experiment script
modal run experiments/benchmark.py --config experiments/config.json

# Detached mode (survives terminal disconnect)
modal run experiments/benchmark.py -d

# Interactive GPU shell for debugging
modal shell --gpu A100
```

### Experiment Python Scripts

Experiments live in each project's `experiments/` directory as Modal-decorated Python scripts:

```python
# projects/reasoning-gaps/experiments/eval_models.py
import modal

app = modal.App("reasoning-gaps-eval")

image = (
    modal.Image.debian_slim()
    .uv_pip_install(["torch", "transformers", "datasets", "scipy"])
)

results_vol = modal.Volume.from_name("reasoning-gaps-results", create_if_missing=True)
cache_vol = modal.Volume.from_name("model-cache", create_if_missing=True)

@app.function(
    gpu="A100-80GB",
    image=image,
    volumes={"/results": results_vol, "/cache": cache_vol},
    secrets=[modal.Secret.from_name("hf-token")],
    timeout=6 * 3600,  # 6 hour max
)
def run_benchmark(config: dict) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model = AutoModelForCausalLM.from_pretrained(
        config["model_name"], cache_dir="/cache"
    )
    # ... run evaluation ...

    # Write results to persistent volume
    with open(f"/results/{config['run_id']}.json", "w") as f:
        json.dump(metrics, f)

    return metrics
```

### Data Persistence

- **Modal Volumes** persist data across runs (model caches, experiment results, datasets)
- Create volumes: `modal volume create model-cache`
- Upload data: `modal volume put model-cache ./data /data`
- Download results: `modal volume get reasoning-gaps-results /results ./local-results/`
- Volumes are accessible from the Modal dashboard and CLI
- Mount multiple volumes per experiment (cache + results + datasets)

### Automated Workflow

```
Agent designs experiment → writes experiments/<name>/config.yaml
  → Daemon detects new experiment spec
  → Orchestrator calls Modal JS SDK:
      1. Create/reuse Modal App
      2. Deploy experiment function (or create sandbox)
      3. Spawn async job with config
      4. Poll for completion (or await result)
      5. Read results from Modal Volume
      6. Copy results to project directory
      7. Update status.yaml metrics
  → Zero cleanup needed (Modal auto-scales to zero)
```

### Cost Management

- Start with A10G ($1.10/hr) for prototyping, upgrade to A100 for full evaluation runs
- Set `timeout` on every function (prevent runaway experiments)
- Modal dashboard shows real-time cost per app
- Budget GPU compute separately from API costs in `budget.yaml`
- Scale-to-zero means no wasted spend on idle servers
- Use `modal app stop` to force-terminate if needed

### Secrets Management

```bash
# Create secrets for experiment scripts
modal secret create hf-token HF_TOKEN=hf_abc123
modal secret create openai-key OPENAI_API_KEY=sk-...
modal secret create wandb-key WANDB_API_KEY=...

# List secrets
modal secret list
```

### Monitoring

- **Modal dashboard** (modal.com): real-time logs, cost tracking, function call timeline
- Per-call metrics: queue time, cold start time, execution time, GPU utilization
- Stream stdout/stderr from running experiments via JS SDK or CLI
- Logs stored in `.logs/experiments/<name>.log` locally (captured by orchestrator)

---

## API Keys and Rate Limits

### Anthropic API

| Parameter | Value |
|-----------|-------|
| Key env var | `ANTHROPIC_API_KEY` |
| Rate limit (Claude 4 Opus) | ~60 requests/min, ~400K tokens/min |
| Rate limit (Claude 4 Sonnet) | ~120 requests/min, ~800K tokens/min |
| Cost (Opus input/output) | ~$15 / $75 per 1M tokens |
| Cost (Sonnet input/output) | ~$3 / $15 per 1M tokens |

**Note on Claude Code Max accounts:** With Max accounts, API calls made through Claude Code sessions are included in the subscription. The `ANTHROPIC_API_KEY` is for direct API usage via the Claude Agent SDK. The two cost structures are separate -- Max accounts have unlimited usage within their plan, while API key usage is pay-per-token.

**Rate limit strategy:**
- Stagger sessions so they don't all make API calls simultaneously
- Use Sonnet for routine tasks (literature search, formatting) and Opus for critical reasoning
- Monitor rate limit headers in API responses
- Back off exponentially on 429 errors

### Firecrawl API

| Parameter | Value |
|-----------|-------|
| Key env var | `FIRECRAWL_API_KEY` |
| Purpose | Web scraping for literature review |
| Estimated monthly cost | ~$50 |
| Rate limit | Varies by plan (typically 100-500 requests/min) |

Used primarily during the research phase for:
- Scraping paper abstracts and metadata from arxiv, Semantic Scholar, etc.
- Extracting content from technical blogs and documentation
- Downloading publicly available datasets

### GitHub API

| Parameter | Value |
|-----------|-------|
| Auth method | `gh auth login` (preferred) or `GITHUB_TOKEN` |
| Rate limit | 5,000 requests/hr (authenticated) |
| Used for | PR creation, PR listing, branch operations |

The orchestrator uses the `gh` CLI for all GitHub operations, which handles authentication via the gh auth state. Rate limits are rarely an issue with research platform usage patterns.

### Rate Limit Recovery

All API interactions should implement exponential backoff:

```
Attempt 1: immediate
Attempt 2: wait 1s
Attempt 3: wait 2s
Attempt 4: wait 4s
Attempt 5: wait 8s
Max retries: 5
```

If rate limits are consistently hit, reduce the number of concurrent sessions or increase the interval between scheduling loop iterations.

---

## Worktree Disk Layout

### Structure

```
deepwork/                          # Main repo checkout (~50MB base)
├── .worktrees/                    # All project worktrees
│   ├── reasoning-gaps/            # ~100-500MB depending on artifacts
│   │   ├── projects/
│   │   ├── orchestrator/
│   │   └── ...                    # Full repo checkout on research/reasoning-gaps
│   ├── scaling-laws/              # Another project worktree
│   └── ...
├── projects/                      # Project metadata (on main branch)
├── orchestrator/                  # Orchestrator source
├── cli/                           # CLI source
└── .git/                          # Shared git object store
```

### Disk Planning

| Item | Size | Notes |
|------|------|-------|
| Base repo checkout | ~50 MB | Shared across all worktrees via .git |
| Per worktree overhead | ~50-100 MB | Working copy of all tracked files |
| Per project artifacts | 50-400 MB | Papers, figures, data, experiment results |
| Git object store growth | ~5-10 MB/week/project | Commits, diffs, blobs |

**Formula for total disk:**

```
Total = Base (50MB) + N_worktrees * (100MB + avg_artifact_size) + git_objects
```

**Example for 6 concurrent projects:**

```
50MB + 6 * (100MB + 200MB) + 100MB = ~1.95 GB
```

With generous headroom, plan for **5 GB per 6 projects**, plus space for the OS, Node.js, and tools.

### Disk Management

- **Clean up worktrees after sessions:** `SessionManager.stopProject()` removes worktrees automatically
- **Periodic prune:** Run `git worktree prune` weekly to clean stale references
- **Large file policy:** Do not commit datasets >10MB to git. Store them externally and reference by URL
- **Monitor disk usage:**
  ```bash
  # Total worktree usage
  du -sh .worktrees/*

  # Git object store
  du -sh .git/objects

  # Available disk
  df -h .
  ```

---

## Monitoring Infrastructure

### Process Health

**Orchestrator daemon:**

```bash
# systemd (Linux)
systemctl status deepwork
journalctl -u deepwork --since "1 hour ago"

# launchd (macOS)
launchctl list | grep deepwork
tail -100 /Users/oddurs/Code/deepwork/logs/orchestrator.log
```

**Running sessions:**

```bash
# List active Claude Code processes
ps aux | grep claude

# Check worktree state
git worktree list
```

### Disk Monitoring

Set up a simple cron job or monitoring script:

```bash
#!/bin/bash
# /usr/local/bin/deepwork-disk-check.sh

WORKTREE_DIR="/home/deepwork/deepwork/.worktrees"
THRESHOLD_GB=2

AVAILABLE=$(df --output=avail -BG "$WORKTREE_DIR" | tail -1 | tr -d 'G ')

if [ "$AVAILABLE" -lt "$THRESHOLD_GB" ]; then
    echo "WARNING: Deepwork disk space low: ${AVAILABLE}GB remaining"
    # Could send notification here (email, Slack webhook, etc.)
fi
```

Add to crontab:

```bash
# Check disk every hour
0 * * * * /usr/local/bin/deepwork-disk-check.sh >> /var/log/deepwork-disk.log 2>&1
```

### API Quota Monitoring

Track API spend by logging costs after each session:

- The orchestrator should log estimated token usage per session
- Compare against monthly budget in `budget.yaml`
- Alert at 80% threshold (configured in `config.yaml` as `alert_threshold_pct: 80`)

### Health Check Summary

| Check | Frequency | Method | Alert Condition |
|-------|-----------|--------|-----------------|
| Orchestrator process alive | Every 5 min | systemd/launchd watchdog | Process exited |
| Disk space | Hourly | Cron script | <2 GB free |
| API budget | Per session | Orchestrator logging | >80% of monthly limit |
| Stale worktrees | Daily | `git worktree list` | Worktrees older than 7 days |
| Git repo health | Weekly | `git fsck` | Any errors |

---

## Backup Strategy

### Primary Backup: Git

The git repository on GitHub is the primary backup for all project artifacts:

- Every commit is pushed to remote immediately
- All project files, papers, notes, and experiment results are in git
- Branch history preserves the full evolution of every project

**This is sufficient for all research artifacts.** As long as agents push after every commit (which is the configured workflow), GitHub has a complete copy.

### What Git Does NOT Back Up

| Item | Backup Method |
|------|---------------|
| `.env` file (API keys) | Manual copy to password manager or encrypted backup |
| `budget.yaml` (spending history) | In git, but verify it's committed regularly |
| GPU experiment data (large files) | External storage (S3, Google Drive) with links in git |
| Orchestrator logs | Rotate and archive to external storage weekly |
| Daemon configuration (systemd/launchd) | Version-controlled separately or documented here |

### .env Backup Procedure

```bash
# Encrypt and store .env
gpg --symmetric --cipher-algo AES256 .env
# Store .env.gpg in a secure location (password manager, encrypted drive)

# Restore
gpg --decrypt .env.gpg > .env
```

### Recovery Procedure

If the orchestrator machine is lost:

1. Provision a new machine (see [Environment Setup](#environment-setup))
2. Clone the repo: `git clone git@github.com:<org>/deepwork.git`
3. Restore `.env` from secure backup
4. Install dependencies and build: `cd orchestrator && npm install && npm run build`
5. Start the daemon
6. The orchestrator will read project statuses from `main` and resume where it left off

Recovery time target: **under 1 hour** for a prepared operator.

---

## Multi-Machine Setup

The platform can be distributed across machines for different roles.

### Recommended Setup

| Machine | Role | Requirements |
|---------|------|-------------|
| VPS (cloud server) | Always-on orchestrator, automated sessions | 4 CPU, 4 GB RAM, 50 GB disk, $20-50/mo |
| Laptop/Desktop #1 | Human review, interactive Claude Code sessions, dashboard | Git, gh, Node.js |
| Laptop/Desktop #2 | Secondary interactive sessions (second Max account) | Git, gh, Node.js |
| GPU instance (on-demand) | Experiment execution | Provisioned per-experiment |

### Coordination

All machines coordinate through git and GitHub:

- The VPS runs automated sessions and pushes to GitHub
- Laptops pull from GitHub, review PRs, and push interactive work
- GPU instances clone the repo, run experiments, push results, and are terminated

**No direct machine-to-machine communication is needed.** GitHub is the coordination layer.

### Setting Up the VPS

```bash
# 1. Provision a VPS (e.g., DigitalOcean, Hetzner, Linode)
#    - Ubuntu 24.04 LTS
#    - 4 CPU, 4 GB RAM, 50 GB SSD
#    - $20-40/month

# 2. Create a dedicated user
sudo adduser deepwork
sudo usermod -aG sudo deepwork
su - deepwork

# 3. Install dependencies (see Environment Setup above)

# 4. Set up SSH key for GitHub
ssh-keygen -t ed25519 -C "deepwork-server"
# Add the public key to GitHub (deploy key or user key)

# 5. Clone, build, configure (see Environment Setup above)

# 6. Install and start the systemd service (see Daemon section above)
```

### Keeping Machines in Sync

```bash
# On any machine, before starting work:
git fetch --all --prune
git pull origin main

# This ensures you see all project updates, merged PRs, and branch state
```

---

## Network Requirements

### Required Outbound Access

| Destination | Port | Protocol | Purpose |
|-------------|------|----------|---------|
| github.com | 22 | SSH | Git push/pull |
| github.com | 443 | HTTPS | GitHub API, gh CLI |
| api.anthropic.com | 443 | HTTPS | Anthropic API |
| api.firecrawl.dev | 443 | HTTPS | Firecrawl web scraping |

### Bandwidth

Typical bandwidth usage is low:

- Git operations: <10 MB/day for normal commit/push activity
- API calls: <50 MB/day for text-based LLM interactions
- Web scraping: <100 MB/day during active literature review
- Peak: ~500 MB/day during heavy experiment data transfers

### Firewall Configuration

The orchestrator server needs only outbound HTTPS and SSH. No inbound ports are required unless you want to SSH into the server for management.

```bash
# UFW example (Linux)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
```

---

## Security

### API Key Management

**Rules:**

1. API keys live only in `.env` files, never in code or git
2. `.env` is in `.gitignore` (verify this)
3. Each machine has its own `.env` with only the keys it needs
4. Rotate keys quarterly or immediately if compromised
5. Use separate API keys per machine if the provider supports it

**Verification:**

```bash
# Confirm .env is gitignored
git check-ignore .env
# Should output: .env

# Scan for accidentally committed secrets
git log --all --diff-filter=A -- '*.env' '.env*'
# Should return nothing
```

### SSH Keys

- Use Ed25519 keys: `ssh-keygen -t ed25519`
- Use separate keys per machine (server key, laptop key)
- Use GitHub deploy keys (read-only) where possible; read-write only on machines that push
- Protect private keys with a passphrase on interactive machines
- For the daemon server, use an unpassphrased key (the systemd service can't enter passphrases) stored with restrictive permissions (`chmod 600`)

### Server Hardening (VPS)

```bash
# Disable password authentication for SSH
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Keep system updated
sudo apt update && sudo apt upgrade -y

# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Run the orchestrator as a non-root user (already covered in systemd config)
```

### Principle of Least Privilege

| Component | Access Level |
|-----------|-------------|
| Orchestrator daemon | Read/write to repo directory only; no sudo |
| Claude Code sessions | Sandboxed within worktree directory |
| GitHub deploy key (server) | Read-write to the single repository |
| GPU instances | Ephemeral; terminated after use; no persistent keys |
| Human laptops | Full access (owner/admin) |

### Secrets Rotation Schedule

| Secret | Rotation Frequency | Procedure |
|--------|--------------------|-----------|
| Anthropic API key | Quarterly | Generate new key in console, update `.env`, restart daemon |
| Firecrawl API key | Quarterly | Generate new key in dashboard, update `.env`, restart daemon |
| GitHub SSH keys | Annually | Generate new key, add to GitHub, remove old key, update `.env` |
| VPS SSH access | Annually | Rotate user passwords, audit authorized_keys |

---

## Quick Reference: Common Infrastructure Tasks

```bash
# Start the orchestrator manually (foreground)
cd /Users/oddurs/Code/deepwork
node orchestrator/dist/index.js start reasoning-gaps

# View the dashboard
cd cli && npx tsx src/index.tsx

# Check daemon status (Linux)
sudo systemctl status deepwork

# Check daemon status (macOS)
launchctl list | grep deepwork

# View daemon logs (Linux)
journalctl -u deepwork -f

# View daemon logs (macOS)
tail -f logs/orchestrator.log

# List all worktrees
git worktree list

# Clean up stale worktrees
git worktree prune

# Check disk usage
du -sh .worktrees/* .git/objects

# Check budget
cat budget.yaml

# List open PRs
gh pr list --state open

# Verify .env is not tracked
git check-ignore .env
```
