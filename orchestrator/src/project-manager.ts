import { readdir, readFile, writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import { parse as parseYaml, stringify as stringifyYaml } from "./yaml.js";

export interface ProjectStatus {
  project: string;
  title: string;
  status: "active" | "in-progress" | "blocked" | "paused" | "review" | "completed";
  phase: string;
  confidence: number;
  created: string;
  updated: string;
  collaborators: string[];
  current_focus: string;
  current_activity?: string;
  venue?: string;
  key_terms?: string[];
  next_steps: string[];
  immediate_next_steps?: Record<string, {
    agent?: string;
    priority?: string;
    blocking?: string;
    tasks?: string[];
    status?: string;
  }>;
  decisions_pending: Decision[];
  git?: {
    branch: string;
    latest_commit: string;
    open_prs: string[];
  };
  metrics: Record<string, number>;
}

export interface Decision {
  id: string;
  question: string;
  context: string;
  options: string[];
  priority: "low" | "medium" | "high";
  created: string;
  resolved?: string;
  answer?: string;
}

const PROJECTS_DIR = "projects";

export class ProjectManager {
  private rootDir: string;

  constructor(rootDir: string = process.cwd()) {
    this.rootDir = rootDir;
  }

  async listProjects(): Promise<ProjectStatus[]> {
    const projectsPath = join(this.rootDir, PROJECTS_DIR);
    const entries = await readdir(projectsPath, { withFileTypes: true });
    const projects: ProjectStatus[] = [];

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      try {
        const status = await this.getProjectStatus(entry.name);
        projects.push(status);
      } catch {
        // Skip projects without valid status.yaml
      }
    }
    return projects;
  }

  async getProjectStatus(name: string): Promise<ProjectStatus> {
    const statusPath = join(this.rootDir, PROJECTS_DIR, name, "status.yaml");
    const content = await readFile(statusPath, "utf-8");
    return parseYaml(content) as unknown as ProjectStatus;
  }

  async updateProjectStatus(
    name: string,
    updates: Partial<ProjectStatus>,
  ): Promise<void> {
    const current = await this.getProjectStatus(name);
    const updated = { ...current, ...updates, updated: new Date().toISOString() };
    const statusPath = join(this.rootDir, PROJECTS_DIR, name, "status.yaml");
    await writeFile(statusPath, stringifyYaml(updated as unknown as Record<string, unknown>));
  }

  async createProject(config: {
    name: string;
    title: string;
    brief: string;
    collaborators: string[];
  }): Promise<void> {
    const projectDir = join(this.rootDir, PROJECTS_DIR, config.name);
    await mkdir(projectDir, { recursive: true });
    await mkdir(join(projectDir, "paper", "figures"), { recursive: true });
    await mkdir(join(projectDir, "src"), { recursive: true });
    await mkdir(join(projectDir, "data"), { recursive: true });
    await mkdir(join(projectDir, "notes"), { recursive: true });

    const status: ProjectStatus = {
      project: config.name,
      title: config.title,
      status: "active",
      phase: "research",
      confidence: 0.5,
      created: new Date().toISOString().split("T")[0],
      updated: new Date().toISOString(),
      collaborators: config.collaborators,
      current_focus: "Initial research and literature review",
      next_steps: ["Survey existing literature", "Identify research gap", "Draft methodology"],
      decisions_pending: [],
      git: {
        branch: "main",
        latest_commit: "",
        open_prs: [],
      },
      metrics: {
        papers_reviewed: 0,
        sections_drafted: 0,
        experiments_run: 0,
      },
    };

    await writeFile(join(projectDir, "status.yaml"), stringifyYaml(status as unknown as Record<string, unknown>));
    await writeFile(join(projectDir, "BRIEF.md"), config.brief);
    await writeFile(
      join(projectDir, "CLAUDE.md"),
      `# ${config.title}\n\nSee BRIEF.md for research goals.\nSee status.yaml for current state.\n\n## Instructions\n- Focus on producing novel, rigorous, publishable research\n- Update status.yaml after each significant milestone\n- Add decision entries when uncertain about direction\n- Commit frequently with conventional commit format: \`type(${config.name}): description\`\n`,
    );
  }

  async addDecision(projectName: string, decision: Omit<Decision, "id" | "created">): Promise<string> {
    const status = await this.getProjectStatus(projectName);
    const id = `d${String(status.decisions_pending.length + 1).padStart(3, "0")}`;
    status.decisions_pending.push({
      ...decision,
      id,
      created: new Date().toISOString(),
    });
    await this.updateProjectStatus(projectName, {
      decisions_pending: status.decisions_pending,
    });
    return id;
  }

  async resolveDecision(projectName: string, decisionId: string, answer: string): Promise<void> {
    const status = await this.getProjectStatus(projectName);
    const decision = status.decisions_pending.find((d) => d.id === decisionId);
    if (decision) {
      decision.resolved = new Date().toISOString();
      decision.answer = answer;
    }
    await this.updateProjectStatus(projectName, {
      decisions_pending: status.decisions_pending,
    });
  }
}
