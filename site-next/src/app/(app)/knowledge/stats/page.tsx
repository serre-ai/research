'use client';

import { TuiBox, TuiSkeleton, TuiProgress } from '@/components/tui';
import { KnowledgeStatsBar } from '@/components/knowledge/knowledge-stats-bar';
import { useKnowledgeStats } from '@/hooks';
import { useKnowledgeSnapshot } from '@/hooks/use-knowledge-mutations';

export default function KnowledgeStatsPage() {
  const { data: stats, isLoading } = useKnowledgeStats();
  const snapshot = useKnowledgeSnapshot();

  if (isLoading) {
    return (
      <div className="space-y-3">
        <TuiSkeleton width={40} />
        <TuiSkeleton width={50} />
        <TuiSkeleton width={50} />
      </div>
    );
  }

  if (!stats) return null;

  const maxTypeCount = Math.max(1, ...Object.values(stats.by_type));
  const maxRelCount = Math.max(1, ...Object.values(stats.by_relation));

  return (
    <>
      <div className="flex items-center justify-between mb-3">
        <KnowledgeStatsBar stats={stats} />
        <button
          onClick={() => snapshot.mutate('reasoning-gaps')}
          disabled={snapshot.isPending}
          className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-secondary hover:text-text-bright focus:outline-none"
        >
          {snapshot.isPending ? 'snapshotting...' : '[snapshot]'}
        </button>
      </div>

      {/* Claims by Type */}
      <TuiBox title="CLAIMS BY TYPE" className="mb-3">
        <div className="space-y-1">
          {Object.entries(stats.by_type).map(([type, count]) => (
            <div key={type} className="flex items-center gap-2">
              <span className="w-20 shrink-0 text-text-secondary">{type}</span>
              <TuiProgress value={Math.round((count / maxTypeCount) * 100)} width={20} showPercent={false} color="accent" />
              <span className="w-6 shrink-0 text-right tabular-nums text-text-bright">{count}</span>
            </div>
          ))}
        </div>
      </TuiBox>

      {/* Relations by Type */}
      <TuiBox title="RELATIONS BY TYPE">
        <div className="space-y-1">
          {Object.entries(stats.by_relation).map(([type, count]) => (
            <div key={type} className="flex items-center gap-2">
              <span className="w-20 shrink-0 text-text-secondary">{type.replace('_', ' ')}</span>
              <TuiProgress value={Math.round((count / maxRelCount) * 100)} width={20} showPercent={false} color="accent" />
              <span className="w-6 shrink-0 text-right tabular-nums text-text-bright">{count}</span>
            </div>
          ))}
        </div>
      </TuiBox>
    </>
  );
}
