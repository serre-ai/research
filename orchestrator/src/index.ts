#!/usr/bin/env node

import { ProjectManager } from "./project-manager.js";
import { SessionManager } from "./session-manager.js";
import { GitEngine } from "./git-engine.js";
import { Daemon, type DaemonConfig } from "./daemon.js";
import { createApi } from "./api.js";
import { readFileSync } from "node:fs";
import { join } from "node:path";

function loadEnv(): void {
  try {
    const envPath = join(process.cwd(), ".env");
    const content = readFileSync(envPath, "utf-8");
    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const eqIdx = trimmed.indexOf("=");
      if (eqIdx === -1) continue;
      const key = trimmed.slice(0, eqIdx).trim();
      const value = trimmed.slice(eqIdx + 1).trim();
      if (!process.env[key]) {
        process.env[key] = value;
      }
    }
  } catch {
    // .env not found, continue with existing env
  }
}

async function main() {
  loadEnv();

  const projectManager = new ProjectManager();
  const gitEngine = new GitEngine();
  const sessionManager = new SessionManager(projectManager, gitEngine);

  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case "run": {
      // Parse flags
      let interval = Number(process.env.POLL_INTERVAL_MINUTES) || 30;
      let maxSessions = Number(process.env.MAX_CONCURRENT_SESSIONS) || 2;
      let budget = Number(process.env.DAILY_BUDGET_USD) || 40;

      for (let i = 1; i < args.length; i++) {
        if (args[i] === "--interval" && args[i + 1]) interval = Number(args[++i]);
        if (args[i] === "--max-sessions" && args[i + 1]) maxSessions = Number(args[++i]);
        if (args[i] === "--budget" && args[i + 1]) budget = Number(args[++i]);
      }

      const config: DaemonConfig = {
        pollIntervalMs: interval * 60 * 1000,
        maxConcurrentSessions: maxSessions,
        dailyBudgetUsd: budget,
        rootDir: process.cwd(),
      };

      console.log(`Starting daemon: interval=${interval}m, sessions=${maxSessions}, budget=$${budget}/day`);

      // Create DB pool for daemon + API to share
      const apiKey = process.env.DEEPWORK_API_KEY;
      const databaseUrl = process.env.DATABASE_URL;
      const apiPort = Number(process.env.API_PORT) || 3001;

      let dbPool: import("pg").Pool | undefined;
      if (databaseUrl) {
        const pg = await import("pg");
        dbPool = new pg.default.Pool({ connectionString: databaseUrl, max: 10 });
      }

      const daemon = new Daemon(config, dbPool);

      if (apiKey && databaseUrl) {
        const { broadcast } = createApi(
          { port: apiPort, apiKey, databaseUrl },
          daemon.getEvalManager(),
          daemon.getLogger(),
          (project) => daemon.getQualityHistory(project),
          daemon,
        );

        // Wire activity logger → WebSocket broadcast
        daemon.getLogger().setBroadcast((event) => broadcast("logs", event));

        console.log(`API server listening on port ${apiPort}`);
      } else {
        console.log("API server skipped (DEEPWORK_API_KEY or DATABASE_URL not set)");
      }

      // Start daemon loop
      await daemon.start();
      break;
    }

    case "start": {
      const projectName = args[1];
      if (!projectName) {
        console.error("Usage: deepwork start <project-name>");
        process.exit(1);
      }
      await sessionManager.startProject(projectName);
      break;
    }

    case "list": {
      const projects = await projectManager.listProjects();
      for (const p of projects) {
        console.log(`${p.status === "active" ? "●" : "○"} ${p.project} — ${p.title}`);
        console.log(`  Phase: ${p.phase} | Branch: ${p.git?.branch ?? "n/a"}`);
      }
      break;
    }

    default:
      console.log("Deepwork Research Platform v0.1.0");
      console.log("Commands: run, start <project>, list");
  }
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
