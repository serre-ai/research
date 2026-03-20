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
import { useSendMessage } from '@/hooks/use-messages';
import { PenSquare } from 'lucide-react';
import type { MessagePriority } from '@/lib/message-types';

export function ComposeMessageDialog() {
  const [open, setOpen] = useState(false);
  const [fromAgent, setFromAgent] = useState('sol');
  const [toAgent, setToAgent] = useState('noor');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [priority, setPriority] = useState<MessagePriority>('normal');

  const sendMessage = useSendMessage();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!subject.trim() || !body.trim()) return;

    sendMessage.mutate(
      {
        from_agent: fromAgent,
        to_agent: toAgent,
        subject: subject.trim(),
        body: body.trim(),
        priority,
      },
      {
        onSuccess: () => {
          setOpen(false);
          setSubject('');
          setBody('');
        },
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <PenSquare className="h-3 w-3 mr-1" />
          Compose
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>New Message</DialogTitle>
        <DialogDescription>Send a direct message between agents.</DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <Label className="mb-1.5 block">From</Label>
              <AgentSelector value={fromAgent} onChange={setFromAgent} />
            </div>
            <div className="flex-1">
              <Label className="mb-1.5 block">To</Label>
              <AgentSelector value={toAgent} onChange={setToAgent} />
            </div>
          </div>
          <div>
            <Label className="mb-1.5 block">Subject</Label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Message subject..."
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
            />
          </div>
          <div>
            <Label className="mb-1.5 block">Body</Label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Write your message..."
              rows={5}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
            />
          </div>
          <div className="flex items-center gap-3">
            <Label>Priority</Label>
            <label className="flex items-center gap-1.5 font-mono text-xs text-text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={priority === 'urgent'}
                onChange={(e) => setPriority(e.target.checked ? 'urgent' : 'normal')}
                className="accent-primary"
              />
              Urgent
            </label>
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={sendMessage.isPending || !subject.trim() || !body.trim()}>
              {sendMessage.isPending ? 'Sending...' : 'Send Message'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
