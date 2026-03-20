'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ui/progress-bar';
import { Skeleton } from '@/components/ui/skeleton';
import { Label } from '@/components/ui/label';
import { ClaimTypeBadge } from './claim-type-badge';
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
      <Card className="space-y-4">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-2 w-full" />
      </Card>
    );
  }

  if (!claim) return null;

  return (
    <Card className="space-y-4">
      <div className="flex items-center gap-2">
        <ClaimTypeBadge type={claim.type} />
        <span className="font-mono text-[10px] text-text-muted">{claim.project}</span>
      </div>

      <p className="font-mono text-sm text-text-bright">{claim.statement}</p>

      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <Label>Confidence</Label>
          <span className="font-mono text-xs text-text-secondary">
            {Math.round(claim.confidence * 100)}%
          </span>
        </div>
        <ProgressBar value={claim.confidence * 100} />
        <ConfidenceEditor claimId={claimId} currentConfidence={claim.confidence} />
      </div>

      <div className="space-y-1">
        <Label>Source</Label>
        <p className="font-mono text-xs text-text-secondary">{claim.source}</p>
      </div>

      <div className="space-y-1">
        <p className="font-mono text-[10px] text-text-muted">
          Created {relativeTime(claim.created_at)} &middot; Updated {relativeTime(claim.updated_at)}
        </p>
      </div>

      {/* Evidence chain */}
      <div className="space-y-2">
        <Label>Evidence Chain</Label>
        {evidenceLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        ) : evidence?.chain && evidence.chain.length > 0 ? (
          <ol className="space-y-2">
            {evidence.chain.map((link, i) => (
              <li
                key={link.claim.id}
                className="flex items-start gap-2 border-l-2 border-border pl-3"
              >
                <span className="font-mono text-[10px] text-text-muted tabular-nums">
                  {i + 1}.
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">
                      {link.relation.relation_type.replace('_', ' ')}
                    </Badge>
                    <ClaimTypeBadge type={link.claim.type} />
                  </div>
                  <p className="mt-1 font-mono text-xs text-text-secondary line-clamp-2">
                    {link.claim.statement}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        ) : (
          <p className="font-mono text-xs text-text-muted">No evidence chain found.</p>
        )}
      </div>
    </Card>
  );
}
