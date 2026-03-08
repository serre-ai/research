#!/usr/bin/env node

import { ProjectManager } from "./project-manager.js";
import { SessionManager } from "./session-manager.js";
import { GitEngine } from "./git-engine.js";

async function main() {
  const projectManager = new ProjectManager();
  const gitEngine = new GitEngine();
  const sessionManager = new SessionManager(projectManager, gitEngine);

  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
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
        console.log(`  Phase: ${p.phase} | Branch: ${p.git.branch}`);
      }
      break;
    }
    default:
      console.log("Deepwork Research Platform v0.1.0");
      console.log("Commands: start <project>, list");
  }
}

main().catch(console.error);
