import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About',
};

export default function AboutPage() {
  return (
    <>
      <section className="pt-8 pb-4">
        <h1 className="text-xs text-text-muted uppercase tracking-widest mb-8">About</h1>

        <div className="space-y-6 text-sm leading-relaxed">
          <p>
            <span className="text-text-bright">Serre AI</span> is an independent research lab
            focused on the formal foundations of AI reasoning. We prove theorems about what
            language models can and cannot do.
          </p>
          <p>
            Our work spans three areas: the computational complexity of LLM reasoning,
            the theory of verifying model outputs, and empirical evaluation at scale.
            We publish at top venues and release our benchmarks, data, and analysis code.
          </p>
        </div>
      </section>

      <hr />

      <section>
        <h2 className="text-xs text-text-muted uppercase tracking-widest mb-6">Researcher</h2>
        <div className="text-sm space-y-2">
          <p className="text-text-bright">Oddur Sigurdsson</p>
          <p>Based in Reykjavik. Background in software engineering and
            computational theory. Building Serre AI as a solo research operation
            with autonomous infrastructure.</p>
          <p className="text-text-muted mt-4">oddur@serre.ai</p>
        </div>
      </section>

      <hr />

      <section>
        <h2 className="text-xs text-text-muted uppercase tracking-widest mb-6">Methodology</h2>
        <div className="text-sm space-y-4 leading-relaxed">
          <p>
            We run research using autonomous AI agents built on Claude Code.
            Our platform orchestrates literature surveys, experiment design and execution,
            paper drafting, and internal peer review — all as structured agent sessions
            with quality gates, budget controls, and formal verification.
          </p>
          <p>
            This isn't AI-assisted writing. The agents operate autonomously within
            defined research protocols: pre-registered experiments, knowledge graph
            consistency checks, and multi-agent review cycles. Human oversight is
            strategic, not operational.
          </p>
          <p>
            The platform itself — an autonomous research orchestrator — is a research
            artifact. We study what works and what breaks when AI agents do science.
          </p>
        </div>
      </section>

      <hr />

      <section>
        <h2 className="text-xs text-text-muted uppercase tracking-widest mb-6">Research Areas</h2>
        <div className="text-sm space-y-6">
          <div>
            <p className="text-text-bright">Computational Complexity of LLM Reasoning</p>
            <p className="mt-1">
              Formal characterization of when and why language models fail at reasoning tasks,
              mapped to complexity classes. What is the relationship between a task's
              computational difficulty and a model's accuracy?
            </p>
          </div>
          <div>
            <p className="text-text-bright">Verification Theory</p>
            <p className="mt-1">
              When can we efficiently check whether a model's output is correct?
              Complexity-theoretic bounds on verification, with applications to
              scalable oversight and cross-model consistency.
            </p>
          </div>
          <div>
            <p className="text-text-bright">Benchmark Design</p>
            <p className="mt-1">
              Building evaluation frameworks with known computational structure.
              Tasks with provable ground truth, controlled difficulty scaling,
              and formal guarantees about what they measure.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
