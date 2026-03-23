import { describe, it, expect } from "vitest";
import {
  isValidProjectName,
  isValidId,
  isValidTaskName,
  assertContained,
} from "../../path-validation.js";

describe("isValidProjectName", () => {
  it("accepts valid project names", () => {
    expect(isValidProjectName("reasoning-gaps")).toBe(true);
    expect(isValidProjectName("self-improvement-limits")).toBe(true);
    expect(isValidProjectName("verification-complexity")).toBe(true);
    expect(isValidProjectName("agent-failure-taxonomy")).toBe(true);
    expect(isValidProjectName("a")).toBe(true);
    expect(isValidProjectName("project.v2")).toBe(true);
    expect(isValidProjectName("test_project")).toBe(true);
  });

  it("rejects path traversal", () => {
    expect(isValidProjectName("../../../etc")).toBe(false);
    expect(isValidProjectName("..")).toBe(false);
    expect(isValidProjectName("foo/../bar")).toBe(false);
  });

  it("rejects empty and whitespace", () => {
    expect(isValidProjectName("")).toBe(false);
    expect(isValidProjectName(" ")).toBe(false);
  });

  it("rejects uppercase", () => {
    expect(isValidProjectName("MyProject")).toBe(false);
    expect(isValidProjectName("ALLCAPS")).toBe(false);
  });

  it("rejects names starting with special chars", () => {
    expect(isValidProjectName("-leading-dash")).toBe(false);
    expect(isValidProjectName(".leading-dot")).toBe(false);
    expect(isValidProjectName("_leading-underscore")).toBe(false);
  });

  it("rejects names exceeding 64 characters", () => {
    expect(isValidProjectName("a".repeat(65))).toBe(false);
    expect(isValidProjectName("a".repeat(64))).toBe(true);
  });

  it("rejects slashes and backslashes", () => {
    expect(isValidProjectName("foo/bar")).toBe(false);
    expect(isValidProjectName("foo\\bar")).toBe(false);
  });

  it("rejects null bytes", () => {
    expect(isValidProjectName("project\x00/../etc")).toBe(false);
    expect(isValidProjectName("foo\x00")).toBe(false);
  });
});

describe("isValidId", () => {
  it("accepts valid IDs", () => {
    expect(isValidId("abc-123-def")).toBe(true);
    expect(isValidId("a1b2c3")).toBe(true);
    expect(isValidId("session_001")).toBe(true);
    expect(isValidId("550e8400-e29b-41d4-a716-446655440000")).toBe(true);
  });

  it("rejects path traversal", () => {
    expect(isValidId("../etc/passwd")).toBe(false);
    expect(isValidId("..")).toBe(false);
  });

  it("rejects empty", () => {
    expect(isValidId("")).toBe(false);
  });

  it("rejects IDs starting with special chars", () => {
    expect(isValidId("-leading")).toBe(false);
    expect(isValidId("_leading")).toBe(false);
  });

  it("rejects IDs exceeding 128 characters", () => {
    expect(isValidId("a".repeat(129))).toBe(false);
    expect(isValidId("a".repeat(128))).toBe(true);
  });
});

describe("isValidTaskName", () => {
  it("accepts valid task/condition/model names", () => {
    expect(isValidTaskName("B1_addition")).toBe(true);
    expect(isValidTaskName("direct")).toBe(true);
    expect(isValidTaskName("budget_cot")).toBe(true);
    expect(isValidTaskName("short_cot")).toBe(true);
    expect(isValidTaskName("claude-haiku-4-5-20251001")).toBe(true);
  });

  it("accepts colons for provider:model format", () => {
    expect(isValidTaskName("anthropic:claude-haiku-4-5-20251001")).toBe(true);
    expect(isValidTaskName("openai:o3")).toBe(true);
    expect(isValidTaskName("openrouter:meta-llama:llama-3.1-8b-instruct")).toBe(true);
  });

  it("rejects path traversal despite colons", () => {
    expect(isValidTaskName("../../etc")).toBe(false);
    expect(isValidTaskName("model/../../etc")).toBe(false);
    expect(isValidTaskName("..")).toBe(false);
  });

  it("rejects slashes and backslashes", () => {
    expect(isValidTaskName("has/slash")).toBe(false);
    expect(isValidTaskName("has\\backslash")).toBe(false);
  });

  it("rejects empty", () => {
    expect(isValidTaskName("")).toBe(false);
  });

  it("rejects .. embedded in colon-separated parts", () => {
    expect(isValidTaskName("model:..")).toBe(false);
    expect(isValidTaskName("provider:..:model")).toBe(false);
    expect(isValidTaskName("..:..:..")).toBe(false);
  });

  it("rejects null bytes", () => {
    expect(isValidTaskName("task\x00")).toBe(false);
  });
});

describe("assertContained", () => {
  const root = "/opt/deepwork/projects";

  it("passes for paths within root", () => {
    expect(() => assertContained(`${root}/reasoning-gaps/status.yaml`, root)).not.toThrow();
    expect(() => assertContained(`${root}/foo/bar/baz.txt`, root)).not.toThrow();
  });

  it("passes when path equals root", () => {
    expect(() => assertContained(root, root)).not.toThrow();
  });

  it("throws for paths escaping root via traversal", () => {
    expect(() => assertContained(`${root}/../../../etc/passwd`, root)).toThrow("Path traversal detected");
    expect(() => assertContained(`${root}/../secret`, root)).toThrow("Path traversal detected");
  });

  it("throws for completely unrelated paths", () => {
    expect(() => assertContained("/etc/passwd", root)).toThrow("Path traversal detected");
    expect(() => assertContained("/tmp/evil", root)).toThrow("Path traversal detected");
  });

  it("throws for paths that share a prefix but escape", () => {
    // /opt/deepwork/projects-evil is NOT inside /opt/deepwork/projects
    expect(() => assertContained("/opt/deepwork/projects-evil/file", root)).toThrow("Path traversal detected");
  });
});
