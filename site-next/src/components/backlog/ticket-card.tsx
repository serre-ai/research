'use client';

import { clsx } from 'clsx';
import { Badge } from '@/components/ui/badge';
import type { BacklogTicket } from '@/lib/backlog-types';

interface TicketCardProps {
  ticket: BacklogTicket;
  isSelected?: boolean;
  onClick?: () => void;
}

const priorityVariant: Record<string, 'default' | 'success' | 'warning' | 'error'> = {
  low: 'default',
  medium: 'default',
  high: 'warning',
  critical: 'error',
};

const statusLabel: Record<string, string> = {
  open: 'Open',
  in_progress: 'In Progress',
  done: 'Done',
  wont_fix: "Won't Fix",
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'now';
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}

export function TicketCard({ ticket, isSelected, onClick }: TicketCardProps) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'w-full text-left border-b border-border p-4 transition-colors',
        isSelected ? 'bg-bg-elevated' : 'hover:bg-bg-hover',
      )}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <Badge variant={priorityVariant[ticket.priority] ?? 'default'}>
          {ticket.priority}
        </Badge>
        <Badge variant="outline">{ticket.category}</Badge>
        <span className="ml-auto font-mono text-[10px] text-text-muted">{timeAgo(ticket.created_at)}</span>
      </div>
      <p className="font-mono text-sm text-text-bright truncate">{ticket.title}</p>
      <div className="flex items-center gap-3 mt-2">
        <span className="font-mono text-[10px] text-text-muted">
          {statusLabel[ticket.status] ?? ticket.status}
        </span>
        <span className="font-mono text-[10px] text-text-muted">by {ticket.filed_by}</span>
        {ticket.assigned_to && (
          <span className="font-mono text-[10px] text-text-muted">→ {ticket.assigned_to}</span>
        )}
      </div>
    </button>
  );
}
