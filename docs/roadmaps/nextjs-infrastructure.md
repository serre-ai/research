# Next.js Migration: Infrastructure Roadmap

**Created**: 2026-03-19
**Status**: Planning
**Goal**: Migrate frontend from Astro static site to Next.js 15 on Vercel, with Auth.js v5 (GitHub OAuth), while keeping the VPS as the backend workhorse.

---

## 1. Current State Assessment

### VPS (Hetzner CPX21)
- **IP**: 89.167.5.50
- **Spec**: 4 vCPU, 8 GB RAM, 80 GB disk (Ubuntu 24.04)
- **Node.js**: 22, **Python**: 3.12, **PostgreSQL**: 16
- **Express API**: port 3001, proxied by nginx on port 80
- **Daemon**: systemd `deepwork-daemon.service` (auto-restart, 60-min interval)
- **SSH**: `deepwork-vps` (user), `deepwork-vps-root` (root)
- **Repo path**: `~/deepwork` (`/opt/deepwork` symlink)

### Networking
- **DNS**: `research.oddurs.com` points to current Astro site (deployed externally)
- **No HTTPS on VPS** — port 443 open in UFW but certbot not yet configured
- **No `api.deepwork.site` DNS record** exists yet
- **CORS**: currently set to `*` (no origin restriction)

### Database
- **40+ tables** across 8 migration files (`001_initial_schema.sql` through `008_verification.sql`)
- **200K+ rows** in `eval_results`, 243 `eval_runs`, materialized views, pgvector extension
- Key tables: `projects`, `eval_results`, `eval_runs`, `sessions`, `decisions`, `budget_events`, `cost_providers`, `fixed_cost_entries`, `cost_snapshots`, plus collective/knowledge/event/planner/verification tables
- Connection string: `postgresql://deepwork:<password>@localhost:5432/deepwork`

### Authentication
- **Single API key** (`X-Api-Key` header or `?api_key=` query param)
- Stored in VPS `.env` as `DEEPWORK_API_KEY`
- WebSocket auth: `ws://host/api/ws?api_key=xxx`
- No user accounts, no sessions, no OAuth

### Frontend (Astro)
- Static site at `site/` — Astro 5.17 + Tailwind 4
- Pages: `index`, `about`, `dashboard/`, `papers/`, `research/`, `blog/`
- Dashboard pages: `dashboard/index.astro`, `dashboard/live.astro`, `dashboard/project/`
- Configured for `https://research.oddurs.com`
- Uses mock data — not yet wired to VPS API

### API Surface (Express)
25 route groups mounted in `api.ts`:
- `/api/health` (public)
- `/api/projects`, `/api/projects/:id/eval`, `/api/projects/:id/sessions`, `/api/projects/:id/decisions`
- `/api/budget`, `/api/budget/manual`, `/api/budget/providers`
- `/api/eval/jobs`, `/api/eval/status`, `/api/eval/start`, `/api/eval/stop`
- `/api/activity/recent`
- `/api/quality/:project`
- `/api/sessions/dispatch`, `/api/sessions/dispatch/queue`
- `/api/backlog`
- `/api/memory/digest`
- `/api/daemon/health`
- `/api/forum`, `/api/messages`, `/api/predictions`, `/api/agents`, `/api/rituals`, `/api/governance`
- `/api/collective`, `/api/triggers`
- `/api/planner`
- `/api/projects/:id/verification`
- `/api/paper`
- `/api/knowledge`
- `/api/events`
- **WebSocket**: `/api/ws` (channels: `eval-progress`, `logs`)

---

## 2. Target State

### Architecture

```
                          Internet
                             |
              +--------------+--------------+
              |                             |
      deepwork.site (Vercel)       api.deepwork.site (VPS)
     ┌──────────────────────┐    ┌──────────────────────────┐
     │  Next.js 15 App      │    │  nginx (HTTPS, certbot)  │
     │  ├── App Router      │    │    ↓ proxy_pass :3001    │
     │  ├── Auth.js v5      │    │  Express API + WebSocket │
     │  │   ├── GitHub OAuth│    │  ├── /api/health         │
     │  │   ├── Sessions ──────→ │  ├── /api/projects       │
     │  │   └── (PostgreSQL)│    │  ├── /api/eval           │
     │  ├── API proxy routes│───→│  ├── /api/budget         │
     │  │   (server-side)   │    │  ├── /api/ws (WebSocket) │
     │  ├── React components│    │  └── ... (25 route groups)│
     │  └── Tailwind CSS    │    │                          │
     └──────────────────────┘    │  Daemon (systemd)        │
              │                  │  PostgreSQL 16            │
              │                  │  Python venv (analysis)   │
       Vercel Edge Network       └──────────────────────────┘
```

### Communication Flow

```
Browser                    Vercel (Next.js)                  VPS (Express)
  │                             │                                │
  │── GET /dashboard ──────────→│                                │
  │                             │── fetch /api/vps/projects ────→│ (server-side, X-Api-Key)
  │                             │←── JSON response ──────────────│
  │←── Rendered HTML ───────────│                                │
  │                             │                                │
  │── WS connect ──────────────→│                                │
  │                             │── WS proxy to VPS ────────────→│ (api_key in query)
  │←── WS frames ──────────────←│←── WS frames ─────────────────│
```

