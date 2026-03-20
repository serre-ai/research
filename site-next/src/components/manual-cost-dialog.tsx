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
import { useRecordManualCost } from '@/hooks/use-budget-extras';
import { Plus } from 'lucide-react';

export function ManualCostDialog() {
  const [open, setOpen] = useState(false);
  const [provider, setProvider] = useState('');
  const [costUsd, setCostUsd] = useState('');
  const [description, setDescription] = useState('');

  const recordCost = useRecordManualCost();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cost = parseFloat(costUsd);
    if (!provider.trim() || isNaN(cost) || cost <= 0 || !description.trim()) return;

    recordCost.mutate(
      {
        provider: provider.trim(),
        cost_usd: cost,
        description: description.trim(),
      },
      {
        onSuccess: () => {
          setOpen(false);
          setProvider('');
          setCostUsd('');
          setDescription('');
        },
      },
    );
  }

  const isValid =
    provider.trim() !== '' &&
    !isNaN(parseFloat(costUsd)) &&
    parseFloat(costUsd) > 0 &&
    description.trim() !== '';

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="h-3 w-3 mr-1" />
          Record Cost
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Record Manual Cost</DialogTitle>
        <DialogDescription>Log an external or manual cost entry to the budget.</DialogDescription>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <Label className="mb-1.5 block">Provider</Label>
              <input
                type="text"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                placeholder="e.g. anthropic"
                className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
              />
            </div>
            <div className="w-32">
              <Label className="mb-1.5 block">Cost (USD)</Label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={costUsd}
                onChange={(e) => setCostUsd(e.target.value)}
                placeholder="0.00"
                className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted"
              />
            </div>
          </div>
          <div>
            <Label className="mb-1.5 block">Description</Label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What was this cost for?"
              rows={3}
              className="w-full bg-bg border border-border px-3 py-2 font-mono text-sm text-text placeholder:text-text-muted resize-y"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={recordCost.isPending || !isValid}>
              {recordCost.isPending ? 'Recording...' : 'Record Cost'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
