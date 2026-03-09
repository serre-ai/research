# Monitoring UI and Dashboard Research

## Executive Summary

For the Deepwork platform's monitoring needs, we recommend a **phased approach**: start with a GitHub-based MVP (Issues + Projects board + markdown status files), then graduate to a lightweight web dashboard (Next.js or SvelteKit) as requirements grow. A terminal UI (Ink) can serve as a complementary developer tool.

---

## 1. Dashboard/UI Framework Options

### Option A: Next.js App Router (Web Dashboard)

**Strengths:**
- Mature ecosystem with many admin dashboard templates (shadcn/ui, TailAdmin, NextAdmin)
- Server Components reduce client-side JS, improving performance
- Built-in API routes for backend logic
- Server-Sent Events (SSE) and WebSocket support for real-time updates
- Large community, extensive documentation
- Easy deployment on Vercel or self-hosted

**Weaknesses:**
- Heavier than needed for an MVP
- Requires React knowledge
- More infrastructure to maintain

**Best for:** Production-grade dashboard with rich UI, multiple views, and user authentication.

**Key templates:** shadcn/ui admin dashboard (Vercel), TailAdmin (free/open-source), NextAdmin (200+ components).

### Option B: SvelteKit (Lighter Web Alternative)

**Strengths:**
- Smaller bundle sizes than Next.js (~40% less JS)
- Built-in SSE support for real-time streaming
- Simpler mental model (less boilerplate than React)
- Built-in API routes and SSR
- Excellent for internal tools and dashboards

**Weaknesses:**
- Smaller ecosystem than React/Next.js
- Fewer pre-built dashboard templates
- Smaller hiring pool if team grows

**Best for:** Lightweight internal dashboard where performance and simplicity matter more than ecosystem.

### Option C: Ink (React-in-Terminal)

**Strengths:**
- Uses React patterns (useState, useEffect, hooks) in the terminal
- Real-time updates without a browser
- Flexbox layouts via Yoga
- TypeScript support out of the box
- Perfect for developer-facing monitoring
- No web server needed

**Weaknesses:**
- Limited to terminal display capabilities
- Can't easily share with non-technical stakeholders
- No persistent visual state (closes when process ends)

**Best for:** Developer CLI tool for quick status checks, complementing a web dashboard.

### Option D: Textual (Python Terminal UI)

**Strengths:**
- 120 FPS renders via Rich's segment trees
- 2.5M+ PyPI downloads, strong adoption
- CSS-like styling for terminal apps
- Async-first (asyncio)
- Can also serve as a web app via Textual Web

**Weaknesses:**
- Python-based (if the rest of the stack is TypeScript/Node.js, this adds a language)
- Less natural integration with Claude Code SDK (which is TypeScript/Python dual)

**Best for:** Python-heavy teams or when dual terminal/web serving via Textual Web is attractive.

### Recommendation: **Next.js App Router** for the web dashboard (when needed), with an **Ink-based CLI** as a quick developer tool. Start with **GitHub + markdown files** for MVP.

---

## 2. What the Dashboard Needs to Show

### Core Views

| View | Data Source | Priority |
|------|------------|----------|
| Active research projects & status | Git repos, status files | P0 |
| Git activity (commits, PRs, branches) | GitHub API / git CLI | P0 |
| Claude Code session status | Claude Code SDK / Analytics API | P0 |
| Decision queue (needs human input) | Custom queue (file/DB) | P0 |
| Paper/document drafts with preview | File system, markdown | P1 |
| Collaboration status | Session metadata | P1 |

### Data Sources Available

- **Claude Code Analytics API**: Daily aggregated metrics (sessions, LOC, commits, PRs, tool usage, tokens, costs)
- **Claude Code SDK**: `listSessions()` for session enumeration, session state on disk
- **GitHub API**: Commits, PRs, issues, branches via `gh` CLI or REST/GraphQL API
- **File system**: Status markdown files, research documents, logs

---

## 3. Decision-Making Interface Patterns

### Human-in-the-Loop (HITL) Approaches

Based on research into LangGraph, Temporal, n8n, and other frameworks:

**Pattern 1: Interrupt-and-Resume**
- Agent pauses at decision points, writes a decision request to a queue
- Human reviews and responds (approve/reject/modify)
- Agent resumes with the decision
- Used by: LangGraph's `interrupt()`, Temporal's signals

**Pattern 2: Async Approval Queue**
- Decisions accumulate in a queue (file, database, or GitHub Issues)
- Human reviews batch of decisions periodically
- Agent continues other work while waiting
- Used by: n8n Wait node, custom approval workflows

**Pattern 3: Confidence-Based Routing**
- High-confidence decisions proceed automatically
- Low-confidence or high-risk decisions route to humans
- Over time, the threshold adjusts based on feedback
- Used by: Most production AI agent systems

### Recommended Implementation for Deepwork

**MVP (GitHub-based):**
- Create GitHub Issues with a "decision-needed" label
- Use GitHub Projects board with a "Decision Queue" column
- Agent creates issues; human comments with decisions
- Agent polls for responses via `gh` CLI

**Growth (Custom UI):**
- WebSocket-based notification when decisions are queued
- Dashboard view with approve/reject/modify buttons
- Slack/email notifications for urgent decisions
- Decision history and audit trail

### Notification Systems

| Channel | Complexity | Best For |
|---------|-----------|----------|
| GitHub notifications | Zero setup | Already using GitHub |
| Slack webhook | Low | Team already on Slack |
| Email (SendGrid/SES) | Medium | Async, non-urgent |
| Web push | Medium-High | Real-time, browser-based |
| CLI alerts (terminal bell) | Zero | Developer at terminal |