### Auth Flow (GitHub OAuth)

```
Browser                    Vercel (Next.js)           GitHub           VPS PostgreSQL
  │                             │                       │                    │
  │── GET /auth/signin ────────→│                       │                    │
  │←── Redirect to GitHub ──────│                       │                    │
  │── OAuth consent ───────────────────────────────────→│                    │
  │←── Redirect + code ────────────────────────────────←│                    │
  │── GET /api/auth/callback ──→│                       │                    │
  │                             │── Exchange code ─────→│                    │
  │                             │←── Access token ──────│                    │
  │                             │── INSERT session ─────────────────────────→│
  │                             │── INSERT account ─────────────────────────→│
  │←── Set session cookie ──────│                       │                    │
  │                             │                       │                    │
  │── GET /dashboard ──────────→│                       │                    │
  │                             │── SELECT session ─────────────────────────→│
  │                             │←── Valid session ─────────────────────────←│
  │                             │── fetch VPS API (X-Api-Key) ──────────────→│
  │←── Authenticated page ──────│                       │                    │
```

---

## 3. Implementation Steps

Steps are ordered by dependency. Each step lists what, why, files, and verification.

---

### Step 1: DNS Configuration

**What**: Create DNS records for the new architecture.

**Why**: Vercel needs a domain to serve the Next.js app. The VPS needs a subdomain for HTTPS (certbot requires a domain, not a bare IP).

**Actions**:
1. Add an A record: `api.deepwork.site` -> `89.167.5.50`
2. Either:
   - (a) Point `deepwork.site` to Vercel via CNAME (Vercel will provide the value during project setup), or
   - (b) Keep `research.oddurs.com` and add a Vercel domain later

**DNS records** (at your registrar for `deepwork.site`):

```
Type    Name    Value               TTL
A       api     89.167.5.50         300
CNAME   @       cname.vercel-dns.com  300   (added after Vercel project setup)
CNAME   www     cname.vercel-dns.com  300
```

**Verification**:
```bash
dig api.deepwork.site +short
# Expected: 89.167.5.50

dig deepwork.site +short
# Expected: Vercel IP (76.76.21.x or similar)
```

**Dependencies**: None. Do this first since DNS propagation can take minutes to hours.

---

### Step 2: SSL/HTTPS on VPS

**What**: Install a TLS certificate for `api.deepwork.site` using Let's Encrypt.

**Why**: The Next.js app on Vercel runs over HTTPS. Browsers and server-side fetch calls to the VPS API need HTTPS to avoid mixed-content errors and ensure transport security.

**Actions** (on VPS):

1. Install certbot:
```bash
sudo apt update && sudo apt install -y certbot python3-certbot-nginx
```

2. Update nginx to serve the API subdomain. Create or edit `/etc/nginx/sites-available/deepwork-api`:
```nginx
server {
    listen 80;
    server_name api.deepwork.site;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts for long-running requests
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

3. Enable and test:
```bash
sudo ln -sf /etc/nginx/sites-available/deepwork-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

4. Run certbot:
```bash
sudo certbot --nginx -d api.deepwork.site
```

Certbot will modify the nginx config to add the `listen 443 ssl` block and redirect HTTP to HTTPS.

5. Verify auto-renewal:
```bash
sudo certbot renew --dry-run
```

**Verification**:
```bash
curl -s https://api.deepwork.site/api/health | jq .status
# Expected: "ok"
```

**Dependencies**: Step 1 (DNS must resolve before certbot can verify).

---

### Step 3: CORS Configuration on VPS

**What**: Restrict CORS to allow only the Vercel-hosted frontend.

**Why**: The current API allows `*` origins. Once we have a known frontend domain, lock it down. Note that the Next.js API proxy makes server-side requests (no CORS needed for those), but the WebSocket connection from the browser will trigger CORS preflight.

**Actions**:

1. Update `.env` on VPS:
```bash
# Add to ~/deepwork/.env
CORS_ORIGIN=https://deepwork.site
```

2. The Express API already reads `CORS_ORIGIN` from env (line 1077 of `api.ts`):
```typescript
const origin = config.corsOrigin ?? "*";
```
No code change needed — just set the env var. The daemon reads `CORS_ORIGIN` from `process.env` at startup.

3. If you need multiple origins (e.g., localhost during development), modify the CORS middleware in `orchestrator/src/api.ts` to accept a comma-separated list:

```typescript
// In the CORS middleware
app.use((_req: Request, res: Response, next: NextFunction) => {
    const allowedOrigins = (config.corsOrigin ?? "*").split(",").map(s => s.trim());
    const requestOrigin = _req.headers.origin ?? "";
    const origin = allowedOrigins.includes("*") ? "*"
        : allowedOrigins.includes(requestOrigin) ? requestOrigin
        : "";
    if (origin) {
        res.setHeader("Access-Control-Allow-Origin", origin);
    }
    // ... rest unchanged
});
```

4. Restart daemon:
```bash
sudo systemctl restart deepwork-daemon
```

