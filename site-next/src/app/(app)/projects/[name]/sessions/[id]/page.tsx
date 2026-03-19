'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ArrowLeft, Clock, Coins, DollarSign, Activity } from 'lucide-react';
import { useSessionDetail, useTranscript } from '@/hooks';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/ui/status-badge';
import { MetricCard } from '@/components/ui/metric-card';
import { Skeleton } from '@/components/ui/skeleton';
import { Label } from '@/components/ui/label';
import { TranscriptViewer } from '@/components/transcript-viewer';
import type { StatusKey } from '@/lib/constants';
import { formatDuration, formatTokens, formatCost } from '@/lib/format';

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

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

function DetailSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center gap-3">
        <Skeleton className="h-5 w-20" />
        <Skeleton className="h-5 w-16" />
      </div>

      {/* Metric cards skeleton */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="flex flex-col gap-2">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-8 w-20" />
          </Card>
        ))}
      </div>

      {/* Transcript skeleton */}
      <div className="space-y-2">
        <Skeleton className="h-3 w-24" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    </div>
  );
}

const PAGE_SIZE = 100;

export default function SessionDetailPage() {
  const { name, id } = useParams<{ name: string; id: string }>();
  const { data: session, isLoading: sessionLoading, error: sessionError } = useSessionDetail(id);

  const [limit, setLimit] = useState(PAGE_SIZE);
  const {
    data: transcript,
    isLoading: transcriptLoading,
  } = useTranscript(id, 0, limit);

  const handleLoadMore = useCallback(() => {
    setLimit((prev) => prev + PAGE_SIZE);
  }, []);

  return (
    <div>
      {/* Back link */}
      <Link
        href={`/projects/${name}/sessions`}
        className="mb-6 inline-flex items-center gap-1.5 font-mono text-xs text-text-muted hover:text-text-secondary hover:no-underline"
      >
        <ArrowLeft className="h-3 w-3" />
        Back to sessions
      </Link>

      {sessionLoading ? (
        <DetailSkeleton />
      ) : sessionError ? (
        <Card>
          <p className="text-sm text-[--color-status-error]">
            Failed to load session: {sessionError.message}
          </p>
        </Card>
      ) : session ? (
        <div className="space-y-6">
          {/* Session header */}
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="outline">{session.agent_type}</Badge>
            <StatusBadge status={sessionStatusKey(session.status)}>
              {session.status}
            </StatusBadge>
            <span className="font-mono text-xs text-text-muted">
              {formatDateTime(session.started_at)}
            </span>
            {session.ended_at && (
              <>
                <span className="font-mono text-xs text-text-muted">&rarr;</span>
                <span className="font-mono text-xs text-text-muted">
                  {formatDateTime(session.ended_at)}
                </span>
              </>
            )}
          </div>

          {/* Metadata cards */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <MetricCard
              label="Duration"
              value={
                session.duration_seconds != null
                  ? formatDuration(session.duration_seconds)
                  : '--'
              }
              icon={Clock}
            />
            <MetricCard
              label="Tokens"
              value={
                session.token_usage != null
                  ? formatTokens(session.token_usage)
                  : '--'
              }
              icon={Coins}
            />
            <MetricCard
              label="Cost"
              value={
                session.cost != null ? formatCost(session.cost) : '--'
              }
              icon={DollarSign}
            />
            <MetricCard
              label="Status"
              value={session.status}
              icon={Activity}
            />
          </div>

          {/* Transcript */}
          <div>
            <Label className="mb-4 block">Transcript</Label>
            {transcriptLoading ? (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : transcript ? (
              <TranscriptViewer
                lines={transcript.lines}
                total={transcript.total}
                onLoadMore={handleLoadMore}
              />
            ) : (
              <div className="flex items-center justify-center py-12">
                <p className="font-mono text-sm text-text-muted">
                  No transcript data available
                </p>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
