'use client';

import { useParams } from 'next/navigation';
import { PlannerInsights } from '@/components/planner-insights';
import { usePlannerEvaluations } from '@/hooks/use-planner';
import { useQuality } from '@/hooks/use-quality';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Badge } from '@/components/ui/badge';

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
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
    <div className="space-y-8">
      {/* Planner insights */}
      <section>
        <PlannerInsights project={name} />
      </section>

      {/* Recent Evaluations */}
      <section>
        <Label className="mb-4 block">Recent Evaluations</Label>
        {evalsLoading ? (
          <Card className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="space-y-1.5">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </Card>
        ) : evaluations && evaluations.length > 0 ? (
          <Card padding={false}>
            <div className="divide-y divide-border">
              {evaluations.map((ev) => (
                <div key={ev.id} className="px-6 py-4">
                  <div className="flex items-center gap-3 mb-1">
                    <Badge variant="outline">{ev.type}</Badge>
                    {ev.project && (
                      <span className="font-mono text-xs text-text-muted">{ev.project}</span>
                    )}
                    <span className="font-mono text-xs text-text-muted ml-auto">
                      {formatDate(ev.created_at)}
                    </span>
                  </div>
                  <p className="font-mono text-sm text-text-bright">
                    {summarizeResult(ev.result)}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        ) : (
          <Card>
            <EmptyState
              message="No evaluations yet"
              description="Planner evaluations will appear here once generated"
            />
          </Card>
        )}
      </section>

      {/* Quality score */}
      <section>
        <Label className="mb-4 block">Quality Score</Label>
        {qualityLoading ? (
          <Card className="space-y-3">
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
          </Card>
        ) : quality ? (
          <Card className="space-y-4">
            <div className="flex items-center gap-4">
              <span className="font-mono text-2xl font-bold text-text-bright">
                {quality.score}
              </span>
              <span className="font-mono text-xs text-text-muted">/ 100</span>
              <span className="font-mono text-xs text-text-muted ml-auto">
                Generated: {formatDate(quality.generated_at)}
              </span>
            </div>

            <div className="space-y-2">
              {quality.checks.map((check, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span
                    className={`inline-block h-2 w-2 rounded-full ${
                      check.passed ? 'bg-green-500' : 'bg-red-500'
                    }`}
                  />
                  <span className="font-mono text-xs text-text-bright">{check.name}</span>
                  {check.details && (
                    <span className="font-mono text-xs text-text-muted">{check.details}</span>
                  )}
                </div>
              ))}
            </div>
          </Card>
        ) : (
          <Card>
            <EmptyState
              message="No quality report"
              description="Quality scores will appear here once generated"
            />
          </Card>
        )}
      </section>
    </div>
  );
}
