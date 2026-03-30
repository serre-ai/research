'use client';

import { useState } from 'react';
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
    <form onSubmit={handleSubmit} className="space-y-2 mt-2 border-t border-border pt-2">
      <div className="flex items-center gap-2">
        <span className="text-text-muted">adjust</span>
        <input
          type="range"
          min={0}
          max={100}
          value={confidence}
          onChange={(e) => setConfidence(Number(e.target.value))}
          className="flex-1"
        />
        <span className="tabular-nums text-text-bright">{confidence}%</span>
      </div>
      <textarea
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        placeholder="reason for adjustment..."
        rows={2}
        className="w-full bg-bg border border-border px-2 py-1 font-mono text-xs text-text placeholder:text-text-muted resize-y focus:outline-none focus:ring-1 focus:ring-primary"
      />
      <button
        type="submit"
        disabled={updateConfidence.isPending || !reason.trim()}
        className="border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text-secondary hover:text-text-bright disabled:opacity-50"
      >
        {updateConfidence.isPending ? 'updating...' : '[update]'}
      </button>
    </form>
  );
}
