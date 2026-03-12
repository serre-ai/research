import { readFile, readdir, writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { ActivityLogger } from "./logger.js";
import { Notifier } from "./notifier.js";

const execFileAsync = promisify(execFile);

// ============================================================
// Types
// ============================================================

export type EvalJobStatus = "queued" | "running" | "completed" | "failed" | "cancelled";

export interface EvalJob {
  id: string;
  model: string;
  task: string;
  condition: string;
  project: string;
  status: EvalJobStatus;
  systemdUnit?: string;
  queuedAt: string;
  startedAt?: string;
  completedAt?: string;
  error?: string;
  instanceCount?: number;
  accuracy?: number;
}

export interface EvalManagerConfig {
  maxConcurrentJobs: number;
  benchmarkDir: string;
  resultsDir: string;
}

const DEFAULT_CONFIG: EvalManagerConfig = {
  maxConcurrentJobs: 2,
  benchmarkDir: "/opt/deepwork/projects/reasoning-gaps/benchmarks",
  resultsDir: "/opt/deepwork/projects/reasoning-gaps/benchmarks/results",
};

// ============================================================
// EvalJobManager
// ============================================================

export class EvalJobManager {
  private config: EvalManagerConfig;
  private rootDir: string;
  private logger: ActivityLogger;
  private notifier: Notifier;
  private queueFile: string;
  private jobs: Map<string, EvalJob> = new Map();
  private initialized = false;

  constructor(
    rootDir: string,
    logger: ActivityLogger,
    notifier: Notifier,
    config: Partial<EvalManagerConfig> = {},
  ) {
    this.rootDir = rootDir;
    this.logger = logger;
    this.notifier = notifier;
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.queueFile = join(rootDir, ".logs", "eval-queue.json");
  }

  /**
   * Called every daemon cycle. Checks running jobs, starts queued ones.
   */
  async tick(): Promise<void> {
    await this.ensureLoaded();

    // Check status of running jobs
    await this.checkRunningJobs();

    // Start queued jobs if slots available
    const running = this.getJobsByStatus("running");
    const queued = this.getJobsByStatus("queued");
    const availableSlots = this.config.maxConcurrentJobs - running.length;

    for (let i = 0; i < Math.min(availableSlots, queued.length); i++) {
      await this.startJob(queued[i]);
    }
  }

  /**
   * Add a new eval job to the queue.
   */
  async enqueue(params: {
    model: string;
    task: string;
    condition: string;
    project?: string;
  }): Promise<EvalJob> {
    await this.ensureLoaded();

    const id = this.makeJobId(params.model, params.task, params.condition);

    // Check for duplicate
    const existing = this.jobs.get(id);
    if (existing && (existing.status === "queued" || existing.status === "running")) {
      return existing;
    }

    const job: EvalJob = {
      id,
      model: params.model,
      task: params.task,
      condition: params.condition,
      project: params.project ?? "reasoning-gaps",
      status: "queued",
      queuedAt: new Date().toISOString(),
    };

    this.jobs.set(id, job);
    await this.persist();

    await this.logger.log({
      type: "experiment_start",
      project: job.project,
      data: { jobId: id, model: job.model, task: job.task, condition: job.condition },
    });

    return job;
  }

  /**
   * Cancel a queued or running job.
   */
  async cancel(jobId: string): Promise<boolean> {
    await this.ensureLoaded();

    const job = this.jobs.get(jobId);
    if (!job) return false;

    if (job.status === "running" && job.systemdUnit) {
      try {
        await execFileAsync("systemctl", ["stop", job.systemdUnit]);
      } catch {
        // Unit might already be stopped
      }
    }

    if (job.status === "queued" || job.status === "running") {
      job.status = "cancelled";
      job.completedAt = new Date().toISOString();
      await this.persist();
      return true;
    }

    return false;
  }

  /**
   * Get all jobs, optionally filtered by status.
   */
  listJobs(status?: EvalJobStatus): EvalJob[] {
    if (status) {
      return this.getJobsByStatus(status);
    }
    return Array.from(this.jobs.values())
      .sort((a, b) => new Date(b.queuedAt).getTime() - new Date(a.queuedAt).getTime());
  }

  /**
   * Get a single job by ID.
   */
  getJob(jobId: string): EvalJob | undefined {
    return this.jobs.get(jobId);
  }

  /**
   * Scan the results directory for incomplete eval combos and enqueue them.
   */
  async scanIncomplete(
    models: string[],
    tasks: string[],
    conditions: string[],
    expectedPerCombo: number = 500,
  ): Promise<EvalJob[]> {
    await this.ensureLoaded();
    const enqueued: EvalJob[] = [];

    for (const model of models) {
      for (const task of tasks) {
        for (const condition of conditions) {
          // Check final JSON result: {provider}_{model}_{task}_{condition}.json
          const flatModel = model.replace(/:/g, "_");
          const resultFile = join(
            this.config.resultsDir,
            `${flatModel}_${task}_${condition}.json`,
          );

          let instanceCount = 0;
          try {
            const content = await readFile(resultFile, "utf-8");
            const data = JSON.parse(content);
            instanceCount = data.summary?.total_instances ?? 0;
          } catch {
            // File doesn't exist — 0 instances
          }

          if (instanceCount < expectedPerCombo) {
            const job = await this.enqueue({ model, task, condition });
            enqueued.push(job);
          }
        }
      }
    }

    return enqueued;
  }

  // ============================================================
  // Private methods
  // ============================================================

  private async startJob(job: EvalJob): Promise<void> {
    // Instance format: model::task::condition (using :: delimiter)
    const instanceName = `${job.model}::${job.task}::${job.condition}`;
    const unitName = `deepwork-eval@${instanceName}.service`;

    try {
      await execFileAsync("systemctl", ["start", unitName]);

      job.status = "running";
      job.startedAt = new Date().toISOString();
      job.systemdUnit = unitName;
      await this.persist();

      console.log(`[eval-manager] Started ${unitName}`);

      await this.logger.log({
        type: "experiment_start",
        project: job.project,
        data: {
          jobId: job.id,
          model: job.model,
          task: job.task,
          condition: job.condition,
          systemdUnit: unitName,
        },
      });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      job.status = "failed";
      job.completedAt = new Date().toISOString();
      job.error = `Failed to start systemd unit: ${errorMsg}`;
      await this.persist();

      console.error(`[eval-manager] Failed to start ${unitName}: ${errorMsg}`);

      await this.notifier.notify({
        event: "Eval Job Failed",
        project: job.project,
        summary: `Failed to start ${job.model} / ${job.task} / ${job.condition}: ${errorMsg}`,
        level: "error",
      });
    }
  }

  private async checkRunningJobs(): Promise<void> {
    const running = this.getJobsByStatus("running");

    for (const job of running) {
      if (!job.systemdUnit) continue;

      const isActive = await this.isUnitActive(job.systemdUnit);

      if (!isActive) {
        // Job finished — check exit status
        const exitStatus = await this.getUnitExitStatus(job.systemdUnit);
        const success = exitStatus === 0;

        if (success) {
          job.status = "completed";
          job.completedAt = new Date().toISOString();

          // Try to read result stats
          const stats = await this.readResultStats(job);
          if (stats) {
            job.instanceCount = stats.count;
            job.accuracy = stats.accuracy;
          }

          console.log(
            `[eval-manager] Completed: ${job.model}/${job.task}/${job.condition}` +
            (stats ? ` — ${stats.count} instances, ${(stats.accuracy * 100).toFixed(1)}% accuracy` : ""),
          );

          await this.logger.log({
            type: "experiment_end",
            project: job.project,
            data: {
              jobId: job.id,
              model: job.model,
              task: job.task,
              condition: job.condition,
              instanceCount: stats?.count,
              accuracy: stats?.accuracy,
            },
          });

          await this.notifier.notify({
            event: "Eval Job Completed",
            project: job.project,
            summary: `${job.model} / ${job.task} / ${job.condition}: ` +
              (stats ? `${stats.count} instances, ${(stats.accuracy * 100).toFixed(1)}% accuracy` : "completed"),
            level: "info",
          });
        } else {
          job.status = "failed";
          job.completedAt = new Date().toISOString();
          job.error = `Systemd unit exited with status ${exitStatus}`;

          console.error(`[eval-manager] Failed: ${job.model}/${job.task}/${job.condition} (exit ${exitStatus})`);

          await this.notifier.notify({
            event: "Eval Job Failed",
            project: job.project,
            summary: `${job.model} / ${job.task} / ${job.condition} exited with status ${exitStatus}`,
            level: "error",
          });
        }

        await this.persist();
      }
    }
  }

  private async isUnitActive(unit: string): Promise<boolean> {
    try {
      const { stdout } = await execFileAsync("systemctl", ["is-active", unit]);
      return stdout.trim() === "active";
    } catch {
      return false;
    }
  }

  private async getUnitExitStatus(unit: string): Promise<number> {
    try {
      const { stdout } = await execFileAsync("systemctl", [
        "show", unit, "--property=ExecMainStatus", "--value",
      ]);
      return parseInt(stdout.trim(), 10) || 0;
    } catch {
      return -1;
    }
  }

  private async readResultStats(
    job: EvalJob,
  ): Promise<{ count: number; accuracy: number } | null> {
    // Try final JSON result file: {provider}_{model}_{task}_{condition}.json
    // Model format is "provider:model" — flatten to "provider_model"
    const flatModel = job.model.replace(/:/g, "_");
    const jsonFile = join(
      this.config.resultsDir,
      `${flatModel}_${job.task}_${job.condition}.json`,
    );

    try {
      const content = await readFile(jsonFile, "utf-8");
      const data = JSON.parse(content);
      if (data.summary) {
        return {
          count: data.summary.total_instances ?? 0,
          accuracy: data.summary.accuracy ?? 0,
        };
      }
    } catch {
      // Fall through to checkpoint
    }

    // Try checkpoint JSONL: {short_model}_{task_full}_{condition}.jsonl
    // Short model is the part after ":" (e.g., "openai:o3" -> "o3")
    const shortModel = job.model.includes(":") ? job.model.split(":").pop()! : job.model;
    const checkpointDir = join(this.config.resultsDir, "checkpoints");

    try {
      // Find matching checkpoint file by prefix
      const files = await readdir(checkpointDir);
      const prefix = `${shortModel}_${job.task}_`;
      const suffix = `_${job.condition}.jsonl`;
      const match = files.find((f) => f.startsWith(prefix) && f.endsWith(suffix));

      if (!match) return null;

      const content = await readFile(join(checkpointDir, match), "utf-8");
      const lines = content.trim().split("\n").filter(Boolean);
      if (lines.length === 0) return null;

      let correct = 0;
      for (const line of lines) {
        const entry = JSON.parse(line);
        if (entry.correct) correct++;
      }

      return {
        count: lines.length,
        accuracy: lines.length > 0 ? correct / lines.length : 0,
      };
    } catch {
      return null;
    }
  }

  private getJobsByStatus(status: EvalJobStatus): EvalJob[] {
    return Array.from(this.jobs.values()).filter((j) => j.status === status);
  }

  private makeJobId(model: string, task: string, condition: string): string {
    return `${model}__${task}__${condition}`;
  }

  private async ensureLoaded(): Promise<void> {
    if (this.initialized) return;
    this.initialized = true;

    try {
      const content = await readFile(this.queueFile, "utf-8");
      const saved = JSON.parse(content) as EvalJob[];
      for (const job of saved) {
        this.jobs.set(job.id, job);
      }
      console.log(`[eval-manager] Loaded ${saved.length} jobs from queue file`);
    } catch {
      // No queue file yet — fresh start
    }
  }

  private async persist(): Promise<void> {
    const dir = join(this.rootDir, ".logs");
    await mkdir(dir, { recursive: true });
    const jobs = Array.from(this.jobs.values());
    await writeFile(this.queueFile, JSON.stringify(jobs, null, 2), "utf-8");
  }
}
