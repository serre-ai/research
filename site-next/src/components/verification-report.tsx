'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { ProgressBar } from '@/components/ui/progress-bar';
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
    <Card>
      <div className="flex items-center justify-between mb-4">
        <Label>Verification Report</Label>
        <Badge variant={hasIssues ? 'warning' : 'success'}>
          {hasIssues ? 'Issues Found' : 'Clean'}
        </Badge>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-4">
        <div className="text-center">
          <p className="font-mono text-lg font-bold text-text-bright tabular-nums">
            {report.totalClaims}
          </p>
          <p className="font-mono text-[10px] text-text-muted">Total Claims</p>
        </div>
        <div className="text-center">
          <p className="font-mono text-lg font-bold text-text-bright tabular-nums">
            {report.verified}
          </p>
          <p className="font-mono text-[10px] text-text-muted">Verified</p>
        </div>
        <div className="text-center">
          <p className="font-mono text-lg font-bold tabular-nums" style={{ color: report.inconsistencies > 0 ? '#ef4444' : 'var(--color-text-bright)' }}>
            {report.inconsistencies}
          </p>
          <p className="font-mono text-[10px] text-text-muted">Inconsistencies</p>
        </div>
        <div className="text-center">
          <p className="font-mono text-lg font-bold tabular-nums" style={{ color: report.missingEvidence > 0 ? '#EAB308' : 'var(--color-text-bright)' }}>
            {report.missingEvidence}
          </p>
          <p className="font-mono text-[10px] text-text-muted">Missing Evidence</p>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="font-mono text-xs text-text-muted">Verified</span>
          <span className="font-mono text-xs text-text-secondary">{verifiedPct}%</span>
        </div>
        <ProgressBar value={verifiedPct} />
      </div>

      {report.created_at && (
        <p className="font-mono text-[10px] text-text-muted mt-3">
          Run at {new Date(report.created_at).toLocaleString()}
        </p>
      )}
    </Card>
  );
}
