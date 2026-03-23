/**
 * Mock PostgreSQL pool for unit tests.
 *
 * Records all queries and returns configurable results.
 * Supports pool.query(), pool.connect() → client, and pool.on().
 */

import type pg from "pg";

interface QueryCall {
  text: string;
  params: unknown[];
}

interface MockQueryResult {
  rows: unknown[];
  rowCount: number;
}

export function createMockPool() {
  const queryResults = new Map<string, MockQueryResult>();
  const queryCalls: QueryCall[] = [];

  const mockQuery = async (text: string, params?: unknown[]): Promise<MockQueryResult> => {
    queryCalls.push({ text, params: params ?? [] });
    // Match by substring for flexibility
    for (const [pattern, result] of queryResults) {
      if (text.includes(pattern)) return result;
    }
    return { rows: [], rowCount: 0 };
  };

  const eventListeners = new Map<string, Function[]>();
  let outstandingClients = 0;

  function createMockClient() {
    outstandingClients++;
    return {
      query: mockQuery,
      release: () => { outstandingClients--; },
    };
  }

  const pool = {
    query: mockQuery,
    connect: async () => createMockClient(),
    end: async () => {},
    on: (event: string, listener: Function) => {
      const listeners = eventListeners.get(event) ?? [];
      listeners.push(listener);
      eventListeners.set(event, listeners);
      return pool;
    },

    // ── Test helpers (not on real Pool) ──
    /** Set the result for queries matching a pattern */
    mockQueryResult(pattern: string, rows: unknown[]) {
      queryResults.set(pattern, { rows, rowCount: rows.length });
    },
    /** Get all recorded query calls */
    getQueryCalls(): QueryCall[] {
      return queryCalls;
    },
    /** Get registered event listeners */
    getListeners(event: string): Function[] {
      return eventListeners.get(event) ?? [];
    },
    /** Get count of clients checked out but not released */
    getOutstandingClients(): number {
      return outstandingClients;
    },
    /** Reset all mocks */
    reset() {
      queryCalls.length = 0;
      queryResults.clear();
      eventListeners.clear();
      outstandingClients = 0;
    },
  };

  return pool as typeof pool & pg.Pool;
}
