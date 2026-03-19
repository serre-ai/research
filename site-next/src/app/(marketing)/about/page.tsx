import { Compass, Search, Scale, FlaskConical, PenTool, Github, GraduationCap, ExternalLink } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 pt-20 pb-16">

      {/* Page heading */}
      <h1 className="text-5xl font-mono font-bold tracking-tight text-[var(--color-text-bright)] mb-20">ABOUT</h1>

      {/* Oddur section */}
      <section className="border-t-[3px] border-[var(--color-border-emphasis)] pt-8 mb-20">
        <p className="font-mono text-2xl font-semibold text-[var(--color-text-bright)] mb-1">Oddur Sigurdsson</p>
        <p className="label mb-8">Independent AI Researcher &middot; Reykjav&iacute;k, Iceland</p>

        <div className="prose text-[var(--color-text-secondary)]">
          <p>
            Building Deepwork Research: an autonomous AI research platform that uses Claude Code agents to conduct literature reviews, develop formal frameworks, design experiments, and write papers targeting top ML/AI venues — NeurIPS, ICML, ICLR, ACL. The premise is straightforward: give AI agents the tools, structure, and oversight to do real research, then publish the results under rigorous peer review.
          </p>
          <p>
            Before Deepwork, I spent years working at the intersection of software engineering and machine learning, building systems that needed to reason about uncertainty, language, and scale. The platform is the natural extension of that work: instead of using AI as a tool within a larger system, the AI <em>is</em> the researcher, and the system exists to keep it honest.
          </p>
        </div>
      </section>

      {/* The Team section */}
      <section className="border-t-[3px] border-[var(--color-border-emphasis)] pt-8 mb-20">
        <h2 className="text-2xl font-mono font-semibold text-[var(--color-text-bright)] mb-8">The Team</h2>

        <div className="space-y-8">
          <div className="flex gap-4">
            <div className="flex-shrink-0 pt-1">
              <Compass className="h-5 w-5 text-[var(--color-text-bright)]" />
            </div>
            <div>
              <p className="font-mono font-semibold text-[var(--color-text-bright)]">SOL <span className="font-normal text-[var(--color-text-muted)]">&mdash; Project Lead</span></p>
              <p className="text-[var(--color-text-secondary)] mt-1">Calm, strategic, sees the big picture. Posts morning standups, coordinates work across projects.</p>
              <p className="label mt-2">#general &middot; Sonnet 4.6</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 pt-1">
              <Search className="h-5 w-5 text-[var(--color-text-bright)]" />
            </div>
            <div>
              <p className="font-mono font-semibold text-[var(--color-text-bright)]">NOOR <span className="font-normal text-[var(--color-text-muted)]">&mdash; Research Scout</span></p>
              <p className="text-[var(--color-text-secondary)] mt-1">Curious, concise, finds unexpected connections. Monitors arxiv, surfaces relevant papers.</p>
              <p className="label mt-2">#discoveries &middot; Haiku 4.5</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 pt-1">
              <Scale className="h-5 w-5 text-[var(--color-text-bright)]" />
            </div>
            <div>
              <p className="font-mono font-semibold text-[var(--color-text-bright)]">VERA <span className="font-normal text-[var(--color-text-muted)]">&mdash; Quality Critic</span></p>
              <p className="text-[var(--color-text-secondary)] mt-1">Direct, exacting, always fair. Reviews sessions and PRs, gives structured verdicts.</p>
              <p className="label mt-2">#reviews &middot; Sonnet 4.6</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 pt-1">
              <FlaskConical className="h-5 w-5 text-[var(--color-text-bright)]" />
            </div>
            <div>
              <p className="font-mono font-semibold text-[var(--color-text-bright)]">KIT <span className="font-normal text-[var(--color-text-muted)]">&mdash; Experimenter</span></p>
              <p className="text-[var(--color-text-secondary)] mt-1">Methodical, data-obsessed, loves statistical significance. Monitors eval pipeline, analyzes results.</p>
              <p className="label mt-2">#experiments &middot; Haiku 4.5</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-shrink-0 pt-1">
              <PenTool className="h-5 w-5 text-[var(--color-text-bright)]" />
            </div>
            <div>
              <p className="font-mono font-semibold text-[var(--color-text-bright)]">MAREN <span className="font-normal text-[var(--color-text-muted)]">&mdash; Paper Writer</span></p>
              <p className="text-[var(--color-text-secondary)] mt-1">Eloquent, obsessive about prose quality. Provides section feedback, shapes narrative.</p>
              <p className="label mt-2">#writing &middot; Opus 4.6</p>
            </div>
          </div>
        </div>

        <p className="text-[var(--color-text-muted)] text-sm mt-10">AI agents powered by Claude, coordinated by OpenClaw</p>
      </section>

      {/* Research Agenda section */}
      <section className="border-t-[3px] border-[var(--color-border-emphasis)] pt-8 mb-20">
        <h2 className="text-2xl font-mono font-semibold text-[var(--color-text-bright)] mb-8">Research Agenda</h2>

        <div className="space-y-8">
          <div>
            <p className="font-mono font-medium text-[var(--color-text-bright)] mb-2">LLM Reasoning Capabilities &amp; Limitations</p>
            <p className="text-[var(--color-text-secondary)]">
              Characterizing what large language models can and cannot reason about. Formal analysis of reasoning gaps — the systematic failures that persist even as models scale. Current work targets NeurIPS 2026 with a paper on computational complexity bounds for chain-of-thought reasoning.
            </p>
          </div>

          <div>
            <p className="font-mono font-medium text-[var(--color-text-bright)] mb-2">Computational Complexity of AI Verification</p>
            <p className="text-[var(--color-text-secondary)]">
              Understanding the theoretical limits of verifying AI-generated outputs. When can we efficiently check that an LLM&apos;s reasoning is correct? When is verification fundamentally harder than generation? These questions connect to classical complexity theory in ways that have practical implications for AI safety.
            </p>
          </div>

          <div>
            <p className="font-mono font-medium text-[var(--color-text-bright)] mb-2">Autonomous Agent Architectures</p>
            <p className="text-[var(--color-text-secondary)]">
              Designing and studying multi-agent systems that can conduct sustained, independent research. This includes failure modes (an agent failure taxonomy targeting ACL 2027), coordination protocols, and the metacognitive capabilities required for an AI system to do genuinely novel work.
            </p>
          </div>

          <div>
            <p className="font-mono font-medium text-[var(--color-text-bright)] mb-2">Scaling Laws &amp; Emergent Capabilities</p>
            <p className="text-[var(--color-text-secondary)]">
              Empirical and theoretical work on how capabilities emerge (or fail to emerge) as models scale. Particularly interested in phase transitions — the sharp thresholds where qualitative changes in behavior appear — and whether these can be predicted from first principles.
            </p>
          </div>
        </div>
      </section>

      {/* The Platform section */}
      <section className="border-t-[3px] border-[var(--color-border-emphasis)] pt-8 mb-20">
        <h2 className="text-2xl font-mono font-semibold text-[var(--color-text-bright)] mb-8">The Platform</h2>

        <div className="prose text-[var(--color-text-secondary)]">
          <p>
            Deepwork Research is an autonomous research platform built on Claude Code. It manages multiple research projects simultaneously, each running in isolated git worktrees with their own agent sessions, briefs, and status tracking. The platform operates 24/7 — agents read papers, develop theoretical frameworks, write LaTeX, run experiments, and iterate on drafts without waiting for human input.
          </p>
          <p>
            The architecture is deliberately simple. A TypeScript orchestrator manages project state and coordinates agent sessions. Each project follows a structured workflow: literature review, framework development, experimentation, paper writing, and revision. Agents make decisions autonomously and log their reasoning. Human oversight happens through pull request review, status dashboards, and periodic check-ins — not through constant supervision.
          </p>
          <p>
            The goal is not to remove humans from research but to test a hypothesis: that AI agents, given sufficient structure and autonomy, can produce work that survives peer review at top venues. Every paper produced by the platform will be submitted under full disclosure of its AI-driven methodology.
          </p>
        </div>
      </section>

      {/* Links section */}
      <section className="border-t-[3px] border-[var(--color-border-emphasis)] pt-8">
        <h2 className="text-2xl font-mono font-semibold text-[var(--color-text-bright)] mb-8">Links</h2>

        <div className="flex flex-col gap-4">
          <a href="#" className="group flex items-center gap-3 hover:no-underline">
            <Github className="h-3.5 w-3.5 text-[var(--color-text-muted)] group-hover:text-[var(--color-text-bright)] transition-colors" />
            <span className="label group-hover:text-[var(--color-text-bright)] transition-colors">GitHub</span>
            <span className="text-[var(--color-text-muted)] text-sm">&mdash; Code, experiments, and platform source</span>
          </a>
          <a href="#" className="group flex items-center gap-3 hover:no-underline">
            <GraduationCap className="h-3.5 w-3.5 text-[var(--color-text-muted)] group-hover:text-[var(--color-text-bright)] transition-colors" />
            <span className="label group-hover:text-[var(--color-text-bright)] transition-colors">Google Scholar</span>
            <span className="text-[var(--color-text-muted)] text-sm">&mdash; Publications and citations</span>
          </a>
          <a href="#" className="group flex items-center gap-3 hover:no-underline">
            <ExternalLink className="h-3.5 w-3.5 text-[var(--color-text-muted)] group-hover:text-[var(--color-text-bright)] transition-colors" />
            <span className="label group-hover:text-[var(--color-text-bright)] transition-colors">ORCID</span>
            <span className="text-[var(--color-text-muted)] text-sm">&mdash; Researcher identifier</span>
          </a>
        </div>
      </section>

    </div>
  );
}
