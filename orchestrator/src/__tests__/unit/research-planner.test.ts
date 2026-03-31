import { describe, it, expect } from "vitest";
import { PHASE_TO_AGENT, type AgentType } from "../../session-runner.js";

/**
 * Tests for research planner pure logic.
 *
 * buildConstraints is a private method on ResearchPlanner, so we extract its
 * logic into a standalone function that mirrors the implementation. This lets
 * us test the tiered model selection and budget-aware downgrades without
 * needing to instantiate the full planner with all its dependencies.
 */

// ------------------------------------------------------------------
// Replicate buildConstraints logic as a pure function for testing
// ------------------------------------------------------------------

interface BriefConstraints {
  maxTurns: number;
  maxDurationMs: number;
  maxBudgetUsd: number;
  model: string;
}

function buildConstraints(
  agentType: AgentType,
  budgetUsd: number,
  highStakes: boolean = false,
): BriefConstraints {
  let model = "claude-sonnet-4-6"; // Tier 2 default
  let maxBudget = 5;

  // Tier 1 — Opus
  if (agentType === "theorist") {
    model = "claude-opus-4-6";
    maxBudget = 15;
  }
  if (agentType === "writer") {
    model = "claude-opus-4-6";
    maxBudget = 15;
  }
  if (agentType === "critic" && highStakes) {
    model = "claude-opus-4-6";
    maxBudget = 10;
  }

  // Tier 3 — Haiku
  if (agentType === "scout" || agentType === "strategist" || agentType === "editor") {
    model = "claude-haiku-4-5-20251001";
    maxBudget = 2;
  }

  // Budget-aware downgrades
  if (budgetUsd < 10 && model.includes("opus")) {
    model = "claude-sonnet-4-6";
    maxBudget = 5;
  }
  if (budgetUsd < 3) {
    model = "claude-haiku-4-5-20251001";
    maxBudget = 2;
  }

  return {
    maxTurns: agentType === "editor" ? 20 : agentType === "experimenter" ? 80 : 40,
    maxDurationMs: 45 * 60 * 1000,
    maxBudgetUsd: Math.min(budgetUsd, maxBudget),
    model,
  };
}

// ------------------------------------------------------------------
// Tests
// ------------------------------------------------------------------

describe("buildConstraints", () => {
  describe("tiered model selection", () => {
    it("uses Opus for theorist (Tier 1)", () => {
      const c = buildConstraints("theorist", 100);
      expect(c.model).toBe("claude-opus-4-6");
      expect(c.maxBudgetUsd).toBe(15);
    });

    it("uses Opus for writer (Tier 1)", () => {
      const c = buildConstraints("writer", 100);
      expect(c.model).toBe("claude-opus-4-6");
      expect(c.maxBudgetUsd).toBe(15);
    });

    it("uses Opus for high-stakes critic (Tier 1)", () => {
      const c = buildConstraints("critic", 100, true);
      expect(c.model).toBe("claude-opus-4-6");
      expect(c.maxBudgetUsd).toBe(10);
    });

    it("uses Sonnet for regular critic (Tier 2)", () => {
      const c = buildConstraints("critic", 100, false);
      expect(c.model).toBe("claude-sonnet-4-6");
      expect(c.maxBudgetUsd).toBe(5);
    });

    it("uses Sonnet for researcher (Tier 2 default)", () => {
      const c = buildConstraints("researcher", 100);
      expect(c.model).toBe("claude-sonnet-4-6");
      expect(c.maxBudgetUsd).toBe(5);
    });

    it("uses Sonnet for experimenter (Tier 2)", () => {
      const c = buildConstraints("experimenter", 100);
      expect(c.model).toBe("claude-sonnet-4-6");
      expect(c.maxBudgetUsd).toBe(5);
    });

    it("uses Sonnet for engineer (Tier 2)", () => {
      const c = buildConstraints("engineer", 100);
      expect(c.model).toBe("claude-sonnet-4-6");
      expect(c.maxBudgetUsd).toBe(5);
    });

    it("uses Haiku for scout (Tier 3)", () => {
      const c = buildConstraints("scout", 100);
      expect(c.model).toBe("claude-haiku-4-5-20251001");
      expect(c.maxBudgetUsd).toBe(2);
    });

    it("uses Haiku for strategist (Tier 3)", () => {
      const c = buildConstraints("strategist", 100);
      expect(c.model).toBe("claude-haiku-4-5-20251001");
      expect(c.maxBudgetUsd).toBe(2);
    });

    it("uses Haiku for editor (Tier 3)", () => {
      const c = buildConstraints("editor", 100);
      expect(c.model).toBe("claude-haiku-4-5-20251001");
      expect(c.maxBudgetUsd).toBe(2);
    });
  });

  describe("budget-aware downgrades", () => {
    it("downgrades Opus to Sonnet when budget < $10", () => {
      const c = buildConstraints("theorist", 8);
      expect(c.model).toBe("claude-sonnet-4-6");
      expect(c.maxBudgetUsd).toBe(5);
    });

    it("downgrades writer from Opus to Sonnet when budget < $10", () => {
      const c = buildConstraints("writer", 9);
      expect(c.model).toBe("claude-sonnet-4-6");
      expect(c.maxBudgetUsd).toBe(5);
    });

    it("does NOT downgrade Opus when budget is exactly $10", () => {
      const c = buildConstraints("theorist", 10);
      expect(c.model).toBe("claude-opus-4-6");
    });

    it("emergency downgrade: everything to Haiku when budget < $3", () => {
      const c = buildConstraints("researcher", 2);
      expect(c.model).toBe("claude-haiku-4-5-20251001");
      expect(c.maxBudgetUsd).toBe(2);
    });

    it("emergency downgrade applies even to theorist", () => {
      const c = buildConstraints("theorist", 1);
      expect(c.model).toBe("claude-haiku-4-5-20251001");
      expect(c.maxBudgetUsd).toBe(1); // min(1, 2) = 1
    });

    it("does NOT emergency-downgrade at exactly $3", () => {
      const c = buildConstraints("researcher", 3);
      expect(c.model).toBe("claude-sonnet-4-6");
    });

    it("caps maxBudgetUsd at available budget", () => {
      const c = buildConstraints("theorist", 12);
      // Opus maxBudget = 15, but budget is only 12
      expect(c.maxBudgetUsd).toBe(12);
    });

    it("Haiku agents are unaffected by Opus downgrade threshold", () => {
      const c = buildConstraints("scout", 8);
      // Scout is already Haiku, so budget < 10 doesn't change model
      expect(c.model).toBe("claude-haiku-4-5-20251001");
      expect(c.maxBudgetUsd).toBe(2);
    });
  });

  describe("turn limits", () => {
    it("gives editor 20 turns", () => {
      const c = buildConstraints("editor", 100);
      expect(c.maxTurns).toBe(20);
    });

    it("gives experimenter 80 turns", () => {
      const c = buildConstraints("experimenter", 100);
      expect(c.maxTurns).toBe(80);
    });

    it("gives all other agents 40 turns", () => {
      const agents: AgentType[] = ["researcher", "writer", "reviewer", "critic", "theorist", "strategist", "scout", "engineer"];
      for (const agent of agents) {
        const c = buildConstraints(agent, 100);
        expect(c.maxTurns).toBe(40);
      }
    });
  });

  describe("duration", () => {
    it("sets maxDurationMs to 45 minutes for all agents", () => {
      const agents: AgentType[] = ["researcher", "writer", "reviewer", "editor", "critic", "experimenter", "theorist", "strategist", "scout", "engineer"];
      for (const agent of agents) {
        const c = buildConstraints(agent, 100);
        expect(c.maxDurationMs).toBe(45 * 60 * 1000);
      }
    });
  });
});

