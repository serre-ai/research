import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { HealthStatus, DaemonHealth } from '@/lib/types';

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiFetch<HealthStatus>('/health'),
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function useDaemonHealth() {
  return useQuery({
    queryKey: ['daemon', 'health'],
    queryFn: () => apiFetch<DaemonHealth>('/daemon/health'),
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}
