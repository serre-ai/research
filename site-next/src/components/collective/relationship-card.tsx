'use client';

import { Card } from '@/components/ui/card';
import { AgentAvatar } from './agent-avatar';
import { AgentNameBadge } from './agent-name-badge';
import { TrustBar } from './trust-bar';
import type { AgentRelationship } from '@/lib/collective-types';

interface RelationshipCardProps {
  relationship: AgentRelationship;
}

function dynamicText(r: AgentRelationship): string {
  if (r.trust >= 0.9) return 'Deep trust';
  if (r.trust >= 0.75) return 'Strong alignment';
  if (r.trust >= 0.5) return 'Working relationship';
  if (r.trust >= 0.25) return 'Developing rapport';
  return 'New connection';
}

export function RelationshipCard({ relationship }: RelationshipCardProps) {
  return (
    <Card className="space-y-3">
      <div className="flex items-center gap-3">
        <AgentAvatar agentId={relationship.agent} size="md" />
        <div>
          <AgentNameBadge agentId={relationship.agent} />
          <p className="font-mono text-[10px] text-text-muted mt-0.5">{dynamicText(relationship)}</p>
        </div>
      </div>
      <div className="space-y-2">
        <div>
          <span className="font-mono text-[10px] text-text-muted">Trust</span>
          <TrustBar value={relationship.trust} />
        </div>
        <div className="flex justify-between font-mono text-[10px]">
          <span className="text-text-muted">Agreement</span>
          <span className="text-text-secondary">{(relationship.agreement_rate * 100).toFixed(0)}%</span>
        </div>
        <div className="flex justify-between font-mono text-[10px]">
          <span className="text-text-muted">Interactions</span>
          <span className="text-text-secondary">{relationship.interactions}</span>
        </div>
      </div>
    </Card>
  );
}
