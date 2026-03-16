import { appendFile, readFile, mkdir } from "node:fs/promises";
import { join } from "node:path";

export type EventType =
  | "session_start" | "session_end" | "session_error"
  | "session_chain" | "session_quality"
  | "commit" | "push" | "pr_created" | "pr_merged"
  | "decision_created" | "decision_resolved"
  | "budget_spend" | "budget_alert"
  | "experiment_start" | "experiment_end"
  | "eval_job_queued" | "eval_job_started" | "eval_job_completed" | "eval_job_failed"
  | "phase_transition"
  | "daemon_start" | "daemon_stop" | "daemon_error"
  | "knowledge_contradictions" | "knowledge_snapshot";

export interface ActivityEvent {
  timestamp: string;
  type: EventType;
  project?: string;
  agent?: string;
  data: Record<string, unknown>;
}

export class ActivityLogger {
  private readonly logsDir: string;
  private readonly logFile: string;
  private dirCreated = false;
  private onEvent?: (event: ActivityEvent) => void;

  constructor(rootDir: string = process.cwd()) {
    this.logsDir = join(rootDir, ".logs");
    this.logFile = join(this.logsDir, "activity.jsonl");
  }

  setBroadcast(fn: (event: ActivityEvent) => void): void {
    this.onEvent = fn;
  }

  async log(event: Omit<ActivityEvent, "timestamp">): Promise<void> {
    await this.ensureDir();
    const entry: ActivityEvent = {
      timestamp: new Date().toISOString(),
      ...event,
    };
    await appendFile(this.logFile, JSON.stringify(entry) + "\n", "utf-8");
    this.onEvent?.(entry);
  }

  async recent(
    count: number,
    filter?: { type?: EventType; project?: string },
  ): Promise<ActivityEvent[]> {
    let content: string;
    try {
      content = await readFile(this.logFile, "utf-8");
    } catch {
      return [];
    }

    const lines = content.trim().split("\n").filter(Boolean);
    let events: ActivityEvent[] = lines.map((line) => JSON.parse(line) as ActivityEvent);

    if (filter?.type) {
      events = events.filter((e) => e.type === filter.type);
    }
    if (filter?.project) {
      events = events.filter((e) => e.project === filter.project);
    }

    return events.slice(-count);
  }

  async getLogPath(): Promise<string> {
    return this.logFile;
  }

  private async ensureDir(): Promise<void> {
    if (this.dirCreated) return;
    await mkdir(this.logsDir, { recursive: true });
    this.dirCreated = true;
  }
}
