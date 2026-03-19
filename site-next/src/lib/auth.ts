import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';
import { Pool } from 'pg';
import AuthjsAdapter from '@/lib/auth-adapter';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Only these GitHub usernames can sign in (comma-separated).
// If empty / unset, all GitHub users are allowed.
const ALLOWED_USERS = new Set(
  (process.env.AUTH_ALLOWED_USERS ?? '')
    .split(',')
    .map((u) => u.trim())
    .filter(Boolean),
);

export const { handlers, auth, signIn, signOut } = NextAuth({
  debug: true,
  adapter: AuthjsAdapter(pool),
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID!,
      clientSecret: process.env.AUTH_GITHUB_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ profile }) {
      if (ALLOWED_USERS.size === 0) return true;
      return ALLOWED_USERS.has(profile?.login as string);
    },
    async session({ session, user }) {
      if (session.user) {
        session.user.id = user.id;
      }
      return session;
    },
  },
  pages: {
    signIn: '/sign-in',
  },
  trustHost: true,
});
