import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';
import { Pool } from 'pg';
import AuthjsAdapter from '@/lib/auth-adapter';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Hard-coded owner allowlist — only these identities can sign in.
const ALLOWED_EMAILS = new Set(['oddurs@gmail.com']);
const ALLOWED_GITHUB_LOGINS = new Set(['oddurs']);

export const { handlers, auth, signIn, signOut } = NextAuth({
  debug: process.env.NODE_ENV !== 'production',
  adapter: AuthjsAdapter(pool),
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID!,
      clientSecret: process.env.AUTH_GITHUB_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ profile }) {
      const login = (profile?.login as string | undefined)?.toLowerCase();
      const email = (profile?.email as string | undefined)?.toLowerCase();
      return (
        (!!login && ALLOWED_GITHUB_LOGINS.has(login)) ||
        (!!email && ALLOWED_EMAILS.has(email))
      );
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
