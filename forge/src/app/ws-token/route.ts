import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

export async function GET() {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // The API key is injected server-side — only authenticated users get it.
  // The WebSocket connection goes browser → nginx → Express, so the key
  // must be in the URL. This is acceptable since the site is auth-gated.
  return NextResponse.json({
    url: `/api/ws?api_key=${process.env.VPS_API_KEY ?? ''}`,
  });
}
