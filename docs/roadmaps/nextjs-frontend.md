# Next.js 15 Frontend Migration

**Status:** Proposed
**Author:** Oddur Sigurdsson
**Date:** 2026-03-19
**Estimated effort:** 60-80 hours across 8 phases

---

## Overview

Migrate the Deepwork dashboard and marketing site from Astro 5 (static/SSR with `.astro` components) to Next.js 15 (App Router, React Server Components, Server Actions). The current site lives at `site/src/` with 22 Astro components, 12 pages, a typed API client, and a WebSocket-based live feed. The new app will live at `site-next/` (or replace `site/` once stable) and add real-time interactivity, client-side navigation, a command palette, and animated transitions that the current static architecture cannot support.

### Why Migrate

1. **Interactivity ceiling.** Astro components are HTML-first — the live feed page (`site/src/pages/dashboard/live.astro`) resorts to 260 lines of inline `<script>` because Astro has no React runtime in the browser. Every interactive feature (filters, WebSocket, charts) requires raw DOM manipulation.
2. **No client-side routing.** Every page navigation is a full reload. The dashboard's tab navigation (`TabNav.astro`) triggers a server round-trip to switch between Overview/Eval/Budget/Decisions tabs.
3. **No shared client state.** WebSocket connections, filter state, and auth sessions cannot persist across navigations.
4. **Component reuse.** Astro components cannot be composed in client-side interactive contexts. The same `MetricCard` that works in SSR cannot be used inside a React chart tooltip.

### What We Keep

