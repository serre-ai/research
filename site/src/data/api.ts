// Fetch live data from VPS API — transforms API responses into dashboard types

import type {
  Project, ProjectEvalData, ProjectBudgetData, Decision,
  ModelData, EvalTask,
} from './mock';
import { evalTasks } from './mock';

// Same-origin: site and API served from the same domain, so empty base = relative URLs
const API_BASE = import.meta.env.DEEPWORK_API_URL ?? '';
const API_KEY = import.meta.env.DEEPWORK_API_KEY ?? '';

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'X-Api-Key': API_KEY },
    signal: AbortSignal.timeout(5000),
  });
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`);
  return res.json() as Promise<T>;
}

// Model display name mapping
const MODEL_DISPLAY: Record<string, { name: string; family: string; scale: 'small' | 'large'; provider: string }> = {
  'claude-haiku-4-5-20251001': { name: 'haiku-4.5', family: 'Claude', scale: 'small', provider: 'Anthropic' },
  'claude-sonnet-4-20250514': { name: 'sonnet-4', family: 'Claude', scale: 'large', provider: 'Anthropic' },
  'gpt-4o-mini': { name: 'gpt-4o-mini', family: 'GPT', scale: 'small', provider: 'OpenAI' },
  'gpt-4o': { name: 'gpt-4o', family: 'GPT', scale: 'large', provider: 'OpenAI' },
  'o3': { name: 'o3', family: 'GPT', scale: 'large', provider: 'OpenAI' },
  'meta-llama/llama-3.1-8b-instruct': { name: 'llama-3.1-8b', family: 'Llama', scale: 'small', provider: 'OpenRouter' },
  'meta-llama/llama-3.1-70b-instruct': { name: 'llama-3.1-70b', family: 'Llama', scale: 'large', provider: 'OpenRouter' },
  'mistralai/ministral-8b-2512': { name: 'ministral-8b', family: 'Mistral', scale: 'small', provider: 'OpenRouter' },
  'mistralai/mistral-small-24b-instruct-2501': { name: 'mistral-small-24b', family: 'Mistral', scale: 'large', provider: 'OpenRouter' },
  'qwen/qwen-2.5-7b-instruct': { name: 'qwen-2.5-7b', family: 'Qwen', scale: 'small', provider: 'OpenRouter' },
  'qwen/qwen-2.5-72b-instruct': { name: 'qwen-2.5-72b', family: 'Qwen', scale: 'large', provider: 'OpenRouter' },
};

// Task ID extraction: "B1_masked_majority" -> "B1"
function taskId(fullTask: string): string {
  return fullTask.split('_')[0];
}

// Phase mapping for display
const PHASE_DISPLAY: Record<string, { label: string; number: number }> = {
  'research': { label: 'Phase 1 — Research', number: 1 },
  'literature-review': { label: 'Phase 1 — Literature Review', number: 1 },
  'framework': { label: 'Phase 2 — Framework', number: 2 },
  'benchmark-design': { label: 'Phase 3 — Benchmark Design', number: 3 },
  'analysis-infra': { label: 'Phase 4 — Analysis Infra', number: 4 },
  'empirical-evaluation': { label: 'Phase 5 — Evaluation', number: 5 },
  'paper-writing': { label: 'Phase 6 — Paper Writing', number: 6 },
  'submission': { label: 'Phase 7 — Submission', number: 7 },
};

const REASONING_GAPS_PHASES = [
  'Literature Review', 'Framework', 'Benchmark Design',
  'Analysis Infra', 'Evaluation', 'Paper Writing', 'Submission',
];

const AGENT_TAXONOMY_PHASES = [
  'Literature Review', 'Taxonomy Design', 'Data Collection', 'Analysis', 'Paper',
];

function buildPhases(projectId: string, currentPhase: string): Array<{ name: string; status: 'complete' | 'active' | 'pending' }> {
  const phaseInfo = PHASE_DISPLAY[currentPhase];
  const currentNum = phaseInfo?.number ?? 1;
  const phaseNames = projectId === 'reasoning-gaps' ? REASONING_GAPS_PHASES : AGENT_TAXONOMY_PHASES;

  return phaseNames.map((name, i) => ({
    name,
    status: (i + 1) < currentNum ? 'complete' as const
      : (i + 1) === currentNum ? 'active' as const
      : 'pending' as const,
  }));
}

// ============================================================
// Public fetch functions
// ============================================================

interface ApiProject {
  id: string;
  name: string;
  title: string;
  venue: string;
  phase: string;
  status: string;
  confidence: number;
  current_focus: string | null;
  current_activity: string | null;
  branch: string;
  updated_at: string;
}

interface ApiProgressRow {
  model: string;
  task: string;
  condition: string;
  completed_count: string;
  correct_count: string;
  accuracy: string;
  avg_latency_ms: string;
  last_updated: string;
}

interface ApiEvalRun {
  run_id: string;
  model: string;
  task: string;
  condition: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  accuracy: number | null;
  instance_count: number;
}

interface ApiDecision {
  id: number;
  project: string;
  date: string;
  decision: string;
  rationale: string;
}

interface ApiBudget {
  daily: { daily_total: number };
  monthly: { monthly_total: number };
  byProject: Array<{ project: string; cost_usd: number }>;
  byModel: Array<{ model: string; cost_usd: number }>;
  burnRate: Array<{ day: string; total: number }>;
  limits: { daily_usd: number; monthly_usd: number };
}

export async function fetchProjects(): Promise<Project[]> {
  const apiProjects = await apiFetch<ApiProject[]>('/api/projects');

  // Also fetch eval status to compute progress
  const evalPromises = apiProjects.map(async (p) => {
    try {
      const eval_ = await apiFetch<{ progress: ApiProgressRow[]; runs: ApiEvalRun[] }>(`/api/projects/${p.id}/eval`);
      return { id: p.id, eval: eval_ };
    } catch {
      return { id: p.id, eval: null };
    }
  });
  const evalResults = await Promise.all(evalPromises);
  const evalMap = new Map(evalResults.map(e => [e.id, e.eval]));

  // Fetch eval job status for running info
  let evalStatus: { runningJobs: Array<{ model: string }> } = { runningJobs: [] };
  try {
    evalStatus = await apiFetch('/api/eval/status');
  } catch { /* ignore */ }

  return apiProjects.map((p): Project => {
    const phaseInfo = PHASE_DISPLAY[p.phase] ?? { label: `Phase — ${p.phase}`, number: 1 };
    const phases = buildPhases(p.id, p.phase);
    const eval_ = evalMap.get(p.id);

    // Count models and tasks from progress data
    const models = new Set<string>();
    const tasksComplete = new Set<string>();
    let totalInstances = 0;
    if (eval_) {
      for (const row of eval_.progress) {
        models.add(row.model);
        tasksComplete.add(`${row.model}_${row.task}_${row.condition}`);
        totalInstances += parseInt(row.completed_count, 10);
      }
    }

    const status = p.status === 'active'
      ? (evalStatus.runningJobs.length > 0 ? 'running' : 'idle')
      : p.status === 'paused' ? 'paused' : 'idle';

    const modelsTotal = p.id === 'reasoning-gaps' ? 12 : 0;
    const tasksTotal = modelsTotal * 27; // 9 tasks × 3 conditions

    return {
      name: p.id,
      title: p.title,
      venue: p.venue ?? '',
      phase: phaseInfo.label,
      phaseNumber: phaseInfo.number,
      totalPhases: phases.length,
      phases,
      status: status as Project['status'],
      lastActivity: p.updated_at,
      description: p.current_focus ?? '',
      modelsCompleted: models.size,
      modelsTotal,
      tasksCompleted: tasksComplete.size,
      tasksTotal,
      completionPct: tasksTotal > 0 ? Math.round((tasksComplete.size / tasksTotal) * 100) : 0,
    };
  });
}

export async function fetchEvalData(projectId: string): Promise<ProjectEvalData | null> {
  try {
    const data = await apiFetch<{ progress: ApiProgressRow[]; runs: ApiEvalRun[] }>(`/api/projects/${projectId}/eval`);
    if (!data.progress.length) return null;

    // Group by model, then by task
    const modelMap = new Map<string, Map<string, { direct: number | null; cot: number | null }>>();

    for (const row of data.progress) {
      const tid = taskId(row.task);
      if (!modelMap.has(row.model)) modelMap.set(row.model, new Map());
      const taskMap = modelMap.get(row.model)!;
      if (!taskMap.has(tid)) taskMap.set(tid, { direct: null, cot: null });
      const entry = taskMap.get(tid)!;
      const acc = Math.round(parseFloat(row.accuracy) * 100);
      if (row.condition === 'direct') entry.direct = acc;
      if (row.condition === 'short_cot') entry.cot = acc;
    }

    const models: ModelData[] = [];
    for (const [modelName, taskMap] of modelMap) {
      const display = MODEL_DISPLAY[modelName] ?? {
        name: modelName.split('/').pop() ?? modelName,
        family: 'Unknown',
        scale: 'large' as const,
        provider: 'Unknown',
      };

      const results: Record<string, { direct: number | null; cot: number | null }> = {};
      for (const task of evalTasks) {
        results[task.id] = taskMap.get(task.id) ?? { direct: null, cot: null };
      }

      models.push({ ...display, results });
    }

    // Sort: Claude first, then GPT, then alphabetical
    const familyOrder = ['Claude', 'GPT', 'Llama', 'Mistral', 'Qwen'];
    models.sort((a, b) => {
      const ai = familyOrder.indexOf(a.family);
      const bi = familyOrder.indexOf(b.family);
      if (ai !== bi) return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
      return a.scale === 'small' ? -1 : 1;
    });

    // Total instances
    let totalInstances = 0;
    for (const row of data.progress) {
      totalInstances += parseInt(row.completed_count, 10);
    }

    // Running models
    const runningRuns = data.runs.filter(r => r.status === 'running');
    const runningNow = [...new Set(runningRuns.map(r => {
      const d = MODEL_DISPLAY[r.model];
      return d?.name ?? r.model;
    }))];

    return { models, tasks: evalTasks, totalInstances, runningNow };
  } catch {
    return null;
  }
}

export async function fetchBudgetData(projectId: string): Promise<ProjectBudgetData> {
  try {
    const data = await apiFetch<ApiBudget>('/api/budget');

    const providers = new Map<string, { spent: number; models: Map<string, number> }>();
    for (const row of data.byModel) {
      const display = MODEL_DISPLAY[row.model];
      const providerName = display?.provider ?? 'Unknown';
      if (!providers.has(providerName)) providers.set(providerName, { spent: 0, models: new Map() });
      const p = providers.get(providerName)!;
      p.spent += row.cost_usd;
      p.models.set(display?.name ?? row.model, row.cost_usd);
    }

    return {
      monthlyLimit: data.limits.monthly_usd,
      dailyLimit: data.limits.daily_usd,
      providers: Array.from(providers.entries()).map(([name, p]) => ({
        name,
        spent: p.spent,
        limit: name === 'Anthropic' ? 200 : name === 'OpenAI' ? 100 : 50,
        models: Array.from(p.models.entries()).map(([mname, cost]) => ({
          name: mname,
          calls: 0,
          tokens: '—',
          cost,
        })),
      })),
      dailySpend: data.burnRate.map(r => ({
        date: r.day.slice(5),
        amount: r.total,
      })),
    };
  } catch {
    return { monthlyLimit: 1000, dailyLimit: 40, providers: [], dailySpend: [] };
  }
}

export async function fetchDecisions(projectId?: string): Promise<Decision[]> {
  try {
    if (projectId) {
      const rows = await apiFetch<ApiDecision[]>(`/api/projects/${projectId}/decisions`);
      return rows.map(r => ({
        date: r.date,
        project: r.project,
        decision: r.decision,
        rationale: r.rationale ?? '',
      }));
    }
    // For all projects, fetch each
    const projects = await apiFetch<ApiProject[]>('/api/projects');
    const all: Decision[] = [];
    for (const p of projects) {
      const rows = await apiFetch<ApiDecision[]>(`/api/projects/${p.id}/decisions`);
      all.push(...rows.map(r => ({
        date: r.date,
        project: r.project,
        decision: r.decision,
        rationale: r.rationale ?? '',
      })));
    }
    all.sort((a, b) => b.date.localeCompare(a.date));
    return all;
  } catch {
    return [];
  }
}

export async function fetchHealth(): Promise<Record<string, string>> {
  try {
    const data = await apiFetch<{ status: string; database: string; memory: { percent_used: number } }>('/api/health');
    return {
      orchestrator: data.status === 'ok' ? 'operational' : 'degraded',
      database: data.database === 'connected' ? 'operational' : 'error',
      memory: `${data.memory.percent_used}% used`,
    };
  } catch {
    return { orchestrator: 'unreachable' };
  }
}

export async function fetchAggregateStats(): Promise<{
  totalProjects: number;
  activeSessions: number;
  papersInPipeline: number;
  monthlySpend: number;
  monthlyBudget: number;
}> {
  try {
    const [projects, budget] = await Promise.all([
      apiFetch<ApiProject[]>('/api/projects'),
      apiFetch<ApiBudget>('/api/budget'),
    ]);

    return {
      totalProjects: projects.length,
      activeSessions: 0,
      papersInPipeline: projects.filter(p => p.status === 'active').length,
      monthlySpend: budget.monthly.monthly_total,
      monthlyBudget: budget.limits.monthly_usd,
    };
  } catch {
    return { totalProjects: 0, activeSessions: 0, papersInPipeline: 0, monthlySpend: 0, monthlyBudget: 1000 };
  }
}
