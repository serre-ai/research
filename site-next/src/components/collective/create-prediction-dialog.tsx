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
import { useCreatePrediction } from '@/hooks/use-prediction-mutations';
import { Plus } from 'lucide-react';

export function CreatePredictionDialog() {
  const [open, setOpen] = useState(false);
  const [author, setAuthor] = useState('sol');
  const [claim, setClaim] = useState('');
  const [probability, setProbability] = useState(50);
  const [category, setCategory] = useState('');
  const [project, setProject] = useState('');

  const createPrediction = useCreatePrediction();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!claim.trim()) return;

    createPrediction.mutate(
      {
        author,
        claim: claim.trim(),
        probability: probability / 100,
        ...(category.trim() ? { category: category.trim() } : {}),
        ...(project.trim() ? { project: project.trim() } : {}),
      },
      {
        onSuccess: () => {
          setOpen(false);
          setClaim('');
          setProbability(50);
          setCategory('');
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
          New Prediction
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>New Prediction</DialogTitle>
        <DialogDescription>Create a new prediction for the collective to track.</DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <Label className="mb-1.5 block">Author</Label>
            <AgentSelector value={author} onChange={setAuthor} />
          </div>
          <div>
            <Label className="mb-1.5 block">Claim</Label>
            <textarea
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              placeholder="What do you predict will happen?"
              rows={3}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
            />
          </div>
          <div>
            <Label className="mb-1.5 block">Probability: {probability}%</Label>
            <input
              type="range"
              min={0}
              max={100}
              value={probability}
              onChange={(e) => setProbability(Number(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between font-mono text-[10px] text-text-muted">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="flex-1">
              <Label className="mb-1.5 block">Category</Label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="Optional"
                className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
              />
            </div>
            <div className="flex-1">
              <Label className="mb-1.5 block">Project</Label>
              <input
                type="text"
                value={project}
                onChange={(e) => setProject(e.target.value)}
                placeholder="Optional"
                className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={createPrediction.isPending || !claim.trim()}>
              {createPrediction.isPending ? 'Creating...' : 'Create Prediction'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
