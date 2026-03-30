'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { AgentSelector } from './agent-selector';
import { useReplyToThread } from '@/hooks/use-forum-mutations';

interface ReplyFormProps {
  threadId: string;
}

export function ReplyForm({ threadId }: ReplyFormProps) {
  const [author, setAuthor] = useState('sol');
  const [body, setBody] = useState('');
  const [expanded, setExpanded] = useState(false);

  const reply = useReplyToThread(threadId);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!body.trim()) return;

    reply.mutate(
      { author, body: body.trim() },
      { onSuccess: () => { setBody(''); setExpanded(false); } },
    );
  }

  if (!expanded) {
    return (
      <Button variant="outline" size="sm" onClick={() => setExpanded(true)}>
        Reply
      </Button>
    );
  }

  return (
    <Card>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex items-center gap-3">
          <Label>Reply as</Label>
          <AgentSelector value={author} onChange={setAuthor} />
        </div>
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Write a reply..."
          rows={3}
          className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
          autoFocus
        />
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" size="sm" onClick={() => setExpanded(false)}>
            Cancel
          </Button>
          <Button type="submit" size="sm" disabled={reply.isPending || !body.trim()}>
            {reply.isPending ? 'Posting...' : 'Post Reply'}
          </Button>
        </div>
      </form>
    </Card>
  );
}
