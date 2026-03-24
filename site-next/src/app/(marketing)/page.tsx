import {
  TerminalHero,
  StatusBar,
  ProjectsTable,
  PapersList,
  ActivityLog,
  LandingFooter,
} from '@/components/landing';

// ── Static data ─────────────────────────────────────────

const papers = [
  {
    title: 'On the Reasoning Gaps of Large Language Models',
    subtitle: 'A Formal Characterization',
    venue: 'NeurIPS 2026',
    status: 'Pre-Print',
    description: '176K evaluations, 12 models, 9 benchmark tasks',
    href: '/papers/reasoning-gaps',
  },
  {
    title: 'The Computational Complexity of Verifying LLM Outputs',
    venue: 'ICLR 2027',
    status: 'In Progress',
    href: '/research/reasoning-gaps',
  },
  {
    title: 'A Taxonomy of Failure Modes in LLM-Based Autonomous Agents',
    venue: 'ACL 2027',
    status: 'In Progress',
  },
];

const posts = [
  { date: '2026-03-16', title: 'Building a Research Paper with AI Agents', href: '/blog/building-a-paper-with-ai' },
  { date: '2026-03-13', title: 'When Chain-of-Thought Works (and When It\'s Theater)', href: '/blog/when-cot-works' },
  { date: '2026-03-12', title: 'The $75 Experiment: 121,000 Reasoning Tasks', href: '/blog/the-75-dollar-experiment' },
  { date: '2026-03-10', title: 'Introducing Deepwork Research', href: '/blog/introducing-deepwork' },
];

// ── Server-side data fetching ───────────────────────────

const VPS_API_URL = process.env.VPS_API_URL ?? 'http://localhost:3001';
const VPS_API_KEY = process.env.VPS_API_KEY ?? '';

async function fetchHealth() {
  try {
    const res = await fetch(`${VPS_API_URL}/api/health`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    const text = await res.text();
    return JSON.parse(text);
  } catch {
    return null;
  }
}

async function fetchProjects() {
  try {
    const res = await fetch(`${VPS_API_URL}/api/projects`, {
      headers: { 'X-Api-Key': VPS_API_KEY },
      next: { revalidate: 300 },
    });
    if (!res.ok) return [];
    const text = await res.text();
    const data = JSON.parse(text);
    return Array.isArray(data) ? data : data.projects ?? [];
  } catch {
    return [];
  }
}

// Force dynamic rendering — don't try to fetch at build time
export const dynamic = 'force-dynamic';

// ── Page ────────────────────────────────────────────────

export default async function HomePage() {
  const [health, projects] = await Promise.all([
    fetchHealth(),
    fetchProjects(),
  ]);

  const activeProjects = projects.filter(
    (p: { status: string }) => p.status === 'active',
  );

  return (
    <div className="mx-auto max-w-4xl px-6 space-y-6">
      <TerminalHero />
      <StatusBar health={health} projectCount={activeProjects.length} />
      <ProjectsTable projects={activeProjects} />
      <PapersList papers={papers} />
      <ActivityLog posts={posts} />
      <LandingFooter />
    </div>
  );
}
