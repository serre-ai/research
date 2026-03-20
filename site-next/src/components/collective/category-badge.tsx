'use client';

const CATEGORY_COLORS: Record<string, string> = {
  methodology: '#3b82f6',
  results: '#10b981',
  timeline: '#f59e0b',
  process: '#a855f7',
  technical: '#38BDF8',
  quality: '#EC4899',
};

interface CategoryBadgeProps {
  category: string;
}

export function CategoryBadge({ category }: CategoryBadgeProps) {
  const color = CATEGORY_COLORS[category] ?? '#737373';

  return (
    <span
      className="inline-flex items-center px-2 py-0.5 font-mono text-[10px] font-medium border"
      style={{ color, borderColor: color, backgroundColor: `${color}15` }}
    >
      {category}
    </span>
  );
}
