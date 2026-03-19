# Next.js Migration: Master Roadmap

> Transform Deepwork from Astro static site to a full-featured Next.js application with auth, real-time dashboards, OpenClaw collective UI, and research pipeline tooling.

**Source Roadmaps:**
- [`nextjs-infrastructure.md`](nextjs-infrastructure.md) — Vercel + VPS split, auth, DNS, SSL
- [`nextjs-frontend.md`](nextjs-frontend.md) — App structure, design system, components, data layer
- [`nextjs-openclaw-ui.md`](nextjs-openclaw-ui.md) — Collective intelligence UI for 9 AI agents
- [`nextjs-pipelines-tooling.md`](nextjs-pipelines-tooling.md) — Pipeline viz, logging, eval drilldown, paper builds

**Total Scope:** ~240–310 hours across 4 roadmaps
**Timeline:** 7–8 sprints (each sprint = 1 agent team session)
**Agent Team:** 2–3 parallel agents per sprint where dependencies allow

---

## Sprint Overview

| Sprint | Theme | Agents | Key Deliverable |
|--------|-------|--------|-----------------|
| **S1** | Foundation | 3 parallel | Next.js app deploys to Vercel, VPS has HTTPS + CORS, design system ported |
| **S2** | Auth & Data Layer | 2 parallel | GitHub OAuth working, API proxy live, TanStack Query hooks |
| **S3** | Marketing & Dashboard Shell | 3 parallel | Public pages ported, app shell with sidebar/header, dashboard overview |
| **S4** | Project Detail Pages | 3 parallel | Eval heatmap, budget charts, decisions, session history |
| **S5** | OpenClaw Core | 3 parallel | Agent grid, forum threads, mission control |
| **S6** | Pipelines & Logging | 3 parallel | Pipeline viz, log viewer, paper build UI |
| **S7** | Real-time & Polish | 2 parallel | WebSocket events, command palette, animations, OpenClaw predictions/governance |
| **S8** | Refinement & Launch | 2 parallel | Accessibility, mobile, performance, DNS cutover |

---

## Sprint 1: Foundation

> **Goal:** Next.js app scaffold deployed to Vercel, VPS secured with HTTPS and CORS, design system migrated.

### Agent 1A: Infrastructure Setup
**Source:** Infrastructure Steps 1–5

| Task | Source | Effort |
|------|--------|--------|
| Configure DNS: `api.deepwork.site` A record → VPS, `deepwork.site` CNAME → Vercel | Infra §3.1 | 10 min |
| SSL/HTTPS on VPS via certbot + nginx config for `api.deepwork.site` | Infra §3.2 | 20 min |
| Update CORS on VPS: set `CORS_ORIGIN=https://deepwork.site` | Infra §3.3 | 10 min |
| Create `009_authjs.sql` migration (users, accounts, sessions, verification_tokens) | Infra §3.4 | 15 min |
| Run migration on VPS PostgreSQL | Infra §3.4 | 5 min |

**Verification:**
- `curl https://api.deepwork.site/api/health` returns 200
- Auth.js tables exist in PostgreSQL

### Agent 1B: Next.js Scaffold + Vercel Deploy
**Source:** Frontend Phase 1, Infrastructure Step 5

| Task | Source | Effort |
|------|--------|--------|
| Create `site-next/` with `npx create-next-app@latest` (App Router, TypeScript, Tailwind) | Frontend §8.1 | 15 min |
| Configure `next.config.ts` (output, images, redirects) | Frontend §8.1 | 30 min |
| Link to Vercel, configure custom domain `deepwork.site` | Infra §3.5 | 30 min |
| Set Vercel environment variables (VPS_API_URL, VPS_API_KEY, AUTH_SECRET, etc.) | Infra §3.10 | 15 min |
| Create root layout with `next/font/google` (IBM Plex Mono, IBM Plex Sans) | Frontend §2 | 30 min |
| Verify deploy: empty Next.js app live at `deepwork.site` | — | 5 min |

### Agent 1C: Design System Migration
**Source:** Frontend Phase 1–2

