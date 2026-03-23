/**
 * Thin Linear API client using raw GraphQL over fetch.
 * No SDK — matches codebase convention of minimal dependencies.
 */

import { retry } from "./utils/retry.js";

const LINEAR_API = "https://api.linear.app/graphql";

// ============================================================
// Types
// ============================================================

export interface LinearIssue {
  id: string;
  identifier: string; // e.g. "DW-42"
  title: string;
  description: string | null;
  priority: number; // 0=none, 1=urgent, 2=high, 3=medium, 4=low
  state: { id: string; name: string };
  labels: { nodes: { id: string; name: string }[] };
  project: { id: string; name: string } | null;
  assignee: { id: string; name: string } | null;
  cycle: { id: string; name: string; number: number } | null;
  url: string;
  createdAt: string;
  updatedAt: string;
}

export interface LinearCreateIssueInput {
  title: string;
  description?: string;
  teamId: string;
  projectId?: string;
  priority?: number;
  labelIds?: string[];
  cycleId?: string;
  stateId?: string;
}

export interface LinearTeamState {
  id: string;
  name: string;
  type: string; // "triage" | "backlog" | "unstarted" | "started" | "completed" | "canceled"
}

interface GraphQLResponse<T> {
  data?: T;
  errors?: { message: string }[];
}

// ============================================================
// Client
// ============================================================

export class LinearClient {
  private apiKey: string;
  private teamId: string;
  private stateCache: Map<string, LinearTeamState> | null = null;

  constructor(apiKey: string, teamId: string) {
    this.apiKey = apiKey;
    this.teamId = teamId;
  }

  // --------------------------------------------------------
  // Core GraphQL
  // --------------------------------------------------------

