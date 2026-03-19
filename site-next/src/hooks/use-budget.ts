import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { Budget } from '@/lib/types';

export function useBudget() {
  return useQuery({
    queryKey: ['budget'],
    queryFn: () => apiFetch<Budget>('/budget'),
    staleTime: 60_000,
  });
}
