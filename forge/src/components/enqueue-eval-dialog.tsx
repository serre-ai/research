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
import { useEnqueueEvalJob } from '@/hooks/use-eval-jobs';
import { Plus } from 'lucide-react';

const CONDITIONS = [
  { label: 'Direct', value: 'direct' },
  { label: 'Chain of Thought', value: 'cot' },
  { label: 'Budget CoT', value: 'budget_cot' },
];

export function EnqueueEvalDialog() {
  const [open, setOpen] = useState(false);
  const [model, setModel] = useState('');
  const [task, setTask] = useState('');
  const [condition, setCondition] = useState('direct');
  const [project, setProject] = useState('');

  const enqueueJob = useEnqueueEvalJob();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!model.trim() || !task.trim()) return;

    enqueueJob.mutate(
      {
        model: model.trim(),
        task: task.trim(),
        condition,
        ...(project.trim() ? { project: project.trim() } : {}),
      },
      {
        onSuccess: () => {
          setOpen(false);
          setModel('');
          setTask('');
          setCondition('direct');
          setProject('');
        },
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="h-3 w-3 mr-1" />
          Enqueue Eval
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Enqueue Eval Job</DialogTitle>
        <DialogDescription>Submit a new evaluation job to the queue.</DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <Label className="mb-1.5 block">Model</Label>
              <input
                type="text"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="e.g. claude-sonnet-4-20250514"
                className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
              />
            </div>
            <div className="flex-1">
              <Label className="mb-1.5 block">Condition</Label>
              <select
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
                className="w-full bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
              >
                {CONDITIONS.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <Label className="mb-1.5 block">Task</Label>
            <input
              type="text"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="e.g. B1_syllogistic"
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
            />
          </div>
          <div>
            <Label className="mb-1.5 block">Project (optional)</Label>
            <input
              type="text"
              value={project}
              onChange={(e) => setProject(e.target.value)}
              placeholder="e.g. reasoning-gaps"
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={enqueueJob.isPending || !model.trim() || !task.trim()}>
              {enqueueJob.isPending ? 'Enqueuing...' : 'Enqueue Job'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
