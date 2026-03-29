'use client';

import { useHealth, useDaemonHealth, useBudget } from '@/hooks';
import { TuiBox, TuiStatusDot, TuiSkeleton, TuiProgress } from '@/components/tui';
import { AGENTS } from '@/lib/agents';
import { DigestViewer } from '@/components/digest-viewer';

export default function SettingsPage() {
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: daemon, isLoading: daemonLoading } = useDaemonHealth();
  const { data: budget, isLoading: budgetLoading } = useBudget();

  const memPct = health?.memory ? Math.round(health.memory.percentage) : 0;

  return (
    <>
      {/* System Info */}
      <TuiBox title="SYSTEM" className="mb-3">
        {healthLoading || daemonLoading ? (
          <div className="flex flex-wrap gap-x-6 gap-y-1">
            {Array.from({ length: 4 }).map((_, i) => (
              <TuiSkeleton key={i} width={20} />
            ))}
          </div>
        ) : (
          <div className="flex flex-wrap gap-x-6 gap-y-1">
            <span className="flex items-center gap-1">
              <TuiStatusDot status={health?.status === 'ok' ? 'ok' : 'error'} />
              <span className="text-text-muted">API</span>
              <span className="text-text-secondary">{health?.status === 'ok' ? 'online' : 'offline'}</span>
            </span>
            <span className="flex items-center gap-1">
              <TuiStatusDot status={health?.database?.connected ? 'ok' : 'error'} />
              <span className="text-text-muted">DB</span>
              <span className="text-text-secondary">{health?.database?.connected ? 'connected' : 'down'}</span>
            </span>
            <span className="flex items-center gap-1">
              <TuiStatusDot status={daemon?.running ? 'ok' : 'idle'} />
              <span className="text-text-muted">Daemon</span>
              <span className="text-text-secondary">{daemon?.running ? 'running' : 'stopped'}</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="text-text-muted">MEM</span>
              <TuiProgress value={memPct} width={8} showPercent={false} />
              <span className="text-text-muted">{memPct}%</span>
            </span>
          </div>
        )}
      </TuiBox>

      {/* Budget */}
      <TuiBox title="BUDGET" className="mb-3">
        {budgetLoading ? (
          <div className="flex flex-wrap gap-x-6 gap-y-1">
            {Array.from({ length: 4 }).map((_, i) => (
              <TuiSkeleton key={i} width={20} />
            ))}
          </div>
        ) : (
          <div className="flex flex-wrap gap-x-6 gap-y-1">
            <span>
              <span className="text-text-muted">spend </span>
              <span className="text-text-bright">${budget?.total?.toFixed(2) ?? '0.00'}</span>
              <span className="text-text-muted"> / ${budget?.daily_limit ? (budget.daily_limit * 30).toFixed(2) : '0.00'}</span>
            </span>
            <span>
              <span className="text-text-muted">burn </span>
              <span className="text-text-bright">${budget?.burn_rate?.toFixed(2) ?? '0.00'}</span>
              <span className="text-text-muted">/day</span>
            </span>
            <span>
              <span className="text-text-muted">projected </span>
              <span className="text-text-bright">${budget?.projected_monthly?.toFixed(2) ?? '0.00'}</span>
            </span>
            <span>
              <span className="text-text-muted">remaining </span>
              <span className="text-text-bright">${budget?.remaining?.toFixed(2) ?? '0.00'}</span>
            </span>
          </div>
        )}
      </TuiBox>

      {/* Daily Digest */}
      <div className="mb-3">
        <DigestViewer />
      </div>

      {/* Agent Configuration */}
      <TuiBox title="AGENTS">
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {Object.values(AGENTS).map((agent) => (
            <div key={agent.id} className="flex items-baseline gap-2">
              <span style={{ color: agent.color }}>{'●'}</span>
              <span className="text-text-bright">{agent.displayName}</span>
              <span className="text-text-muted">{agent.role}</span>
              <span className="text-text-muted">({agent.model.replace('claude-', '').split('-').slice(0, 2).join('-')})</span>
            </div>
          ))}
        </div>
      </TuiBox>
    </>
  );
}
