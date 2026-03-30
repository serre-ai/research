'use client';

import { useState } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Mail } from 'lucide-react';
import { AgentSelector } from '@/components/collective/agent-selector';
import { MessageCard } from '@/components/collective/message-card';
import { MessageDetail } from '@/components/collective/message-detail';
import { ComposeMessageDialog } from '@/components/collective/compose-message-dialog';
import { useInbox, useMarkRead } from '@/hooks/use-messages';
import type { Message } from '@/lib/message-types';

const PRIORITIES: { label: string; value: string }[] = [
  { label: 'All Priority', value: '' },
  { label: 'Normal', value: 'normal' },
  { label: 'Urgent', value: 'urgent' },
];

export default function MessagesPage() {
  const [selectedAgent, setSelectedAgent] = useState('sol');
  const [selectedMessageId, setSelectedMessageId] = useState<number | null>(null);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [priorityFilter, setPriorityFilter] = useState('');

  const filters: Record<string, string | boolean> = {};
  if (unreadOnly) filters.unread = true;
  if (priorityFilter) filters.priority = priorityFilter;

  const { data: messages, isLoading } = useInbox(selectedAgent, {
    unread: unreadOnly || undefined,
    priority: priorityFilter || undefined,
  });
  const markRead = useMarkRead();

  const selectedMessage = messages?.find((m) => m.id === selectedMessageId);

  return (
    <div className="space-y-4">
      {/* Top bar */}
      <div className="flex items-center gap-3">
        <AgentSelector value={selectedAgent} onChange={setSelectedAgent} />
        <ComposeMessageDialog />
        <label className="flex items-center gap-1.5 font-mono text-xs text-text-secondary cursor-pointer">
          <input
            type="checkbox"
            checked={unreadOnly}
            onChange={(e) => setUnreadOnly(e.target.checked)}
            className="accent-primary"
          />
          Unread only
        </label>
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
        >
          {PRIORITIES.map((p) => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
      </div>

      {/* Split pane */}
      <div className="flex gap-4 h-[calc(100vh-280px)]">
        {/* Message list */}
        <div className="w-2/5 flex flex-col border border-border bg-bg-elevated">
          <div className="flex-1 overflow-y-auto">
            {isLoading ? (
              <div className="space-y-0 divide-y divide-border">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="p-4 space-y-2">
                    <Skeleton className="h-3 w-32" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-48" />
                  </div>
                ))}
              </div>
            ) : messages && messages.length > 0 ? (
              messages.map((message) => (
                <MessageCard
                  key={message.id}
                  message={message}
                  isSelected={selectedMessageId === message.id}
                  onClick={() => setSelectedMessageId(message.id)}
                />
              ))
            ) : (
              <EmptyState
                icon={Mail}
                message="No messages"
                description="This inbox is empty"
                className="py-12"
              />
            )}
          </div>
        </div>

        {/* Message detail */}
        <div className="w-3/5 overflow-y-auto">
          <MessageDetail
            message={selectedMessage}
            onMarkRead={(id) => markRead.mutate(id)}
          />
        </div>
      </div>
    </div>
  );
}