| Task | Source | Effort |
|------|--------|--------|
| Port CSS tokens from `site/src/styles/tokens.css` to Tailwind config / CSS variables | Frontend §2 | 1–2h |
| Port global styles from `site/src/styles/global.css` | Frontend §2 | 1h |
| Build UI primitives: Button, Card, Badge, StatusBadge, StatusDot, Label, Skeleton | Frontend §3 | 3–4h |
| Build Radix wrappers: Dialog, DropdownMenu, Tabs, Popover, Tooltip (styled to match design) | Frontend §3 | 2–3h |
| Build layout primitives: Container, Section, PageHeader, Heading | Frontend §3 | 1h |
| Sonner toaster setup | Frontend §3 | 15 min |

**Deliverable:** Component library in `site-next/components/ui/` with design system parity.

---

## Sprint 2: Auth & Data Layer

> **Goal:** GitHub OAuth login working, API proxy forwarding requests to VPS, TanStack Query configured.

### Agent 2A: Authentication
**Source:** Infrastructure Steps 6–7, Frontend §7

| Task | Source | Effort |
|------|--------|--------|
| Create GitHub OAuth app (callback URL: `https://deepwork.site/api/auth/callback/github`) | Infra §3.6 | 10 min |
| Install & configure Auth.js v5 with GitHub provider + PostgreSQL adapter | Infra §3.6 | 2h |
| Configure user allowlist (only authorized GitHub usernames can log in) | Infra §3.6 | 30 min |
| Set up PostgreSQL remote access for Auth.js (dedicated `authjs` user, SSL) | Infra §3.7 | 1h |
| Create auth middleware: protect `(app)` routes, redirect unauthenticated to sign-in | Frontend §7 | 1h |
| Build sign-in page and session display in header (avatar, dropdown, sign-out) | Frontend §7 | 1–2h |

**Alternative:** If opening port 5432 is too risky, use Neon free tier for auth tables only (5-minute setup, no VPS exposure).

### Agent 2B: API Proxy & Data Layer
**Source:** Infrastructure Step 8, Frontend Phase 3

| Task | Source | Effort |
|------|--------|--------|
| Build Next.js API proxy route: `app/api/vps/[...path]/route.ts` | Infra §3.8 | 1–2h |
| Create typed `apiFetch()` utility (server-side fetch with API key injection) | Frontend §4 | 1h |
| Set up TanStack Query: QueryClientProvider, devtools, default options | Frontend §4 | 1h |
| Build core query hooks: `useProjects`, `useProject`, `useEvalData`, `useBudget`, `useDecisions` | Frontend §4 | 2–3h |
| Configure cache revalidation intervals per data type | Frontend §4 | 30 min |
| WebSocket client singleton with reconnection logic + React context provider | Frontend §5 | 2h |

**Verification:**
- Authenticated user can hit `/api/vps/projects` and see project data
- TanStack Query devtools show cached data in browser

---

## Sprint 3: Marketing & Dashboard Shell

> **Goal:** Public marketing pages ported, app shell with sidebar/header, main dashboard page live.

### Agent 3A: Marketing Pages
**Source:** Frontend Phase 4

| Task | Source | Effort |
|------|--------|--------|
| Port homepage (hero, project cards, blog posts) | Frontend §8.4 | 2–3h |
| Port about page | Frontend §8.4 | 1h |
| Port papers index + `/papers/reasoning-gaps` detail page | Frontend §8.4 | 2h |
| Port blog index + 4 blog posts (as JSX pages, MDX later) | Frontend §8.4 | 2–3h |
| Port `/research/reasoning-gaps` research detail page | Frontend §8.4 | 1h |

### Agent 3B: App Shell & Dashboard
**Source:** Frontend Phase 5

