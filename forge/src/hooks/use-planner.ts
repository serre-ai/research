import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { PlannerState, ProjectInsight, PlannerEvaluation } from '@/lib/planner-types';

export function usePlannerStatus() {
  return useQuery({
    queryKey: ['planner', 'status'],
    queryFn: () => apiFetch<PlannerState>('/planner/status'),
    staleTime: 30_000,
  });
}

export function usePlannerInsights(project: string) {
  return useQuery({
    queryKey: ['planner', 'insights', project],
    queryFn: () => apiFetch<ProjectInsight>(`/planner/insights/${project}`),
    staleTime: 30_000,
    enabled: !!project,
  });
}

export function usePlannerEvaluations() {
  return useQuery({
    queryKey: ['planner', 'evaluations'],
    queryFn: () => apiFetch<PlannerEvaluation[]>('/planner/evaluations'),
    staleTime: 60_000,
  });
}
