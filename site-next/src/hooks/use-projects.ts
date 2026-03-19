import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import type { Project } from '@/lib/types';

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => apiFetch<Project[]>('/projects'),
    staleTime: 60_000,
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: () => apiFetch<Project>(`/projects/${id}`),
    staleTime: 60_000,
    enabled: !!id,
  });
}
