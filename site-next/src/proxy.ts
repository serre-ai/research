import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { auth } from '@/lib/auth';

/**
 * Next.js 16 proxy (replaces middleware.ts).
 *
 * Wraps Auth.js's `auth()` to keep sessions alive on every matched request,
 * and redirects unauthenticated users away from protected (app) routes.
 */

const PROTECTED_PREFIXES = ['/dashboard', '/projects', '/collective', '/settings'];

function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

// Auth.js v5's `auth()` with a callback returns NextMiddleware.
// We re-export the result as `proxy` for the Next.js 16 convention.
const authProxy = auth((req) => {
  const isLoggedIn = !!req.auth;
  const { pathname } = req.nextUrl;

  if (isProtectedPath(pathname) && !isLoggedIn) {
    const signInUrl = req.nextUrl.clone();
    signInUrl.pathname = '/sign-in';
    signInUrl.searchParams.set('callbackUrl', req.nextUrl.href);
    return NextResponse.redirect(signInUrl);
  }

  return NextResponse.next();
});

// Next.js 16 expects a named `proxy` export (not `middleware`).
export function proxy(request: NextRequest, event: unknown) {
  return authProxy(request, event as Parameters<typeof authProxy>[1]);
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|sign-in).*)'],
};
