'use client';

import { useState } from 'react';
import { TuiBox, TuiSkeleton } from '@/components/tui';
import { useLatestDigest, useDigestDates, useDigestByDate } from '@/hooks/use-digest';

export function DigestViewer() {
  const [selectedDate, setSelectedDate] = useState('');
  const { data: dates, isLoading: datesLoading } = useDigestDates();
  const { data: latestDigest, isLoading: latestLoading } = useLatestDigest();
  const { data: dateDigest, isLoading: dateLoading } = useDigestByDate(selectedDate);

  const digest = selectedDate ? dateDigest : latestDigest;
  const isLoading = datesLoading || latestLoading || (selectedDate ? dateLoading : false);

  return (
    <TuiBox title="DAILY DIGEST">
      {/* Date selector */}
      <div className="flex items-center justify-between mb-2">
        {dates && dates.length > 0 && (
          <select
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-bright focus:outline-none"
          >
            <option value="">latest</option>
            {dates.map((date) => (
              <option key={date} value={date}>{date}</option>
            ))}
          </select>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-1">
          {Array.from({ length: 5 }).map((_, i) => (
            <TuiSkeleton key={i} width={50} />
          ))}
        </div>
      ) : digest ? (
        <div className="space-y-2">
          <span className="text-text-muted">{digest.date}</span>
          <p className="text-text-bright whitespace-pre-wrap">{digest.digest}</p>

          {digest.key_events && digest.key_events.length > 0 && (
            <div>
              <span className="text-text-muted block mb-1">KEY EVENTS</span>
              {digest.key_events.map((event, i) => (
                <div key={i} className="text-text-secondary">{'  '}- {event}</div>
              ))}
            </div>
          )}

          <span className="text-text-muted">filed by: {digest.filed_by}</span>
        </div>
      ) : (
        <span className="text-text-muted">no digest available</span>
      )}
    </TuiBox>
  );
}
