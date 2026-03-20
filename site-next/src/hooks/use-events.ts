import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { DomainEvent } from '@/lib/collective-types';
import type { DeadLetter } from '@/lib/event-types';

interface EventFilters {
  type?: string;
  limit?: number;
  since?: string;
}

export function useEvents(filters?: EventFilters) {
  const params: Record<string, string> = {};
  if (filters?.type) params.type = filters.type;
  if (filters?.limit) params.limit = String(filters.limit);
  if (filters?.since) params.since = filters.since;

  return useQuery({
    queryKey: ['events', 'filtered', params],
    queryFn: () => apiFetch<DomainEvent[]>('/events', { params }),
    staleTime: 15_000,
  });
}

export function useDeadLetters() {
  return useQuery({
    queryKey: ['events', 'dead-letters'],
    queryFn: () => apiFetch<DeadLetter[]>('/events/dead-letters'),
    staleTime: 30_000,
  });
}

export function useRetryDeadLetter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) =>
      apiFetch<void>(`/events/dead-letters/${id}/retry`, { method: 'POST' }),
    onSuccess: () => {
      toast.success('Dead letter retried');
      queryClient.invalidateQueries({ queryKey: ['events', 'dead-letters'] });
    },
    onError: (error) => {
      toast.error(`Retry failed: ${error.message}`);
    },
  });
}

interface EmitEventRequest {
  event_type: string;
  agent?: string;
  payload: Record<string, unknown>;
}

export function useEmitEvent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: EmitEventRequest) =>
      apiFetch<DomainEvent>('/events', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Event emitted');
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
    onError: (error) => {
      toast.error(`Failed to emit event: ${error.message}`);
    },
  });
}
