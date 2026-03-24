import Link from 'next/link';
import { TuiBox, TuiBadge } from '@/components/tui';

interface Paper {
  title: string;
  subtitle?: string;
  venue: string;
  status: string;
  description?: string;
  href?: string;
}

export function PapersList({ papers }: { papers: Paper[] }) {
  return (
    <TuiBox title="PAPERS">
      <div className="space-y-4">
        {papers.map((paper) => (
          <div key={paper.title} className="font-mono">
            <div className="flex items-start gap-2">
              <span className="terminal-prompt shrink-0">&gt;</span>
              <div>
                <p className="text-sm text-text-bright leading-snug">
                  {paper.title}
                  {paper.subtitle && (
                    <span className="text-text-secondary">: {paper.subtitle}</span>
                  )}
                </p>
                <p className="mt-1 text-xs text-text-muted">
                  {paper.venue}{' '}
                  <TuiBadge color={paper.status === 'Pre-Print' ? 'ok' : 'accent'}>
                    {paper.status.toUpperCase()}
                  </TuiBadge>
                  {paper.description && (
                    <span className="ml-2">{paper.description}</span>
                  )}
                </p>
                {paper.href && (
                  <Link
                    href={paper.href}
                    className="mt-1 inline-block text-xs text-text-muted hover:text-text-secondary"
                  >
                    {'\u2192'} {paper.href}
                  </Link>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </TuiBox>
  );
}
