import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { Decision } from '@/lib/types';

export function useDecisions(projectId: string) {
  return useQuery({
    queryKey: ['decisions', projectId],
    queryFn: () => apiFetch<Decision[]>(`/projects/${projectId}/decisions`),
    staleTime: 60_000,
    enabled: !!projectId,
  });
}
