/**
 * EventBus — domain event system backed by PostgreSQL LISTEN/NOTIFY.
 *
 * Events are persisted in `domain_events` (audit trail) and broadcast
 * in real-time via pg_notify. Handlers are registered per event type
 * with automatic retry and dead-letter handling.
 */

import pg from "pg";

// ============================================================
// Types
// ============================================================

export interface DomainEvent {
  id: number;
  type: string;
  payload: Record<string, unknown>;
  createdAt?: string;
}

export interface EventHandler {
  name: string;
  fn: (event: DomainEvent) => Promise<void>;
}

export type BroadcastFn = (channel: string, data: unknown) => void;

// ============================================================
// EventBus
// ============================================================

const MAX_HANDLER_ATTEMPTS = 3;
const RECONNECT_BASE_MS = 5_000;
const RECONNECT_MAX_MS = 5 * 60_000;
const HEARTBEAT_INTERVAL_MS = 30_000;
const MAX_RECONNECT_ATTEMPTS = 10;
const MAX_DEAD_LETTER_RETRIES = 5;
const MAX_CONCURRENT_EVENTS = 100;

export class EventBus {
  private pool: pg.Pool;
  private listenClient: pg.PoolClient | null = null;
  private handlers = new Map<string, EventHandler[]>();
  private wildcardHandlers: EventHandler[] = [];
  private running = false;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private broadcastFn: BroadcastFn | null = null;
  private reconnectAttempts = 0;
  private reconnecting = false;
  private activeDispatches = 0;

  constructor(pool: pg.Pool) {
    this.pool = pool;
  }

  /** Set a broadcast function for WebSocket forwarding. */
  setBroadcast(fn: BroadcastFn): void {
    this.broadcastFn = fn;
  }

  /** Register a handler for a specific event type. */
  on(type: string, name: string, fn: EventHandler["fn"]): void {
    const list = this.handlers.get(type) ?? [];
    list.push({ name, fn });
    this.handlers.set(type, list);
  }

  /** Register a handler that receives all events. */
  onAny(name: string, fn: EventHandler["fn"]): void {
    this.wildcardHandlers.push({ name, fn });
  }

  /** Emit a domain event. Inserts into DB, triggers pg_notify automatically. */
  async emit(type: string, payload: Record<string, unknown>): Promise<number> {
    const { rows } = await this.pool.query(
      "INSERT INTO domain_events (type, payload) VALUES ($1, $2) RETURNING id",
      [type, JSON.stringify(payload)],
    );
    return rows[0].id as number;
  }

  /** Start listening for events via pg_notify. */
  async start(): Promise<void> {
    if (this.running) return;
    this.running = true;
    await this.connect();

    // Heartbeat to detect dropped connections
    this.heartbeatTimer = setInterval(() => {
      if (this.listenClient && !this.reconnecting) {
        this.listenClient.query("SELECT 1").catch(() => {
          console.error("[EventBus] Heartbeat failed, reconnecting...");
          this.reconnect();
        });
      }
    }, HEARTBEAT_INTERVAL_MS);

    // Process any unprocessed events from before startup
    await this.replayUnprocessed();
  }

  /** Stop listening and clean up. */
  async stop(): Promise<void> {
    this.running = false;
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    if (this.listenClient) {
      try {
        await this.listenClient.query("UNLISTEN forge_events");
      } catch { /* shutting down */ }
      this.listenClient.release();
      this.listenClient = null;
    }
  }

  /** Get recent events for the API. */
  async getRecent(opts?: {
    limit?: number;
    type?: string;
    since?: string;
  }): Promise<DomainEvent[]> {
    const limit = opts?.limit ?? 50;
    let sql = "SELECT id, type, payload, created_at FROM domain_events";
    const params: unknown[] = [];
    const conditions: string[] = [];
    let idx = 1;

    if (opts?.type) {
      conditions.push(`type = $${idx}`);
      params.push(opts.type);
      idx++;
    }
    if (opts?.since) {
      conditions.push(`created_at > $${idx}`);
      params.push(opts.since);
      idx++;
    }

    if (conditions.length > 0) {
      sql += " WHERE " + conditions.join(" AND ");
    }
    sql += ` ORDER BY id DESC LIMIT $${idx}`;
    params.push(limit);

    const { rows } = await this.pool.query(sql, params);
    return rows.map((r: Record<string, unknown>) => ({
      id: r.id as number,
      type: r.type as string,
      payload: r.payload as Record<string, unknown>,
      createdAt: (r.created_at as Date).toISOString(),
    }));
  }

