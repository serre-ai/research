# Next.js Pipelines, Logging & Internal Tooling UI

**Date:** 2026-03-19
**Scope:** Pipeline visualization, unified logging, budget dashboard, settings/configuration
**Stack:** Next.js 15 (App Router), React 19, Tailwind CSS, shadcn/ui, Recharts, ReactFlow

---

## Table of Contents

1. [Pipeline Visualization](#1-pipeline-visualization)
2. [Logging System](#2-logging-system)
3. [Budget Dashboard Enhancement](#3-budget-dashboard-enhancement)
4. [Settings & Configuration](#4-settings--configuration)
5. [Component Inventory](#5-component-inventory)
6. [API Endpoints Required](#6-api-endpoints-required)
7. [Implementation Order](#7-implementation-order)

---

## 1. Pipeline Visualization

### 1.1 Project Phase Pipeline (`/projects/[id]/pipeline`)

**Data model.** Each project progresses through ordered phases defined in `status.yaml`. The canonical phase set is: `ideation` → `literature-review` → `framework` → `empirical-evaluation` → `analysis` → `drafting` → `revision` → `paper-finalization` → `submission-prep` → `submitted`. Each phase contains named streams (e.g., `literature_review`, `formal_framework`, `benchmark_design`) with a `status` field (`pending` | `in-progress` | `complete`) and free-text `notes`. The project's `phase` field in `status.yaml` (mirrored in the `projects` DB table) indicates the current active phase.

**Layout.** A horizontal pipeline with phases rendered as connected nodes in a single row, left to right. Use a stepper-like layout, not a freeform graph. Each phase node is a rounded rectangle approximately 140px wide. Connector lines between nodes carry small directional arrows.

**Phase node states:**

| State | Visual treatment |
|-------|-----------------|
| Completed | Solid fill (green-tinted background), checkmark icon in top-right corner, muted border |
| Current | Bold border (accent color), subtle pulse animation on the border (2s cycle, `animate-pulse` is too aggressive — use a custom keyframe that oscillates border-opacity between 0.5 and 1.0), filled background at medium opacity |
| Future | Dashed border, light gray fill, text at 50% opacity |

**Phase node content.** The node shows: (a) phase name in title case, (b) a compact horizontal stacked bar below the name showing stream completion — each stream is a segment of the bar, colored green when complete, amber when in-progress, gray when pending, (c) session count badge in the bottom-right corner (e.g., "4 sessions").

**Stream detail panel.** Clicking a phase node opens a right-side sheet (not a modal — use `Sheet` from shadcn/ui, sliding in from the right, ~400px wide). The sheet contains:

- Phase name as heading.
- One row per stream: stream name, status badge (`complete` / `in-progress` / `pending`), a horizontal progress bar (percentage derived from substatus if available, otherwise binary 0% or 100%), and the `notes` text truncated to 2 lines with a "Show more" toggle.
- A "Sessions" section at the bottom listing all sessions that ran during this phase (fetched from `GET /api/projects/:id/sessions` filtered by phase). Each session row shows: agent type icon, date, duration, cost, commit count, status badge.

**Interaction: session link.** Clicking a session row in the sheet navigates to `/logs/sessions/[sessionId]`.

**Responsive behavior.** On screens narrower than 768px, the pipeline switches to a vertical layout (top to bottom) with phase nodes stacked. The sheet becomes a full-screen overlay.

---

### 1.2 Session DAG (`/projects/[id]/sessions`)

**Data model.** Sessions have: `session_id`, `project`, `agent_type`, `status`, `started_at`, `duration_s`, `cost_usd`, `commits_created`, `error`. Chain relationships are tracked via the daemon's `chainId` field logged in activity events (`session_start` events with `data.chainId` and `data.chainDepth`). External dispatches carry `data.triggeredBy` and `data.dispatchId`. Planner-launched sessions carry `data.briefId` and `data.strategy`.

**Graph rendering.** Use ReactFlow with a custom layout. Nodes are arranged in columns by chain depth (depth 0 on the left, depth 1 next, etc.). Independent chains are stacked vertically with 40px vertical gap. Edges connect predecessor sessions to their successors.

**Node design.** Each node is a card approximately 200px wide and 80px tall, containing:

- **Top row:** Agent type icon (small, 16px) + agent type label + session status badge (right-aligned).
- **Middle row:** Date/time (relative, e.g., "2h ago"), duration (e.g., "23m").
- **Bottom row:** Cost (e.g., "$1.42"), commits (e.g., "3 commits"), strategy tag if planner-launched.

**Node color coding by status:**

| Status | Background | Border |
|--------|-----------|--------|
| `completed` | `bg-green-50` | `border-green-300` |
| `failed` | `bg-red-50` | `border-red-300` |
| `timeout` | `bg-amber-50` | `border-amber-300` |
| `budget_exceeded` | `bg-orange-50` | `border-orange-300` |
| `running` | `bg-blue-50` | `border-blue-300`, animated border (same subtle pulse as the phase pipeline) |

**Agent type color coding.** In addition to the status border, each node has a small colored left-edge accent (4px wide) indicating agent type:

| Agent | Color |
|-------|-------|
| researcher | `blue-500` |
| writer | `purple-500` |
| critic | `amber-600` |
| editor | `teal-500` |
| experimenter | `emerald-500` |
| strategist | `indigo-500` |
| scout | `cyan-500` |
| theorist | `violet-500` |
| engineer | `gray-600` |

**Interaction.** Clicking a node opens a right-side sheet with full session details: the complete session metadata, a mini cost breakdown, list of commits (with commit messages), and a link to the full transcript at `/logs/sessions/[sessionId]`. The sheet also shows the session's brief objective if it was planner-launched (`data.objective` from the activity log).

**Filtering.** Above the graph, provide a horizontal filter bar with:

- Agent type multi-select (checkboxes with agent type labels and color dots).
- Status multi-select.
- Date range picker (defaults to last 7 days).
- A "Show failed only" quick toggle.

**Empty state.** If the project has no sessions, show a centered illustration (a simple line-art diagram placeholder) with text: "No sessions yet. The daemon will launch sessions when this project is active."

**Performance.** ReactFlow handles hundreds of nodes well. For projects with 100+ sessions, paginate by date range and provide a "Load more" button at the bottom that extends the date range backward by 7 days.

---

### 1.3 Eval Pipeline (`/projects/[id]/eval`)

**Data model.** The eval system produces a three-dimensional matrix: model x task x condition. Data comes from `GET /api/projects/:id/eval`, which returns `{ progress, byDifficulty, runs }`. `progress` rows contain `model`, `task`, `condition`, `completed_count`, `correct_count`, `accuracy`, `avg_latency_ms`, `last_updated`. `byDifficulty` adds `difficulty` and per-difficulty accuracy. `runs` contain run-level metadata with status.

The project currently has 12 models (Haiku 4.5, Sonnet 4.6, Opus 4.6, GPT-4o-mini, GPT-4o, o3, Llama 3.1 8B, Llama 3.1 70B, Ministral 8B, Mistral Small 24B, Qwen 2.5 7B, Qwen 2.5 72B), 9 tasks (B1-B9), and 3+ conditions (direct, short_cot, budget_cot, tool_use).

#### 1.3.1 Accuracy Heatmap (default view)

**Layout.** A full-width interactive heatmap table. Rows are models (grouped by family: Anthropic, OpenAI, Meta, Mistral, Qwen). Columns are tasks (B1-B9). Each cell shows the accuracy value for a selected condition.

**Condition selector.** A horizontal tab bar above the heatmap with tabs for each condition: `direct`, `short_cot`, `budget_cot`, `tool_use`. Selecting a tab recolors the entire heatmap. Default: `direct`.

**Cell rendering.** Each cell is a small rectangle (approximately 80px wide, 36px tall) displaying the accuracy as a number (e.g., "0.847"). The cell background is colored on a diverging scale:

- 0.0 - 0.3: deep red (`red-600`)
- 0.3 - 0.5: light red (`red-200`)
- 0.5 - 0.7: amber (`amber-200`)
- 0.7 - 0.85: light green (`green-200`)
- 0.85 - 1.0: deep green (`green-600`, with white text)

Use linear interpolation within each band for smooth gradients. If no data exists for a cell, show a gray background with "---".

**Hover tooltip.** Hovering over a cell shows a tooltip with: model, task, condition, accuracy (4 decimal places), instance count, average latency, last updated timestamp.

**Cell click → drill-down.** Clicking a cell navigates to a detail view (described in 1.3.2).

**Row headers.** Each model row starts with the model name. Family grouping is indicated by a subtle left-border color (one color per family) and a family label that spans the group (using a `rowspan`-like sticky header). Model rows within a family are sorted by parameter count (ascending).

**Column headers.** Each task column header shows the task ID (B1-B9) and, on hover, the full task name (e.g., "B1: Masked Majority").

**CoT Lift overlay.** A toggle switch labeled "Show CoT Lift" above the heatmap. When enabled, each cell shows the difference between `short_cot` accuracy and `direct` accuracy for that model/task combination instead of the raw accuracy. Positive values are green, negative values are red. The condition tab bar is hidden when this overlay is active.

**Summary row.** Below the model rows, add a "Mean" row showing the average accuracy across all models for each task. Similarly, add a "Mean" column on the right showing the average accuracy across all tasks for each model.

#### 1.3.2 Cell Drill-Down (`/projects/[id]/eval/[model]/[task]/[condition]`)

When a heatmap cell is clicked, navigate to a detail page (or open a full-screen modal) showing instance-level data for that model/task/condition combination.

**Header.** Show model name, task name, condition, overall accuracy (large, prominent), and instance count.

**Difficulty distribution chart.** A bar chart (Recharts `BarChart`) showing accuracy on the y-axis and difficulty level on the x-axis. Each bar is colored using the same diverging scale as the heatmap. The bar height represents accuracy at that difficulty level. Above each bar, show the instance count as a small label.

**Instance table.** Below the chart, a paginated table (20 rows per page) showing individual eval instances. Columns:

| Column | Content |
|--------|---------|
| Instance ID | e.g., `B1_masked_majority_d3_0042` |
| Difficulty | Integer |
| Correct | Green checkmark or red X |
| Ground Truth | The expected answer |
| Extracted Answer | The model's parsed answer |
| Latency | Milliseconds |
| Response | Truncated to 100 chars, with "Expand" button to show full response in a modal |

The table supports sorting by any column (click column header to toggle asc/desc). Add a filter row below the headers with: a difficulty dropdown, a correct/incorrect toggle, and a text search on Instance ID.

**Back navigation.** A breadcrumb at the top: `Eval` > `[Model]` > `[Task]` > `[Condition]`.

#### 1.3.3 Progress Tracking (running evaluations)

**When eval jobs are active.** `GET /api/eval/status` returns `{ running, queued, completed, failed, total, runningJobs, queuedJobs }`. If `running > 0`, show a progress banner at the top of the eval page.

**Progress banner.** A horizontal bar showing:
- "N running, M queued" text on the left.
- A progress bar showing `completed_count / total_expected` for the currently running job.
- Model, task, condition labels for each running job.
- Estimated time remaining (computed from `avg_latency_ms * remaining_instances`).

**Real-time updates.** Subscribe to the WebSocket channel `eval-progress`. On receiving `job_queued`, `job_started`, `job_completed`, or `job_cancelled` events, update the banner and heatmap without full page reload. Use a React context provider (`EvalProgressProvider`) wrapping the eval pages to manage WebSocket state.

**Run history panel.** Below the heatmap, an expandable section "Recent Runs" showing the last 20 eval runs from the `runs` array. Each run row shows: run_id, model, task, condition, status badge, started_at (relative time), completed_at, accuracy (if completed), instance count. Failed runs have a red status badge and show error details on expansion.

#### 1.3.4 Comparison View

**Layout.** A split-screen view accessible via a "Compare" button on the eval page. The left panel shows one condition (defaulting to `direct`), the right panel shows another (defaulting to `short_cot`). Both panels display the same heatmap layout, scrolled in sync.

**Delta column.** Between the two heatmaps, a narrow column shows the per-cell delta (right minus left) with color coding: green for positive deltas (CoT/tool helped), red for negative deltas (CoT/tool hurt).

**Condition selectors.** Each panel has its own condition dropdown. The comparison is purely visual — no additional API calls needed since all condition data is already fetched.

---

### 1.4 Paper Build Pipeline (`/projects/[id]/paper`)

**Data model.** `GET /api/paper/status` returns `{ status, lastBuild: { buildId, status, startedAt, finishedAt, durationMs } }`. `POST /api/paper/build` triggers a build. `GET /api/paper/log` returns the last build log as plain text. `GET /api/paper/pdf` serves the PDF. `GET /api/paper/download` serves submission.zip.

The build script (`build-paper.sh`) runs three sequential steps: (1) `analyze.py` — regenerate tables and figures from eval data, (2) `tectonic main.tex` — compile LaTeX to PDF, (3) package submission.zip.

#### 1.4.1 Build Status Display

**Layout.** A vertical step indicator (like GitHub Actions) showing the three build stages:

| Step | Label | Icon |
|------|-------|------|
| 1 | Analyze | Chart icon |
| 2 | Compile | File icon |
| 3 | Package | Package icon |

Each step is a horizontal row with: step number in a circle, label, status indicator (spinner when running, checkmark when done, X when failed), and duration when completed.

**Step states:**

| State | Circle | Duration | Detail |
|-------|--------|----------|--------|
| Pending | Gray outline, gray number | — | — |
| Running | Blue fill, white number, spinner overlay | Elapsed timer (live) | Spinner animation |
| Done | Green fill, white checkmark | "12s" | — |
| Error | Red fill, white X | "8s" | Error message below in red text |

The steps are connected by a vertical line on the left side. The line is solid and green up to the current step, dashed and gray after.

**Note on step detection.** The current API does not distinguish between build steps — it reports a single build status. To render per-step status, parse the build log in the frontend: look for markers like `[analyze]`, `[compile]`, `[package]` in the log output. If the log contains `[analyze] done`, mark step 1 as complete. This is a heuristic; the build script should be updated to emit structured markers (see Section 6, new endpoints).

#### 1.4.2 Build Trigger

**Trigger button.** A primary action button labeled "Build Paper" in the top-right corner of the paper page. When a build is in progress, the button changes to a disabled state with a spinner and text "Building...".

**Build options.** Clicking a dropdown chevron next to the button reveals two checkboxes:
- "Skip analysis" — sends `{ skipAnalysis: true }` to the API. Useful when only the LaTeX has changed.
- "Skip compile" — sends `{ skipCompile: true }`. Useful when only regenerating analysis outputs.

**Confirmation.** No confirmation dialog needed — builds are non-destructive (they overwrite outputs but do not modify source files).

#### 1.4.3 PDF Preview

Below the step indicator, an inline PDF viewer using `react-pdf` (based on PDF.js). The viewer renders the compiled PDF from `GET /api/paper/pdf` with:

- Page navigation (previous/next buttons + page number input).
- Zoom controls (fit width, fit page, manual percentage).
- A download button linking to `GET /api/paper/download` (submission.zip).

**Fallback.** If no PDF exists yet (404 from the API), show a gray placeholder with text: "No PDF available. Run a build to generate it."

**Auto-refresh.** After a build completes successfully, automatically reload the PDF preview by re-fetching from the API. Use the build status polling (or WebSocket events once the paper build is wired into the event bus) to detect build completion.

#### 1.4.4 Build Log Viewer

Below the PDF preview, a collapsible section "Build Log" that shows the raw build output from `GET /api/paper/log`. Rendered using a terminal-style component (described in Section 2.3).

**During active builds.** Poll `GET /api/paper/log` every 2 seconds and append new content. The terminal auto-scrolls to the bottom. Show a "Building..." indicator at the top of the log section.

#### 1.4.5 Build History

**Note.** The current API only tracks the last build in memory. To support build history, a new persistence layer is needed (see Section 6). Until then, show only the current/last build status. Once history is available, render a table below the build log:

| Column | Content |
|--------|---------|
| Build ID | Short UUID |
| Status | Badge: `done` / `error` |
| Started | Relative time |
| Duration | e.g., "45s" |
| Triggered By | "manual" or "daemon" |
| Actions | "View Log" link |

---

## 2. Logging System

### 2.1 Unified Log Viewer (`/logs`)

**Data sources.** The platform produces several log types, each stored differently:

| Log Type | Storage | API |
|----------|---------|-----|
| Activity events | `.logs/activity.jsonl` | `GET /api/activity/recent` |
| Session transcripts | `.sessions/<project>/<month>/<sessionId>.jsonl` | New endpoint needed |
| Build logs | In-memory (paper routes) | `GET /api/paper/log` |
| Budget events | DB `budget_events` table | `GET /api/budget` (aggregated) |
| Domain events | DB `domain_events` table | `GET /api/events` |
| Spending records | `.logs/spending.jsonl` | No direct endpoint |

#### 2.1.1 Search Interface

**Layout.** A full-width page with a search bar at the top and a filterable log stream below.

**Search bar.** A single text input, full-width, with a search icon on the left and a clear button on the right. Placeholder text: "Search across all logs...". The search queries the `GET /api/activity/recent` endpoint (and future full-text search endpoint) with debounced input (300ms delay).

**Filter bar.** Below the search bar, a horizontal row of filter controls:

| Filter | Control | Values |
|--------|---------|--------|
| Log Type | Multi-select dropdown | Activity, Session Transcript, Build, Budget, Domain Event |
| Project | Dropdown | All projects from `GET /api/projects` |
| Date Range | Date range picker | Presets: Today, Last 7 days, Last 30 days, Custom |
| Severity | Multi-select dropdown | Info, Warning, Error |
| Agent Type | Multi-select dropdown | All agent types |

**Active filters.** Show active filters as dismissible chips below the filter bar. Clicking a chip removes that filter.

#### 2.1.2 Log Stream

**Layout.** A virtual-scrolled list (use `@tanstack/react-virtual` or `react-window`) of log entries. Each entry is a row with:

- **Timestamp column** (120px, fixed): Relative time (e.g., "2m ago"), full ISO timestamp on hover.
- **Type column** (100px, fixed): Colored badge indicating log type. Color mapping:
  - `session_start` / `session_end` / `session_error`: blue
  - `budget_spend` / `budget_alert`: amber
  - `eval_*`: purple
  - `daemon_*`: gray
  - `commit` / `push` / `pr_*`: green
  - `decision_*`: indigo
  - `phase_transition`: teal
  - `verification_completed`: emerald
  - `knowledge_*`: violet
- **Project column** (120px, fixed): Project name, or "platform" for non-project events.
- **Agent column** (100px, fixed): Agent type with color dot (matching the session DAG color scheme), or "—" if not agent-specific.
- **Message column** (remaining width): A single-line summary derived from the event data. For example, a `session_end` event shows "Completed in 23m, $1.42, 3 commits". A `budget_spend` event shows "$0.87 — claude-sonnet-4-6 (reasoning-gaps)". An `eval_job_completed` event shows "claude-sonnet-4-6 / B1 / direct — 84.7% (500 instances)".

**Row expansion.** Clicking a row expands it inline to show the full JSON payload in a formatted code block (use a monospace font, syntax-highlighted JSON). The expanded view also shows a "View full log" link that navigates to the appropriate detail viewer (e.g., `/logs/sessions/[id]` for session events).

**Pagination.** Load 50 entries at a time. Scrolling to the bottom loads the next 50 (infinite scroll). The API's `count` and `offset` (via tail behavior) parameters support this pattern.

**Real-time mode.** A toggle switch in the top-right corner labeled "Live". When enabled, subscribe to the WebSocket `logs` channel and prepend new events to the top of the list with a brief highlight animation (a yellow flash that fades over 1 second). Show a small indicator dot pulsing next to the "Live" label.

#### 2.1.3 Log Type-Specific Views

Each log type in the filter dropdown links to a dedicated sub-page:

- `/logs/sessions` — Session transcript browser
- `/logs/builds` — Build log browser
- `/logs/budget` — Budget event log
- `/logs/events` — Domain event explorer

These are convenience views that pre-set the log type filter and may offer additional type-specific UI (e.g., the session transcript viewer described below).

---

### 2.2 Session Transcript Viewer (`/logs/sessions/[id]`)

**Data model.** Session transcripts are stored as JSONL files at `.sessions/<project>/<month>/<sessionId>.jsonl`. Each line is a JSON object with at minimum a `t` (timestamp) field and a `type` field from the Claude Agent SDK stream. Message types include `assistant` (model responses), `user` (tool results), `result` (final session result), and `stream_event` (filtered out during write).

**Note on data access.** Transcripts are stored on the filesystem, not in the database. A new API endpoint is needed to serve transcript content (see Section 6).

#### 2.2.1 Conversation Renderer

**Layout.** A full-page conversation view similar to a chat interface, but optimized for dense technical content.

**Message layout.** Messages are rendered as full-width blocks (no chat bubbles) with clear visual separation:

- **Assistant messages:** White background, left-aligned. Show the full text content rendered as Markdown (use `react-markdown` with syntax highlighting via `rehype-highlight`). Long messages have a max-height of 600px with a "Show full message" toggle that removes the height constraint.
- **Tool call blocks:** Indented slightly (left margin 24px), with a colored left border (4px, blue). Show the tool name as a bold header (e.g., "Bash", "Read", "Edit"), followed by the tool input in a collapsible code block. Default state: collapsed, showing only the first line. The tool result appears below the input, also collapsible, defaulting to collapsed. If the tool result is an error, the left border turns red.
- **Result messages:** A horizontal divider followed by a summary card showing: status, turns used, tokens used (input/output), cost, duration, commits created. Use a grid layout with labeled values.

**Annotations per message:**

- **Turn number.** A small gray label in the top-right corner of each message block: "Turn 1", "Turn 2", etc.
- **Token count.** Next to the turn number, show estimated token count for that message. If token usage data is available at the message level, use it; otherwise, estimate from character count (divide by 4 as a rough heuristic).
- **Cost annotation.** If per-message cost data is available, show it next to the token count. Otherwise, omit.
- **Timestamp.** Each message block shows the relative time since session start (e.g., "+2m 34s") in the top-left corner.

#### 2.2.2 Navigation

**Jump to turn.** A small input field in the top toolbar: "Go to turn #___". Entering a number scrolls to that turn.

**Turn list sidebar.** A narrow sidebar (240px, collapsible) on the left showing a sequential list of turns. Each turn is a small row showing: turn number, type (assistant/tool), and a 1-line preview (first 60 characters of the assistant text, or tool name for tool calls). Clicking a turn scrolls the main content to it. The current visible turn is highlighted in the sidebar.

**Search within transcript.** A search input in the top toolbar. Matches are highlighted in the transcript with yellow background. Arrow buttons navigate between matches. Show match count: "3 of 12 matches".

#### 2.2.3 Session Metadata Header

Above the conversation, a compact header bar showing:

- Project name (linked to project page).
- Agent type with color dot.
- Status badge.
- Duration (e.g., "23m 14s").
- Cost (e.g., "$1.42").
- Turns used (e.g., "34 turns").
- Tokens (e.g., "45.2K in / 12.8K out").
- Commits created (e.g., "3 commits", linked to commit list).
- Strategy tag if planner-launched.
- A "Previous Session" / "Next Session" navigation for the same project.

---

### 2.3 Build Log Viewer (`/logs/builds/[id]`)

**Rendering.** Use a terminal-style component with:

- Black background (`bg-gray-950`), monospace font (IBM Plex Mono or the system monospace stack).
- ANSI color support. Parse ANSI escape codes and render them as inline styles. Use the `ansi-to-html` npm package (or a lighter alternative like `anser`) to convert ANSI sequences to HTML spans with color classes.
- Line numbers in a gutter on the left (gray, non-selectable using `user-select: none`).
- Word wrap disabled by default, with a toggle to enable it.

**Auto-scroll.** During active builds (detected by polling `GET /api/paper/status` every 2 seconds), the terminal auto-scrolls to the bottom. A "Follow output" toggle controls this behavior. If the user manually scrolls up, auto-scroll disengages. A floating button "Jump to bottom" appears when the user is not at the bottom.

**Error highlighting.** Lines containing `error`, `Error`, `ERROR`, or `fatal` are highlighted with a red left-border (4px) and a subtle red background tint (`bg-red-950` at 20% opacity). Lines containing `warning` or `Warning` get an amber treatment.

**Search.** A search input in the terminal toolbar. Matches are highlighted with a yellow background. Forward/backward navigation buttons.

**Copy.** A "Copy all" button in the toolbar that copies the raw log text (without ANSI codes) to the clipboard.

---

## 3. Budget Dashboard Enhancement

### 3.1 Budget Overview (`/budget`)

**Data source.** `GET /api/budget` returns: `{ monthly, byProvider, byProject, byModel, burnRate, reconciliation, limits }`.

#### 3.1.1 Summary Cards

**Layout.** A row of four summary cards at the top of the page:

| Card | Content | Visual |
|------|---------|--------|
| Monthly Spend | `$X / $1,000` with progress bar | Bar turns amber at 80%, red at 95% |
| Daily Spend | `$X / $40` with progress bar | Same color thresholds |
| Burn Rate | `$X.XX/day (7-day avg)` | Trend arrow (up/down vs. previous period) |
| Projected Month End | `$X` with "On track" / "Over budget" label | Green if under limit, red if over |

Each card is a `Card` component from shadcn/ui, approximately 25% width on desktop, full-width stacked on mobile.

**Alert banner.** If `alertLevel` is `warning`, `critical`, or `exceeded`, show a banner above the cards:
- `warning`: Amber banner — "Budget warning: approaching daily/monthly limit."
- `critical`: Red banner — "Budget critical: 95%+ of limit consumed."
- `exceeded`: Red banner with bold text — "Budget exceeded. Daemon will not launch new sessions."

#### 3.1.2 Monthly Burn Chart

**Chart.** A Recharts `AreaChart` spanning the full width below the summary cards. X-axis: days of the current month. Y-axis: cumulative spending in USD.

**Data series:**
- **Actual spend:** A filled area chart (blue, 20% opacity fill) showing cumulative daily spending. Each day's point is the sum of all spending up to that day.
- **Budget limit line:** A horizontal dashed line at $1,000 (monthly limit).
- **Projected trajectory:** A dashed line extending from the current day to month end, using the 7-day average burn rate as the slope. If the trajectory crosses the budget limit line, the projected area above the limit is shaded red.

**Tooltip.** Hovering over a day shows: date, daily spend, cumulative spend, daily average.

**Time range selector.** Tabs above the chart: "This Month" (default), "Last 30 Days", "Last 90 Days". The "Last 90 Days" view shows monthly bars instead of daily.

#### 3.1.3 Provider Breakdown

**Layout.** Two visualizations side by side (50% width each on desktop, stacked on mobile):

**Pie chart (left).** A Recharts `PieChart` showing spending by provider. Each provider gets a distinct color:
- Anthropic: `blue-500`
- OpenAI: `green-500`
- OpenRouter: `purple-500`
- Claude Code Max: `indigo-500`
- Hetzner: `gray-500`
- Firecrawl: `orange-500`

The pie chart shows the provider name and dollar amount in the legend. Hovering over a segment shows the percentage and exact amount.

**Provider table (right).** A table listing all providers with columns:

| Column | Content |
|--------|---------|
| Provider | Display name with color dot |
| Type | `api_variable` / `subscription` / `infrastructure` badge |
| This Month | Dollar amount |
| % of Total | Percentage |

Sort by "This Month" descending.

#### 3.1.4 Model-Level Cost Tracking

**Layout.** A horizontal bar chart (Recharts `BarChart`) showing spending per model. Models on the y-axis, cost on the x-axis. Bars are colored by provider (same provider colors as the pie chart). Top 10 models shown by default, with a "Show all" toggle.

#### 3.1.5 Per-Project Spending

**Layout.** A stacked bar chart showing spending by project over time, or a simple table:

| Column | Content |
|--------|---------|
| Project | Project name (linked to project page) |
| This Month | Dollar amount |
| Events | Number of budget events |
| Avg per Session | Dollar amount (total / session count) |

#### 3.1.6 Session Cost History

**Layout.** A scatter plot (Recharts `ScatterChart`) with sessions as dots. X-axis: date/time. Y-axis: cost per session. Dot size proportional to duration. Dot color by agent type (same color scheme as session DAG). Hovering over a dot shows: session ID, project, agent type, cost, duration, turns. Clicking navigates to the session transcript.

---

## 4. Settings & Configuration

### 4.1 Settings Page (`/settings`)

**Layout.** A left sidebar navigation with sections, content area on the right. The sidebar lists: General, Daemon, API Keys, Projects, Agents.

#### 4.1.1 General Settings

- **Platform name:** Text input (read-only display of "Deepwork").
- **API endpoint:** Display the current API URL (e.g., `http://89.167.5.50:3001`).
- **Database status:** Connected/disconnected indicator with connection details (host, database name).
- **Server health:** Pull from `GET /api/health` and display uptime, memory usage, CPU count, database status, knowledge graph stats.

#### 4.1.2 Daemon Configuration

**Data source.** `GET /api/daemon/health` returns daemon state including config. Currently, daemon config is set via environment variables and constructor arguments. Changing config requires a daemon restart.

**Display (read-only initially):**

| Setting | Current Value | Description |
|---------|--------------|-------------|
| Poll Interval | 30 min | How often the daemon checks for work |
| Max Concurrent Sessions | 2 | Maximum parallel sessions |
| Daily Budget Limit | $40 | Per-day spending cap |
| Monthly Budget Limit | $1,000 | Per-month spending cap |
| Max Chain Depth | 3 | Maximum session chain depth |
| Max Dispatches/Hour | 5 | Rate limit per agent per hour |
| Max Dispatches/Day | 10 | Rate limit total per day |
| Research Planner | Enabled/Disabled | USE_RESEARCH_PLANNER flag |

**Future: editable config.** Once the daemon supports hot-reload of configuration (via a `PATCH /api/daemon/config` endpoint), these fields become editable inputs with a "Save" button. Until then, show them as read-only with a note: "Configuration is set via environment variables. Restart the daemon to apply changes."

**Daemon controls:**
- **Status indicator:** Green dot + "Running" or red dot + "Stopped".
- **Uptime:** e.g., "3d 14h 22m".
- **Cycles completed:** e.g., "142".
- **Active sessions:** Count and list.
- **Restart button** (future): Triggers daemon restart via API. Not implemented yet — show as disabled with tooltip "Coming soon".

#### 4.1.3 API Key Management

**Display.**
- **Deepwork API Key:** Show first 8 and last 4 characters, masked in between. A "Copy" button. A "Regenerate" button (disabled until backend support exists).
- **Provider API Keys:** A table showing configured providers:

| Provider | Status | Key (masked) |
|----------|--------|-------------|
| Anthropic | Active | `sk-ant-...7f3a` |
| OpenAI | Active | `sk-proj-...x2b1` |
| OpenRouter | Active | `sk-or-...9c4d` |

Status is inferred from whether the key environment variable is set (the API could expose this via a new endpoint, or the frontend checks against provider list from `GET /api/budget/providers`).

**Security note.** API keys should never be transmitted in full from the server. The settings page only displays masked versions. Key rotation and management are handled server-side.

#### 4.1.4 Project Management

**Project list.** A table of all projects from `GET /api/projects`:

| Column | Content |
|--------|---------|
| Name | Project name (linked to project page) |
| Title | Full title |
| Venue | e.g., "NeurIPS 2026" |
| Phase | Current phase badge |
| Status | `active` / `paused` / `review` / `completed` badge |
| Branch | Git branch name |
| Updated | Relative time |

**Actions per project:**
- "Pause" / "Resume" button — calls `PATCH /api/projects/:id/status` with `{ status: "paused" }` or `{ status: "active" }`.
- "View" link — navigates to `/projects/[id]`.

**Create project button (future).** A "New Project" button that opens a form: name, title, venue, branch. This requires a backend endpoint to scaffold a new project directory. Show as disabled until implemented.

#### 4.1.5 Agent Configuration Viewer

**Layout.** A list of all agent types with their configuration. Data comes from reading the `.claude/agents/*.md` files (requires a new API endpoint, or embed agent definitions at build time).

Each agent type is a collapsible card showing:
- Agent type name with color dot.
- Phase mapping: which phases this agent is assigned to (from `PHASE_TO_AGENT`).
- Knowledge injection limit (from `KNOWLEDGE_LIMITS`).
- Role description (from the agent .md file).

This section is purely informational — agent configurations are changed by editing the .md files directly.

---

## 5. Component Inventory

### Layout Components

| Component | Description | Used In |
|-----------|-------------|---------|
| `AppShell` | Main layout with sidebar nav, header, content area | All pages |
| `PageHeader` | Page title, breadcrumbs, action buttons | All pages |
| `SideSheet` | Right-side sliding panel (wraps shadcn `Sheet`) | Phase pipeline, session DAG |
| `FilterBar` | Horizontal row of filter controls with active filter chips | Logs, eval, sessions |
| `EmptyState` | Centered placeholder with icon and message | Session DAG, logs, builds |

### Pipeline Components

| Component | Description | Used In |
|-----------|-------------|---------|
| `PhasePipeline` | Horizontal stepper showing project phases | Pipeline page |
| `PhaseNode` | Individual phase node with stream completion bar | PhasePipeline |
| `StreamList` | List of streams within a phase with progress bars | Phase detail sheet |
| `SessionDAG` | ReactFlow graph of sessions with chain relationships | Sessions page |
| `SessionNode` | Custom ReactFlow node for a session | SessionDAG |
| `SessionDetailSheet` | Sheet showing full session metadata | SessionDAG click |
| `BuildPipeline` | Vertical step indicator for paper build stages | Paper page |
| `BuildStep` | Individual build step with status and duration | BuildPipeline |

### Eval Components

| Component | Description | Used In |
|-----------|-------------|---------|
| `AccuracyHeatmap` | Model x Task matrix with colored cells | Eval page |
| `HeatmapCell` | Individual cell with accuracy value and color | AccuracyHeatmap |
| `HeatmapLegend` | Color scale legend for accuracy values | AccuracyHeatmap |
| `ConditionTabs` | Tab bar for switching between conditions | Eval page |
| `CoTLiftToggle` | Toggle switch for CoT lift overlay | Eval page |
| `DifficultyChart` | Bar chart of accuracy by difficulty | Cell drill-down |
| `InstanceTable` | Paginated table of eval instances | Cell drill-down |
| `EvalProgressBanner` | Real-time progress bar for running evals | Eval page |
| `RunHistoryTable` | Table of recent eval runs | Eval page |
| `ComparisonView` | Split-screen condition comparison | Eval page |

### Log Components

| Component | Description | Used In |
|-----------|-------------|---------|
| `LogStream` | Virtual-scrolled list of log entries | Unified log viewer |
| `LogEntry` | Single log entry row with expansion | LogStream |
| `LogEntryDetail` | Expanded JSON payload view | LogEntry |
| `LiveToggle` | Toggle for real-time WebSocket updates | Log viewer |
| `TranscriptViewer` | Full conversation renderer for session transcripts | Session transcript page |
| `TranscriptMessage` | Single assistant/tool message block | TranscriptViewer |
| `ToolCallBlock` | Collapsible tool call with input/output | TranscriptMessage |
| `TurnSidebar` | Navigable list of turns | TranscriptViewer |
| `TerminalOutput` | ANSI-aware terminal-style log renderer | Build log viewer, paper page |
| `TranscriptSearch` | Search within transcript with match navigation | TranscriptViewer |

### Budget Components

| Component | Description | Used In |
|-----------|-------------|---------|
| `BudgetSummaryCards` | Row of summary cards (monthly, daily, burn rate, projection) | Budget page |
| `BurnChart` | Area chart of cumulative spending over time | Budget page |
| `ProviderPieChart` | Pie chart of spending by provider | Budget page |
| `ProviderTable` | Table of providers with spending | Budget page |
| `ModelCostChart` | Horizontal bar chart of spending by model | Budget page |
| `ProjectSpendTable` | Table of per-project spending | Budget page |
| `SessionCostScatter` | Scatter plot of session costs over time | Budget page |
| `BudgetAlertBanner` | Warning/critical/exceeded banner | Budget page |

### Settings Components

| Component | Description | Used In |
|-----------|-------------|---------|
| `SettingsNav` | Left sidebar navigation for settings sections | Settings page |
| `DaemonStatusCard` | Daemon status, uptime, controls | Settings page |
| `ConfigTable` | Read-only (or editable) table of configuration values | Settings page |
| `ApiKeyRow` | Masked API key display with copy button | Settings page |
| `ProjectTable` | Table of projects with status controls | Settings page |
| `AgentCard` | Collapsible card showing agent type configuration | Settings page |

### Shared / Utility Components

| Component | Description | Used In |
|-----------|-------------|---------|
| `StatusBadge` | Colored badge for status values | Everywhere |
| `AgentTypeDot` | Small colored dot for agent type | Sessions, logs |
| `RelativeTime` | Displays relative time with full timestamp tooltip | Everywhere |
| `CostDisplay` | Formatted dollar amount | Sessions, budget, logs |
| `ProgressBar` | Horizontal progress bar with percentage | Phase pipeline, eval, budget |
| `JsonViewer` | Syntax-highlighted JSON viewer | Log detail, settings |
| `DateRangePicker` | Date range picker with presets | Logs, budget, eval |
| `WebSocketProvider` | React context for WebSocket connection management | App-level |
| `EvalProgressProvider` | React context for eval progress state | Eval pages |
| `SearchInput` | Debounced search input with clear button | Logs, transcripts |
| `VirtualList` | Virtual-scrolled list wrapper | Logs |
| `Breadcrumbs` | Breadcrumb navigation | Eval drill-down, logs |
| `PdfViewer` | PDF.js-based inline PDF viewer | Paper page |

**Total unique components: 52**

---

## 6. API Endpoints Required

### Existing Endpoints (sufficient as-is)

| Feature | Endpoint | Method | Notes |
|---------|----------|--------|-------|
| Project list | `/api/projects` | GET | Returns all projects |
| Project eval data | `/api/projects/:id/eval` | GET | Returns progress, byDifficulty, runs |
| Project sessions | `/api/projects/:id/sessions` | GET | Paginated session list |
| Project decisions | `/api/projects/:id/decisions` | GET | Decision log |
| Project status update | `/api/projects/:id/status` | PATCH | Update phase, status, etc. |
| Budget overview | `/api/budget` | GET | Full budget summary with breakdowns |
| Budget providers | `/api/budget/providers` | GET | Provider list |
| Manual budget entry | `/api/budget/manual` | POST | Record manual cost |
| Eval jobs list | `/api/eval/jobs` | GET | List eval jobs |
| Eval job create | `/api/eval/jobs` | POST | Enqueue new eval job |
| Eval job cancel | `/api/eval/jobs/:id` | DELETE | Cancel a job |
| Eval status | `/api/eval/status` | GET | Running/queued/completed summary |
| Paper build trigger | `/api/paper/build` | POST | Start a build |
| Paper status | `/api/paper/status` | GET | Current build status |
| Paper PDF | `/api/paper/pdf` | GET | Serve compiled PDF |
| Paper download | `/api/paper/download` | GET | Serve submission.zip |
| Paper log | `/api/paper/log` | GET | Last build log (plain text) |
| Activity log | `/api/activity/recent` | GET | Recent activity events |
| Domain events | `/api/events` | GET | Recent domain events |
| Dead letters | `/api/events/dead-letters` | GET | Unresolved dead letters |
| Retry dead letter | `/api/events/dead-letters/:id/retry` | POST | Retry failed handler |
| Daemon health | `/api/daemon/health` | GET | Full daemon state |
| Planner status | `/api/planner/status` | GET | Planner state |
| Planner insights | `/api/planner/insights/:project` | GET | Project knowledge insight |
| Session dispatch | `/api/sessions/dispatch` | POST | Queue external session |
| Dispatch queue | `/api/sessions/dispatch/queue` | GET | View dispatch queue |
| Backlog list | `/api/backlog` | GET | List backlog tickets |
| Health check | `/api/health` | GET | Server health (public) |
| WebSocket | `/api/ws` | WS | Real-time channel subscriptions |

### New Endpoints Needed

#### 1. `GET /api/sessions/:id/transcript` — Session transcript content

**Purpose:** Serve session transcript JSONL content for the transcript viewer.

**Implementation:** Read the `.sessions/<project>/<month>/<sessionId>.jsonl` file from disk, parse each line, return as a JSON array. Look up the session in the `sessions` DB table to find the project name, then scan `.sessions/<project>/` directories for the matching file.

**Query params:**
- `offset` (int): Skip first N messages. Default: 0.
- `limit` (int): Return at most N messages. Default: 500.
- `turn` (int): Jump to a specific turn number.

**Response:** `{ sessionId, project, agentType, messages: [...], totalMessages, hasMore }`

**Notes:** Transcript files can be large (up to 50MB per the `TranscriptWriter` cap). Pagination is essential. Consider streaming the response for very large transcripts.

#### 2. `GET /api/sessions/:id` — Single session metadata

**Purpose:** Fetch full metadata for a single session.

**Implementation:** Query the `sessions` table by `session_id`. Include related activity events (from `activity.jsonl` or `domain_events`) to get chain/brief metadata.

**Response:** `{ session_id, project, agent_type, model, tokens_used, cost_usd, commits_created, status, error, started_at, duration_s, brief_id?, strategy?, chain_depth?, triggered_by? }`

#### 3. `GET /api/projects/:id/eval/instances` — Eval instance detail

**Purpose:** Fetch individual eval instances for the cell drill-down view.

**Query params:**
- `model` (string, required)
- `task` (string, required)
- `condition` (string, required)
- `difficulty` (int, optional): Filter by difficulty level.
- `correct` (boolean, optional): Filter by correctness.
- `offset` (int): Default 0.
- `limit` (int): Default 20.
- `sort` (string): Column to sort by. Default: `instance_id`.
- `order` (string): `asc` or `desc`. Default: `asc`.

**Implementation:** Query `eval_results` with the given filters. For the response field, truncate to 200 characters unless `full_response=true` is passed.

**Response:** `{ instances: [...], total, offset, limit }`

#### 4. `GET /api/paper/builds` — Paper build history

**Purpose:** List past builds for the build history table.

**Implementation:** Currently, only the last build is tracked in memory. This endpoint requires persisting build records. Options:
- Store build records in a JSON file (`.logs/paper-builds.json`).
- Add a `paper_builds` table to the DB.

Recommend the DB approach for consistency. Schema:

```sql
CREATE TABLE paper_builds (
    build_id    TEXT PRIMARY KEY,
    status      TEXT NOT NULL CHECK (status IN ('building', 'done', 'error')),
    started_at  TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    duration_ms INTEGER,
    log         TEXT,
    triggered_by TEXT DEFAULT 'manual',
    skip_analysis BOOLEAN DEFAULT FALSE,
    skip_compile BOOLEAN DEFAULT FALSE
);
```

**Response:** `{ builds: [...] }`

#### 5. `GET /api/projects/:id/phases` — Structured phase data

**Purpose:** Return phase and stream data in a structured format for the pipeline visualization.

**Implementation:** Parse the project's `status.yaml` and return structured phase data:

```json
{
  "currentPhase": "submission-prep",
  "phases": [
    {
      "name": "literature-review",
      "status": "complete",
      "streams": [
        {
          "name": "literature_review",
          "status": "complete",
          "notes": "..."
        }
      ],
      "sessionCount": 4
    }
  ]
}
```

The `sessionCount` per phase requires mapping sessions to phases. Since sessions do not currently record which phase they ran in, this requires either: (a) adding a `phase` column to the `sessions` table and recording it at session start, (b) inferring phase from the session date and the project's phase transition dates, or (c) using the `data.phase` field from `session_start` activity events.

Option (c) is most practical since the daemon already logs `data.phase` in legacy-path session starts. Planner-path sessions could be augmented to log phase as well.

#### 6. `GET /api/daemon/config` — Current daemon configuration

**Purpose:** Return the current daemon configuration values for the settings page.

**Implementation:** Expose the `DaemonConfig` object from the daemon instance. Also include environment-derived settings like `USE_RESEARCH_PLANNER`, `MAX_CHAIN_DEPTH`, etc.

**Response:**
```json
{
  "pollIntervalMs": 1800000,
  "maxConcurrentSessions": 2,
  "dailyBudgetUsd": 40,
  "monthlyBudgetUsd": 1000,
  "maxChainDepth": 3,
  "maxDispatchesPerHour": 5,
  "maxDispatchesPerDay": 10,
  "researchPlannerEnabled": true
}
```

#### 7. `GET /api/budget/daily-history` — Daily spending history

**Purpose:** Return daily spending for the burn chart, extended beyond the 7-day window currently embedded in the budget endpoint.

**Query params:**
- `days` (int): Number of days to look back. Default: 30. Max: 365.

**Implementation:** Query `budget_events` grouped by day.

**Response:** `{ days: [{ day: "2026-03-19", total: 12.34, byProvider: {...}, byProject: {...} }, ...] }`

**Note:** The existing `GET /api/budget` already returns `burnRate.daily_history` for 7 days. This new endpoint extends it with more history and richer per-day breakdowns.

#### 8. `GET /api/agents` — Agent type definitions

**Purpose:** Return agent type configurations for the settings page.

**Implementation:** Read `.claude/agents/*.md` files, parse frontmatter if any, and return structured data.

**Response:** `{ agents: [{ type: "researcher", phases: ["research", "literature-review"], knowledgeLimit: 15, description: "..." }, ...] }`

---

### WebSocket Channel Additions

The existing WebSocket (`/api/ws`) supports channel subscriptions. Currently available channels: `eval-progress`, `logs`, `events`.

**Additions needed:**

| Channel | Events | Used By |
|---------|--------|---------|
| `paper-build` | `build_started`, `build_step`, `build_completed`, `build_error` | Paper page real-time updates |
| `sessions` | `session_started`, `session_completed`, `session_failed` | Session DAG live updates |
| `budget` | `budget_spend`, `budget_alert` | Budget dashboard live updates |

The `paper-build` channel requires the paper routes to call `broadcast("paper-build", ...)` during build progress. The `sessions` and `budget` channels should forward existing activity log events.

---

## 7. Implementation Order

### Phase 0: Foundation (3-4 days, no dependencies)

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 0.1 | Set up Next.js 15 project with App Router, Tailwind, shadcn/ui | 0.5d | Replace or run alongside Astro site |
| 0.2 | Build `AppShell` layout (sidebar nav, header, content area) | 0.5d | Establishes page structure for everything |
| 0.3 | Build shared components: `StatusBadge`, `RelativeTime`, `CostDisplay`, `ProgressBar`, `AgentTypeDot`, `SearchInput`, `DateRangePicker`, `Breadcrumbs` | 1d | Used across all features |
| 0.4 | Build `WebSocketProvider` context and hook (`useWebSocket`) | 0.5d | Manages WS connection lifecycle, channel subscriptions |
| 0.5 | Build API client layer with fetch wrapper, auth header injection, error handling | 0.5d | All data fetching routes through this |
| 0.6 | Implement `FilterBar` and `EmptyState` components | 0.5d | Shared across log viewer, eval, sessions |

### Phase 1: Budget Dashboard (2-3 days, depends on Phase 0)

**Why first:** Simplest feature to build end-to-end, no new backend endpoints required, validates the data fetching pattern and charting setup.

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 1.1 | `BudgetSummaryCards` — 4 summary cards with progress bars and alert levels | 0.5d | Data from `GET /api/budget` |
| 1.2 | `BudgetAlertBanner` — warning/critical/exceeded banners | 0.25d | |
| 1.3 | `BurnChart` — area chart with cumulative spend + projected trajectory | 0.5d | Install Recharts, establish charting patterns |
| 1.4 | `ProviderPieChart` + `ProviderTable` | 0.5d | |
| 1.5 | `ModelCostChart` — horizontal bar chart | 0.25d | |
| 1.6 | `ProjectSpendTable` | 0.25d | |
| 1.7 | `SessionCostScatter` — scatter plot of session costs | 0.5d | |
| 1.8 | Wire budget WebSocket channel for live updates | 0.25d | |

### Phase 2: Unified Log Viewer (3-4 days, depends on Phase 0)

**Why second:** Core infrastructure that other features link into. The transcript viewer is the deepest component.

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 2.1 | **Backend:** Implement `GET /api/sessions/:id/transcript` endpoint | 0.5d | Read JSONL from disk, paginate |
| 2.2 | **Backend:** Implement `GET /api/sessions/:id` endpoint | 0.25d | Single session metadata |
| 2.3 | `LogStream` + `LogEntry` — virtual-scrolled log list with expansion | 1d | Core log viewer component |
| 2.4 | `LiveToggle` — WebSocket integration for real-time log updates | 0.25d | |
| 2.5 | `TerminalOutput` — ANSI-aware terminal renderer | 0.5d | Used for build logs |
| 2.6 | `TranscriptViewer` + `TranscriptMessage` + `ToolCallBlock` | 1d | Most complex component |
| 2.7 | `TurnSidebar` + `TranscriptSearch` — transcript navigation | 0.5d | |
| 2.8 | Wire log viewer page with filters, search, pagination | 0.5d | |

### Phase 3: Session DAG (2-3 days, depends on Phase 0 + Phase 2)

**Why third:** Depends on the session detail sheet which links to the transcript viewer from Phase 2.

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 3.1 | Install ReactFlow, build `SessionNode` custom node component | 0.5d | |
| 3.2 | Build chain extraction logic (parse activity events for chain relationships) | 0.5d | Client-side logic from activity log data |
| 3.3 | Build `SessionDAG` with auto-layout (columns by chain depth) | 1d | Layout algorithm, edge rendering |
| 3.4 | `SessionDetailSheet` — right-side sheet with full session info | 0.5d | Links to transcript viewer |
| 3.5 | Filter bar (agent type, status, date range) | 0.25d | Reuses `FilterBar` |
| 3.6 | Wire WebSocket for live session updates | 0.25d | New sessions appear as nodes |

### Phase 4: Eval Pipeline (3-4 days, depends on Phase 0)

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 4.1 | **Backend:** Implement `GET /api/projects/:id/eval/instances` | 0.5d | Instance-level data with pagination |
| 4.2 | `AccuracyHeatmap` + `HeatmapCell` + `HeatmapLegend` | 1d | Core heatmap with color scale |
| 4.3 | `ConditionTabs` + `CoTLiftToggle` | 0.25d | |
| 4.4 | Cell drill-down page: `DifficultyChart` + `InstanceTable` | 1d | Chart + paginated table |
| 4.5 | `EvalProgressBanner` + `EvalProgressProvider` with WebSocket | 0.5d | Real-time eval progress |
| 4.6 | `RunHistoryTable` | 0.25d | |
| 4.7 | `ComparisonView` — split-screen condition comparison | 0.5d | |

### Phase 5: Project Phase Pipeline (1-2 days, depends on Phase 0 + Phase 3)

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 5.1 | **Backend:** Implement `GET /api/projects/:id/phases` | 0.5d | Parse status.yaml, count sessions per phase |
| 5.2 | `PhasePipeline` + `PhaseNode` — horizontal stepper with stream bars | 0.5d | |
| 5.3 | `StreamList` in side sheet — phase detail view | 0.25d | |
| 5.4 | Wire session list per phase (reuses session list component) | 0.25d | |
| 5.5 | Responsive vertical layout for mobile | 0.25d | |

### Phase 6: Paper Build Pipeline (2 days, depends on Phase 2)

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 6.1 | **Backend:** Add `paper-build` WebSocket channel + structured build step markers | 0.5d | Modify paper routes to broadcast events |
| 6.2 | **Backend:** Implement `GET /api/paper/builds` with DB persistence | 0.5d | New `paper_builds` table |
| 6.3 | `BuildPipeline` + `BuildStep` — vertical step indicator | 0.5d | |
| 6.4 | `PdfViewer` — inline PDF preview with controls | 0.5d | Install react-pdf |
| 6.5 | Build trigger button with options dropdown | 0.25d | |
| 6.6 | Build history table | 0.25d | |

### Phase 7: Settings (1-2 days, depends on Phase 0)

| # | Task | Effort | Notes |
|---|------|--------|-------|
| 7.1 | **Backend:** Implement `GET /api/daemon/config` and `GET /api/agents` | 0.5d | |
| 7.2 | `SettingsNav` + page layout | 0.25d | |
| 7.3 | General settings + server health display | 0.25d | |
| 7.4 | `DaemonStatusCard` + `ConfigTable` | 0.25d | |
| 7.5 | `ApiKeyRow` — masked key display | 0.25d | |
| 7.6 | `ProjectTable` with pause/resume actions | 0.25d | |
| 7.7 | `AgentCard` — agent type configuration viewer | 0.25d | |

### Summary

| Phase | Feature | Effort | Cumulative |
|-------|---------|--------|------------|
| 0 | Foundation | 3-4d | 3-4d |
| 1 | Budget Dashboard | 2-3d | 5-7d |
| 2 | Unified Log Viewer | 3-4d | 8-11d |
| 3 | Session DAG | 2-3d | 10-14d |
| 4 | Eval Pipeline | 3-4d | 13-18d |
| 5 | Phase Pipeline | 1-2d | 14-20d |
| 6 | Paper Build Pipeline | 2d | 16-22d |
| 7 | Settings | 1-2d | 17-24d |

**Total estimated effort: 17-24 working days** (3.5-5 weeks at full pace).

### Dependency Graph

```
Phase 0 (Foundation)
  ├── Phase 1 (Budget)
  ├── Phase 2 (Logs)
  │     ├── Phase 3 (Session DAG)
  │     └── Phase 6 (Paper Build)
  ├── Phase 4 (Eval)
  ├── Phase 5 (Phase Pipeline) ← also depends on Phase 3
  └── Phase 7 (Settings)
```

Phases 1, 2, 4, and 7 can run in parallel after Phase 0. Phase 3 depends on Phase 2. Phase 5 depends on Phases 0 and 3. Phase 6 depends on Phase 2.

### Backend Work Summary

New endpoints to implement (total: ~3 days of backend work, spread across phases):

1. `GET /api/sessions/:id/transcript` — 0.5d
2. `GET /api/sessions/:id` — 0.25d
3. `GET /api/projects/:id/eval/instances` — 0.5d
4. `GET /api/paper/builds` + DB migration — 0.5d
5. `GET /api/projects/:id/phases` — 0.5d
6. `GET /api/daemon/config` — 0.25d
7. `GET /api/budget/daily-history` — 0.25d
8. `GET /api/agents` — 0.25d
9. WebSocket channel additions (`paper-build`, `sessions`, `budget`) — 0.5d
