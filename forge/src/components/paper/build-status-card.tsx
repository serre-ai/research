'use client';

import { useState } from 'react';
import { TuiStatusDot, TuiSkeleton } from '@/components/tui';
import { usePaperStatus, usePaperBuild } from '@/hooks';
import type { BuildStatus } from '@/lib/paper-types';

const dotMap: Record<BuildStatus, 'ok' | 'warn' | 'error' | 'idle'> = {
  idle: 'idle',
  running: 'warn',
  success: 'ok',
  failed: 'error',
};

export function BuildStatusCard() {
  const { data: status, isLoading } = usePaperStatus();
  const paperBuild = usePaperBuild();
  const [skipAnalysis, setSkipAnalysis] = useState(false);
  const [skipCompile, setSkipCompile] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-1">
        <TuiSkeleton width={20} />
        <TuiSkeleton width={30} />
      </div>
    );
  }

  const buildStatus = status?.status ?? 'idle';
  const isRunning = buildStatus === 'running' || paperBuild.isPending;

  return (
    <div className="space-y-2">
      {/* Status */}
      <div className="flex items-center gap-2">
        <TuiStatusDot status={dotMap[buildStatus]} />
        <span className="text-text-secondary">{buildStatus}</span>
        {status?.duration_ms != null && buildStatus !== 'running' && (
          <span className="text-text-muted">{(status.duration_ms / 1000).toFixed(1)}s</span>
        )}
      </div>

      {/* Error */}
      {buildStatus === 'failed' && status?.error && (
        <span className="text-[--color-danger]">{status.error}</span>
      )}

      {/* Options */}
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-1 text-text-secondary cursor-pointer">
          <input
            type="checkbox"
            checked={skipAnalysis}
            onChange={(e) => setSkipAnalysis(e.target.checked)}
            className="accent-primary"
          />
          skip analysis
        </label>
        <label className="flex items-center gap-1 text-text-secondary cursor-pointer">
          <input
            type="checkbox"
            checked={skipCompile}
            onChange={(e) => setSkipCompile(e.target.checked)}
            className="accent-primary"
          />
          skip compile
        </label>
      </div>

      {/* Build button */}
      <button
        disabled={isRunning}
        onClick={() => paperBuild.mutate({ skipAnalysis, skipCompile })}
        className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-secondary hover:text-text-bright disabled:opacity-50"
      >
        {isRunning ? 'building...' : '[build paper]'}
      </button>
    </div>
  );
}
