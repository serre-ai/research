'use client';

import { usePlannerStatus, usePlannerInsights } from '@/hooks/use-planner';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';

interface PlannerInsightsProps {
  project: string;
}

export function PlannerInsights({ project }: PlannerInsightsProps) {
  const { data: status, isLoading: statusLoading } = usePlannerStatus();
  const { data: insights, isLoading: insightsLoading } = usePlannerInsights(project);

  const isLoading = statusLoading || insightsLoading;

  if (isLoading) {
    return (
      <Card className="space-y-3">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-4 w-48" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
      </Card>
    );
  }

  if (!status && !insights) {
    return (
      <Card>
        <EmptyState
          message="No planner data"
          description="Planner insights will appear here once available"
        />
      </Card>
    );
  }

  return (
    <Card className="space-y-4">
      <Label className="block">Planner</Label>

      {/* Status line */}
      <div className="flex items-center gap-3">
        <span
          className={`inline-block h-2 w-2 rounded-full ${
            status?.enabled ? 'bg-green-500' : 'bg-text-muted'
          }`}
        />
        <span className="font-mono text-xs text-text-secondary">
          {status?.enabled ? 'Enabled' : 'Disabled'}
        </span>
        {status?.last_run && (
          <span className="font-mono text-xs text-text-muted">
            Last run: {new Date(status.last_run).toLocaleString()}
          </span>
        )}
      </div>

      {/* Recommendations */}
      {insights?.recommendations && insights.recommendations.length > 0 ? (
        <div className="space-y-2">
          <span className="font-mono text-xs font-medium text-text-secondary">
            Recommendations
          </span>
          <ul className="space-y-1">
            {insights.recommendations.map((rec, i) => (
              <li
                key={i}
                className="font-mono text-xs text-text-bright pl-4 relative before:content-[''] before:absolute before:left-0 before:top-[0.45em] before:h-1 before:w-1 before:rounded-full before:bg-text-muted"
              >
                {rec}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="font-mono text-xs text-text-muted">No recommendations available</p>
      )}
    </Card>
  );
}
