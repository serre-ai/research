'use client';

import { useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  useProjects, useBudget, useHealth, useDaemonHealth,
  useDecisions, usePendingTriggers, useAckTrigger,
} from '@/hooks';
import { TuiPanel, TuiList, TuiStatusDot, TuiBadge, TuiProgress } from '@/components/tui';
import { mapStatusToKey, formatCurrency, formatDate } from '@/lib/dashboard-helpers';
import type { Decision } from '@/lib/types';

function useAllDecisions(projectIds: string[]) {
  const q1 = useDecisions(projectIds[0] ?? '');
  const q2 = useDecisions(projectIds[1] ?? '');
  const q3 = useDecisions(projectIds[2] ?? '');
  const q4 = useDecisions(projectIds[3] ?? '');
  const q5 = useDecisions(projectIds[4] ?? '');
  const queries = [q1, q2, q3, q4, q5];
  const isLoading = queries.some((q) => q.isLoading);
  const allDecisions: Decision[] = [];
  for (const q of queries) { if (q.data) allDecisions.push(...q.data); }
  allDecisions.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  return { data: allDecisions, isLoading };
}

export default function DashboardPage() {
  const router = useRouter();
  const { data: projects, isLoading: projectsLoading, error: projectsError } = useProjects();
  const { data: budget, isLoading: budgetLoading } = useBudget();
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: daemon, isLoading: daemonLoading } = useDaemonHealth();

  const projectIds = (projects ?? []).map((p) => p.id);
  const { data: decisions, isLoading: decisionsLoading } = useAllDecisions(projectIds);
  const { data: triggers } = usePendingTriggers();
  const ackTrigger = useAckTrigger();

  const projectList = projects ?? [];
  const decisionList = (decisions ?? []).slice(0, 8);
  const triggerList = (triggers ?? []).slice(0, 8);
  const activeCount = projectList.filter((p) => p.status === 'active').length;
  const budgetLimit = budget ? budget.total + budget.remaining : 1000;
  const budgetPct = budget ? Math.round((budget.total / budgetLimit) * 100) : 0;

  const navigateToProject = useCallback(
    (p: (typeof projectList)[number]) => router.push(`/projects/${p.name}`),
    [router],
  );

  return (
    <>
      {/* Status line — not a panel */}
      <div className="flex flex-wrap gap-x-6 gap-y-1 mb-3">
        <span className="text-text-muted">
          {projectsLoading ? '...' : `${activeCount} active / ${projectList.length} projects`}
        </span>
        <span className="flex items-center gap-1">
          <TuiStatusDot status={daemon?.running ? 'ok' : 'idle'} />
          <span className="text-text-secondary">
            {daemonLoading ? '...' : daemon?.running ? 'daemon running' : 'daemon idle'}
          </span>
        </span>
        {!budgetLoading && budget && (
          <span className="flex items-center gap-1">
            <span className="text-text-muted">SPEND</span>
            <span className="text-text-secondary">{formatCurrency(budget.total)}</span>
            <TuiProgress
              value={budgetPct}
              width={8}
              showPercent={false}
              color={budgetPct > 90 ? 'error' : budgetPct > 70 ? 'warn' : 'ok'}
            />
          </span>
        )}
        {!healthLoading && health && (
          <span className="flex items-center gap-1">
            <TuiStatusDot status={health.status === 'ok' ? 'ok' : 'error'} />
            <span className="text-text-secondary">
              API {health.status === 'ok' ? 'online' : 'degraded'}
            </span>
          </span>
        )}
      </div>

      {/* Two columns: PROJECTS | HEALTH */}
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 mb-3">
        <TuiPanel
          id="projects"
          title="PROJECTS"
          order={1}
          itemCount={projectList.length}
          onActivateItem={(idx) => navigateToProject(projectList[idx])}
        >
          {projectsError ? (
            <span className="text-[--color-status-error]">
              failed to load: {projectsError.message ?? 'error'}
            </span>
          ) : (
            <TuiList
              panelId="projects"
              items={projectList}
              keyFn={(p) => p.id}
              onActivate={navigateToProject}
              emptyMessage={projectsLoading ? 'loading...' : 'no projects'}
              renderItem={(p, _i, active) => (
                <div className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-2">
                    <TuiStatusDot status={mapStatusToKey(p.status)} />
                    <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                      {p.name}
                    </span>
                  </span>
                  <span className="flex items-center gap-2">
                    <TuiBadge color="accent">{p.phase ?? p.status}</TuiBadge>
                    {p.confidence != null && (
                      <TuiProgress
                        value={Math.round(p.confidence * 100)}
                        width={6}
                        showPercent={false}
                        color={p.confidence > 0.7 ? 'ok' : p.confidence > 0.3 ? 'warn' : 'error'}
                      />
                    )}
                  </span>
                </div>
              )}
            />
          )}
        </TuiPanel>

        <TuiPanel id="health" title="HEALTH" order={2} itemCount={0}>
          {healthLoading || daemonLoading ? (
            <span className="text-text-muted">loading...</span>
          ) : (
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <TuiStatusDot status={health?.status === 'ok' ? 'ok' : 'error'} />
                  <span className="text-text-secondary">API</span>
                </span>
                <span className="text-text-muted">{health ? 'online' : 'offline'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <TuiStatusDot status={health?.database?.connected ? 'ok' : 'error'} />
                  <span className="text-text-secondary">Database</span>
                </span>
                <span className="text-text-muted">
                  {health?.database?.connected ? `${health.database.latency_ms}ms` : 'down'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <TuiStatusDot status={daemon?.running ? 'ok' : 'idle'} />
                  <span className="text-text-secondary">Daemon</span>
                </span>
                <span className="text-text-muted">
                  {daemon?.running ? 'running' : 'stopped'}
                </span>
              </div>
              {health?.memory && (
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <TuiStatusDot
                      status={health.memory.percentage > 90 ? 'error' : health.memory.percentage > 70 ? 'warn' : 'ok'}
                    />
                    <span className="text-text-secondary">Memory</span>
                  </span>
                  <span className="text-text-muted">{Math.round(health.memory.percentage)}%</span>
                </div>
              )}
              {daemon?.last_session && (
                <div className="text-text-muted mt-2 pt-1 border-t border-border">
                  last session: {formatDate(daemon.last_session)}
                </div>
              )}
            </div>
          )}
        </TuiPanel>
      </div>

      {/* DECISIONS */}
      <TuiPanel id="decisions" title="DECISIONS" order={3} itemCount={decisionList.length} className="mb-3">
        <TuiList
          panelId="decisions"
          items={decisionList}
          keyFn={(d, i) => `${d.date}-${i}`}
          emptyMessage={decisionsLoading ? 'loading...' : 'no decisions'}
          renderItem={(d, _i, active) => (
            <div>
              <div className="flex items-start justify-between gap-4">
                <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                  {d.decision}
                </span>
                <span className="shrink-0 text-text-muted">{formatDate(d.date)}</span>
              </div>
              {d.rationale && <span className="text-text-muted">{d.rationale}</span>}
              {d.project_id && <TuiBadge color="muted" className="ml-1">{d.project_id}</TuiBadge>}
            </div>
          )}
        />
      </TuiPanel>

      {/* TRIGGERS — only when present */}
      {triggerList.length > 0 && (
        <TuiPanel
          id="triggers"
          title="TRIGGERS"
          order={4}
          itemCount={triggerList.length}
          onActivateItem={(idx) => ackTrigger.mutate(triggerList[idx].id)}
          keyHints={[{ key: 'Enter', label: 'Acknowledge' }]}
        >
          <TuiList
            panelId="triggers"
            items={triggerList}
            keyFn={(t) => String(t.id)}
            onActivate={(t) => ackTrigger.mutate(t.id)}
            emptyMessage="no pending triggers"
            renderItem={(t, _i, active) => (
              <div className="flex items-center justify-between gap-2">
                <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                  {t.trigger_type}
                </span>
                <TuiBadge color="warn">{t.agent}</TuiBadge>
              </div>
            )}
          />
        </TuiPanel>
      )}
    </>
  );
}