| Task | Source | Effort |
|------|--------|--------|
| Build AppSidebar: nav sections (Dashboard, Projects, Collective, Logs, Settings), project list, responsive collapse | Frontend §6 | 3–4h |
| Build AppHeader: breadcrumbs, session display, command palette trigger | Frontend §6 | 2h |
| Build `(app)/layout.tsx`: persistent shell wrapping all authenticated pages | Frontend §6 | 1h |
| Build dashboard page: 4 metric cards, project cards grid, recent decisions, system health panel | Frontend §8.5 | 4–5h |

### Agent 3C: Backend Enhancements (Batch 1)
**Source:** Pipelines §6 (new endpoints needed)

| Task | Source | Effort |
|------|--------|--------|
| `GET /api/sessions/:id` — session metadata endpoint | Pipelines §6 | 1h |
| `GET /api/sessions/:id/transcript` — paginated JSONL transcript serving | Pipelines §6 | 2h |
| `GET /api/projects/:id/phases` — structured phase data from status.yaml | Pipelines §6 | 1h |
| `GET /api/budget/daily-history` — historical daily spending | Pipelines §6 | 1h |
| `GET /api/agents` — agent list with definitions | Pipelines §6 | 30 min |
| `GET /api/collective/health` — single aggregated health endpoint | OpenClaw App. A | 1h |

---

## Sprint 4: Project Detail Pages

> **Goal:** Full project view with eval heatmap, budget tracking, decisions, and session history.

### Agent 4A: Eval Pipeline
**Source:** Frontend Phase 6, Pipelines Phase 4

| Task | Source | Effort |
|------|--------|--------|
| Build project layout with TabNav (Overview, Eval, Budget, Sessions, Decisions, Paper, Pipeline) | Frontend §8.6 | 2h |
| Build project overview page (phase indicator, key metrics, recent activity) | Frontend §8.6 | 3h |
| Build AccuracyHeatmap component (model × task, color-coded cells, tooltips) | Pipelines §1.3 | 4h |
| Build ConditionTabs (switch between direct/CoT/budget_cot/tool_use views) | Pipelines §1.3 | 1h |
| Build cell drill-down: click cell → instance-level data (correct/incorrect, difficulty) | Pipelines §1.3 | 3h |
| Backend: `GET /api/projects/:id/eval/instances` (instance-level data) | Pipelines §6 | 2h |

### Agent 4B: Budget & Decisions
**Source:** Frontend Phase 6, Pipelines Phase 1

| Task | Source | Effort |
|------|--------|--------|
| Build budget page: summary cards (spent, remaining, burn rate, projected) | Pipelines §3 | 2h |
| Build burn chart (Recharts area chart, daily spending over time) | Pipelines §3 | 2h |
| Build provider breakdown (pie chart + table) | Pipelines §3 | 1h |
| Build model-level cost chart | Pipelines §3 | 1h |
| Build decisions page (chronological list, date + decision + rationale) | Frontend §8.6 | 2h |

### Agent 4C: Session History
**Source:** Pipelines Phase 2–3

| Task | Source | Effort |
|------|--------|--------|
| Build sessions list page (filterable by agent type, status, date) | Pipelines §2 | 2h |
| Build TranscriptViewer (conversation rendering, tool call expansion, turn navigation) | Pipelines §2 | 5–6h |
| Build TerminalOutput (ANSI color support for build logs) | Pipelines §2 | 2h |
| Build SessionDAG with ReactFlow (nodes = sessions, edges = chain relationships) | Pipelines §3 | 4h |

---

## Sprint 5: OpenClaw Core

> **Goal:** Collective intelligence UI — agent grid, forum threads, mission control dashboard.

### Agent 5A: Agent Identity & Mission Control
**Source:** OpenClaw Phase 1

| Task | Source | Effort |
|------|--------|--------|
| Build agent identity system: colors, monogram avatars, role badges, status animations | OpenClaw §4 | 3h |
| Build AgentAvatar component (size variants, status dot, pulse animation) | OpenClaw §3 | 1h |
| Build Mission Control page: agent status bar (9 avatars), stats grid, activity ticker, active proposals | OpenClaw §2a | 4–5h |
| Build `(app)/collective/layout.tsx` with collective navigation | OpenClaw §2 | 1h |

