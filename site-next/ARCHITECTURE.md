# site-next Architecture

Frontend for the Deepwork research platform. Built with Next.js 15 (App Router),
React 19, TanStack Query, and Tailwind CSS 4. Connects to a VPS-hosted Express
REST API and WebSocket server.

---

## Technology Stack

| Layer           | Technology                                    |
| --------------- | --------------------------------------------- |
| Framework       | Next.js 16 (App Router, React Server Components) |
| UI              | React 19, Tailwind CSS 4, Radix UI primitives |
| Data fetching   | TanStack React Query 5                        |
| Auth            | NextAuth v5 (Auth.js) + GitHub OAuth          |
| Charts          | Recharts 3                                    |
| Icons           | Lucide React                                  |
| Toasts          | Sonner                                        |
| Command palette | cmdk                                          |
| Database        | PostgreSQL (pg driver, for auth adapter only)  |
| Build output    | `standalone` (Docker-ready)                   |

---

## Directory Structure

```
site-next/
├── next.config.ts              # Standalone output, security headers, pg external pkg
├── package.json
├── tsconfig.json
├── ARCHITECTURE.md             # This file
├── CLAUDE.md                   # Agent instructions
│
└── src/
    ├── app/
    │   ├── layout.tsx          # Root layout: fonts, QueryProvider, html/body
    │   ├── error.tsx           # Global error boundary
    │   ├── not-found.tsx       # Global 404
    │   │
    │   ├── (app)/              # Authenticated routes (requires session)
    │   │   ├── layout.tsx      # Sidebar + header + skip-nav + auth gate
    │   │   ├── loading.tsx     # Suspense fallback
    │   │   ├── error.tsx       # App-scoped error boundary
    │   │   ├── not-found.tsx   # App-scoped 404
    │   │   ├── dashboard/      # Main dashboard
    │   │   ├── projects/       # Project list + [name]/ dynamic route
    │   │   │   └── [name]/     # Per-project layout with tab nav
    │   │   │       ├── layout.tsx
    │   │   │       ├── page.tsx        # Overview
    │   │   │       ├── eval/           # Eval results
    │   │   │       ├── budget/         # Budget breakdown
    │   │   │       ├── sessions/       # Session history
    │   │   │       ├── decisions/      # Decision log
    │   │   │       ├── verification/   # Verification reports
    │   │   │       └── planner/        # Planner insights
    │   │   ├── collective/     # Agent collective: forum, governance, rituals, messages
    │   │   ├── knowledge/      # Knowledge graph browser, alerts, stats
    │   │   ├── backlog/        # Ticket backlog
    │   │   ├── paper/          # Paper builder
    │   │   ├── logs/           # Activity & event logs
    │   │   └── settings/       # Platform settings
    │   │
    │   ├── (marketing)/        # Public routes (no auth required)
    │   │   ├── layout.tsx
    │   │   ├── page.tsx        # Landing page
    │   │   ├── about/
    │   │   ├── blog/
    │   │   ├── papers/
    │   │   └── research/
    │   │
    │   ├── sign-in/            # Auth sign-in page
    │   ├── api/auth/           # NextAuth API route handlers
    │   ├── proxy/[...path]/    # Authenticated API proxy to VPS
    │   └── ws-token/           # WebSocket auth token endpoint
    │
    ├── components/
    │   ├── ui/                 # Base UI primitives (shadcn/ui style)
    │   │   ├── badge.tsx
    │   │   ├── button.tsx
    │   │   ├── card.tsx
    │   │   ├── dialog.tsx
    │   │   ├── dropdown-menu.tsx
    │   │   ├── empty-state.tsx
    │   │   ├── label.tsx
    │   │   ├── metric-card.tsx
    │   │   ├── page-header.tsx
    │   │   ├── progress-bar.tsx
    │   │   ├── skeleton.tsx
    │   │   ├── status-badge.tsx
    │   │   ├── status-dot.tsx
    │   │   ├── tabs.tsx
    │   │   └── tooltip.tsx
    │   │
    │   ├── app-sidebar.tsx     # Main sidebar navigation
    │   ├── breadcrumb-nav.tsx  # Dynamic breadcrumb from pathname
    │   ├── command-palette.tsx # Cmd+K command palette (cmdk)
    │   ├── user-menu.tsx       # User avatar + sign-out dropdown
    │   │
    │   ├── collective/         # Agent collective components
    │   ├── knowledge/          # Knowledge graph components
    │   ├── backlog/            # Backlog components
    │   ├── paper/              # Paper builder components
    │   └── logs/               # Log viewer components
    │
    ├── hooks/
    │   ├── index.ts            # Barrel export (~120 hooks)
    │   ├── use-projects.ts     # useProjects, useProject
    │   ├── use-eval.ts         # useEvalData, useEvalStatus
    │   ├── use-budget.ts       # useBudget
    │   ├── use-sessions.ts     # useSessions
    │   ├── use-collective.ts   # Forum, agents, predictions, calibration
    │   ├── use-knowledge.ts    # Claims, subgraph, contradictions
    │   ├── use-governance.ts   # Proposals, voting
    │   ├── use-rituals.ts      # Ritual scheduling
    │   ├── use-messages.ts     # Inbox, mentions, send
    │   ├── use-ws-invalidation.ts # WebSocket → React Query bridge
    │   └── ...                 # ~30 hook files total
    │
    ├── lib/
    │   ├── api.ts              # Client-side apiFetch (via /proxy)
    │   ├── api-server.ts       # Server-side serverFetch (direct to VPS)
    │   ├── auth.ts             # NextAuth config (GitHub provider)
    │   ├── auth-adapter.ts     # PostgreSQL adapter for auth sessions
    │   ├── constants.ts        # Status colors, data colors
    │   ├── agents.ts           # Agent registry (id, name, color)
    │   ├── nav-items.ts        # Sidebar navigation items
    │   ├── format.ts           # Formatting utilities
    │   ├── types.ts            # Core API types
    │   └── *-types.ts          # Domain-specific type definitions
    │
    ├── providers/
    │   ├── query-provider.tsx      # TanStack QueryClientProvider
    │   ├── app-providers.tsx       # WebSocket + Toaster wrapper
    │   └── websocket-provider.tsx  # WebSocket context with reconnect
    │
    └── styles/
        ├── globals.css         # Tailwind imports, base styles
        └── tokens.css          # CSS custom properties (design tokens)
```

