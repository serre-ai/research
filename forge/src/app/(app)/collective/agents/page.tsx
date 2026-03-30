'use client';

import { useState } from 'react';
import { Grid3X3, Share2 } from 'lucide-react';
import { clsx } from 'clsx';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { AgentGridCard } from '@/components/collective/agent-grid-card';
import { SimpleTrustGraph } from '@/components/collective/simple-trust-graph';
import { useAgentGraph } from '@/hooks/use-collective';
import { AGENTS } from '@/lib/agents';

type View = 'grid' | 'graph';

export default function AgentsPage() {
  const [view, setView] = useState<View>('grid');
  const { data: graph, isLoading } = useAgentGraph();

  // Compute per-agent stats from graph edges
  const agentStats = new Map<string, { avgTrust: number; interactions: number }>();
  if (graph) {
    for (const agent of Object.keys(AGENTS)) {
      const edges = graph.edges.filter((e) => e.source === agent || e.target === agent);
      const avgTrust = edges.length > 0 ? edges.reduce((s, e) => s + e.trust, 0) / edges.length : 0;
      const interactions = edges.reduce((s, e) => s + e.interactions, 0);
      agentStats.set(agent, { avgTrust, interactions });
    }
  }

  return (
    <div className="space-y-4">
      {/* View toggle */}
      <div className="flex gap-1">
        <button
          onClick={() => setView('grid')}
          className={clsx(
            'flex items-center gap-1.5 px-3 py-1.5 font-mono text-xs border transition-colors',
            view === 'grid'
              ? 'border-primary bg-bg-elevated text-text-bright'
              : 'border-border text-text-muted hover:text-text-secondary',
          )}
        >
          <Grid3X3 className="h-3.5 w-3.5" /> Grid
        </button>
        <button
          onClick={() => setView('graph')}
          className={clsx(
            'flex items-center gap-1.5 px-3 py-1.5 font-mono text-xs border transition-colors',
            view === 'graph'
              ? 'border-primary bg-bg-elevated text-text-bright'
              : 'border-border text-text-muted hover:text-text-secondary',
          )}
        >
          <Share2 className="h-3.5 w-3.5" /> Graph
        </button>
      </div>

      {view === 'grid' ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading
            ? Array.from({ length: 9 }).map((_, i) => (
                <Card key={i} className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Skeleton className="h-12 w-12" />
                    <div className="space-y-1">
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-3 w-16" />
                    </div>
                  </div>
                  <Skeleton className="h-2 w-full" />
                </Card>
              ))
            : Object.values(AGENTS).map((agent) => {
                const stats = agentStats.get(agent.id);
                return (
                  <AgentGridCard
                    key={agent.id}
                    agent={agent}
                    avgTrust={stats?.avgTrust}
                    interactions={stats?.interactions}
                  />
                );
              })}
        </div>
      ) : (
        <Card>
          {isLoading || !graph ? (
            <div className="flex items-center justify-center py-24">
              <Skeleton className="h-64 w-64" />
            </div>
          ) : (
            <SimpleTrustGraph graph={graph} />
          )}
        </Card>
      )}
    </div>
  );
}
