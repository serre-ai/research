'use client';

import Link from 'next/link';
import {
  FolderOpen,
  Activity,
  FileText,
  DollarSign,
  ArrowRight,
} from 'lucide-react';
import { useProjects, useBudget, useHealth, useDaemonHealth, useDecisions, usePendingTriggers, useAckTrigger } from '@/hooks';
import { PageHeader } from '@/components/ui/page-header';
import { MetricCard } from '@/components/ui/metric-card';
import { Card } from '@/components/ui/card';
import { StatusBadge } from '@/components/ui/status-badge';
import { StatusDot } from '@/components/ui/status-dot';
import { Skeleton } from '@/components/ui/skeleton';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { TriggerCard } from '@/components/collective/trigger-card';
import { mapStatusToKey, formatCurrency, formatDate } from '@/lib/dashboard-helpers';
import type { Decision } from '@/lib/types';

function MetricSkeleton() {
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-4 w-4" />
      </div>
      <Skeleton className="h-8 w-20" />
    </Card>
  );
}

function ProjectCardSkeleton() {
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-5 w-16" />
      </div>
      <Skeleton className="h-3 w-48" />
      <Skeleton className="h-3 w-24" />
    </Card>
  );
}

// A wrapper that fetches decisions for a single project
function useAllDecisions(projectIds: string[]) {
  const q1 = useDecisions(projectIds[0] ?? '');
  const q2 = useDecisions(projectIds[1] ?? '');

  const isLoading = q1.isLoading || q2.isLoading;
  const error = q1.error || q2.error;

  const allDecisions: Decision[] = [];
  if (q1.data) allDecisions.push(...q1.data);
  if (q2.data) allDecisions.push(...q2.data);

  // Sort by date descending
  allDecisions.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  return { data: allDecisions, isLoading, error };
}

