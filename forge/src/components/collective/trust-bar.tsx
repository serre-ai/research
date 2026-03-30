'use client';

interface TrustBarProps {
  value: number;
  className?: string;
}

function trustColor(value: number): string {
  if (value >= 0.75) return '#10b981';
  if (value >= 0.5) return '#f59e0b';
  return '#ef4444';
}

export function TrustBar({ value, className }: TrustBarProps) {
  const color = trustColor(value);

  return (
    <div className={className}>
      <div className="flex h-2 w-full border border-border">
        <div
          className="h-full transition-all"
          style={{ width: `${value * 100}%`, backgroundColor: color }}
        />
      </div>
      <span className="font-mono text-[10px] text-text-muted">{value.toFixed(2)}</span>
    </div>
  );
}
