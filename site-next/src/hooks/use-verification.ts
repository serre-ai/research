import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { VerificationReport, VerificationSummary } from '@/lib/verification-types';

export function useVerificationReport(projectId: string) {
  return useQuery({
    queryKey: ['verification', projectId, 'latest'],
    queryFn: () => apiFetch<VerificationReport>(`/projects/${projectId}/verification`),
    staleTime: 60_000,
    enabled: !!projectId,
    retry: false,
  });
}

export function useVerificationHistory(projectId: string) {
  return useQuery({
    queryKey: ['verification', projectId, 'history'],
    queryFn: () => apiFetch<VerificationReport[]>(`/projects/${projectId}/verification/history`),
    staleTime: 60_000,
    enabled: !!projectId,
    retry: false,
  });
}

export function useTriggerVerification(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      apiFetch<VerificationSummary>(`/projects/${projectId}/verification`, {
        method: 'POST',
      }),
    onSuccess: () => {
      toast.success('Verification run complete');
      queryClient.invalidateQueries({ queryKey: ['verification', projectId] });
    },
    onError: (error) => {
      toast.error(`Verification failed: ${error.message}`);
    },
  });
}