- Design language: neo-brutalist, dark theme (#0a0a0a), IBM Plex Mono/Sans, sharp corners, no border-radius
- All CSS design tokens from `site/src/styles/tokens.css`
- Tailwind CSS 4 with the existing `@theme` block from `site/src/styles/global.css`
- The VPS API at port 3001 (Express + WebSocket, `orchestrator/src/api.ts`)
- All existing page content and data structures from `site/src/data/mock.ts`

---

## 1. App Structure

### File Tree

```
site-next/
├── app/
│   ├── layout.tsx                        # Root layout: html, body, fonts, global CSS
│   ├── not-found.tsx                     # Custom 404
│   ├── error.tsx                         # Root error boundary
│   ├── loading.tsx                       # Root loading (global spinner)
│   │
│   ├── (marketing)/                      # Route group: public pages, no sidebar
│   │   ├── layout.tsx                    # Marketing layout: nav + footer (mirrors Base.astro)
│   │   ├── page.tsx                      # / — homepage (current index.astro)
│   │   ├── about/
│   │   │   └── page.tsx                  # /about
│   │   ├── blog/
│   │   │   ├── page.tsx                  # /blog — post listing
│   │   │   └── [slug]/
│   │   │       └── page.tsx              # /blog/[slug] — individual post
│   │   ├── papers/
│   │   │   ├── page.tsx                  # /papers — paper listing
│   │   │   └── [slug]/
│   │   │       └── page.tsx              # /papers/[slug] — paper detail (reasoning-gaps)
│   │   └── research/
│   │       └── [slug]/
│   │           └── page.tsx              # /research/[slug] — research explainer
│   │
│   ├── (app)/                            # Route group: authenticated dashboard, sidebar
│   │   ├── layout.tsx                    # App shell: sidebar + header + main content area
│   │   ├── dashboard/
│   │   │   ├── page.tsx                  # /dashboard — portfolio overview
│   │   │   ├── loading.tsx               # Dashboard skeleton
│   │   │   └── live/
│   │   │       └── page.tsx              # /dashboard/live — real-time event feed
│   │   └── project/
│   │       └── [name]/
│   │           ├── layout.tsx            # Project layout: TabNav persists across sub-pages
│   │           ├── page.tsx              # /project/[name] — overview
│   │           ├── loading.tsx           # Project skeleton
│   │           ├── eval/
│   │           │   └── page.tsx          # /project/[name]/eval — heatmap + CoT analysis
│   │           ├── budget/
│   │           │   └── page.tsx          # /project/[name]/budget — budget tracker
│   │           ├── decisions/
│   │           │   └── page.tsx          # /project/[name]/decisions — decision log
│   │           └── sessions/
│   │               └── page.tsx          # /project/[name]/sessions — session history (new)
│   │
│   └── api/
│       └── proxy/
│           └── [...path]/
│               └── route.ts             # Proxy to VPS API (server-side, hides API key)
│
├── components/
│   ├── ui/                               # Primitives (Radix-based, design-system)
│   │   ├── badge.tsx
│   │   ├── breadcrumb.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── command.tsx                   # cmdk wrapper
│   │   ├── dialog.tsx                    # Radix Dialog
│   │   ├── dropdown-menu.tsx             # Radix DropdownMenu
│   │   ├── empty-state.tsx
│   │   ├── popover.tsx                   # Radix Popover
│   │   ├── progress.tsx
│   │   ├── skeleton.tsx                  # Animated loading placeholder
│   │   ├── tabs.tsx                      # Radix Tabs
│   │   ├── tooltip.tsx                   # Radix Tooltip
│   │   └── toaster.tsx                   # Sonner provider
│   │
│   ├── layout/                           # Shell and navigation
│   │   ├── app-sidebar.tsx               # Collapsible sidebar (projects, nav links)
│   │   ├── app-header.tsx                # Top bar: breadcrumbs, user avatar, search trigger
│   │   ├── marketing-nav.tsx             # Public nav bar (mirrors current <nav> in Base.astro)
│   │   ├── marketing-footer.tsx          # Public footer
│   │   ├── logo.tsx                      # DEEPWORK wordmark + icon
│   │   ├── breadcrumb-auto.tsx           # Auto-generates breadcrumbs from route segments
│   │   └── animated-layout.tsx           # Framer Motion page transition wrapper
│   │
│   ├── command-palette.tsx               # cmd+K global command palette
│   ├── connection-status.tsx             # WebSocket connection indicator
│   │
│   ├── dashboard/                        # Dashboard-specific domain components
│   │   ├── project-card.tsx
│   │   ├── metric-card.tsx
│   │   ├── decision-item.tsx
│   │   ├── status-badge.tsx
│   │   ├── status-dot.tsx
│   │   ├── system-health.tsx
│   │   └── aggregate-stats.tsx
│   │
│   ├── eval/                             # Eval monitor domain components
│   │   ├── accuracy-heatmap.tsx
│   │   ├── heatmap-cell.tsx
│   │   ├── cot-lift-card.tsx
│   │   ├── scale-comparison.tsx
│   │   └── eval-pipeline-summary.tsx
│   │
│   ├── budget/                           # Budget tracker domain components
│   │   ├── budget-kpis.tsx
│   │   ├── provider-breakdown.tsx
│   │   ├── daily-spend-chart.tsx
│   │   ├── monthly-progress.tsx
│   │   └── model-cost-table.tsx
│   │
│   ├── live/                             # Live feed components
│   │   ├── event-feed.tsx
│   │   ├── event-row.tsx
│   │   └── filter-bar.tsx
│   │
│   └── charts/                           # Reusable chart components (Recharts)
│       ├── sparkline.tsx
│       ├── bar-chart.tsx
│       └── area-chart.tsx
│
├── lib/
│   ├── api-client.ts                     # Typed fetch wrapper (server-side, hits VPS directly)
│   ├── api-types.ts                      # API response types (from current mock.ts interfaces)
│   ├── constants.ts                      # MODEL_DISPLAY, PHASE_DISPLAY, task definitions
│   ├── helpers.ts                        # cellBg, cellText, liftColor, timeAgo, etc.
│   ├── websocket.ts                      # WebSocket singleton, reconnection, event dispatch
│   └── hooks/
│       ├── use-projects.ts               # TanStack Query: projects list
│       ├── use-project.ts                # TanStack Query: single project
│       ├── use-eval-data.ts              # TanStack Query: eval progress
│       ├── use-budget.ts                 # TanStack Query: budget data
│       ├── use-decisions.ts              # TanStack Query: decision log
│       ├── use-activity.ts               # TanStack Query: recent activity
│       ├── use-health.ts                 # TanStack Query: system health
│       ├── use-websocket.ts              # WebSocket connection hook
│       └── use-command-palette.ts        # cmd+K state
│
├── providers/
│   ├── query-provider.tsx                # TanStack QueryClientProvider
│   └── websocket-provider.tsx            # WebSocket context provider
│
├── styles/
│   ├── tokens.css                        # Copied from site/src/styles/tokens.css
│   └── globals.css                       # Adapted from site/src/styles/global.css
│
├── public/
│   └── fonts/                            # Self-hosted IBM Plex (optional, or keep Google Fonts)
│
├── next.config.ts
├── tailwind.config.ts                    # Extends with design tokens
├── tsconfig.json
└── package.json
```

### Route Groups

| Group | Purpose | Layout | Auth |
|-------|---------|--------|------|
| `(marketing)` | Public pages: home, about, blog, papers, research explainers | `marketing-nav.tsx` + `marketing-footer.tsx`, full-width, no sidebar | None |
| `(app)` | Authenticated dashboard: project views, live feed, settings | `app-sidebar.tsx` + `app-header.tsx`, sidebar layout | Required (middleware redirect) |

### Layout Hierarchy

```
app/layout.tsx                  ← html, body, fonts, QueryProvider, WebSocketProvider, Toaster
├── (marketing)/layout.tsx      ← MarketingNav + MarketingFooter, max-w-6xl container
│   ├── page.tsx                ← Homepage
│   ├── about/page.tsx
│   ├── blog/page.tsx
│   └── ...
└── (app)/layout.tsx            ← AppSidebar + AppHeader + AnimatedLayout, flex layout
    ├── dashboard/page.tsx
    ├── dashboard/live/page.tsx
    └── project/[name]/
        └── layout.tsx          ← TabNav (Overview|Eval|Budget|Decisions|Sessions)
            ├── page.tsx
            ├── eval/page.tsx
            └── ...
```

**What persists across navigations:**
- Root layout: font loading, CSS, QueryClient (cache survives route changes), WebSocket connection, Sonner toaster
- `(app)` layout: sidebar state (expanded/collapsed), header with breadcrumbs, user session
- `project/[name]/layout.tsx`: TabNav with active state, project header (title, venue, status badge)

---

## 2. Design System Migration

### CSS Token Strategy

The existing tokens in `site/src/styles/tokens.css` define CSS custom properties for spacing, typography, and status colors. The `global.css` file extends Tailwind 4's `@theme` directive to register these as Tailwind utilities. This approach carries over directly.

**Step 1: Copy tokens verbatim.** The `:root` block in `tokens.css` (lines 6-70) stays unchanged. All 12 spacing values, 8 typography sizes, 6 status colors, 2 accent colors, and 6 chart palette colors are preserved.

**Step 2: Adapt global.css for Next.js.** The `@theme` block in `global.css` (lines 4-33) already registers Tailwind theme extensions. This works with Tailwind CSS 4 in Next.js without modification. The `@layer base` styles (lines 35-106) also port directly.

**Step 3: Map tokens to Tailwind config.** For utilities that need programmatic access (e.g., Recharts colors), expose tokens as a JavaScript object:

```typescript
// lib/constants.ts
export const colors = {
  bg: '#0a0a0a',
  bgElevated: '#171717',
  bgSurface: '#1a1a1a',
  bgHover: '#1f1f1f',
  text: '#e5e5e5',
  textSecondary: '#a1a1a1',
  textMuted: '#737373',
  textBright: '#fafafa',
  border: 'rgba(255, 255, 255, 0.1)',
  borderStrong: '#404040',
  primary: '#3b82f6',
  success: '#10b981',
  danger: '#ef4444',
  warning: '#f59e0b',
  data: ['#60a5fa', '#34d399', '#fbbf24', '#a78bfa', '#f87171', '#22d3ee'],
} as const;
```

### Typography Scale

The current typography uses IBM Plex Mono for headings/labels/data and IBM Plex Sans for body text. This is defined in `global.css` lines 5-7:

```css
--font-mono: 'IBM Plex Mono', 'SF Mono', 'Consolas', monospace;
--font-sans: 'IBM Plex Sans', 'Inter', -apple-system, 'Segoe UI', sans-serif;
--font-serif: 'IBM Plex Serif', 'Georgia', serif;
```

In Next.js, load fonts via `next/font/google` in the root layout for optimal performance (font files are self-hosted, no layout shift):

```typescript
// app/layout.tsx
import { IBM_Plex_Mono, IBM_Plex_Sans, IBM_Plex_Serif } from 'next/font/google';

const plexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  style: ['normal', 'italic'],
  variable: '--font-mono',
});

const plexSans = IBM_Plex_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  style: ['normal', 'italic'],
  variable: '--font-sans',
});
```

### Typography Patterns to Preserve

From the existing codebase, these patterns recur across every page:

| Pattern | Usage | CSS |
|---------|-------|-----|
| `.stat-value` | Large numeric displays (MetricCard, budget totals) | `font-mono text-3xl font-bold tabular-nums text-[var(--color-text-bright)]` |
| `.stat-label` | Uppercase micro-labels above stats | `font-mono text-[10px] uppercase tracking-[0.05em] text-[var(--color-text-muted)]` |
| `.label` | Section headings, nav items | `font-mono text-xs font-medium uppercase tracking-[0.05em] text-[var(--color-text-muted)]` |
| Page titles | `PageHeader` h1 | `font-mono text-2xl sm:text-3xl font-bold tracking-tight text-[var(--color-text-bright)]` |
| Data cells | Heatmap, tables | `font-mono text-sm font-semibold tabular-nums` |

All of these must be preserved exactly. Create Tailwind `@apply` aliases or component-level className constants for consistency.

### Color Palette (Complete)

**Surfaces:**
- Background: `#0a0a0a` — page background
- Elevated: `#171717` — cards, panels (used by every `Card.astro`, `MetricCard.astro`)
- Surface: `#1a1a1a` — nested containers, table alternating rows
- Hover: `#1f1f1f` — interactive element hover
- Subnav: `#111111` — tab navigation bar background

**Text:**
- Bright: `#fafafa` — headings, primary data, emphasis
- Default: `#e5e5e5` — body text
- Secondary: `#a1a1a1` — supporting text, descriptions
- Muted: `#737373` — labels, timestamps, tertiary info

**Borders:**
- Default: `rgba(255, 255, 255, 0.1)` — subtle dividers
- Strong: `#404040` — section separators, active borders
- Emphasis: `#e5e5e5` — section top borders on about page

**Status (with muted + border variants):**
- OK: `#10b981` / `rgba(16, 185, 129, 0.15)` / `rgba(16, 185, 129, 0.25)`
- Warn: `#f59e0b` / `rgba(245, 158, 11, 0.15)` / `rgba(245, 158, 11, 0.25)`
- Error: `#ef4444` / `rgba(239, 68, 68, 0.15)` / `rgba(239, 68, 68, 0.25)`
- Idle: `#737373` / `rgba(115, 115, 115, 0.15)` / `rgba(115, 115, 115, 0.25)`

### Dark Theme

The current site is dark-only. No light mode toggle is planned. The dark theme is implemented through the `@theme` directive in `global.css`, not through Tailwind's `dark:` variant. This means:

1. All color tokens in `@theme` define the dark palette directly
2. `html { background-color: var(--color-bg); color: var(--color-text); }` sets the default
3. No `class="dark"` or `prefers-color-scheme` detection needed
4. Keep it this way in Next.js — dark-only simplifies the entire design system

### Responsive Breakpoints

The current site uses Tailwind's default breakpoints: `sm:` (640px), `md:` (768px), `lg:` (1024px). The `max-w-6xl` container (1152px) with `px-6` padding is used on every page via `Container.astro`. Key responsive patterns:

- **Grid columns:** `grid-cols-1 md:grid-cols-2` (project cards), `grid-cols-2 md:grid-cols-4` (metric cards), `grid-cols-1 lg:grid-cols-3` (sidebar panels)
- **Typography:** `text-4xl sm:text-5xl md:text-6xl` (hero), `text-2xl sm:text-3xl` (page headers)
- **Layout:** Stack on mobile, side-by-side on desktop for dashboard cards, budget panels, CoT lift grids
- **Sidebar (new):** Hidden on mobile (slide-out drawer), visible and collapsible on `lg:` and above. Content area fills remaining space.

### Component Library Plan (Radix Primitives)

| Radix Primitive | Why Needed | Current Equivalent |
|-----------------|------------|-------------------|
| `Dialog` | Command palette overlay, confirmation modals, session details | None (new) |
| `DropdownMenu` | User menu, project actions, export options | None (new) |
| `Tabs` | Replace `TabNav.astro` with client-side tabs that don't trigger navigation | `TabNav.astro` (link-based, full reload) |
| `Popover` | Inline details: metric card hover, model info, help text | None (new) |
| `Tooltip` | Heatmap cell details, status explanations, icon button labels | None (new) |

**Styling approach:** Radix primitives are unstyled. Apply the existing design language directly:
- Borders: `border border-[var(--color-border)]`
- Surfaces: `bg-[var(--color-bg-elevated)]`
- Text: `font-mono text-xs text-[var(--color-text-secondary)]`
- Animations: Framer Motion for enter/exit, not CSS transitions (consistency with page transitions)

---

## 3. Component Architecture

### Migration Map: Astro to Next.js

Every existing Astro component maps to a Next.js equivalent. The key decision for each is whether it stays a Server Component (default, zero JS shipped) or needs `'use client'` (interactive).

#### Server Components (No `'use client'` Needed)

These components render static HTML on the server. They can `await` data directly, access server-only code, and ship zero client JavaScript.

| Astro Component | Next.js Component | Location | Notes |
|-----------------|-------------------|----------|-------|
| `Container.astro` | Inline `<div className="max-w-6xl mx-auto px-6">` | No separate file | Too simple for a component — use directly in layouts |
| `PageHeader.astro` | `components/layout/page-header.tsx` | Server | Props: title, subtitle, breadcrumbs, children |
| `Section.astro` | Inline with `section-gap` utility class | No separate file | Same reasoning as Container |
| `Heading.astro` | Inline `<h2>` with size classes | No separate file | Level-based sizing is trivial inline |
| `Card.astro` | `components/ui/card.tsx` | Server | `border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-5` |
| `Badge.astro` | `components/ui/badge.tsx` | Server | Variants: `default`, `outline` |
| `StatusBadge.astro` | `components/dashboard/status-badge.tsx` | Server | Maps status string to color classes via `statusColor()` |
| `StatusDot.astro` | `components/dashboard/status-dot.tsx` | Server | 1.5px dot with health color |
| `Label.astro` | Inline `.label` class | No separate file | Single class wrapper |
| `Breadcrumb.astro` | `components/ui/breadcrumb.tsx` | Server | Slash-separated links |
| `EmptyState.astro` | `components/ui/empty-state.tsx` | Server | Icon + message + detail |
| `ProgressBar.astro` | `components/ui/progress.tsx` | Server | Value-based width bar |
| `DecisionItem.astro` | `components/dashboard/decision-item.tsx` | Server | Date, decision, rationale, optional project link |
| `DataTable.astro` | `components/ui/data-table.tsx` (shell only) | Server | Table wrapper with consistent thead/tbody styling |
| `Logo.astro` | `components/layout/logo.tsx` | Server | CPU icon + "DEEPWORK" wordmark (use Lucide React instead of reading SVG from fs) |
| `Icon.astro` | Replaced by `lucide-react` | N/A | Current Icon.astro reads SVG files from node_modules at build time. In Next.js, import icons directly: `import { Cpu, BarChart3 } from 'lucide-react'` |
| `Stat.astro` | `components/dashboard/stat.tsx` | Server | Label + value + sublabel |
| `MetricCard.astro` | `components/dashboard/metric-card.tsx` | Server | Card with icon, label, value slot, sublabel |
| `ProjectCard.astro` | `components/dashboard/project-card.tsx` | Server | Full project summary card (status, phase, progress bar, stats) |
| `HeatmapCell.astro` | `components/eval/heatmap-cell.tsx` | Server | `cellBg` + `cellText` conditional classes |

#### Client Components (`'use client'` Required)

These need browser APIs, React state, event handlers, or third-party client-side libraries.

| Component | Location | Why Client | Key Dependencies |
|-----------|----------|-----------|------------------|
| `FilterBar` | `components/live/filter-bar.tsx` | Click handlers, active state | React state |
| `EventFeed` | `components/live/event-feed.tsx` | WebSocket subscription, real-time DOM updates, virtual scrolling | `use-websocket` hook, TanStack Query |
| `EventRow` | `components/live/event-row.tsx` | Relative timestamps that update | `useEffect` for time updates |
| `AccuracyHeatmap` | `components/eval/accuracy-heatmap.tsx` | Tooltip on hover, column sorting, filter toggles | Radix Tooltip, React state |
| `CotLiftCard` | `components/eval/cot-lift-card.tsx` | Animated bars, hover details | Framer Motion |
| `DailySpendChart` | `components/budget/daily-spend-chart.tsx` | Interactive chart | Recharts |
| `ConnectionStatus` | `components/connection-status.tsx` | WebSocket state indicator | `use-websocket` hook |
| `CommandPalette` | `components/command-palette.tsx` | Keyboard shortcut, search, navigation | `cmdk`, Radix Dialog |
| `AppSidebar` | `components/layout/app-sidebar.tsx` | Collapse/expand toggle, active route highlighting | React state, `usePathname()` |
| `AnimatedLayout` | `components/layout/animated-layout.tsx` | Page transition animations | Framer Motion, `usePathname()` |
| `TabNav` (app) | Inside `project/[name]/layout.tsx` | Active tab from URL, client-side tab switching with `router.push` | `usePathname()` |
| `SystemHealth` | `components/dashboard/system-health.tsx` | Polls health endpoint, live status dots | TanStack Query with `refetchInterval` |
| `Sparkline` | `components/charts/sparkline.tsx` | SVG rendered client-side for animation | Recharts or custom SVG |

#### New Components (Not in Current Codebase)

| Component | Location | Type | Purpose |
|-----------|----------|------|---------|
| `Skeleton` | `components/ui/skeleton.tsx` | Client | Animated loading placeholder. Pulse animation on `bg-[var(--color-bg-surface)]`. Used inside every `loading.tsx`. |
| `CommandPalette` | `components/command-palette.tsx` | Client | Global `cmd+K` overlay. Uses `cmdk` for fuzzy search over: pages, projects, actions (trigger build, open live feed). Radix Dialog for the overlay. |
| `AnimatedLayout` | `components/layout/animated-layout.tsx` | Client | Wraps `{children}` in Framer Motion `AnimatePresence`. Fade + slight Y-translate on route change. Keyed by `usePathname()`. |
| `AppSidebar` | `components/layout/app-sidebar.tsx` | Client | Collapsible sidebar with: Logo, project list (with status dots), nav links (Dashboard, Live, Settings), collapse button. Persists collapsed state in localStorage. |
| `AppHeader` | `components/layout/app-header.tsx` | Client | Top bar with: auto-generated breadcrumbs, search trigger (opens CommandPalette), connection status indicator, user avatar/menu. |
| `SessionViewer` | `components/dashboard/session-viewer.tsx` | Client | CodeMirror 6 instance for reading session transcripts/logs. Read-only, syntax highlighting for JSON and markdown. |
| `Toaster` | `components/ui/toaster.tsx` | Client | Sonner toast container. Positioned bottom-right. Used for: "Session triggered", "Budget alert", "Connection lost". |

### Component Organization

```
components/
├── ui/             # Design-system primitives. No domain logic. Reusable across any page.
│                   # badge, button, card, dialog, skeleton, tabs, tooltip, etc.
│
├── layout/         # Shell components. Compose the page frame.
│                   # sidebar, header, nav, footer, logo, breadcrumbs, animated-layout
│
├── dashboard/      # Domain: portfolio overview
│                   # project-card, metric-card, decision-item, status-badge, system-health
│
├── eval/           # Domain: evaluation monitor
│                   # accuracy-heatmap, heatmap-cell, cot-lift-card, scale-comparison
│
├── budget/         # Domain: budget tracker
│                   # budget-kpis, provider-breakdown, daily-spend-chart, model-cost-table
│
├── live/           # Domain: real-time event feed
│                   # event-feed, event-row, filter-bar
│
├── charts/         # Reusable chart wrappers (Recharts)
│                   # sparkline, bar-chart, area-chart
│
├── command-palette.tsx
└── connection-status.tsx
```

---

## 4. Data Fetching Strategy

### Architecture Overview

The current data layer (`site/src/data/index.ts`) uses a "try API, fallback to mock" pattern. Every page calls functions like `getProjects()`, `getEvalData()` at build time (Astro SSG) or request time (Astro SSR). The Next.js architecture splits this into two patterns:

1. **Server Components:** Fetch data directly on the server using the typed API client. No network round-trip visible to the user.
2. **Client Components:** Use TanStack Query hooks for data that needs to be interactive, polled, or invalidated by WebSocket events.

### API Client (Server-Side)

The proxy route at `app/api/proxy/[...path]/route.ts` forwards requests to the VPS API, injecting the API key server-side so it never reaches the browser:

```typescript
// app/api/proxy/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.DEEPWORK_API_URL!;   // e.g., http://89.167.5.50:3001
const API_KEY = process.env.DEEPWORK_API_KEY!;

export async function GET(req: NextRequest, { params }: { params: { path: string[] } }) {
  const path = params.path.join('/');
  const url = new URL(`/api/${path}`, API_BASE);
  req.nextUrl.searchParams.forEach((v, k) => url.searchParams.set(k, v));

  const res = await fetch(url.toString(), {
    headers: { 'X-Api-Key': API_KEY },
    signal: AbortSignal.timeout(10000),
  });

  return NextResponse.json(await res.json(), { status: res.status });
}
```

For Server Components, fetch directly from the VPS (bypassing the proxy since we're server-side):

```typescript
// lib/api-client.ts
const API_BASE = process.env.DEEPWORK_API_URL!;
const API_KEY = process.env.DEEPWORK_API_KEY!;

export async function apiFetch<T>(path: string, options?: { revalidate?: number }): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'X-Api-Key': API_KEY },
    next: { revalidate: options?.revalidate ?? 60 },  // ISR: cache for 60s by default
  });
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`);
  return res.json() as Promise<T>;
}
```

### API Types

Port the existing interfaces from `site/src/data/mock.ts` and `site/src/data/api.ts` into `lib/api-types.ts`:

- `Project` — project listing with phases, status, completion
- `ModelData` — model name, family, scale, provider, results by task
- `EvalTask` — task ID, label, gap type
- `ProjectEvalData` — models + tasks + total instances + running models
- `ProjectBudgetData` — monthly/daily limits, providers, daily spend history
- `Decision` — date, project, decision text, rationale
- `ApiProject`, `ApiProgressRow`, `ApiEvalRun`, `ApiDecision`, `ApiBudget` — raw API response shapes

### TanStack Query Hooks (Client-Side)

Each domain has a dedicated hook that wraps TanStack Query's `useQuery`:

```typescript
// lib/hooks/use-projects.ts
import { useQuery } from '@tanstack/react-query';
import type { Project } from '@/lib/api-types';

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: () => fetch('/api/proxy/projects').then(r => r.json()),
    staleTime: 30_000,        // Consider fresh for 30s
    refetchInterval: 60_000,  // Background refetch every 60s
  });
}
```

Other hooks follow the same pattern:
- `useProject(name)` — single project, queryKey: `['project', name]`
- `useEvalData(projectId)` — eval progress, queryKey: `['eval', projectId]`
- `useBudget(projectId)` — budget data, queryKey: `['budget', projectId]`
- `useDecisions(projectId?)` — decisions, queryKey: `['decisions', projectId]`
- `useActivity(count, filters)` — recent activity, queryKey: `['activity', count, filters]`
- `useHealth()` — system health, queryKey: `['health']`, `refetchInterval: 15_000`

### Cache Revalidation Strategy

| Data | Server (RSC) | Client (TanStack) | Revalidation Trigger |
|------|-------------|-------------------|---------------------|
| Project list | `revalidate: 60` | `staleTime: 30s, refetchInterval: 60s` | WebSocket `session_end`, `phase_transition` |
| Eval progress | `revalidate: 30` | `staleTime: 15s, refetchInterval: 30s` | WebSocket `eval_job_completed`, `eval_job_failed` |
| Budget | `revalidate: 120` | `staleTime: 60s, refetchInterval: 120s` | WebSocket `budget_spend` |
| Decisions | `revalidate: 300` | `staleTime: 120s` | WebSocket `decision_created` |
| System health | `revalidate: 10` | `refetchInterval: 15s` | Continuous polling |
| Activity feed | Not cached in RSC | `staleTime: 0` (always fresh) | WebSocket `logs` channel |

### Loading States: Suspense + Skeletons

Each route segment with async data gets a `loading.tsx` that renders skeletons matching the page layout:

```
app/(app)/dashboard/loading.tsx        → 4 MetricCard skeletons + 2 ProjectCard skeletons
app/(app)/project/[name]/loading.tsx   → TabNav + Phase timeline skeleton + 4 MetricCard skeletons
```

Skeleton components use the `Skeleton` primitive:

```tsx
// components/ui/skeleton.tsx
export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn('animate-pulse bg-[var(--color-bg-surface)]', className)} />
  );
}
```

For client components that fetch via TanStack Query, use the hook's `isLoading` state to show inline skeletons within the component, not Suspense boundaries.

### Error Boundaries

Each route group gets an `error.tsx`:

```
app/(app)/error.tsx                         → "Dashboard unavailable" with retry button
app/(app)/project/[name]/eval/error.tsx     → "Eval data unavailable" with retry
app/(app)/project/[name]/budget/error.tsx   → "Budget data unavailable" with retry
```

Error boundaries catch server-side fetch failures and render a styled error state using the existing `EmptyState` component pattern with an added "Retry" button that calls `reset()`.

---

## 5. Real-time Architecture

### WebSocket Connection Management

The current live feed page (`site/src/pages/dashboard/live.astro`, lines 260-322) manages its own WebSocket with reconnection. In Next.js, this becomes a global singleton managed by a React context provider, so the connection persists across all page navigations within the `(app)` route group.

**Connection lifecycle:**

```
WebSocketProvider mounts (in app/(app)/layout.tsx)
  → Establish WSS connection to VPS (/api/ws?api_key=...)
  → Subscribe to channels: ['logs', 'eval-progress']
  → On message: dispatch to registered handlers
  → On close: exponential backoff reconnect (1s → 2s → 4s → ... → 30s cap)
  → On unmount (route group exit): close connection
