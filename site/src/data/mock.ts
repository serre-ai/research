// Mock data — will be replaced with VPS API calls

export interface Project {
  name: string;
  title: string;
  venue: string;
  phase: string;
  phaseNumber: number;
  totalPhases: number;
  phases: Array<{ name: string; status: 'complete' | 'active' | 'pending' }>;
  status: 'running' | 'paused' | 'error' | 'idle';
  lastActivity: string;
  description: string;
  modelsCompleted: number;
  modelsTotal: number;
  tasksCompleted: number;
  tasksTotal: number;
  completionPct: number;
}

export const projects: Project[] = [
  {
    name: 'reasoning-gaps',
    title: 'On the Reasoning Gaps of LLMs',
    venue: 'NeurIPS 2026',
    phase: 'Phase 5 — Evaluation',
    phaseNumber: 5,
    totalPhases: 7,
    phases: [
      { name: 'Literature Review', status: 'complete' },
      { name: 'Framework', status: 'complete' },
      { name: 'Benchmark Design', status: 'complete' },
      { name: 'Analysis Infra', status: 'complete' },
      { name: 'Evaluation', status: 'active' },
      { name: 'Paper Writing', status: 'active' },
      { name: 'Submission', status: 'pending' },
    ],
    status: 'running',
    lastActivity: '2026-03-11T16:30:00Z',
    description: 'Formal characterization of reasoning limitations in LLMs bridging computational complexity theory with empirical evaluation.',
    modelsCompleted: 9,
    modelsTotal: 12,
    tasksCompleted: 265,
    tasksTotal: 297,
    completionPct: 89,
  },
  {
    name: 'agent-failure-taxonomy',
    title: 'Taxonomy of LLM Agent Failures',
    venue: 'ACL 2027',
    phase: 'Phase 1 — Literature Review',
    phaseNumber: 1,
    totalPhases: 5,
    phases: [
      { name: 'Literature Review', status: 'active' },
      { name: 'Taxonomy Design', status: 'pending' },
      { name: 'Data Collection', status: 'pending' },
      { name: 'Analysis', status: 'pending' },
      { name: 'Paper', status: 'pending' },
    ],
    status: 'paused',
    lastActivity: '2026-03-09T14:20:00Z',
    description: 'Systematic taxonomy of failure modes in LLM-based autonomous agents across tool use, planning, and multi-step reasoning.',
    modelsCompleted: 0,
    modelsTotal: 0,
    tasksCompleted: 0,
    tasksTotal: 0,
    completionPct: 0,
  },
];

export function getProject(name: string): Project | undefined {
  return projects.find(p => p.name === name);
}

// Eval data

export interface EvalTask {
  id: string;
  label: string;
  gapType: string;
}

export const evalTasks: EvalTask[] = [
  { id: 'B1', label: 'Modus Tollens', gapType: 'Propositional Logic' },
  { id: 'B2', label: 'Syllogistic', gapType: 'Categorical Reasoning' },
  { id: 'B3', label: 'Temporal Ordering', gapType: 'Temporal Logic' },
  { id: 'B4', label: 'Spatial Rotation', gapType: 'Spatial Reasoning' },
  { id: 'B5', label: 'Counting', gapType: 'Arithmetic' },
  { id: 'B6', label: 'Set Membership', gapType: 'Set Theory' },
  { id: 'B7', label: 'Recursive Depth', gapType: 'Recursion' },
  { id: 'B8', label: 'Pattern Matching', gapType: 'Induction' },
  { id: 'B9', label: 'Compositional', gapType: 'Compositionality' },
];

export interface ModelData {
  name: string;
  family: string;
  scale: 'small' | 'large';
  provider: string;
  results: Record<string, { direct: number | null; cot: number | null }>;
}

export interface ProjectEvalData {
  models: ModelData[];
  tasks: EvalTask[];
  totalInstances: number;
  runningNow: string[];
}

