'use client';

interface ProbabilityBarProps {
  value: number;
}

function probColor(value: number): string {
  if (value >= 0.7) return '#10b981';
  if (value >= 0.4) return '#f59e0b';
  return '#ef4444';
}

export function ProbabilityBar({ value }: ProbabilityBarProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex h-2 w-full border border-border">
        <div
          className="h-full"
          style={{ width: `${value * 100}%`, backgroundColor: probColor(value) }}
        />
      </div>
      <span className="font-mono text-xs text-text-secondary tabular-nums w-10 text-right">
        {(value * 100).toFixed(0)}%
      </span>
    </div>
  );
}
