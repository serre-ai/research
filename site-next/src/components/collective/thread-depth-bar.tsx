'use client';

interface ThreadDepthBarProps {
  depth: number;
  max?: number;
}

export function ThreadDepthBar({ depth, max = 10 }: ThreadDepthBarProps) {
  return (
    <div className="flex items-center gap-1">
      <span className="font-mono text-[10px] text-text-muted mr-1">Depth</span>
      {Array.from({ length: max }).map((_, i) => {
        const filled = i < depth;
        let color = '#3b82f6';
        if (depth >= 10) color = '#ef4444';
        else if (depth >= 8) color = '#f59e0b';

        return (
          <div
            key={i}
            className="h-3 w-2 border border-border"
            style={{ backgroundColor: filled ? color : 'transparent' }}
          />
        );
      })}
      <span className="font-mono text-[10px] text-text-muted ml-1">{depth}/{max}</span>
    </div>
  );
}
