'use client';

import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Badge } from '@/components/ui/badge';
import { Gavel } from 'lucide-react';
import { AgentNameBadge } from './agent-name-badge';
import { ProposalTypeBadge } from './proposal-type-badge';
import { useGovernanceProposal } from '@/hooks/use-governance';

const positionColors = {
  support: '#10b981',
  oppose: '#ef4444',
  abstain: '#737373',
};

interface ProposalDetailProps {
  proposalId: number | null;
}

export function ProposalDetail({ proposalId }: ProposalDetailProps) {
  const { data: detail, isLoading } = useGovernanceProposal(proposalId);

  if (isLoading) {
    return (
      <Card className="space-y-4">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-3 w-40" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </Card>
    );
  }

  if (!detail) {
    return (
      <Card>
        <EmptyState
          icon={Gavel}
          message="Select a proposal"
          description="Choose a proposal from the list to view details"
        />
      </Card>
    );
  }

  const { tally, votes } = detail;
  const total = tally.total_votes || 1;

  return (
    <div className="space-y-4">
      {/* Header */}
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <ProposalTypeBadge type={detail.proposal_type} />
          <span className="font-mono text-[10px] text-text-muted uppercase">{detail.status}</span>
        </div>
        <h2 className="font-mono text-lg font-semibold text-text-bright mb-2">{detail.title}</h2>
        <AgentNameBadge agentId={detail.proposer} />
      </Card>

      {/* Body */}
      <Card>
        <p className="font-mono text-sm text-text-secondary whitespace-pre-wrap">{detail.proposal}</p>
      </Card>

      {/* Tally */}
      <Card>
        <Label>Vote Tally ({tally.total_votes} votes)</Label>
        <div className="mt-3 mb-2">
          <div className="flex h-3 w-full overflow-hidden border border-border">
            {tally.votes_for > 0 && (
              <div
                className="h-full"
                style={{ width: `${(tally.votes_for / total) * 100}%`, backgroundColor: '#10b981' }}
              />
            )}
            {tally.votes_against > 0 && (
              <div
                className="h-full"
                style={{ width: `${(tally.votes_against / total) * 100}%`, backgroundColor: '#ef4444' }}
              />
            )}
            {tally.votes_abstain > 0 && (
              <div
                className="h-full"
                style={{ width: `${(tally.votes_abstain / total) * 100}%`, backgroundColor: '#737373' }}
              />
            )}
          </div>
          <div className="flex gap-4 mt-1.5 font-mono text-[10px] text-text-muted">
            <span style={{ color: '#10b981' }}>{tally.votes_for} support</span>
            <span style={{ color: '#ef4444' }}>{tally.votes_against} oppose</span>
            <span>{tally.votes_abstain} abstain</span>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-2">
          <Badge variant={tally.quorum_reached ? 'success' : 'warning'}>
            {tally.quorum_reached ? 'Quorum reached' : 'No quorum'}
          </Badge>
          {tally.outcome && (
            <span className="font-mono text-xs text-text-secondary">{tally.outcome}</span>
          )}
        </div>
      </Card>

      {/* Individual votes */}
      {votes.length > 0 && (
        <Card>
          <Label>Votes ({votes.length})</Label>
          <div className="mt-3 space-y-2">
            {votes.map((vote, i) => {
              const color = positionColors[vote.position] ?? '#737373';
              return (
                <div key={i} className="border border-border p-3" style={{ borderLeft: `3px solid ${color}` }}>
                  <div className="flex items-center justify-between mb-2">
                    <AgentNameBadge agentId={vote.voter} />
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] font-medium" style={{ color }}>
                        {vote.position.toUpperCase()}
                      </span>
                      {vote.confidence !== undefined && (
                        <span className="font-mono text-[10px] text-text-muted">
                          {(vote.confidence * 100).toFixed(0)}% conf
                        </span>
                      )}
                    </div>
                  </div>
                  {vote.rationale && (
                    <p className="font-mono text-xs text-text-secondary">{vote.rationale}</p>
                  )}
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
}