  /** Get dead-letter entries. */
  async getDeadLetters(resolved = false): Promise<Array<{
    id: number;
    eventId: number;
    handlerName: string;
    error: string;
    attempts: number;
    lastAttemptAt: string;
  }>> {
    const { rows } = await this.pool.query(
      `SELECT id, event_id, handler_name, error, attempts, last_attempt_at
       FROM domain_events_dead_letter
       WHERE resolved = $1
       ORDER BY last_attempt_at DESC
       LIMIT 100`,
      [resolved],
    );
    return rows.map((r: Record<string, unknown>) => ({
      id: r.id as number,
      eventId: r.event_id as number,
      handlerName: r.handler_name as string,
      error: r.error as string,
      attempts: r.attempts as number,
      lastAttemptAt: (r.last_attempt_at as Date).toISOString(),
    }));
  }

  /** Retry a dead-letter entry — only re-runs the specific failed handler. */
  async retryDeadLetter(deadLetterId: number): Promise<boolean> {
    const { rows } = await this.pool.query(
      `SELECT dl.handler_name, dl.event_id, dl.attempts, de.type, de.payload
       FROM domain_events_dead_letter dl
       JOIN domain_events de ON de.id = dl.event_id
       WHERE dl.id = $1 AND dl.resolved = FALSE`,
      [deadLetterId],
    );
    if (rows.length === 0) return false;

    const attempts = rows[0].attempts as number;
    if (attempts >= MAX_DEAD_LETTER_RETRIES) {
      console.warn(`[EventBus] Dead letter ${deadLetterId} (event ${rows[0].event_id}) exceeded max retries (${MAX_DEAD_LETTER_RETRIES}), skipping`);
      return false;
    }

    const handlerName = rows[0].handler_name as string;
    const event: DomainEvent = {
      id: rows[0].event_id as number,
      type: rows[0].type as string,
      payload: rows[0].payload as Record<string, unknown>,
    };

    // Find the specific handler that failed
    const typeHandlers = this.handlers.get(event.type) ?? [];
    const allHandlers = [...typeHandlers, ...this.wildcardHandlers];
    const handler = allHandlers.find((h) => h.name === handlerName);

    if (handler) {
      const ok = await this.runHandler(handler, event);
      if (!ok) return false;
    }

    await this.pool.query(
      "UPDATE domain_events_dead_letter SET resolved = TRUE WHERE id = $1",
      [deadLetterId],
    );

    // Check if all dead letters for this event are now resolved
    const { rows: remaining } = await this.pool.query(
      "SELECT COUNT(*) AS cnt FROM domain_events_dead_letter WHERE event_id = $1 AND resolved = FALSE",
      [event.id],
    );
    if (parseInt(remaining[0].cnt) === 0) {
      await this.pool.query(
        "UPDATE domain_events SET processed = TRUE WHERE id = $1",
        [event.id],
      ).catch((err) => {
        console.error(`[EventBus] Failed to mark event ${event.id} as processed after dead letter resolution:`, err);
      });
    }

    return true;
  }

  /** Retry all unresolved dead letters. Returns count of successfully retried. */
  async retryAllDeadLetters(): Promise<number> {
    const deadLetters = await this.getDeadLetters(false);
    let retried = 0;
    for (const dl of deadLetters) {
      try {
        const ok = await this.retryDeadLetter(dl.id);
        if (ok) retried++;
      } catch {
        // Individual retry failed — continue with others
      }
    }
    return retried;
  }

  // --------------------------------------------------------
  // Internal
  // --------------------------------------------------------

  private async connect(): Promise<void> {
    try {
      this.listenClient = await this.pool.connect();
      await this.listenClient.query("LISTEN forge_events");

      this.listenClient.on("notification", (msg) => {
        if (!msg.payload) return;
        try {
          const event = JSON.parse(msg.payload) as DomainEvent;
          this.dispatch(event).catch((err) => {
            console.error("[EventBus] Dispatch error:", err);
          });
        } catch (err) {
          console.error("[EventBus] Failed to parse notification:", err);
        }
      });

      this.listenClient.on("error", (err) => {
        console.error("[EventBus] Listen connection error:", err);
        this.reconnect();
      });

      this.reconnectAttempts = 0;
      console.log("[EventBus] Connected and listening for events");
    } catch (err) {
      console.error("[EventBus] Failed to connect:", err);
      if (this.running) this.reconnect();
    }
  }

