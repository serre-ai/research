'use client';

import Link from 'next/link';
import { useProjects, useBudget, useHealth, useDaemonHealth, useDecisions, usePendingTriggers, useAckTrigger } from '@/hooks';
import {
  TuiBox,
  TuiTable,
  TuiBadge,
  TuiStatusDot,
  TuiProgress,
  TuiMetric,
  TuiSkeleton,
} from '@/components/tui';
import { TriggerCard } from '@/components/collective/trigger-card';
import { mapStatusToKey, formatCurrency, formatDate } from '@/lib/dashboard-helpers';
import type { Decision } from '@/lib/types';

// Fetch decisions for first two projects
function useAllDecisions(projectIds: string[]) {
  const q1 = useDecisions(projectIds[0] ?? '');
  const q2 = useDecisions(projectIds[1] ?? '');

  const isLoading = q1.isLoading || q2.isLoading;
  const allDecisions: Decision[] = [];
  if (q1.data) allDecisions.push(...q1.data);
  if (q2.data) allDecisions.push(...q2.data);
  allDecisions.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  return { data: allDecisions, isLoading };
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
  const budgetPct = budget ? Math.round((budget.total / 1000) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="font-mono">
        <h1 className="text-xl font-semibold text-text-bright">DEEPWORK</h1>
        <span className="text-xs text-text-muted">Platform overview and project status</span>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <TuiBox>
          {projectsLoading ? (
            <TuiSkeleton width={12} />
          ) : (
            <TuiMetric
              label="Projects"
              value={activeProjects.length}
              unit={`/ ${projects?.length ?? 0}`}
            />
          )}
        </TuiBox>

        <TuiBox>
          {daemonLoading ? (
            <TuiSkeleton width={12} />
          ) : (
            <TuiMetric
              label="Daemon"
              value={daemon?.running ? '● RUN' : '○ IDLE'}
            />
          )}
        </TuiBox>

        <TuiBox>
          {projectsLoading ? (
            <TuiSkeleton width={12} />
          ) : (
            <TuiMetric label="Papers" value={projects?.length ?? 0} />
          )}
        </TuiBox>

        <TuiBox>
          {budgetLoading ? (
            <TuiSkeleton width={12} />
          ) : (
            <div className="font-mono">
              <TuiMetric
                label="Monthly Spend"
                value={budget ? formatCurrency(budget.total) : '$0'}
                unit="/ $1,000"
              />
              <TuiProgress
                value={budgetPct}
                width={16}
                color={budgetPct > 90 ? 'error' : budgetPct > 70 ? 'warn' : 'ok'}
                className="mt-1"
              />
            </div>
          )}
        </TuiBox>
      </div>

      {/* Projects table */}
      <TuiBox title="Projects">
        {projectsLoading ? (
          <div className="space-y-2">
            <TuiSkeleton width={40} />
            <TuiSkeleton width={40} />
            <TuiSkeleton width={40} />
          </div>
        ) : projects && projects.length > 0 ? (
          <TuiTable
            columns={[
              {
                key: 'name',
                header: 'Name',
                render: (row) => (
                  <Link
                    href={`/projects/${row.name}`}
                    className="text-text-bright hover:text-[--color-accent-primary]"
                  >
                    {String(row.name)}
                  </Link>
                ),
              },
              {
                key: 'status',
                header: '',
                className: 'w-8',
                render: (row) => (
                  <TuiStatusDot status={mapStatusToKey(String(row.status))} />
                ),
              },
              {
                key: 'phase',
                header: 'Phase',
                render: (row) => (
                  <TuiBadge color="accent">{String(row.phase ?? '—')}</TuiBadge>
                ),
              },
              {
                key: 'confidence',
                header: 'Conf',
                render: (row) => {
                  const conf = Number(row.confidence ?? 0);
                  return (
                    <TuiProgress
                      value={Math.round(conf * 100)}
                      width={8}
                      showPercent={false}
                      color={conf > 0.7 ? 'ok' : conf > 0.3 ? 'warn' : 'error'}
                    />
                  );
                },
              },
              {
                key: 'updated_at',
                header: 'Updated',
                className: 'text-text-muted',
                render: (row) => formatDate(String(row.updated_at ?? '')),
              },
            ]}
            data={projects}
            rowKey={(r) => String(r.id)}
          />
        ) : (
          <span className="text-sm text-text-muted">No projects found</span>
        )}
      </TuiBox>

      {/* Pending Triggers */}
      {triggers && triggers.length > 0 && (
        <TuiBox title="Pending Triggers" variant="warning">
          <div className="divide-y divide-border">
            {triggers.slice(0, 8).map((trigger) => (
              <TriggerCard
                key={trigger.id}
                trigger={trigger}
                onAck={(id) => ackTrigger.mutate(id)}
                isAcking={ackTrigger.isPending}
              />
            ))}
          </div>
        </TuiBox>
      )}

      {/* Bottom row: Decisions + Health */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Recent Decisions */}
        <TuiBox title="Decisions" className="lg:col-span-2">
          {decisionsLoading ? (
            <div className="space-y-2">
              <TuiSkeleton width={48} />
              <TuiSkeleton width={36} />
              <TuiSkeleton width={48} />
            </div>
          ) : decisions && decisions.length > 0 ? (
            <ul className="space-y-3">
              {decisions.slice(0, 5).map((d, i) => (
                <li key={i} className="border-b border-border pb-2 font-mono last:border-0 last:pb-0">
                  <div className="flex items-start justify-between gap-4">
                    <span className="text-xs text-text">{d.decision}</span>
                    <span className="shrink-0 text-[10px] text-text-muted">
                      {formatDate(d.date)}
                    </span>
                  </div>
                  <p className="mt-0.5 text-[10px] text-text-muted">{d.rationale}</p>
                  {d.project_id && (
                    <TuiBadge color="muted" className="mt-1">{d.project_id}</TuiBadge>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <span className="text-xs text-text-muted">No decisions recorded</span>
          )}
        </TuiBox>

        {/* System Health */}
        <TuiBox title="Health">
          {healthLoading || daemonLoading ? (
            <div className="space-y-2">
              <TuiSkeleton width={20} />
              <TuiSkeleton width={20} />
              <TuiSkeleton width={20} />
              <TuiSkeleton width={20} />
            </div>
          ) : (
            <ul className="space-y-2 font-mono text-xs">
              <li className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <TuiStatusDot status={health?.status === 'ok' ? 'ok' : 'error'} />
                  <span className="text-text-secondary">API</span>
                </span>
                <span className="text-text-muted">{health ? 'online' : 'offline'}</span>
              </li>

              <li className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <TuiStatusDot status={health?.database?.connected ? 'ok' : 'error'} />
                  <span className="text-text-secondary">Database</span>
                </span>
                <span className="text-text-muted">
                  {health?.database?.connected
                    ? `${health.database.latency_ms}ms`
                    : 'disconnected'}
                </span>
              </li>

              <li className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <TuiStatusDot status={daemon?.running ? 'ok' : 'idle'} />
                  <span className="text-text-secondary">Daemon</span>
                </span>
                <span className="text-text-muted">
                  {daemon?.running ? 'running' : 'stopped'}
                </span>
              </li>

              <li className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <TuiStatusDot
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
                  <span className="text-text-secondary">Memory</span>
                </span>
                <span className="text-text-muted">
                  {health?.memory
                    ? `${Math.round(health.memory.percentage)}%`
                    : '--'}
                </span>
              </li>

              {daemon?.last_session && (
                <li className="mt-2 border-t border-border pt-2 text-[10px] text-text-muted">
                  Last session: {formatDate(daemon.last_session)}
                </li>
              )}
            </ul>
          )}
        </TuiBox>
      </div>
    </div>
  );
}
