// Event System

export interface DeadLetter {
  id: string;
  event_type: string;
  payload: Record<string, unknown>;
  error: string;
  attempts: number;
  created_at: string;
  last_attempt_at: string;
}
