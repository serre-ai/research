// Paper Build

export type BuildStatus = 'idle' | 'running' | 'success' | 'failed';

export interface PaperBuildStatus {
  status: BuildStatus;
  started_at: string | null;
  finished_at: string | null;
  project: string | null;
  error: string | null;
  duration_ms: number | null;
}

export interface PaperBuildRequest {
  project?: string;
  skipAnalysis?: boolean;
  skipCompile?: boolean;
}
