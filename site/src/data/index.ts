// Unified data layer: tries VPS API first, falls back to mock data
// Set DEEPWORK_API_URL env to enable live data (defaults to VPS IP)

import * as api from './api';
import * as mock from './mock';

export type { Project, ModelData, EvalTask, ProjectEvalData, ProjectBudgetData, Decision } from './mock';

const USE_API = import.meta.env.DEEPWORK_LIVE !== 'false';

export async function getProjects() {
  if (USE_API) {
    try {
      const apiProjects = await api.fetchProjects();
      if (apiProjects.length > 0) {
        // Merge: use API data for known projects, fill in missing ones from mock
        const apiNames = new Set(apiProjects.map(p => p.name));
        const missing = mock.projects.filter(p => !apiNames.has(p.name));
        return [...apiProjects, ...missing];
      }
    } catch { /* fall through */ }
  }
  return mock.projects;
}

export async function getProject(name: string) {
  const projects = await getProjects();
  return projects.find(p => p.name === name);
}

export async function getEvalData(projectId: string) {
  if (USE_API) {
    try {
      const data = await api.fetchEvalData(projectId);
      if (data) return data;
    } catch { /* fall through */ }
  }
  return mock.evalData[projectId] ?? null;
}

export async function getBudgetData(projectId: string) {
  if (USE_API) {
    try {
      return await api.fetchBudgetData(projectId);
    } catch { /* fall through */ }
  }
  return mock.budgetData[projectId] ?? { monthlyLimit: 1000, dailyLimit: 40, providers: [], dailySpend: [] };
}

export async function getDecisions(projectId?: string) {
  if (USE_API) {
    try {
      const decisions = await api.fetchDecisions(projectId);
      if (decisions.length > 0) return decisions;
    } catch { /* fall through */ }
  }
  return mock.getDecisions(projectId);
}

export async function getAggregateStats() {
  if (USE_API) {
    try {
      return await api.fetchAggregateStats();
    } catch { /* fall through */ }
  }
  return mock.aggregateStats;
}

export async function getSystemHealth() {
  if (USE_API) {
    try {
      return await api.fetchHealth();
    } catch { /* fall through */ }
  }
  return mock.systemHealth;
}

export { evalTasks } from './mock';
