/**
 * Consolidated model pricing table.
 * Single source of truth for all token cost calculations.
 * Ported from projects/reasoning-gaps/benchmarks/cost_estimator.py
 */

export interface ModelPricing {
  inputPer1MTokens: number;
  outputPer1MTokens: number;
}

export const PRICING_TABLE: Record<string, ModelPricing> = {
  // Anthropic
  "claude-opus-4-6":              { inputPer1MTokens: 15,    outputPer1MTokens: 75 },
  "claude-sonnet-4-6":            { inputPer1MTokens: 3,     outputPer1MTokens: 15 },
  "claude-haiku-4-5-20251001":    { inputPer1MTokens: 0.80,  outputPer1MTokens: 4 },
  // Legacy names
  "claude-3-5-sonnet-20241022":   { inputPer1MTokens: 3,     outputPer1MTokens: 15 },
  "claude-3-5-haiku-20241022":    { inputPer1MTokens: 0.80,  outputPer1MTokens: 4 },
  "claude-3-opus-20240229":       { inputPer1MTokens: 15,    outputPer1MTokens: 75 },

  // OpenAI
  "gpt-4o":                       { inputPer1MTokens: 2.50,  outputPer1MTokens: 10 },
  "gpt-4o-mini":                  { inputPer1MTokens: 0.15,  outputPer1MTokens: 0.60 },
  "o1":                           { inputPer1MTokens: 15,    outputPer1MTokens: 60 },
  "o1-mini":                      { inputPer1MTokens: 3,     outputPer1MTokens: 12 },
  "o3":                           { inputPer1MTokens: 10,    outputPer1MTokens: 40 },
  "o3-mini":                      { inputPer1MTokens: 1.10,  outputPer1MTokens: 4.40 },

  // OpenRouter-hosted
  "deepseek/deepseek-r1":         { inputPer1MTokens: 0.55,  outputPer1MTokens: 2.19 },
  "google/gemini-2.0-flash-001":  { inputPer1MTokens: 0.10,  outputPer1MTokens: 0.40 },
  "google/gemini-2.5-pro-preview-03-25": { inputPer1MTokens: 1.25, outputPer1MTokens: 10 },
};

/** Default pricing when model is unknown — assumes Sonnet-class pricing */
const DEFAULT_PRICING: ModelPricing = { inputPer1MTokens: 3, outputPer1MTokens: 15 };

/**
 * Look up pricing for a model. Tries exact match first, then prefix match.
 */
export function getModelPricing(model: string): ModelPricing {
  if (PRICING_TABLE[model]) return PRICING_TABLE[model];

  // Prefix match: "claude-sonnet-4-6-20250514" -> "claude-sonnet-4-6"
  for (const key of Object.keys(PRICING_TABLE)) {
    if (model.startsWith(key)) return PRICING_TABLE[key];
  }

  return DEFAULT_PRICING;
}

/**
 * Calculate cost in USD for a given model and token counts.
 */
export function calculateCost(
  model: string,
  inputTokens: number,
  outputTokens: number,
): number {
  const pricing = getModelPricing(model);
  return (
    (inputTokens / 1_000_000) * pricing.inputPer1MTokens +
    (outputTokens / 1_000_000) * pricing.outputPer1MTokens
  );
}
