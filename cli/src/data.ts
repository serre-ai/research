import { readdir, readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";
import { parse } from "yaml";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..", "..");

export interface ProjectInfo {
  project: string;
  title: string;
  status: string;
  phase: string;
  venue?: string;
  branch: string;
  created: string;
  decisionsMade: number;
  decisionsPending: number;
}

export interface BudgetData {
  monthlyLimit: number;
  currentMonth: string;
  spending: Record<string, Record<string, number>>;
  currentMonthTotal: number;
}

export interface ConfigData {
  budget: { monthly_limit_usd: number; alert_threshold_pct: number };
  resources: { claude_code_max: { plan: string; accounts: number } };
  apis: Record<string, { purpose: string }>;
  decision_policy: { mode: string; reasoning: string };
}

export interface DashboardData {
  projects: ProjectInfo[];
  budget: BudgetData;
  config: ConfigData;
  recentCommits: string[];
}

export async function loadDashboardData(): Promise<DashboardData> {
  const [projects, budget, config, commits] = await Promise.all([
    loadProjects(),
    loadBudget(),
    loadConfig(),
    loadRecentCommits(),
  ]);
  return { projects, budget, config, recentCommits: commits };
}

async function loadProjects(): Promise<ProjectInfo[]> {
  const projectsDir = join(ROOT, "projects");
  try {
    const entries = await readdir(projectsDir, { withFileTypes: true });
    const projects: ProjectInfo[] = [];
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      try {
        const raw = await readFile(
          join(projectsDir, entry.name, "status.yaml"),
          "utf-8",
        );
        const data = parse(raw);
        projects.push({
          project: data.project ?? entry.name,
          title: data.title ?? "",
          status: data.status ?? "unknown",
          phase: data.phase ?? "unknown",
          venue: data.venue,
          branch: data.git?.branch ?? `research/${entry.name}`,
          created: data.created ?? "",
          decisionsMade: Array.isArray(data.decisions_made)
            ? data.decisions_made.length
            : 0,
          decisionsPending: Array.isArray(data.decisions_pending)
            ? data.decisions_pending.length
            : 0,
        });
      } catch {
        /* skip projects without valid status */
      }
    }
    return projects;
  } catch {
    return [];
  }
}

async function loadBudget(): Promise<BudgetData> {
  const currentMonth = new Date().toISOString().slice(0, 7);
  try {
    const raw = await readFile(join(ROOT, "budget.yaml"), "utf-8");
    const data = parse(raw);
    const month = data.current_month ?? currentMonth;
    const monthSpending = data.spending?.[month] ?? {};
    const total = Object.values(monthSpending).reduce(
      (a: number, b) => a + (Number(b) || 0),
      0,
    ) as number;
    return {
      monthlyLimit: data.monthly_limit_usd ?? 1000,
      currentMonth: month,
      spending: data.spending ?? {},
      currentMonthTotal: total,
    };
  } catch {
    return {
      monthlyLimit: 1000,
      currentMonth: currentMonth,
      spending: {},
      currentMonthTotal: 0,
    };
  }
}

async function loadConfig(): Promise<ConfigData> {
  try {
    const raw = await readFile(join(ROOT, "config.yaml"), "utf-8");
    return parse(raw);
  } catch {
    return {
      budget: { monthly_limit_usd: 1000, alert_threshold_pct: 80 },
      resources: { claude_code_max: { plan: "max_2", accounts: 2 } },
      apis: {},
      decision_policy: { mode: "autonomous", reasoning: "extended_thinking" },
    };
  }
}

async function loadRecentCommits(): Promise<string[]> {
  try {
    const output = execSync("git log --oneline -10 --all", {
      cwd: ROOT,
      encoding: "utf-8",
    });
    return output
      .trim()
      .split("\n")
      .filter(Boolean);
  } catch {
    return [];
  }
}
