'use client';

import { AgentAvatar } from './agent-avatar';

interface AgentAvatarGroupProps {
  agentIds: string[];
  max?: number;
  size?: 'sm' | 'md';
}

export function AgentAvatarGroup({ agentIds, max = 5, size = 'sm' }: AgentAvatarGroupProps) {
  const visible = agentIds.slice(0, max);
  const overflow = agentIds.length - max;

  return (
    <div className="flex items-center -space-x-1.5">
      {visible.map((id) => (
        <AgentAvatar key={id} agentId={id} size={size} />
      ))}
      {overflow > 0 && (
        <span className="flex h-6 w-6 items-center justify-center border border-border bg-bg-elevated font-mono text-[9px] text-text-muted">
          +{overflow}
        </span>
      )}
    </div>
  );
}
