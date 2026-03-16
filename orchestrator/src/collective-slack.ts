// ============================================================
// Collective Slack — cross-post forum/governance outcomes to Slack
// ============================================================

interface SlackMessage {
  channel: string;
  text: string;
  blocks?: unknown[];
}

export class CollectiveSlack {
  private token: string | undefined;
  private enabled: boolean;

  constructor() {
    this.token = process.env.SLACK_BOT_TOKEN;
    this.enabled = !!this.token;
  }

  private async post(msg: SlackMessage): Promise<void> {
    if (!this.enabled || !this.token) return;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
      await fetch("https://slack.com/api/chat.postMessage", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(msg),
        signal: controller.signal,
      });
    } catch (err) {
      // Fire-and-forget — log but don't throw
      console.error("Slack cross-post failed:", err instanceof Error ? err.message : err);
    } finally {
      clearTimeout(timeout);
    }
  }

  async crossPostForumResolution(thread: {
    thread_id: string;
    title: string;
    status: string;
    author?: string;
  }): Promise<void> {
    await this.post({
      channel: "#general",
      text: `Forum thread resolved: *${thread.title}* (thread #${thread.thread_id}) — status: ${thread.status}`,
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `:white_check_mark: *Forum Thread Resolved*\n*${thread.title}*\nThread #${thread.thread_id} | Status: ${thread.status}${thread.author ? ` | Author: ${thread.author}` : ""}`,
          },
        },
      ],
    });
  }

  async crossPostSynthesis(thread: {
    thread_id: string;
    title: string;
    synthesizer: string;
    summary: string;
  }): Promise<void> {
    const truncated = thread.summary.length > 300
      ? thread.summary.slice(0, 300) + "…"
      : thread.summary;

    await this.post({
      channel: "#debate",
      text: `Synthesis posted for "${thread.title}" by ${thread.synthesizer}`,
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `:bulb: *Synthesis* — ${thread.title}\nBy *${thread.synthesizer}* | Thread #${thread.thread_id}\n\n>${truncated.replace(/\n/g, "\n>")}`,
          },
        },
      ],
    });
  }

  async crossPostGovernanceOutcome(proposal: {
    id: number;
    title: string;
    status: string;
    votes_for: number;
    votes_against: number;
    votes_abstain: number;
  }): Promise<void> {
    const emoji = proposal.status === "accepted" ? ":ballot_box_with_check:" : ":x:";

    await this.post({
      channel: "#deliberation",
      text: `Governance proposal ${proposal.status}: "${proposal.title}"`,
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `${emoji} *Governance Proposal ${proposal.status.toUpperCase()}*\n*${proposal.title}*\nVotes: ${proposal.votes_for} for / ${proposal.votes_against} against / ${proposal.votes_abstain} abstain`,
          },
        },
      ],
    });
  }
}