```

**Implementation:**

```typescript
// lib/websocket.ts
type EventHandler = (event: WsEvent) => void;

class DeepworkWebSocket {
  private ws: WebSocket | null = null;
  private handlers = new Map<string, Set<EventHandler>>();
  private reconnectDelay = 1000;

  connect(url: string) { /* ... */ }
  subscribe(channel: string, handler: EventHandler): () => void { /* returns unsubscribe */ }
  disconnect() { /* ... */ }
}

export const wsClient = new DeepworkWebSocket();
```

```typescript
// providers/websocket-provider.tsx
'use client';

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const wsUrl = buildWsUrl();
    wsClient.connect(wsUrl);
    return () => wsClient.disconnect();
  }, []);

  return <WebSocketContext.Provider value={wsClient}>{children}</WebSocketContext.Provider>;
}
```

### Event Types and UI Mappings

From the current live feed implementation and the API (`orchestrator/src/api.ts`), these are the WebSocket event types:

| Event Type | Channel | UI Update |
|-----------|---------|-----------|
| `session_start` | `logs` | Toast notification, activity feed prepend |
| `session_end` | `logs` | Toast, activity feed, invalidate `['projects']` query |
| `session_error` | `logs` | Error toast, activity feed |
| `commit` | `logs` | Activity feed prepend |
| `push` | `logs` | Activity feed prepend |
| `pr_created` | `logs` | Toast + activity feed |
| `eval_job_queued` | `eval-progress` | Activity feed, invalidate `['eval', projectId]` |
| `eval_job_started` | `eval-progress` | Update running indicator, invalidate `['eval', projectId]` |
| `eval_job_completed` | `eval-progress` | Toast, invalidate `['eval', projectId]`, update heatmap |
| `eval_job_failed` | `eval-progress` | Error toast, invalidate `['eval', projectId]` |
| `budget_spend` | `logs` | Invalidate `['budget', projectId]` |
| `budget_alert` | `logs` | Warning toast, invalidate `['budget', projectId]` |
| `phase_transition` | `logs` | Toast, invalidate `['projects']`, `['project', name]` |
| `daemon_start` | `logs` | Toast, invalidate `['health']` |
| `daemon_stop` | `logs` | Warning toast, invalidate `['health']` |
| `daemon_error` | `logs` | Error toast, invalidate `['health']` |

### TanStack Query Cache Invalidation on Events

A central hook subscribes to WebSocket events and invalidates the relevant queries:

```typescript
// lib/hooks/use-websocket-invalidation.ts
'use client';

