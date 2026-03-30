import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import type { PostType, VotePosition } from '@/lib/collective-types';

interface CreateThreadRequest {
  author: string;
  title: string;
  body: string;
  post_type: PostType;
}

interface ReplyRequest {
  author: string;
  body: string;
}

interface VoteRequest {
  voter: string;
  position: VotePosition;
  rationale?: string;
  confidence?: number;
}

export function useCreateThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateThreadRequest) =>
      apiFetch('/forum/threads', {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Thread created');
      queryClient.invalidateQueries({ queryKey: ['forum'] });
    },
    onError: (error) => {
      toast.error(`Failed to create thread: ${error.message}`);
    },
  });
}

export function useReplyToThread(threadId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ReplyRequest) =>
      apiFetch(`/forum/threads/${threadId}/reply`, {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Reply posted');
      queryClient.invalidateQueries({ queryKey: ['forum'] });
    },
    onError: (error) => {
      toast.error(`Failed to post reply: ${error.message}`);
    },
  });
}

export function useVoteOnThread(threadId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: VoteRequest) =>
      apiFetch(`/forum/threads/${threadId}/vote`, {
        method: 'POST',
        body: JSON.stringify(request),
      }),
    onSuccess: () => {
      toast.success('Vote cast');
      queryClient.invalidateQueries({ queryKey: ['forum'] });
    },
    onError: (error) => {
      toast.error(`Failed to cast vote: ${error.message}`);
    },
  });
}

export function useUpdateThreadStatus(threadId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (status: string) =>
      apiFetch(`/forum/threads/${threadId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    onSuccess: () => {
      toast.success('Thread status updated');
      queryClient.invalidateQueries({ queryKey: ['forum'] });
    },
    onError: (error) => {
      toast.error(`Failed to update status: ${error.message}`);
    },
  });
}

export function useSynthesizeThread(threadId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      apiFetch(`/forum/threads/${threadId}/synthesize`, {
        method: 'POST',
      }),
    onSuccess: () => {
      toast.success('Thread synthesized');
      queryClient.invalidateQueries({ queryKey: ['forum'] });
    },
    onError: (error) => {
      toast.error(`Synthesis failed: ${error.message}`);
    },
  });
}
