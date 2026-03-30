import type { KnowledgeStats } from '@/lib/knowledge-types';

interface KnowledgeStatsBarProps {
  stats: KnowledgeStats;
}

export function KnowledgeStatsBar({ stats }: KnowledgeStatsBarProps) {
  const types = Object.keys(stats.by_type).length;
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-1">
      <span><span className="text-text-bright">{stats.total_claims}</span> <span className="text-text-muted">claims</span></span>
      <span><span className="text-text-bright">{stats.total_relations}</span> <span className="text-text-muted">relations</span></span>
      <span><span className="text-text-bright">{stats.projects.length}</span> <span className="text-text-muted">projects</span></span>
      <span><span className="text-text-bright">{types}</span> <span className="text-text-muted">types</span></span>
    </div>
  );
}
