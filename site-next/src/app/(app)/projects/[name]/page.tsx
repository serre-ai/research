'use client';

import { useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useProject, useEvalData, useDecisions, useSessions } from '@/hooks';
import { useQuality } from '@/hooks/use-quality';
import { TuiBox, TuiPanel, TuiList, TuiMetric, TuiProgress, TuiBadge, TuiStatusDot } from '@/components/tui';
import { mapStatusToKey, formatDate } from '@/lib/dashboard-helpers';
import { formatDuration } from '@/lib/format';

export default function ProjectOverviewPage() {
  const params = useParams();
  const name = params.name as string;
  const router = useRouter();

  const { data: project, isLoading: projectLoading } = useProject(name);
  const { data: evalData, isLoading: evalLoading } = useEvalData(name);
  const { data: decisions, isLoading: decisionsLoading } = useDecisions(name);
  const { data: sessions, isLoading: sessionsLoading } = useSessions(name);
  const { data: quality, isLoading: qualityLoading } = useQuality(name);

  const decisionList = (decisions ?? []).slice(0, 5);
  const sessionList = (sessions ?? []).slice(0, 5);

  const navigateToSession = useCallback(
    (s: (typeof sessionList)[number]) => router.push(`/projects/${name}/sessions/${s.id}`),
    [router, name],
  );

  const confidencePct = project?.confidence != null ? Math.round(project.confidence * 100) : null;
  const evalPct = evalData
    ? Math.round((evalData.summary.completed / (evalData.summary.total || 1)) * 100)
    : 0;

  return (
    <>
      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 mb-3">
        <TuiBox title="PROJECT">
          {projectLoading ? (
            <span className="text-text-muted">loading...</span>
          ) : (
            <div className="space-y-2">
              <TuiMetric label="PHASE" value={project?.phase ?? '--'} />
              <div>
                <div className="text-text-muted text-xs mb-0.5">CONFIDENCE</div>
                <div className="flex items-center gap-2">
                  <span className="text-text-bright">
                    {confidencePct != null ? `${confidencePct}%` : '--'}
                  </span>
                  {confidencePct != null && (
                    <TuiProgress
                      value={confidencePct}
                      width={12}
                      color={confidencePct > 70 ? 'ok' : confidencePct > 30 ? 'warn' : 'error'}
                    />
                  )}
                </div>
              </div>
              <TuiMetric label="FOCUS" value={project?.focus ?? '--'} />
              <div>
                <div className="text-text-muted text-xs mb-0.5">STATUS</div>
                <span className="flex items-center gap-2">
                  <TuiStatusDot status={mapStatusToKey(project?.status ?? 'idle')} />
                  <span className="text-text-bright">{project?.status ?? '--'}</span>
                </span>
              </div>
            </div>
          )}
        </TuiBox>

        {/* Quality Score */}
        <TuiBox title="QUALITY">
          {qualityLoading ? (
            <span className="text-text-muted">loading...</span>
          ) : quality ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-text-bright text-lg">{quality.score}</span>
                <span className="text-text-muted">/ 100</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {(quality.checks ?? []).map((check, i) => (
                  <TuiBadge key={i} color={check.passed ? 'ok' : 'error'}>
                    {check.name}
                  </TuiBadge>
                ))}
              </div>
            </div>
          ) : (
            <span className="text-text-muted">no quality data</span>
          )}
        </TuiBox>
      </div>

      {/* Eval Progress */}
      <TuiBox title="EVAL" className="mb-3">
        {evalLoading ? (
          <span className="text-text-muted">loading...</span>
        ) : evalData && (evalData.runs ?? []).length > 0 ? (
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-text-secondary">
                {evalData.summary.completed.toLocaleString()} / {evalData.summary.total.toLocaleString()} runs
              </span>
              {evalData.summary.failed > 0 && (
                <TuiBadge color="error">{evalData.summary.failed} failed</TuiBadge>
              )}
            </div>
            <TuiProgress
              value={evalPct}
              width={30}
              color={evalData.summary.failed > 0 ? 'warn' : 'ok'}
            />
            <span className="text-text-muted">{(evalData.runs ?? []).length} total eval runs</span>
          </div>
        ) : (
          <span className="text-text-muted">no eval data yet</span>
        )}
      </TuiBox>

      {/* Recent Decisions */}
      <TuiPanel id="decisions" title="DECISIONS" order={1} itemCount={decisionList.length} className="mb-3">
        <TuiList
          panelId="decisions"
          items={decisionList}
          keyFn={(d, i) => `${d.date}-${i}`}
          emptyMessage={decisionsLoading ? 'loading...' : 'no decisions yet'}
          renderItem={(d, _i, active) => (
            <div>
              <div className="flex items-start justify-between gap-4">
                <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                  {d.decision}
                </span>
                <span className="shrink-0 text-text-muted">{formatDate(d.date)}</span>
              </div>
              {d.rationale && <span className="text-text-muted">{d.rationale}</span>}
            </div>
          )}
        />
      </TuiPanel>

      {/* Recent Sessions */}
      <TuiPanel
        id="sessions"
        title="SESSIONS"
        order={2}
        itemCount={sessionList.length}
        onActivateItem={(idx) => navigateToSession(sessionList[idx])}
        keyHints={[{ key: 'Enter', label: 'Open session' }]}
      >
        <TuiList
          panelId="sessions"
          items={sessionList}
          keyFn={(s) => String(s.id)}
          onActivate={navigateToSession}
          emptyMessage={sessionsLoading ? 'loading...' : 'no sessions yet'}
          renderItem={(s, _i, active) => (
            <div className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-2">
                <TuiBadge color="accent">{s.agent_type}</TuiBadge>
                <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                  {formatDate(s.started_at)}
                </span>
              </span>
              <span className="flex items-center gap-2">
                <span className="text-text-muted tabular-nums">
                  {s.duration_seconds ? formatDuration(s.duration_seconds) : '--'}
                </span>
                <TuiStatusDot status={mapStatusToKey(s.status)} />
              </span>
            </div>
          )}
        />
      </TuiPanel>
    </>
  );
}
