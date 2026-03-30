import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type {
  ForumThread,
  ThreadDetail,
  ForumStats,
  AgentState,
  AgentGraph,
  Prediction,
  CalibrationData,
  CalibrationLeaderboardEntry,
  CollectiveHealth,
  DomainEvent,
} from '@/lib/collective-types';

// Forum

interface ThreadFilters {
  status?: string;
  type?: string;
  author?: string;
  limit?: number;
  offset?: number;
}

export function useForumThreads(filters?: ThreadFilters) {
  const params: Record<string, string> = {};
  if (filters?.status) params.status = filters.status;
  if (filters?.type) params.type = filters.type;
  if (filters?.author) params.author = filters.author;
  if (filters?.limit) params.limit = String(filters.limit);
  if (filters?.offset) params.offset = String(filters.offset);

  return useQuery({
    queryKey: ['forum', 'threads', params],
    queryFn: () => apiFetch<ForumThread[]>('/forum/threads', { params }),
    staleTime: 30_000,
  });
}

export function useForumThread(threadId: string | null) {
  return useQuery({
    queryKey: ['forum', 'thread', threadId],
    queryFn: () => apiFetch<ThreadDetail>(`/forum/threads/${threadId}`),
    staleTime: 15_000,
    enabled: !!threadId,
  });
}

export function useForumStats() {
  return useQuery({
    queryKey: ['forum', 'stats'],
    queryFn: () => apiFetch<ForumStats>('/forum/stats'),
    staleTime: 60_000,
  });
}

// Agents

export function useAgentState(agentId: string) {
  return useQuery({
    queryKey: ['agents', agentId, 'state'],
    queryFn: () => apiFetch<AgentState>(`/agents/${agentId}/state`),
    staleTime: 60_000,
    enabled: !!agentId,
  });
}

export function useAgentGraph() {
  return useQuery({
    queryKey: ['agents', 'graph'],
    queryFn: () => apiFetch<AgentGraph>('/agents/graph'),
    staleTime: 120_000,
  });
}

// Predictions

export function useAgentPredictions(agentId: string) {
  return useQuery({
    queryKey: ['predictions', agentId],
    queryFn: () => apiFetch<Prediction[]>('/predictions', { params: { author: agentId } }),
    staleTime: 30_000,
    enabled: !!agentId,
  });
}

export function useCalibration(agentId: string) {
  return useQuery({
    queryKey: ['predictions', 'calibration', agentId],
    queryFn: () => apiFetch<CalibrationData>(`/predictions/calibration/${agentId}`),
    staleTime: 300_000,
    enabled: !!agentId,
  });
}

export function useCalibrationLeaderboard() {
  return useQuery({
    queryKey: ['predictions', 'leaderboard'],
    queryFn: () => apiFetch<CalibrationLeaderboardEntry[]>('/predictions/leaderboard'),
    staleTime: 300_000,
  });
}

// Collective

export function useCollectiveHealth() {
  return useQuery({
    queryKey: ['collective', 'health'],
    queryFn: () => apiFetch<CollectiveHealth>('/collective/health'),
    staleTime: 30_000,
  });
}

export function useCollectiveEvents(limit = 20) {
  return useQuery({
    queryKey: ['events', limit],
    queryFn: () => apiFetch<DomainEvent[]>('/events', { params: { limit: String(limit) } }),
    staleTime: 15_000,
  });
}
