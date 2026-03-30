import { readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { BudgetTracker } from "./budget-tracker.js";
import { ActivityLogger } from "./logger.js";

const execAsync = promisify(execFile);

export interface HealthStatus {
  daemon: {
    running: boolean;
    lastHeartbeat: string | null;
    heartbeatAgeMs: number | null;
    cycle: number;
    activeSessions: string[];
    uptimeMs: number;
  };
  budget: {
    dailySpent: number;
    dailyLimit: number;
    monthlySpent: number;
    monthlyLimit: number;
    alertLevel: string;
    byProject: Record<string, number>;
  };
  disk: {
    usedGb: number;
    totalGb: number;
    percentUsed: number;
  };
  recentErrors: number;
  lastActivity: string | null;
}

export class Monitor {
  private rootDir: string;
  private budgetTracker: BudgetTracker;
  private logger: ActivityLogger;

  constructor(rootDir: string, budgetTracker: BudgetTracker, logger: ActivityLogger) {
    this.rootDir = rootDir;
    this.budgetTracker = budgetTracker;
    this.logger = logger;
  }

  async getHealth(): Promise<HealthStatus> {
    const [daemon, budget, disk, recentErrors, lastActivity] = await Promise.all([
      this.getDaemonStatus(),
      this.getBudgetStatus(),
      this.getDiskUsage(),
      this.getRecentErrorCount(),
      this.getLastActivity(),
    ]);

    return { daemon, budget, disk, recentErrors, lastActivity };
  }

  private async getDaemonStatus(): Promise<HealthStatus["daemon"]> {
    const heartbeatPath = join(this.rootDir, ".forge.heartbeat");
    try {
      const content = await readFile(heartbeatPath, "utf-8");
      const data = JSON.parse(content) as {
        timestamp: string;
        cycle: number;
        activeSessions: string[];
        uptimeMs: number;
      };
      const heartbeatAge = Date.now() - new Date(data.timestamp).getTime();
      // Consider daemon running if heartbeat is <2x poll interval (default 60 min)
      const running = heartbeatAge < 2 * 60 * 60 * 1000;

      return {
        running,
        lastHeartbeat: data.timestamp,
        heartbeatAgeMs: heartbeatAge,
        cycle: data.cycle,
        activeSessions: data.activeSessions,
        uptimeMs: data.uptimeMs,
      };
    } catch {
      return {
        running: false,
        lastHeartbeat: null,
        heartbeatAgeMs: null,
        cycle: 0,
        activeSessions: [],
        uptimeMs: 0,
      };
    }
  }

  private async getBudgetStatus(): Promise<HealthStatus["budget"]> {
    const status = await this.budgetTracker.getStatus();
    return {
      dailySpent: status.dailySpent,
      dailyLimit: status.dailyLimit,
      monthlySpent: status.monthlySpent,
      monthlyLimit: status.monthlyLimit,
      alertLevel: status.alertLevel,
      byProject: status.byProject,
    };
  }

  private async getDiskUsage(): Promise<HealthStatus["disk"]> {
    try {
      const { stdout } = await execAsync("df", ["-k", this.rootDir]);
      const lines = stdout.trim().split("\n");
      if (lines.length < 2) return { usedGb: 0, totalGb: 0, percentUsed: 0 };

      const parts = lines[1].split(/\s+/);
      const totalKb = parseInt(parts[1], 10);
      const usedKb = parseInt(parts[2], 10);
      return {
        usedGb: parseFloat((usedKb / 1024 / 1024).toFixed(1)),
        totalGb: parseFloat((totalKb / 1024 / 1024).toFixed(1)),
        percentUsed: Math.round((usedKb / totalKb) * 100),
      };
    } catch {
      return { usedGb: 0, totalGb: 0, percentUsed: 0 };
    }
  }

  private async getRecentErrorCount(): Promise<number> {
    const events = await this.logger.recent(100, { type: "session_error" });
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    return events.filter((e) => new Date(e.timestamp).getTime() > oneDayAgo).length;
  }

  private async getLastActivity(): Promise<string | null> {
    const events = await this.logger.recent(1);
    return events.length > 0 ? events[0].timestamp : null;
  }

  formatHealth(health: HealthStatus): string {
    const lines: string[] = [];

    // Daemon
    const daemonStatus = health.daemon.running ? "running" : "stopped";
    const uptime = health.daemon.uptimeMs > 0 ? this.formatDuration(health.daemon.uptimeMs) : "—";
    lines.push(`Daemon:   ${daemonStatus} (uptime: ${uptime}, cycles: ${health.daemon.cycle})`);
    if (health.daemon.activeSessions.length > 0) {
      lines.push(`Sessions: ${health.daemon.activeSessions.join(", ")}`);
    } else {
      lines.push("Sessions: none active");
    }

    // Budget
    lines.push(`Budget:   $${health.budget.dailySpent.toFixed(2)} / $${health.budget.dailyLimit.toFixed(2)} today, $${health.budget.monthlySpent.toFixed(2)} / $${health.budget.monthlyLimit.toFixed(2)} this month [${health.budget.alertLevel}]`);
    if (Object.keys(health.budget.byProject).length > 0) {
      for (const [name, cost] of Object.entries(health.budget.byProject)) {
        lines.push(`          ${name}: $${cost.toFixed(2)}`);
      }
    }

    // Disk
    lines.push(`Disk:     ${health.disk.usedGb} GB / ${health.disk.totalGb} GB (${health.disk.percentUsed}%)`);

    // Errors
    lines.push(`Errors:   ${health.recentErrors} in last 24h`);

    // Last activity
    if (health.lastActivity) {
      const ago = this.formatDuration(Date.now() - new Date(health.lastActivity).getTime());
      lines.push(`Activity: ${ago} ago`);
    } else {
      lines.push("Activity: none recorded");
    }

    return lines.join("\n");
  }

  private formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m`;
    return `${seconds}s`;
  }
}
