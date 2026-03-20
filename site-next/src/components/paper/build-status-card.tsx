'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { StatusDot } from '@/components/ui/status-dot';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { usePaperStatus, usePaperBuild } from '@/hooks';
import type { StatusKey } from '@/lib/constants';
import type { BuildStatus } from '@/lib/paper-types';

const statusDotMap: Record<BuildStatus, { status: StatusKey; pulse: boolean }> = {
  idle: { status: 'idle', pulse: false },
  running: { status: 'warn', pulse: true },
  success: { status: 'ok', pulse: false },
  failed: { status: 'error', pulse: false },
};

const statusLabel: Record<BuildStatus, { text: string; className: string }> = {
  idle: { text: 'Idle', className: 'text-text-muted' },
  running: { text: 'Building...', className: 'text-[--color-status-warn]' },
  success: { text: 'Success', className: 'text-[--color-status-ok]' },
  failed: { text: 'Failed', className: 'text-[--color-status-error]' },
};

function formatDuration(ms: number): string {
  if (ms < 60_000) {
    return `${(ms / 1000).toFixed(1)}s`;
  }
  const minutes = Math.floor(ms / 60_000);
  const seconds = Math.round((ms % 60_000) / 1000);
  return `${minutes}m ${seconds}s`;
}

export function BuildStatusCard() {
  const { data: status, isLoading } = usePaperStatus();
  const paperBuild = usePaperBuild();
  const [skipAnalysis, setSkipAnalysis] = useState(false);
  const [skipCompile, setSkipCompile] = useState(false);

  if (isLoading) {
    return (
      <Card className="space-y-4">
        <div className="flex items-center gap-3">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-2 w-2 rounded-full" />
        </div>
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-full" />
      </Card>
    );
  }

  const buildStatus = status?.status ?? 'idle';
  const dot = statusDotMap[buildStatus];
  const label = statusLabel[buildStatus];
  const isRunning = buildStatus === 'running' || paperBuild.isPending;

  return (
    <Card className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Label>Paper Build</Label>
        <StatusDot status={dot.status} pulse={dot.pulse} />
      </div>

      {/* Status text */}
      <p className={`font-mono text-sm font-medium ${label.className}`}>
        {label.text}
      </p>

      {/* Duration */}
      {status?.duration_ms != null && status.status !== 'running' && (
        <p className="font-mono text-xs text-text-muted">
          Duration: {formatDuration(status.duration_ms)}
        </p>
      )}

      {/* Error */}
      {status?.status === 'failed' && status.error && (
        <p className="truncate font-mono text-xs text-[--color-status-error]">
          {status.error}
        </p>
      )}

      {/* Checkboxes */}
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-1.5 font-mono text-xs text-text-secondary">
          <input
            type="checkbox"
            checked={skipAnalysis}
            onChange={(e) => setSkipAnalysis(e.target.checked)}
            className="accent-primary"
          />
          Skip Analysis
        </label>
        <label className="flex items-center gap-1.5 font-mono text-xs text-text-secondary">
          <input
            type="checkbox"
            checked={skipCompile}
            onChange={(e) => setSkipCompile(e.target.checked)}
            className="accent-primary"
          />
          Skip Compile
        </label>
      </div>

      {/* Build button */}
      <Button
        variant="primary"
        size="sm"
        disabled={isRunning}
        onClick={() => paperBuild.mutate({ skipAnalysis, skipCompile })}
      >
        {isRunning ? 'Building...' : 'Build Paper'}
      </Button>
    </Card>
  );
}