**Verification**:
```bash
# Should succeed (correct origin):
curl -s -H "Origin: https://deepwork.site" -H "X-Api-Key: $DEEPWORK_API_KEY" \
  https://api.deepwork.site/api/projects -I | grep Access-Control

# Should fail (wrong origin):
curl -s -H "Origin: https://evil.com" -H "X-Api-Key: $DEEPWORK_API_KEY" \
  https://api.deepwork.site/api/projects -I | grep Access-Control
```

**Dependencies**: Step 2 (HTTPS must be working).

---

### Step 4: PostgreSQL Auth.js Tables

**What**: Create the required Auth.js v5 tables in the existing PostgreSQL database.

**Why**: Auth.js needs `users`, `accounts`, `sessions`, and `verification_token` tables to store OAuth data and session state. These go in the same database as the rest of the platform.

**Actions**:

1. Create migration file `orchestrator/sql/009_authjs.sql`:

```sql
-- Auth.js v5 PostgreSQL Adapter Tables
-- Migration: 009_authjs.sql
-- Created: 2026-03-19
--
-- Required by @auth/pg-adapter for NextAuth.js v5.
-- These tables store OAuth accounts, user profiles, and sessions.
-- Matches the schema expected by @auth/pg-adapter exactly.

BEGIN;

-- ============================================================
-- users — authenticated users (GitHub profile data)
-- ============================================================
CREATE TABLE IF NOT EXISTS authjs_users (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name            TEXT,
    email           TEXT UNIQUE,
    "emailVerified" TIMESTAMPTZ,
    image           TEXT
);

-- ============================================================
-- accounts — OAuth provider connections
-- ============================================================
CREATE TABLE IF NOT EXISTS authjs_accounts (
    id                  TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    "userId"            TEXT NOT NULL REFERENCES authjs_users(id) ON DELETE CASCADE,
    type                TEXT NOT NULL,
    provider            TEXT NOT NULL,
    "providerAccountId" TEXT NOT NULL,
    refresh_token       TEXT,
    access_token        TEXT,
    expires_at          INTEGER,
    token_type          TEXT,
    scope               TEXT,
    id_token            TEXT,
    session_state        TEXT,
    UNIQUE(provider, "providerAccountId")
);

-- ============================================================
-- sessions — browser sessions (cookie-backed)
-- ============================================================
CREATE TABLE IF NOT EXISTS authjs_sessions (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    "sessionToken"  TEXT NOT NULL UNIQUE,
    "userId"        TEXT NOT NULL REFERENCES authjs_users(id) ON DELETE CASCADE,
    expires         TIMESTAMPTZ NOT NULL
);

-- ============================================================
-- verification_token — email verification / magic links
-- ============================================================
CREATE TABLE IF NOT EXISTS authjs_verification_token (
    identifier      TEXT NOT NULL,
    token           TEXT NOT NULL UNIQUE,
    expires         TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (identifier, token)
);

-- Indexes for session lookup performance
CREATE INDEX IF NOT EXISTS idx_authjs_sessions_token ON authjs_sessions ("sessionToken");
CREATE INDEX IF NOT EXISTS idx_authjs_sessions_user  ON authjs_sessions ("userId");
CREATE INDEX IF NOT EXISTS idx_authjs_accounts_user  ON authjs_accounts ("userId");

COMMIT;
```

2. Apply on VPS:
```bash
ssh deepwork-vps "psql deepwork < ~/deepwork/orchestrator/sql/009_authjs.sql"
```

**Note on table naming**: Auth.js's `@auth/pg-adapter` expects specific column names (camelCase like `emailVerified`, `sessionToken`, `providerAccountId`). The `authjs_` prefix avoids collisions with the existing `sessions` table (which tracks Claude agent sessions, a completely different concept). You will configure the adapter to use these prefixed table names.

**Verification**:
```bash
ssh deepwork-vps "psql deepwork -c '\dt authjs_*'"
# Expected: 4 tables listed
```

**Dependencies**: None (can run in parallel with Steps 1-3).

---

### Step 5: Vercel Project Setup

**What**: Create a Vercel project linked to the deepwork repo, configured to build from a `site-next/` directory (or root, depending on monorepo strategy).

**Why**: Vercel hosts the Next.js frontend. Needs to be configured before we can deploy.

**Actions**:

1. **Create the Next.js app** (local, in repo root):
```bash
cd /Users/oddurs/Code/deepwork
npx create-next-app@latest site-next \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --use-npm
```

This creates `site-next/` alongside the existing `site/` (Astro), allowing a gradual migration.

2. **Update root `package.json`** — add `site-next` to workspaces:
```json
{
  "workspaces": [
    "orchestrator",
    "cli",
    "site",
    "site-next"
  ]
}
```

3. **Link to Vercel**:
```bash
cd site-next
npx vercel link
```
During setup:
- Select your Vercel account
- Link to existing project or create new
- Framework: Next.js (auto-detected)
- Root Directory: `site-next`

4. **Configure Vercel project settings** (via dashboard or `vercel.json`):

