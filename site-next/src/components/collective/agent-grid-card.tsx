'use client';

import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { AgentAvatar } from './agent-avatar';
import { TrustBar } from './trust-bar';
import type { AgentMeta } from '@/lib/agents';

interface AgentGridCardProps {
  agent: AgentMeta;
  avgTrust?: number;
  brierScore?: number;
  interactions?: number;
}

export function AgentGridCard({ agent, avgTrust, brierScore, interactions }: AgentGridCardProps) {
  return (
    <Link href={`/collective/agents/${agent.id}`}>
      <Card className="transition-colors hover:bg-bg-hover cursor-pointer space-y-3">
        <div className="flex items-center gap-3">
          <AgentAvatar agentId={agent.id} size="lg" />
          <div>
            <p className="font-mono text-sm font-semibold text-text-bright">{agent.displayName}</p>
            <p className="font-mono text-[10px] text-text-muted">{agent.role}</p>
            <p className="font-mono text-[10px] text-text-muted">{agent.model}</p>
          </div>
        </div>
        {avgTrust !== undefined && (
          <div>
            <span className="font-mono text-[10px] text-text-muted">Avg Trust</span>
            <TrustBar value={avgTrust} />
          </div>
        )}
        <div className="flex justify-between font-mono text-[10px]">
          {brierScore !== undefined && (
            <span className="text-text-muted">
              Brier: <span className="text-text-secondary">{brierScore.toFixed(3)}</span>
            </span>
          )}
          {interactions !== undefined && (
            <span className="text-text-muted">
              {interactions} interactions
            </span>
          )}
        </div>
      </Card>
    </Link>
  );
}