export default function DashboardPage() {
  const { data: projects, isLoading: projectsLoading } = useProjects();
  const { data: budget, isLoading: budgetLoading } = useBudget();
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: daemon, isLoading: daemonLoading } = useDaemonHealth();

  const projectIds = (projects ?? []).map((p) => p.id);
  const { data: decisions, isLoading: decisionsLoading } = useAllDecisions(projectIds);
  const { data: triggers } = usePendingTriggers();
  const ackTrigger = useAckTrigger();

  const activeProjects = (projects ?? []).filter((p) => p.status === 'active');
  const isActiveSessions = daemon?.running ?? false;

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Platform overview and project status" />

      {/* Metric cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {projectsLoading ? (
          <MetricSkeleton />
        ) : (
          <MetricCard
            label="Projects"
            value={projects?.length ?? 0}
            icon={FolderOpen}
            trend={
              activeProjects.length > 0
                ? { value: activeProjects.length, label: 'active' }
                : undefined
            }
          />
        )}

        {daemonLoading ? (
          <MetricSkeleton />
        ) : (
          <MetricCard
            label="Daemon"
            value={isActiveSessions ? 'Running' : 'Idle'}
            icon={Activity}
          />
        )}

        {projectsLoading ? (
          <MetricSkeleton />
        ) : (
          <MetricCard
            label="Papers"
            value={projects?.length ?? 0}
            icon={FileText}
          />
        )}

        {budgetLoading ? (
          <MetricSkeleton />
        ) : (
          <MetricCard
            label="Monthly Spend"
            value={budget ? formatCurrency(budget.total) : '$0'}
            icon={DollarSign}
            trend={
              budget
                ? {
                    value: -Math.round(((budget.remaining ?? 0) / 1000) * 100),
                    label: `of $1,000`,
                  }
                : undefined
            }
          />
        )}
      </div>

      {/* Project cards */}
      <div className="mt-8">
        <Label className="mb-4 block">Projects</Label>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {projectsLoading ? (
            <>
              <ProjectCardSkeleton />
              <ProjectCardSkeleton />
            </>
          ) : projects && projects.length > 0 ? (
            projects.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.name}`}
                className="group block hover:no-underline"
              >
                <Card className="transition-colors group-hover:border-border-strong">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <StatusDot
                        status={mapStatusToKey(project.status)}
                        pulse={project.status === 'active'}
                      />
                      <span className="font-mono text-sm font-semibold text-text-bright">
                        {project.name}
                      </span>
                    </div>
                    <StatusBadge status={mapStatusToKey(project.status)}>
                      {project.status}
                    </StatusBadge>
                  </div>

                  {project.phase && (
                    <div className="mt-3 flex items-center gap-2">
                      <span className="font-mono text-xs text-text-muted">Phase:</span>
                      <Badge variant="outline">{project.phase}</Badge>
                    </div>
                  )}

                  {project.focus && (
                    <p className="mt-2 text-xs text-text-secondary">{project.focus}</p>
                  )}

                  <div className="mt-3 flex items-center justify-between text-xs text-text-muted">
                    {project.confidence !== undefined && (
                      <span className="font-mono">
                        Confidence: {Math.round(project.confidence * 100)}%
                      </span>
                    )}
                    <span className="font-mono">
                      Updated {formatDate(project.updated_at)}
                    </span>
                  </div>

                  <div className="mt-3 flex items-center gap-1 text-xs text-text-muted opacity-0 transition-opacity group-hover:opacity-100">
                    View project <ArrowRight className="h-3 w-3" />
                  </div>
                </Card>
              </Link>
            ))
          ) : (
            <Card className="col-span-full">
              <p className="text-center text-sm text-text-muted">No projects found</p>
            </Card>
          )}
        </div>
      </div>

      {/* Pending Triggers */}
      {triggers && triggers.length > 0 && (
        <div className="mt-8">
          <Card>
            <Label className="mb-4 block">
              Pending Triggers
              <Badge variant="warning" className="ml-2">{triggers.length}</Badge>
            </Label>
            <div className="divide-y divide-border -mx-4 -mb-4">
              {triggers.slice(0, 8).map((trigger) => (
                <TriggerCard
                  key={trigger.id}
                  trigger={trigger}
                  onAck={(id) => ackTrigger.mutate(id)}
                  isAcking={ackTrigger.isPending}
                />
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Bottom row: Decisions + Health */}
      <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Recent Decisions */}
        <Card className="lg:col-span-2">
          <Label className="mb-4 block">Recent Decisions</Label>
          {decisionsLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="space-y-1.5">
                  <Skeleton className="h-3 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              ))}
            </div>
          ) : decisions && decisions.length > 0 ? (
            <ul className="space-y-4">
              {decisions.slice(0, 5).map((d, i) => (
                <li key={i} className="border-b border-border pb-3 last:border-0 last:pb-0">
                  <div className="flex items-start justify-between gap-4">
                    <p className="font-mono text-xs text-text">{d.decision}</p>
                    <span className="shrink-0 font-mono text-[10px] text-text-muted">
                      {formatDate(d.date)}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-text-muted">{d.rationale}</p>
                  {d.project_id && (
                    <Badge variant="outline" className="mt-1.5">
                      {d.project_id}
                    </Badge>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-text-muted">No decisions recorded yet</p>
          )}
        </Card>

        {/* System Health */}
        <Card>
          <Label className="mb-4 block">System Health</Label>
          {healthLoading || daemonLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3">
                  <Skeleton className="h-2 w-2 rounded-full" />
                  <Skeleton className="h-3 w-24" />
                </div>
              ))}
            </div>
          ) : (
            <ul className="space-y-3">
              <li className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <StatusDot
                    status={health?.status === 'ok' ? 'ok' : 'error'}
                    pulse={health?.status === 'ok'}
                  />
                  <span className="font-mono text-xs text-text-secondary">API Server</span>
                </div>
                <span className="font-mono text-xs text-text-muted">
                  {health ? 'online' : 'offline'}
                </span>
              </li>

              <li className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <StatusDot
                    status={health?.database?.connected ? 'ok' : 'error'}
                  />
                  <span className="font-mono text-xs text-text-secondary">Database</span>
                </div>
                <span className="font-mono text-xs text-text-muted">
                  {health?.database?.connected
                    ? `${health.database.latency_ms}ms`
                    : 'disconnected'}
                </span>
              </li>

              <li className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <StatusDot
                    status={daemon?.running ? 'ok' : 'idle'}
                    pulse={daemon?.running}
                  />
                  <span className="font-mono text-xs text-text-secondary">Daemon</span>
                </div>
                <span className="font-mono text-xs text-text-muted">
                  {daemon?.running ? 'running' : 'stopped'}
                </span>
              </li>

              <li className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <StatusDot
                    status={
                      health?.memory
                        ? health.memory.percentage > 90
                          ? 'error'
                          : health.memory.percentage > 70
                            ? 'warn'
                            : 'ok'
                        : 'idle'
                    }
                  />
                  <span className="font-mono text-xs text-text-secondary">Memory</span>
                </div>
                <span className="font-mono text-xs text-text-muted">
                  {health?.memory
                    ? `${Math.round(health.memory.percentage)}%`
                    : '--'}
                </span>
              </li>

              {daemon?.last_session && (
                <li className="mt-2 border-t border-border pt-3">
                  <span className="font-mono text-[10px] text-text-muted">
                    Last session: {formatDate(daemon.last_session)}
                  </span>
                </li>
              )}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
