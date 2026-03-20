'use client';

import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ShieldCheck, Play } from 'lucide-react';
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
    <div className="space-y-6">
      {/* Actions */}
      <div className="flex items-center justify-between">
        <Label>Claim Verification</Label>
        <Button
          variant="outline"
          size="sm"
          disabled={triggerVerification.isPending}
          onClick={() => triggerVerification.mutate()}
        >
          <Play className="h-3 w-3 mr-1" />
          {triggerVerification.isPending ? 'Running...' : 'Run Verification'}
        </Button>
      </div>

      {/* Latest report */}
      {latestLoading ? (
        <Card className="space-y-4">
          <Skeleton className="h-4 w-32" />
          <div className="grid grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
          <Skeleton className="h-3 w-full" />
        </Card>
      ) : latestError ? (
        <EmptyState
          icon={ShieldCheck}
          message="No verification report"
          description="Run a verification to check claim consistency"
        />
      ) : latest ? (
        <VerificationReport report={latest} />
      ) : null}

      {/* History */}
      {!historyLoading && history && history.length > 1 && (
        <Card>
          <Label className="mb-3 block">History</Label>
          <div className="space-y-2">
            {history.slice(1).map((report) => (
              <div
                key={report.id}
                className="flex items-center justify-between border-b border-border pb-2 last:border-0 last:pb-0"
              >
                <div className="flex items-center gap-3">
                  <Badge variant={report.inconsistencies > 0 || report.missingEvidence > 0 ? 'warning' : 'success'}>
                    {report.inconsistencies > 0 || report.missingEvidence > 0 ? 'Issues' : 'Clean'}
                  </Badge>
                  <span className="font-mono text-xs text-text-secondary">
                    {report.totalClaims} claims, {report.verified} verified
                  </span>
                </div>
                <span className="font-mono text-[10px] text-text-muted">
                  {report.created_at ? new Date(report.created_at).toLocaleDateString() : '—'}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
