'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { DeadLetter } from '@/lib/event-types';

function relativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;

  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

interface DeadLetterCardProps {
  deadLetter: DeadLetter;
  onRetry: (id: string) => void;
  isRetrying?: boolean;
}

export function DeadLetterCard({ deadLetter, onRetry, isRetrying }: DeadLetterCardProps) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <Badge variant="warning">{deadLetter.event_type}</Badge>
        <span className="font-mono text-[10px] text-text-muted">
          {deadLetter.attempts} attempt{deadLetter.attempts !== 1 ? 's' : ''}
        </span>
      </div>

      <p className="mt-2 line-clamp-2 font-mono text-xs text-[--color-status-error]">
        {deadLetter.error}
      </p>

      <div className="mt-3 flex items-center justify-between">
        <span className="font-mono text-[10px] text-text-muted">
          Last attempt: {relativeTime(deadLetter.last_attempt_at)}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={isRetrying}
          onClick={() => onRetry(deadLetter.id)}
        >
          Retry
        </Button>
      </div>
    </Card>
  );
}