Create `site-next/vercel.json`:
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next"
}
```

5. **Add custom domain** in Vercel dashboard:
   - Go to Project Settings > Domains
   - Add `deepwork.site` and `www.deepwork.site`
   - Vercel will show you the DNS records to set (done in Step 1)

**Verification**:
```bash
cd /Users/oddurs/Code/deepwork/site-next
npx vercel dev
# Should start local dev server at localhost:3000
```

**Dependencies**: None (can run in parallel with Steps 1-4).

---

### Step 6: Auth.js Configuration

**What**: Set up Auth.js v5 with GitHub OAuth provider and PostgreSQL session storage.

**Why**: The platform needs user authentication. GitHub OAuth is the simplest path — Oddur already has a GitHub account, and the platform is GitHub-centric.

**Actions**:

1. **Create a GitHub OAuth App**:
   - Go to https://github.com/settings/developers
   - Click "New OAuth App"
   - Application name: `Deepwork`
   - Homepage URL: `https://deepwork.site`
   - Authorization callback URL: `https://deepwork.site/api/auth/callback/github`
   - Save the **Client ID** and generate a **Client Secret**

2. **Install dependencies** in `site-next/`:
```bash
cd /Users/oddurs/Code/deepwork/site-next
npm install next-auth@beta @auth/pg-adapter pg
npm install -D @types/pg
```

3. **Create auth configuration** at `site-next/src/lib/auth.ts`:

```typescript
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import PostgresAdapter from "@auth/pg-adapter";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.AUTH_DATABASE_URL,
  max: 5,
  ssl: { rejectUnauthorized: false },
});

// Map Auth.js default table names to our prefixed tables
const adapter = PostgresAdapter(pool, {
  // If @auth/pg-adapter supports table name config, use it.
  // Otherwise, create a view layer (see note below).
});

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter,
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID!,
      clientSecret: process.env.AUTH_GITHUB_SECRET!,
    }),
  ],
  session: {
    strategy: "database",          // Store sessions in PostgreSQL
    maxAge: 30 * 24 * 60 * 60,    // 30 days
  },
  callbacks: {
    async signIn({ user }) {
      // Restrict to specific GitHub users (allowlist)
      const allowedEmails = (process.env.AUTH_ALLOWED_EMAILS ?? "").split(",");
      if (user.email && allowedEmails.includes(user.email)) {
        return true;
      }
      return false; // Reject unknown users
    },
    async session({ session, user }) {
      session.user.id = user.id;
      return session;
    },
  },
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },
});
```

**Note on adapter table names**: The `@auth/pg-adapter` by default expects tables named `users`, `accounts`, `sessions`, `verification_token`. Since we prefixed them with `authjs_`, you have two options:
- (a) Use PostgreSQL views to alias: `CREATE VIEW users AS SELECT * FROM authjs_users;` etc.
- (b) Use the non-prefixed names if collision with the existing `sessions` table is acceptable (it is not — the existing `sessions` table has a different schema entirely).
- (c) Fork or wrap the adapter to use custom table names (most robust).

The recommended approach is **(a)** — create views in a separate schema:

```sql
-- Add to 009_authjs.sql or create 010_authjs_views.sql
CREATE SCHEMA IF NOT EXISTS authjs;
CREATE VIEW authjs.users AS SELECT * FROM authjs_users;
CREATE VIEW authjs.accounts AS SELECT * FROM authjs_accounts;
CREATE VIEW authjs.sessions AS SELECT * FROM authjs_sessions;
CREATE VIEW authjs.verification_token AS SELECT * FROM authjs_verification_token;
```

Then configure the adapter pool to use `search_path: 'authjs,public'`.

4. **Create the API route handler** at `site-next/src/app/api/auth/[...nextauth]/route.ts`:

```typescript
import { handlers } from "@/lib/auth";
export const { GET, POST } = handlers;
```

5. **Create middleware** at `site-next/src/middleware.ts` to protect dashboard routes:

```typescript
import { auth } from "@/lib/auth";

export default auth((req) => {
  const isAuthenticated = !!req.auth;
  const isAuthRoute = req.nextUrl.pathname.startsWith("/api/auth");
  const isPublicRoute = ["/", "/about", "/papers", "/research"].includes(req.nextUrl.pathname);

  if (!isAuthenticated && !isAuthRoute && !isPublicRoute) {
    return Response.redirect(new URL("/auth/signin", req.nextUrl.origin));
  }
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

**Verification**:
```bash
cd /Users/oddurs/Code/deepwork/site-next
AUTH_GITHUB_ID=xxx AUTH_GITHUB_SECRET=xxx AUTH_DATABASE_URL=xxx AUTH_SECRET=xxx npm run dev
# Visit http://localhost:3000/api/auth/signin
# Should show GitHub sign-in button
```

**Dependencies**: Step 4 (Auth.js tables must exist in PostgreSQL), Step 5 (Next.js project must exist).

---

### Step 7: VPS PostgreSQL — Allow Remote Connections (for Auth.js)

**What**: Configure PostgreSQL on the VPS to accept connections from Vercel's servers over SSL.

**Why**: Auth.js running on Vercel needs to read/write sessions directly in the VPS PostgreSQL. The Express API proxy pattern does not work for Auth.js — it needs a direct database connection.

**Actions**:

1. **Create a dedicated auth database user** (least privilege):
```bash
ssh deepwork-vps "sudo -u postgres psql -c \"
  CREATE USER authjs WITH PASSWORD '<strong-random-password>';
  GRANT CONNECT ON DATABASE deepwork TO authjs;
  GRANT USAGE ON SCHEMA public TO authjs;
  GRANT SELECT, INSERT, UPDATE, DELETE ON authjs_users, authjs_accounts, authjs_sessions, authjs_verification_token TO authjs;