### Agent 5B: Forum
**Source:** OpenClaw Phase 2

| Task | Source | Effort |
|------|--------|--------|
| Build ForumPost component (type-specific rendering: proposal/debate/signal/synthesis) | OpenClaw §3 | 3h |
| Build ThreadCard (preview with author, replies, vote summary) | OpenClaw §3 | 2h |
| Build VoteBar (support/oppose/abstain with agent avatars, animated) | OpenClaw §3 | 2h |
| Build forum page: thread list, filtering by topic/agent/type, pagination | OpenClaw §2b | 3h |
| Build thread detail page: full conversation with nested replies | OpenClaw §2b | 3h |

### Agent 5C: Agent Grid & Profiles
**Source:** OpenClaw Phase 3

| Task | Source | Effort |
|------|--------|--------|
| Build agent grid page (9 cards with role, model, status, recent activity, trust scores) | OpenClaw §2c | 3h |
| Build agent profile page: activity timeline, trust relationships, learning log | OpenClaw §2d | 4h |
| Build TrustGraph component (D3/visx force-directed graph of inter-agent trust) | OpenClaw §3 | 3–4h |
| Build CalibrationChart (predicted vs actual probabilities) | OpenClaw §3 | 2h |

---

## Sprint 6: Pipelines & Paper

> **Goal:** Pipeline visualization, paper build UI, remaining pipeline tooling.

### Agent 6A: Phase Pipeline & Paper Build
**Source:** Pipelines Phase 5–6

| Task | Source | Effort |
|------|--------|--------|
| Build PhasePipeline component (horizontal stepper with stream completion bars) | Pipelines §1.1 | 3h |
| Build pipeline page integrating phase stepper + session DAG (from S4) | Pipelines §1.1 | 2h |
| Build paper build page: build trigger button, step-by-step progress, log output | Pipelines §1.4 | 3h |
| Build PdfViewer (inline PDF preview with react-pdf) | Pipelines §1.4 | 2h |
| Build build history list with status/duration/download links | Pipelines §1.4 | 1h |
| Backend: `GET /api/paper/builds` + paper_builds table + WebSocket channel | Pipelines §6 | 2h |

### Agent 6B: Eval Comparison & Live Feed
**Source:** Pipelines Phase 4 (remaining), Frontend Phase 7

| Task | Source | Effort |
|------|--------|--------|
| Build ComparisonView: side-by-side eval results across conditions | Pipelines §1.3 | 3h |
| Build EvalProgressBanner (WebSocket-driven progress for running evals) | Pipelines §1.3 | 2h |
| Build live event feed page (port from Astro, enhance with new WebSocket infra) | Frontend §7 | 3h |
| Build ConnectionStatus indicator (connected/reconnecting/disconnected) | Frontend §7 | 1h |

### Agent 6C: Settings
**Source:** Pipelines Phase 7

| Task | Source | Effort |
|------|--------|--------|
| Build settings page: daemon config display, health status | Pipelines §7 | 2h |
| Build API key management (masked display, regenerate) | Pipelines §7 | 1h |
| Build project management table (create, archive, pause/resume) | Pipelines §7 | 2h |
| Build agent configuration viewer (roles, models, schedules) | Pipelines §7 | 1h |
| Backend: `GET /api/daemon/config`, `GET /api/agents/definitions` | Pipelines §6 | 1h |

---

## Sprint 7: Real-time & Polish

> **Goal:** WebSocket-driven live updates everywhere, command palette, animations, OpenClaw remaining pages.

### Agent 7A: Real-time & Command Palette
**Source:** Frontend Phase 7–8

| Task | Source | Effort |
|------|--------|--------|
| Wire WebSocket events to TanStack Query cache invalidation across all pages | Frontend §5 | 3h |
| Build command palette with cmdk (⌘K: search projects, jump to agents, trigger builds) | Frontend §8.8 | 3h |
| Add Framer Motion page transitions (fade + Y-translate between routes) | Frontend §6 | 2h |
| Add micro-interactions: hover effects, loading skeletons, optimistic updates | Frontend §8.8 | 2h |

