import Link from 'next/link';
import { AlertTriangle, Download, BookOpen, BarChart3, ArrowLeft } from 'lucide-react';

export default function ReasoningGapsPaperPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 pt-16 pb-24">

      {/* Pre-print banner */}
      <div className="border border-[var(--color-status-warn-border)] bg-[var(--color-status-warn-muted)] px-4 py-3 mb-10 flex items-center gap-3">
        <AlertTriangle className="h-3.5 w-3.5 text-[var(--color-status-warn)] shrink-0" />
        <p className="font-mono text-xs text-[var(--color-status-warn)]">
          Pre-print — not yet published. Under review for NeurIPS 2026.
        </p>
      </div>

      {/* Header */}
      <div className="mb-10">
        <p className="label mb-3">Paper</p>
        <h1 className="text-3xl sm:text-4xl font-mono font-bold tracking-tight text-[var(--color-text-bright)] leading-[1.1] mb-3">
          On the Reasoning Gaps of Large Language Models: A Formal Characterization
        </h1>
        <div className="flex flex-wrap items-center gap-4 mt-5">
          <span className="stat-label">Oddur Sigurdsson</span>
          <span className="text-[var(--color-text-muted)]">&middot;</span>
          <span className="stat-label">NeurIPS 2026</span>
          <span className="font-mono text-xs border border-[var(--color-border)] px-2 py-0.5 text-[var(--color-text-muted)]">Pre-print</span>
        </div>
      </div>

      {/* Download */}
      <div className="border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-6 mb-12">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="font-mono text-sm font-semibold text-[var(--color-text-bright)]">Download</p>
            <p className="text-sm text-[var(--color-text-muted)] mt-1">Full paper with appendices</p>
          </div>
          <a
            href="/papers/reasoning-gaps.pdf"
            className="inline-flex items-center gap-2 font-mono text-xs font-medium uppercase tracking-wider px-5 py-2.5 border-2 border-[var(--color-text-bright)] text-[var(--color-text-bright)] bg-transparent hover:bg-[var(--color-text-bright)] hover:text-[var(--color-bg)] transition-colors hover:no-underline"
          >
            <Download className="h-3.5 w-3.5" />
            PDF
          </a>
        </div>
      </div>

      <hr className="border-[var(--color-border)] mb-12" />

      {/* Abstract */}
      <section className="mb-16">
        <h2 className="text-xl font-mono font-semibold text-[var(--color-text-bright)] mb-6">Abstract</h2>
        <div className="prose">
          <p>
            Large language models exhibit systematic reasoning failures that resist scaling and prompt engineering. We present a formal framework that characterizes these failures through the lens of computational complexity theory. By mapping the transformer architecture to the complexity class TC&#x2070; (constant-depth threshold circuits), we identify six distinct types of reasoning gaps corresponding to specific complexity-theoretic boundaries: sensitivity gaps (AC&#x2070;), depth gaps (TC&#x2070;/NC&#xB9;), serial composition gaps (bounded-depth vs. linear depth), algorithmic gaps (within P), intractability gaps (NP-hard), and architectural gaps (autoregressive constraints).
          </p>
          <p>
            We construct ReasonGap, a diagnostic benchmark suite of nine procedurally generated tasks (B1&ndash;B9), each targeting a specific gap type with controlled difficulty scaling. Evaluating twelve models from five families &mdash; including GPT-4o, o3, Claude Haiku 4.5, Sonnet 4.6, Opus 4.6, Llama 3.1, Qwen 2.5, and Mistral &mdash; across 176,477 instances under direct-answer, chain-of-thought, budget-constrained, and answer-only conditions, we find that chain-of-thought prompting produces a mean accuracy lift of +0.351 for depth and serial composition gaps (Types 2&ndash;3) but only +0.037 for intractability and architectural gaps (Types 5&ndash;6), confirming the framework&apos;s central prediction.
          </p>
          <p>
            The framework provides practitioners with a principled basis for determining when prompting strategies can address reasoning limitations versus when tool augmentation or architectural changes are required.
          </p>
        </div>
      </section>

      {/* Key Results */}
      <section className="mb-16">
        <h2 className="text-xl font-mono font-semibold text-[var(--color-text-bright)] mb-6">Key Results</h2>

        <div className="border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-8 items-center justify-center">
            <div className="text-center">
              <p className="stat-label mb-2">CoT Lift &mdash; Types 2&ndash;3</p>
              <p className="font-mono text-4xl font-bold text-emerald-400 tabular-nums">+0.351</p>
              <p className="stat-label mt-1">depth &amp; serial gaps</p>
            </div>
            <div className="hidden sm:block w-px h-16 bg-[var(--color-border)]"></div>
            <div className="text-center">
              <p className="stat-label mb-2">CoT Lift &mdash; Types 5&ndash;6</p>
              <p className="font-mono text-4xl font-bold text-red-400 tabular-nums">+0.037</p>
              <p className="stat-label mt-1">intractability &amp; architectural gaps</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="border border-[var(--color-border)] bg-[var(--color-bg-surface)] p-4">
            <p className="stat-label mb-1">Models</p>
            <p className="font-mono text-2xl font-bold text-[var(--color-text-bright)] tabular-nums">12</p>
          </div>
          <div className="border border-[var(--color-border)] bg-[var(--color-bg-surface)] p-4">
            <p className="stat-label mb-1">Tasks</p>
            <p className="font-mono text-2xl font-bold text-[var(--color-text-bright)] tabular-nums">9</p>
          </div>
          <div className="border border-[var(--color-border)] bg-[var(--color-bg-surface)] p-4">
            <p className="stat-label mb-1">Conditions</p>
            <p className="font-mono text-2xl font-bold text-[var(--color-text-bright)] tabular-nums">4</p>
          </div>
          <div className="border border-[var(--color-border)] bg-[var(--color-bg-surface)] p-4">
            <p className="stat-label mb-1">Instances</p>
            <p className="font-mono text-2xl font-bold text-[var(--color-text-bright)] tabular-nums">176K</p>
          </div>
        </div>
      </section>

      {/* Taxonomy overview */}
      <section className="mb-16">
        <h2 className="text-xl font-mono font-semibold text-[var(--color-text-bright)] mb-6">Gap Taxonomy</h2>
        <div className="space-y-0 divide-y divide-[var(--color-border)] border border-[var(--color-border)]">
          <div className="flex items-start gap-4 p-4 bg-[var(--color-bg-elevated)]">
            <span className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5 shrink-0 w-8">T1</span>
            <div className="flex-1">
              <p className="font-mono text-sm font-semibold text-[var(--color-text-bright)]">Sensitivity Gap</p>
              <p className="text-xs text-[var(--color-text-muted)] mt-0.5">AC&#x2070; boundary &mdash; CoT helps</p>
            </div>
            <span className="font-mono text-xs text-emerald-400 shrink-0">fixable</span>
          </div>
          <div className="flex items-start gap-4 p-4 bg-[var(--color-bg-elevated)]">
            <span className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5 shrink-0 w-8">T2</span>
            <div className="flex-1">
              <p className="font-mono text-sm font-semibold text-[var(--color-text-bright)]">Depth Gap</p>
              <p className="text-xs text-[var(--color-text-muted)] mt-0.5">TC&#x2070;/NC&#xB9; boundary &mdash; O(log n) CoT</p>
            </div>
            <span className="font-mono text-xs text-emerald-400 shrink-0">fixable</span>
          </div>
          <div className="flex items-start gap-4 p-4 bg-[var(--color-bg-elevated)]">
            <span className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5 shrink-0 w-8">T3</span>
            <div className="flex-1">
              <p className="font-mono text-sm font-semibold text-[var(--color-text-bright)]">Serial Composition</p>
              <p className="text-xs text-[var(--color-text-muted)] mt-0.5">Needs O(n) steps &mdash; O(n) CoT</p>
            </div>
            <span className="font-mono text-xs text-emerald-400 shrink-0">fixable</span>
          </div>
          <div className="flex items-start gap-4 p-4 bg-[var(--color-bg-elevated)]">
            <span className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5 shrink-0 w-8">T4</span>
            <div className="flex-1">
              <p className="font-mono text-sm font-semibold text-[var(--color-text-bright)]">Algorithmic Gap</p>
              <p className="text-xs text-[var(--color-text-muted)] mt-0.5">Complex within P &mdash; tools better</p>
            </div>
            <span className="font-mono text-xs text-amber-400 shrink-0">partial</span>
          </div>
          <div className="flex items-start gap-4 p-4 bg-[var(--color-bg-elevated)]">
            <span className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5 shrink-0 w-8">T5</span>
            <div className="flex-1">
              <p className="font-mono text-sm font-semibold text-[var(--color-text-bright)]">Intractability Gap</p>
              <p className="text-xs text-[var(--color-text-muted)] mt-0.5">NP-hard &mdash; fundamentally hard</p>
            </div>
            <span className="font-mono text-xs text-red-400 shrink-0">unfixable</span>
          </div>
          <div className="flex items-start gap-4 p-4 bg-[var(--color-bg-elevated)]">
            <span className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5 shrink-0 w-8">T6</span>
            <div className="flex-1">
              <p className="font-mono text-sm font-semibold text-[var(--color-text-bright)]">Architectural Gap</p>
              <p className="text-xs text-[var(--color-text-muted)] mt-0.5">Autoregressive constraint &mdash; structural</p>
            </div>
            <span className="font-mono text-xs text-red-400 shrink-0">unfixable</span>
          </div>
        </div>
      </section>

      {/* Citation */}
      <section className="mb-12">
        <h2 className="text-xl font-mono font-semibold text-[var(--color-text-bright)] mb-6">Citation</h2>
        <pre className="text-xs text-[var(--color-text-secondary)] !bg-[var(--color-bg-surface)]">{`@article{sigurdsson2026reasoning,
  title   = {On the Reasoning Gaps of Large Language Models:
             A Formal Characterization},
  author  = {Sigurdsson, Oddur},
  journal = {Preprint},
  year    = {2026}
}`}</pre>
      </section>

      {/* Links */}
      <hr className="border-[var(--color-border)] mb-8" />
      <div className="flex gap-6">
        <a href="/papers/reasoning-gaps.pdf" className="label hover:text-[var(--color-text-bright)] transition-colors hover:no-underline flex items-center gap-1.5">
          <Download className="h-3 w-3" />
          PDF
        </a>
        <Link href="/research/reasoning-gaps" className="label hover:text-[var(--color-text-bright)] transition-colors hover:no-underline flex items-center gap-1.5">
          <BookOpen className="h-3 w-3" />
          Explainer
        </Link>
        <Link href="/dashboard/project/reasoning-gaps" className="label hover:text-[var(--color-text-bright)] transition-colors hover:no-underline flex items-center gap-1.5">
          <BarChart3 className="h-3 w-3" />
          Dashboard
        </Link>
        <Link href="/papers" className="label hover:text-[var(--color-text-bright)] transition-colors hover:no-underline flex items-center gap-1.5">
          <ArrowLeft className="h-3 w-3" />
          All Papers
        </Link>
      </div>

    </div>
  );
}
