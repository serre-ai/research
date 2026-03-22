import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import type { ReactNode } from 'react';
import { useDailySpend } from '@/hooks/use-daily-spend';

vi.mock('@/lib/api', () => ({
  apiFetch: vi.fn(),
}));

import { apiFetch } from '@/lib/api';

const mockApiFetch = apiFetch as ReturnType<typeof vi.fn>;

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe('useDailySpend', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches from /budget/daily-history endpoint', async () => {
    mockApiFetch.mockResolvedValueOnce({ days: [] });

    renderHook(() => useDailySpend(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledWith('/budget/daily-history');
    });
  });

  it('returns the days array from the response', async () => {
    const mockDays = [
      { date: '2026-03-19', total_usd: 12.5, event_count: 45 },
      { date: '2026-03-20', total_usd: 8.3, event_count: 22 },
    ];
    mockApiFetch.mockResolvedValueOnce({ days: mockDays });

    const { result } = renderHook(() => useDailySpend(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data!.days).toEqual(mockDays);
    expect(result.current.data!.days).toHaveLength(2);
    expect(result.current.data!.days[0].date).toBe('2026-03-19');
    expect(result.current.data!.days[1].total_usd).toBe(8.3);
  });
});
