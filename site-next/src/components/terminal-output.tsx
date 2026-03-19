'use client';

import { useMemo } from 'react';
import { clsx } from 'clsx';

interface TerminalOutputProps {
  content: string;
  className?: string;
}

interface StyledSegment {
  text: string;
  bold: boolean;
  color: string | null;
}

const ANSI_COLOR_MAP: Record<string, string> = {
  '30': 'color: #737373', // black (muted)
  '31': 'color: #ef4444', // red
  '32': 'color: #10b981', // green
  '33': 'color: #f59e0b', // yellow
  '34': 'color: #60a5fa', // blue
  '35': 'color: #a78bfa', // magenta
  '36': 'color: #22d3ee', // cyan
  '37': 'color: #e5e5e5', // white
  '90': 'color: #737373', // bright black (gray)
  '91': 'color: #f87171', // bright red
  '92': 'color: #34d399', // bright green
  '93': 'color: #fbbf24', // bright yellow
  '94': 'color: #93c5fd', // bright blue
  '95': 'color: #c4b5fd', // bright magenta
  '96': 'color: #67e8f9', // bright cyan
  '97': 'color: #fafafa', // bright white
};

// eslint-disable-next-line no-control-regex
const ANSI_REGEX = /\x1b\[([0-9;]*)m/g;

function parseAnsi(content: string): StyledSegment[] {
  const segments: StyledSegment[] = [];
  let bold = false;
  let color: string | null = null;
  let lastIndex = 0;

  let match;
  while ((match = ANSI_REGEX.exec(content)) !== null) {
    // Push text before this escape code
    if (match.index > lastIndex) {
      segments.push({ text: content.slice(lastIndex, match.index), bold, color });
    }

    // Parse escape code parameters
    const codes = match[1].split(';').filter(Boolean);
    for (const code of codes) {
      if (code === '0') {
        bold = false;
        color = null;
      } else if (code === '1') {
        bold = true;
      } else if (ANSI_COLOR_MAP[code]) {
        color = ANSI_COLOR_MAP[code];
      }
    }

    lastIndex = match.index + match[0].length;
  }

  // Push remaining text
  if (lastIndex < content.length) {
    segments.push({ text: content.slice(lastIndex), bold, color });
  }

  return segments;
}

export function TerminalOutput({ content, className }: TerminalOutputProps) {
  const segments = useMemo(() => parseAnsi(content), [content]);

  return (
    <pre
      className={clsx(
        'overflow-x-auto bg-[#0d0d0d] p-4 font-mono text-xs leading-relaxed text-text-secondary',
        'border border-border',
        className,
      )}
    >
      <code>
        {segments.map((seg, i) => {
          if (!seg.bold && !seg.color) return seg.text;

          const style: React.CSSProperties = {};
          if (seg.bold) style.fontWeight = 700;
          if (seg.color) {
            // Parse "color: #xxx" into the style object
            const colorValue = seg.color.replace('color: ', '');
            style.color = colorValue;
          }

          return (
            <span key={i} style={style}>
              {seg.text}
            </span>
          );
        })}
      </code>
    </pre>
  );
}
