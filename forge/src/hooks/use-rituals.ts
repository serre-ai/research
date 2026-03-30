import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { Ritual, RitualType } from '@/lib/ritual-types';

interface RitualFilters {
  type?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export function useRituals(filters?: RitualFilters) {
  const params: Record<string, string> = {};
  if (filters?.type) params.type = filters.type;
  if (filters?.status) params.status = filters.status;
  if (filters?.limit) params.limit = String(filters.limit);
  if (filters?.offset) params.offset = String(filters.offset);

  return useQuery({
    queryKey: ['rituals', params],
    queryFn: () => apiFetch<Ritual[]>('/rituals', { params }),
    staleTime: 30_000,
  });
}

export function useUpcomingRituals() {
  return useQuery({
    queryKey: ['rituals', 'upcoming'],
    queryFn: () => apiFetch<Ritual[]>('/rituals/upcoming'),
    staleTime: 30_000,
  });
}

export function useRitualHistory(type?: RitualType) {
  const params: Record<string, string> = {};
  if (type) params.type = type;

  return useQuery({
    queryKey: ['rituals', 'history', params],
    queryFn: () => apiFetch<Ritual[]>('/rituals/history', { params }),
    staleTime: 60_000,
  });
}

export function useRitual(id: number | null) {
  return useQuery({
    queryKey: ['rituals', id],
    queryFn: () => apiFetch<Ritual>(`/rituals/${id}`),
    staleTime: 30_000,
    enabled: id !== null,
  });
}

export function useStartRitual() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) =>
      apiFetch<Ritual>(`/rituals/${id}/start`, { method: 'PATCH' }),
    onSuccess: () => {
      toast.success('Ritual started');
      queryClient.invalidateQueries({ queryKey: ['rituals'] });
    },
    onError: (error) => {
      toast.error(`Failed to start ritual: ${error.message}`);
    },
  });
}

export function useCompleteRitual() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, outcome }: { id: number; outcome?: string }) =>
      apiFetch<Ritual>(`/rituals/${id}/complete`, {
        method: 'PATCH',
        body: JSON.stringify({ outcome }),
      }),
    onSuccess: () => {
      toast.success('Ritual completed');
      queryClient.invalidateQueries({ queryKey: ['rituals'] });
    },
    onError: (error) => {
      toast.error(`Failed to complete ritual: ${error.message}`);
    },
  });
}
