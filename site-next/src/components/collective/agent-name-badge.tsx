'use client';

import { getAgent, getAgentColor } from '@/lib/agents';
import { clsx } from 'clsx';

interface AgentNameBadgeProps {
  agentId: string;
  className?: string;
}

export function AgentNameBadge({ agentId, className }: AgentNameBadgeProps) {
  const agent = getAgent(agentId);
  const color = getAgentColor(agentId);

  return (
    <span className={clsx('inline-flex items-center gap-1.5 font-mono text-xs', className)}>
      <span
        className="inline-block h-2 w-2 shrink-0"
        style={{ backgroundColor: color, borderRadius: '50%' }}
      />
      <span className="text-text-bright">{agent?.displayName ?? agentId}</span>
    </span>
  );
}
