import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const papers = [
  {
    title: 'On the Reasoning Gaps of Large Language Models: A Formal Characterization',
    authors: 'Oddur Sigurdsson',
    venue: 'NeurIPS 2026',
    status: 'Pre-print',
    href: '/papers/reasoning-gaps',
    description: 'A formal framework connecting LLM reasoning failures to computational complexity boundaries, with a diagnostic benchmark suite of 121,000+ evaluations across 9 models.',
  },
  {
    title: 'A Taxonomy of Failure Modes in LLM-Based Autonomous Agents',
    authors: 'Oddur Sigurdsson',
    venue: 'ACL 2027',
    status: 'In Progress',
    href: null as string | null,
    description: 'Comprehensive survey categorizing 100+ documented agent failures into a rigorous, hierarchical taxonomy grounded in controlled experiments.',
  },
];

export default function PapersPage() {
  return (
    <>
      <div className="mx-auto max-w-6xl px-6 pt-24 pb-16">
        <h1 className="font-mono text-[var(--color-text-bright)]">PAPERS</h1>
        <p className="mt-4 text-lg text-[var(--color-text-secondary)] max-w-2xl">
          Publications and preprints from Deepwork Research
        </p>
      </div>

      <div className="mx-auto max-w-6xl px-6 pb-24">
        <div className="flex flex-col gap-6">
          {papers.map((paper) => (
            <article key={paper.title} className="border-t-[3px] border-t-[var(--color-text)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-6">
              <div className="flex flex-wrap items-center gap-4 mb-3">
                <span className="label text-[var(--color-text-secondary)]">{paper.venue}</span>
                <Badge variant={paper.status === 'Pre-print' ? 'default' : 'outline'}>
                  {paper.status}
                </Badge>
              </div>
              {paper.href ? (
                <Link href={paper.href} className="hover:no-underline group">
                  <h3 className="font-mono font-semibold text-[var(--color-text-bright)] leading-snug group-hover:underline">
                    {paper.title}
                  </h3>
                </Link>
              ) : (
                <h3 className="font-mono font-semibold text-[var(--color-text-bright)] leading-snug">
                  {paper.title}
                </h3>
              )}
              <p className="mt-1 font-mono text-xs text-[var(--color-text-muted)]">{paper.authors}</p>
              <p className="mt-2 text-[var(--color-text-secondary)] text-sm">
                {paper.description}
              </p>
              {paper.href && (
                <div className="mt-4">
                  <Link href={paper.href} className="label hover:text-[var(--color-text-bright)] transition-colors hover:no-underline flex items-center gap-1.5 w-fit">
                    <ArrowRight className="h-3 w-3" />
                    View paper
                  </Link>
                </div>
              )}
            </article>
          ))}
        </div>
      </div>
    </>
  );
}
