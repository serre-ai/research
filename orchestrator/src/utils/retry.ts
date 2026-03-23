/**
 * Retry configuration for API calls and external operations.
 */
export interface RetryOptions {
  /** Maximum number of retry attempts */
  maxAttempts: number;
  /** Initial delay in milliseconds */
  initialDelayMs: number;
  /** Maximum delay in milliseconds */
  maxDelayMs: number;
  /** Backoff multiplier (exponential backoff) */
  backoffMultiplier: number;
  /** HTTP status codes that should trigger a retry */
  retryableStatusCodes?: number[];
  /** Error types that should trigger a retry */
  retryableErrors?: string[];
}

export const DEFAULT_RETRY_OPTIONS: RetryOptions = {
  maxAttempts: 3,
  initialDelayMs: 1000,
  maxDelayMs: 30000,
  backoffMultiplier: 2,
  retryableStatusCodes: [408, 429, 500, 502, 503, 504],
  retryableErrors: ["ECONNRESET", "ETIMEDOUT", "ENOTFOUND", "EAI_AGAIN"],
};

interface RetryContext {
  attempt: number;
  lastError?: Error;
  delayMs: number;
}

/**
 * Determine if an error is retryable based on configuration.
 */
export function isRetryable(error: unknown, options: RetryOptions): boolean {
  if (!error) return false;

  // HTTP status code check
  if (typeof error === "object" && error !== null) {
    const statusCode = (error as { status?: number; statusCode?: number }).status
      ?? (error as { status?: number; statusCode?: number }).statusCode;
    if (statusCode && options.retryableStatusCodes?.includes(statusCode)) {
      return true;
    }

    // Error code check (e.g., ECONNRESET)
    const code = (error as { code?: string }).code;
    if (code && options.retryableErrors?.includes(code)) {
      return true;
    }

    // Check error message for rate limit indicators
    const message = error instanceof Error ? error.message.toLowerCase() : "";
    if (message.includes("rate limit") || message.includes("too many requests")) {
      return true;
    }
  }

  return false;
}

/**
 * Calculate delay for next retry attempt using exponential backoff.
 */
export function calculateDelay(ctx: RetryContext, options: RetryOptions): number {
  const delay = options.initialDelayMs * Math.pow(options.backoffMultiplier, ctx.attempt - 1);
  return Math.min(delay, options.maxDelayMs);
}

/**
 * Sleep for specified milliseconds.
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry an async operation with exponential backoff.
 *
 * @example
 * const result = await retry(
 *   async () => await fetchDataFromApi(),
 *   { maxAttempts: 3, initialDelayMs: 1000 }
 * );
 */
export async function retry<T>(
  operation: () => Promise<T>,
  options: Partial<RetryOptions> = {},
): Promise<T> {
  const config = { ...DEFAULT_RETRY_OPTIONS, ...options };
  const ctx: RetryContext = { attempt: 0, delayMs: config.initialDelayMs };

  while (true) {
    ctx.attempt++;

    try {
      return await operation();
    } catch (error) {
      ctx.lastError = error instanceof Error ? error : new Error(String(error));

      // Check if we should retry
      const shouldRetry = ctx.attempt < config.maxAttempts && isRetryable(error, config);

      if (!shouldRetry) {
        throw ctx.lastError;
      }

      // Calculate and apply backoff delay
      ctx.delayMs = calculateDelay(ctx, config);
      console.warn(
        `[Retry] Attempt ${ctx.attempt}/${config.maxAttempts} failed: ${ctx.lastError.message}. ` +
        `Retrying in ${ctx.delayMs}ms...`
      );
      await sleep(ctx.delayMs);
    }
  }
}

/**
 * Retry with jitter to avoid thundering herd problem.
 * Adds random variation to delay (±20%).
 */
export async function retryWithJitter<T>(
  operation: () => Promise<T>,
  options: Partial<RetryOptions> = {},
): Promise<T> {
  return retry(async () => {
    try {
      return await operation();
    } catch (error) {
      // Add jitter before rethrowing to trigger retry
      const jitter = 0.8 + Math.random() * 0.4; // 0.8 to 1.2
      await sleep(options.initialDelayMs ? options.initialDelayMs * jitter * 0.1 : 100);
      throw error;
    }
  }, options);
}
