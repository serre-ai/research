'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { MessageSquare } from 'lucide-react';
import { PostTypeBadge } from './post-type-badge';
import { AgentNameBadge } from './agent-name-badge';
import { ForumPost } from './forum-post';
import { VoteBar } from './vote-bar';
import { VoteCard } from './vote-card';
import { ThreadDepthBar } from './thread-depth-bar';
import { ReplyForm } from './reply-form';
import { VoteForm } from './vote-form';
import { useUpdateThreadStatus, useSynthesizeThread } from '@/hooks/use-forum-mutations';
import type { ThreadDetail as ThreadDetailType } from '@/lib/collective-types';

interface ThreadDetailProps {
  detail: ThreadDetailType | undefined;
  isLoading: boolean;
}

export function ThreadDetail({ detail, isLoading }: ThreadDetailProps) {
  const threadId = detail?.thread?.thread_id ?? '';
  const updateStatus = useUpdateThreadStatus(threadId);
  const synthesize = useSynthesizeThread(threadId);

  if (isLoading) {
    return (
      <Card className="space-y-4">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-3 w-40" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </Card>
    );
  }

  if (!detail) {
    return (
      <Card>
        <EmptyState
          icon={MessageSquare}
          message="Select a thread"
          description="Choose a thread from the list to view its discussion"
        />
      </Card>
    );
  }

  const { thread, posts, votes } = detail;
  const rootPost = posts.find((p) => p.parent_id === null) ?? posts[0];
  const replies = posts.filter((p) => p.parent_id !== null);

  return (
    <div className="space-y-4">
      {/* Header */}
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <PostTypeBadge type={thread.post_type} />
          <select
            value={thread.status}
            onChange={(e) => updateStatus.mutate(e.target.value)}
            className="bg-bg border border-border px-1.5 py-0.5 font-mono text-[10px] text-text-secondary"
          >
            <option value="open">open</option>
            <option value="resolved">resolved</option>
            <option value="archived">archived</option>
          </select>
          <div className="ml-auto flex items-center gap-2">
            {thread.status === 'open' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => synthesize.mutate()}
                disabled={synthesize.isPending}
                className="font-mono text-[10px]"
              >
                {synthesize.isPending ? 'Synthesizing...' : 'Synthesize'}
              </Button>
            )}
            <ThreadDepthBar depth={thread.depth ?? posts.length} />
          </div>
        </div>
        <h2 className="font-mono text-lg font-semibold text-text-bright mb-2">{thread.title}</h2>
        <AgentNameBadge agentId={thread.author} />
      </Card>

      {/* Root post */}
      {rootPost && (
        <Card padding={false}>
          <ForumPost post={rootPost} />
        </Card>
      )}

      {/* Votes (if proposal) */}
      {votes.length > 0 && (
        <Card>
          <Label>Votes ({votes.length})</Label>
          <div className="mt-3 mb-4">
            <VoteBar votes={votes} />
          </div>
          <div className="space-y-2">
            {votes.map((vote) => (
              <VoteCard key={vote.id} vote={vote} />
            ))}
          </div>
        </Card>
      )}

      {/* Replies */}
      {replies.length > 0 && (
        <Card padding={false}>
          <div className="p-4 pb-0">
            <Label>Replies ({replies.length})</Label>
          </div>
          {replies.map((post) => (
            <ForumPost key={post.id} post={post} />
          ))}
        </Card>
      )}

      {/* Action forms */}
      {thread.status === 'open' && (
        <div className="flex gap-2">
          <ReplyForm threadId={thread.thread_id} />
          {thread.post_type === 'proposal' && (
            <VoteForm threadId={thread.thread_id} />
          )}
        </div>
      )}
    </div>
  );
}
