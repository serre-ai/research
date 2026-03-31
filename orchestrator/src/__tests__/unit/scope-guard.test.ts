import { describe, it, expect } from "vitest";
import { GitEngine } from "../../git-engine.js";

/**
 * Tests for GitEngine.scopeCheck() — a pure function that validates
 * file changes against allowed project scope.
 *
 * No git operations or filesystem access needed.
 */

describe("scopeCheck", () => {
  const engine = new GitEngine("/fake/dir");

  // ------------------------------------------------------------------
  // Project sessions — only projects/<name>/ files allowed
  // ------------------------------------------------------------------
  describe("project sessions", () => {
    it("accepts files within the project directory", () => {
      const files = [
        "projects/reasoning-gaps/paper.tex",
        "projects/reasoning-gaps/status.yaml",
        "projects/reasoning-gaps/data/results.json",
      ];
      const violations = engine.scopeCheck(files, "reasoning-gaps");
      expect(violations).toEqual([]);
    });

    it("rejects files outside the project directory", () => {
      const files = [
        "projects/reasoning-gaps/paper.tex",
        "orchestrator/src/index.ts",
        "scripts/deploy.sh",
      ];
      const violations = engine.scopeCheck(files, "reasoning-gaps");
      expect(violations).toEqual([
        "orchestrator/src/index.ts",
        "scripts/deploy.sh",
      ]);
    });

    it("rejects files in other project directories", () => {
      const files = [
        "projects/reasoning-gaps/paper.tex",
        "projects/verification-complexity/paper.tex",
      ];
      const violations = engine.scopeCheck(files, "reasoning-gaps");
      expect(violations).toEqual([
        "projects/verification-complexity/paper.tex",
      ]);
    });

    it("rejects root-level files for project sessions", () => {
      const files = [
        "projects/reasoning-gaps/status.yaml",
        "CLAUDE.md",
        "config.yaml",
      ];
      const violations = engine.scopeCheck(files, "reasoning-gaps");
      expect(violations).toEqual(["CLAUDE.md", "config.yaml"]);
    });

    it("rejects platform directories for project sessions", () => {
      const files = [
        "orchestrator/src/daemon.ts",
        "docs/architecture.md",
        ".claude/agents/researcher.md",
        "shared/templates/paper.tex",
      ];
      const violations = engine.scopeCheck(files, "reasoning-gaps");
      expect(violations).toEqual(files);
    });
  });

  // ------------------------------------------------------------------
  // Platform sessions — orchestrator/, scripts/, docs/, .claude/, shared/ allowed
  // ------------------------------------------------------------------
  describe("platform sessions (_platform)", () => {
    it("accepts orchestrator files", () => {
      const files = [
        "orchestrator/src/index.ts",
        "orchestrator/src/daemon.ts",
        "orchestrator/package.json",
      ];
      const violations = engine.scopeCheck(files, "_platform");
      expect(violations).toEqual([]);
    });

    it("accepts scripts, docs, .claude, and shared files", () => {
      const files = [
        "scripts/deploy.sh",
        "docs/architecture.md",
        ".claude/agents/researcher.md",
        "shared/templates/paper.tex",
      ];
      const violations = engine.scopeCheck(files, "_platform");
      expect(violations).toEqual([]);
    });

    it("accepts root-level config files", () => {
      const files = [
        "CLAUDE.md",
        "config.yaml",
        "budget.yaml",
        "ideas/new-idea.md",
      ];
      const violations = engine.scopeCheck(files, "_platform");
      expect(violations).toEqual([]);
    });

    it("rejects project files for platform sessions", () => {
      const files = [
        "orchestrator/src/index.ts",
        "projects/reasoning-gaps/paper.tex",
        "projects/verification-complexity/status.yaml",
      ];
      const violations = engine.scopeCheck(files, "_platform");
      expect(violations).toEqual([
        "projects/reasoning-gaps/paper.tex",
        "projects/verification-complexity/status.yaml",
      ]);
    });

    it("rejects unknown root-level directories", () => {
      const files = [
        "cli/src/index.ts",
        "site-next/src/page.tsx",
        "random-dir/file.txt",
      ];
      const violations = engine.scopeCheck(files, "_platform");
      expect(violations).toEqual(files);
    });
  });

  // ------------------------------------------------------------------
  // Edge cases
  // ------------------------------------------------------------------
  describe("edge cases", () => {
    it("returns empty array for empty file list", () => {
      expect(engine.scopeCheck([], "reasoning-gaps")).toEqual([]);
      expect(engine.scopeCheck([], "_platform")).toEqual([]);
    });

    it("handles unknown project name correctly", () => {
      const files = [
        "projects/nonexistent-project/file.txt",
      ];
      // For a session scoped to "nonexistent-project", files in that directory are valid
      const violations = engine.scopeCheck(files, "nonexistent-project");
      expect(violations).toEqual([]);
    });

    it("is strict about prefix matching — no partial directory names", () => {
      const files = [
        "projects/reasoning-gaps-extended/file.txt",
      ];
      // Session for "reasoning-gaps" should NOT allow "reasoning-gaps-extended/"
      const violations = engine.scopeCheck(files, "reasoning-gaps");
      expect(violations).toEqual([
        "projects/reasoning-gaps-extended/file.txt",
      ]);
    });

    it("treats files at projects/ root as out-of-scope for project sessions", () => {
      const files = ["projects/README.md"];
      const violations = engine.scopeCheck(files, "reasoning-gaps");
      expect(violations).toEqual(["projects/README.md"]);
    });

    it("handles deeply nested paths", () => {
      const deep = "projects/reasoning-gaps/experiments/exp01/data/raw/file.csv";
      const violations = engine.scopeCheck([deep], "reasoning-gaps");
      expect(violations).toEqual([]);
    });
  });
});
