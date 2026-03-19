'use client';

import { useMemo } from 'react';
import { clsx } from 'clsx';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import type { EvalRun } from '@/lib/types';

interface HeatmapProps {
  runs: EvalRun[];
  condition: string;
  onCellClick?: (model: string, task: string) => void;
}

function accuracyColor(value: number): string {
  if (value >= 85) return 'bg-emerald-500/20 text-emerald-400';
  if (value >= 70) return 'bg-emerald-500/10 text-emerald-300';
  if (value >= 50) return 'bg-yellow-500/15 text-yellow-400';
  if (value >= 30) return 'bg-orange-500/15 text-orange-400';
  return 'bg-red-500/15 text-red-400';
}

function formatAccuracy(value: number): string {
  return (value * 100).toFixed(1);
}

export function AccuracyHeatmap({ runs, condition, onCellClick }: HeatmapProps) {
  const { models, tasks, grid } = useMemo(() => {
    const filtered = runs.filter((r) => r.condition === condition);

    const modelSet = new Set<string>();
    const taskSet = new Set<string>();
    const lookup = new Map<string, { accuracy: number; instances: number }>();

    for (const run of filtered) {
      modelSet.add(run.model);
      taskSet.add(run.task);
      lookup.set(`${run.model}::${run.task}`, {
        accuracy: run.accuracy,
        instances: run.instances,
      });
    }

    const models = Array.from(modelSet).sort();
    const tasks = Array.from(taskSet).sort();

    return { models, tasks, grid: lookup };
  }, [runs, condition]);

  if (models.length === 0 || tasks.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-text-muted font-mono">
        No data for this condition
      </div>
    );
  }

  return (
    <TooltipProvider delayDuration={150}>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse font-mono text-xs">
          <thead>
            <tr>
              <th className="sticky left-0 z-10 bg-bg-base border border-border px-3 py-2 text-left text-text-muted font-medium min-w-[140px]">
                Model
              </th>
              {tasks.map((task) => (
                <th
                  key={task}
                  className="border border-border px-3 py-2 text-center text-text-muted font-medium min-w-[72px]"
                >
                  {task}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {models.map((model) => (
              <tr key={model}>
                <td className="sticky left-0 z-10 bg-bg-base border border-border px-3 py-2 text-text-secondary font-medium whitespace-nowrap">
                  {model}
                </td>
                {tasks.map((task) => {
                  const cell = grid.get(`${model}::${task}`);

                  if (!cell) {
                    return (
                      <td
                        key={task}
                        className="border border-border px-3 py-2 text-center text-text-muted bg-bg-elevated"
                      >
                        &mdash;
                      </td>
                    );
                  }

                  const pct = cell.accuracy;
                  const displayPct = formatAccuracy(pct);

                  return (
                    <td key={task} className="border border-border p-0">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button
                            onClick={() => onCellClick?.(model, task)}
                            className={clsx(
                              'w-full px-3 py-2 text-center tabular-nums transition-colors',
                              accuracyColor(pct * 100),
                              onCellClick && 'cursor-pointer hover:opacity-80',
                              !onCellClick && 'cursor-default',
                            )}
                          >
                            {displayPct}
                          </button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <div className="space-y-1">
                            <div className="font-medium text-text-bright">{model} / {task}</div>
                            <div>Accuracy: {displayPct}%</div>
                            <div>Instances: {cell.instances.toLocaleString()}</div>
                            <div>Condition: {condition}</div>
                          </div>
                        </TooltipContent>
                      </Tooltip>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </TooltipProvider>
  );
}
