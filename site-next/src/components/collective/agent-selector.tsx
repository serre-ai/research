'use client';

import { AGENTS } from '@/lib/agents';

interface AgentSelectorProps {
  value: string;
  onChange: (id: string) => void;
  includeAll?: boolean;
}

export function AgentSelector({ value, onChange, includeAll }: AgentSelectorProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-bg border border-border px-2 py-1 font-mono text-xs text-text-secondary"
    >
      {includeAll && <option value="">All Agents</option>}
      {Object.values(AGENTS).map((agent) => (
        <option key={agent.id} value={agent.id}>
          {agent.displayName} — {agent.role}
        </option>
      ))}
    </select>
  );
}
