'use client';

import { TuiBadge, TuiProgress, TuiSkeleton } from '@/components/tui';
import { ConfidenceEditor } from './confidence-editor';
import { relativeTime } from '@/lib/format';
import { useKnowledgeClaim, useKnowledgeEvidence } from '@/hooks';

interface ClaimDetailProps {
  claimId: string;
}

export function ClaimDetail({ claimId }: ClaimDetailProps) {
  const { data: claim, isLoading: claimLoading } = useKnowledgeClaim(claimId);
  const { data: evidence, isLoading: evidenceLoading } = useKnowledgeEvidence(claimId);

  if (claimLoading) {
    return (
      <div className="space-y-2">
        <TuiSkeleton width={20} />
        <TuiSkeleton width={50} />
        <TuiSkeleton width={30} />
      </div>
    );
  }

  if (!claim) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <TuiBadge color="accent">{claim.type}</TuiBadge>
        <span className="text-text-muted">{claim.project}</span>
      </div>

      <p className="text-text-bright">{claim.statement}</p>

      <div className="flex items-center gap-2">
        <span className="text-text-muted">confidence</span>
        <TuiProgress value={claim.confidence * 100} width={12} showPercent={false} />
        <span className="text-text-secondary">{Math.round(claim.confidence * 100)}%</span>
        <ConfidenceEditor claimId={claimId} currentConfidence={claim.confidence} />
      </div>

      <div>
        <span className="text-text-muted">source: </span>
        <span className="text-text-secondary">{claim.source}</span>
      </div>

      <span className="text-text-muted">
        created {relativeTime(claim.created_at)} · updated {relativeTime(claim.updated_at)}
      </span>

      {/* Evidence chain */}
      <div>
        <span className="text-text-muted block mb-1">EVIDENCE CHAIN</span>
        {evidenceLoading ? (
          <div className="space-y-1">
            <TuiSkeleton width={40} />
            <TuiSkeleton width={35} />
          </div>
        ) : evidence?.chain && evidence.chain.length > 0 ? (
          <div className="space-y-1">
            {evidence.chain.map((link, i) => (
              <div key={link.claim.id} className="border-l border-border pl-2">
                <span className="text-text-muted tabular-nums">{i + 1}. </span>
                <TuiBadge color="muted">{link.relation.relation_type.replaceAll('_', ' ')}</TuiBadge>
                {' '}
                <TuiBadge color="accent">{link.claim.type}</TuiBadge>
                <span className="text-text-secondary block mt-0.5">{link.claim.statement.slice(0, 100)}</span>
              </div>
            ))}
          </div>
        ) : (
          <span className="text-text-muted">no evidence chain</span>
        )}
      </div>
    </div>
  );
}