---

## Route Groups

### `(app)` — Authenticated

All routes under `src/app/(app)/` require a valid session. The layout calls
`auth()` from NextAuth and redirects unauthenticated users to `/sign-in`.

Features: sidebar navigation, breadcrumb header, skip-nav link, command palette,
WebSocket connectivity, toast notifications.

### `(marketing)` — Public

Static marketing pages: landing, about, blog, papers, research. No auth required.
Separate layout without sidebar or WebSocket.

---

## Authentication

**NextAuth v5** with GitHub OAuth:

1. User clicks "Sign in with GitHub" on `/sign-in`
2. OAuth flow via `api/auth/[...nextauth]` route handlers
3. Sessions stored in PostgreSQL via custom `auth-adapter.ts`
4. Allowlist via `AUTH_ALLOWED_USERS` env var (comma-separated GitHub usernames)
5. Session checked server-side in `(app)/layout.tsx` — redirect if missing

Environment variables:
- `AUTH_GITHUB_ID` / `AUTH_GITHUB_SECRET` — GitHub OAuth app credentials
- `AUTH_ALLOWED_USERS` — optional user allowlist
- `AUTH_SECRET` — NextAuth session encryption key
- `DATABASE_URL` — PostgreSQL connection string for session storage

---

## API Proxy

Client-side code never talks directly to the VPS. All API requests go through
a Next.js catch-all route at `src/app/proxy/[...path]/route.ts`.

```
Browser → /proxy/projects → Next.js proxy → VPS:3001/api/projects
```

The proxy:
1. Checks the user's session (rejects 401 if unauthenticated)
2. Forwards the request to the VPS Express API
3. Injects `X-Api-Key` header for VPS authentication
4. Supports GET, POST, PATCH, PUT, DELETE methods
5. Forwards query parameters and JSON bodies
6. Returns 502 if the upstream is unreachable

**Server-side fetching** uses `serverFetch()` from `lib/api-server.ts` which
calls the VPS directly with the API key (for Server Components, Server Actions).

**Client-side fetching** uses `apiFetch()` from `lib/api.ts` which routes
through `/proxy` (no API key in the browser).

---

## Data Fetching

All client-side data fetching uses **TanStack React Query 5**.

### Pattern

Each domain has a hook file in `src/hooks/` that exports query hooks:

```ts
// hooks/use-projects.ts
export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => apiFetch<Project[]>('/projects'),
  });
}
```

Mutation hooks follow the same pattern with `useMutation` and automatic
cache invalidation.

### Hook Categories

- **Read hooks**: `useProjects`, `useEvalData`, `useBudget`, `useKnowledgeClaims`, ...
- **Mutation hooks**: `useCreateTicket`, `useCastVote`, `useSendMessage`, ...
- **Real-time**: `useWsInvalidation` bridges WebSocket events to query invalidation

All hooks are re-exported from `hooks/index.ts` for clean imports:
```ts
import { useProjects, useBudget, useWsInvalidation } from '@/hooks';
```

---

## WebSocket Integration