\""
```

2. **Enable SSL on PostgreSQL**:
```bash
ssh deepwork-vps-root << 'CMDS'
# Generate self-signed cert (or use the Let's Encrypt cert)
sudo -u postgres openssl req -new -x509 -days 365 -nodes \
  -out /etc/postgresql/16/main/server.crt \
  -keyout /etc/postgresql/16/main/server.key \
  -subj "/CN=api.deepwork.site"
chmod 600 /etc/postgresql/16/main/server.key
chown postgres:postgres /etc/postgresql/16/main/server.{crt,key}
CMDS
```

3. **Edit `postgresql.conf`** on VPS:
```bash
# /etc/postgresql/16/main/postgresql.conf
listen_addresses = 'localhost,89.167.5.50'
ssl = on
ssl_cert_file = '/etc/postgresql/16/main/server.crt'
ssl_key_file = '/etc/postgresql/16/main/server.key'
```

4. **Edit `pg_hba.conf`** — allow the `authjs` user from any IP over SSL:
```
# /etc/postgresql/16/main/pg_hba.conf
# Auth.js connections from Vercel (SSL required, specific user only)
hostssl deepwork authjs 0.0.0.0/0 scram-sha-256
```

5. **Open port 5432** in UFW (restrict to known Vercel IP ranges if possible, but Vercel uses many IPs):
```bash
sudo ufw allow 5432/tcp comment "PostgreSQL for Auth.js"
sudo systemctl restart postgresql
```

**Security consideration**: Exposing PostgreSQL to the internet is a trade-off. Mitigations:
- The `authjs` user can only access 4 tables
- SSL required (no plaintext connections)
- Strong random password
- fail2ban can be configured for PostgreSQL
- Alternative: Use a managed PostgreSQL service (Neon, Supabase) for auth tables only — see Security Considerations section

**Verification**:
```bash
# From local machine:
psql "postgresql://authjs:<password>@api.deepwork.site:5432/deepwork?sslmode=require" \
  -c "SELECT count(*) FROM authjs_users;"
# Expected: 0 (empty table)
```

**Dependencies**: Step 4 (tables must exist).

---

### Step 8: Next.js API Proxy (VPS Backend Access)

**What**: Create Next.js API route handlers that proxy requests to the VPS Express API, injecting the API key server-side.

**Why**: The VPS API key must never reach the browser. The Next.js server acts as a secure intermediary — authenticated users hit Next.js routes, which forward to the VPS with the secret key.

**Actions**:

1. **Create the proxy utility** at `site-next/src/lib/vps-client.ts`:

```typescript
const VPS_API_URL = process.env.VPS_API_URL!;       // https://api.deepwork.site
const VPS_API_KEY = process.env.VPS_API_KEY!;        // DEEPWORK_API_KEY value

export async function vpsFetch(
  path: string,
  options: RequestInit = {},
): Promise<Response> {
  const url = `${VPS_API_URL}${path}`;
  const headers = new Headers(options.headers);
  headers.set("X-Api-Key", VPS_API_KEY);
  headers.set("Content-Type", "application/json");

  return fetch(url, {
    ...options,
    headers,
    // No caching for API data
    cache: "no-store",
  });
}
```

2. **Create proxy route handlers**. Example for `/api/vps/[...path]/route.ts`:

```typescript
// site-next/src/app/api/vps/[...path]/route.ts
import { auth } from "@/lib/auth";
import { vpsFetch } from "@/lib/vps-client";
import { NextRequest, NextResponse } from "next/server";

async function handler(req: NextRequest, { params }: { params: { path: string[] } }) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const path = `/api/${params.path.join("/")}`;
  const searchParams = req.nextUrl.searchParams.toString();
  const fullPath = searchParams ? `${path}?${searchParams}` : path;

  const vpsResponse = await vpsFetch(fullPath, {
    method: req.method,
    body: req.method !== "GET" ? await req.text() : undefined,
  });

  const data = await vpsResponse.json();
  return NextResponse.json(data, { status: vpsResponse.status });
}

export const GET = handler;
export const POST = handler;
export const PATCH = handler;
export const DELETE = handler;
```

3. **Usage in React Server Components**:

```typescript
// site-next/src/app/dashboard/page.tsx
import { auth } from "@/lib/auth";
import { vpsFetch } from "@/lib/vps-client";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();
  if (!session) redirect("/auth/signin");

  const res = await vpsFetch("/api/projects");
  const projects = await res.json();

  return <Dashboard projects={projects} />;
}
```

**Verification**:
```bash
# With local dev server running (requires env vars set):
curl -s http://localhost:3000/api/vps/health | jq .status
# Expected: "ok" (proxied from VPS)
```

**Dependencies**: Step 2 (VPS HTTPS), Step 6 (Auth.js configured).

---

### Step 9: WebSocket Proxy

**What**: Enable the browser to receive real-time WebSocket updates from the VPS through the Next.js layer.

**Why**: The dashboard has a live eval monitor (`dashboard/live.astro` currently) that needs real-time updates. Vercel's serverless environment does not support persistent WebSocket connections natively.

**Options** (in order of preference):

#### Option A: Direct WebSocket from Browser to VPS (Recommended)

The simplest approach. The browser connects directly to `wss://api.deepwork.site/api/ws?api_key=<token>`.

