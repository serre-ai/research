import { readFile, writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";

export interface BacklogTicket {
  id: string;
  title: string;
  description?: string;
  filed_by: string;
  priority: "low" | "medium" | "high" | "critical";
  category: "daemon" | "api" | "agents" | "eval" | "infra" | "other";
  status: "open" | "in_progress" | "done" | "wont_fix";
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  session_id?: string;
}

export class BacklogManager {
  private readonly filePath: string;
  private dirCreated = false;

  constructor(rootDir: string) {
    this.filePath = join(rootDir, ".logs", "backlog.json");
  }

  async list(filters?: {
    status?: string;
    priority?: string;
    category?: string;
  }): Promise<BacklogTicket[]> {
    let tickets = await this.read();

    if (filters?.status) {
      tickets = tickets.filter((t) => t.status === filters.status);
    }
    if (filters?.priority) {
      tickets = tickets.filter((t) => t.priority === filters.priority);
    }
    if (filters?.category) {
      tickets = tickets.filter((t) => t.category === filters.category);
    }

    // Sort: critical > high > medium > low, then by created_at desc
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    tickets.sort((a, b) => {
      const pDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      if (pDiff !== 0) return pDiff;
      return b.created_at.localeCompare(a.created_at);
    });

    return tickets;
  }

  async create(
    ticket: Pick<BacklogTicket, "title" | "filed_by" | "priority" | "category"> &
      Partial<Pick<BacklogTicket, "description">>,
  ): Promise<BacklogTicket> {
    const tickets = await this.read();
    const now = new Date().toISOString();
    const newTicket: BacklogTicket = {
      id: randomUUID().slice(0, 8),
      title: ticket.title,
      description: ticket.description,
      filed_by: ticket.filed_by,
      priority: ticket.priority,
      category: ticket.category,
      status: "open",
      created_at: now,
      updated_at: now,
    };
    tickets.push(newTicket);
    await this.write(tickets);
    return newTicket;
  }

  async update(
    id: string,
    updates: Partial<Pick<BacklogTicket, "status" | "priority" | "assigned_to" | "session_id">>,
  ): Promise<BacklogTicket | null> {
    const tickets = await this.read();
    const ticket = tickets.find((t) => t.id === id);
    if (!ticket) return null;

    if (updates.status) ticket.status = updates.status;
    if (updates.priority) ticket.priority = updates.priority;
    if (updates.assigned_to) ticket.assigned_to = updates.assigned_to;
    if (updates.session_id) ticket.session_id = updates.session_id;
    ticket.updated_at = new Date().toISOString();

    await this.write(tickets);
    return ticket;
  }

  async get(id: string): Promise<BacklogTicket | null> {
    const tickets = await this.read();
    return tickets.find((t) => t.id === id) ?? null;
  }

  private async read(): Promise<BacklogTicket[]> {
    try {
      const content = await readFile(this.filePath, "utf-8");
      return JSON.parse(content) as BacklogTicket[];
    } catch {
      return [];
    }
  }

  private async write(tickets: BacklogTicket[]): Promise<void> {
    await this.ensureDir();
    await writeFile(this.filePath, JSON.stringify(tickets, null, 2), "utf-8");
  }

  private async ensureDir(): Promise<void> {
    if (this.dirCreated) return;
    const dir = join(this.filePath, "..");
    await mkdir(dir, { recursive: true });
    this.dirCreated = true;
  }
}
