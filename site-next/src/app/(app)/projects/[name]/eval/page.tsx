'use client';

import { useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { FlaskConical } from 'lucide-react';
import { useEvalData, useEvalStatus } from '@/hooks';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { StatusDot } from '@/components/ui/status-dot';
import { EmptyState } from '@/components/ui/empty-state';
import { ConditionTabs } from '@/components/condition-tabs';
import { AccuracyHeatmap } from '@/components/accuracy-heatmap';

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function EvalPage() {
  const params = useParams();
  const name = params.name as string;

  const { data: evalData, isLoading } = useEvalData(name);
  const { data: evalStatus } = useEvalStatus();
  const [activeCondition, setActiveCondition] = useState('direct');

  const conditions = useMemo(() => {
    if (!evalData?.runs) return ['direct', 'cot', 'budget_cot'];
    const condSet = new Set(evalData.runs.map((r) => r.condition));
    const sorted = Array.from(condSet).sort();
    return sorted.length > 0 ? sorted : ['direct', 'cot', 'budget_cot'];
  }, [evalData]);

  // Ensure active condition is valid
  const validCondition = conditions.includes(activeCondition)
    ? activeCondition
    : conditions[0] ?? 'direct';

  const recentRuns = useMemo(() => {
    if (!evalData?.runs) return [];
    return [...evalData.runs]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 20);
  }, [evalData]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-7 w-48" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="font-mono text-lg font-semibold text-text-bright">
          Evaluation Results
        </h2>
        {evalStatus && (
          <div className="flex items-center gap-2">
            <StatusDot
              status={evalStatus.running ? 'ok' : 'idle'}
              pulse={evalStatus.running}
            />
            <span className="font-mono text-xs text-text-muted">
              {evalStatus.running
                ? `Running (${evalStatus.queued} queued)`
                : evalStatus.completed > 0
                  ? `${evalStatus.completed} completed`
                  : 'Idle'}
            </span>
          </div>
        )}
      </div>

      {!evalData || evalData.runs.length === 0 ? (
        <Card>
          <EmptyState
            icon={FlaskConical}
            message="No evaluation data"
            description="Evaluation results will appear here once eval runs are completed"
          />
        </Card>
      ) : (
        <>
          {/* Condition tabs */}
          <ConditionTabs
            conditions={conditions}
            active={validCondition}
            onChange={setActiveCondition}
          />

          {/* Accuracy heatmap */}
          <section>
            <Label className="mb-3 block">Accuracy (Model x Task)</Label>
            <Card padding={false} className="overflow-hidden">
              <AccuracyHeatmap
                runs={evalData.runs}
                condition={validCondition}
              />
            </Card>
          </section>

          {/* Run history */}
          <section>
            <Label className="mb-3 block">Recent Runs</Label>
            <Card padding={false}>
              <div className="overflow-x-auto">
                <table className="w-full font-mono text-xs">
                  <thead>
                    <tr className="border-b border-border text-left text-text-muted">
                      <th className="px-4 py-2 font-medium">Model</th>
                      <th className="px-4 py-2 font-medium">Task</th>
                      <th className="px-4 py-2 font-medium">Condition</th>
                      <th className="px-4 py-2 font-medium text-right">Accuracy</th>
                      <th className="px-4 py-2 font-medium text-right">Instances</th>
                      <th className="px-4 py-2 font-medium text-right">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {recentRuns.map((run) => (
                      <tr key={run.id} className="hover:bg-bg-elevated transition-colors">
                        <td className="px-4 py-2 text-text-secondary whitespace-nowrap">
                          {run.model}
                        </td>
                        <td className="px-4 py-2 text-text-secondary">
                          <Badge variant="outline">{run.task}</Badge>
                        </td>
                        <td className="px-4 py-2 text-text-muted">{run.condition}</td>
                        <td className="px-4 py-2 text-right tabular-nums text-text-bright">
                          {(run.accuracy * 100).toFixed(1)}%
                        </td>
                        <td className="px-4 py-2 text-right tabular-nums text-text-muted">
                          {run.instances.toLocaleString()}
                        </td>
                        <td className="px-4 py-2 text-right text-text-muted whitespace-nowrap">
                          {formatDate(run.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </section>
        </>
      )}
    </div>
  );
}
