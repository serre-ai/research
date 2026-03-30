'use client';

import { useMemo, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Filter } from 'lucide-react';
import { useSessions } from '@/hooks';
import { DispatchSessionDialog } from '@/components/dispatch-session-dialog';
import { TuiPanel, TuiList, TuiStatusDot, TuiBadge } from '@/components/tui';
import { Label } from '@/components/ui/label';
import type { Session } from '@/lib/types';
import { mapStatusToKey } from '@/lib/dashboard-helpers';
import { formatDuration, formatCost, relativeTime } from '@/lib/format';

function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      <Label>{label}</Label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-secondary outline-none focus:border-border-strong"
      >
        <option value="">All</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );
}

export default function SessionsPage() {
  const { name } = useParams<{ name: string }>();
  const router = useRouter();
  const { data: sessions, isLoading, error } = useSessions(name);

  const [agentFilter, setAgentFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Compute unique values for filter dropdowns
  const agentTypes = useMemo(() => {
    if (!sessions) return [];
    return [...new Set(sessions.map((s) => s.agent_type))].sort();
  }, [sessions]);

  const statuses = useMemo(() => {
    if (!sessions) return [];
    return [...new Set(sessions.map((s) => s.status))].sort();
  }, [sessions]);

  // Apply client-side filters
  const filtered = useMemo(() => {
    if (!sessions) return [];
    return sessions.filter((s) => {
      if (agentFilter && s.agent_type !== agentFilter) return false;
      if (statusFilter && s.status !== statusFilter) return false;
      return true;
    });
  }, [sessions, agentFilter, statusFilter]);

  const navigateToSession = useCallback(
    (session: Session) => router.push(`/projects/${name}/sessions/${session.id}`),
    [router, name],
  );

  return (
    <div>
      {/* Filter bar */}
      <div className="mb-6 flex items-center gap-6">
        <DispatchSessionDialog projectName={name} />
        {(sessions ?? []).length > 0 && (
          <>
            <Filter className="h-4 w-4 text-text-muted" />
            <FilterSelect
              label="Agent"
              value={agentFilter}
              options={agentTypes}
              onChange={setAgentFilter}
            />
            <FilterSelect
              label="Status"
              value={statusFilter}
              options={statuses}
              onChange={setStatusFilter}
            />
            {(agentFilter || statusFilter) && (
              <button
                type="button"
                onClick={() => {
                  setAgentFilter('');
                  setStatusFilter('');
                }}
                className="font-mono text-xs text-text-muted hover:text-text-secondary"
              >
                Clear filters
              </button>
            )}
          </>
        )}
      </div>

      {/* Filter count */}
      {(agentFilter || statusFilter) && filtered.length > 0 && (
        <p className="mb-2 font-mono text-xs text-text-muted">
          Showing {filtered.length} of {(sessions ?? []).length} sessions
        </p>
      )}

      {/* Sessions list */}
      {error ? (
        <span className="text-[--color-status-error]">
          failed to load: {error.message ?? 'error'}
        </span>
      ) : (
        <TuiPanel
          id="sessions"
          title="SESSIONS"
          order={1}
          itemCount={filtered.length}
          onActivateItem={(idx) => navigateToSession(filtered[idx])}
        >
          <TuiList
            panelId="sessions"
            items={filtered}
            keyFn={(s) => s.id}
            onActivate={navigateToSession}
            emptyMessage={isLoading ? 'loading...' : 'no sessions'}
            renderItem={(session, _i, active) => (
              <div className="flex items-center justify-between gap-2">
                <span className="flex items-center gap-2">
                  <TuiStatusDot status={mapStatusToKey(session.status)} />
                  <TuiBadge color="accent">{session.agent_type}</TuiBadge>
                  <span className={active ? 'text-text-bright' : 'text-text-muted'}>
                    {relativeTime(session.started_at)}
                  </span>
                </span>
                <span className="flex items-center gap-3">
                  {session.duration_seconds != null && (
                    <span className="text-text-secondary tabular-nums">
                      {formatDuration(session.duration_seconds)}
                    </span>
                  )}
                  {session.cost != null && (
                    <span className="text-text-secondary tabular-nums">
                      {formatCost(session.cost)}
                    </span>
                  )}
                </span>
              </div>
            )}
          />
        </TuiPanel>
      )}
    </div>
  );
}
