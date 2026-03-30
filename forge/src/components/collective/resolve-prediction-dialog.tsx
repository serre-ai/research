'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { AgentSelector } from './agent-selector';
import { useResolvePrediction } from '@/hooks/use-prediction-mutations';

interface ResolvePredictionDialogProps {
  predictionId: string;
  claim: string;
}

export function ResolvePredictionDialog({ predictionId, claim }: ResolvePredictionDialogProps) {
  const [open, setOpen] = useState(false);
  const [outcome, setOutcome] = useState<boolean | null>(null);
  const [resolvedBy, setResolvedBy] = useState('sol');
  const [resolutionNote, setResolutionNote] = useState('');

  const resolvePrediction = useResolvePrediction();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (outcome === null) return;

    resolvePrediction.mutate(
      {
        id: predictionId,
        outcome,
        resolved_by: resolvedBy,
        ...(resolutionNote.trim() ? { resolution_note: resolutionNote.trim() } : {}),
      },
      {
        onSuccess: () => {
          setOpen(false);
          setOutcome(null);
          setResolutionNote('');
        },
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Resolve
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Resolve Prediction</DialogTitle>
        <DialogDescription className="line-clamp-2">{claim}</DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <Label className="mb-1.5 block">Outcome</Label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setOutcome(true)}
                className={`flex-1 border px-3 py-2 font-mono text-sm transition-colors ${
                  outcome === true
                    ? 'border-green-500 bg-green-500/10 text-green-400'
                    : 'border-border bg-bg text-text-secondary hover:bg-bg-hover'
                }`}
              >
                True
              </button>
              <button
                type="button"
                onClick={() => setOutcome(false)}
                className={`flex-1 border px-3 py-2 font-mono text-sm transition-colors ${
                  outcome === false
                    ? 'border-red-500 bg-red-500/10 text-red-400'
                    : 'border-border bg-bg text-text-secondary hover:bg-bg-hover'
                }`}
              >
                False
              </button>
            </div>
          </div>
          <div>
            <Label className="mb-1.5 block">Resolved by</Label>
            <AgentSelector value={resolvedBy} onChange={setResolvedBy} />
          </div>
          <div>
            <Label className="mb-1.5 block">Resolution note</Label>
            <textarea
              value={resolutionNote}
              onChange={(e) => setResolutionNote(e.target.value)}
              placeholder="Optional explanation..."
              rows={3}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={resolvePrediction.isPending || outcome === null}>
              {resolvePrediction.isPending ? 'Resolving...' : 'Resolve'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
