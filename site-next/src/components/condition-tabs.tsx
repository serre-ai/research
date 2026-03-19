'use client';

import { clsx } from 'clsx';

interface ConditionTabsProps {
  conditions: string[];
  active: string;
  onChange: (condition: string) => void;
}

const DISPLAY_NAMES: Record<string, string> = {
  direct: 'Direct',
  cot: 'Chain-of-Thought',
  budget_cot: 'Budget CoT',
  tool_use: 'Tool Use',
};

export function ConditionTabs({ conditions, active, onChange }: ConditionTabsProps) {
  return (
    <div className="flex border-b border-border">
      {conditions.map((condition) => (
        <button
          key={condition}
          onClick={() => onChange(condition)}
          className={clsx(
            'px-4 py-2 font-mono text-sm border-b-2 -mb-px transition-colors',
            condition === active
              ? 'border-primary text-text-bright'
              : 'border-transparent text-text-muted hover:text-text-secondary',
          )}
        >
          {DISPLAY_NAMES[condition] ?? condition}
        </button>
      ))}
    </div>
  );
}
