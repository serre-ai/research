import { Database, GitBranch, FolderOpen, Tag } from 'lucide-react';
import { MetricCard } from '@/components/ui/metric-card';
import type { KnowledgeStats } from '@/lib/knowledge-types';

interface KnowledgeStatsBarProps {
  stats: KnowledgeStats;
}

export function KnowledgeStatsBar({ stats }: KnowledgeStatsBarProps) {
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <MetricCard label="Total Claims" value={stats.total_claims} icon={Database} />
      <MetricCard label="Relations" value={stats.total_relations} icon={GitBranch} />
      <MetricCard label="Projects" value={stats.projects.length} icon={FolderOpen} />
      <MetricCard label="Types" value={Object.keys(stats.by_type).length} icon={Tag} />
    </div>
  );
}