import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from './use-websocket';

export function useWebSocketInvalidation() {
  const queryClient = useQueryClient();
  const ws = useWebSocket();

  useEffect(() => {
    const unsubLogs = ws.subscribe('logs', (event) => {
      // Route event types to query invalidation
      switch (event.type) {
        case 'session_end':
        case 'phase_transition':
          queryClient.invalidateQueries({ queryKey: ['projects'] });
          if (event.project) {
            queryClient.invalidateQueries({ queryKey: ['project', event.project] });
          }
          break;
        case 'budget_spend':
        case 'budget_alert':
          queryClient.invalidateQueries({ queryKey: ['budget'] });
          break;
        case 'decision_created':
          queryClient.invalidateQueries({ queryKey: ['decisions'] });
          break;
      }
    });

    const unsubEval = ws.subscribe('eval-progress', (event) => {
      queryClient.invalidateQueries({ queryKey: ['eval'] });
    });

    return () => { unsubLogs(); unsubEval(); };
  }, [queryClient, ws]);
}
```

Mount this hook once in the `(app)` layout so it runs globally across all dashboard pages.

### Optimistic Updates

For actions triggered from the UI (future features like "Trigger Eval Run", "Dispatch Session"):

1. User clicks action button
2. Optimistic update: immediately update the TanStack Query cache to show the expected result (e.g., a new job in "queued" state)
3. Send POST to `/api/proxy/eval/jobs` or `/api/proxy/sessions/dispatch`
4. If server confirms, the WebSocket event will arrive and update the real data
5. If server rejects, roll back the optimistic update and show an error toast

---

## 6. Navigation & Loading

### App Shell

The `(app)` route group uses a sidebar + header layout that persists across all dashboard navigations:

```
┌──────────────────────────────────────────────────┐
│ ┌─────────┐ ┌──────────────────────────────────┐ │
│ │         │ │ Header: Breadcrumbs    [⌘K] [●]  │ │
│ │ DEEPWORK│ ├──────────────────────────────────┤ │
│ │         │ │                                  │ │
│ │ ─ Dash  │ │  Page Content                    │ │
│ │ ─ Live  │ │  (from nested route)             │ │
│ │         │ │                                  │ │
│ │ PROJECTS│ │                                  │ │
│ │ ● r-gaps│ │                                  │ │
│ │ ○ a-f-t │ │                                  │ │
│ │         │ │                                  │ │
│ │ ─ Settngs│ │                                  │ │
│ └─────────┘ └──────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

