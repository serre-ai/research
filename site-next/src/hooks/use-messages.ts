import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { Message, Mention, MessageStats, SendMessageRequest } from '@/lib/message-types';

interface InboxFilters {
  unread?: boolean;
  priority?: string;
  limit?: number;
  offset?: number;
}

export function useInbox(agent: string, filters?: InboxFilters) {
  const params: Record<string, string> = {};
  if (filters?.unread) params.unread = 'true';
  if (filters?.priority) params.priority = filters.priority;
  if (filters?.limit) params.limit = String(filters.limit);
  if (filters?.offset) params.offset = String(filters.offset);

  return useQuery({
    queryKey: ['messages', 'inbox', agent, params],
    queryFn: () => apiFetch<Message[]>(`/messages/inbox/${agent}`, { params }),
    staleTime: 15_000,
    enabled: !!agent,
  });
}

export function useMentions(agent: string) {
  return useQuery({
    queryKey: ['messages', 'mentions', agent],
    queryFn: () => apiFetch<Mention[]>(`/messages/mentions/${agent}`),
    staleTime: 30_000,
    enabled: !!agent,
  });
}

export function useMessageStats(agent: string) {
  return useQuery({
    queryKey: ['messages', 'stats', agent],
    queryFn: () => apiFetch<MessageStats>(`/messages/stats/${agent}`),
    staleTime: 30_000,
    enabled: !!agent,
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: SendMessageRequest) =>
      apiFetch<Message>('/messages/send', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Message sent');
      queryClient.invalidateQueries({ queryKey: ['messages'] });
    },
    onError: (error) => {
      toast.error(`Failed to send message: ${error.message}`);
    },
  });
}

export function useMarkRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) =>
      apiFetch(`/messages/${id}/read`, { method: 'PATCH' }),
    onSuccess: () => {
      toast.success('Marked as read');
      queryClient.invalidateQueries({ queryKey: ['messages'] });
    },
    onError: (error) => {
      toast.error(`Failed to mark as read: ${error.message}`);
    },
  });
}
