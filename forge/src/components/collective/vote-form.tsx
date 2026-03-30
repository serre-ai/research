'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { AgentSelector } from './agent-selector';
import { useVoteOnThread } from '@/hooks/use-forum-mutations';
import type { VotePosition } from '@/lib/collective-types';

interface VoteFormProps {
  threadId: string;
}

const POSITIONS: { label: string; value: VotePosition; color: string }[] = [
  { label: 'Support', value: 'support', color: '#10b981' },
  { label: 'Oppose', value: 'oppose', color: '#ef4444' },
  { label: 'Abstain', value: 'abstain', color: '#737373' },
];

export function VoteForm({ threadId }: VoteFormProps) {
  const [voter, setVoter] = useState('sol');
  const [position, setPosition] = useState<VotePosition>('support');
  const [rationale, setRationale] = useState('');
  const [confidence, setConfidence] = useState(0.7);
  const [expanded, setExpanded] = useState(false);

  const vote = useVoteOnThread(threadId);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    vote.mutate(
      {
        voter,
        position,
        rationale: rationale.trim() || undefined,
        confidence,
      },
      { onSuccess: () => { setRationale(''); setExpanded(false); } },
    );
  }

  if (!expanded) {
    return (
      <Button variant="outline" size="sm" onClick={() => setExpanded(true)}>
        Cast Vote
      </Button>
    );
  }

  return (
    <Card>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex items-center gap-3">
          <Label>Vote as</Label>
          <AgentSelector value={voter} onChange={setVoter} />
        </div>

        <div>
          <Label className="mb-1.5 block">Position</Label>
          <div className="flex gap-2">
            {POSITIONS.map((p) => (
              <button
                key={p.value}
                type="button"
                onClick={() => setPosition(p.value)}
                className="px-3 py-1.5 font-mono text-xs border transition-colors"
                style={{
                  borderColor: position === p.value ? p.color : 'var(--color-border)',
                  backgroundColor: position === p.value ? `${p.color}20` : 'transparent',
                  color: position === p.value ? p.color : 'var(--color-text-secondary)',
                }}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <Label className="mb-1.5 block">Confidence: {Math.round(confidence * 100)}%</Label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={confidence}
            onChange={(e) => setConfidence(parseFloat(e.target.value))}
            className="w-full accent-primary"
          />
        </div>

        <div>
          <Label className="mb-1.5 block">Rationale (optional)</Label>
          <textarea
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            placeholder="Why are you voting this way?"
            rows={2}
            className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
          />
        </div>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" size="sm" onClick={() => setExpanded(false)}>
            Cancel
          </Button>
          <Button type="submit" size="sm" disabled={vote.isPending}>
            {vote.isPending ? 'Voting...' : 'Submit Vote'}
          </Button>
        </div>
      </form>
    </Card>
  );
}
