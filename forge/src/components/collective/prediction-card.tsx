'use client';

import { Card } from '@/components/ui/card';
import { ProbabilityBar } from './probability-bar';
import { OutcomeBadge } from './outcome-badge';
import { CategoryBadge } from './category-badge';
import type { Prediction } from '@/lib/collective-types';

interface PredictionCardProps {
  prediction: Prediction;
}

export function PredictionCard({ prediction }: PredictionCardProps) {
  return (
    <Card className="space-y-3">
      <div className="flex items-center gap-2">
        <CategoryBadge category={prediction.category} />
        <OutcomeBadge outcome={prediction.outcome} />
      </div>
      <p className="font-mono text-sm text-text-bright">{prediction.claim}</p>
      <ProbabilityBar value={prediction.probability} />
      {prediction.resolved_at && (
        <p className="font-mono text-[10px] text-text-muted">
          Resolved {new Date(prediction.resolved_at).toLocaleDateString()} by {prediction.resolved_by}
        </p>
      )}
    </Card>
  );
}
