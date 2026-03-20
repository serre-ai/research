import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';

export interface QualityReport {
  project: string;
  score: number;
  checks: { name: string; passed: boolean; details?: string }[];
  generated_at: string;
}

export function useQuality(project: string) {
  return useQuery({
    queryKey: ['quality', project],
    queryFn: () => apiFetch<QualityReport>(`/quality/${project}`),
    staleTime: 120_000,
    enabled: !!project,
  });
}
