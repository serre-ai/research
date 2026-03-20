'use client';

import { Skeleton } from '@/components/ui/skeleton';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { KnowledgeStatsBar } from '@/components/knowledge/knowledge-stats-bar';
import { useKnowledgeStats } from '@/hooks';
import { useKnowledgeSnapshot } from '@/hooks/use-knowledge-mutations';

export default function KnowledgeStatsPage() {
  const { data: stats, isLoading } = useKnowledgeStats();
  const snapshot = useKnowledgeSnapshot();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!stats) return null;

  const maxTypeCount = Math.max(1, ...Object.values(stats.by_type));
  const maxRelCount = Math.max(1, ...Object.values(stats.by_relation));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-mono text-lg font-semibold text-text-bright">Statistics</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => snapshot.mutate('reasoning-gaps')}
          disabled={snapshot.isPending}
        >
          {snapshot.isPending ? 'Snapshotting...' : 'Snapshot'}
        </Button>
      </div>
      <KnowledgeStatsBar stats={stats} />

      {/* Claims by Type */}
      <Card>
        <Label className="mb-4 block">Claims by Type</Label>
        <div className="space-y-2">
          {Object.entries(stats.by_type).map(([type, count]) => (
            <div key={type} className="flex items-center gap-3">
              <span className="w-24 shrink-0 font-mono text-xs text-text-secondary">{type}</span>
              <div className="flex-1 h-5 bg-bg-elevated">
                <div
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${(count / maxTypeCount) * 100}%` }}
                />
              </div>
              <span className="w-10 shrink-0 text-right font-mono text-xs tabular-nums text-text-bright">
                {count}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Relations by Type */}
      <Card>
        <Label className="mb-4 block">Relations by Type</Label>
        <div className="space-y-2">
          {Object.entries(stats.by_relation).map(([type, count]) => (
            <div key={type} className="flex items-center gap-3">
              <span className="w-24 shrink-0 font-mono text-xs text-text-secondary">
                {type.replace('_', ' ')}
              </span>
              <div className="flex-1 h-5 bg-bg-elevated">
                <div
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${(count / maxRelCount) * 100}%` }}
                />
              </div>
              <span className="w-10 shrink-0 text-right font-mono text-xs tabular-nums text-text-bright">
                {count}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
