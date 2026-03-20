'use client';

import { useState } from 'react';
import { useLatestDigest, useDigestDates, useDigestByDate } from '@/hooks/use-digest';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';

export function DigestViewer() {
  const [selectedDate, setSelectedDate] = useState('');
  const { data: dates, isLoading: datesLoading } = useDigestDates();
  const { data: latestDigest, isLoading: latestLoading } = useLatestDigest();
  const { data: dateDigest, isLoading: dateLoading } = useDigestByDate(selectedDate);

  const digest = selectedDate ? dateDigest : latestDigest;
  const isLoading = datesLoading || latestLoading || (selectedDate ? dateLoading : false);

  if (isLoading) {
    return (
      <Card className="space-y-3">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </Card>
    );
  }

  return (
    <Card className="space-y-4">
      <div className="flex items-center justify-between">
        <Label>Daily Digest</Label>

        {dates && dates.length > 0 && (
          <select
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="font-mono text-xs bg-bg-elevated border border-border text-text-bright px-2 py-1 rounded"
          >
            <option value="">Latest</option>
            {dates.map((date) => (
              <option key={date} value={date}>
                {date}
              </option>
            ))}
          </select>
        )}
      </div>

      {digest ? (
        <div className="space-y-3">
          {/* Date header */}
          <div className="font-mono text-xs text-text-muted">{digest.date}</div>

          {/* Digest text */}
          <p className="font-mono text-sm text-text-bright whitespace-pre-wrap">
            {digest.digest}
          </p>

          {/* Key events */}
          {digest.key_events && digest.key_events.length > 0 && (
            <div className="space-y-2">
              <span className="font-mono text-xs font-medium text-text-secondary">
                Key Events
              </span>
              <ul className="space-y-1">
                {digest.key_events.map((event, i) => (
                  <li
                    key={i}
                    className="font-mono text-xs text-text-secondary pl-4 relative before:content-[''] before:absolute before:left-0 before:top-[0.45em] before:h-1 before:w-1 before:rounded-full before:bg-text-muted"
                  >
                    {event}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Filed by */}
          <div className="font-mono text-[10px] text-text-muted">
            Filed by: {digest.filed_by}
          </div>
        </div>
      ) : (
        <EmptyState
          message="No digest available"
          description="Daily digests will appear here once generated"
        />
      )}
    </Card>
  );
}
