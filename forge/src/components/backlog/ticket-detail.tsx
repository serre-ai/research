'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { ClipboardList } from 'lucide-react';
import { useUpdateTicket } from '@/hooks/use-backlog';
import type { BacklogTicket, TicketStatus } from '@/lib/backlog-types';

interface TicketDetailProps {
  ticket: BacklogTicket | undefined;
  isLoading?: boolean;
}

const priorityVariant: Record<string, 'default' | 'success' | 'warning' | 'error'> = {
  low: 'default',
  medium: 'default',
  high: 'warning',
  critical: 'error',
};

const STATUS_TRANSITIONS: Record<string, TicketStatus[]> = {
  open: ['in_progress', 'wont_fix'],
  in_progress: ['done', 'open'],
  done: ['open'],
  wont_fix: ['open'],
};

const statusLabel: Record<string, string> = {
  open: 'Open',
  in_progress: 'In Progress',
  done: 'Done',
  wont_fix: "Won't Fix",
};

export function TicketDetail({ ticket, isLoading }: TicketDetailProps) {
  const updateTicket = useUpdateTicket();

  if (isLoading) {
    return (
      <Card className="space-y-4">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-3 w-40" />
        <Skeleton className="h-24 w-full" />
      </Card>
    );
  }

  if (!ticket) {
    return (
      <Card>
        <EmptyState
          icon={ClipboardList}
          message="Select a ticket"
          description="Choose a ticket from the list to view details"
        />
      </Card>
    );
  }

  const transitions = STATUS_TRANSITIONS[ticket.status] ?? [];

  return (
    <div className="space-y-4">
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <Badge variant={priorityVariant[ticket.priority] ?? 'default'}>
            {ticket.priority}
          </Badge>
          <Badge variant="outline">{ticket.category}</Badge>
          <span className="font-mono text-[10px] text-text-muted uppercase">
            {statusLabel[ticket.status] ?? ticket.status}
          </span>
        </div>
        <h2 className="font-mono text-lg font-semibold text-text-bright mb-2">{ticket.title}</h2>
        <div className="flex items-center gap-4 font-mono text-xs text-text-muted">
          <span>Filed by {ticket.filed_by}</span>
          <span>{new Date(ticket.created_at).toLocaleString()}</span>
        </div>
        {ticket.assigned_to && (
          <p className="font-mono text-xs text-text-secondary mt-2">
            Assigned to: {ticket.assigned_to}
          </p>
        )}
      </Card>

      {ticket.description && (
        <Card>
          <Label className="mb-2 block">Description</Label>
          <p className="font-mono text-sm text-text-secondary whitespace-pre-wrap">
            {ticket.description}
          </p>
        </Card>
      )}

      {transitions.length > 0 && (
        <Card>
          <Label className="mb-3 block">Actions</Label>
          <div className="flex gap-2">
            {transitions.map((status) => (
              <Button
                key={status}
                variant="outline"
                size="sm"
                disabled={updateTicket.isPending}
                onClick={() => updateTicket.mutate({ id: ticket.id, status })}
              >
                {statusLabel[status] ?? status}
              </Button>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