### Agent 7B: OpenClaw Remaining Pages
**Source:** OpenClaw Phase 4–5

| Task | Source | Effort |
|------|--------|--------|
| Build Prediction Market page (prediction cards, probability timeline, calibration leaderboard) | OpenClaw §2e | 4h |
| Build Ritual Calendar page (timeline view, participant display, outcomes) | OpenClaw §2f | 3h |
| Build Governance page (active proposals, vote tallies, process change history) | OpenClaw §2g | 3h |
| Add real-time updates to collective pages (live posts, votes, status changes) | OpenClaw §5 | 2h |
| Add notification system for collective events (toast + tray) | OpenClaw §5 | 2h |

---

## Sprint 8: Refinement & Launch

> **Goal:** Accessibility, mobile responsiveness, performance, DNS cutover from Astro to Next.js.

### Agent 8A: Quality & Accessibility
**Source:** OpenClaw Phase 6, Frontend Phase 8

| Task | Source | Effort |
|------|--------|--------|
| WCAG AA accessibility audit: ARIA labels, keyboard navigation, focus management | OpenClaw §6 | 3h |
| Responsive design pass: sidebar collapse, mobile layouts, touch targets | Frontend §8.8 | 3h |
| Performance audit: Lighthouse, bundle analysis, image optimization | Frontend §8.8 | 2h |
| Error boundary refinement: per-section error states, retry mechanisms | Frontend §4 | 1h |

### Agent 8B: Launch
**Source:** Infrastructure Step 11–12

| Task | Source | Effort |
|------|--------|--------|
| Final DNS cutover: point `deepwork.site` to Vercel (if not already) | Infra §3.1 | 10 min |
| Set up monitoring: UptimeRobot for both Vercel and VPS health endpoints | Infra §3.11 | 30 min |
| Decommission old Astro site (archive `site/` directory) | — | 15 min |
| Smoke test all pages and flows | — | 2h |
| Document the new architecture in ARCHITECTURE.md | — | 1h |

---

## Dependency Graph

```
Sprint 1 ──────────────────────────────────────────────────────────────
  Agent 1A: Infrastructure (DNS, SSL, CORS, DB migration)
  Agent 1B: Next.js scaffold + Vercel deploy
  Agent 1C: Design system + UI primitives
         │
Sprint 2 ──────────────────────────────────────────────────────────────
  Agent 2A: Auth (GitHub OAuth + middleware)     ← needs 1A (DB), 1B (Next.js)
  Agent 2B: API proxy + data layer              ← needs 1A (HTTPS), 1B (Next.js)
         │
Sprint 3 ──────────────────────────────────────────────────────────────
  Agent 3A: Marketing pages                     ← needs 1C (design system)
  Agent 3B: App shell + dashboard               ← needs 2A (auth), 2B (data)
  Agent 3C: Backend enhancements (new endpoints) ← independent
         │
Sprint 4 ──────────────────────────────────────────────────────────────
  Agent 4A: Eval pipeline                       ← needs 3B (app shell), 3C (endpoints)
  Agent 4B: Budget + decisions                  ← needs 3B (app shell)
  Agent 4C: Sessions + transcript viewer        ← needs 3B (app shell), 3C (endpoints)
         │
Sprint 5 ──────────────────────────────────────────────────────────────
  Agent 5A: Agent identity + mission control    ← needs 3B (app shell)
  Agent 5B: Forum                               ← needs 5A (agent identity)
  Agent 5C: Agent grid + profiles               ← needs 5A (agent identity)
         │
Sprint 6 ──────────────────────────────────────────────────────────────
  Agent 6A: Phase pipeline + paper build        ← needs 4C (session DAG)
  Agent 6B: Eval comparison + live feed         ← needs 4A (eval), 2B (WebSocket)
  Agent 6C: Settings                            ← needs 3B (app shell)
         │
Sprint 7 ──────────────────────────────────────────────────────────────
  Agent 7A: Real-time + command palette         ← needs all prior sprints
  Agent 7B: OpenClaw remaining pages            ← needs 5A-5C (OpenClaw foundation)
         │
Sprint 8 ──────────────────────────────────────────────────────────────
  Agent 8A: Quality + accessibility             ← needs all prior sprints
  Agent 8B: Launch + cutover                    ← needs 8A
```

