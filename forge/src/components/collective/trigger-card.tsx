'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AgentNameBadge } from './agent-name-badge';
import { Check } from 'lucide-react';
import type { Trigger, TriggerType } from '@/lib/trigger-types';

interface TriggerCardProps {
  trigger: Trigger;
  onAck?: (id: number) => void;
  isAcking?: boolean;
}

const typeLabels: Record<TriggerType, { label: string; variant: 'default' | 'warning' | 'error' | 'success' }> = {
  'forum:unanimous_support': { label: 'Unanimous Support', variant: 'success' },
  'forum:stalled': { label: 'Stalled Thread', variant: 'warning' },
  'governance:proposed': { label: 'New Proposal', variant: 'default' },
  'ritual:scheduled': { label: 'Ritual Due', variant: 'warning' },
  'forum:mention': { label: 'Mention', variant: 'default' },
};

function contextSummary(trigger: Trigger): string {
  const ctx = trigger.context;
  switch (trigger.trigger_type) {
    case 'forum:unanimous_support':
      return `"${ctx.title}" — ${ctx.vote_count} votes`;
    case 'forum:stalled':
      return `"${ctx.title}" — stalled`;
    case 'governance:proposed':
      return `"${ctx.title}" by ${ctx.proposer}`;
    case 'ritual:scheduled':
      return `${ctx.ritual_type} scheduled`;
    case 'forum:mention':
      return `Mentioned in "${ctx.title}" by ${ctx.mentioner}`;
    default:
      return JSON.stringify(ctx);
  }
}

export function TriggerCard({ trigger, onAck, isAcking }: TriggerCardProps) {
  const meta = typeLabels[trigger.trigger_type] ?? { label: trigger.trigger_type, variant: 'default' as const };

  return (
    <div className="flex items-start justify-between gap-3 border-b border-border p-3 last:border-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <Badge variant={meta.variant}>{meta.label}</Badge>
          <AgentNameBadge agentId={trigger.agent} />
        </div>
        <p className="font-mono text-xs text-text-secondary truncate">
          {contextSummary(trigger)}
        </p>
      </div>
      {onAck && (
        <Button
          variant="ghost"
          size="sm"
          disabled={isAcking}
          onClick={() => onAck(trigger.id)}
          className="shrink-0"
        >
          <Check className="h-3 w-3" />
        </Button>
      )}
    </div>
  );
}
