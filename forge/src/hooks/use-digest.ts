import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { Digest, CreateDigestRequest } from '@/lib/digest-types';

export function useDigestDates() {
  return useQuery({
    queryKey: ['digest', 'dates'],
    queryFn: () => apiFetch<string[]>('/memory/digest'),
    staleTime: 60_000,
  });
}

export function useLatestDigest() {
  return useQuery({
    queryKey: ['digest', 'latest'],
    queryFn: () => apiFetch<Digest>('/memory/digest/latest'),
    staleTime: 30_000,
  });
}

export function useDigestByDate(date: string) {
  return useQuery({
    queryKey: ['digest', date],
    queryFn: () => apiFetch<Digest>(`/memory/digest/${date}`),
    staleTime: 120_000,
    enabled: !!date,
  });
}

export function useSaveDigest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateDigestRequest) =>
      apiFetch<Digest>('/memory/digest', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Digest saved');
      queryClient.invalidateQueries({ queryKey: ['digest'] });
    },
    onError: (error) => {
      toast.error(`Failed to save digest: ${error.message}`);
    },
  });
}
