export type TriggerType =
  | 'forum:unanimous_support'
  | 'forum:stalled'
  | 'governance:proposed'
  | 'ritual:scheduled'
  | 'forum:mention';

export interface Trigger {
  id: number;
  agent: string;
  trigger_type: TriggerType;
  context: Record<string, unknown>;
}
