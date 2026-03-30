'use client';

import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Trophy } from 'lucide-react';
import { AgentAvatar } from './agent-avatar';
import { AgentNameBadge } from './agent-name-badge';
import type { CalibrationLeaderboardEntry } from '@/lib/collective-types';

interface CalibrationLeaderboardProps {
  entries: CalibrationLeaderboardEntry[] | undefined;
  isLoading: boolean;
}

export function CalibrationLeaderboard({ entries, isLoading }: CalibrationLeaderboardProps) {
  if (isLoading) {
    return (
      <Card className="space-y-3">
        <Label>Calibration Leaderboard</Label>
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-full" />
        ))}
      </Card>
    );
  }

  if (!entries || entries.length === 0) {
    return (
      <Card>
        <Label>Calibration Leaderboard</Label>
        <EmptyState icon={Trophy} message="No calibration data yet" className="py-8" />
      </Card>
    );
  }

  return (
    <Card>
      <Label>Calibration Leaderboard</Label>
      <div className="mt-3">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="py-2 text-left font-mono text-[10px] font-medium text-text-muted w-8">#</th>
              <th className="py-2 text-left font-mono text-[10px] font-medium text-text-muted">Agent</th>
              <th className="py-2 text-right font-mono text-[10px] font-medium text-text-muted">Brier</th>
              <th className="py-2 text-right font-mono text-[10px] font-medium text-text-muted">Resolved</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry, i) => (
              <tr key={entry.agent} className="border-b border-border">
                <td className="py-2 font-mono text-xs text-text-muted">{i + 1}</td>
                <td className="py-2">
                  <div className="flex items-center gap-2">
                    <AgentAvatar agentId={entry.agent} size="sm" />
                    <AgentNameBadge agentId={entry.agent} />
                  </div>
                </td>
                <td className="py-2 text-right font-mono text-xs text-text-bright tabular-nums">
                  {entry.brier_score.toFixed(3)}
                </td>
                <td className="py-2 text-right font-mono text-xs text-text-secondary tabular-nums">
                  {entry.total_resolved}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
