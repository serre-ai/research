#!/usr/bin/env node

import { ProjectManager } from "./project-manager.js";
import { SessionManager } from "./session-manager.js";
import { GitEngine } from "./git-engine.js";
import { Daemon, type DaemonConfig } from "./daemon.js";
import { createApi } from "./api.js";
import { readFileSync, existsSync } from "node:fs";
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

  const args = process.argv.slice(2);
  const command = args[0];

  // Parse --root-dir early so all subcommands can use it
  let cliRootDir: string | undefined;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--root-dir" && args[i + 1]) { cliRootDir = args[i + 1]; break; }
  }
  const baseRootDir = cliRootDir ?? process.env.DAEMON_ROOT_DIR ?? process.cwd();

  const projectManager = new ProjectManager(baseRootDir);
  const gitEngine = new GitEngine(baseRootDir);
  const sessionManager = new SessionManager(projectManager, gitEngine, baseRootDir);

  switch (command) {
    case "run": {
      // Parse flags
      let interval = Number(process.env.POLL_INTERVAL_MINUTES) || 30;
      let maxSessions = Number(process.env.MAX_CONCURRENT_SESSIONS) || 2;
      let budget = Number(process.env.DAILY_BUDGET_USD) || 40;

      const rootDir = baseRootDir;

      for (let i = 1; i < args.length; i++) {
        if (args[i] === "--interval" && args[i + 1]) interval = Number(args[++i]);
        if (args[i] === "--max-sessions" && args[i + 1]) maxSessions = Number(args[++i]);
        if (args[i] === "--budget" && args[i + 1]) budget = Number(args[++i]);
      }

      // Validate parsed values
      if (interval < 1) { console.error("--interval must be >= 1 (minutes)"); process.exit(1); }
      if (maxSessions < 1) { console.error("--max-sessions must be >= 1"); process.exit(1); }
      if (budget < 1) { console.error("--budget must be >= 1 (USD)"); process.exit(1); }
      if (!existsSync(rootDir)) { console.error("--root-dir does not exist:", rootDir); process.exit(1); }

      const config: DaemonConfig = {
        pollIntervalMs: interval * 60 * 1000,
        maxConcurrentSessions: maxSessions,
        dailyBudgetUsd: budget,
        rootDir,
      };

      console.log(`Starting daemon: interval=${interval}m, sessions=${maxSessions}, budget=$${budget}/day`);
      if (rootDir !== process.cwd()) {
        console.log(`  Root directory: ${rootDir}`);
      }

      // Create DB pool for daemon + API to share
      const apiKey = process.env.DEEPWORK_API_KEY;
      const databaseUrl = process.env.DATABASE_URL;
      const apiPort = Number(process.env.API_PORT) || 3001;

      let dbPool: import("pg").Pool | undefined;
      if (databaseUrl) {
        const pg = await import("pg");
        dbPool = new pg.default.Pool({ connectionString: databaseUrl, max: 10 });

        // Handle pool errors to prevent unhandled rejections
        dbPool.on("error", (err) => {
          console.error("[DB Pool] Unexpected error on idle client:", err);
        });
      }

      // Verify database connection before proceeding
      if (dbPool) {
        try {
          await dbPool.query("SELECT 1");
          console.log("Database connection verified");
        } catch (err) {
          console.error("Failed to connect to database:", err instanceof Error ? err.message : err);
          process.exit(1);
        }
      }

      // Run database migrations before starting daemon
      if (dbPool) {
        const { runMigrations } = await import("./migrate.js");
        await runMigrations(dbPool);
      }

      const daemon = new Daemon(config, dbPool);

      let closeApi: (() => Promise<void>) | undefined;

      if (apiKey && databaseUrl) {
        const { broadcast, close } = createApi(
          { port: apiPort, apiKey, databaseUrl, pool: dbPool, corsOrigin: process.env.CORS_ORIGIN, rootDir },
          daemon.getEvalManager(),
          daemon.getLogger(),
          (project) => daemon.getQualityHistory(project),
          daemon,
        );
        closeApi = close;

        // Wire activity logger → WebSocket broadcast
        daemon.getLogger().setBroadcast((event) => broadcast("logs", event));
      } else {
        console.log("API server skipped (DEEPWORK_API_KEY or DATABASE_URL not set)");
      }

      // Start daemon loop (blocks until shutdown signal)
      await daemon.start();

      // Daemon loop exited — clean up all resources keeping the event loop alive
      console.log("Cleaning up resources...");

      if (closeApi) {
        await closeApi();
        console.log("  API server closed");
      }

      if (dbPool) {
        await dbPool.end();
        console.log("  DB pool closed");
      }

      console.log("All resources released. Exiting.");
      process.exit(0);
    }

    case "start": {
      const projectName = args[1];
      if (!projectName) {
        console.error("Usage: forge start <project-name>");
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
      console.log("Forge v0.1.0");
      console.log("Commands: run, start <project>, list");
  }
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
