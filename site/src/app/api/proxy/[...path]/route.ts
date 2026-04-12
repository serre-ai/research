import { type NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

const VPS_API_URL = process.env.VPS_API_URL ?? 'http://localhost:3001';
const VPS_API_KEY = process.env.VPS_API_KEY ?? '';

async function proxyRequest(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
  method: string,
) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { path } = await params;
  const apiPath = `/api/${path.join('/')}`;
  const url = new URL(apiPath, VPS_API_URL);

  // Forward query params from the original request
  req.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.set(key, value);
  });

  const headers: Record<string, string> = {
    'X-Api-Key': VPS_API_KEY,
    'Content-Type': 'application/json',
  };

  const fetchInit: RequestInit = { method, headers };

  // Forward body for methods that support it
  if (method !== 'GET' && method !== 'HEAD') {
    const body = await req.json().catch(() => null);
    if (body !== null) {
      fetchInit.body = JSON.stringify(body);
    }
  }

  try {
    const response = await fetch(url.toString(), fetchInit);
    const data = await response.json().catch(() => null);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: 'Upstream API unavailable' },
      { status: 502 },
    );
  }
}

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  return proxyRequest(req, ctx, 'GET');
}

export async function POST(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  return proxyRequest(req, ctx, 'POST');
}

export async function PATCH(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  return proxyRequest(req, ctx, 'PATCH');
}

export async function PUT(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  return proxyRequest(req, ctx, 'PUT');
}

export async function DELETE(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  return proxyRequest(req, ctx, 'DELETE');
}