const reasoningGapsModels: ModelData[] = [
  {
    name: 'haiku-4.5',
    family: 'Claude',
    scale: 'small',
    provider: 'Anthropic',
    results: {
      B1: { direct: 59, cot: 81 },
      B2: { direct: 53, cot: 93 },
      B3: { direct: 16, cot: 93 },
      B4: { direct: 35, cot: 89 },
      B5: { direct: 75, cot: 100 },
      B6: { direct: 24, cot: 50 },
      B7: { direct: 10, cot: 70 },
      B8: { direct: 99, cot: 100 },
      B9: { direct: 53, cot: 95 },
    },
  },
  {
    name: 'gpt-4o-mini',
    family: 'GPT',
    scale: 'small',
    provider: 'OpenAI',
    results: {
      B1: { direct: 61, cot: 78 },
      B2: { direct: 76, cot: 87 },
      B3: { direct: 21, cot: 81 },
      B4: { direct: 46, cot: 64 },
      B5: { direct: 77, cot: 79 },
      B6: { direct: 28, cot: 31 },
      B7: { direct: 15, cot: 55 },
      B8: { direct: 95, cot: 98 },
      B9: { direct: 48, cot: 72 },
    },
  },
  {
    name: 'gpt-4o',
    family: 'GPT',
    scale: 'large',
    provider: 'OpenAI',
    results: {
      B1: { direct: 72, cot: 89 },
      B2: { direct: 81, cot: 95 },
      B3: { direct: 34, cot: 91 },
      B4: { direct: 58, cot: 82 },
      B5: { direct: 85, cot: 93 },
      B6: { direct: 35, cot: 58 },
      B7: { direct: 22, cot: 72 },
      B8: { direct: 98, cot: 100 },
      B9: { direct: 61, cot: 88 },
    },
  },
  {
    name: 'llama-3.1-8b',
    family: 'Llama',
    scale: 'small',
    provider: 'OpenRouter',
    results: {
      B1: { direct: 45, cot: 62 },
      B2: { direct: 38, cot: 71 },
      B3: { direct: 12, cot: 58 },
      B4: { direct: 22, cot: 41 },
      B5: { direct: 55, cot: 65 },
      B6: { direct: 15, cot: 22 },
      B7: { direct: 8, cot: 35 },
      B8: { direct: 82, cot: 90 },
      B9: { direct: 30, cot: 55 },
    },
  },
  {
    name: 'llama-3.1-70b',
    family: 'Llama',
    scale: 'large',
    provider: 'OpenRouter',
    results: {
      B1: { direct: 65, cot: 83 },
      B2: { direct: 72, cot: 91 },
      B3: { direct: 28, cot: 85 },
      B4: { direct: 50, cot: 75 },
      B5: { direct: 80, cot: 90 },
      B6: { direct: 30, cot: 48 },
      B7: { direct: 18, cot: 62 },
      B8: { direct: 96, cot: 99 },
      B9: { direct: 55, cot: 82 },
    },
  },
  {
    name: 'ministral-8b',
    family: 'Mistral',
    scale: 'small',
    provider: 'OpenRouter',
    results: {
      B1: { direct: 42, cot: 58 },
      B2: { direct: 35, cot: 65 },
      B3: { direct: 10, cot: 52 },
      B4: { direct: 20, cot: 38 },
      B5: { direct: 50, cot: 60 },
      B6: { direct: 12, cot: 20 },
      B7: { direct: 6, cot: 30 },
      B8: { direct: 78, cot: 88 },
      B9: { direct: 28, cot: 50 },
    },
  },
  {
    name: 'mistral-small-24b',
    family: 'Mistral',
    scale: 'large',
    provider: 'OpenRouter',
    results: {
      B1: { direct: 58, cot: 76 },
      B2: { direct: 62, cot: 84 },
      B3: { direct: 22, cot: 78 },
      B4: { direct: 42, cot: 68 },
      B5: { direct: 72, cot: 85 },
      B6: { direct: 25, cot: 42 },
      B7: { direct: 14, cot: 55 },
      B8: { direct: 92, cot: 97 },
      B9: { direct: 48, cot: 75 },
    },
  },
  {
    name: 'qwen-2.5-7b',
    family: 'Qwen',
    scale: 'small',
    provider: 'OpenRouter',
    results: {
      B1: { direct: 48, cot: 65 },
      B2: { direct: 40, cot: 72 },
      B3: { direct: 14, cot: 60 },
      B4: { direct: 25, cot: 45 },
      B5: { direct: 58, cot: 68 },
      B6: { direct: 18, cot: 25 },
      B7: { direct: 9, cot: 38 },
      B8: { direct: 85, cot: 92 },
      B9: { direct: 32, cot: 58 },
    },
  },
  {
    name: 'qwen-2.5-72b',
    family: 'Qwen',
    scale: 'large',
    provider: 'OpenRouter',
    results: {
      B1: { direct: 68, cot: 85 },
      B2: { direct: 75, cot: 92 },
      B3: { direct: 30, cot: 88 },
      B4: { direct: 52, cot: 78 },
      B5: { direct: 82, cot: 91 },
      B6: { direct: 32, cot: 52 },
      B7: { direct: 20, cot: 65 },
      B8: { direct: 97, cot: 99 },
      B9: { direct: 58, cot: 85 },
    },
  },
  {
    name: 'sonnet-4',
    family: 'Claude',
    scale: 'large',
    provider: 'Anthropic',
    results: {
      B1: { direct: 71, cot: 88 },
      B2: { direct: 79, cot: 96 },
      B3: { direct: 32, cot: 94 },
      B4: { direct: 55, cot: 90 },
      B5: { direct: 83, cot: 98 },
      B6: { direct: null, cot: null },
      B7: { direct: null, cot: null },
      B8: { direct: null, cot: null },
      B9: { direct: null, cot: null },
    },
  },
  {
    name: 'o3',
    family: 'GPT',
    scale: 'large',
    provider: 'OpenAI',
    results: {
      B1: { direct: 78, cot: 92 },
      B2: { direct: 85, cot: 97 },
      B3: { direct: 40, cot: 95 },
      B4: { direct: 62, cot: null },
      B5: { direct: null, cot: null },
      B6: { direct: null, cot: null },
      B7: { direct: null, cot: null },
      B8: { direct: null, cot: null },
      B9: { direct: null, cot: null },
    },
  },
];

