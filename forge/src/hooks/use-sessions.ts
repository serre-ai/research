import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { Session } from '@/lib/types';

export function useSessions(projectId: string) {
  return useQuery({
    queryKey: ['sessions', projectId],
    queryFn: () => apiFetch<Session[]>(`/projects/${projectId}/sessions`),
    staleTime: 30_000,
    enabled: !!projectId,
  });
}
