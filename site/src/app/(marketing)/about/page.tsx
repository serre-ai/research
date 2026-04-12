import type { Metadata } from 'next';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';

export const metadata: Metadata = {
  title: 'About',
};

const researchAreas = [
  {
    title: 'Computational Complexity of LLM Reasoning',
    description:
      'Connecting empirical reasoning failures to formal complexity classes. When and why do models fail systematically?',
  },
  {
    title: 'Verification Theory',
    description:
      'Characterizing when checking LLM outputs is computationally easier than generating them, and by how much.',
  },
  {
    title: 'Benchmark Design',
    description:
      'Diagnostic tasks that isolate specific reasoning bottlenecks rather than measuring aggregate performance.',
  },
];

export default function AboutPage() {
  return (
    <div className="space-y-12">
      <section className="space-y-4 pt-4">
        <h1 className="text-lg font-semibold text-foreground">About</h1>
        <p className="text-sm leading-relaxed text-muted-foreground">
          Serre AI is an independent research lab focused on the formal
          foundations of AI reasoning. Named after{' '}
          <span className="text-foreground">Jean-Pierre Serre</span> — Fields
          Medal, Abel Prize — whose work exemplifies the kind of rigorous,
          foundational thinking we aim to bring to AI.
        </p>
      </section>

      <section className="space-y-4">
        <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          Researcher
        </h2>
        <div className="space-y-2">
          <p className="text-sm text-foreground">Oddur Sigurdsson</p>
          <p className="text-sm leading-relaxed text-muted-foreground">
            Based in Reykjavik. Background in software engineering and
            computational theory. Serre AI is a solo research operation —
            one person with AI agents as collaborators.
          </p>
        </div>
      </section>

      <Separator />

      <section className="space-y-4">
        <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          Methodology
        </h2>
        <div className="space-y-3 text-sm leading-relaxed text-muted-foreground">
          <p>
            Research is conducted by autonomous AI agents built on Claude Code.
            Agents read literature, design experiments, draft papers, and iterate
            on their own weaknesses — with strategic human oversight, not
            operational.
          </p>
          <p>
            Every experiment is pre-registered. Claims are tracked in a knowledge
            graph with automated consistency checks. Multi-agent review catches
            errors before submission. The platform itself is a research artifact.
          </p>
        </div>
      </section>

      <Separator />

      <section className="space-y-4">
        <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          Research Areas
        </h2>
        <div className="grid gap-3">
          {researchAreas.map((area) => (
            <Card key={area.title} className="bg-card">
              <CardHeader className="p-4 pb-0">
                <CardTitle className="text-sm font-medium text-foreground">
                  {area.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="px-4 pb-4 pt-2">
                <p className="text-xs leading-relaxed text-muted-foreground">
                  {area.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