Real-time updates flow through a WebSocket connection managed by
`WebSocketProvider` in `src/providers/websocket-provider.tsx`.

### Connection Flow

1. Provider fetches a signed URL from `/ws-token` on mount
2. Opens a WebSocket connection with auto-reconnect (exponential backoff)
3. Components subscribe to channels via `useWebSocket().subscribe(channel)`
4. `useWsInvalidation` hook maps channel events to React Query invalidations:

| Channel         | Invalidated Query Keys      |
| --------------- | --------------------------- |
| `eval-progress` | `['eval']`                  |
| `logs`          | `['activity']`, `['sessions']` |
| `budget`        | `['budget']`                |
| `health`        | `['health']`, `['daemon']`  |

---

## Design System

### Visual Language

**Neo-brutalist** aesthetic: sharp corners, visible borders, monospace typography,
high-contrast dark theme. Inspired by terminal UIs and research tooling.

### Typography

- **Primary**: IBM Plex Mono (headings, body, code, navigation)
- **Secondary**: IBM Plex Sans (long-form content)
- Loaded via `next/font/google` with CSS variables `--font-mono` and `--font-sans`

### Theming

CSS custom properties defined in `src/styles/tokens.css`:

- `--color-bg`, `--color-bg-elevated`, `--color-bg-hover` — background layers
- `--color-text`, `--color-text-bright`, `--color-text-secondary`, `--color-text-muted` — text hierarchy
- `--color-border` — borders
- `--color-primary` — accent / interactive
- Status colors: `--color-status-ok`, `--color-status-warn`, `--color-status-error`

Dark mode is the only mode (`<html class="dark">`).

### Component Library

Base primitives in `src/components/ui/` follow shadcn/ui conventions:
- Built on Radix UI for accessibility (Dialog, DropdownMenu, Popover, Tooltip, Tabs)
- Styled with Tailwind utility classes
- Composed into domain-specific components in feature directories

---

## Build & Deployment

### Next.js Configuration

```ts
// next.config.ts
{
  output: 'standalone',           // Self-contained build for Docker
  poweredByHeader: false,         // Security: remove X-Powered-By
  images: { unoptimized: true },  // No image optimization (static deploy)
  serverExternalPackages: ['pg'], // Keep pg out of webpack bundle
}
```

Security headers applied to all routes: `X-Frame-Options: DENY`,
`X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`.

### Build

```bash
npm run build    # Produces .next/standalone/
npm run start    # Starts production server
```

The `standalone` output includes a minimal Node.js server and all dependencies,
ready to be copied into a Docker container.

### Environment Variables

| Variable              | Required | Description                       |
| --------------------- | -------- | --------------------------------- |
| `DATABASE_URL`        | Yes      | PostgreSQL for auth sessions      |
| `AUTH_SECRET`         | Yes      | NextAuth encryption key           |
| `AUTH_GITHUB_ID`      | Yes      | GitHub OAuth client ID            |
| `AUTH_GITHUB_SECRET`  | Yes      | GitHub OAuth client secret        |
| `AUTH_ALLOWED_USERS`  | No       | Comma-separated GitHub usernames  |
| `VPS_API_URL`         | Yes      | Express API URL (e.g. http://89.167.5.50:3001) |
| `VPS_API_KEY`         | Yes      | API key for VPS authentication    |

---

## Accessibility

- Skip-to-content link as first focusable element in the app layout
- Sidebar: `role="navigation"`, `aria-label="Main navigation"`, `aria-expanded` on collapsible sections
- Breadcrumbs: `aria-label="Breadcrumb"`, `aria-current="page"` on active item
- Tab navigation: horizontally scrollable on mobile (`overflow-x-auto`)
- All interactive elements have visible focus indicators
- Radix UI primitives provide keyboard navigation and screen reader support

---

## Key Architectural Decisions

1. **Proxy pattern over direct API calls**: Client never holds the API key.
   All requests go through the Next.js proxy which injects auth. This keeps
   secrets server-side and provides a single origin for CORS.

2. **React Query over Server Components for data**: Most pages are client
   components using React Query. This enables real-time updates via WebSocket
   invalidation and optimistic UI for mutations. Server Components are used
   for the auth gate and static layouts.

3. **WebSocket for push updates**: Rather than polling, the VPS pushes events
   over WebSocket. The client maps these to React Query cache invalidations,
   keeping the UI fresh without manual refetch logic.

4. **CSS custom properties over Tailwind theme**: Design tokens are CSS
   variables in `tokens.css`. This allows runtime theming and keeps the
   Tailwind config minimal.

5. **Standalone output**: The `standalone` build bundles everything needed to
   run the app into `.next/standalone/`, making Docker deployment a simple
   `COPY` + `node server.js`.
