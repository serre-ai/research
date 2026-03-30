'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Users, Play } from 'lucide-react';
import { AgentNameBadge } from './agent-name-badge';
import { RitualTypeBadge } from './ritual-type-badge';
import type { Ritual } from '@/lib/ritual-types';

interface RitualCardProps {
  ritual: Ritual;
  onStart?: (id: number) => void;
  isStarting?: boolean;
}

const statusVariant: Record<string, 'default' | 'success' | 'warning' | 'error'> = {
  scheduled: 'default',
  active: 'warning',
  completed: 'success',
  cancelled: 'error',
};

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function RitualCard({ ritual, onStart, isStarting }: RitualCardProps) {
  return (
    <Card className="flex items-start justify-between gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <RitualTypeBadge type={ritual.ritual_type} />
          <Badge variant={statusVariant[ritual.status] ?? 'default'}>
            {ritual.status}
          </Badge>
        </div>
        <p className="font-mono text-xs text-text-secondary mb-2">
          {formatTime(ritual.scheduled_for)}
        </p>
        <div className="flex items-center gap-3">
          <AgentNameBadge agentId={ritual.facilitator} />
          <span className="flex items-center gap-1 font-mono text-[10px] text-text-muted">
            <Users className="h-3 w-3" /> {ritual.participants.length}
          </span>
        </div>
        {ritual.status === 'completed' && ritual.outcome && (
          <p className="font-mono text-xs text-text-muted mt-2 truncate">{ritual.outcome}</p>
        )}
      </div>
      {ritual.status === 'scheduled' && onStart && (
        <Button
          variant="outline"
          size="sm"
          disabled={isStarting}
          onClick={() => onStart(ritual.id)}
        >
          <Play className="h-3 w-3 mr-1" />
          Start
        </Button>
      )}
    </Card>
  );
}