// ------------------------------------------------------------------
// PHASE_TO_AGENT mapping
// ------------------------------------------------------------------

describe("PHASE_TO_AGENT mapping", () => {
  it("maps research-related phases to researcher", () => {
    expect(PHASE_TO_AGENT["research"]).toBe("researcher");
    expect(PHASE_TO_AGENT["literature-review"]).toBe("researcher");
  });

  it("maps experiment-related phases to experimenter", () => {
    expect(PHASE_TO_AGENT["experimental"]).toBe("experimenter");
    expect(PHASE_TO_AGENT["empirical-evaluation"]).toBe("experimenter");
    expect(PHASE_TO_AGENT["analysis"]).toBe("experimenter");
  });

  it("maps theory phases to theorist", () => {
    expect(PHASE_TO_AGENT["theory"]).toBe("theorist");
    expect(PHASE_TO_AGENT["theory-completion-parallel-experiment-execution"]).toBe("theorist");
  });

  it("maps writing-related phases to writer", () => {
    expect(PHASE_TO_AGENT["drafting"]).toBe("writer");
    expect(PHASE_TO_AGENT["writing"]).toBe("writer");
    expect(PHASE_TO_AGENT["submission-prep"]).toBe("writer");
    expect(PHASE_TO_AGENT["revision"]).toBe("writer");
    expect(PHASE_TO_AGENT["paper-finalization"]).toBe("writer");
  });

  it("maps final phase to editor", () => {
    expect(PHASE_TO_AGENT["final"]).toBe("editor");
  });

  it("maps review phase to critic", () => {
    expect(PHASE_TO_AGENT["review"]).toBe("critic");
  });

  it("maps active phase to engineer", () => {
    expect(PHASE_TO_AGENT["active"]).toBe("engineer");
  });

  it("has no duplicate phase keys", () => {
    const keys = Object.keys(PHASE_TO_AGENT);
    const unique = new Set(keys);
    expect(unique.size).toBe(keys.length);
  });

  it("all agent types in the mapping are valid AgentType values", () => {
    const validAgents: AgentType[] = [
      "researcher", "writer", "reviewer", "editor",
      "critic", "experimenter", "theorist", "strategist", "scout",
      "engineer",
    ];
    for (const agent of Object.values(PHASE_TO_AGENT)) {
      expect(validAgents).toContain(agent);
    }
  });
});
