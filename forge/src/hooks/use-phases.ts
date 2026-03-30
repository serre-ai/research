import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';

interface PhaseData {
  current_phase: string;
  phases: Array<{ name: string; status: 'complete' | 'active' | 'pending' }>;
}

export function usePhases(projectId: string) {
  return useQuery({
    queryKey: ['phases', projectId],
    queryFn: () => apiFetch<PhaseData>(`/projects/${projectId}/phases`),
    staleTime: 60_000,
    enabled: !!projectId,
  });
}
