import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { BacklogTicket, CreateTicketRequest, UpdateTicketRequest } from '@/lib/backlog-types';

interface TicketFilters {
  status?: string;
  priority?: string;
  category?: string;
}

export function useBacklog(filters?: TicketFilters) {
  const params: Record<string, string> = {};
  if (filters?.status) params.status = filters.status;
  if (filters?.priority) params.priority = filters.priority;
  if (filters?.category) params.category = filters.category;

  return useQuery({
    queryKey: ['backlog', params],
    queryFn: () => apiFetch<BacklogTicket[]>('/backlog', { params }),
    staleTime: 30_000,
  });
}

export function useBacklogTicket(id: string | null) {
  return useQuery({
    queryKey: ['backlog', id],
    queryFn: () => apiFetch<BacklogTicket>(`/backlog/${id}`),
    staleTime: 30_000,
    enabled: id !== null,
  });
}

export function useCreateTicket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateTicketRequest) =>
      apiFetch<BacklogTicket>('/backlog', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Ticket created');
      queryClient.invalidateQueries({ queryKey: ['backlog'] });
    },
    onError: (error) => {
      toast.error(`Failed to create ticket: ${error.message}`);
    },
  });
}

export function useUpdateTicket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...updates }: UpdateTicketRequest & { id: string }) =>
      apiFetch<BacklogTicket>(`/backlog/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      toast.success('Ticket updated');
      queryClient.invalidateQueries({ queryKey: ['backlog'] });
    },
    onError: (error) => {
      toast.error(`Failed to update ticket: ${error.message}`);
    },
  });
}
