'use client';

import { TuiBadge } from '@/components/tui';
import { useCancelEvalJob } from '@/hooks/use-eval-jobs';

interface EvalJob {
  id: string;
  model: string;
  task: string;
  condition: string;
  project?: string;
  status: string;
  created_at: string;
}

function statusColor(status: string): 'ok' | 'warn' | 'error' | 'muted' {
  switch (status) {
    case 'completed': return 'ok';
    case 'running': return 'warn';
    case 'failed':
    case 'cancelled': return 'error';
    default: return 'muted';
  }
}

export function EvalJobCard({ job }: { job: EvalJob }) {
  const cancelJob = useCancelEvalJob();
  const cancellable = job.status === 'queued' || job.status === 'running';

  return (
    <div className="flex items-center justify-between gap-4 border-b border-border py-1.5 last:border-0 first:pt-0">
      <div className="flex items-center gap-2 min-w-0">
        <TuiBadge color={statusColor(job.status)}>{job.status}</TuiBadge>
        <span className="text-text-secondary truncate">{job.model}</span>
        <span className="text-text-muted">{job.task}</span>
        <TuiBadge color="accent">{job.condition}</TuiBadge>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <span className="text-text-muted">
          {new Date(job.created_at).toISOString().slice(0, 16).replace('T', ' ')}
        </span>
        {cancellable && (
          <button
            onClick={() => cancelJob.mutate(job.id)}
            disabled={cancelJob.isPending}
            className="text-text-muted hover:text-text-bright disabled:opacity-50"
          >
            [x]
          </button>
        )}
      </div>
    </div>
  );
}