**Problem**: This exposes the API key to the browser.
**Solution**: Create a short-lived WebSocket token endpoint:

1. Add a new route to the Express API (`orchestrator/src/api.ts`):
```typescript
// POST /api/ws/token — issue a short-lived WebSocket token
router.post("/ws/token", async (req: Request, res: Response) => {
  const token = crypto.randomUUID();
  const expiresAt = Date.now() + 60_000; // 60 seconds
  wsTokens.set(token, expiresAt);
  res.json({ token, expiresAt });
});
```

2. Modify WebSocket auth to accept these tokens:
```typescript
// In setupWebSocket():
const key = url.searchParams.get("api_key");
const token = url.searchParams.get("token");

if (key === apiKey) { /* permanent key: OK */ }
else if (token && wsTokens.has(token)) {
  const expires = wsTokens.get(token)!;
  wsTokens.delete(token); // one-time use
  if (Date.now() > expires) {
    ws.close(4001, "Token expired");
    return;
  }
} else {
  ws.close(4001, "Unauthorized");
  return;
}
```

3. Next.js server-side endpoint to issue token (authenticated):
```typescript
// site-next/src/app/api/ws-token/route.ts
import { auth } from "@/lib/auth";
import { vpsFetch } from "@/lib/vps-client";

export async function POST() {
  const session = await auth();
  if (!session?.user) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  const res = await vpsFetch("/api/ws/token", { method: "POST" });
  return Response.json(await res.json());
}
```

4. Client-side connection:
```typescript
// React hook in the browser
async function connectWebSocket() {
  const { token } = await fetch("/api/ws-token", { method: "POST" }).then(r => r.json());
  const ws = new WebSocket(`wss://api.deepwork.site/api/ws?token=${token}`);
  ws.onopen = () => ws.send(JSON.stringify({ type: "subscribe", channel: "eval-progress" }));
  return ws;
}
```

#### Option B: Server-Sent Events (SSE) as Fallback

If WebSocket complexity is too high, convert the live feed to SSE:
- Create a Next.js API route that opens a connection to the VPS WebSocket server-side
- Stream events to the browser as SSE (`text/event-stream`)
- Simpler but one-directional (browser can't send messages to VPS)

#### Option C: Polling

Simplest fallback — poll `/api/vps/eval/status` every 5 seconds. No WebSocket needed. Adequate for eval progress that updates every few seconds at most.

**Recommendation**: Start with Option A. Fall back to Option C if the token system adds too much complexity for the current stage.

**Dependencies**: Step 3 (CORS), Step 8 (API proxy for token endpoint).

---

### Step 10: Environment Variable Management

**What**: Define what goes where and ensure secrets are properly isolated.

**Why**: The system spans two environments (Vercel and VPS). Misconfigured secrets could expose the VPS API key to browsers or break auth flows.

#### Vercel Environment Variables (set in Vercel Dashboard > Settings > Environment Variables)

| Variable | Value | Purpose |
|----------|-------|---------|
| `AUTH_SECRET` | `openssl rand -base64 32` | Auth.js encryption key |
| `AUTH_GITHUB_ID` | GitHub OAuth Client ID | GitHub sign-in |
| `AUTH_GITHUB_SECRET` | GitHub OAuth Client Secret | GitHub sign-in |
| `AUTH_DATABASE_URL` | `postgresql://authjs:<pw>@api.deepwork.site:5432/deepwork?sslmode=require` | Auth.js session storage |
| `AUTH_ALLOWED_EMAILS` | `oddur@example.com` | Allowlisted user emails |
| `VPS_API_URL` | `https://api.deepwork.site` | Express API base URL |
| `VPS_API_KEY` | `85062f0e...` (existing key) | VPS API authentication |
| `NEXTAUTH_URL` | `https://deepwork.site` | Auth.js canonical URL |

All of these are server-side only. None should be prefixed with `NEXT_PUBLIC_`.

#### VPS Environment Variables (`~/deepwork/.env`)

Existing variables (no changes needed):
| Variable | Purpose |
|----------|---------|
| `DEEPWORK_API_KEY` | API authentication |
| `DATABASE_URL` | PostgreSQL connection (local) |
| `API_PORT` | Express port (3001) |
| `CORS_ORIGIN` | **Update to**: `https://deepwork.site` |
| `ANTHROPIC_API_KEY` | Model API access |
| `OPENAI_API_KEY` | Model API access |
| `OPENROUTER_API_KEY` | Model API access |
| `FIRECRAWL_API_KEY` | Web scraping |

New variable to add:
| Variable | Purpose |
|----------|---------|
| `CORS_ORIGIN` | Set to `https://deepwork.site` (was `*` or unset) |

