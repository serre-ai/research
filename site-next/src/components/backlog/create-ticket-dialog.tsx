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
import { useCreateTicket } from '@/hooks/use-backlog';
import { Plus } from 'lucide-react';
import type { TicketPriority, TicketCategory } from '@/lib/backlog-types';

const PRIORITIES: TicketPriority[] = ['low', 'medium', 'high', 'critical'];
const CATEGORIES: TicketCategory[] = ['daemon', 'api', 'agents', 'eval', 'infra', 'other'];

export function CreateTicketDialog() {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [filedBy, setFiledBy] = useState('operator');
  const [priority, setPriority] = useState<TicketPriority>('medium');
  const [category, setCategory] = useState<TicketCategory>('other');

  const createTicket = useCreateTicket();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;

    createTicket.mutate(
      {
        title: title.trim(),
        filed_by: filedBy.trim(),
        priority,
        category,
        description: description.trim() || undefined,
      },
      {
        onSuccess: () => {
          setOpen(false);
          setTitle('');
          setDescription('');
        },
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="h-3 w-3 mr-1" />
          New Ticket
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>New Ticket</DialogTitle>
        <DialogDescription>File a new backlog ticket for the platform.</DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <Label className="mb-1.5 block">Title</Label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ticket title..."
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
            />
          </div>
          <div className="flex gap-3">
            <div className="flex-1">
              <Label className="mb-1.5 block">Priority</Label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as TicketPriority)}
                className="w-full bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
              >
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <Label className="mb-1.5 block">Category</Label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as TicketCategory)}
                className="w-full bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <Label className="mb-1.5 block">Filed By</Label>
            <input
              type="text"
              value={filedBy}
              onChange={(e) => setFiledBy(e.target.value)}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
            />
          </div>
          <div>
            <Label className="mb-1.5 block">Description (optional)</Label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Details..."
              rows={4}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={createTicket.isPending || !title.trim()}>
              {createTicket.isPending ? 'Creating...' : 'Create Ticket'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
