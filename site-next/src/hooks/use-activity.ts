import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { ActivityItem } from '@/lib/types';

export function useActivity(limit = 20) {
  return useQuery({
    queryKey: ['activity', limit],
    queryFn: () =>
      apiFetch<ActivityItem[]>('/activity/recent', {
        params: { limit: String(limit) },
      }),
    staleTime: 15_000,
  });
}
