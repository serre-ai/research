'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { MessageSquare } from 'lucide-react';
import { ThreadCard } from '@/components/collective/thread-card';
import { ThreadDetail } from '@/components/collective/thread-detail';
import { CreateThreadDialog } from '@/components/collective/create-thread-dialog';
import { useForumThreads, useForumThread } from '@/hooks/use-collective';
import type { PostType } from '@/lib/collective-types';

const POST_TYPES: { label: string; value: string }[] = [
  { label: 'All Types', value: '' },
  { label: 'Proposal', value: 'proposal' },
  { label: 'Debate', value: 'debate' },
  { label: 'Signal', value: 'signal' },
  { label: 'Prediction', value: 'prediction' },
  { label: 'Synthesis', value: 'synthesis' },
];

const STATUSES: { label: string; value: string }[] = [
  { label: 'All Status', value: '' },
  { label: 'Open', value: 'open' },
  { label: 'Resolved', value: 'resolved' },
  { label: 'Archived', value: 'archived' },
];

export default function ForumPage() {
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const filters: Record<string, string> = {};
  if (typeFilter) filters.type = typeFilter;
  if (statusFilter) filters.status = statusFilter;

  const { data: threads, isLoading: threadsLoading } = useForumThreads(
    Object.keys(filters).length > 0 ? filters : undefined,
  );
  const { data: threadDetail, isLoading: detailLoading } = useForumThread(selectedThreadId);

  return (
    <div className="flex gap-4 h-[calc(100vh-220px)]">
      {/* Thread list */}
      <div className="w-2/5 flex flex-col border border-border bg-bg-elevated">
        {/* Filter bar */}
        <div className="flex gap-2 p-3 border-b border-border">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="flex-1 bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
          >
            {POST_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flex-1 bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
          >
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
          <CreateThreadDialog />
        </div>

        {/* Thread list */}
        <div className="flex-1 overflow-y-auto">
          {threadsLoading ? (
            <div className="space-y-0 divide-y divide-border">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="p-4 space-y-2">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-24" />
                </div>
              ))}
            </div>
          ) : threads && threads.length > 0 ? (
            threads.map((thread) => (
              <ThreadCard
                key={thread.id}
                thread={thread}
                isSelected={selectedThreadId === thread.thread_id}
                onClick={() => setSelectedThreadId(thread.thread_id)}
              />
            ))
          ) : (
            <EmptyState
              icon={MessageSquare}
              message="No threads found"
              description="Try changing the filters"
              className="py-12"
            />
          )}
        </div>
      </div>

      {/* Thread detail */}
      <div className="w-3/5 overflow-y-auto">
        <ThreadDetail detail={threadDetail} isLoading={detailLoading} />
      </div>
    </div>
  );
}
