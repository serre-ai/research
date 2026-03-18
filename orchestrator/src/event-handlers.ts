/**
 * Event handler registry — connects domain events to side effects.
 *
 * Each handler is registered on a specific event type and runs
 * asynchronously when that event fires. The EventBus manages
 * retry and dead-letter for failed handlers.
 */

import type { EventBus, DomainEvent } from "./event-bus.js";
import type { KnowledgeGraph } from "./knowledge-graph.js";
import type { Notifier } from "./notifier.js";
import type { ActivityLogger } from "./logger.js";
import type { ClaimVerifier } from "./verification.js";

// ============================================================
// Handler registration
// ============================================================

export interface HandlerDeps {
  knowledgeGraph?: KnowledgeGraph | null;
  notifier?: Notifier | null;
  logger?: ActivityLogger | null;
  verifier?: ClaimVerifier | null;
}

/**
 * Register all domain event handlers on the given EventBus.
 * Call once at startup after constructing the bus and its dependencies.
 */
export function registerHandlers(bus: EventBus, deps: HandlerDeps): void {
  const { knowledgeGraph, notifier, logger, verifier } = deps;

  // --- Session lifecycle ---

  bus.on("session.completed", "log-session-completed", async (event) => {
    if (logger) {
      await logger.log({
        type: "session_end",
        project: event.payload.project as string,
        agent: event.payload.agentType as string,
        data: {
          sessionId: event.payload.sessionId,
          commits: event.payload.commits,
          cost: event.payload.costUsd,
          quality: event.payload.quality,
          source: "event_bus",
        },
      });
    }
  });

  bus.on("session.failed", "notify-session-failed", async (event) => {
    if (notifier) {
      await notifier.notify({
        event: "Session Failed",
        project: event.payload.project as string,
        summary: `${event.payload.agentType}: ${event.payload.error}`,
        level: "error",
      });
    }
  });

  // --- Knowledge graph events ---

  bus.on("claim.added", "log-claim-added", async (event) => {
    if (logger) {
      await logger.log({
        type: "knowledge_snapshot",
        project: event.payload.project as string,
        data: {
          claimId: event.payload.claimId,
          claimType: event.payload.claimType,
          source: "event_bus",
        },
      });
    }
  });

  bus.on("contradiction.detected", "notify-contradiction", async (event) => {
    if (notifier) {
      await notifier.notify({
        event: "Contradiction Detected",
        project: event.payload.project as string,
        summary: `Claims ${event.payload.sourceId} and ${event.payload.targetId} contradict (strength: ${event.payload.strength})`,
        level: "warning",
      });
    }
  });

  // --- Budget events ---

  bus.on("budget.critical", "notify-budget-critical", async (event) => {
    if (notifier) {
      await notifier.notify({
        event: "Budget Critical",
        summary: `Daily: $${event.payload.dailySpent}/$${event.payload.dailyLimit} | Monthly: $${event.payload.monthlySpent}/$${event.payload.monthlyLimit}`,
        level: "error",
      });
    }
  });

  // --- Eval events ---

  bus.on("eval.completed", "log-eval-completed", async (event) => {
    if (logger) {
      await logger.log({
        type: "session_end",
        project: event.payload.project as string,
        data: {
          runId: event.payload.runId,
          model: event.payload.model,
          task: event.payload.task,
          accuracy: event.payload.accuracy,
          source: "event_bus",
        },
      });
    }
  });

  // --- Paper verification ---

  bus.on("paper.edited", "auto-verify-paper", async (event) => {
    if (!verifier) return;
    const project = event.payload.project as string;
    try {
      const report = await verifier.verifyAll(project);
      if (logger) {
        await logger.log({
          type: "verification_completed",
          project,
          data: {
            totalClaims: report.totalClaims,
            verified: report.verifiedClaims,
            inconsistencies: report.inconsistencies,
            triggeredBy: event.payload.sessionId,
          },
        });
      }
      if (report.inconsistencies > 0 && notifier) {
        await notifier.notify({
          event: "Verification Issues",
          project,
          summary: `${report.inconsistencies} inconsistency(ies) in paper after edit (${report.verifiedClaims}/${report.totalClaims} verified)`,
          level: "warning",
        });
      }
    } catch (err) {
      console.error("[Verification] Auto-verify failed:", err);
    }
  });

  // --- Wildcard: forward all events to knowledge graph as observations ---

  if (knowledgeGraph) {
    bus.onAny("kg-observation-recorder", async (event: DomainEvent) => {
      // Only record significant lifecycle events as observations
      const recordable = ["session.completed", "eval.completed", "contradiction.detected"];
      if (!recordable.includes(event.type)) return;

      const project = event.payload.project as string | undefined;
      if (!project) return;

      try {
        await knowledgeGraph.addClaim({
          project,
          claimType: "observation",
          statement: formatEventAsObservation(event),
          confidence: 0.9,
          source: `event:${event.id}`,
          sourceType: "agent_session",
          metadata: { eventType: event.type, eventId: event.id },
        });
      } catch {
        // Best effort — don't fail the handler chain for KG writes
      }
    });
  }
}

// ============================================================
// Helpers
// ============================================================

function formatEventAsObservation(event: DomainEvent): string {
  switch (event.type) {
    case "session.completed":
      return `${event.payload.agentType} session completed for ${event.payload.project}: ${event.payload.commits} commits, $${(event.payload.costUsd as number)?.toFixed(2)} cost, quality ${event.payload.quality}/100`;
    case "eval.completed":
      return `Eval run ${event.payload.runId} completed: ${event.payload.model} on ${event.payload.task}, accuracy ${event.payload.accuracy}`;
    case "contradiction.detected":
      return `Contradiction detected between claims ${event.payload.sourceId} and ${event.payload.targetId} (strength: ${event.payload.strength})`;
    default:
      return `Event ${event.type}: ${JSON.stringify(event.payload).slice(0, 200)}`;
  }
}
