'use client';

import { TuiBox, TuiStatusDot, TuiSkeleton } from '@/components/tui';
import { usePlannerStatus, usePlannerInsights } from '@/hooks/use-planner';

interface PlannerInsightsProps {
  project: string;
}

export function PlannerInsights({ project }: PlannerInsightsProps) {
  const { data: status, isLoading: statusLoading } = usePlannerStatus();
  const { data: insights, isLoading: insightsLoading } = usePlannerInsights(project);

  const isLoading = statusLoading || insightsLoading;

  return (
    <TuiBox title="PLANNER">
      {isLoading ? (
        <div className="space-y-1">
          <TuiSkeleton width={20} />
          <TuiSkeleton width={40} />
        </div>
      ) : !status && !insights ? (
        <span className="text-text-muted">no planner data</span>
      ) : (
        <div className="space-y-2">
          {/* Status */}
          <div className="flex items-center gap-2">
            <TuiStatusDot status={status?.enabled ? 'ok' : 'idle'} />
            <span className="text-text-secondary">{status?.enabled ? 'enabled' : 'disabled'}</span>
            {status?.last_run && (
              <span className="text-text-muted">last: {new Date(status.last_run).toISOString().slice(0, 16).replace('T', ' ')}</span>
            )}
          </div>

          {/* Recommendations */}
          {insights?.recommendations && insights.recommendations.length > 0 ? (
            <div>
              <span className="text-text-muted block mb-1">RECOMMENDATIONS</span>
              {insights.recommendations.map((rec, i) => (
                <div key={i} className="text-text-secondary">{'  '}- {rec}</div>
              ))}
            </div>
          ) : (
            <span className="text-text-muted">no recommendations</span>
          )}
        </div>
      )}
    </TuiBox>
  );
}