**Sidebar sections:**
1. Logo (links to `/`)
2. Navigation: Dashboard, Live Feed
3. Projects: dynamically lists projects with status dots (green = running, yellow = paused, gray = idle)
4. Footer: Settings link, connection status, collapse toggle

**Sidebar behavior:**
- Desktop (`lg:` and above): visible, collapsible to icon-only mode (stored in localStorage)
- Mobile (below `lg:`): hidden, slide-out drawer triggered by hamburger button in header

### Page Transitions with Framer Motion

The `AnimatedLayout` component wraps the `(app)` route group's page content:

```tsx
// components/layout/animated-layout.tsx
'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';

export function AnimatedLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -4 }}
        transition={{ duration: 0.15, ease: 'easeOut' }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

Animation values: subtle opacity + Y-translate. Duration 150ms. No heavy slide or scale effects — matches the minimal, data-focused aesthetic.

### Command Palette (cmd+K)

Global keyboard shortcut opens a search overlay using `cmdk` + Radix Dialog:

**Searchable items:**
- Pages: Dashboard, Live Feed, About, Blog, Papers
- Projects: reasoning-gaps, agent-failure-taxonomy (with current status)
- Actions: "Go to eval monitor", "Open budget tracker", "View decisions"
- Recent: last 5 visited pages

**Implementation plan:**
1. `cmdk` provides the fuzzy search input + results list
2. Radix `Dialog` provides the modal overlay (backdrop blur, escape to close)
3. Items are grouped by category: Pages, Projects, Actions
4. Selection navigates via `router.push()`
5. Keyboard shortcut registered in the root `(app)` layout via `useEffect`

### Breadcrumb Generation

Auto-generate breadcrumbs from the Next.js route segments:

```typescript
// components/layout/breadcrumb-auto.tsx
'use client';

