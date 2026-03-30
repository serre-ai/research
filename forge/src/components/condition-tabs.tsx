'use client';

interface ConditionTabsProps {
  conditions: string[];
  active: string;
  onChange: (condition: string) => void;
}

const DISPLAY_NAMES: Record<string, string> = {
  direct: 'direct',
  cot: 'chain-of-thought',
  budget_cot: 'budget-cot',
  tool_use: 'tool-use',
};

export function ConditionTabs({ conditions, active, onChange }: ConditionTabsProps) {
  return (
    <div className="flex gap-2">
      {conditions.map((condition) => (
        <button
          key={condition}
          onClick={() => onChange(condition)}
          className={`border px-2 py-1 font-mono text-xs ${
            condition === active
              ? 'border-text-bright text-text-bright bg-bg-elevated'
              : 'border-border text-text-muted hover:text-text-secondary'
          }`}
        >
          [{DISPLAY_NAMES[condition] ?? condition}]
        </button>
      ))}
    </div>
  );
}
