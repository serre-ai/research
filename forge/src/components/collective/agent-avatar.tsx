'use client';

import { clsx } from 'clsx';
import { getAgent } from '@/lib/agents';

interface AgentAvatarProps {
  agentId: string;
  size?: 'sm' | 'md' | 'lg';
  showStatus?: boolean;
  status?: 'active' | 'idle' | 'offline';
  className?: string;
}

const sizes = {
  sm: 'h-6 w-6 text-[9px]',
  md: 'h-8 w-8 text-[11px]',
  lg: 'h-12 w-12 text-sm',
};

const statusColors = {
  active: '#10b981',
  idle: '#f59e0b',
  offline: '#737373',
};

export function AgentAvatar({ agentId, size = 'md', showStatus, status = 'idle', className }: AgentAvatarProps) {
  const agent = getAgent(agentId);
  const color = agent?.color ?? '#737373';
  const monogram = (agent?.displayName ?? agentId).slice(0, 2).toUpperCase();

  return (
    <div className={clsx('relative inline-flex shrink-0', className)}>
      <div
        className={clsx(
          'flex items-center justify-center border-2 bg-bg font-mono font-bold text-text-bright',
          sizes[size],
        )}
        style={{ borderColor: color }}
        title={agent?.displayName ?? agentId}
      >
        {monogram}
      </div>
      {showStatus && (
        <span
          className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 border border-bg"
          style={{ backgroundColor: statusColors[status], borderRadius: '50%' }}
        />
      )}
    </div>
  );
}
