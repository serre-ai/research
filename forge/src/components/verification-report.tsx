'use client';

import { TuiBadge, TuiProgress } from '@/components/tui';
import type { VerificationReport as VerificationReportType } from '@/lib/verification-types';

interface VerificationReportProps {
  report: VerificationReportType;
}

export function VerificationReport({ report }: VerificationReportProps) {
  const verifiedPct = report.totalClaims > 0
    ? Math.round((report.verified / report.totalClaims) * 100)
    : 0;
  const hasIssues = report.inconsistencies > 0 || report.missingEvidence > 0;

  return (
    <div className="space-y-2">
      {/* Status */}
      <div className="flex items-center gap-2">
        <TuiBadge color={hasIssues ? 'warn' : 'ok'}>
          {hasIssues ? 'ISSUES FOUND' : 'CLEAN'}
        </TuiBadge>
      </div>

      {/* Metrics */}
      <div className="flex flex-wrap gap-x-6 gap-y-1">
        <span><span className="text-text-bright tabular-nums">{report.totalClaims}</span> <span className="text-text-muted">total</span></span>
        <span><span className="text-text-bright tabular-nums">{report.verified}</span> <span className="text-text-muted">verified</span></span>
        <span>
          <span className={`tabular-nums ${report.inconsistencies > 0 ? 'text-[--color-danger]' : 'text-text-bright'}`}>
            {report.inconsistencies}
          </span>
          {' '}<span className="text-text-muted">inconsistencies</span>
        </span>
        <span>
          <span className={`tabular-nums ${report.missingEvidence > 0 ? 'text-[--color-secondary]' : 'text-text-bright'}`}>
            {report.missingEvidence}
          </span>
          {' '}<span className="text-text-muted">missing evidence</span>
        </span>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2">
        <span className="text-text-muted">verified</span>
        <TuiProgress value={verifiedPct} width={20} color={hasIssues ? 'warn' : 'ok'} />
      </div>

      {report.created_at && (
        <span className="text-text-muted">
          run at {new Date(report.created_at).toISOString().slice(0, 16).replace('T', ' ')}
        </span>
      )}
    </div>
  );
}
