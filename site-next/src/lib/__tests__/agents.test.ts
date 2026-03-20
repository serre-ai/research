import { AGENTS, AGENT_IDS, getAgent, getAgentColor } from '../agents';

describe('AGENTS', () => {
  it('has 9 agents', () => {
    expect(Object.keys(AGENTS)).toHaveLength(9);
  });

  it('every agent has required fields', () => {
    for (const agent of Object.values(AGENTS)) {
      expect(agent).toHaveProperty('id');
      expect(agent).toHaveProperty('displayName');
      expect(agent).toHaveProperty('role');
      expect(agent).toHaveProperty('color');
      expect(agent).toHaveProperty('model');
      expect(typeof agent.id).toBe('string');
      expect(typeof agent.displayName).toBe('string');
      expect(typeof agent.role).toBe('string');
      expect(agent.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(agent.model).toMatch(/^claude-/);
    }
  });

  it('agent ids match their keys', () => {
    for (const [key, agent] of Object.entries(AGENTS)) {
      expect(agent.id).toBe(key);
    }
  });
});

describe('AGENT_IDS', () => {
  it('has 9 ids matching AGENTS keys', () => {
    expect(AGENT_IDS).toHaveLength(9);
    expect(AGENT_IDS).toEqual(Object.keys(AGENTS));
  });
});

describe('getAgent', () => {
  it('returns agent for valid id', () => {
    const agent = getAgent('sol');
    expect(agent).toBeDefined();
    expect(agent!.displayName).toBe('Sol');
    expect(agent!.role).toBe('Research Lead');
  });

  it('returns undefined for unknown id', () => {
    expect(getAgent('nonexistent')).toBeUndefined();
  });
});

describe('getAgentColor', () => {
  it('returns color for valid agent', () => {
    expect(getAgentColor('sol')).toBe('#EAB308');
  });

  it('returns fallback for unknown agent', () => {
    expect(getAgentColor('nonexistent')).toBe('#737373');
  });
});