#### Local Development (`.env.local` in `site-next/`)

```env
AUTH_SECRET=dev-secret-change-me
AUTH_GITHUB_ID=<dev-oauth-app-client-id>
AUTH_GITHUB_SECRET=<dev-oauth-app-secret>
AUTH_DATABASE_URL=postgresql://authjs:<pw>@api.deepwork.site:5432/deepwork?sslmode=require
AUTH_ALLOWED_EMAILS=oddur@example.com
VPS_API_URL=https://api.deepwork.site
VPS_API_KEY=85062f0e...
NEXTAUTH_URL=http://localhost:3000
```

Add `site-next/.env.local` to `.gitignore`.

**Tip**: Create a separate GitHub OAuth App for local development with callback URL `http://localhost:3000/api/auth/callback/github`.

**Dependencies**: Steps 5, 6, 7.

---

### Step 11: Monitoring and Health Checks

**What**: Verify both systems are healthy and set up basic uptime monitoring.

**Why**: With two systems (Vercel + VPS), you need to know when either is down.

**Actions**:

1. **VPS health endpoint** (already exists):
```bash
curl -s https://api.deepwork.site/api/health | jq '{status, uptime_s, database, timestamp}'
```

2. **Next.js health endpoint** — create `site-next/src/app/api/health/route.ts`:

```typescript
import { vpsFetch } from "@/lib/vps-client";

export async function GET() {
  let vpsStatus = "unreachable";
  try {
    const res = await vpsFetch("/api/health");
    const data = await res.json();
    vpsStatus = data.status;
  } catch {
    vpsStatus = "error";
  }

  return Response.json({
    status: "ok",
    frontend: "vercel",
    vps: vpsStatus,
    timestamp: new Date().toISOString(),
  });
}
```

3. **Uptime monitoring** (pick one):
   - **UptimeRobot** (free, 5-min intervals): monitor `https://api.deepwork.site/api/health` and `https://deepwork.site/api/health`
   - **Better Stack** (free tier): same endpoints, with Slack integration
   - **Simple cron on VPS**: Add to crontab:
```bash
# Every 5 minutes, check both endpoints
*/5 * * * * curl -sf https://api.deepwork.site/api/health > /dev/null || echo "VPS API down" | mail -s "Deepwork Alert" oddur@example.com
```

4. **Vercel deployment notifications**: Enable in Vercel Dashboard > Settings > Notifications. Get Slack or email alerts on failed deployments.

**Verification**:
```bash
curl -s https://deepwork.site/api/health | jq .
# Expected: { status: "ok", frontend: "vercel", vps: "ok", ... }
```

**Dependencies**: Steps 2, 5, 8 (everything deployed and connected).

---

### Step 12: Rollback Plan

If something breaks during migration, here is how to revert at each stage.

#### DNS Rollback
```bash
# Point deepwork.site back to original host (or remove Vercel DNS records)
# Revert api.deepwork.site A record
# TTL was set to 300s, so changes propagate within 5 minutes
```

#### VPS Rollback
The VPS is untouched by the frontend migration. The only VPS changes are:
- CORS_ORIGIN env var (revert to `*`)
- nginx config for api.deepwork.site (remove the server block)
- PostgreSQL auth tables (drop if needed, zero impact on existing tables)
- pg_hba.conf remote access (comment out the authjs line)

```bash
# Revert CORS
ssh deepwork-vps "sed -i 's/^CORS_ORIGIN=.*/CORS_ORIGIN=*/' ~/deepwork/.env"
ssh deepwork-vps "sudo systemctl restart deepwork-daemon"

# Remove remote PG access
ssh deepwork-vps-root "sudo ufw delete allow 5432/tcp"

# Revert nginx
ssh deepwork-vps-root "sudo rm /etc/nginx/sites-enabled/deepwork-api && sudo systemctl reload nginx"
```

#### Frontend Rollback
The Astro site at `site/` is preserved. To revert:
1. Point DNS back to original host
2. Redeploy Astro site
3. The Next.js code in `site-next/` can remain in the repo without impact

#### Database Rollback
```sql
-- Only drops auth tables, zero impact on platform data
DROP TABLE IF EXISTS authjs_verification_token CASCADE;
DROP TABLE IF EXISTS authjs_sessions CASCADE;
DROP TABLE IF EXISTS authjs_accounts CASCADE;
DROP TABLE IF EXISTS authjs_users CASCADE;
DROP SCHEMA IF EXISTS authjs CASCADE;
```

---

## 4. Security Considerations

### API Key Isolation
- The `DEEPWORK_API_KEY` is stored **only** in:
  - VPS `.env` (filesystem, chmod 600)
  - Vercel environment variables (encrypted at rest)
- It is **never** sent to the browser. All VPS API calls happen server-side in Next.js API routes or Server Components.
- The only browser-facing secret is the Auth.js session cookie (httpOnly, secure, sameSite=lax).

### CORS Whitelist
- VPS Express API restricts `Access-Control-Allow-Origin` to `https://deepwork.site`
- WebSocket upgrade requests are authenticated via short-lived tokens (not the permanent API key)

