'use client';

import { useMemo } from 'react';
import type { EvalRun } from '@/lib/types';

interface HeatmapProps {
  runs: EvalRun[];
  condition: string;
  onCellClick?: (model: string, task: string) => void;
}

function accuracyColor(pct: number): string {
  if (pct >= 85) return 'text-[--color-success]';
  if (pct >= 70) return 'text-[--color-success] opacity-70';
  if (pct >= 50) return 'text-[--color-secondary]';
  if (pct >= 30) return 'text-[--color-secondary] opacity-70';
  return 'text-[--color-danger]';
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

    return {
      models: Array.from(modelSet).sort(),
      tasks: Array.from(taskSet).sort(),
      grid: lookup,
    };
  }, [runs, condition]);

  if (models.length === 0 || tasks.length === 0) {
    return <span className="text-text-muted">no data for this condition</span>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="tui-table">
        <thead>
          <tr>
            <th>Model</th>
            {tasks.map((task) => (
              <th key={task} className="text-center">{task}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {models.map((model) => (
            <tr key={model}>
              <td className="text-text-secondary">{model}</td>
              {tasks.map((task) => {
                const cell = grid.get(`${model}::${task}`);
                if (!cell) {
                  return <td key={task} className="text-center text-text-muted">--</td>;
                }
                const pct = cell.accuracy * 100;
                return (
                  <td
                    key={task}
                    className={`text-center tabular-nums ${accuracyColor(pct)} ${onCellClick ? 'cursor-pointer hover:bg-bg-hover' : ''}`}
                    onClick={() => onCellClick?.(model, task)}
                    title={`${model} / ${task}: ${pct.toFixed(1)}% (n=${cell.instances})`}
                  >
                    {pct.toFixed(1)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
