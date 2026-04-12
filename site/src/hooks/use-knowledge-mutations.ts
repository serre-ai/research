import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { Claim, Relation } from '@/lib/knowledge-types';

interface UpdateClaimRequest {
  statement?: string;
  type?: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
}

interface SearchQuery {
  query: string;
  project?: string;
  type?: string;
  limit?: number;
}

interface CreateRelationRequest {
  source_id: string;
  target_id: string;
  relation: string;
  strength?: number;
  evidence?: string;
}

interface UpdateConfidenceRequest {
  confidence: number;
  reason: string;
  changed_by?: string;
}

export function useUpdateClaim() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...request }: UpdateClaimRequest & { id: string }) =>
      apiFetch<Claim>(`/knowledge/claims/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Claim updated');
      queryClient.invalidateQueries({ queryKey: ['knowledge'] });
    },
    onError: (error) => {
      toast.error(`Failed to update claim: ${error.message}`);
    },
  });
}

export function useKnowledgeSearch() {
  return useMutation({
    mutationFn: (query: SearchQuery) =>
      apiFetch<Claim[]>('/knowledge/query', {
        method: 'POST',
        body: JSON.stringify(query),
      }),
  });
}

export function useCreateRelation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: CreateRelationRequest) =>
      apiFetch<Relation>('/knowledge/relations', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Relation created');
      queryClient.invalidateQueries({ queryKey: ['knowledge'] });
    },
    onError: (error) => {
      toast.error(`Failed to create relation: ${error.message}`);
    },
  });
}

export function useKnowledgeSnapshot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (project: string) =>
      apiFetch<void>(`/knowledge/snapshot/${project}`, { method: 'POST' }),
    onSuccess: () => {
      toast.success('Knowledge snapshot created');
      queryClient.invalidateQueries({ queryKey: ['knowledge'] });
    },
    onError: (error) => {
      toast.error(`Snapshot failed: ${error.message}`);
    },
  });
}

export function useUpdateConfidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...request }: UpdateConfidenceRequest & { id: string }) =>
      apiFetch<Claim>(`/knowledge/confidence/${id}`, {
        method: 'PUT',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Confidence updated');
      queryClient.invalidateQueries({ queryKey: ['knowledge'] });
    },
    onError: (error) => {
      toast.error(`Failed to update confidence: ${error.message}`);
    },
  });
}
