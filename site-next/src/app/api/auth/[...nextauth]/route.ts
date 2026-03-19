import type { NextRequest } from 'next/server';
import { handlers } from '@/lib/auth';

const originalGET = handlers.GET;
const originalPOST = handlers.POST;

export async function GET(request: NextRequest) {
  console.log('[auth-debug] GET url:', request.url, 'nextUrl:', request.nextUrl.pathname);
  return originalGET(request);
}

export async function POST(request: NextRequest) {
  console.log('[auth-debug] POST url:', request.url, 'nextUrl:', request.nextUrl.pathname);
  return originalPOST(request);
}
