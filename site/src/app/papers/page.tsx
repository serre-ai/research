import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Papers',
};

const papers = [
  {
    title: 'On the Reasoning Gaps of Large Language Models: A Formal Characterization',
    venue: 'NeurIPS 2026',
    status: 'Pre-Print',
    statusColor: 'text-status-ok',
    abstract: 'We present a formal framework for characterizing reasoning failures in large language models. Through 176,000 evaluations across 12 models and 9 benchmark tasks spanning P to coNP complexity classes, we demonstrate that LLM reasoning gaps are systematic, predictable, and correlate with the computational complexity of the underlying task. Our taxonomy identifies six distinct gap types with measurable signatures.',
    keywords: ['LLM reasoning', 'computational complexity', 'benchmark design', 'formal characterization'],
  },
  {
    title: 'The Computational Complexity of Verifying LLM Outputs Across Reasoning Domains',
    venue: 'ICLR 2027',
    status: 'In Progress',
    statusColor: 'text-accent',
    abstract: 'We develop a complexity-theoretic framework for analyzing when LLM outputs can be efficiently verified. Our approach connects verification difficulty to the VC dimension of the underlying reasoning task, with three main theorems establishing bounds on cross-model verification, self-consistency checking, and interactive verification protocols.',
    keywords: ['verification complexity', 'scalable oversight', 'cross-model verification'],
  },
  {
    title: 'A Taxonomy of Failure Modes in LLM-Based Autonomous Agents',
    venue: 'ACL 2027',
    status: 'In Progress',
    statusColor: 'text-accent',
    abstract: 'Drawing from 50+ real deployment incidents, we construct a comprehensive taxonomy of how LLM-based autonomous agents fail. Our 9-category framework with C1-C8 failure code mapping enables systematic diagnosis and mitigation of agent failures across tool use, planning, and self-monitoring dimensions.',
    keywords: ['autonomous agents', 'failure taxonomy', 'LLM agents', 'reliability'],
  },
  {
    title: 'Impossibility Results for Unsupervised Self-Improvement in Language Models',
    venue: 'ICLR 2027',
    status: 'Early Stage',
    statusColor: 'text-text-muted',
    abstract: 'We investigate theoretical limits on what language models can learn from their own outputs without external supervision. Preliminary results suggest fundamental bounds on self-improvement through self-training, self-refinement, and constitutional AI approaches.',
    keywords: ['self-improvement', 'impossibility results', 'self-training', 'theoretical ML'],
  },
];

export default function PapersPage() {
  return (
    <>
      <section className="pt-8 pb-4">
        <h1 className="text-xs text-text-muted uppercase tracking-widest mb-2">Papers</h1>
        <p className="text-sm text-text-muted">Research publications and working papers.</p>
      </section>

      <div className="space-y-0">
        {papers.map((paper) => (
          <article key={paper.title} className="py-8 border-b border-border last:border-0">
            <h2 className="text-text-bright font-medium leading-snug">{paper.title}</h2>
            <p className="text-sm mt-1.5">
              <span className="text-text-muted">{paper.venue}</span>
              {'  '}
              <span className={paper.statusColor}>{paper.status}</span>
            </p>
            <p className="text-sm mt-3 leading-relaxed">{paper.abstract}</p>
            <p className="text-xs text-text-muted mt-3">
              {paper.keywords.join(' · ')}
            </p>
          </article>
        ))}
      </div>
    </>
  );
}
