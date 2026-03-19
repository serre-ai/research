import { handlers } from '@/lib/auth';

const originalGET = handlers.GET;
const originalPOST = handlers.POST;

export async function GET(request: Request, context: unknown) {
  console.log('[auth-debug] GET', request.url);
  return originalGET(request, context as Parameters<typeof originalGET>[1]);
}

export async function POST(request: Request, context: unknown) {
  console.log('[auth-debug] POST', request.url);
  return originalPOST(request, context as Parameters<typeof originalPOST>[1]);
}