import { usePathname } from 'next/navigation';

const SEGMENT_LABELS: Record<string, string> = {
  dashboard: 'Dashboard',
  project: 'Projects',
  eval: 'Eval',
  budget: 'Budget',
  decisions: 'Decisions',
  sessions: 'Sessions',
  live: 'Live Feed',
};

export function AutoBreadcrumb() {
  const pathname = usePathname();
  const segments = pathname.split('/').filter(Boolean);

  const crumbs = segments.map((seg, i) => ({
    label: SEGMENT_LABELS[seg] ?? seg,  // fallback: use segment as-is (e.g., project name)
    href: '/' + segments.slice(0, i + 1).join('/'),
    isLast: i === segments.length - 1,
  }));

  // Render using existing breadcrumb styling (font-mono text-[10px], slash separators)
}
```

### Active State in Sidebar

The sidebar highlights the current route using `usePathname()`:

- Exact match for top-level links (Dashboard = `/dashboard`, Live = `/dashboard/live`)
- Prefix match for projects (`/project/reasoning-gaps/**` highlights the project entry)
- Active style: `text-[var(--color-text-bright)]` with a left border accent `border-l-2 border-[var(--color-primary)]`
- Inactive style: `text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]`

---

## 7. Authentication UI

Authentication is not a launch requirement — the current site has no auth. However, the architecture should support it from day one, since the dashboard exposes sensitive operational data (API costs, system health, eval results).

### Plan

1. **Sign In Page:** `app/(marketing)/sign-in/page.tsx`. Simple email/password or OAuth (GitHub). Centered card on dark background, matches the neo-brutalist design.

2. **Middleware:** `middleware.ts` at the app root. Checks for a session cookie on `(app)` routes. Redirects to `/sign-in` if not authenticated. Public routes (`(marketing)`) are unprotected.

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Only protect /dashboard and /project routes
  if (request.nextUrl.pathname.startsWith('/dashboard') || request.nextUrl.pathname.startsWith('/project')) {
    const session = request.cookies.get('session');
    if (!session) {
      return NextResponse.redirect(new URL('/sign-in', request.url));
    }
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/project/:path*'],
};
```

3. **Session Display:** In the `AppHeader`, show a user avatar (initials-based, e.g., "OS" for Oddur Sigurdsson) with a Radix `DropdownMenu` containing: name, email, "Sign Out" action.

4. **Sign Out:** Server Action that clears the session cookie and redirects to `/`.

5. **Auth Provider:** Start simple with a custom JWT-based auth (no third-party service). The VPS API already has an API key mechanism (`X-Api-Key` header). Extend this to support user sessions. Or, if a managed solution is preferred, use NextAuth.js v5 (Auth.js) with the credentials provider.

**Phase 1 (launch):** No auth. All pages public. API key injected server-side only.
**Phase 2 (post-launch):** Add auth middleware, sign-in page, and session management.

---

## 8. Implementation Order

### Phase 1: Scaffolding & Design System (6-8 hours)

**Dependencies:** None (greenfield)

1. Initialize Next.js 15 project with App Router, TypeScript, Tailwind CSS 4
2. Install dependencies: `@tanstack/react-query`, `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-tabs`, `@radix-ui/react-popover`, `@radix-ui/react-tooltip`, `framer-motion`, `lucide-react`, `sonner`, `cmdk`, `recharts`
3. Port `tokens.css` and `global.css` (copy, adapt imports)
4. Set up `next/font/google` for IBM Plex Mono, Sans, Serif
5. Create root `app/layout.tsx` with font classes, global CSS, Sonner `<Toaster />`
6. Create `app/not-found.tsx` with styled 404 page
7. Verify dark theme renders correctly end-to-end

**Deliverable:** Empty Next.js app with correct typography, colors, and dark theme.

### Phase 2: UI Primitives (6-8 hours)

**Dependencies:** Phase 1

1. Build `components/ui/` primitives: `card.tsx`, `badge.tsx`, `button.tsx`, `progress.tsx`, `skeleton.tsx`, `empty-state.tsx`, `breadcrumb.tsx`, `data-table.tsx`
2. Build Radix wrappers: `dialog.tsx`, `dropdown-menu.tsx`, `tabs.tsx`, `tooltip.tsx`, `popover.tsx`
3. Build `components/ui/toaster.tsx` (Sonner configuration)
4. Port `lib/helpers.ts` from `site/src/utils/helpers.ts` (all color/status/cell utility functions)
5. Port `lib/constants.ts` from `site/src/data/api.ts` (MODEL_DISPLAY, PHASE_DISPLAY, evalTasks, phase builders)
6. Port `lib/api-types.ts` from `site/src/data/mock.ts` interfaces

**Deliverable:** Complete primitive component library and type definitions. No pages yet.

### Phase 3: Data Layer & API Client (4-6 hours)

**Dependencies:** Phase 2

1. Create `lib/api-client.ts` — typed server-side fetch wrapper with `next.revalidate` support
2. Create `app/api/proxy/[...path]/route.ts` — API proxy route that injects API key
3. Create `providers/query-provider.tsx` — TanStack QueryClientProvider
4. Create all TanStack Query hooks in `lib/hooks/`: `use-projects`, `use-project`, `use-eval-data`, `use-budget`, `use-decisions`, `use-activity`, `use-health`
5. Mount `QueryProvider` in root layout
6. Verify data fetching works by rendering a raw JSON dump page

**Deliverable:** Complete data layer. Both server-side `apiFetch` and client-side TanStack Query hooks operational.

### Phase 4: Marketing Pages (8-10 hours)

**Dependencies:** Phase 2

1. Create `(marketing)/layout.tsx` with `MarketingNav` + `MarketingFooter` (port from `Base.astro` lines 24-55)
2. Port homepage: `(marketing)/page.tsx` from `site/src/pages/index.astro`
3. Port about page: `(marketing)/about/page.tsx` from `site/src/pages/about.astro`
4. Port blog listing: `(marketing)/blog/page.tsx` from `site/src/pages/blog/index.astro`
5. Port blog posts: `(marketing)/blog/[slug]/page.tsx` for each of the 4 existing posts
6. Port papers listing: `(marketing)/papers/page.tsx` from `site/src/pages/papers/index.astro`
7. Port papers detail: `(marketing)/papers/[slug]/page.tsx` from `site/src/pages/papers/reasoning-gaps.astro`
8. Port research explainer: `(marketing)/research/[slug]/page.tsx` from `site/src/pages/research/reasoning-gaps.astro`

**Deliverable:** All public-facing pages functional with correct content and styling.

### Phase 5: Dashboard Shell & Portfolio (10-12 hours)

**Dependencies:** Phase 3, Phase 2

1. Build `components/layout/app-sidebar.tsx` — collapsible sidebar with project list
2. Build `components/layout/app-header.tsx` — breadcrumbs + search trigger + connection status
3. Build `components/layout/animated-layout.tsx` — Framer Motion page transitions
4. Create `(app)/layout.tsx` composing sidebar + header + animated content area
5. Build dashboard domain components: `project-card.tsx`, `metric-card.tsx`, `decision-item.tsx`, `status-badge.tsx`, `status-dot.tsx`, `system-health.tsx`, `aggregate-stats.tsx`
6. Port dashboard page: `(app)/dashboard/page.tsx` from `site/src/pages/dashboard/index.astro`
7. Create `(app)/dashboard/loading.tsx` with metric card and project card skeletons
8. Create `(app)/error.tsx` with styled error state

**Deliverable:** Dashboard shell with working sidebar, header, page transitions, and portfolio overview page with live data from VPS.

### Phase 6: Project Detail Pages (12-16 hours)

**Dependencies:** Phase 5

1. Create `(app)/project/[name]/layout.tsx` — project header + TabNav (client-side tabs)
2. Port project overview: `(app)/project/[name]/page.tsx` from `site/src/pages/dashboard/project/[name].astro`
3. Build eval components: `accuracy-heatmap.tsx`, `heatmap-cell.tsx`, `cot-lift-card.tsx`, `scale-comparison.tsx`, `eval-pipeline-summary.tsx`
4. Port eval page: `(app)/project/[name]/eval/page.tsx` from `site/src/pages/dashboard/project/[name]/eval.astro`
5. Build budget components: `budget-kpis.tsx`, `provider-breakdown.tsx`, `daily-spend-chart.tsx` (Recharts), `monthly-progress.tsx`, `model-cost-table.tsx`
6. Port budget page: `(app)/project/[name]/budget/page.tsx` from `site/src/pages/dashboard/project/[name]/budget.astro`
7. Port decisions page: `(app)/project/[name]/decisions/page.tsx` from `site/src/pages/dashboard/project/[name]/decisions.astro`
8. Create loading.tsx files for each sub-page with appropriate skeletons
9. Add Radix Tooltips to heatmap cells (show model, task, accuracy, lift on hover)

**Deliverable:** Full project detail experience with all 4 tabs, interactive charts, and tooltip overlays.

### Phase 7: Real-time & Live Feed (8-10 hours)

**Dependencies:** Phase 5

1. Build `lib/websocket.ts` — WebSocket singleton with reconnection and channel subscription
2. Build `providers/websocket-provider.tsx` — React context wrapping the WS client
3. Build `lib/hooks/use-websocket.ts` and `lib/hooks/use-websocket-invalidation.ts`
4. Mount `WebSocketProvider` in `(app)/layout.tsx`
5. Build live feed components: `event-feed.tsx`, `event-row.tsx`, `filter-bar.tsx`
6. Port live feed page: `(app)/dashboard/live/page.tsx` from `site/src/pages/dashboard/live.astro`
7. Build `components/connection-status.tsx` — indicator in header
8. Add toast notifications for key events (session start/end, eval complete, budget alert)
9. Wire WebSocket events to TanStack Query cache invalidation (so heatmap, budget, etc. update in real-time)

**Deliverable:** Real-time event feed with WebSocket connection that persists across navigations. Dashboard data auto-updates when events arrive.

### Phase 8: Command Palette & Polish (6-10 hours)

**Dependencies:** Phase 7

1. Build `components/command-palette.tsx` using `cmdk` + Radix Dialog
2. Register `cmd+K` shortcut in `(app)` layout
3. Populate command palette with: page navigation, project shortcuts, action items
4. Add Framer Motion micro-interactions: skeleton load-in transitions, card hover effects, stat counter animations
5. Responsive testing: verify sidebar drawer on mobile, grid collapse, touch interactions
6. Performance audit: check bundle size, ensure server components aren't accidentally client-bundled
7. Accessibility pass: keyboard navigation, focus management in dialog/command palette, aria labels
8. Lighthouse run: target 90+ on Performance, Accessibility, Best Practices

**Deliverable:** Polished, production-ready Next.js frontend with command palette, animations, and passing performance/accessibility audits.

---

## Summary

| Phase | Scope | Effort | Dependencies |
|-------|-------|--------|-------------|
| 1 | Scaffolding & Design System | 6-8h | None |
| 2 | UI Primitives | 6-8h | Phase 1 |
| 3 | Data Layer & API Client | 4-6h | Phase 2 |
| 4 | Marketing Pages | 8-10h | Phase 2 |
| 5 | Dashboard Shell & Portfolio | 10-12h | Phase 2, 3 |
| 6 | Project Detail Pages | 12-16h | Phase 5 |
| 7 | Real-time & Live Feed | 8-10h | Phase 5 |
| 8 | Command Palette & Polish | 6-10h | Phase 7 |
| **Total** | | **60-80h** | |

Phases 4 and 5 can run in parallel (marketing pages have no dependency on the data layer if content is hardcoded initially). Phases 6 and 7 can also partially overlap since they touch different page areas.

### Critical Path

```
Phase 1 → Phase 2 → Phase 3 → Phase 5 → Phase 6
                   ↘ Phase 4              ↗
                                Phase 7 → Phase 8
```

### Key Risks

1. **Tailwind CSS 4 + Next.js 15 compatibility.** Tailwind v4 uses a new engine. Ensure the `@theme` directive and `@import "tailwindcss"` syntax work with Next.js's PostCSS pipeline. May need `@tailwindcss/postcss` instead of the classic plugin.

2. **Framer Motion + App Router.** `AnimatePresence` requires careful handling with React Server Components. The `AnimatedLayout` component must be a client component and only wrap the page content slot, not the entire layout tree.

3. **WebSocket in production.** The current WebSocket URL construction (`site/src/pages/dashboard/live.astro`, line 267) handles protocol detection and host resolution. The Next.js version must handle: same-origin development (localhost:3000 proxying to VPS:3001), and production (both behind nginx on the same domain).

4. **Blog content format.** The current blog posts are hardcoded Astro components. Decide whether to keep them as JSX pages (simplest migration) or move to MDX (more flexible for future posts). Recommendation: keep as JSX pages in Phase 4, add MDX support in a future iteration.
