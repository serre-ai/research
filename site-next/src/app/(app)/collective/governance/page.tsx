'use client';

import { useState } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Gavel } from 'lucide-react';
import { ProposalCard } from '@/components/collective/proposal-card';
import { ProposalDetail } from '@/components/collective/proposal-detail';
import { CreateProposalDialog } from '@/components/collective/create-proposal-dialog';
import { useGovernanceProposals } from '@/hooks/use-governance';

const STATUSES: { label: string; value: string }[] = [
  { label: 'All Status', value: '' },
  { label: 'Proposed', value: 'proposed' },
  { label: 'Voting', value: 'voting' },
  { label: 'Accepted', value: 'accepted' },
  { label: 'Rejected', value: 'rejected' },
];

const TYPES: { label: string; value: string }[] = [
  { label: 'All Types', value: '' },
  { label: 'Process', value: 'process' },
  { label: 'Schedule', value: 'schedule' },
  { label: 'Budget', value: 'budget' },
  { label: 'Personnel', value: 'personnel' },
  { label: 'Values', value: 'values' },
];

export default function GovernancePage() {
  const [selectedProposalId, setSelectedProposalId] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const filters: Record<string, string> = {};
  if (statusFilter) filters.status = statusFilter;
  if (typeFilter) filters.type = typeFilter;

  const { data: proposals, isLoading } = useGovernanceProposals(
    Object.keys(filters).length > 0 ? filters : undefined,
  );

  return (
    <div className="flex gap-4 h-[calc(100vh-220px)]">
      {/* Proposal list */}
      <div className="w-2/5 flex flex-col border border-border bg-bg-elevated">
        {/* Filter bar */}
        <div className="flex gap-2 p-3 border-b border-border">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flex-1 bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
          >
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="flex-1 bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
          >
            {TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          <CreateProposalDialog />
        </div>

        {/* Proposal list */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="space-y-0 divide-y divide-border">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="p-4 space-y-2">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-24" />
                </div>
              ))}
            </div>
          ) : proposals && proposals.length > 0 ? (
            proposals.map((proposal) => (
              <ProposalCard
                key={proposal.id}
                proposal={proposal}
                isSelected={selectedProposalId === proposal.id}
                onClick={() => setSelectedProposalId(proposal.id)}
              />
            ))
          ) : (
            <EmptyState
              icon={Gavel}
              message="No proposals found"
              description="Try changing the filters"
              className="py-12"
            />
          )}
        </div>
      </div>

      {/* Proposal detail */}
      <div className="w-3/5 overflow-y-auto">
        <ProposalDetail proposalId={selectedProposalId} />
      </div>
    </div>
  );
}
