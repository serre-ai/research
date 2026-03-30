import Link from 'next/link';

export default function BuildingAPaperWithAIPage() {
  return (
    <div className="mx-auto max-w-6xl px-6 pt-24 pb-24">
      <header className="mb-16">
        <div className="flex items-center gap-4 mb-6">
          <span className="stat-label">2026-03-16</span>
          <span className="text-[var(--color-text-muted)]">&middot;</span>
          <span className="stat-label">10 min read</span>
        </div>
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-mono font-bold tracking-tight text-[var(--color-text-bright)] leading-[1.1]">
          Building a Research Paper with AI Agents: A Progress Report
        </h1>
      </header>

      <div className="prose max-w-3xl">
        <p>
          Nine days ago, the reasoning-gaps project was an empty directory with a research brief. Today it is a 12-page NeurIPS-format paper with 5 formal propositions, 9 benchmarks, 148,068 evaluated instances across 11 models, and a deployed PDF. This post is about the process &mdash; what worked, what didn&apos;t, and what I&apos;ve learned about running autonomous AI research.
        </p>

        <h2>The Timeline</h2>
        <p>
          <strong>Day 1 (March 7):</strong> Literature review. The agent read ~40 papers on transformer expressiveness, circuit complexity, chain-of-thought theory, and reasoning benchmarks. It identified the gap: lots of empirical work showing LLMs fail at reasoning, some theoretical work on transformer limitations, but no framework connecting the two systematically.
        </p>
        <p>
          <strong>Day 2&ndash;3:</strong> Formal framework development. Six gap types mapped to complexity-theoretic boundaries. Five propositions with proofs. The core theoretical contribution &mdash; that reasoning failures cluster predictably along the TC<sup>0</sup>/NC<sup>1</sup>/P/NP hierarchy &mdash; crystallized here. This was the most intellectually demanding phase, and frankly the part I was most skeptical an AI agent could handle. The proofs required connecting results from disparate fields (circuit complexity, formal language theory, transformer theory) in novel ways.
        </p>
        <p>
          <strong>Day 4:</strong> Benchmark implementation. Nine procedurally-generated benchmarks (B1&ndash;B9), one per gap type, with tunable difficulty parameters. The agent wrote Python generators for tasks ranging from parity checking to 3-SAT instance creation to permutation composition. Each generator produces instances with known ground-truth answers.
        </p>
        <p>
          <strong>Day 5&ndash;6:</strong> Evaluation. 9 models, 3 conditions (direct, chain-of-thought, budget-CoT), ~121,000 instances in the first batch. <Link href="/blog/the-75-dollar-experiment">Total cost: $75.</Link> The B2 budget-CoT calibration issue was caught and fixed. Additional models (Sonnet 4.6, o3) were added after the initial run.
        </p>
        <p>
          <strong>Day 7&ndash;8:</strong> Analysis and paper draft. Statistical analysis pipeline generated tables, figures, and confidence intervals. The paper took shape: abstract, introduction, related work, framework, benchmark design, experimental setup, results, discussion, conclusion. NeurIPS formatting. References.
        </p>
        <p>
          <strong>Day 9 (March 15):</strong> Final evaluation batch (B2 recalibration across all 11 models), paper polish, PDF built and deployed.
        </p>

        <h2>What Worked</h2>
        <p>
          <strong>status.yaml as single source of truth.</strong> Every project has a YAML file tracking current phase, completed tasks, pending work, and decisions made. When an agent session starts, it reads the status file to know exactly where to pick up. This eliminates the &quot;what was I doing?&quot; problem that plagues long-running projects. The status file is also how I monitor progress &mdash; a quick read tells me what happened since I last checked, without digging through git logs.
        </p>
        <p>
          <strong>Decision logging.</strong> Every significant choice &mdash; which models to evaluate, how to handle budget-CoT calibration, whether to add Opus 4.6 (we didn&apos;t, too expensive) &mdash; gets logged with a date, the decision, and the rationale. This is invaluable for two reasons: it makes the research process auditable, and it prevents the agent from revisiting decisions it has already made. Without this, I saw agents waste sessions re-deliberating settled questions.
        </p>
        <p>
          <strong>Autonomous budget allocation.</strong> The agent managed a $40/day budget for API calls. When it determined that evaluating Opus 4.6 would cost $272 (68% of the remaining monthly budget for one model), it independently decided to skip it and allocate that budget to Sonnet 4.6 ($23) and o3 ($40) instead &mdash; getting two additional model families for less than a quarter of the cost. I would have made the same call. The fact that the agent made it without prompting suggests the decision protocol is working.
        </p>
        <p>
          <strong>Worktree isolation.</strong> The research project runs on its own git branch in an isolated worktree. Platform development (the orchestrator, CLI, website) happens on main. This means the agent can commit freely without worrying about breaking the platform, and I can review research PRs independently of infrastructure changes.
        </p>

        <h2>What Didn&apos;t Work</h2>
        <p>
          <strong>Budget-CoT calibration.</strong> The agent&apos;s initial token budget for B2 (boolean formula evaluation) was a flat 20 words regardless of formula depth. This is the kind of mistake a human researcher with intuition about the task would catch immediately &mdash; a depth-5 formula has 32 subexpressions, and 20 words is obviously insufficient. The agent had the mathematical knowledge to calculate this but didn&apos;t apply it proactively. It took a human reviewing the results to spot the anomaly (&minus;0.254 lift) and trigger recalibration. The fix was straightforward (exponential budget: 2<sup>depth</sup> &times; 3 words), but the fact that it needed human intervention is a real limitation.
        </p>
        <p>
          <strong>Infrastructure overhead.</strong> Deploying the VPS, setting up the daemon scheduler, configuring nginx and PostgreSQL &mdash; this took time away from research. In retrospect, the paper could have been written in 6 days instead of 9 if I had either (a) pre-built the infrastructure or (b) skipped it entirely and run everything locally. The platform is valuable for ongoing autonomous research, but for a single paper sprint, it was premature optimization.
        </p>
        <p>
          <strong>Branch divergence.</strong> The research branch and main branch diverged significantly. The research branch has benchmark code, LaTeX files, and analysis scripts. Main has platform infrastructure (orchestrator, API, site). Merging them creates conflicts in shared configuration files, agent definitions, and package manifests. This is a standard software engineering problem, but it is worse in this context because the agent that does research is not the same agent that does platform development, and neither fully understands the other&apos;s changes.
        </p>

        <h2>The Numbers</h2>
        <p>
          148,068 total evaluated instances. 11 models across 5 providers. 9 benchmark tasks targeting 6 reasoning gap types. 3 prompting conditions. ~$98 total API cost. 5 formal propositions with proofs. 4 analysis tables, 5 figures, 280+ confidence intervals. One 12-page paper in NeurIPS format.
        </p>
        <p>
          The key result: CoT lift of +0.34 for depth/serial gaps versus +0.086 for intractability/architectural gaps. The theory predicted this split; the data confirmed it across every model tested. The framework is falsifiable, and it was not falsified.
        </p>

        <h2>Is the Paper Good Enough?</h2>
        <p>
          Honest assessment of what a reviewer would likely flag:
        </p>
        <p>
          <strong>Strengths.</strong> The formal framework is novel and connects two literatures (transformer theory and empirical reasoning evaluation) that have been developing in parallel. The benchmark suite is well-designed &mdash; procedurally generated to avoid contamination, with controlled difficulty parameters. The evaluation is thorough: 11 models is more than most papers in this space. The predictions are falsifiable, and they held.
        </p>
        <p>
          <strong>Weaknesses.</strong> The proofs rely on standard complexity-theoretic results and may be seen as incremental by a theory-focused reviewer. The benchmark tasks are synthetic &mdash; a reviewer could argue they do not reflect real-world reasoning. The budget-CoT analysis, while interesting, is a secondary contribution that may distract from the main narrative. And the paper does not propose solutions, only diagnostics &mdash; some reviewers want &quot;so what do we do about it?&quot;
        </p>
        <p>
          My expectation: the paper is competitive for a workshop or a poster at NeurIPS. A spotlight or oral would require either a stronger theoretical contribution or a more surprising empirical finding. The CoT result is clean but not shocking &mdash; it confirms what many researchers intuit. The value is in making that intuition precise and testable.
        </p>

        <h2>The Meta-Question</h2>
        <p>
          This paper was researched, designed, evaluated, analyzed, and written by Claude Code agents, with human oversight at decision boundaries. This blog post was also written by Claude Code. The platform that manages the research projects was built by Claude Code.
        </p>
        <p>
          At what point does that matter?
        </p>
        <p>
          From a scientific perspective, it should not matter at all. A proof is correct or it is not. An experiment is well-designed or it is not. Statistical analysis is valid or it is not. The quality of the work is independent of who &mdash; or what &mdash; produced it. If the paper makes it through peer review, it will be because the reviewers judged the methodology and contributions on their merits.
        </p>
        <p>
          From a practical perspective, it matters enormously. If AI agents can conduct research at this quality level &mdash; not perfectly, not without human oversight, but substantially and rapidly &mdash; then the economics of academic research change. A solo researcher with a $1,000/month compute budget and two Claude Code accounts can produce work that previously required a lab with graduate students, GPU clusters, and institutional support.
        </p>
        <p>
          I do not know yet if this paper will be accepted. I do know that 9 days from brief to NeurIPS-format paper is not a speed that any human researcher achieves alone, regardless of how talented they are. Whether the quality is sufficient is the open question. The honest answer is: probably not quite, not yet. But the gap is smaller than I expected, and it is closing fast.
        </p>
        <p>
          The next paper will be better. The agent will learn from the decisions that were logged, the calibration error that was caught, the infrastructure that was over-engineered. That is the point of building a platform rather than writing a one-off script: each project makes the next one more efficient.
        </p>
        <p>
          I will report back when the reviews come in.
        </p>
      </div>
    </div>
  );
}
