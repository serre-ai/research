'use client';

import { useState } from 'react';
import { PageHeader } from '@/components/ui/page-header';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { ClipboardList } from 'lucide-react';
import { TicketCard } from '@/components/backlog/ticket-card';
import { TicketDetail } from '@/components/backlog/ticket-detail';
import { CreateTicketDialog } from '@/components/backlog/create-ticket-dialog';
import { useBacklog } from '@/hooks/use-backlog';

const STATUSES: { label: string; value: string }[] = [
  { label: 'All Status', value: '' },
  { label: 'Open', value: 'open' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Done', value: 'done' },
  { label: "Won't Fix", value: 'wont_fix' },
];

const PRIORITIES: { label: string; value: string }[] = [
  { label: 'All Priority', value: '' },
  { label: 'Critical', value: 'critical' },
  { label: 'High', value: 'high' },
  { label: 'Medium', value: 'medium' },
  { label: 'Low', value: 'low' },
];

const CATEGORIES: { label: string; value: string }[] = [
  { label: 'All Categories', value: '' },
  { label: 'Daemon', value: 'daemon' },
  { label: 'API', value: 'api' },
  { label: 'Agents', value: 'agents' },
  { label: 'Eval', value: 'eval' },
  { label: 'Infra', value: 'infra' },
  { label: 'Other', value: 'other' },
];

export default function BacklogPage() {
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  const filters: Record<string, string> = {};
  if (statusFilter) filters.status = statusFilter;
  if (priorityFilter) filters.priority = priorityFilter;
  if (categoryFilter) filters.category = categoryFilter;

  const { data: tickets, isLoading } = useBacklog(
    Object.keys(filters).length > 0 ? filters : undefined,
  );

  const selectedTicket = tickets?.find((t) => t.id === selectedTicketId);

  return (
    <div>
      <PageHeader title="Backlog" subtitle="Platform tickets and tasks" />

      <div className="flex gap-4 h-[calc(100vh-220px)]">
        {/* Ticket list */}
        <div className="w-2/5 flex flex-col border border-border bg-bg-elevated">
          {/* Filter bar */}
          <div className="flex flex-wrap gap-2 p-3 border-b border-border">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="flex-1 min-w-0 bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
            >
              {STATUSES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="flex-1 min-w-0 bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
            >
              {PRIORITIES.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="flex-1 min-w-0 bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
            <CreateTicketDialog />
          </div>

          {/* Ticket list */}
          <div className="flex-1 overflow-y-auto">
            {isLoading ? (
              <div className="space-y-0 divide-y divide-border">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="p-4 space-y-2">
                    <Skeleton className="h-3 w-24" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-32" />
                  </div>
                ))}
              </div>
            ) : tickets && tickets.length > 0 ? (
              tickets.map((ticket) => (
                <TicketCard
                  key={ticket.id}
                  ticket={ticket}
                  isSelected={selectedTicketId === ticket.id}
                  onClick={() => setSelectedTicketId(ticket.id)}
                />
              ))
            ) : (
              <EmptyState
                icon={ClipboardList}
                message="No tickets found"
                description="Try changing the filters or create a new ticket"
                className="py-12"
              />
            )}
          </div>
        </div>

        {/* Ticket detail */}
        <div className="w-3/5 overflow-y-auto">
          <TicketDetail ticket={selectedTicket} />
        </div>
      </div>
    </div>
  );
}
