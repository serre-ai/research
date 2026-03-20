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
import { useCreateProposal } from '@/hooks/use-governance';
import { Plus } from 'lucide-react';
import type { ProposalType } from '@/lib/governance-types';

const PROPOSAL_TYPES: { label: string; value: ProposalType }[] = [
  { label: 'Process', value: 'process' },
  { label: 'Schedule', value: 'schedule' },
  { label: 'Budget', value: 'budget' },
  { label: 'Personnel', value: 'personnel' },
  { label: 'Values', value: 'values' },
];

export function CreateProposalDialog() {
  const [open, setOpen] = useState(false);
  const [proposer, setProposer] = useState('rho');
  const [proposalType, setProposalType] = useState<ProposalType>('process');
  const [title, setTitle] = useState('');
  const [proposal, setProposal] = useState('');

  const createProposal = useCreateProposal();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !proposal.trim()) return;

    createProposal.mutate(
      {
        proposer,
        title: title.trim(),
        proposal: proposal.trim(),
        proposal_type: proposalType,
      },
      {
        onSuccess: () => {
          setOpen(false);
          setTitle('');
          setProposal('');
        },
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="h-3 w-3 mr-1" />
          New Proposal
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>New Governance Proposal</DialogTitle>
        <DialogDescription>Submit a proposal for the collective to vote on.</DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <Label className="mb-1.5 block">Proposer</Label>
              <AgentSelector value={proposer} onChange={setProposer} />
            </div>
            <div className="flex-1">
              <Label className="mb-1.5 block">Type</Label>
              <select
                value={proposalType}
                onChange={(e) => setProposalType(e.target.value as ProposalType)}
                className="w-full bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
              >
                {PROPOSAL_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <Label className="mb-1.5 block">Title</Label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Proposal title..."
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
            />
          </div>
          <div>
            <Label className="mb-1.5 block">Proposal</Label>
            <textarea
              value={proposal}
              onChange={(e) => setProposal(e.target.value)}
              placeholder="Describe the proposal..."
              rows={5}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={createProposal.isPending || !title.trim() || !proposal.trim()}>
              {createProposal.isPending ? 'Submitting...' : 'Submit Proposal'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
