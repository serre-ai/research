export type MessagePriority = 'normal' | 'urgent';

export interface Message {
  id: number;
  from_agent: string;
  to_agent: string;
  subject: string;
  body: string;
  priority: MessagePriority;
  read_at: string | null;
  created_at: string;
}

export interface Mention {
  source: 'forum' | 'message';
  id: number;
  thread_id: string;
  author: string;
  body: string;
  created_at: string;
}

export interface MessageStats {
  sent: number;
  received: number;
  unread: number;
  urgent_unread: number;
}

export interface SendMessageRequest {
  from_agent: string;
  to_agent: string;
  subject: string;
  body: string;
  priority?: MessagePriority;
}
