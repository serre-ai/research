import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { EvalData } from '@/lib/types';

export function useEvalData(projectId: string) {
  return useQuery({
    queryKey: ['eval', projectId],
    queryFn: () => apiFetch<EvalData>(`/projects/${projectId}/eval`),
    staleTime: 30_000,
    enabled: !!projectId,
  });
}

export function useEvalStatus() {
  return useQuery({
    queryKey: ['eval', 'status'],
    queryFn: () =>
      apiFetch<{ running: boolean; queued: number; completed: number }>(
        '/eval/status',
      ),
    staleTime: 10_000,
  });
}
