import Link from 'next/link';
import { BarChart3, FileText } from 'lucide-react';

export default function ReasoningGapsExplainerPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 pt-16 pb-24">

      {/* Header */}
      <div className="mb-12">
        <p className="label mb-3">Research Explainer</p>
        <h1 className="text-3xl sm:text-4xl font-mono font-bold tracking-tight text-[var(--color-text-bright)] leading-[1.1] mb-4">
          On the Reasoning Gaps of Large Language Models
        </h1>
        <p className="text-[var(--color-text-secondary)] leading-relaxed max-w-2xl">
          A formal characterization of why LLMs fail at specific reasoning tasks, which failures chain-of-thought can fix, and which are fundamentally beyond reach.
        </p>
        <div className="flex gap-4 mt-5 stat-label">
          <span>NeurIPS 2026</span>
          <span>&middot;</span>
          <span>Oddur Sigurdsson</span>
        </div>
      </div>

      <hr className="border-[var(--color-border)] mb-12" />

      {/* The Idea */}
      <section className="prose mb-16">
        <h2 className="!border-0 !pt-0 !mt-0">The Problem</h2>
        <p>
          LLMs fail at certain types of reasoning &mdash; they can&apos;t reliably reverse strings, track state through long chains, or solve SAT problems. Everyone knows this, but nobody has a unified explanation for <em>why</em> they fail at these specific things and not others.
        </p>

        <h2>The Insight</h2>
        <p>
          Transformers, architecturally, are constant-depth circuits. No matter how big you make the model, a single forward pass computes everything in parallel through a fixed number of layers. This puts a hard ceiling on what they can compute in one shot &mdash; formally, they live in a complexity class called <strong>TC&#x2070;</strong> (constant-depth threshold circuits).
        </p>
        <p>
          Some problems require <em>sequential</em> depth that a parallel architecture fundamentally can&apos;t provide. Sorting a long list requires stepping through it. Evaluating deeply nested boolean expressions requires resolving inner brackets first. These aren&apos;t just &quot;hard problems&quot; &mdash; they&apos;re problems whose structure <em>mismatches the architecture</em>.
        </p>

        <h2>The Taxonomy</h2>
        <p>
          The paper maps six types of reasoning failures to specific complexity-theoretic boundaries:
        </p>
      </section>

      {/* Taxonomy Table */}
      <div className="mb-16">
        <table className="w-full text-sm border-collapse border border-[var(--color-border)]">
          <thead>
            <tr className="bg-[var(--color-bg-elevated)]">
              <th className="px-5 py-3 text-left font-mono text-xs font-semibold text-[var(--color-text-bright)] uppercase tracking-wider">Type</th>
              <th className="px-5 py-3 text-left font-mono text-xs font-semibold text-[var(--color-text-bright)] uppercase tracking-wider">Name</th>
              <th className="px-5 py-3 text-left font-mono text-xs font-semibold text-[var(--color-text-bright)] uppercase tracking-wider">Boundary</th>
              <th className="px-5 py-3 text-left font-mono text-xs font-semibold text-[var(--color-text-bright)] uppercase tracking-wider">CoT Helps?</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-border)]">
            <tr>
              <td className="px-5 py-3 text-[var(--color-text-muted)]">1</td>
              <td className="px-5 py-3 text-[var(--color-text-bright)]">Sensitivity Gap</td>
              <td className="px-5 py-3 text-[var(--color-text-secondary)]">AC&#x2070; boundary</td>
              <td className="px-5 py-3 text-emerald-400">Yes, short CoT</td>
            </tr>
            <tr>
              <td className="px-5 py-3 text-[var(--color-text-muted)]">2</td>
              <td className="px-5 py-3 text-[var(--color-text-bright)]">Depth Gap</td>
              <td className="px-5 py-3 text-[var(--color-text-secondary)]">TC&#x2070;/NC&#xB9; boundary</td>
              <td className="px-5 py-3 text-emerald-400">Yes, O(log n) steps</td>
            </tr>
            <tr>
              <td className="px-5 py-3 text-[var(--color-text-muted)]">3</td>
              <td className="px-5 py-3 text-[var(--color-text-bright)]">Serial Composition</td>
              <td className="px-5 py-3 text-[var(--color-text-secondary)]">Needs O(n) steps</td>
              <td className="px-5 py-3 text-emerald-400">Yes, O(n) steps</td>
            </tr>
            <tr>
              <td className="px-5 py-3 text-[var(--color-text-muted)]">4</td>
              <td className="px-5 py-3 text-[var(--color-text-bright)]">Algorithmic Gap</td>
              <td className="px-5 py-3 text-[var(--color-text-secondary)]">Complex within P</td>
              <td className="px-5 py-3 text-amber-400">In theory; tools better</td>
            </tr>
            <tr>
              <td className="px-5 py-3 text-[var(--color-text-muted)]">5</td>
              <td className="px-5 py-3 text-[var(--color-text-bright)]">Intractability Gap</td>
              <td className="px-5 py-3 text-[var(--color-text-secondary)]">NP-hard</td>
              <td className="px-5 py-3 text-red-400">No</td>
            </tr>
            <tr>
              <td className="px-5 py-3 text-[var(--color-text-muted)]">6</td>
              <td className="px-5 py-3 text-[var(--color-text-bright)]">Architectural Gap</td>
              <td className="px-5 py-3 text-[var(--color-text-secondary)]">Autoregressive constraint</td>
              <td className="px-5 py-3 text-red-400">No</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Prediction + Result */}
      <section className="prose mb-16">
        <h2>The Prediction</h2>
        <p>
          CoT should dramatically help on Types 1&ndash;3 (where the model just needs more sequential steps) and barely help on Types 5&ndash;6 (where the problem is fundamentally hard or the architecture itself is the constraint). This is a testable, falsifiable claim.
        </p>

        <h2>The Experiment</h2>
        <p>
          9 diagnostic benchmarks (one per gap type), each with procedurally generated instances at controlled difficulty levels. Tested across 11 models &mdash; GPT-4o, GPT-4o-mini, Claude Haiku 4.5, Claude Sonnet 4.6, o3, Llama 3.1 8B &amp; 70B, Qwen 2.5 7B &amp; 72B, Ministral 8B, Mistral Small 24B &mdash; under three conditions: direct answer, chain-of-thought, and budget-limited CoT. 148,068 total evaluations.
        </p>

        <h2>The Result</h2>
      </section>

      {/* Result Callout */}
      <div className="border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-6 mb-16">
        <div className="flex flex-col sm:flex-row gap-8 items-center justify-center">
          <div className="text-center">
            <p className="stat-label mb-2">CoT Lift &mdash; Types 1&ndash;3</p>
            <p className="font-mono text-4xl font-bold text-emerald-400 tabular-nums">+0.340</p>
            <p className="stat-label mt-1">depth &amp; serial gaps</p>
          </div>
          <div className="hidden sm:block w-px h-16 bg-[var(--color-border)]"></div>
          <div className="text-center">
            <p className="stat-label mb-2">CoT Lift &mdash; Types 5&ndash;6</p>
            <p className="font-mono text-4xl font-bold text-red-400 tabular-nums">+0.086</p>
            <p className="stat-label mt-1">intractability &amp; architectural gaps</p>
          </div>
        </div>
        <p className="font-mono text-xs text-[var(--color-text-muted)] text-center mt-6">
          The theory predicts exactly which failures are fixable and which aren&apos;t. The data matches.
        </p>
      </div>

      {/* Why It Matters */}
      <section className="prose mb-16">
        <h2>Why It Matters</h2>
        <p>
          Instead of saying &quot;LLMs are bad at reasoning,&quot; you can now say precisely <em>which</em> reasoning they&apos;re bad at, <em>why</em> (complexity-theoretic mismatch), and <em>whether</em> prompting techniques like CoT can help. It gives practitioners a principled framework for knowing when to use chain-of-thought vs. tool use vs. &quot;this just won&apos;t work.&quot;
        </p>
      </section>

      <hr className="border-[var(--color-border)] mb-12" />

      {/* Glossary */}
      <section className="mb-8">
        <h2 className="text-xl font-mono font-semibold text-[var(--color-text-bright)] mb-8">Glossary</h2>

        <div className="space-y-0 divide-y divide-[var(--color-border)]">

          <div className="py-5 first:pt-0">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">TC&#x2070; &mdash; Threshold Circuit, depth 0</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">The set of problems solvable by constant-depth circuits with AND, OR, NOT, and MAJORITY gates. This is what a transformer&apos;s forward pass can compute. &quot;Constant depth&quot; means adding more parameters doesn&apos;t add more sequential steps.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">NC&#xB9; &mdash; Nick&apos;s Class, depth 1</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">Problems solvable by logarithmic-depth circuits. Slightly more powerful than TC&#x2070; &mdash; includes things like evaluating boolean formulas and arithmetic expressions. Requires sequential depth that grows with input size.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">AC&#x2070; &mdash; Alternating Circuit, depth 0</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">Weaker than TC&#x2070; &mdash; constant-depth circuits <em>without</em> MAJORITY gates. Can&apos;t even compute parity (is the count of 1s odd or even?). Relevant because some transformer limitations trace to this boundary.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">P &mdash; Polynomial Time</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">Everything solvable in polynomial time by a standard sequential computer. CoT with polynomial steps can theoretically reach P.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">NP-hard</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">Problems where no known polynomial-time algorithm exists (e.g., 3-SAT). Neither more layers nor more CoT steps will reliably solve these.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">CoT &mdash; Chain-of-Thought</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">Prompting the model to show its work step by step. Mechanistically, each generated token is an extra compute step, giving the model sequential depth it otherwise lacks.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">Forward Pass</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">One run through all the transformer&apos;s layers, producing a single output token. Fixed depth regardless of model size &mdash; a 7B model and a 400B model both do the same number of sequential steps per token.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">Complexity Class</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">A category of problems grouped by the computational resources (time, depth, parallelism) needed to solve them. The hierarchy AC&#x2070; &sub; TC&#x2070; &sube; NC&#xB9; &sub; P &sube; NP defines increasingly powerful levels of computation.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">Sensitivity</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">How many input bits can flip the output when changed individually. High-sensitivity functions (like parity) are hard for shallow circuits, which is why transformers struggle with them.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">Serial Composition</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">Chaining operations where each step depends on the previous one &mdash; e.g., applying a function k times. Requires k sequential steps, which a constant-depth architecture can&apos;t do in one pass.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">Autoregressive Generation</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">How LLMs produce text &mdash; one token at a time, left to right. This creates architectural constraints (e.g., can&apos;t &quot;look ahead&quot;), which is the source of Type 6 gaps like string reversal.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">Phase Transition (3-SAT)</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">At a specific clause-to-variable ratio (~4.27), SAT problems shift from almost always solvable to almost always unsolvable. The benchmark generates instances at this boundary where problems are hardest.</p>
          </div>

          <div className="py-5">
            <h3 className="font-mono text-sm font-semibold text-[var(--color-text-bright)] mb-1">ReasonGap Benchmark</h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">The diagnostic suite built for this paper. 9 tasks (B1&ndash;B9), procedurally generated to avoid training contamination, each targeting a specific complexity boundary with tunable difficulty.</p>
          </div>

        </div>
      </section>

      {/* Footer links */}
      <hr className="border-[var(--color-border)] mb-8" />
      <div className="flex gap-6">
        <Link href="/dashboard/project/reasoning-gaps" className="label hover:text-[var(--color-text-bright)] transition-colors hover:no-underline flex items-center gap-1.5">
          <BarChart3 className="h-3 w-3" />
          Dashboard
        </Link>
        <Link href="/papers" className="label hover:text-[var(--color-text-bright)] transition-colors hover:no-underline flex items-center gap-1.5">
          <FileText className="h-3 w-3" />
          Papers
        </Link>
      </div>

    </div>
  );
}
