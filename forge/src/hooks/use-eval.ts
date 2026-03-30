import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { EvalData, EvalRun } from '@/lib/types';

interface RawEvalRun {
  run_id: string;
  model: string;
  task: string;
  condition: string;
  instance_count: number;
  accuracy: number;
  started_at: string;
  completed_at?: string;
  status?: string;
  total_expected?: number;
  metadata?: Record<string, unknown>;
}

interface RawEvalResponse {
  progress: EvalData['progress'];
  byDifficulty: EvalData['byDifficulty'];
  runs: RawEvalRun[];
}

function transformRun(raw: RawEvalRun): EvalRun {
  return {
    id: raw.run_id,
    model: raw.model,
    task: raw.task,
    condition: raw.condition,
    instances: raw.instance_count ?? 0,
    accuracy: raw.accuracy ?? 0,
    created_at: raw.started_at,
  };
}

export function useEvalData(projectId: string) {
  return useQuery({
    queryKey: ['eval', projectId],
    queryFn: async (): Promise<EvalData> => {
      const raw = await apiFetch<RawEvalResponse>(
        `/projects/${projectId}/eval`,
      );
      const runs = (raw.runs ?? []).map(transformRun);
      const progress = raw.progress ?? [];

      // Compute summary from progress rows
      const completed = progress.reduce(
        (sum, p) => sum + (p.completed_count ?? 0),
        0,
      );
      const total = runs.length;
      const failed = runs.filter((r) => r.accuracy === 0 && r.instances > 0).length;

      return {
        project_id: projectId,
        runs,
        progress,
        byDifficulty: raw.byDifficulty ?? [],
        summary: { total, completed, failed },
      };
    },
    staleTime: 30_000,
    enabled: !!projectId,
  });
}

export function useEvalStatus() {
  return useQuery({
    queryKey: ['eval', 'status'],
    queryFn: () =>
      apiFetch<{ running: boolean; queued: number; completed: number }>(
        '/eval/status',
      ),
    staleTime: 10_000,
  });
}