---

## 4. Real-Time Monitoring Approaches

### File System Watching

**Chokidar (Node.js):**
- Standard for Node.js file watching (~30M repos use it)
- Wraps fs.watch/fs.watchFile/FSEvents
- v5 (Nov 2025): ESM-only, requires Node.js v20+
- Events: add, change, unlink, ready
- Low CPU usage (avoids polling by default)

**Use case for Deepwork:** Watch status files, research documents, and git directories for changes. Trigger dashboard updates on file changes.

### Real-Time Dashboard Architecture

**Option 1: Server-Sent Events (SSE)** - RECOMMENDED for MVP
- One-way server-to-client streaming
- Simpler than WebSockets
- Native browser support (EventSource API)
- SvelteKit and Next.js both support SSE well
- Perfect for dashboard updates, log streaming

**Option 2: WebSockets**
- Bi-directional communication
- More complex setup and state management
- Better when client needs to send frequent updates
- Overkill for a monitoring dashboard

**Option 3: Polling**
- Simplest to implement
- Works with any backend (even static files)
- 5-10 second intervals sufficient for research monitoring
- No persistent connections to manage

**Recommended:** Start with **polling** (read status files every 10s), graduate to **SSE** when real-time feels necessary.

### Log Streaming

- Claude Code SDK sessions write to disk; tail these files
- Use chokidar to watch log directories
- Stream via SSE to dashboard
- Consider structured logging (JSON lines) for easier parsing

---

## 5. Lightweight MVP Options

### Option A: GitHub-Based Workflow (RECOMMENDED MVP)

**How it works:**
- **GitHub Issues** = research tasks and decision queue
- **GitHub Projects board** = kanban view of all work
- **Labels** = status tracking (in-progress, needs-review, decision-needed, blocked)
- **Markdown status files** in repo = machine-readable status
- **GitHub Actions** = automated status updates
- **`gh` CLI** = programmatic access from Claude Code agents

**Pros:**
- Zero additional infrastructure
- Already integrated with git workflow
- Built-in notifications (email, mobile, web)
- Automation via GitHub Actions
- API access via `gh` CLI (perfect for Claude Code)
- Free for public repos, included in GitHub plans

**Cons:**
- Limited real-time capabilities
- No custom visualizations
- Dependent on GitHub's UI
- Not ideal for complex dashboards

**Implementation:**
```
repo/
  .github/
    ISSUE_TEMPLATE/
      decision-request.md    # Template for decision queue items
      research-task.md       # Template for research tasks
    workflows/
      update-status.yml      # Auto-update project board
  status/
    platform-status.md       # Overall platform status
    projects/
      project-1-status.md    # Per-project status (machine-readable YAML frontmatter)
    sessions/
      active-sessions.json   # Current Claude Code sessions
    decisions/
      pending.json           # Pending decisions queue
```

### Option B: Markdown Status Files + Simple Viewer

**How it works:**
- Agents write structured markdown/YAML status files
- A simple static site generator (Astro, 11ty) renders them
- Deployed to GitHub Pages or served locally
- File watcher triggers rebuilds

**Pros:**
- Extremely simple
- Git-native (all changes tracked)
- Works offline
- Easy to parse programmatically

**Cons:**
- Not real-time without a watcher
- Limited interactivity

### Option C: CLI Monitoring Tool (Ink-based)

**How it works:**
- `deepwork status` command shows current state
- Reads from status files and git
- Real-time updates via file watching
- Interactive: can approve decisions from terminal

**Pros:**
- Fast to build with Ink
- No browser needed
- Integrates naturally with developer workflow
- Can be the first "product" of the platform

---

## 6. Phased Recommendation

### Phase 1: MVP (Week 1-2)
- **GitHub Issues + Projects board** for task tracking and decision queue
- **Structured markdown status files** in the repo for machine-readable state
- **Simple CLI tool** (`deepwork status`) using Ink for developer monitoring
- **`gh` CLI** for all GitHub interactions from agents

### Phase 2: Enhanced CLI + Simple Web (Week 3-4)
- **Richer Ink CLI** with real-time file watching (chokidar)
- **Static dashboard** (GitHub Pages or simple HTML) rendering status files
- **Slack webhook** for decision notifications
- **Claude Code Analytics API** integration for usage metrics

### Phase 3: Full Dashboard (Month 2+)
- **Next.js App Router** dashboard with SSE for real-time updates
- **Custom decision queue UI** with approve/reject/modify
- **Session monitoring** via Claude Code SDK
- **Git activity visualization**
- **Document preview** for research papers

### Technology Stack Summary

| Component | MVP | Growth |
|-----------|-----|--------|
| Task tracking | GitHub Issues + Projects | Same + custom views |
| Decision queue | GitHub Issues (labeled) | Custom UI + Slack |
| Status display | Markdown files + CLI | Next.js dashboard |
| Real-time updates | Polling / file watch | SSE |
| Notifications | GitHub notifications | Slack + web push |
| Session monitoring | Status files | Claude Code SDK + Analytics API |
| Git activity | `gh` CLI | GitHub API + dashboard |

---

## Key Technical Notes

- **Claude Code Analytics API** provides daily aggregated metrics only; for real-time session monitoring, use the SDK's `listSessions()` or watch session files on disk
- **Chokidar v5** is ESM-only and requires Node.js v20+ (align with project requirements)
- **GitHub Projects** supports automation via GitHub Actions, reducing manual status updates
- **SSE > WebSockets** for this use case (one-way data flow to dashboard)
- **Structured status files** (YAML frontmatter + markdown) serve as the universal data layer that both CLI and web dashboard can consume
