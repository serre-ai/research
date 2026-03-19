import Link from 'next/link';

const posts = [
  {
    title: 'Building a Research Paper with AI Agents: A Progress Report',
    date: '2026-03-16',
    excerpt: 'The reasoning-gaps paper went from zero to NeurIPS-ready in 9 days. What worked, what didn\'t, and what I learned about autonomous AI research.',
    href: '/blog/building-a-paper-with-ai',
  },
  {
    title: 'When Chain-of-Thought Works (and When It\'s Theater)',
    date: '2026-03-13',
    excerpt: 'CoT lifts accuracy by +0.34 on depth-limited problems and +0.086 on intractable ones. A formal framework for predicting when step-by-step reasoning actually helps.',
    href: '/blog/when-cot-works',
  },
  {
    title: 'The $75 Experiment: Evaluating 121,000 Reasoning Tasks on a Budget',
    date: '2026-03-12',
    excerpt: 'How we evaluated 9 models across 121K instances for ~$75 total, the decision to use OpenRouter over rented GPUs, and the budget-CoT calibration disaster.',
    href: '/blog/the-75-dollar-experiment',
  },
  {
    title: 'Introducing Deepwork Research',
    date: '2026-03-10',
    excerpt: 'What happens when you give AI agents the autonomy to conduct research 24/7? An introduction to the Deepwork platform and our first research projects.',
    href: '/blog/introducing-deepwork',
  },
];

export default function BlogPage() {
  return (
    <>
      <div className="mx-auto max-w-6xl px-6 pt-24 pb-16">
        <h1 className="font-mono text-[var(--color-text-bright)]">BLOG</h1>
        <p className="mt-4 text-lg text-[var(--color-text-secondary)] max-w-2xl">
          Notes on AI research, methodology, and building autonomous research systems
        </p>
      </div>

      <div className="mx-auto max-w-6xl px-6 pb-24">
        <div className="flex flex-col gap-0">
          {posts.map((post) => (
            <Link key={post.href} href={post.href} className="group block border-t border-[var(--color-border)] py-8 hover:no-underline">
              <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                <time className="font-mono text-sm text-[var(--color-text-muted)] shrink-0 sm:w-32 sm:pt-0.5 tabular-nums">
                  {post.date}
                </time>
                <div className="flex-1">
                  <h3 className="font-mono font-semibold text-[var(--color-text-bright)] group-hover:underline leading-snug">
                    {post.title}
                  </h3>
                  <p className="mt-2 text-[var(--color-text-secondary)] text-sm leading-relaxed">
                    {post.excerpt}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
