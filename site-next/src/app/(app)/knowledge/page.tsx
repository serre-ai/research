'use client';

import { useState, useMemo } from 'react';
import { Brain } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/ui/empty-state';
import { ClaimCard } from '@/components/knowledge/claim-card';
import { ClaimDetail } from '@/components/knowledge/claim-detail';
import { KnowledgeGraphViz } from '@/components/knowledge/knowledge-graph-viz';
import { KnowledgeSearch } from '@/components/knowledge/knowledge-search';
import { useKnowledgeClaims, useKnowledgeSubgraph, useKnowledgeStats } from '@/hooks';
import { useKnowledgeSnapshot } from '@/hooks/use-knowledge-mutations';
import type { ClaimType } from '@/lib/knowledge-types';

const CLAIM_TYPES: ClaimType[] = [
  'hypothesis',
  'finding',
  'definition',
  'proof',
  'citation',
  'method',
  'result',
  'observation',
  'decision',
  'question',
];

export default function KnowledgeBrowserPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [projectFilter, setProjectFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const filters = useMemo(() => {
    const f: { project?: string; type?: string; limit?: number } = { limit: 50 };
    if (projectFilter) f.project = projectFilter;
    if (typeFilter) f.type = typeFilter;
    return f;
  }, [projectFilter, typeFilter]);

  const { data: claims, isLoading: claimsLoading } = useKnowledgeClaims(filters);
  const { data: subgraph } = useKnowledgeSubgraph(selectedId, 2);
  const { data: stats } = useKnowledgeStats();
  const snapshot = useKnowledgeSnapshot();

  const projects = stats?.projects ?? [];

  return (
    <div className="flex gap-6" style={{ minHeight: 'calc(100vh - 220px)' }}>
      {/* Left panel — claim list */}
      <div className="w-2/5 flex flex-col min-w-0">
        {/* Filter bar */}
        <div className="flex gap-2 mb-4">
          <select
            value={projectFilter}
            onChange={(e) => setProjectFilter(e.target.value)}
            className="flex-1 border border-border bg-bg-elevated px-2 py-1.5 font-mono text-xs text-text-secondary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">All projects</option>
            {projects.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="flex-1 border border-border bg-bg-elevated px-2 py-1.5 font-mono text-xs text-text-secondary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">All types</option>
            {CLAIM_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => snapshot.mutate(projectFilter || 'reasoning-gaps')}
            disabled={snapshot.isPending}
            className="shrink-0"
          >
            {snapshot.isPending ? 'Snapshotting...' : 'Snapshot'}
          </Button>
        </div>

        <div className="mb-4">
          <KnowledgeSearch onSelectClaim={setSelectedId} />
        </div>

        {/* Claim list */}
        <div className="flex-1 overflow-y-auto space-y-2">
          {claimsLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-28 w-full" />
            ))
          ) : claims && claims.length > 0 ? (
            claims.map((claim) => (
              <ClaimCard
                key={claim.id}
                claim={claim}
                isSelected={claim.id === selectedId}
                onClick={() => setSelectedId(claim.id)}
              />
            ))
          ) : (
            <EmptyState
              icon={Brain}
              message="No claims found"
              description="Adjust filters or wait for claims to be added."
            />
          )}
        </div>
      </div>

      {/* Right panel — graph + detail */}
      <div className="w-3/5 flex flex-col min-w-0 space-y-4">
        {selectedId && subgraph ? (
          <>
            <KnowledgeGraphViz
              subgraph={subgraph}
              selectedId={selectedId}
              onSelectClaim={setSelectedId}
            />
            <ClaimDetail claimId={selectedId} />
          </>
        ) : (
          <EmptyState
            icon={Brain}
            message="Select a claim"
            description="Choose a claim from the list to view its subgraph and evidence chain."
          />
        )}
      </div>
    </div>
  );
}
