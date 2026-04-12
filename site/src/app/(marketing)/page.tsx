import type { Metadata } from 'next';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

export const metadata: Metadata = {
  title: 'Serre AI — Formal Foundations of AI Reasoning',
};

const papers = [
  {
    title: 'On the Reasoning Gaps of Large Language Models: A Formal Characterization',
    venue: 'NeurIPS 2026',
    status: 'Pre-Print' as const,
    description: '176,000 evaluations across 12 models. Systematic failure modes correlate with computational complexity classes.',
  },
  {
    title: 'The Computational Complexity of Verifying LLM Outputs',
    venue: 'ICLR 2027',
    status: 'In Progress' as const,
    description: 'Formal framework for verification efficiency. When is checking harder than generating?',
  },
  {
    title: 'A Taxonomy of Failure Modes in LLM-Based Autonomous Agents',
    venue: 'ACL 2027',
    status: 'In Progress' as const,
    description: '50+ deployment incidents analyzed. Structured taxonomy of agent failure modes.',
  },
  {
    title: 'Impossibility Results for Unsupervised Self-Improvement in Language Models',
    venue: 'ICLR 2027',
    status: 'Early Stage' as const,
    description: 'Theoretical bounds on what self-learning can and cannot achieve.',
  },
];

function statusVariant(status: string) {
  if (status === 'Pre-Print') return 'default' as const;
  return 'secondary' as const;
}

export default function HomePage() {
  return (
    <div className="space-y-16">
      <section className="space-y-4 pt-8">
        <h1 className="text-lg font-semibold text-foreground">
          Independent research lab.
        </h1>
        <p className="max-w-lg text-sm leading-relaxed text-muted-foreground">
          Formal foundations of AI reasoning — spanning computational complexity,
          verification theory, and large-scale empirical evaluation. Based in
          Reykjavik.
        </p>
      </section>

      <section className="space-y-6">
        <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          Research
        </h2>
        <div className="space-y-3">
          {papers.map((paper) => (
            <Card key={paper.title} className="bg-card">
              <CardHeader className="space-y-2 p-4">
                <div className="flex items-start justify-between gap-4">
                  <CardTitle className="text-sm font-medium leading-snug text-foreground">
                    {paper.title}
                  </CardTitle>
                  <Badge variant={statusVariant(paper.status)} className="shrink-0 text-[10px]">
                    {paper.status}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-muted-foreground">{paper.venue}</span>
                </div>
                <CardDescription className="text-xs leading-relaxed">
                  {paper.description}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
        <Link
          href="/papers"
          className="inline-block text-xs text-muted-foreground transition-colors hover:text-foreground"
        >
          All papers &rarr;
        </Link>
      </section>

      <section className="space-y-4">
        <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          About
        </h2>
        <p className="text-sm leading-relaxed text-muted-foreground">
          Serre AI is a solo research operation by{' '}
          <span className="text-foreground">Oddur Sigurdsson</span>. The lab uses
          autonomous AI agents to conduct research 24/7 — reading literature,
          designing experiments, writing papers, and iterating on their own
          weaknesses.
        </p>
        <Link
          href="/about"
          className="inline-block text-xs text-muted-foreground transition-colors hover:text-foreground"
        >
          Read more &rarr;
        </Link>
      </section>
    </div>
  );
}
