/**
 * Embedding functions for the knowledge graph.
 * Supports Voyage AI (preferred) and OpenAI (fallback).
 */

export type EmbedFn = (text: string) => Promise<number[]>;

/**
 * Create an embedding function using the best available provider.
 * Tries Voyage first (1024-dim), then OpenAI (1536-dim).
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
  if (process.env.VOYAGE_API_KEY) return 1024;
  if (process.env.OPENAI_API_KEY) return 1536;
  return 1024; // default to Voyage dimensions
}

function createVoyageEmbedFn(apiKey: string): EmbedFn {
  return async (text: string): Promise<number[]> => {
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
      throw new Error(`Voyage embedding failed (${res.status}): ${body}`);
    }

    const json = await res.json() as { data: Array<{ embedding: number[] }> };
    return json.data[0].embedding;
  };
}

function createOpenAIEmbedFn(apiKey: string): EmbedFn {
  return async (text: string): Promise<number[]> => {
    const res = await fetch("https://api.openai.com/v1/embeddings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "text-embedding-3-small",
        input: text,
      }),
    });

    if (!res.ok) {
      const body = await res.text();
      throw new Error(`OpenAI embedding failed (${res.status}): ${body}`);
    }

    const json = await res.json() as { data: Array<{ embedding: number[] }> };
    return json.data[0].embedding;
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
