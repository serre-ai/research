/**
 * Embedding functions for the knowledge graph.
 * Supports Voyage AI (preferred) and OpenAI (fallback).
 */

import { retry } from "./utils/retry.js";

export type EmbedFn = (text: string) => Promise<number[]>;

/**
 * Create an embedding function using the best available provider.
 * Tries Voyage first (1024-dim), then OpenAI (1024-dim, truncated).
 * Returns null if no API key is available.
 */
export function createEmbedFn(): EmbedFn | null {
  if (process.env.VOYAGE_API_KEY) {
    return createVoyageEmbedFn(process.env.VOYAGE_API_KEY);
  }
  if (process.env.OPENAI_API_KEY) {
    return createOpenAIEmbedFn(process.env.OPENAI_API_KEY);
  }
  return null;
}

/**
 * Returns the embedding dimension for the current provider.
 */
export function getEmbeddingDimension(): number {
  return 1024; // Both providers now use 1024 dimensions
}

function createVoyageEmbedFn(apiKey: string): EmbedFn {
  return async (text: string): Promise<number[]> => {
    return retry(async () => {
      const res = await fetch("https://api.voyageai.com/v1/embeddings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "voyage-3-lite",
          input: [text],
          input_type: "document",
        }),
      });

      if (!res.ok) {
        const body = await res.text();
        const error: Error & { status?: number } = new Error(`Voyage embedding failed (${res.status}): ${body}`);
        error.status = res.status;
        throw error;
      }

      const json = await res.json() as { data: Array<{ embedding: number[] }> };
      return json.data[0].embedding;
    }, {
      maxAttempts: 3,
      initialDelayMs: 1000,
      maxDelayMs: 10000,
    });
  };
}

function createOpenAIEmbedFn(apiKey: string): EmbedFn {
  return async (text: string): Promise<number[]> => {
    return retry(async () => {
      const res = await fetch("https://api.openai.com/v1/embeddings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "text-embedding-3-small",
          input: text,
          dimensions: 1024, // Match Voyage/pgvector column size
        }),
      });

      if (!res.ok) {
        const body = await res.text();
        const error: Error & { status?: number } = new Error(`OpenAI embedding failed (${res.status}): ${body}`);
        error.status = res.status;
        throw error;
      }

      const json = await res.json() as { data: Array<{ embedding: number[] }> };
      return json.data[0].embedding;
    }, {
      maxAttempts: 3,
      initialDelayMs: 1000,
      maxDelayMs: 10000,
    });
  };
}

/**
 * Batch embed multiple texts. Useful for backfill.
 * Voyage supports batches of up to 128 inputs.
 */
export async function batchEmbed(
  texts: string[],
  embedFn: EmbedFn,
  batchSize: number = 32,
): Promise<number[][]> {
  const results: number[][] = [];
  for (let i = 0; i < texts.length; i += batchSize) {
    const batch = texts.slice(i, i + batchSize);
    const embeddings = await Promise.all(batch.map(embedFn));
    results.push(...embeddings);
    // Rate limit: small delay between batches
    if (i + batchSize < texts.length) {
      await new Promise((r) => setTimeout(r, 200));
    }
  }
  return results;
}
