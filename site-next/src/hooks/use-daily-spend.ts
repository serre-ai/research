import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { BudgetApiResponse } from '@/lib/types';

interface DailySpend {
  days: Array<{ date: string; total_usd: number }>;
}

export function useDailySpend() {
  return useQuery({
    queryKey: ['budget', 'daily-history'],
    queryFn: async (): Promise<DailySpend> => {
      // Daily history is embedded in the main budget response
      const raw = await apiFetch<BudgetApiResponse>('/budget');
      const days = (raw.burnRate?.daily_history ?? []).map((d) => ({
        date: d.day,
        total_usd: d.total,
      }));
      return { days };
    },
    staleTime: 60_000,
  });
}
