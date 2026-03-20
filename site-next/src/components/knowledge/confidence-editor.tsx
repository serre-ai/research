'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { useUpdateConfidence } from '@/hooks/use-knowledge-mutations';

interface ConfidenceEditorProps {
  claimId: string;
  currentConfidence: number;
}

export function ConfidenceEditor({ claimId, currentConfidence }: ConfidenceEditorProps) {
  const [confidence, setConfidence] = useState(Math.round(currentConfidence * 100));
  const [reason, setReason] = useState('');
  const updateConfidence = useUpdateConfidence();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!reason.trim()) return;
    updateConfidence.mutate(
      { id: claimId, confidence: confidence / 100, reason: reason.trim() },
      { onSuccess: () => setReason('') },
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <div className="flex items-center justify-between mb-1">
          <Label>Adjust Confidence</Label>
          <span className="font-mono text-xs text-text-bright tabular-nums">{confidence}%</span>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          value={confidence}
          onChange={(e) => setConfidence(Number(e.target.value))}
          className="w-full"
        />
      </div>
      <div>
        <Label className="mb-1 block">Reason</Label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Why this confidence level?"
          rows={2}
          className="w-full bg-bg border border-border px-3 py-2 font-mono text-xs text-text placeholder:text-text-muted resize-y"
        />
      </div>
      <Button type="submit" size="sm" disabled={updateConfidence.isPending || !reason.trim()}>
        {updateConfidence.isPending ? 'Updating...' : 'Update'}
      </Button>
    </form>
  );
}
