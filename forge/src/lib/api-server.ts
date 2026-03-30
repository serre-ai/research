import { ApiError } from './api';

type FetchOptions = RequestInit & {
  params?: Record<string, string>;
};

const VPS_API_URL = process.env.VPS_API_URL ?? 'http://localhost:3001';
const VPS_API_KEY = process.env.VPS_API_KEY ?? '';

/**
 * Server-side fetch to Express API. Injects API key automatically.
 * Use in Server Components, Server Actions, and API routes.
 */
export async function serverFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { params, ...init } = options;

  let url = `${VPS_API_URL}/api${path}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  const response = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-Api-Key': VPS_API_KEY,
      ...init.headers,
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, body);
  }

  return response.json() as Promise<T>;
}
