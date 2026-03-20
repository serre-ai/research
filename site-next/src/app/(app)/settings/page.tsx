'use client';

import { useHealth, useDaemonHealth, useBudget } from '@/hooks';
import { PageHeader } from '@/components/ui/page-header';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { StatusDot } from '@/components/ui/status-dot';
import { Skeleton } from '@/components/ui/skeleton';
import { AGENTS } from '@/lib/agents';
import { DigestViewer } from '@/components/digest-viewer';

export default function SettingsPage() {
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: daemon, isLoading: daemonLoading } = useDaemonHealth();
  const { data: budget, isLoading: budgetLoading } = useBudget();

  return (
    <div>
      <PageHeader title="Settings" subtitle="System configuration and status" />

      {/* System Info */}
      <Card>
        <Label className="mb-4 block">System Info</Label>
        {healthLoading || daemonLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-4 w-28" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase text-text-muted">API Status</span>
              <div className="flex items-center gap-2">
                <StatusDot
                  status={health?.status === 'ok' ? 'ok' : 'error'}
                  pulse={health?.status === 'ok'}
                />
                <span className="font-mono text-xs text-text-bright">
                  {health?.status === 'ok' ? 'online' : 'offline'}
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase text-text-muted">Database</span>
              <div className="flex items-center gap-2">
                <StatusDot
                  status={health?.database?.connected ? 'ok' : 'error'}
                />
                <span className="font-mono text-xs text-text-bright">
                  {health?.database?.connected ? 'connected' : 'disconnected'}
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase text-text-muted">Daemon</span>
              <div className="flex items-center gap-2">
                <StatusDot
                  status={daemon?.running ? 'ok' : 'idle'}
                  pulse={daemon?.running}
                />
                <span className="font-mono text-xs text-text-bright">
                  {daemon?.running ? 'running' : 'stopped'}
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase text-text-muted">Memory</span>
              <span className="block font-mono text-xs text-text-bright">
                {health?.memory
                  ? `${health.memory.used}MB / ${health.memory.total}MB (${Math.round(health.memory.percentage)}%)`
                  : '--'}
              </span>
            </div>
          </div>
        )}
      </Card>

      {/* Budget */}
      <Card className="mt-4">
        <Label className="mb-4 block">Budget</Label>
        {budgetLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-4 w-28" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase text-text-muted">Monthly Spend</span>
              <span className="block font-mono text-xs text-text-bright">
                ${budget?.total?.toFixed(2) ?? '0.00'} / ${budget?.daily_limit ? (budget.daily_limit * 30).toFixed(2) : '0.00'}
              </span>
            </div>

            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase text-text-muted">Daily Burn Rate</span>
              <span className="block font-mono text-xs text-text-bright">
                ${budget?.burn_rate?.toFixed(2) ?? '0.00'}/day
              </span>
            </div>

            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase text-text-muted">Projected Monthly</span>
              <span className="block font-mono text-xs text-text-bright">
                ${budget?.projected_monthly?.toFixed(2) ?? '0.00'}
              </span>
            </div>

            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase text-text-muted">Remaining</span>
              <span className="block font-mono text-xs text-text-bright">
                ${budget?.remaining?.toFixed(2) ?? '0.00'}
              </span>
            </div>
          </div>
        )}
      </Card>

      {/* Daily Digest */}
      <div className="mt-4">
        <DigestViewer />
      </div>

      {/* Agent Configuration */}
      <div className="mt-8">
        <Label className="mb-4 block">Agent Configuration</Label>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Object.values(AGENTS).map((agent) => (
            <Card
              key={agent.id}
              style={{ borderLeftColor: agent.color, borderLeftWidth: 3 }}
            >
              <div className="font-mono text-sm font-bold text-text-bright">
                {agent.displayName}
              </div>
              <div className="mt-1 font-mono text-xs text-text-muted">
                {agent.role}
              </div>
              <div className="mt-2 font-mono text-[10px] text-text-secondary">
                {agent.model}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
