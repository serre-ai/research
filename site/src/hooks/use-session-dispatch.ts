import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';

interface DispatchRequest {
  project: string;
  agent_type: string;
  reason: string;
  triggered_by: string;
  priority?: string;
}

interface DispatchQueueResponse {
  queue: unknown[];
  recent: unknown[];
}

export function useDispatchQueue() {
  return useQuery({
    queryKey: ['sessions', 'dispatch', 'queue'],
    queryFn: () => apiFetch<DispatchQueueResponse>('/sessions/dispatch/queue'),
    staleTime: 15_000,
  });
}

export function useDispatchSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: DispatchRequest) =>
      apiFetch('/sessions/dispatch', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Session dispatched');
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
    onError: (error) => {
      toast.error(`Dispatch failed: ${error.message}`);
    },
  });
}