export const evalData: Record<string, ProjectEvalData> = {
  'reasoning-gaps': {
    models: reasoningGapsModels,
    tasks: evalTasks,
    totalInstances: 121614,
    runningNow: ['sonnet-4', 'o3'],
  },
};

// Budget data

export interface ProviderBudget {
  name: string;
  spent: number;
  limit: number;
  models: Array<{ name: string; calls: number; tokens: string; cost: number }>;
}

export interface ProjectBudgetData {
  monthlyLimit: number;
  dailyLimit: number;
  providers: ProviderBudget[];
  dailySpend: Array<{ date: string; amount: number }>;
}

export const budgetData: Record<string, ProjectBudgetData> = {
  'reasoning-gaps': {
    monthlyLimit: 1000,
    dailyLimit: 40,
    providers: [
      {
        name: 'Anthropic',
        spent: 15.42,
        limit: 200,
        models: [
          { name: 'haiku-4.5', calls: 2700, tokens: '8.1M', cost: 12.30 },
          { name: 'sonnet-4', calls: 450, tokens: '2.1M', cost: 3.12 },
        ],
      },
      {
        name: 'OpenAI',
        spent: 59.80,
        limit: 100,
        models: [
          { name: 'gpt-4o-mini', calls: 1800, tokens: '5.4M', cost: 8.60 },
          { name: 'gpt-4o', calls: 120, tokens: '1.2M', cost: 51.20 },
        ],
      },
      {
        name: 'OpenRouter',
        spent: 0.22,
        limit: 50,
        models: [
          { name: 'llama-3.1-8b', calls: 2700, tokens: '4.2M', cost: 0.04 },
          { name: 'llama-3.1-70b', calls: 2700, tokens: '6.8M', cost: 0.04 },
          { name: 'ministral-8b', calls: 2700, tokens: '3.9M', cost: 0.03 },
          { name: 'mistral-small-24b', calls: 2700, tokens: '5.5M', cost: 0.03 },
          { name: 'qwen-2.5-7b', calls: 2700, tokens: '4.0M', cost: 0.04 },
          { name: 'qwen-2.5-72b', calls: 2700, tokens: '7.1M', cost: 0.04 },
        ],
      },
    ],
    dailySpend: [
      { date: '03-05', amount: 4.20 },
      { date: '03-06', amount: 6.80 },
      { date: '03-07', amount: 8.10 },
      { date: '03-08', amount: 12.50 },
      { date: '03-09', amount: 9.30 },
      { date: '03-10', amount: 22.40 },
      { date: '03-11', amount: 12.14 },
    ],
  },
  'agent-failure-taxonomy': {
    monthlyLimit: 1000,
    dailyLimit: 40,
    providers: [],
    dailySpend: [],
  },
};

// Decisions

export interface Decision {
  date: string;
  project: string;
  decision: string;
  rationale: string;
}

export const decisions: Decision[] = [
  {
    date: '2026-03-11',
    project: 'reasoning-gaps',
    decision: 'Run Sonnet 4 and o3 evaluations; defer Opus 4.6',
    rationale: 'Sonnet 4 + o3 ($95 combined) provide more marginal value than Opus alone ($272). Two diverse additions better than one expensive one.',
  },
  {
    date: '2026-03-11',
    project: 'reasoning-gaps',
    decision: 'Switch to autonomous decision workflow',
    rationale: 'Human-in-the-loop bottleneck slowing evaluation progress. All decisions logged in status.yaml.',
  },
  {
    date: '2026-03-11',
    project: 'reasoning-gaps',
    decision: 'Deploy VPS infrastructure for 24/7 operation',
    rationale: 'Remote-first enables daemon, API, PostgreSQL running independently of laptop.',
  },
  {
    date: '2026-03-10',
    project: 'reasoning-gaps',
    decision: 'Run Haiku 4.5 and GPT-4o-mini in parallel',
    rationale: 'Both APIs have sufficient rate limits. Maximize throughput across providers.',
  },
  {
    date: '2026-03-10',
    project: 'reasoning-gaps',
    decision: 'Use 100 instances per task-model-strategy combination',
    rationale: 'Balances statistical significance with budget constraints.',
  },
  {
    date: '2026-03-09',
    project: 'agent-failure-taxonomy',
    decision: 'Target ACL 2027 as venue',
    rationale: 'NLP-focused venue, good fit for agent failure analysis. Deadline provides sufficient runway.',
  },
];

export function getDecisions(projectName?: string): Decision[] {
  if (!projectName) return decisions;
  return decisions.filter(d => d.project === projectName);
}

// System health

export const systemHealth: Record<string, string> = {
  orchestrator: 'operational',
  anthropicApi: 'operational',
  openaiApi: 'operational',
  openrouterApi: 'operational',
  gitSync: 'ok',
  budgetRemaining: '$917',
};

// Aggregate stats
export const aggregateStats = {
  totalProjects: projects.length,
  activeSessions: 3,
  papersInPipeline: 2,
  monthlySpend: 83.44,
  monthlyBudget: 1000,
};
