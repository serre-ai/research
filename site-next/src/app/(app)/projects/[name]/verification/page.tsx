'use client';

import { useParams } from 'next/navigation';
import { TuiBox, TuiBadge, TuiSkeleton } from '@/components/tui';
import { VerificationReport } from '@/components/verification-report';
import {
  useVerificationReport,
  useVerificationHistory,
  useTriggerVerification,
} from '@/hooks/use-verification';

export default function VerificationPage() {
  const { name } = useParams<{ name: string }>();
  const { data: latest, isLoading: latestLoading, error: latestError } = useVerificationReport(name);
  const { data: history, isLoading: historyLoading } = useVerificationHistory(name);
  const triggerVerification = useTriggerVerification(name);

  return (
    <>
      {/* Actions */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-text-muted">CLAIM VERIFICATION</span>
        <button
          disabled={triggerVerification.isPending}
          onClick={() => triggerVerification.mutate()}
          className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-secondary hover:text-text-bright disabled:opacity-50"
        >
          {triggerVerification.isPending ? 'running...' : '[run]'}
        </button>
      </div>

      {/* Latest report */}
      <TuiBox title="LATEST REPORT" className="mb-3">
        {latestLoading ? (
          <div className="space-y-1">
            <TuiSkeleton width={30} />
            <TuiSkeleton width={50} />
          </div>
        ) : latestError || !latest ? (
          <span className="text-text-muted">no verification report yet -- run one above</span>
        ) : (
          <VerificationReport report={latest} />
        )}
      </TuiBox>

      {/* History */}
      {!historyLoading && history && history.length > 1 && (
        <TuiBox title="HISTORY">
          {history.slice(1).map((report) => (
            <div
              key={report.id}
              className="flex items-center justify-between border-b border-border py-1.5 last:border-0 last:pb-0 first:pt-0"
            >
              <div className="flex items-center gap-2">
                <TuiBadge color={report.inconsistencies > 0 || report.missingEvidence > 0 ? 'warn' : 'ok'}>
                  {report.inconsistencies > 0 || report.missingEvidence > 0 ? 'ISSUES' : 'CLEAN'}
                </TuiBadge>
                <span className="text-text-secondary">
                  {report.totalClaims} claims, {report.verified} verified
                </span>
              </div>
              <span className="text-text-muted">
                {report.created_at ? new Date(report.created_at).toISOString().slice(0, 10) : '--'}
              </span>
            </div>
          ))}
        </TuiBox>
      )}
    </>
  );
}
