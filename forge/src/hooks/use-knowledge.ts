import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type {
  Claim,
  KnowledgeSubgraph,
  Contradiction,
  UnsupportedClaim,
  EvidenceChain,
  KnowledgeStats,
} from '@/lib/knowledge-types';

interface ClaimFilters {
  project?: string;
  type?: string;
  limit?: number;
  offset?: number;
}

export function useKnowledgeClaims(filters?: ClaimFilters) {
  const params: Record<string, string> = {};
  if (filters?.project) params.project = filters.project;
  if (filters?.type) params.type = filters.type;
  if (filters?.limit) params.limit = String(filters.limit);
  if (filters?.offset) params.offset = String(filters.offset);

  return useQuery({
    queryKey: ['knowledge', 'claims', params],
    queryFn: () => apiFetch<Claim[]>('/knowledge/claims', { params }),
    staleTime: 30_000,
  });
}

export function useKnowledgeClaim(id: string | null) {
  return useQuery({
    queryKey: ['knowledge', 'claim', id],
    queryFn: () => apiFetch<Claim>(`/knowledge/claims/${id}`),
    staleTime: 30_000,
    enabled: !!id,
  });
}

export function useKnowledgeSubgraph(id: string | null, depth = 2) {
  return useQuery({
    queryKey: ['knowledge', 'subgraph', id, depth],
    queryFn: () =>
      apiFetch<KnowledgeSubgraph>(`/knowledge/subgraph/${id}`, {
        params: { depth: String(depth) },
      }),
    staleTime: 60_000,
    enabled: !!id,
  });
}

export function useKnowledgeContradictions(project?: string) {
  const params: Record<string, string> = {};
  if (project) params.project = project;

  return useQuery({
    queryKey: ['knowledge', 'contradictions', project],
    queryFn: () => apiFetch<Contradiction[]>('/knowledge/contradictions', { params }),
    staleTime: 60_000,
  });
}

export function useKnowledgeUnsupported(project?: string) {
  const params: Record<string, string> = {};
  if (project) params.project = project;

  return useQuery({
    queryKey: ['knowledge', 'unsupported', project],
    queryFn: () => apiFetch<UnsupportedClaim[]>('/knowledge/unsupported', { params }),
    staleTime: 60_000,
  });
}

export function useKnowledgeEvidence(id: string | null) {
  return useQuery({
    queryKey: ['knowledge', 'evidence', id],
    queryFn: () => apiFetch<EvidenceChain>(`/knowledge/evidence/${id}`),
    staleTime: 120_000,
    enabled: !!id,
  });
}

export function useKnowledgeStats() {
  return useQuery({
    queryKey: ['knowledge', 'stats'],
    queryFn: () => apiFetch<KnowledgeStats>('/knowledge/stats'),
    staleTime: 120_000,
  });
}
