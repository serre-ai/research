'use client';

import { useState } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { ContradictionAlert } from '@/components/knowledge/contradiction-alert';
import { UnsupportedAlert } from '@/components/knowledge/unsupported-alert';
import { useKnowledgeContradictions, useKnowledgeUnsupported, useKnowledgeStats } from '@/hooks';
import { ShieldAlert } from 'lucide-react';

export default function KnowledgeAlertsPage() {
  const [project, setProject] = useState('');
  const { data: stats } = useKnowledgeStats();
  const { data: contradictions, isLoading: contradictionsLoading } =
    useKnowledgeContradictions(project || undefined);
  const { data: unsupported, isLoading: unsupportedLoading } =
    useKnowledgeUnsupported(project || undefined);

  const projects = stats?.projects ?? [];

  return (
    <div className="space-y-6">
      {/* Project filter */}
      <div>
        <select
          value={project}
          onChange={(e) => setProject(e.target.value)}
          className="border border-border bg-bg-elevated px-2 py-1.5 font-mono text-xs text-text-secondary focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="">All projects</option>
          {projects.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </div>

      {/* Alerts grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          {contradictionsLoading ? (
            <Skeleton className="h-40 w-full" />
          ) : contradictions && contradictions.length > 0 ? (
            <ContradictionAlert contradictions={contradictions} />
          ) : (
            <EmptyState
              icon={ShieldAlert}
              message="No contradictions"
              description="No contradicting claims found."
            />
          )}
        </div>
        <div>
          {unsupportedLoading ? (
            <Skeleton className="h-40 w-full" />
          ) : unsupported && unsupported.length > 0 ? (
            <UnsupportedAlert unsupported={unsupported} />
          ) : (
            <EmptyState
              icon={ShieldAlert}
              message="No unsupported claims"
              description="All claims have supporting evidence."
            />
          )}
        </div>
      </div>
    </div>
  );
}
