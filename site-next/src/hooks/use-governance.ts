import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type {
  Proposal,
  ProposalDetail,
  GovernanceTally,
  CreateProposalRequest,
  CastVoteRequest,
} from '@/lib/governance-types';

interface ProposalFilters {
  status?: string;
  type?: string;
  limit?: number;
  offset?: number;
}

export function useGovernanceProposals(filters?: ProposalFilters) {
  const params: Record<string, string> = {};
  if (filters?.status) params.status = filters.status;
  if (filters?.type) params.type = filters.type;
  if (filters?.limit) params.limit = String(filters.limit);
  if (filters?.offset) params.offset = String(filters.offset);

  return useQuery({
    queryKey: ['governance', params],
    queryFn: () => apiFetch<Proposal[]>('/governance', { params }),
    staleTime: 30_000,
  });
}

export function useGovernanceProposal(id: number | null) {
  return useQuery({
    queryKey: ['governance', id],
    queryFn: () => apiFetch<ProposalDetail>(`/governance/${id}`),
    staleTime: 15_000,
    enabled: id !== null,
  });
}

export function useGovernanceTally(id: number | null) {
  return useQuery({
    queryKey: ['governance', id, 'tally'],
    queryFn: () => apiFetch<GovernanceTally>(`/governance/${id}/tally`),
    staleTime: 15_000,
    enabled: id !== null,
  });
}

export function useCreateProposal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateProposalRequest) =>
      apiFetch<Proposal>('/governance', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Proposal created');
      queryClient.invalidateQueries({ queryKey: ['governance'] });
    },
    onError: (error) => {
      toast.error(`Failed to create proposal: ${error.message}`);
    },
  });
}

export function useCastVote(proposalId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CastVoteRequest) =>
      apiFetch(`/governance/${proposalId}/vote`, {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Vote cast');
      queryClient.invalidateQueries({ queryKey: ['governance'] });
    },
    onError: (error) => {
      toast.error(`Failed to cast vote: ${error.message}`);
    },
  });
}

export function useResolveProposal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      apiFetch(`/governance/${id}/resolve`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    onSuccess: () => {
      toast.success('Proposal resolved');
      queryClient.invalidateQueries({ queryKey: ['governance'] });
    },
    onError: (error) => {
      toast.error(`Failed to resolve proposal: ${error.message}`);
    },
  });
}
