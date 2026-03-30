export type RitualType = 'standup' | 'retrospective' | 'pre_mortem' | 'reading_club' | 'calibration_review' | 'values_review';
export type RitualStatus = 'scheduled' | 'active' | 'completed' | 'cancelled';

export interface Ritual {
  id: number;
  ritual_type: RitualType;
  scheduled_for: string;
  facilitator: string;
  participants: string[];
  status: RitualStatus;
  thread_id: string;
  outcome: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}
