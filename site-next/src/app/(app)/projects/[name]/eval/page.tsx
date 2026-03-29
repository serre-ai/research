'use client';

import { useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { TuiBox, TuiPanel, TuiList, TuiBadge, TuiStatusDot, TuiSkeleton } from '@/components/tui';
import { useEvalData, useEvalStatus } from '@/hooks';
import { useEvalJobs } from '@/hooks/use-eval-jobs';
import { ConditionTabs } from '@/components/condition-tabs';
import { AccuracyHeatmap } from '@/components/accuracy-heatmap';
import { EnqueueEvalDialog } from '@/components/enqueue-eval-dialog';
import { EvalJobCard } from '@/components/eval-job-card';

function formatDate(dateStr: string): string {
  return new Date(dateStr).toISOString().slice(0, 16).replace('T', ' ');
}

export default function EvalPage() {
  const params = useParams();
  const name = params.name as string;

  const { data: evalData, isLoading } = useEvalData(name);
  const { data: evalStatus } = useEvalStatus();
  const { data: evalJobs } = useEvalJobs();
  const [activeCondition, setActiveCondition] = useState('direct');

  const activeJobs = useMemo(() => {
    if (!evalJobs) return [];
    return evalJobs.filter((j) => j.status === 'queued' || j.status === 'running');
  }, [evalJobs]);

  const conditions = useMemo(() => {
    if (!evalData?.runs) return ['direct', 'cot', 'budget_cot'];
    const condSet = new Set(evalData.runs.map((r) => r.condition));
    const sorted = Array.from(condSet).sort();
    return sorted.length > 0 ? sorted : ['direct', 'cot', 'budget_cot'];
  }, [evalData]);

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
      <>
        <TuiBox title="EVAL STATUS" className="mb-3"><TuiSkeleton width={30} /></TuiBox>
        <TuiBox title="RESULTS" className="mb-3">
          <div className="space-y-1">
            {Array.from({ length: 4 }).map((_, i) => (
              <TuiSkeleton key={i} width={50} />
            ))}
          </div>
        </TuiBox>
      </>
    );
  }

  return (
    <>
      {/* Status bar */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          {evalStatus && (
            <span className="flex items-center gap-1">
              <TuiStatusDot status={evalStatus.running ? 'ok' : 'idle'} />
              <span className="text-text-secondary">
                {evalStatus.running
                  ? `running (${evalStatus.queued} queued)`
                  : evalStatus.completed > 0
                    ? `${evalStatus.completed} completed`
                    : 'idle'}
              </span>
            </span>
          )}
        </div>
        <EnqueueEvalDialog />
      </div>

      {/* Active jobs */}
      {activeJobs.length > 0 && (
        <TuiBox title={`ACTIVE JOBS (${activeJobs.length})`} className="mb-3">
          {activeJobs.map((job) => (
            <EvalJobCard key={job.id} job={job} />
          ))}
        </TuiBox>
      )}

      {!evalData || evalData.runs.length === 0 ? (
        <TuiBox title="RESULTS">
          <span className="text-text-muted">no evaluation data -- enqueue a run above</span>
        </TuiBox>
      ) : (
        <>
          {/* Condition tabs */}
          <div className="mb-3">
            <ConditionTabs
              conditions={conditions}
              active={validCondition}
              onChange={setActiveCondition}
            />
          </div>

          {/* Accuracy heatmap */}
          <TuiBox title="ACCURACY (MODEL x TASK)" className="mb-3">
            <AccuracyHeatmap runs={evalData.runs} condition={validCondition} />
          </TuiBox>

          {/* Run history */}
          <TuiBox title="RECENT RUNS">
            <table className="tui-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Task</th>
                  <th>Cond</th>
                  <th className="text-right">Acc</th>
                  <th className="text-right">N</th>
                  <th className="text-right">Date</th>
                </tr>
              </thead>
              <tbody>
                {recentRuns.map((run) => (
                  <tr key={run.id}>
                    <td className="text-text-secondary">{run.model}</td>
                    <td><TuiBadge color="accent">{run.task}</TuiBadge></td>
                    <td className="text-text-muted">{run.condition}</td>
                    <td className="text-right tabular-nums text-text-bright">{(run.accuracy * 100).toFixed(1)}%</td>
                    <td className="text-right tabular-nums text-text-muted">{run.instances.toLocaleString()}</td>
                    <td className="text-right text-text-muted">{formatDate(run.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TuiBox>
        </>
      )}
    </>
  );
}
