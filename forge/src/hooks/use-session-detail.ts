import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { Session } from '@/lib/types';

interface TranscriptData {
  lines: string[];
  total: number;
  offset: number;
  limit: number;
}

export function useSessionDetail(sessionId: string) {
  return useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => apiFetch<Session>(`/sessions/${sessionId}`),
    staleTime: 60_000,
    enabled: !!sessionId,
  });
}

export function useTranscript(sessionId: string, offset = 0, limit = 100) {
  return useQuery({
    queryKey: ['transcript', sessionId, offset, limit],
    queryFn: () =>
      apiFetch<TranscriptData>(`/sessions/${sessionId}/transcript`, {
        params: { offset: String(offset), limit: String(limit) },
      }),
    staleTime: 60_000,
    enabled: !!sessionId,
  });
}
