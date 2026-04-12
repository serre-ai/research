import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';

interface EvalJob {
  id: string;
  model: string;
  task: string;
  condition: string;
  project?: string;
  status: string;
  created_at: string;
}

interface EnqueueEvalJobRequest {
  model: string;
  task: string;
  condition: string;
  project?: string;
}

export function useEvalJobs(status?: string) {
  const params: Record<string, string> = {};
  if (status) params.status = status;

  return useQuery({
    queryKey: ['eval', 'jobs', params],
    queryFn: () => apiFetch<EvalJob[]>('/eval/jobs', { params }),
    staleTime: 15_000,
  });
}

export function useEnqueueEvalJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: EnqueueEvalJobRequest) =>
      apiFetch<EvalJob>('/eval/jobs', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Eval job enqueued');
      queryClient.invalidateQueries({ queryKey: ['eval'] });
    },
    onError: (error) => {
      toast.error(`Failed to enqueue job: ${error.message}`);
    },
  });
}

export function useCancelEvalJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiFetch<void>(`/eval/jobs/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      toast.success('Eval job cancelled');
      queryClient.invalidateQueries({ queryKey: ['eval'] });
    },
    onError: (error) => {
      toast.error(`Failed to cancel job: ${error.message}`);
    },
  });
}
