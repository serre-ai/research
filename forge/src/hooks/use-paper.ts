import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { PaperBuildStatus, PaperBuildRequest } from '@/lib/paper-types';

export function usePaperStatus() {
  return useQuery({
    queryKey: ['paper', 'status'],
    queryFn: () => apiFetch<PaperBuildStatus>('/paper/status'),
    staleTime: 10_000,
    refetchInterval: (query) =>
      query.state.data?.status === 'running' ? 5_000 : false,
  });
}

export function usePaperLog() {
  return useQuery({
    queryKey: ['paper', 'log'],
    queryFn: () => apiFetch<string>('/paper/log'),
    staleTime: 10_000,
  });
}

export function usePaperBuild() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PaperBuildRequest) =>
      apiFetch<PaperBuildStatus>('/paper/build', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Paper build started');
      queryClient.invalidateQueries({ queryKey: ['paper'] });
    },
    onError: (error) => {
      toast.error(`Build failed: ${error.message}`);
    },
  });
}
