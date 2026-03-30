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
import { useDispatchSession } from '@/hooks/use-session-dispatch';
import { Zap } from 'lucide-react';

const AGENT_TYPES = [
  'researcher',
  'writer',
  'reviewer',
  'analyst',
  'verifier',
  'evaluator',
  'planner',
];

interface DispatchSessionDialogProps {
  projectName: string;
}

export function DispatchSessionDialog({ projectName }: DispatchSessionDialogProps) {
  const [open, setOpen] = useState(false);
  const [agentType, setAgentType] = useState('researcher');
  const [reason, setReason] = useState('');

  const dispatch = useDispatchSession();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!reason.trim()) return;

    dispatch.mutate(
      {
        project: projectName,
        agent_type: agentType,
        reason: reason.trim(),
        triggered_by: 'operator',
      },
      {
        onSuccess: () => {
          setOpen(false);
          setReason('');
        },
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Zap className="h-3 w-3 mr-1" />
          Dispatch Session
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Dispatch Session</DialogTitle>
        <DialogDescription>
          Queue a new agent session for {projectName}.
        </DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <Label className="mb-1.5 block">Agent Type</Label>
            <select
              value={agentType}
              onChange={(e) => setAgentType(e.target.value)}
              className="w-full bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
            >
              {AGENT_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <Label className="mb-1.5 block">Reason</Label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Why should this session run?"
              rows={3}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={dispatch.isPending || !reason.trim()}>
              {dispatch.isPending ? 'Dispatching...' : 'Dispatch'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
