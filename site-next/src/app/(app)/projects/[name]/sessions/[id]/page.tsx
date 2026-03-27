'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useSessionDetail, useTranscript } from '@/hooks';
import { TuiBox, TuiStatusDot, TuiBadge, TuiMetric } from '@/components/tui';
import { TranscriptViewer } from '@/components/transcript-viewer';
import { mapStatusToKey } from '@/lib/dashboard-helpers';
import { formatDuration, formatTokens, formatCost } from '@/lib/format';

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
        <span aria-hidden="true">←</span>
        Back to sessions
      </Link>

      {sessionLoading ? (
        <TuiBox title="SESSION">
          <span className="text-text-muted">loading...</span>
        </TuiBox>
      ) : sessionError ? (
        <TuiBox title="SESSION">
          <span className="text-[--color-status-error]">
            failed to load session: {sessionError.message}
          </span>
        </TuiBox>
      ) : session ? (
        <div className="space-y-3">
          {/* Session header */}
          <TuiBox title="SESSION">
            <div className="flex flex-wrap items-center gap-3">
              <TuiBadge color="accent">{session.agent_type}</TuiBadge>
              <TuiStatusDot status={mapStatusToKey(session.status)} />
              <span className="text-text-secondary">{session.status}</span>
              <span className="text-text-muted">
                {formatDateTime(session.started_at)}
              </span>
              {session.ended_at && (
                <>
                  <span className="text-text-muted">&rarr;</span>
                  <span className="text-text-muted">
                    {formatDateTime(session.ended_at)}
                  </span>
                </>
              )}
            </div>
          </TuiBox>

          {/* Metrics */}
          <TuiBox title="METRICS">
            <div className="flex flex-wrap gap-6">
              <TuiMetric
                label="DURATION"
                value={
                  session.duration_seconds != null
                    ? formatDuration(session.duration_seconds)
                    : '--'
                }
              />
              <TuiMetric
                label="TOKENS"
                value={
                  session.token_usage != null
                    ? formatTokens(session.token_usage)
                    : '--'
                }
              />
              <TuiMetric
                label="COST"
                value={
                  session.cost != null ? formatCost(session.cost) : '--'
                }
              />
            </div>
          </TuiBox>

          {/* Transcript */}
          <TuiBox title="TRANSCRIPT">
            {transcriptLoading ? (
              <span className="text-text-muted">loading...</span>
            ) : transcript ? (
              <TranscriptViewer
                lines={transcript.lines ?? []}
                total={transcript.total}
                onLoadMore={handleLoadMore}
              />
            ) : (
              <span className="text-text-muted">no transcript data available</span>
            )}
          </TuiBox>
        </div>
      ) : null}
    </div>
  );
}
