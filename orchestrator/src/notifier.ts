import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { parse } from "./yaml.js";

export interface NotificationPayload {
  event: string;
  project?: string;
  summary: string;
  details?: Record<string, unknown>;
  level?: "info" | "warning" | "error";
}

export class Notifier {
  private webhookUrl: string | null = null;
  private initialized = false;
  private rootDir: string;

  constructor(rootDir: string) {
    this.rootDir = rootDir;
  }

  async notify(payload: NotificationPayload): Promise<void> {
    try {
      const url = await this.getWebhookUrl();
      if (!url) return;

      const icon =
        payload.level === "error"
          ? ":red_circle:"
          : payload.level === "warning"
            ? ":warning:"
            : ":large_blue_circle:";

      const projectTag = payload.project ? ` [${payload.project}]` : "";
      const text = `${icon} *${payload.event}*${projectTag}\n${payload.summary}`;

      const body: Record<string, unknown> = { text };

      if (payload.details) {
        body.blocks = [
          {
            type: "section",
            text: { type: "mrkdwn", text },
          },
          {
            type: "context",
            elements: [
              {
                type: "mrkdwn",
                text: Object.entries(payload.details)
                  .map(([k, v]) => `*${k}*: ${v}`)
                  .join(" | "),
              },
            ],
          },
        ];
      }

      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);
      await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      clearTimeout(timeout);
    } catch {
      // Fire-and-forget: never throw
      console.error(`[notifier] Failed to send: ${payload.event}`);
    }
  }

  private async getWebhookUrl(): Promise<string | null> {
    if (this.initialized) return this.webhookUrl;
    this.initialized = true;

    if (process.env.NOTIFICATION_WEBHOOK_URL) {
      this.webhookUrl = process.env.NOTIFICATION_WEBHOOK_URL;
      return this.webhookUrl;
    }

    try {
      const configText = await readFile(
        join(this.rootDir, "config.yaml"),
        "utf-8",
      );
      const config = parse(configText);
      const notifications = config.notifications as
        | { webhook_url?: string }
        | undefined;
      this.webhookUrl = notifications?.webhook_url ?? null;
    } catch {
      this.webhookUrl = null;
    }

    return this.webhookUrl;
  }
}
