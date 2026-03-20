import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { Trigger } from '@/lib/trigger-types';

export function usePendingTriggers() {
  return useQuery({
    queryKey: ['triggers', 'pending'],
    queryFn: () => apiFetch<Trigger[]>('/triggers/pending'),
    staleTime: 60_000,
  });
}

export function useAckTrigger() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) =>
      apiFetch(`/triggers/${id}/ack`, { method: 'POST' }),
    onSuccess: () => {
      toast.success('Trigger acknowledged');
      queryClient.invalidateQueries({ queryKey: ['triggers'] });
    },
    onError: (error) => {
      toast.error(`Failed to acknowledge: ${error.message}`);
    },
  });
}
