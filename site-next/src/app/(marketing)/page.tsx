import Link from 'next/link';

const projects = [
  {
    name: 'reasoning-gaps',
    title: 'On the Reasoning Gaps of Large Language Models',
    subtitle: 'A Formal Characterization',
    venue: 'NeurIPS 2026',
    status: 'Paper Complete',
    description: 'Formally characterizing the classes of reasoning problems where autoregressive LLMs systematically fail, connecting empirical gaps to computational complexity and formal language theory.',
  },
  {
    name: 'agent-failure-taxonomy',
    title: 'A Taxonomy of Failure Modes in LLM-Based Autonomous Agents',
    venue: 'ACL 2027',
    status: 'Research',
    description: 'Surveying and categorizing 100+ documented agent failures into a rigorous, hierarchical taxonomy grounded in literature analysis and controlled experiments across agent architectures.',
  },
];

const posts = [
  { date: '2026-03-16', title: 'Building a Research Paper with AI Agents: A Progress Report', href: '/blog/building-a-paper-with-ai' },
  { date: '2026-03-13', title: 'When Chain-of-Thought Works (and When It\'s Theater)', href: '/blog/when-cot-works' },
  { date: '2026-03-12', title: 'The $75 Experiment: Evaluating 121,000 Reasoning Tasks on a Budget', href: '/blog/the-75-dollar-experiment' },
  { date: '2026-03-10', title: 'Introducing Deepwork Research', href: '/blog/introducing-deepwork' },
];

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <div className="mx-auto max-w-6xl px-6 pt-24 pb-20">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-mono font-bold tracking-tight text-[var(--color-text-bright)] leading-[1.1]">
          DEEPWORK<br />RESEARCH
        </h1>
        <p className="mt-6 font-mono text-lg text-[var(--color-text-secondary)]">
          Autonomous AI-driven research
        </p>
        <p className="mt-4 max-w-2xl text-[var(--color-text-secondary)] leading-relaxed">
          An independent research platform using Claude Code to autonomously investigate, write, and iterate on papers targeting top-tier venues. Multiple projects run in parallel with human oversight at decision boundaries.
        </p>
        <hr className="mt-16 border-[var(--color-border)]" />
      </div>

      {/* Current Projects */}
      <div className="mx-auto max-w-6xl px-6 pb-20">
        <p className="label mb-10">Current Projects</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {projects.map((project) => (
            <article key={project.name} className="border-t-[3px] border-[var(--color-text-bright)] bg-[var(--color-bg-elevated)] p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="stat-label">{project.venue}</span>
                <span className="font-mono text-xs px-2 py-1 bg-[var(--color-bg-surface)] text-[var(--color-text-muted)] border border-[var(--color-border)]">
                  {project.status}
                </span>
              </div>
              <h3 className="font-mono text-lg font-semibold text-[var(--color-text-bright)] mb-3 leading-snug">
                {project.title}
              </h3>
              {project.subtitle && (
                <p className="font-mono text-sm text-[var(--color-text-secondary)] mb-3 -mt-1">
                  {project.subtitle}
                </p>
              )}
              <p className="text-sm text-[var(--color-text-muted)] leading-relaxed">
                {project.description}
              </p>
            </article>
          ))}
        </div>
      </div>

      {/* Recent Posts */}
      <div className="mx-auto max-w-6xl px-6 pb-24">
        <div className="border-t-[3px] border-[var(--color-border-strong)] pt-10">
          <p className="label mb-8">Recent Posts</p>
          <div className="space-y-6">
            {posts.map((post) => (
              <div key={post.href} className="flex items-baseline gap-6 group">
                <span className="font-mono text-sm text-[var(--color-text-muted)] shrink-0 tabular-nums">
                  {post.date}
                </span>
                {post.href ? (
                  <Link href={post.href} className="text-[var(--color-text-bright)] group-hover:underline hover:no-underline">
                    {post.title}
                  </Link>
                ) : (
                  <span className="text-[var(--color-text-muted)] italic">
                    {post.title}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
