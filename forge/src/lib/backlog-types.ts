export type TicketPriority = 'low' | 'medium' | 'high' | 'critical';
export type TicketCategory = 'daemon' | 'api' | 'agents' | 'eval' | 'infra' | 'other';
export type TicketStatus = 'open' | 'in_progress' | 'done' | 'wont_fix';

export interface BacklogTicket {
  id: string;
  title: string;
  description?: string;
  filed_by: string;
  priority: TicketPriority;
  category: TicketCategory;
  status: TicketStatus;
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  session_id?: string;
}

export interface CreateTicketRequest {
  title: string;
  filed_by: string;
  priority: TicketPriority;
  category: TicketCategory;
  description?: string;
}

export interface UpdateTicketRequest {
  status?: TicketStatus;
  priority?: TicketPriority;
  assigned_to?: string;
  session_id?: string;
}
