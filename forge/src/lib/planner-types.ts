export interface PlannerState {
  enabled: boolean;
  last_run?: string;
}

export interface ProjectInsight {
  project: string;
  insights: unknown;
  recommendations: string[];
}

export interface PlannerEvaluation {
  id: string;
  project?: string;
  type: string;
  result: unknown;
  created_at: string;
}
