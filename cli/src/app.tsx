import React, { useState, useEffect } from "react";
import { Box, Text, useApp } from "ink";
import {
  loadDashboardData,
  type DashboardData,
  type ProjectInfo,
  type BudgetData,
  type ConfigData,
} from "./data.js";

const RULE = "━".repeat(58);
const THIN = "─".repeat(42);

function StatusBadge({ status }: { status: string }) {
  const color =
    status === "active"
      ? "green"
      : status === "paused"
        ? "yellow"
        : status === "completed"
          ? "blue"
          : "gray";
  return <Text color={color}>{status}</Text>;
}

function Header({ data }: { data: DashboardData }) {
  const { currentMonthTotal: spent } = data.budget;
  const limit = data.config.budget.monthly_limit_usd;
  const pct = limit > 0 ? Math.round((spent / limit) * 100) : 0;
  const accounts = data.config.resources.claude_code_max.accounts;
  const active = data.projects.filter((p) => p.status === "active").length;

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text color="cyan" bold>
        {RULE}
      </Text>
      <Text color="cyan" bold>
        {"  DEEPWORK Research Platform"}
      </Text>
      <Text dimColor>
        {"  "}Budget: ${spent.toFixed(0)} / ${limit.toLocaleString()} ({pct}%)
        · Max ×{accounts} · {data.projects.length} project(s), {active} active
      </Text>
      <Text color="cyan" bold>
        {RULE}
      </Text>
    </Box>
  );
}

function ProjectSection({ projects }: { projects: ProjectInfo[] }) {
  if (projects.length === 0) {
    return (
      <Box flexDirection="column" marginBottom={1}>
        <Text color="yellow" bold>
          {"  PROJECTS"}
        </Text>
        <Text dimColor>{"  No projects yet. Use /new-project to create one."}</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text color="yellow" bold>
        {"  PROJECTS"}
      </Text>
      <Text dimColor>{"  " + THIN}</Text>
      {projects.map((p) => (
        <Box key={p.project} flexDirection="column" marginLeft={2}>
          <Text bold color="white">
            {"  " + p.project}
          </Text>
          <Box>
            <Text>{"    ├ "}</Text>
            <Text dimColor>Status: </Text>
            <StatusBadge status={p.status} />
            <Text>{" · "}</Text>
            <Text dimColor>Phase: </Text>
            <Text>{p.phase}</Text>
          </Box>
          {p.venue && (
            <Box>
              <Text>{"    ├ "}</Text>
              <Text dimColor>Venue: </Text>
              <Text>{p.venue}</Text>
            </Box>
          )}
          <Box>
            <Text>{"    ├ "}</Text>
            <Text dimColor>Branch: </Text>
            <Text>{p.branch}</Text>
          </Box>
          <Box>
            <Text>{"    └ "}</Text>
            <Text dimColor>Decisions: </Text>
            <Text>
              {p.decisionsMade} made · {p.decisionsPending} pending
            </Text>
          </Box>
        </Box>
      ))}
    </Box>
  );
}

function BudgetSection({
  budget,
  config,
}: {
  budget: BudgetData;
  config: ConfigData;
}) {
  const month = budget.currentMonth;
  const spending = budget.spending[month] ?? {};
  const total = budget.currentMonthTotal;
  const limit = config.budget.monthly_limit_usd;
  const pct = limit > 0 ? Math.round((total / limit) * 100) : 0;
  const barWidth = 30;
  const filled = Math.round((pct / 100) * barWidth);
  const bar = "█".repeat(filled) + "░".repeat(barWidth - filled);
  const barColor = pct > 80 ? "red" : pct > 50 ? "yellow" : "green";

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text color="yellow" bold>
        {"  BUDGET (" + month + ")"}
      </Text>
      <Text dimColor>{"  " + THIN}</Text>
      <Text>
        {"    API Calls ........ $" +
          (spending.api_calls ?? 0).toFixed(2)}
      </Text>
      <Text>
        {"    Compute .......... $" + (spending.compute ?? 0).toFixed(2)}
      </Text>
      <Text>
        {"    Services ......... $" +
          (spending.data_services ?? 0).toFixed(2)}
      </Text>
      <Text dimColor>{"    " + "─".repeat(32)}</Text>
      <Box>
        <Text bold>{"    Total "}</Text>
        <Text color={barColor}>{bar}</Text>
        <Text bold>
          {" $" + total.toFixed(2) + " / $" + limit.toFixed(2)}
        </Text>
      </Box>
    </Box>
  );
}

function ActivitySection({ commits }: { commits: string[] }) {
  if (commits.length === 0) return null;
  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text color="yellow" bold>
        {"  RECENT ACTIVITY"}
      </Text>
      <Text dimColor>{"  " + THIN}</Text>
      {commits.slice(0, 5).map((c, i) => (
        <Text key={i} dimColor>
          {"    " + c}
        </Text>
      ))}
    </Box>
  );
}

function ResourceSection({ config }: { config: ConfigData }) {
  const apiNames = Object.keys(config.apis);
  return (
    <Box flexDirection="column" marginBottom={0}>
      <Text color="yellow" bold>
        {"  RESOURCES"}
      </Text>
      <Text dimColor>{"  " + THIN}</Text>
      <Box>
        <Text>
          {"    Claude Code Max ×" +
            config.resources.claude_code_max.accounts +
            " · Decisions: "}
        </Text>
        <Text color="green">{config.decision_policy.mode}</Text>
        <Text>{" · Reasoning: "}</Text>
        <Text color="magenta">{config.decision_policy.reasoning}</Text>
      </Box>
      {apiNames.length > 0 && (
        <Text dimColor>{"    APIs: " + apiNames.join(", ")}</Text>
      )}
    </Box>
  );
}

export default function App() {
  const { exit } = useApp();
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData()
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    if (data || error) {
      const timer = setTimeout(() => exit(), 100);
      return () => clearTimeout(timer);
    }
  }, [data, error, exit]);

  if (error) {
    return <Text color="red">Error: {error}</Text>;
  }
  if (!data) {
    return <Text dimColor>Loading dashboard...</Text>;
  }

  return (
    <Box flexDirection="column">
      <Header data={data} />
      <ProjectSection projects={data.projects} />
      <BudgetSection budget={data.budget} config={data.config} />
      <ActivitySection commits={data.recentCommits} />
      <ResourceSection config={data.config} />
      <Text color="cyan" bold>
        {RULE}
      </Text>
    </Box>
  );
}
