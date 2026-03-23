/**
 * Test data factories for orchestrator tests.
 * All timestamps are fixed for deterministic assertions.
 */

const FIXED_TIMESTAMP = "2026-03-15T00:00:00.000Z";

export function createMockProject(overrides: Record<string, unknown> = {}) {
  return {
    project: "reasoning-gaps",
    title: "Reasoning Gaps in LLMs",
    venue: "NeurIPS 2026",
    phase: "analysis",
    status: "active",
    confidence: 0.8,
    updated: FIXED_TIMESTAMP,
    next_steps: ["Run final evaluation"],
    metrics: {},
    git: { branch: "main" },
    ...overrides,
  };
}

export function createMockSession(overrides: Record<string, unknown> = {}) {
  return {
    session_id: "test-session-001",
    project: "reasoning-gaps",
    agent_type: "researcher",
    status: "completed",
    started_at: FIXED_TIMESTAMP,
    duration_s: 300,
    cost_usd: 1.5,
    turns: 25,
    commits_created: 2,
    ...overrides,
  };
}

export function createMockEvalJob(overrides: Record<string, unknown> = {}) {
  return {
    id: "eval-job-001",
    model: "claude-haiku-4-5-20251001",
    task: "B1_addition",
    condition: "direct",
    project: "reasoning-gaps",
    status: "queued",
    created_at: FIXED_TIMESTAMP,
    ...overrides,
  };
}
