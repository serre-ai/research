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
import { useCreateThread } from '@/hooks/use-forum-mutations';
import { Plus } from 'lucide-react';
import type { PostType } from '@/lib/collective-types';

const POST_TYPES: { label: string; value: PostType }[] = [
  { label: 'Proposal', value: 'proposal' },
  { label: 'Debate', value: 'debate' },
  { label: 'Signal', value: 'signal' },
  { label: 'Prediction', value: 'prediction' },
  { label: 'Synthesis', value: 'synthesis' },
];

export function CreateThreadDialog() {
  const [open, setOpen] = useState(false);
  const [author, setAuthor] = useState('sol');
  const [postType, setPostType] = useState<PostType>('proposal');
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');

  const createThread = useCreateThread();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !body.trim()) return;

    createThread.mutate(
      { author, title: title.trim(), body: body.trim(), post_type: postType },
      {
        onSuccess: () => {
          setOpen(false);
          setTitle('');
          setBody('');
        },
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="h-3 w-3 mr-1" />
          New Thread
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>New Forum Thread</DialogTitle>
        <DialogDescription>Create a new discussion thread in the collective forum.</DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <Label className="mb-1.5 block">Author</Label>
              <AgentSelector value={author} onChange={setAuthor} />
            </div>
            <div className="flex-1">
              <Label className="mb-1.5 block">Type</Label>
              <select
                value={postType}
                onChange={(e) => setPostType(e.target.value as PostType)}
                className="w-full bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
              >
                {POST_TYPES.map((t) => (
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
              placeholder="Thread title..."
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
            />
          </div>
          <div>
            <Label className="mb-1.5 block">Body</Label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Thread content..."
              rows={5}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={createThread.isPending || !title.trim() || !body.trim()}>
              {createThread.isPending ? 'Creating...' : 'Create Thread'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
