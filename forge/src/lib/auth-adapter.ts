/**
 * Custom Auth.js adapter for PostgreSQL with `authjs_` table prefix.
 *
 * The stock @auth/pg-adapter hardcodes table names (users, accounts, sessions,
 * verification_token). Our DB uses authjs_users, authjs_accounts, authjs_sessions,
 * authjs_verification_tokens to avoid collision with the platform's own `sessions`
 * table. This adapter rewrites the queries accordingly.
 */
import type { Adapter, AdapterUser, AdapterAccount, AdapterSession } from 'next-auth/adapters';
import type { Pool } from 'pg';

function mapExpiresAt(account: Record<string, unknown>): AdapterAccount {
  return {
    ...account,
    expires_at: account.expires_at ? parseInt(String(account.expires_at)) : undefined,
  } as AdapterAccount;
}

export default function AuthjsAdapter(pool: Pool): Adapter {
  return {
    async createVerificationToken(verificationToken) {
      const { identifier, expires, token } = verificationToken;
      await pool.query(
        `INSERT INTO authjs_verification_tokens (identifier, expires, token) VALUES ($1, $2, $3)`,
        [identifier, expires, token],
      );
      return verificationToken;
    },

    async useVerificationToken({ identifier, token }) {
      const result = await pool.query(
        `DELETE FROM authjs_verification_tokens WHERE identifier = $1 AND token = $2
         RETURNING identifier, expires, token`,
        [identifier, token],
      );
      return result.rowCount !== 0 ? result.rows[0] : null;
    },

    async createUser(user) {
      const { name, email, emailVerified, image } = user;
      const result = await pool.query(
        `INSERT INTO authjs_users (name, email, "emailVerified", image)
         VALUES ($1, $2, $3, $4)
         RETURNING id, name, email, "emailVerified", image`,
        [name, email, emailVerified, image],
      );
      return result.rows[0] as AdapterUser;
    },

    async getUser(id) {
      try {
        const result = await pool.query(`SELECT * FROM authjs_users WHERE id = $1`, [id]);
        return result.rowCount === 0 ? null : (result.rows[0] as AdapterUser);
      } catch {
        return null;
      }
    },

    async getUserByEmail(email) {
      const result = await pool.query(`SELECT * FROM authjs_users WHERE email = $1`, [email]);
      return result.rowCount !== 0 ? (result.rows[0] as AdapterUser) : null;
    },

    async getUserByAccount({ providerAccountId, provider }) {
      const result = await pool.query(
        `SELECT u.* FROM authjs_users u
         JOIN authjs_accounts a ON u.id = a."userId"
         WHERE a.provider = $1 AND a."providerAccountId" = $2`,
        [provider, providerAccountId],
      );
      return result.rowCount !== 0 ? (result.rows[0] as AdapterUser) : null;
    },

    async updateUser(user) {
      const fetchResult = await pool.query(`SELECT * FROM authjs_users WHERE id = $1`, [user.id]);
      const oldUser = fetchResult.rows[0];
      const newUser = { ...oldUser, ...user };
      const { id, name, email, emailVerified, image } = newUser;
      const result = await pool.query(
        `UPDATE authjs_users SET name = $2, email = $3, "emailVerified" = $4, image = $5
         WHERE id = $1
         RETURNING id, name, email, "emailVerified", image`,
        [id, name, email, emailVerified, image],
      );
      return result.rows[0] as AdapterUser;
    },

    async linkAccount(account) {
      const result = await pool.query(
        `INSERT INTO authjs_accounts
         ("userId", provider, type, "providerAccountId", access_token, expires_at,
          refresh_token, id_token, scope, session_state, token_type)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
         RETURNING id, "userId", provider, type, "providerAccountId", access_token,
                   expires_at, refresh_token, id_token, scope, session_state, token_type`,
        [
          account.userId,
          account.provider,
          account.type,
          account.providerAccountId,
          account.access_token ?? null,
          account.expires_at ?? null,
          account.refresh_token ?? null,
          account.id_token ?? null,
          account.scope ?? null,
          account.session_state ?? null,
          account.token_type ?? null,
        ],
      );
      return mapExpiresAt(result.rows[0]);
    },

    async createSession({ sessionToken, userId, expires }) {
      if (userId === undefined) {
        throw Error('userId is undefined in createSession');
      }
      const result = await pool.query(
        `INSERT INTO authjs_sessions ("userId", expires, "sessionToken")
         VALUES ($1, $2, $3)
         RETURNING id, "sessionToken", "userId", expires`,
        [userId, expires, sessionToken],
      );
      return result.rows[0] as AdapterSession;
    },

    async getSessionAndUser(sessionToken) {
      if (sessionToken === undefined) return null;
      const sessResult = await pool.query(
        `SELECT * FROM authjs_sessions WHERE "sessionToken" = $1`,
        [sessionToken],
      );
      if (sessResult.rowCount === 0) return null;
      const session = sessResult.rows[0] as AdapterSession;
      const userResult = await pool.query(`SELECT * FROM authjs_users WHERE id = $1`, [
        session.userId,
      ]);
      if (userResult.rowCount === 0) return null;
      return {
        session,
        user: userResult.rows[0] as AdapterUser,
      };
    },

    async updateSession(session) {
      const { sessionToken } = session;
      const result = await pool.query(
        `SELECT * FROM authjs_sessions WHERE "sessionToken" = $1`,
        [sessionToken],
      );
      if (result.rowCount === 0) return null;
      const original = result.rows[0];
      const updated = { ...original, ...session };
      await pool.query(
        `UPDATE authjs_sessions SET expires = $2 WHERE "sessionToken" = $1`,
        [updated.sessionToken, updated.expires],
      );
      return updated as AdapterSession;
    },

    async deleteSession(sessionToken) {
      await pool.query(`DELETE FROM authjs_sessions WHERE "sessionToken" = $1`, [sessionToken]);
    },

    async unlinkAccount({ provider, providerAccountId }) {
      await pool.query(
        `DELETE FROM authjs_accounts WHERE "providerAccountId" = $1 AND provider = $2`,
        [providerAccountId, provider],
      );
    },

    async deleteUser(userId) {
      await pool.query(`DELETE FROM authjs_users WHERE id = $1`, [userId]);
      await pool.query(`DELETE FROM authjs_sessions WHERE "userId" = $1`, [userId]);
      await pool.query(`DELETE FROM authjs_accounts WHERE "userId" = $1`, [userId]);
    },
  };
}