---

## Effort Summary

| Sprint | Agents | Est. Hours | Cumulative |
|--------|--------|-----------|------------|
| S1 | 3 | 12–18h | 12–18h |
| S2 | 2 | 10–14h | 22–32h |
| S3 | 3 | 18–24h | 40–56h |
| S4 | 3 | 30–40h | 70–96h |
| S5 | 3 | 24–32h | 94–128h |
| S6 | 3 | 20–26h | 114–154h |
| S7 | 2 | 16–22h | 130–176h |
| S8 | 2 | 10–14h | 140–190h |
| **Total** | — | **140–190h** | — |

---

## Tech Stack Summary

| Category | Choice | Why |
|----------|--------|-----|
| Framework | Next.js 15 (App Router) | RSC, Server Actions, layouts, middleware |
| Auth | Auth.js v5 + GitHub OAuth | Works with existing PostgreSQL, no new service |
| Styling | Tailwind CSS 4 | Already using, port design tokens |
| Data Fetching | TanStack Query v5 | Caching, background revalidation, devtools |
| Real-time | WebSocket (existing) | Already built, just need client integration |
| Charts | Recharts | Lightweight, composable, good for heatmaps |
| UI Primitives | Radix UI | Headless, accessible, style to match design |
| Animations | Framer Motion | Page transitions, skeletons, micro-interactions |
| Icons | Lucide React | Already using lucide-static, easy upgrade |
| Command Palette | cmdk | ⌘K search, proven (used by Linear, Vercel) |
| Toasts | Sonner | Simple, beautiful, matches dark theme |
| Log Viewer | CodeMirror 6 | Syntax highlighting, ANSI support |
| Graph Viz | ReactFlow | Session DAG, interactive node graphs |
| Trust Graph | visx (D3) | Force-directed agent relationship graphs |

---

## Key Decisions & Tradeoffs

| Decision | Choice | Alternative Considered | Rationale |
|----------|--------|----------------------|-----------|
| Hosting | Vercel (frontend) + VPS (backend) | Self-host everything on VPS | Zero-config deploys, preview branches, edge middleware. VPS keeps doing what it does well. |
| Auth DB | Auth.js in existing PostgreSQL | Supabase Auth, Clerk | No new service, no migration, free. Allowlist means only 1 user for now. |
| PG Access | Dedicated `authjs` user + SSL | Neon free tier for auth tables | Simpler, but opening port 5432 is a risk. Neon is the fallback. |
| State Mgmt | TanStack Query (server state) + React state (UI state) | Redux, Zustand | No global client state needed — all data comes from API. |
| Charts | Recharts | Nivo, Chart.js, D3 | Recharts is React-native, composable, good for our use cases. D3 only for trust graph (via visx). |
| Blog | JSX pages initially | MDX from day 1 | Get it working first, add MDX in a later sprint. 4 blog posts don't justify MDX setup cost. |
| OpenClaw Viz | visx for trust graph | Full D3, Sigma.js | visx wraps D3 in React components. More ergonomic than raw D3. |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Tailwind v4 + Next.js 15 PostCSS issues | Medium | Medium | Test in S1, fall back to v3 if needed |
| Port 5432 exposure for Auth.js | High | Low | Use Neon free tier instead if uncomfortable |
| WebSocket through Vercel | Medium | Medium | Three fallbacks: short-lived tokens, SSE, polling |
| TranscriptViewer complexity | Low | High | Build incrementally, start with raw JSON rendering |
| VPS resource pressure (Next.js was removed, but more API load) | Low | Low | VPS currently uses <1GB of 3.7GB RAM |
| DNS propagation delays | Low | Medium | Set low TTL before cutover |