  private async query<T>(query: string, variables?: Record<string, unknown>): Promise<T> {
    return retry(async () => {
      const res = await fetch(LINEAR_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: this.apiKey,
        },
        body: JSON.stringify({ query, variables }),
      });

      if (!res.ok) {
        const error: Error & { status?: number } = new Error(`Linear API ${res.status}: ${await res.text()}`);
        error.status = res.status;
        throw error;
      }

      const json = (await res.json()) as GraphQLResponse<T>;
      if (json.errors?.length) {
        throw new Error(`Linear GraphQL: ${json.errors.map((e) => e.message).join(", ")}`);
      }
      if (!json.data) {
        throw new Error("Linear API returned no data");
      }
      return json.data;
    }, {
      maxAttempts: 3,
      initialDelayMs: 1000,
      maxDelayMs: 10000,
    });
  }

  // --------------------------------------------------------
  // Workflow states
  // --------------------------------------------------------

  async getStates(): Promise<LinearTeamState[]> {
    if (this.stateCache) return [...this.stateCache.values()];

    const data = await this.query<{
      team: { states: { nodes: LinearTeamState[] } };
    }>(
      `query($teamId: String!) {
        team(id: $teamId) {
          states { nodes { id name type } }
        }
      }`,
      { teamId: this.teamId },
    );

    this.stateCache = new Map();
    for (const state of data.team.states.nodes) {
      this.stateCache.set(state.name.toLowerCase(), state);
    }
    return data.team.states.nodes;
  }

  async getStateId(name: string): Promise<string | null> {
    await this.getStates();
    return this.stateCache?.get(name.toLowerCase())?.id ?? null;
  }

  // --------------------------------------------------------
  // Issue queries
  // --------------------------------------------------------

  private readonly ISSUE_FRAGMENT = `
    id identifier title description priority url createdAt updatedAt
    state { id name }
    labels { nodes { id name } }
    project { id name }
    assignee { id name }
    cycle { id name number }
  `;

  async getTodoIssues(projectName?: string): Promise<LinearIssue[]> {
    const data = await this.query<{
      team: { issues: { nodes: LinearIssue[] } };
    }>(
      `query($teamId: String!) {
        team(id: $teamId) {
          issues(
            filter: { state: { type: { eq: "unstarted" } } }
            first: 50
            orderBy: updatedAt
          ) {
            nodes { ${this.ISSUE_FRAGMENT} }
          }
        }
      }`,
      { teamId: this.teamId },
    );

    let issues = data.team.issues.nodes;
    if (projectName) {
      issues = issues.filter((i) =>
        i.project?.name.toLowerCase() === projectName.toLowerCase(),
      );
    }
    return issues;
  }

  async getInProgressIssues(): Promise<LinearIssue[]> {
    const data = await this.query<{
      team: { issues: { nodes: LinearIssue[] } };
    }>(
      `query($teamId: String!) {
        team(id: $teamId) {
          issues(
            filter: { state: { type: { eq: "started" } } }
            first: 50
            orderBy: updatedAt
          ) {
            nodes { ${this.ISSUE_FRAGMENT} }
          }
        }
      }`,
      { teamId: this.teamId },
    );

    return data.team.issues.nodes;
  }

  // --------------------------------------------------------
  // Issue mutations
  // --------------------------------------------------------

  async transitionIssue(issueId: string, stateName: string): Promise<boolean> {
    const stateId = await this.getStateId(stateName);
    if (!stateId) {
      console.error(`[Linear] Unknown state "${stateName}"`);
      return false;
    }

    const data = await this.query<{
      issueUpdate: { success: boolean };
    }>(
      `mutation($issueId: String!, $stateId: String!) {
        issueUpdate(id: $issueId, input: { stateId: $stateId }) {
          success
        }
      }`,
      { issueId, stateId },
    );

    return data.issueUpdate.success;
  }

  async addComment(issueId: string, body: string): Promise<boolean> {
    const data = await this.query<{
      commentCreate: { success: boolean };
    }>(
      `mutation($issueId: String!, $body: String!) {
        commentCreate(input: { issueId: $issueId, body: $body }) {
          success
        }
      }`,
      { issueId, body },
    );

    return data.commentCreate.success;
  }

  async createIssue(input: LinearCreateIssueInput): Promise<LinearIssue | null> {
    const data = await this.query<{
      issueCreate: { success: boolean; issue: LinearIssue };
    }>(
      `mutation($input: IssueCreateInput!) {
        issueCreate(input: $input) {
          success
          issue { ${this.ISSUE_FRAGMENT} }
        }
      }`,
      {
        input: {
          title: input.title,
          description: input.description,
          teamId: input.teamId,
          projectId: input.projectId,
          priority: input.priority,
          labelIds: input.labelIds,
          cycleId: input.cycleId,
          stateId: input.stateId,
        },
      },
    );

    return data.issueCreate.success ? data.issueCreate.issue : null;
  }

  // --------------------------------------------------------
  // Brief conversion
  // --------------------------------------------------------

  /**
   * Convert a Linear issue into a SessionBrief-compatible object.
   * The caller (ResearchPlanner) uses this to create full briefs.
   */
  issueToBrief(issue: LinearIssue, projectName: string): {
    projectName: string;
    objective: string;
    priority: number;
    agentType: string;
    linearIssueId: string;
    linearIdentifier: string;
  } {
    // Priority mapping: Linear 1=urgent→95, 2=high→75, 3=medium→55, 4=low→35, 0=none→45
    const priorityMap: Record<number, number> = {
      1: 95,
      2: 75,
      3: 55,
      4: 35,
      0: 45,
    };
    const priority = priorityMap[issue.priority] ?? 55;

    // Agent type from labels
    const labelNames = issue.labels.nodes.map((l) => l.name.toLowerCase());
    let agentType = "researcher";
    if (labelNames.includes("paper") || labelNames.includes("submission")) agentType = "writer";
    else if (labelNames.includes("experiment")) agentType = "experimenter";
    else if (labelNames.includes("infrastructure") || labelNames.includes("bug") || labelNames.includes("daemon")) agentType = "engineer";

    // Objective from title + description
    const desc = issue.description ? `\n\nDetails:\n${issue.description}` : "";
    const objective = `[${issue.identifier}] ${issue.title}${desc}`;

    return {
      projectName,
      objective,
      priority,
      agentType,
      linearIssueId: issue.id,
      linearIdentifier: issue.identifier,
    };
  }

  // --------------------------------------------------------
  // Workspace management (for setup scripts)
  // --------------------------------------------------------

  async getProjects(): Promise<{ id: string; name: string; state: string }[]> {
    const data = await this.query<{
      team: { projects: { nodes: { id: string; name: string; state: string }[] } };
    }>(
      `query($teamId: String!) {
        team(id: $teamId) {
          projects(first: 100) {
            nodes { id name state }
          }
        }
      }`,
      { teamId: this.teamId },
    );
    return data.team.projects.nodes;
  }

  async archiveProject(projectId: string): Promise<boolean> {
    const data = await this.query<{
      projectArchive: { success: boolean };
    }>(
      `mutation($projectId: String!) {
        projectArchive(id: $projectId) { success }
      }`,
      { projectId },
    );
    return data.projectArchive.success;
  }

  async createProject(name: string, description?: string): Promise<string> {
    const data = await this.query<{
      projectCreate: { success: boolean; project: { id: string } };
    }>(
      `mutation($input: ProjectCreateInput!) {
        projectCreate(input: $input) {
          success
          project { id }
        }
      }`,
      {
        input: {
          name,
          description,
          teamIds: [this.teamId],
        },
      },
    );
    return data.projectCreate.project.id;
  }

  async getCycles(): Promise<{ id: string; name: string; number: number; startsAt: string; endsAt: string }[]> {
    const data = await this.query<{
      team: { cycles: { nodes: { id: string; name: string; number: number; startsAt: string; endsAt: string }[] } };
    }>(
      `query($teamId: String!) {
        team(id: $teamId) {
          cycles(first: 100) {
            nodes { id name number startsAt endsAt }
          }
        }
      }`,
      { teamId: this.teamId },
    );
    return data.team.cycles.nodes;
  }

  async archiveCycle(cycleId: string): Promise<boolean> {
    const data = await this.query<{
      cycleArchive: { success: boolean };
    }>(
      `mutation($cycleId: String!) {
        cycleArchive(id: $cycleId) { success }
      }`,
      { cycleId },
    );
    return data.cycleArchive.success;
  }

  async createCycle(name: string, startsAt: string, endsAt: string): Promise<string> {
    const data = await this.query<{
      cycleCreate: { success: boolean; cycle: { id: string } };
    }>(
      `mutation($input: CycleCreateInput!) {
        cycleCreate(input: $input) {
          success
          cycle { id }
        }
      }`,
      {
        input: {
          name,
          teamId: this.teamId,
          startsAt,
          endsAt,
        },
      },
    );
    return data.cycleCreate.cycle.id;
  }

  async getLabels(): Promise<{ id: string; name: string }[]> {
    const data = await this.query<{
      team: { labels: { nodes: { id: string; name: string }[] } };
    }>(
      `query($teamId: String!) {
        team(id: $teamId) {
          labels(first: 100) {
            nodes { id name }
          }
        }
      }`,
      { teamId: this.teamId },
    );
    return data.team.labels.nodes;
  }

  async createLabel(name: string): Promise<string> {
    const data = await this.query<{
      issueLabelCreate: { success: boolean; issueLabel: { id: string } };
    }>(
      `mutation($input: IssueLabelCreateInput!) {
        issueLabelCreate(input: $input) {
          success
          issueLabel { id }
        }
      }`,
      {
        input: {
          name,
          teamId: this.teamId,
        },
      },
    );
    return data.issueLabelCreate.issueLabel.id;
  }

  async getIssues(filter?: { projectId?: string }): Promise<LinearIssue[]> {
    const filterObj: Record<string, unknown> = {};
    if (filter?.projectId) {
      filterObj.project = { id: { eq: filter.projectId } };
    }

    const data = await this.query<{
      team: { issues: { nodes: LinearIssue[] } };
    }>(
      `query($teamId: String!, $filter: IssueFilter) {
        team(id: $teamId) {
          issues(filter: $filter, first: 250) {
            nodes { ${this.ISSUE_FRAGMENT} }
          }
        }
      }`,
      { teamId: this.teamId, filter: Object.keys(filterObj).length > 0 ? filterObj : undefined },
    );
    return data.team.issues.nodes;
  }

  async archiveIssue(issueId: string): Promise<boolean> {
    const data = await this.query<{
      issueArchive: { success: boolean };
    }>(
      `mutation($issueId: String!) {
        issueArchive(id: $issueId) { success }
      }`,
      { issueId },
    );
    return data.issueArchive.success;
  }

  // --------------------------------------------------------
  // Project-to-DW-project mapping
  // --------------------------------------------------------

  /** Map a Linear project name to a DW project directory name. */
  static projectNameToDW(linearProjectName: string): string | null {
    const map: Record<string, string> = {
      "reasoning-gaps": "reasoning-gaps",
      "verification-complexity": "verification-complexity",
      "self-improvement-limits": "self-improvement-limits",
      "agent-failure-taxonomy": "agent-failure-taxonomy",
      "platform-infra": "_platform",
      "platform-intelligence": "_platform",
      "dashboard": "_platform",
    };
    return map[linearProjectName.toLowerCase()] ?? null;
  }
}