  private reconnect(): void {
    if (!this.running || this.reconnecting) return;
    this.reconnecting = true;
    if (this.listenClient) {
      try { this.listenClient.release(); } catch { /* already released */ }
      this.listenClient = null;
    }
    if (this.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.error(`[EventBus] Max reconnect attempts (${MAX_RECONNECT_ATTEMPTS}) reached, giving up. Manual restart required.`);
      this.running = false;
      if (this.heartbeatTimer) {
        clearInterval(this.heartbeatTimer);
        this.heartbeatTimer = null;
      }
      this.reconnecting = false;
      return;
    }
    const delay = Math.min(RECONNECT_BASE_MS * Math.pow(2, this.reconnectAttempts), RECONNECT_MAX_MS);
    this.reconnectAttempts++;
    console.log(`[EventBus] Reconnecting in ${Math.round(delay / 1000)}s (attempt ${this.reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
    setTimeout(() => {
      this.reconnecting = false;
      if (this.running) this.connect();
    }, delay);
  }

  /** Replay events that weren't processed (e.g., missed during downtime). */
  private async replayUnprocessed(): Promise<void> {
    const { rows } = await this.pool.query(
      `SELECT id, type, payload FROM domain_events
       WHERE processed = FALSE
       ORDER BY id ASC
       LIMIT 100`,
    );
    if (rows.length > 0) {
      console.log(`[EventBus] Replaying ${rows.length} unprocessed events`);
      for (const row of rows) {
        await this.dispatch({
          id: row.id as number,
          type: row.type as string,
          payload: row.payload as Record<string, unknown>,
        });
      }
    }
  }

  private async dispatch(event: DomainEvent): Promise<void> {
    if (this.activeDispatches >= MAX_CONCURRENT_EVENTS) {
      console.warn(`[EventBus] Concurrency limit (${MAX_CONCURRENT_EVENTS}) reached, skipping event ${event.id} (${event.type})`);
      return;
    }
    this.activeDispatches++;
    try {
      await this.dispatchInner(event);
    } finally {
      this.activeDispatches--;
    }
  }

  private async dispatchInner(event: DomainEvent): Promise<void> {
    const typeHandlers = this.handlers.get(event.type) ?? [];
    const allHandlers = [...typeHandlers, ...this.wildcardHandlers];

    let allSucceeded = true;
    for (const handler of allHandlers) {
      const ok = await this.runHandler(handler, event);
      if (!ok) allSucceeded = false;
    }

    // Only mark processed if ALL handlers succeeded
    if (allSucceeded) {
      await this.pool.query(
        "UPDATE domain_events SET processed = TRUE WHERE id = $1",
        [event.id],
      ).catch((err) => {
        console.error(`[EventBus] Failed to mark event ${event.id} as processed:`, err);
      });
    }

    // Broadcast to WebSocket clients
    if (this.broadcastFn) {
      this.broadcastFn("logs", { id: event.id, type: event.type, payload: event.payload });
    }
  }

  /** Returns true if handler succeeded, false if it exhausted retries. */
  private async runHandler(handler: EventHandler, event: DomainEvent): Promise<boolean> {
    let attempts = 0;
    while (attempts < MAX_HANDLER_ATTEMPTS) {
      try {
        await handler.fn(event);
        return true;
      } catch (err) {
        attempts++;
        if (attempts >= MAX_HANDLER_ATTEMPTS) {
          console.error(`[EventBus] Handler "${handler.name}" failed after ${attempts} attempts for event ${event.id}:`, err);
          await this.writeDeadLetter(event.id, handler.name, err, attempts);
          return false;
        } else {
          // Brief backoff before retry
          await new Promise((r) => setTimeout(r, 500 * attempts));
        }
      }
    }
    return false;
  }

  private async writeDeadLetter(
    eventId: number,
    handlerName: string,
    err: unknown,
    attempts: number,
  ): Promise<void> {
    try {
      await this.pool.query(
        `INSERT INTO domain_events_dead_letter (event_id, handler_name, error, attempts)
         VALUES ($1, $2, $3, $4)`,
        [eventId, handlerName, err instanceof Error ? err.message : String(err), attempts],
      );
    } catch (dlErr) {
      console.error("[EventBus] Failed to write dead letter:", dlErr);
    }
  }
}
