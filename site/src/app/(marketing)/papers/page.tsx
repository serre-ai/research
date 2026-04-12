import type { Metadata } from 'next';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';

export const metadata: Metadata = {
  title: 'Papers',
};

const papers = [
  {
    title: 'On the Reasoning Gaps of Large Language Models: A Formal Characterization',
    venue: 'NeurIPS 2026',
    status: 'Pre-Print' as const,
    abstract:
      'We present a formal framework connecting LLM reasoning failures to computational complexity classes. Through 176,000 evaluations across 12 model families and 9 diagnostic tasks, we show that reasoning gaps cluster into six types predictable from problem structure. Chain-of-thought closes gaps for serial composition (+35 pp) but not for problems requiring parallel search or architectural capabilities (+9 pp).',
    keywords: ['reasoning', 'computational complexity', 'chain-of-thought', 'benchmarks', 'formal methods'],
  },
  {
    title: 'The Computational Complexity of Verifying LLM Outputs',
    venue: 'ICLR 2027',
    status: 'In Progress' as const,
    abstract:
      'We develop a formal framework for the computational complexity of verifying language model outputs. We characterize verification difficulty across output types and prove that for several natural problem classes, verification is strictly easier than generation — but this gap varies systematically with output structure.',
    keywords: ['verification', 'complexity theory', 'LLM outputs', 'formal verification'],
  },
  {
    title: 'A Taxonomy of Failure Modes in LLM-Based Autonomous Agents',
    venue: 'ACL 2027',
    status: 'In Progress' as const,
    abstract:
      'Drawing on 50+ deployment incidents from autonomous agent systems, we construct a structured taxonomy of failure modes. Categories span planning failures, tool-use errors, context management breakdowns, and goal drift. We connect each category to architectural mitigations and evaluate their effectiveness.',
    keywords: ['autonomous agents', 'failure modes', 'taxonomy', 'deployment', 'safety'],
  },
  {
    title: 'Impossibility Results for Unsupervised Self-Improvement in Language Models',
    venue: 'ICLR 2027',
    status: 'Early Stage' as const,
    abstract:
      'We establish theoretical bounds on unsupervised self-improvement in language models. Under standard complexity assumptions, we show that certain capability gains require external signal — no amount of self-play or self-evaluation can substitute for ground truth on specific problem classes.',
    keywords: ['self-improvement', 'impossibility results', 'theoretical bounds', 'self-play'],
  },
];

function statusVariant(status: string) {
  if (status === 'Pre-Print') return 'default' as const;
  return 'secondary' as const;
}

export default function PapersPage() {
  return (
    <div className="space-y-8">
      <section className="space-y-2 pt-4">
        <h1 className="text-lg font-semibold text-foreground">Papers</h1>
        <p className="text-sm text-muted-foreground">
          Research publications and works in progress.
        </p>
      </section>

      <div className="space-y-4">
        {papers.map((paper, i) => (
          <div key={paper.title}>
            <Card className="bg-card">
              <CardHeader className="space-y-2 p-5">
                <div className="flex items-start justify-between gap-4">
                  <CardTitle className="text-sm font-medium leading-snug text-foreground">
                    {paper.title}
                  </CardTitle>
                  <Badge variant={statusVariant(paper.status)} className="shrink-0 text-[10px]">
                    {paper.status}
                  </Badge>
                </div>
                <span className="text-[11px] text-muted-foreground">{paper.venue}</span>
              </CardHeader>
              <CardContent className="space-y-3 px-5 pb-5">
                <CardDescription className="text-xs leading-relaxed">
                  {paper.abstract}
                </CardDescription>
                <div className="flex flex-wrap gap-1.5">
                  {paper.keywords.map((kw) => (
                    <span
                      key={kw}
                      className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
            {i < papers.length - 1 && <Separator className="my-4 opacity-0" />}
          </div>
        ))}
      </div>
    </div>
  );
}
