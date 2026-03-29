'use client';

import { useState } from 'react';
import { TuiBox, TuiSkeleton, TuiStatusDot, TuiBadge } from '@/components/tui';
import { BuildLogViewer } from '@/components/paper/build-log-viewer';
import { PdfViewer } from '@/components/paper/pdf-viewer';
import { usePaperStatus } from '@/hooks';

export default function PaperPage() {
  const { data: status, isLoading } = usePaperStatus();
  const [tab, setTab] = useState<'pdf' | 'log'>('pdf');

  return (
    <>
      {/* Build status */}
      <TuiBox title="PAPER BUILD" className="mb-3">
        {isLoading ? (
          <TuiSkeleton width={30} />
        ) : (
          <div className="flex flex-wrap gap-x-6 gap-y-1">
            <span className="flex items-center gap-1">
              <TuiStatusDot status={status?.status === 'success' ? 'ok' : status?.status === 'running' ? 'warn' : 'idle'} />
              <span className="text-text-secondary">{status?.status ?? 'idle'}</span>
            </span>
            {status?.finished_at && (
              <span className="text-text-muted">last: {new Date(status.finished_at).toISOString().slice(0, 16).replace('T', ' ')}</span>
            )}
            {status?.duration_ms != null && (
              <span className="text-text-muted">{(status.duration_ms / 1000).toFixed(1)}s</span>
            )}
          </div>
        )}
      </TuiBox>

      {/* Tab selector */}
      <div className="flex gap-2 mb-3">
        <button
          onClick={() => setTab('pdf')}
          className={`border px-2 py-1 font-mono text-xs ${tab === 'pdf' ? 'border-text-bright text-text-bright bg-bg-elevated' : 'border-border text-text-muted hover:text-text-secondary'}`}
        >
          [pdf]
        </button>
        <button
          onClick={() => setTab('log')}
          className={`border px-2 py-1 font-mono text-xs ${tab === 'log' ? 'border-text-bright text-text-bright bg-bg-elevated' : 'border-border text-text-muted hover:text-text-secondary'}`}
        >
          [log]
        </button>
      </div>

      {/* Content */}
      <TuiBox title={tab === 'pdf' ? 'PDF PREVIEW' : 'BUILD LOG'}>
        {tab === 'pdf' ? (
          <PdfViewer available={status?.status === 'success'} />
        ) : (
          <BuildLogViewer />
        )}
      </TuiBox>
    </>
  );
}
