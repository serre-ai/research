import { describe, it, expect } from "vitest";
import {
  getModelPricing,
  calculateCost,
  PRICING_TABLE,
} from "../../pricing.js";

describe("getModelPricing", () => {
  it("returns exact match for known models", () => {
    const haiku = getModelPricing("claude-haiku-4-5-20251001");
    expect(haiku.inputPer1MTokens).toBe(0.80);
    expect(haiku.outputPer1MTokens).toBe(4);

    const gpt4o = getModelPricing("gpt-4o");
    expect(gpt4o.inputPer1MTokens).toBe(2.50);
    expect(gpt4o.outputPer1MTokens).toBe(10);
  });

  it("returns prefix match for versioned model names", () => {
    // "claude-sonnet-4-6-20250514" should match "claude-sonnet-4-6"
    const pricing = getModelPricing("claude-sonnet-4-6-20250514");
    expect(pricing.inputPer1MTokens).toBe(3);
    expect(pricing.outputPer1MTokens).toBe(15);
  });

  it("returns default pricing for unknown models", () => {
    const pricing = getModelPricing("totally-unknown-model");
    expect(pricing.inputPer1MTokens).toBe(3);   // default = Sonnet-class
    expect(pricing.outputPer1MTokens).toBe(15);
  });

  it("has pricing for all major providers", () => {
    // Anthropic
    expect(PRICING_TABLE["claude-opus-4-6"]).toBeDefined();
    expect(PRICING_TABLE["claude-sonnet-4-6"]).toBeDefined();
    expect(PRICING_TABLE["claude-haiku-4-5-20251001"]).toBeDefined();

    // OpenAI
    expect(PRICING_TABLE["gpt-4o"]).toBeDefined();
    expect(PRICING_TABLE["gpt-4o-mini"]).toBeDefined();
    expect(PRICING_TABLE["o3"]).toBeDefined();

    // OpenRouter
    expect(PRICING_TABLE["deepseek/deepseek-r1"]).toBeDefined();
  });
});

describe("calculateCost", () => {
  it("returns 0 for zero tokens", () => {
    expect(calculateCost("gpt-4o", 0, 0)).toBe(0);
  });

  it("calculates correctly for known model", () => {
    // gpt-4o-mini: $0.15/1M input, $0.60/1M output
    const cost = calculateCost("gpt-4o-mini", 1_000_000, 1_000_000);
    expect(cost).toBeCloseTo(0.15 + 0.60, 6);
  });

  it("calculates correctly for small token counts", () => {
    // haiku: $0.80/1M input, $4/1M output
    // 500 input + 200 output
    const cost = calculateCost("claude-haiku-4-5-20251001", 500, 200);
    const expected = (500 / 1_000_000) * 0.80 + (200 / 1_000_000) * 4;
    expect(cost).toBeCloseTo(expected, 10);
  });

  it("uses default pricing for unknown models", () => {
    // default: $3/1M input, $15/1M output
    const cost = calculateCost("unknown-model", 1_000_000, 1_000_000);
    expect(cost).toBeCloseTo(3 + 15, 6);
  });

  it("handles large token counts without overflow", () => {
    // 1 billion tokens
    const cost = calculateCost("gpt-4o-mini", 1_000_000_000, 1_000_000_000);
    expect(cost).toBeGreaterThan(0);
    expect(Number.isFinite(cost)).toBe(true);
  });
});
