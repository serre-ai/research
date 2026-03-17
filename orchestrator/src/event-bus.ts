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
const RECONNECT_DELAY_MS = 5_000;
const HEARTBEAT_INTERVAL_MS = 30_000;

export class EventBus {
  private pool: pg.Pool;
  private listenClient: pg.PoolClient | null = null;
  private handlers = new Map<string, EventHandler[]>();
  private wildcardHandlers: EventHandler[] = [];
  private running = false;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private broadcastFn: BroadcastFn | null = null;

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
      if (this.listenClient) {
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
        await this.listenClient.query("UNLISTEN deepwork_events");
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

  /** Retry a dead-letter entry. */
  async retryDeadLetter(deadLetterId: number): Promise<boolean> {
    const { rows } = await this.pool.query(
      `SELECT dl.event_id, de.type, de.payload
       FROM domain_events_dead_letter dl
       JOIN domain_events de ON de.id = dl.event_id
       WHERE dl.id = $1 AND dl.resolved = FALSE`,
      [deadLetterId],
    );
    if (rows.length === 0) return false;

    const event: DomainEvent = {
      id: rows[0].event_id as number,
      type: rows[0].type as string,
      payload: rows[0].payload as Record<string, unknown>,
    };

    await this.dispatch(event);
    await this.pool.query(
      "UPDATE domain_events_dead_letter SET resolved = TRUE WHERE id = $1",
      [deadLetterId],
    );
    return true;
  }

  // --------------------------------------------------------
  // Internal
  // --------------------------------------------------------

  private async connect(): Promise<void> {
    try {
      this.listenClient = await this.pool.connect();
      await this.listenClient.query("LISTEN deepwork_events");

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

      console.log("[EventBus] Connected and listening for events");
    } catch (err) {
      console.error("[EventBus] Failed to connect:", err);
      if (this.running) this.reconnect();
    }
  }

  private reconnect(): void {
    if (!this.running) return;
    if (this.listenClient) {
      try { this.listenClient.release(); } catch { /* already released */ }
      this.listenClient = null;
    }
    setTimeout(() => {
      if (this.running) this.connect();
    }, RECONNECT_DELAY_MS);
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
    const typeHandlers = this.handlers.get(event.type) ?? [];
    const allHandlers = [...typeHandlers, ...this.wildcardHandlers];

    for (const handler of allHandlers) {
      await this.runHandler(handler, event);
    }

    // Mark as processed
    await this.pool.query(
      "UPDATE domain_events SET processed = TRUE WHERE id = $1",
      [event.id],
    ).catch(() => { /* best effort */ });

    // Broadcast to WebSocket clients
    if (this.broadcastFn) {
      this.broadcastFn("events", { id: event.id, type: event.type, payload: event.payload });
    }
  }

  private async runHandler(handler: EventHandler, event: DomainEvent): Promise<void> {
    let attempts = 0;
    while (attempts < MAX_HANDLER_ATTEMPTS) {
      try {
        await handler.fn(event);
        return;
      } catch (err) {
        attempts++;
        if (attempts >= MAX_HANDLER_ATTEMPTS) {
          console.error(`[EventBus] Handler "${handler.name}" failed after ${attempts} attempts for event ${event.id}:`, err);
          await this.writeDeadLetter(event.id, handler.name, err, attempts);
        } else {
          // Brief backoff before retry
          await new Promise((r) => setTimeout(r, 500 * attempts));
        }
      }
    }
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
