import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

export async function GET() {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Return absolute WS URL to VPS — browser connects directly since
  // Vercel can't hold long-lived WebSocket connections.
  const vpsUrl = process.env.VPS_API_URL ?? 'http://localhost:3001';
  const wsBase = vpsUrl.replace(/^http/, 'ws');
  return NextResponse.json({
    url: `${wsBase}/api/ws?api_key=${process.env.VPS_API_KEY ?? ''}`,
  });
}
