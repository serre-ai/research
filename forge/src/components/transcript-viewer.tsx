'use client';

import { useState, useMemo } from 'react';
import { clsx } from 'clsx';
import { ChevronDown, ChevronRight, User, Bot, Wrench, Terminal } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface TranscriptViewerProps {
  lines: string[];
  total: number;
  onLoadMore?: () => void;
}

// Expected JSONL shapes
interface MessageEntry {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface ToolCallEntry {
  type: 'tool_call';
  name: string;
  arguments: Record<string, unknown>;
  timestamp?: string;
}

interface ToolResultEntry {
  type: 'tool_result';
  name: string;
  output: string;
  timestamp?: string;
}

type TranscriptEntry =
  | { kind: 'message'; data: MessageEntry }
  | { kind: 'tool_call'; data: ToolCallEntry }
  | { kind: 'tool_result'; data: ToolResultEntry }
  | { kind: 'raw'; text: string };

function parseLine(line: string): TranscriptEntry {
  const trimmed = line.trim();
  if (!trimmed) return { kind: 'raw', text: line };

  try {
    const parsed = JSON.parse(trimmed);

    // Check if it's a message entry
    if (parsed.role === 'user' || parsed.role === 'assistant') {
      return { kind: 'message', data: parsed as MessageEntry };
    }

    // Check if it's a tool call
    if (parsed.type === 'tool_call' && parsed.name) {
      return { kind: 'tool_call', data: parsed as ToolCallEntry };
    }

    // Check if it's a tool result
    if (parsed.type === 'tool_result' && parsed.name) {
      return { kind: 'tool_result', data: parsed as ToolResultEntry };
    }

    // Unknown JSON shape — render as raw
    return { kind: 'raw', text: JSON.stringify(parsed, null, 2) };
  } catch {
    return { kind: 'raw', text: line };
  }
}

function Timestamp({ value }: { value?: string }) {
  if (!value) return null;
  const date = new Date(value);
  const formatted = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
  return (
    <span className="font-mono text-[10px] text-text-muted">{formatted}</span>
  );
}

function CollapsibleBlock({
  label,
  icon: Icon,
  content,
  timestamp,
  variant,
}: {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  content: string;
  timestamp?: string;
  variant: 'call' | 'result';
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={clsx(
        'border-l-2 pl-3',
        variant === 'call'
          ? 'border-[--color-accent-primary]'
          : 'border-[--color-accent-secondary]',
      )}
    >
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 text-left"
      >
        {expanded ? (
          <ChevronDown className="h-3 w-3 shrink-0 text-text-muted" />
        ) : (
          <ChevronRight className="h-3 w-3 shrink-0 text-text-muted" />
        )}
        <Icon className="h-3.5 w-3.5 shrink-0 text-text-muted" />
        <span className="font-mono text-xs font-medium text-text-secondary">
          {label}
        </span>
        <Timestamp value={timestamp} />
      </button>
      {expanded && (
        <pre className="mt-2 overflow-x-auto bg-[#0d0d0d] p-3 font-mono text-xs leading-relaxed text-text-secondary border border-border">
          {content}
        </pre>
      )}
    </div>
  );
}

function EntryRenderer({ entry, index }: { entry: TranscriptEntry; index: number }) {
  switch (entry.kind) {
    case 'message': {
      const { data } = entry;
      const isUser = data.role === 'user';
      return (
        <div
          className={clsx(
            'rounded p-3',
            isUser ? 'bg-bg-surface' : 'bg-bg-elevated',
          )}
        >
          <div className="mb-1.5 flex items-center gap-2">
            {isUser ? (
              <User className="h-3.5 w-3.5 text-text-muted" />
            ) : (
              <Bot className="h-3.5 w-3.5 text-text-muted" />
            )}
            <span className="font-mono text-xs font-medium text-text-secondary">
              {isUser ? 'User' : 'Assistant'}
            </span>
            <Timestamp value={data.timestamp} />
          </div>
          <div className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-text">
            {data.content}
          </div>
        </div>
      );
    }

    case 'tool_call': {
      const { data } = entry;
      const argsStr =
        typeof data.arguments === 'object'
          ? JSON.stringify(data.arguments, null, 2)
          : String(data.arguments ?? '');
      return (
        <CollapsibleBlock
          label={`tool_call: ${data.name}`}
          icon={Wrench}
          content={argsStr}
          timestamp={data.timestamp}
          variant="call"
        />
      );
    }

    case 'tool_result': {
      const { data } = entry;
      return (
        <CollapsibleBlock
          label={`tool_result: ${data.name}`}
          icon={Terminal}
          content={data.output}
          timestamp={data.timestamp}
          variant="result"
        />
      );
    }

    case 'raw':
      return (
        <pre
          key={index}
          className="overflow-x-auto bg-[#0d0d0d] p-3 font-mono text-xs leading-relaxed text-text-muted border border-border"
        >
          {entry.text}
        </pre>
      );
  }
}

export function TranscriptViewer({ lines, total, onLoadMore }: TranscriptViewerProps) {
  const entries = useMemo(() => lines.map(parseLine), [lines]);
  const hasMore = lines.length < total;

  if (entries.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-center">
        <p className="font-mono text-sm text-text-muted">No transcript data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {entries.map((entry, i) => (
        <EntryRenderer key={i} entry={entry} index={i} />
      ))}

      {hasMore && onLoadMore && (
        <div className="flex justify-center pt-4">
          <Button variant="outline" size="sm" onClick={onLoadMore}>
            Load more ({lines.length} of {total})
          </Button>
        </div>
      )}
    </div>
  );
}
