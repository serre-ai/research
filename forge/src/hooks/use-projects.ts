import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { Project } from '@/lib/types';

interface ProjectApiResponse {
  id: string;
  name: string;
  title?: string;
  venue?: string;
  phase: string;
  status: string;
  confidence: number | null;
  current_focus: string | null;
  current_activity: string | null;
  notes: string | null;
  branch: string;
  created_at: string;
  updated_at: string;
}

function transformProject(raw: ProjectApiResponse): Project {
  return {
    id: raw.id ?? raw.name,
    name: raw.name,
    status: raw.status,
    phase: raw.phase,
    focus: raw.current_focus ?? undefined,
    confidence: raw.confidence ?? undefined,
    branch: raw.branch,
    created_at: raw.created_at,
    updated_at: raw.updated_at,
  };
}

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const raw = await apiFetch<ProjectApiResponse[]>('/projects');
      return raw.map(transformProject);
    },
    staleTime: 60_000,
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: async () => {
      const raw = await apiFetch<ProjectApiResponse>(`/projects/${id}`);
      return transformProject(raw);
    },
    staleTime: 60_000,
    enabled: !!id,
  });
}
