'use client';

import { useState } from 'react';
import { TuiBox, TuiSkeleton } from '@/components/tui';
import { ContradictionAlert } from '@/components/knowledge/contradiction-alert';
import { UnsupportedAlert } from '@/components/knowledge/unsupported-alert';
import { useKnowledgeContradictions, useKnowledgeUnsupported, useKnowledgeStats } from '@/hooks';

export default function KnowledgeAlertsPage() {
  const [project, setProject] = useState('');
  const { data: stats } = useKnowledgeStats();
  const { data: contradictions, isLoading: contradictionsLoading } =
    useKnowledgeContradictions(project || undefined);
  const { data: unsupported, isLoading: unsupportedLoading } =
    useKnowledgeUnsupported(project || undefined);

  const projects = stats?.projects ?? [];

  return (
    <>
      {/* Project filter */}
      <div className="mb-3">
        <select
          value={project}
          onChange={(e) => setProject(e.target.value)}
          className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-bright focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="">all projects</option>
          {projects.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        {/* Contradictions */}
        <TuiBox title="CONTRADICTIONS" variant={contradictions?.length ? 'error' : 'default'}>
          {contradictionsLoading ? (
            <div className="space-y-1">
              <TuiSkeleton width={40} />
              <TuiSkeleton width={32} />
            </div>
          ) : contradictions && contradictions.length > 0 ? (
            <ContradictionAlert contradictions={contradictions} />
          ) : (
            <span className="text-text-muted">no contradictions found</span>
          )}
        </TuiBox>

        {/* Unsupported */}
        <TuiBox title="UNSUPPORTED" variant={unsupported?.length ? 'warning' : 'default'}>
          {unsupportedLoading ? (
            <div className="space-y-1">
              <TuiSkeleton width={40} />
              <TuiSkeleton width={32} />
            </div>
          ) : unsupported && unsupported.length > 0 ? (
            <UnsupportedAlert unsupported={unsupported} />
          ) : (
            <span className="text-text-muted">all claims have supporting evidence</span>
          )}
        </TuiBox>
      </div>
    </>
  );
}