### Rate Limiting
- Add rate limiting to the Express API on VPS. Install `express-rate-limit`:
```typescript
import rateLimit from "express-rate-limit";

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                    // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
});
app.use("/api/", limiter);
```
- Vercel has built-in DDoS protection on the Edge Network.
- Consider `express-slow-down` for progressive delays on heavy endpoints like `/api/eval`.

### Session Security
- Auth.js sessions stored in PostgreSQL (not JWT — database sessions can be revoked)
- Session cookie: `httpOnly`, `secure`, `sameSite=lax`
- 30-day max age with sliding window
- GitHub OAuth scope limited to `read:user` and `user:email` (no repo access needed)

### PostgreSQL Remote Access Hardening
Exposing PostgreSQL port 5432 is the highest-risk change. Mitigations:
1. **Dedicated user** (`authjs`) with access to only 4 tables
2. **SSL required** (`hostssl` in `pg_hba.conf`)
3. **Strong password** (32+ character random string)
4. **fail2ban for PostgreSQL**: Add a jail in `/etc/fail2ban/jail.local`:
```ini
[postgresql]
enabled = true
port = 5432
filter = postgresql
logpath = /var/log/postgresql/postgresql-16-main.log
maxretry = 5
bantime = 3600
```

**Alternative — eliminate remote PostgreSQL exposure entirely**:
Use a managed PostgreSQL service (Neon free tier, Supabase free tier, or Vercel Postgres) for the 4 Auth.js tables only. This way:
- VPS PostgreSQL stays local-only (current config, no port 5432 exposure)
- Auth.js connects to managed PG (Neon/Supabase provide connection strings)
- Zero security risk, ~$0 additional cost on free tiers
- Trade-off: auth data lives outside the VPS (acceptable — it is just session tokens, not research data)

This is the recommended path if you want to avoid opening port 5432.

---

## 5. Cost Analysis

### Vercel

| Tier | Price | Limits | Fits? |
|------|-------|--------|-------|
| **Hobby (Free)** | $0/mo | 100 GB bandwidth, 100 hrs build, 1 concurrent build, no commercial use | Yes for personal/research use |
| **Pro** | $20/mo | 1 TB bandwidth, 400 hrs build, team features, custom headers | Only if free tier limits hit |

**Recommendation**: Start on **Hobby (free)**. The dashboard is single-user (Oddur only). Traffic will be minimal. Upgrade to Pro only if:
- You need password-protected preview deployments
- Build times exceed 100 hours/month (unlikely — Next.js builds in ~30s)
- You want Vercel Analytics or Speed Insights

### VPS (No Change)

| Item | Cost |
|------|------|
| Hetzner CPX21 | $5.50/mo (billed as ~$8/mo with tax in earlier docs) |

The VPS cost does not change. It continues running Express API, PostgreSQL, daemon, and Python analysis.

### DNS

| Provider | Cost |
|----------|------|
| Most registrars | $0 for DNS records (included with domain) |
| Cloudflare (if used) | $0 (free tier includes DNS) |
| Domain renewal (`deepwork.site`) | ~$10-15/year |

### Auth.js Database (if using managed PG instead of VPS PG)

| Service | Cost |
|---------|------|
| Neon free tier | $0 (0.5 GB storage, 190 compute hours) |
| Supabase free tier | $0 (500 MB storage, 2 projects) |
| Vercel Postgres | $0 on Hobby (256 MB) |

### SSL

| Item | Cost |
|------|------|
| Let's Encrypt (certbot) | $0 |

### Total Additional Cost

| Scenario | Monthly Cost |
|----------|-------------|
| Vercel Hobby + Let's Encrypt + VPS PG | **$0/mo** additional |
| Vercel Hobby + Let's Encrypt + Neon for auth | **$0/mo** additional |
| Vercel Pro + Let's Encrypt + VPS PG | **$20/mo** additional |

**Bottom line**: The migration adds **$0/month** to the current budget if using Vercel's free tier and Let's Encrypt. The VPS cost remains $5.50/mo. Total infrastructure cost stays well within the $1,000/mo budget, which is dominated by API costs (Anthropic, OpenAI), not hosting.

---

## Appendix: Implementation Order Summary

```
Week 1: Foundation
  ├── Step 1: DNS records (10 min)
  ├── Step 4: Auth.js PG migration (15 min, parallel with DNS)
  ├── Step 5: Create Next.js project, link Vercel (30 min)
  └── Step 2: SSL/HTTPS on VPS (20 min, after DNS propagates)

Week 1-2: Auth & Security
  ├── Step 3: CORS lockdown (10 min)
  ├── Step 6: Auth.js + GitHub OAuth (2-3 hours)
  ├── Step 7: PG remote access or managed PG setup (1 hour)
  └── Step 10: Environment variables (30 min)

Week 2: Integration
  ├── Step 8: API proxy routes (1-2 hours)
  ├── Step 9: WebSocket proxy (1-2 hours)
  └── Step 11: Monitoring (30 min)

Ongoing: Step 12 (rollback plan) is a reference, not an action.
```

**Estimated total effort**: 8-12 hours of implementation work, spread across 1-2 weeks to allow DNS propagation and testing between steps.
