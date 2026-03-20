import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { AgentRelationship, LearningEntry } from '@/lib/collective-types';

interface UpdateAgentStateRequest {
  [key: string]: unknown;
}

interface UpdateRelationshipRequest {
  trust?: number;
  agreement_rate?: number;
  interaction_count?: number;
  dynamic?: string;
}

interface AddLearningRequest {
  lesson: string;
  source: string;
  category?: string;
}

export function useUpdateAgentState() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ agent, ...request }: UpdateAgentStateRequest & { agent: string }) =>
      apiFetch<void>(`/agents/${agent}/state`, {
        method: 'PATCH',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Agent state updated');
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
    onError: (error) => {
      toast.error(`Failed to update agent state: ${error.message}`);
    },
  });
}

export function useAgentRelationships(agent: string) {
  return useQuery({
    queryKey: ['agents', agent, 'relationships'],
    queryFn: () => apiFetch<AgentRelationship[]>(`/agents/${agent}/relationships`),
    staleTime: 60_000,
    enabled: !!agent,
  });
}

export function useUpdateRelationship() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      agent,
      other,
      ...request
    }: UpdateRelationshipRequest & { agent: string; other: string }) =>
      apiFetch<AgentRelationship>(`/agents/${agent}/relationships/${other}`, {
        method: 'PATCH',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Relationship updated');
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
    onError: (error) => {
      toast.error(`Failed to update relationship: ${error.message}`);
    },
  });
}

export function useAddLearning() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ agent, ...request }: AddLearningRequest & { agent: string }) =>
      apiFetch<LearningEntry>(`/agents/${agent}/learned`, {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Learning added');
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
    onError: (error) => {
      toast.error(`Failed to add learning: ${error.message}`);
    },
  });
}
