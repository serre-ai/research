'use client';

import { X } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function statusVariant(status: string): 'default' | 'success' | 'warning' | 'error' {
  switch (status) {
    case 'completed':
      return 'success';
    case 'running':
      return 'warning';
    case 'failed':
    case 'cancelled':
      return 'error';
    default:
      return 'default';
  }
}

export function EvalJobCard({ job }: { job: EvalJob }) {
  const cancelJob = useCancelEvalJob();
  const cancellable = job.status === 'queued' || job.status === 'running';

  return (
    <Card className="flex items-center justify-between gap-4 p-3">
      <div className="flex items-center gap-3 min-w-0">
        <Badge variant={statusVariant(job.status)}>{job.status}</Badge>
        <span className="font-mono text-xs text-text-secondary truncate">
          {job.model}
        </span>
        <span className="font-mono text-xs text-text-muted">
          {job.task}
        </span>
        <Badge variant="outline">{job.condition}</Badge>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <span className="font-mono text-[10px] text-text-muted whitespace-nowrap">
          {formatDate(job.created_at)}
        </span>
        {cancellable && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => cancelJob.mutate(job.id)}
            disabled={cancelJob.isPending}
            className="p-1"
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
    </Card>
  );
}
