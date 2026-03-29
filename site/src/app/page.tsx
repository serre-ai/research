import Link from 'next/link';

const papers = [
  {
    title: 'On the Reasoning Gaps of Large Language Models',
    subtitle: 'A Formal Characterization',
    venue: 'NeurIPS 2026',
    status: 'Pre-Print',
    statusColor: 'text-status-ok',
    description: '176,000 evaluations across 12 models and 9 benchmark tasks reveal systematic, predictable failure modes in LLM reasoning that correlate with computational complexity.',
    href: '/papers',
  },
  {
    title: 'The Computational Complexity of Verifying LLM Outputs',
    venue: 'ICLR 2027',
    status: 'In Progress',
    statusColor: 'text-accent',
    description: 'Formal complexity-theoretic framework for understanding when and why LLM outputs can be efficiently verified, with implications for scalable oversight.',
  },
  {
    title: 'A Taxonomy of Failure Modes in LLM-Based Autonomous Agents',
    venue: 'ACL 2027',
    status: 'In Progress',
    statusColor: 'text-accent',
    description: 'Empirical taxonomy of how autonomous LLM agents fail in practice, drawn from 50+ real deployment incidents across research and production systems.',
  },
  {
    title: 'Impossibility Results for Unsupervised Self-Improvement in Language Models',
    venue: 'ICLR 2027',
    status: 'Early Stage',
    statusColor: 'text-text-muted',
    description: 'Theoretical bounds on what language models can learn from their own outputs without external signal.',
  },
];

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <section className="pt-16 pb-8">
        <p className="text-text-muted text-sm mb-12">
          Independent research lab.{' '}
          <span className="text-text">Formal foundations of AI reasoning.</span>
        </p>
        <div className="text-sm">
          <p className="text-text-bright">Oddur Sigurdsson</p>
          <p className="text-text-muted">oddur@serre.ai</p>
        </div>
      </section>

      <hr />

      {/* Papers */}
      <section>
        <h2 className="text-xs text-text-muted uppercase tracking-widest mb-8">Research</h2>
        <div className="space-y-10">
          {papers.map((paper) => (
            <article key={paper.title}>
              <h3 className="text-text-bright font-medium leading-snug">
                {paper.href ? (
                  <Link href={paper.href}>{paper.title}</Link>
                ) : (
                  paper.title
                )}
              </h3>
              {paper.subtitle && (
                <p className="text-text-muted text-sm mt-0.5">{paper.subtitle}</p>
              )}
              <p className="text-sm mt-1.5">
                <span className="text-text-muted">{paper.venue}</span>
                {'  '}
                <span className={paper.statusColor}>{paper.status}</span>
              </p>
              <p className="text-sm mt-2 leading-relaxed">{paper.description}</p>
            </article>
          ))}
        </div>
      </section>

      <hr />

      {/* Brief about */}
      <section>
        <p className="text-sm leading-relaxed">
          We prove theorems about what language models can and cannot do.
          Our work spans computational complexity, verification theory,
          and empirical evaluation at scale.
        </p>
        <p className="text-sm text-text-muted mt-4">
          <Link href="/about">More about the lab</Link>
        </p>
      </section>
    </>
  );
}
