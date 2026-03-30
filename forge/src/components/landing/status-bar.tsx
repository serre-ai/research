import { TuiBox, TuiStatusDot, TuiProgress } from '@/components/tui';

interface HealthData {
  status: string;
  uptime_s?: number;
  database?: { connected: boolean; latency_ms?: number };
  memory?: { percentage: number; free_mb: number; total_mb: number };
}

function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${d}d ${h}h ${m}m`;
}

export function StatusBar({
  health,
  projectCount,
}: {
  health: HealthData | null;
  projectCount: number;
}) {
  if (!health) {
    return (
      <TuiBox title="STATUS">
        <span className="font-mono text-xs text-text-muted">status unavailable</span>
      </TuiBox>
    );
  }

  const memPct = health.memory?.percentage ?? 0;

  return (
    <TuiBox title="STATUS">
      <div className="flex flex-wrap gap-x-8 gap-y-2 font-mono text-xs">
        <span className="flex items-center gap-1.5">
          <TuiStatusDot status={health.status === 'ok' ? 'ok' : 'error'} />
          <span className="text-text-secondary">API online</span>
        </span>

        <span className="flex items-center gap-1.5">
          <TuiStatusDot status={health.database?.connected ? 'ok' : 'error'} />
          <span className="text-text-secondary">
            DB {health.database?.connected ? `${health.database.latency_ms ?? '?'}ms` : 'down'}
          </span>
        </span>

        <span className="flex items-center gap-1.5">
          <span className="text-text-muted">{projectCount} projects active</span>
        </span>

        {health.uptime_s != null && (
          <span className="text-text-muted">
            up {formatUptime(health.uptime_s)}
          </span>
        )}

        {health.memory && (
          <span className="flex items-center gap-1.5">
            <span className="text-text-muted">MEM</span>
            <TuiProgress
              value={memPct}
              width={10}
              color={memPct > 90 ? 'error' : memPct > 70 ? 'warn' : 'ok'}
              showPercent={false}
            />
            <span className="text-text-muted">{Math.round(memPct)}%</span>
          </span>
        )}
      </div>
    </TuiBox>
  );
}
