#!/usr/bin/env node

import { ProjectManager } from "./project-manager.js";
import { SessionManager } from "./session-manager.js";
import { GitEngine } from "./git-engine.js";
import { Daemon } from "./daemon.js";
import { BudgetTracker } from "./budget-tracker.js";
import { ActivityLogger } from "./logger.js";

function parseFlag(args: string[], flag: string, defaultValue: string): string {
  const idx = args.indexOf(flag);
  if (idx === -1 || idx + 1 >= args.length) return defaultValue;
  return args[idx + 1];
}

async function main() {
  const rootDir = process.cwd();
  const projectManager = new ProjectManager(rootDir);
  const gitEngine = new GitEngine(rootDir);
  const sessionManager = new SessionManager(projectManager, gitEngine, rootDir);
  const logger = new ActivityLogger(rootDir);
  const budgetTracker = new BudgetTracker(rootDir, logger);

  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case "run": {
      const interval = parseInt(parseFlag(args, "--interval", String(process.env.POLL_INTERVAL_MINUTES ?? "30")), 10);
      const maxSessions = parseInt(parseFlag(args, "--max-sessions", String(process.env.MAX_CONCURRENT_SESSIONS ?? "2")), 10);
      const budget = parseInt(parseFlag(args, "--budget", String(process.env.DAILY_BUDGET_USD ?? "40")), 10);

      const daemon = new Daemon({
        pollIntervalMs: interval * 60 * 1000,
        maxConcurrentSessions: maxSessions,
        dailyBudgetUsd: budget,
        rootDir,
      });

      await daemon.start();
      break;
    }

    case "start": {
      const projectName = args[1];
      if (!projectName) {
        console.error("Usage: deepwork start <project-name> [--agent <type>] [--turns <n>]");
        process.exit(1);
      }
      const agentType = parseFlag(args, "--agent", "researcher") as "researcher" | "writer" | "reviewer" | "editor" | "strategist";
      const maxTurns = parseInt(parseFlag(args, "--turns", "50"), 10);
      await sessionManager.startProject(projectName, agentType, { maxTurns });
      break;
    }

    case "list": {
      const projects = await projectManager.listProjects();
      if (projects.length === 0) {
        console.log("No projects found.");
        break;
      }
      for (const p of projects) {
        console.log(`${p.status === "active" ? "●" : "○"} ${p.project} — ${p.title}`);
        console.log(`  Phase: ${p.phase} | Branch: ${p.git.branch}`);
      }
      break;
    }

    case "budget": {
      const status = await budgetTracker.getStatus();
      console.log("Budget Status");
      console.log(`  Daily:   $${status.dailySpent.toFixed(2)} / $${status.dailyLimit.toFixed(2)} (${status.dailyRemaining.toFixed(2)} remaining)`);
      console.log(`  Monthly: $${status.monthlySpent.toFixed(2)} / $${status.monthlyLimit.toFixed(2)} (${status.monthlyRemaining.toFixed(2)} remaining)`);
      console.log(`  Alert:   ${status.alertLevel}`);
      if (Object.keys(status.byProject).length > 0) {
        console.log("  By project:");
        for (const [name, cost] of Object.entries(status.byProject)) {
          console.log(`    ${name}: $${cost.toFixed(2)}`);
        }
      }
      break;
    }

    case "activity": {
      const count = parseInt(args[1] ?? "20", 10);
      const events = await logger.recent(count);
      for (const e of events) {
        const time = e.timestamp.slice(11, 19);
        const proj = e.project ? ` [${e.project}]` : "";
        console.log(`${time} ${e.type}${proj}`);
      }
      break;
    }

    default:
      console.log("Deepwork Research Platform v0.1.0");
      console.log("");
      console.log("Commands:");
      console.log("  run                        Start the daemon scheduler");
      console.log("    --interval <minutes>     Poll interval (default: 30)");
      console.log("    --max-sessions <n>       Max concurrent sessions (default: 2)");
      console.log("    --budget <usd>           Daily budget limit (default: 40)");
      console.log("  start <project> [opts]     Run a single session");
      console.log("    --agent <type>           Agent type (default: researcher)");
      console.log("    --turns <n>              Max turns (default: 50)");
      console.log("  list                       List all projects");
      console.log("  budget                     Show budget status");
      console.log("  activity [count]           Show recent activity");
  }
}

main().catch(console.error);
