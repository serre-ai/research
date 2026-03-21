'use client';

import { useParams } from 'next/navigation';
import { Activity, BarChart3, Crosshair, Gauge } from 'lucide-react';
import { useProject, useEvalData, useDecisions, useSessions } from '@/hooks';
import { useQuality } from '@/hooks/use-quality';
import { MetricCard } from '@/components/ui/metric-card';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { ProgressBar } from '@/components/ui/progress-bar';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatDuration(seconds?: number): string {
  if (!seconds) return '--';
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins < 60) return `${mins}m ${secs}s`;
  const hrs = Math.floor(mins / 60);
  return `${hrs}h ${mins % 60}m`;
}

export default function ProjectOverviewPage() {
  const params = useParams();
  const name = params.name as string;

  const { data: project, isLoading: projectLoading } = useProject(name);
  const { data: evalData, isLoading: evalLoading } = useEvalData(name);
  const { data: decisions, isLoading: decisionsLoading } = useDecisions(name);
  const { data: sessions, isLoading: sessionsLoading } = useSessions(name);
  const { data: quality, isLoading: qualityLoading } = useQuality(name);

  return (
    <div className="space-y-8">
      {/* Key metrics */}
      <section>
        <Label className="mb-4 block">Key Metrics</Label>
        {projectLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="space-y-2">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-7 w-24" />
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              label="Phase"
              value={project?.phase ?? '--'}
              icon={BarChart3}
            />
            <MetricCard
              label="Confidence"
              value={
                project?.confidence != null
                  ? `${Math.round(project.confidence * 100)}%`
                  : '--'
              }
              icon={Gauge}
            />
            <MetricCard
              label="Focus"
              value={project?.focus ?? '--'}
              icon={Crosshair}
            />
            <MetricCard
              label="Status"
              value={project?.status ?? '--'}
              icon={Activity}
            />
          </div>
        )}
      </section>

      {/* Quality score */}
      <section>
        <Label className="mb-4 block">Quality Score</Label>
        {qualityLoading ? (
          <Card className="space-y-2">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-7 w-24" />
          </Card>
        ) : quality ? (
          <Card>
            <div className="flex items-center gap-4">
              <span className="font-mono text-2xl font-bold text-text-bright">
                {quality.score}
              </span>
              <span className="font-mono text-xs text-text-muted">/ 100</span>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {(quality.checks ?? []).map((check, i) => (
                <span
                  key={i}
                  className={`font-mono text-xs px-2 py-0.5 rounded ${
                    check.passed
                      ? 'bg-green-500/10 text-green-400'
                      : 'bg-red-500/10 text-red-400'
                  }`}
                >
                  {check.name}
                </span>
              ))}
            </div>
          </Card>
        ) : (
          <Card>
            <EmptyState message="No quality data" description="Quality scores will appear once generated" />
          </Card>
        )}
      </section>

      {/* Eval progress */}
      <section>
        <Label className="mb-4 block">Eval Progress</Label>
        {evalLoading ? (
          <Card className="space-y-3">
            <Skeleton className="h-3 w-48" />
            <Skeleton className="h-2 w-full" />
          </Card>
        ) : evalData && evalData.runs.length > 0 ? (
          <Card className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm text-text-secondary">
                {evalData.progress.completed.toLocaleString()} /{' '}
                {evalData.progress.total.toLocaleString()} runs completed
              </span>
              {evalData.progress.failed > 0 && (
                <Badge variant="error">{evalData.progress.failed} failed</Badge>
              )}
            </div>
            <ProgressBar
              value={evalData.progress.completed}
              max={evalData.progress.total || 1}
            />
            <div className="font-mono text-xs text-text-muted">
              {evalData.runs.length} total eval runs
            </div>
          </Card>
        ) : (
          <Card>
            <EmptyState message="No eval data yet" description="Evaluations will appear here once started" />
          </Card>
        )}
      </section>

      {/* Recent decisions */}
      <section>
        <Label className="mb-4 block">Recent Decisions</Label>
        {decisionsLoading ? (
          <Card className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="space-y-1.5">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </Card>
        ) : decisions && decisions.length > 0 ? (
          <Card padding={false}>
            <div className="divide-y divide-border">
              {decisions.slice(0, 5).map((d, i) => (
                <div key={i} className="px-6 py-4">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="font-mono text-xs text-text-muted">
                      {formatDate(d.date)}
                    </span>
                  </div>
                  <p className="font-mono text-sm text-text-bright">{d.decision}</p>
                  {d.rationale && (
                    <p className="mt-1 font-mono text-xs text-text-muted">{d.rationale}</p>
                  )}
                </div>
              ))}
            </div>
          </Card>
        ) : (
          <Card>
            <EmptyState message="No decisions yet" description="Decisions will be logged here as they are made" />
          </Card>
        )}
      </section>

      {/* Recent sessions */}
      <section>
        <Label className="mb-4 block">Recent Sessions</Label>
        {sessionsLoading ? (
          <Card className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-4 w-32" />
              </div>
            ))}
          </Card>
        ) : sessions && sessions.length > 0 ? (
          <Card padding={false}>
            <div className="divide-y divide-border">
              {sessions.slice(0, 5).map((s) => (
                <div key={s.id} className="flex items-center justify-between px-6 py-3">
                  <div className="flex items-center gap-4">
                    <Badge variant="outline">{s.agent_type}</Badge>
                    <span className="font-mono text-xs text-text-muted">
                      {formatDate(s.started_at)}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-xs text-text-muted tabular-nums">
                      {formatDuration(s.duration_seconds)}
                    </span>
                    <Badge
                      variant={
                        s.status === 'completed'
                          ? 'success'
                          : s.status === 'running'
                            ? 'default'
                            : s.status === 'failed' || s.status === 'error'
                              ? 'error'
                              : 'default'
                      }
                    >
                      {s.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ) : (
          <Card>
            <EmptyState message="No sessions yet" description="Agent sessions will appear here once started" />
          </Card>
        )}
      </section>
    </div>
  );
}
