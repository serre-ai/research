'use client';

import { useParams } from 'next/navigation';
import { TuiBox, TuiBadge, TuiSkeleton, TuiStatusDot } from '@/components/tui';
import { PlannerInsights } from '@/components/planner-insights';
import { usePlannerEvaluations } from '@/hooks/use-planner';
import { useQuality } from '@/hooks/use-quality';

function formatDate(dateStr: string): string {
  return new Date(dateStr).toISOString().slice(0, 10);
}

function summarizeResult(result: unknown): string {
  if (typeof result === 'string') return result;
  if (typeof result === 'number') return String(result);
  if (result && typeof result === 'object') {
    const obj = result as Record<string, unknown>;
    if ('summary' in obj && typeof obj.summary === 'string') return obj.summary;
    if ('status' in obj && typeof obj.status === 'string') return obj.status;
    return JSON.stringify(result).slice(0, 80);
  }
  return '--';
}

export default function PlannerPage() {
  const params = useParams();
  const name = params.name as string;

  const { data: evaluations, isLoading: evalsLoading } = usePlannerEvaluations();
  const { data: quality, isLoading: qualityLoading } = useQuality(name);

  return (
    <>
      {/* Planner insights */}
      <div className="mb-3">
        <PlannerInsights project={name} />
      </div>

      {/* Recent Evaluations */}
      <TuiBox title="EVALUATIONS" className="mb-3">
        {evalsLoading ? (
          <div className="space-y-1">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex gap-2"><TuiSkeleton width={10} /><TuiSkeleton width={40} /></div>
            ))}
          </div>
        ) : evaluations && evaluations.length > 0 ? (
          evaluations.map((ev) => (
            <div key={ev.id} className="border-b border-border py-1.5 first:pt-0 last:border-0 last:pb-0">
              <div className="flex items-center gap-2 mb-0.5">
                <TuiBadge color="accent">{ev.type}</TuiBadge>
                {ev.project && <span className="text-text-muted">{ev.project}</span>}
                <span className="text-text-muted ml-auto">{formatDate(ev.created_at)}</span>
              </div>
              <span className="text-text-secondary">{summarizeResult(ev.result)}</span>
            </div>
          ))
        ) : (
          <span className="text-text-muted">no evaluations yet</span>
        )}
      </TuiBox>

      {/* Quality score */}
      <TuiBox title="QUALITY SCORE">
        {qualityLoading ? (
          <div className="space-y-1">
            <TuiSkeleton width={10} />
            <TuiSkeleton width={40} />
          </div>
        ) : quality ? (
          <>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-text-bright font-bold">{quality.score}</span>
              <span className="text-text-muted">/ 100</span>
              <span className="text-text-muted ml-auto">{formatDate(quality.generated_at)}</span>
            </div>
            <div className="space-y-0.5">
              {(quality.checks ?? []).map((check, i) => (
                <div key={i} className="flex items-center gap-2">
                  <TuiStatusDot status={check.passed ? 'ok' : 'error'} />
                  <span className="text-text-bright">{check.name}</span>
                  {check.details && <span className="text-text-muted">{check.details}</span>}
                </div>
              ))}
            </div>
          </>
        ) : (
          <span className="text-text-muted">no quality report</span>
        )}
      </TuiBox>
    </>
  );
}
