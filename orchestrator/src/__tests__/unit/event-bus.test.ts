import { describe, it, expect, vi, beforeEach } from "vitest";
import { EventBus, type DomainEvent, type EventHandler } from "../../event-bus.js";

// ------------------------------------------------------------------
// Mock pg Pool — provides a minimal Pool-like object.
// Each test can override query results via mockQuery.
// ------------------------------------------------------------------

let mockQuery: ReturnType<typeof vi.fn>;
let mockConnect: ReturnType<typeof vi.fn>;
let mockListenClient: {
  query: ReturnType<typeof vi.fn>;
  on: ReturnType<typeof vi.fn>;
  release: ReturnType<typeof vi.fn>;
};

function makePool() {
  mockQuery = vi.fn().mockResolvedValue({ rows: [] });
  mockListenClient = {
    query: vi.fn().mockResolvedValue({ rows: [] }),
    on: vi.fn(),
    release: vi.fn(),
  };
  mockConnect = vi.fn().mockResolvedValue(mockListenClient);

  return {
    query: mockQuery,
    connect: mockConnect,
  } as unknown as import("pg").Pool;
}

describe("EventBus", () => {
  let bus: EventBus;
  let pool: ReturnType<typeof makePool>;

  beforeEach(() => {
    vi.clearAllMocks();
    pool = makePool();
    bus = new EventBus(pool as unknown as import("pg").Pool);
  });

  // ------------------------------------------------------------------
  // Handler registration
  // ------------------------------------------------------------------
  describe("handler registration", () => {
    it("registers type-specific handlers via on()", () => {
      const handler = vi.fn();
      bus.on("session.completed", "test-handler", handler);

      // Verify the handler is stored (we can test it by emitting and dispatching)
      // Since emit only inserts into DB, we test indirectly through dispatch behavior
      expect(() => bus.on("session.completed", "another", vi.fn())).not.toThrow();
    });

    it("registers wildcard handlers via onAny()", () => {
      const handler = vi.fn();
      bus.onAny("audit-logger", handler);
      expect(() => bus.onAny("another", vi.fn())).not.toThrow();
    });
  });

  // ------------------------------------------------------------------
  // Event emission
  // ------------------------------------------------------------------
  describe("emit", () => {
    it("inserts event into database and returns id", async () => {
      mockQuery.mockResolvedValueOnce({ rows: [{ id: 42 }] });

      const id = await bus.emit("session.completed", { project: "test", score: 85 });
      expect(id).toBe(42);

      expect(mockQuery).toHaveBeenCalledWith(
        "INSERT INTO domain_events (type, payload) VALUES ($1, $2) RETURNING id",
        ["session.completed", JSON.stringify({ project: "test", score: 85 })],
      );
    });

    it("propagates database errors on emit", async () => {
      mockQuery.mockRejectedValueOnce(new Error("DB down"));
      await expect(bus.emit("test", {})).rejects.toThrow("DB down");
    });
  });

  // ------------------------------------------------------------------
  // Event serialization/deserialization
  // ------------------------------------------------------------------
  describe("event serialization", () => {
    it("serializes payload as JSON on emit", async () => {
      mockQuery.mockResolvedValueOnce({ rows: [{ id: 1 }] });

      const payload = {
        nested: { deep: true },
        array: [1, 2, 3],
        special: "quotes\"and\\backslashes",
      };
      await bus.emit("test.event", payload);

      const calledPayload = mockQuery.mock.calls[0][1]![1];
      expect(JSON.parse(calledPayload as string)).toEqual(payload);
    });

    it("handles empty payload", async () => {
      mockQuery.mockResolvedValueOnce({ rows: [{ id: 1 }] });
      await bus.emit("test.event", {});

      const calledPayload = mockQuery.mock.calls[0][1]![1];
      expect(JSON.parse(calledPayload as string)).toEqual({});
    });
  });

  // ------------------------------------------------------------------
  // Broadcast function
  // ------------------------------------------------------------------
  describe("broadcast", () => {
    it("sets and uses broadcast function", () => {
      const broadcastFn = vi.fn();
      bus.setBroadcast(broadcastFn);
      // Broadcast is called during dispatch, which we can test by triggering
      // a notification. Since dispatch is private, we verify setBroadcast doesn't throw.
      expect(() => bus.setBroadcast(vi.fn())).not.toThrow();
    });
  });

  // ------------------------------------------------------------------
  // Start/stop lifecycle
  // ------------------------------------------------------------------
  describe("lifecycle", () => {
    it("connects and listens on start", async () => {
      // Mock replayUnprocessed to return no events
      mockQuery.mockResolvedValue({ rows: [] });

      await bus.start();

      expect(mockConnect).toHaveBeenCalled();
      expect(mockListenClient.query).toHaveBeenCalledWith("LISTEN forge_events");
      expect(mockListenClient.on).toHaveBeenCalledWith("notification", expect.any(Function));
      expect(mockListenClient.on).toHaveBeenCalledWith("error", expect.any(Function));

      await bus.stop();
    });

    it("cleans up on stop", async () => {
      mockQuery.mockResolvedValue({ rows: [] });
      await bus.start();
      await bus.stop();

      expect(mockListenClient.query).toHaveBeenCalledWith("UNLISTEN forge_events");
      expect(mockListenClient.release).toHaveBeenCalled();
    });

    it("is idempotent on start — does not connect twice", async () => {
      mockQuery.mockResolvedValue({ rows: [] });
      await bus.start();
      await bus.start(); // second call should be no-op

      expect(mockConnect).toHaveBeenCalledTimes(1);

      await bus.stop();
    });
  });

  // ------------------------------------------------------------------
  // Notification-driven dispatch
  // ------------------------------------------------------------------
  describe("dispatch via notification", () => {
    it("routes events to type-specific handlers", async () => {
      const handler = vi.fn().mockResolvedValue(undefined);
      bus.on("session.completed", "test-handler", handler);

      // Mock replayUnprocessed + mark processed
      mockQuery.mockResolvedValue({ rows: [] });
      await bus.start();

      // Simulate pg_notify by capturing the notification callback
      const notificationCallback = mockListenClient.on.mock.calls.find(
        (call: unknown[]) => call[0] === "notification",
      )![1] as (msg: { payload?: string }) => void;

      const event: DomainEvent = { id: 1, type: "session.completed", payload: { project: "alpha" } };
      notificationCallback({ payload: JSON.stringify(event) });

      // Allow async dispatch to complete
      await vi.waitFor(() => expect(handler).toHaveBeenCalledTimes(1));
      expect(handler).toHaveBeenCalledWith(event);

      await bus.stop();
    });

    it("routes events to wildcard handlers", async () => {
      const wildcard = vi.fn().mockResolvedValue(undefined);
      bus.onAny("audit", wildcard);

      mockQuery.mockResolvedValue({ rows: [] });
      await bus.start();

      const notificationCallback = mockListenClient.on.mock.calls.find(
        (call: unknown[]) => call[0] === "notification",
      )![1] as (msg: { payload?: string }) => void;

      const event: DomainEvent = { id: 2, type: "budget.warning", payload: { level: "critical" } };
      notificationCallback({ payload: JSON.stringify(event) });

      await vi.waitFor(() => expect(wildcard).toHaveBeenCalledTimes(1));
      expect(wildcard).toHaveBeenCalledWith(event);

      await bus.stop();
    });

    it("calls broadcast function on dispatch", async () => {
      const broadcastFn = vi.fn();
      bus.setBroadcast(broadcastFn);

      mockQuery.mockResolvedValue({ rows: [] });
      await bus.start();

      const notificationCallback = mockListenClient.on.mock.calls.find(
        (call: unknown[]) => call[0] === "notification",
      )![1] as (msg: { payload?: string }) => void;

      const event: DomainEvent = { id: 3, type: "test", payload: { data: 1 } };
      notificationCallback({ payload: JSON.stringify(event) });

      await vi.waitFor(() => expect(broadcastFn).toHaveBeenCalledTimes(1));
      expect(broadcastFn).toHaveBeenCalledWith("logs", {
        id: 3,
        type: "test",
        payload: { data: 1 },
      });

      await bus.stop();
    });

    it("does not call handlers for non-matching event types", async () => {
      const handler = vi.fn().mockResolvedValue(undefined);
      bus.on("session.completed", "test-handler", handler);

      mockQuery.mockResolvedValue({ rows: [] });
      await bus.start();

      const notificationCallback = mockListenClient.on.mock.calls.find(
        (call: unknown[]) => call[0] === "notification",
      )![1] as (msg: { payload?: string }) => void;

      // Emit an event of a different type
      const event: DomainEvent = { id: 4, type: "budget.warning", payload: {} };
      notificationCallback({ payload: JSON.stringify(event) });

      // Give dispatch a tick to complete
      await new Promise((r) => setTimeout(r, 50));
      expect(handler).not.toHaveBeenCalled();

      await bus.stop();
    });

    it("ignores notifications with no payload", async () => {
      mockQuery.mockResolvedValue({ rows: [] });
      await bus.start();

      const notificationCallback = mockListenClient.on.mock.calls.find(
        (call: unknown[]) => call[0] === "notification",
      )![1] as (msg: { payload?: string }) => void;

      // Should not throw
      expect(() => notificationCallback({ payload: undefined })).not.toThrow();
      expect(() => notificationCallback({})).not.toThrow();

      await bus.stop();
    });
  });

  // ------------------------------------------------------------------
  // getRecent
  // ------------------------------------------------------------------
  describe("getRecent", () => {
    it("queries domain_events with default limit", async () => {
      const now = new Date();
      mockQuery.mockResolvedValueOnce({
        rows: [
          { id: 10, type: "test.event", payload: { key: "value" }, created_at: now },
        ],
      });

      const events = await bus.getRecent();
      expect(events).toHaveLength(1);
      expect(events[0].id).toBe(10);
      expect(events[0].type).toBe("test.event");
      expect(events[0].payload).toEqual({ key: "value" });
      expect(events[0].createdAt).toBe(now.toISOString());
    });

    it("filters by type when specified", async () => {
      mockQuery.mockResolvedValueOnce({ rows: [] });

      await bus.getRecent({ type: "session.completed", limit: 10 });

      const sql = mockQuery.mock.calls[0][0] as string;
      expect(sql).toContain("type = $1");
      const params = mockQuery.mock.calls[0][1] as unknown[];
      expect(params).toContain("session.completed");
    });

    it("filters by since when specified", async () => {
      mockQuery.mockResolvedValueOnce({ rows: [] });

      await bus.getRecent({ since: "2026-01-01T00:00:00Z" });

      const sql = mockQuery.mock.calls[0][0] as string;
      expect(sql).toContain("created_at > $1");
    });
  });
});
