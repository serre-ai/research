import { handlers } from '@/lib/auth';

const originalGET = handlers.GET;
const originalPOST = handlers.POST;

export async function GET(request: Request) {
  console.log('[auth-debug] GET', request.url, request.method);
  return originalGET(request);
}

export async function POST(request: Request) {
  console.log('[auth-debug] POST', request.url, request.method);
  return originalPOST(request);
}
