import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { HealthStatus, DaemonHealth, HealthApiResponse, DaemonApiResponse } from '@/lib/types';

function transformHealth(raw: HealthApiResponse): HealthStatus {
  const usedMb = raw.memory.total_mb - raw.memory.free_mb;
  return {
    status: raw.status,
    uptime: raw.uptime_s,
    memory: {
      used: usedMb,
      total: raw.memory.total_mb,
      percentage: raw.memory.percent_used,
    },
    database: {
      connected: raw.database === 'connected',
      latency_ms: 0, // not provided by API
    },
  };
}

function transformDaemon(raw: DaemonApiResponse): DaemonHealth {
  return {
    status: raw.running ? 'running' : 'stopped',
    running: raw.running,
    last_session: undefined, // not provided by API
    interval_minutes: 60,
    max_concurrent: 1,
  };
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const raw = await apiFetch<HealthApiResponse>('/health');
      return transformHealth(raw);
    },
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function useDaemonHealth() {
  return useQuery({
    queryKey: ['daemon', 'health'],
    queryFn: async () => {
      const raw = await apiFetch<DaemonApiResponse>('/daemon/health');
      return transformDaemon(raw);
    },
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}
