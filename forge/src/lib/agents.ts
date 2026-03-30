export interface AgentMeta {
  id: string;
  displayName: string;
  role: string;
  color: string;
  model: string;
}

export const AGENTS: Record<string, AgentMeta> = {
  sol: { id: 'sol', displayName: 'Sol', role: 'Research Lead', color: '#EAB308', model: 'claude-opus-4-6' },
  noor: { id: 'noor', displayName: 'Noor', role: 'Methodology', color: '#F97316', model: 'claude-opus-4-6' },
  vera: { id: 'vera', displayName: 'Vera', role: 'Verification', color: '#38BDF8', model: 'claude-sonnet-4-6' },
  kit: { id: 'kit', displayName: 'Kit', role: 'Implementation', color: '#84CC16', model: 'claude-sonnet-4-6' },
  maren: { id: 'maren', displayName: 'Maren', role: 'Writing', color: '#EC4899', model: 'claude-opus-4-6' },
  eli: { id: 'eli', displayName: 'Eli', role: 'Literature', color: '#94A3B8', model: 'claude-sonnet-4-6' },
  lev: { id: 'lev', displayName: 'Lev', role: 'Statistics', color: '#D97706', model: 'claude-sonnet-4-6' },
  rho: { id: 'rho', displayName: 'Rho', role: 'Governance', color: '#DC2626', model: 'claude-sonnet-4-6' },
  sage: { id: 'sage', displayName: 'Sage', role: 'Facilitation', color: '#14B8A6', model: 'claude-sonnet-4-6' },
} as const;

export const AGENT_IDS = Object.keys(AGENTS);

export function getAgent(id: string): AgentMeta | undefined {
  return AGENTS[id];
}

export function getAgentColor(id: string): string {
  return AGENTS[id]?.color ?? '#737373';
}
