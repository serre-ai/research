'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Mail } from 'lucide-react';
import { AgentNameBadge } from './agent-name-badge';
import type { Message } from '@/lib/message-types';

interface MessageDetailProps {
  message: Message | undefined;
  onMarkRead?: (id: number) => void;
  isLoading?: boolean;
}

export function MessageDetail({ message, onMarkRead, isLoading }: MessageDetailProps) {
  if (isLoading) {
    return (
      <Card className="space-y-4">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-3 w-40" />
        <Skeleton className="h-24 w-full" />
      </Card>
    );
  }

  if (!message) {
    return (
      <Card>
        <EmptyState
          icon={Mail}
          message="Select a message"
          description="Choose a message from the list to view its content"
        />
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <h2 className="font-mono text-lg font-semibold text-text-bright mb-3">{message.subject}</h2>
        <div className="flex items-center gap-3 mb-1">
          <span className="font-mono text-[10px] text-text-muted">From:</span>
          <AgentNameBadge agentId={message.from_agent} />
        </div>
        <div className="flex items-center gap-3 mb-3">
          <span className="font-mono text-[10px] text-text-muted">To:</span>
          <AgentNameBadge agentId={message.to_agent} />
        </div>
        <p className="font-mono text-[10px] text-text-muted">
          {new Date(message.created_at).toLocaleString()}
        </p>
      </Card>

      <Card>
        <p className="font-mono text-sm text-text-secondary whitespace-pre-wrap">{message.body}</p>
      </Card>

      {message.read_at === null && onMarkRead && (
        <Button variant="outline" size="sm" onClick={() => onMarkRead(message.id)}>
          Mark as read
        </Button>
      )}
    </div>
  );
}
