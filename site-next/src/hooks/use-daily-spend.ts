import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';

interface DailySpend {
  days: Array<{ date: string; total_usd: number; event_count: number }>;
}

export function useDailySpend() {
  return useQuery({
    queryKey: ['budget', 'daily-history'],
    queryFn: () => apiFetch<DailySpend>('/budget/daily-history'),
    staleTime: 60_000,
  });
}
