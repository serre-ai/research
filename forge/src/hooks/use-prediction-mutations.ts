import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { Prediction } from '@/lib/collective-types';

interface CreatePredictionRequest {
  author: string;
  claim: string;
  probability: number;
  category?: string;
  project?: string;
}

interface ResolvePredictionRequest {
  outcome: boolean;
  resolved_by: string;
  resolution_note?: string;
}

export function useCreatePrediction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: CreatePredictionRequest) =>
      apiFetch<Prediction>('/predictions', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Prediction created');
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
    },
    onError: (error) => {
      toast.error(`Failed to create prediction: ${error.message}`);
    },
  });
}

export function usePrediction(id: string | null) {
  return useQuery({
    queryKey: ['predictions', id],
    queryFn: () => apiFetch<Prediction>(`/predictions/${id}`),
    staleTime: 30_000,
    enabled: !!id,
  });
}

export function useResolvePrediction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...request }: ResolvePredictionRequest & { id: string }) =>
      apiFetch<Prediction>(`/predictions/${id}/resolve`, {
        method: 'PATCH',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Prediction resolved');
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
    },
    onError: (error) => {
      toast.error(`Failed to resolve prediction: ${error.message}`);
    },
  });
}
