'use client';

import { clsx } from 'clsx';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { AgentNameBadge } from './agent-name-badge';
import { ProposalTypeBadge } from './proposal-type-badge';
import type { Proposal } from '@/lib/governance-types';

interface ProposalCardProps {
  proposal: Proposal;
  isSelected?: boolean;
  onClick?: () => void;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'now';
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}

const statusVariant: Record<string, 'default' | 'success' | 'warning' | 'error'> = {
  proposed: 'default',
  voting: 'warning',
  accepted: 'success',
  rejected: 'error',
};

export function ProposalCard({ proposal, isSelected, onClick }: ProposalCardProps) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'w-full text-left border-b border-border p-4 transition-colors',
        isSelected ? 'bg-bg-elevated' : 'hover:bg-bg-hover',
      )}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <ProposalTypeBadge type={proposal.proposal_type} />
        <Badge variant={statusVariant[proposal.status] ?? 'default'}>
          {proposal.status}
        </Badge>
        <span className="font-mono text-[10px] text-text-muted">{timeAgo(proposal.created_at)}</span>
      </div>
      <p className="font-mono text-sm text-text-bright truncate">{proposal.title}</p>
      <div className="flex items-center gap-3 mt-2">
        <AgentNameBadge agentId={proposal.proposer} />
        <span className="flex items-center gap-1 font-mono text-[10px] text-text-muted">
          <ThumbsUp className="h-3 w-3" /> {proposal.votes_for}
        </span>
        <span className="flex items-center gap-1 font-mono text-[10px] text-text-muted">
          <ThumbsDown className="h-3 w-3" /> {proposal.votes_against}
        </span>
      </div>
    </button>
  );
}
