-- Deepwork Research Platform — Auth.js (NextAuth) Schema
-- Created: 2026-03-19
--
-- Standard Auth.js tables for NextAuth v5, adapted for PostgreSQL.
-- Uses `authjs_` prefix to avoid collision with existing `sessions` table.
-- Reference: https://authjs.dev/getting-started/adapters/pg

BEGIN;

-- ============================================================
-- Users — Auth.js user accounts
-- ============================================================
CREATE TABLE authjs_users (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name            TEXT,
    email           TEXT UNIQUE,
    "emailVerified" TIMESTAMPTZ,
    image           TEXT
);

-- ============================================================
-- Accounts — OAuth provider accounts linked to users
-- ============================================================
CREATE TABLE authjs_accounts (
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
    session_state       TEXT,

    UNIQUE (provider, "providerAccountId")
);

CREATE INDEX idx_authjs_accounts_user ON authjs_accounts ("userId");

-- ============================================================
-- Sessions — Auth.js sessions (separate from platform sessions)
-- ============================================================
CREATE TABLE authjs_sessions (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    "sessionToken"  TEXT NOT NULL UNIQUE,
    "userId"        TEXT NOT NULL REFERENCES authjs_users(id) ON DELETE CASCADE,
    expires         TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_authjs_sessions_user ON authjs_sessions ("userId");

-- ============================================================
-- Verification Tokens — email verification / magic links
-- ============================================================
CREATE TABLE authjs_verification_tokens (
    identifier      TEXT NOT NULL,
    token           TEXT NOT NULL,
    expires         TIMESTAMPTZ NOT NULL,

    UNIQUE (identifier, token)
);

COMMIT;
