'use client';

import { useState, useMemo } from 'react';
import { TuiBox, TuiPanel, TuiList, TuiSkeleton, TuiBadge } from '@/components/tui';
import { ClaimDetail } from '@/components/knowledge/claim-detail';
import { KnowledgeGraphViz } from '@/components/knowledge/knowledge-graph-viz';
import { KnowledgeSearch } from '@/components/knowledge/knowledge-search';
import { useKnowledgeClaims, useKnowledgeSubgraph, useKnowledgeStats } from '@/hooks';
import type { ClaimType } from '@/lib/knowledge-types';

const CLAIM_TYPES: ClaimType[] = [
  'hypothesis', 'finding', 'definition', 'proof', 'citation',
  'method', 'result', 'observation', 'decision', 'question',
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

  const projects = stats?.projects ?? [];
  const claimList = claims ?? [];

  return (
    <>
      {/* Filters */}
      <div className="flex gap-2 mb-3">
        <select
          value={projectFilter}
          onChange={(e) => setProjectFilter(e.target.value)}
          className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-bright focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="">all projects</option>
          {projects.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-bright focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="">all types</option>
          {CLAIM_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <div className="flex-1">
          <KnowledgeSearch onSelectClaim={setSelectedId} />
        </div>
      </div>

      <div className="grid gap-3 lg:grid-cols-5" style={{ minHeight: 'calc(100vh - 220px)' }}>
        {/* Left: claim list */}
        <div className="lg:col-span-2">
          <TuiPanel
            id="claims"
            title="CLAIMS"
            order={1}
            itemCount={claimList.length}
          >
            {claimsLoading ? (
              <div className="space-y-1">
                {Array.from({ length: 6 }).map((_, i) => (
                  <TuiSkeleton key={i} width={40} />
                ))}
              </div>
            ) : (
              <TuiList
                panelId="claims"
                items={claimList}
                keyFn={(c) => c.id}
                onActivate={(c) => setSelectedId(c.id)}
                emptyMessage="no claims found"
                renderItem={(claim, _i, active) => (
                  <div>
                    <div className="flex items-center gap-2">
                      <TuiBadge color="accent">{claim.type}</TuiBadge>
                      <span className={active ? 'text-text-bright' : 'text-text-secondary'}>
                        {claim.statement.slice(0, 60)}{claim.statement.length > 60 ? '...' : ''}
                      </span>
                    </div>
                    <div className="flex gap-2 text-text-muted mt-0.5">
                      <span>{claim.project}</span>
                      {claim.confidence != null && (
                        <span>{(claim.confidence * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  </div>
                )}
              />
            )}
          </TuiPanel>
        </div>

        {/* Right: graph + detail */}
        <div className="lg:col-span-3 space-y-3">
          {selectedId && subgraph ? (
            <>
              <TuiBox title="KNOWLEDGE GRAPH">
                <KnowledgeGraphViz
                  subgraph={subgraph}
                  selectedId={selectedId}
                  onSelectClaim={setSelectedId}
                />
              </TuiBox>
              <TuiBox title="CLAIM DETAIL">
                <ClaimDetail claimId={selectedId} />
              </TuiBox>
            </>
          ) : (
            <TuiBox title="KNOWLEDGE GRAPH">
              <span className="text-text-muted">select a claim to view its subgraph and evidence chain</span>
            </TuiBox>
          )}
        </div>
      </div>
    </>
  );
}
