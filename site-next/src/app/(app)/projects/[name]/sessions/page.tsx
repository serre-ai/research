'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ArrowRight, Radio, Filter } from 'lucide-react';
import { useSessions } from '@/hooks';
import { DispatchSessionDialog } from '@/components/dispatch-session-dialog';
import { Card } from '@/components/ui/card';
import { StatusDot } from '@/components/ui/status-dot';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Label } from '@/components/ui/label';
import type { StatusKey } from '@/lib/constants';
import type { Session } from '@/lib/types';
import { formatDuration, formatTokens, formatCost, relativeTime } from '@/lib/format';

function sessionStatusKey(status: string): StatusKey {
  switch (status) {
    case 'completed':
    case 'success':
      return 'ok';
    case 'running':
    case 'in_progress':
      return 'warn';
    case 'failed':
    case 'error':
      return 'error';
    default:
      return 'idle';
  }
}

function SessionRowSkeleton() {
  return (
    <Card className="flex items-center justify-between">
      <div className="flex items-center gap-4">
        <Skeleton className="h-2 w-2 rounded-full" />
        <div className="space-y-1.5">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-3 w-32" />
        </div>
      </div>
      <div className="flex items-center gap-6">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-12" />
        <Skeleton className="h-3 w-12" />
      </div>
    </Card>
  );
}

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

function SessionRow({ session, projectName }: { session: Session; projectName: string }) {
  const statusKey = sessionStatusKey(session.status);

  return (
    <Link
      href={`/projects/${projectName}/sessions/${session.id}`}
      className="group block hover:no-underline"
    >
      <Card className="flex items-center justify-between transition-colors group-hover:border-border-strong">
        <div className="flex items-center gap-4">
          <StatusDot
            status={statusKey}
            pulse={session.status === 'running' || session.status === 'in_progress'}
          />
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{session.agent_type}</Badge>
              <span className="font-mono text-xs text-text-muted">
                {relativeTime(session.started_at)}
              </span>
            </div>
            <span className="mt-0.5 block font-mono text-[10px] text-text-muted">
              {session.id.slice(0, 8)}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-6">
          {session.duration_seconds != null && (
            <span className="font-mono text-xs tabular-nums text-text-secondary">
              {formatDuration(session.duration_seconds)}
            </span>
          )}
          {session.token_usage != null && (
            <span className="font-mono text-xs tabular-nums text-text-muted">
              {formatTokens(session.token_usage)} tokens
            </span>
          )}
          {session.cost != null && (
            <span className="font-mono text-xs tabular-nums text-text-secondary">
              {formatCost(session.cost)}
            </span>
          )}
          <ArrowRight className="h-4 w-4 text-text-muted opacity-0 transition-opacity group-hover:opacity-100" />
        </div>
      </Card>
    </Link>
  );
}

export default function SessionsPage() {
  const { name } = useParams<{ name: string }>();
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

  return (
    <div>
      {/* Filter bar */}
      <div className="mb-6 flex items-center gap-6">
        <DispatchSessionDialog projectName={name} />
        {sessions && sessions.length > 0 && (
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

      {/* Content */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <SessionRowSkeleton key={i} />
          ))}
        </div>
      ) : error ? (
        <Card>
          <p className="text-sm text-[--color-status-error]">
            Failed to load sessions: {error.message}
          </p>
        </Card>
      ) : filtered.length > 0 ? (
        <div className="space-y-3">
          {(agentFilter || statusFilter) && (
            <p className="font-mono text-xs text-text-muted">
              Showing {filtered.length} of {sessions?.length ?? 0} sessions
            </p>
          )}
          {filtered.map((session) => (
            <SessionRow key={session.id} session={session} projectName={name} />
          ))}
        </div>
      ) : sessions && sessions.length > 0 ? (
        <EmptyState
          icon={Filter}
          message="No matching sessions"
          description="Try adjusting your filters"
        />
      ) : (
        <EmptyState
          icon={Radio}
          message="No sessions yet"
          description="Sessions will appear here once the daemon runs"
        />
      )}
    </div>
  );
}
