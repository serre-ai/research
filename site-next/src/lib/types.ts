export interface Project {
  id: string;
  name: string;
  status: string;
  phase: string;
  focus?: string;
  confidence?: number;
  branch?: string;
  created_at: string;
  updated_at: string;
}

export interface EvalData {
  project_id: string;
  runs: EvalRun[];
  accuracy: Record<string, Record<string, number>>;
  progress: {
    total: number;
    completed: number;
    failed: number;
  };
}

export interface EvalRun {
  id: string;
  model: string;
  task: string;
  condition: string;
  instances: number;
  accuracy: number;
  created_at: string;
}

export interface Budget {
  month: string;
  variable_costs: {
    total: number;
    by_provider: Record<string, number>;
  };
  fixed_costs: {
    total: number;
    items: { name: string; amount: number }[];
  };
  total: number;
  daily_limit: number;
  burn_rate: number;
  projected_monthly: number;
  remaining: number;
}

export interface Decision {
  date: string;
  decision: string;
  rationale: string;
  project_id: string;
}

export interface Session {
  id: string;
  project_id: string;
  agent_type: string;
  status: string;
  started_at: string;
  ended_at?: string;
  duration_seconds?: number;
  token_usage?: number;
  cost?: number;
}

export interface HealthStatus {
  status: string;
  uptime: number;
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  database: {
    connected: boolean;
    latency_ms: number;
  };
}

export interface DaemonHealth {
  status: string;
  running: boolean;
  last_session?: string;
  interval_minutes: number;
  max_concurrent: number;
}

export interface ActivityItem {
  id: string;
  type: string;
  project_id?: string;
  message: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}
