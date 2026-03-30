import { LandingShell } from '@/components/landing/landing-shell';

const papers = [
  {
    title: 'On the Reasoning Gaps of Large Language Models',
    subtitle: 'A Formal Characterization',
    venue: 'NeurIPS 2026',
    status: 'Pre-Print',
    href: '/papers/reasoning-gaps',
  },
  {
    title: 'The Computational Complexity of Verifying LLM Outputs',
    venue: 'ICLR 2027',
    status: 'In Progress',
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

const VPS_API_URL = process.env.VPS_API_URL ?? 'http://localhost:3001';
const VPS_API_KEY = process.env.VPS_API_KEY ?? '';

async function fetchHealth() {
  try {
    const res = await fetch(`${VPS_API_URL}/api/health`, { cache: 'no-store' });
    if (!res.ok) return null;
    return JSON.parse(await res.text());
  } catch { return null; }
}

async function fetchProjects() {
  try {
    const res = await fetch(`${VPS_API_URL}/api/projects`, {
      headers: { 'X-Api-Key': VPS_API_KEY },
      cache: 'no-store',
    });
    if (!res.ok) return [];
    const data = JSON.parse(await res.text());
    return Array.isArray(data) ? data : data.projects ?? [];
  } catch { return []; }
}

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  const [health, projects] = await Promise.all([fetchHealth(), fetchProjects()]);
  const activeProjects = projects.filter((p: { status: string }) => p.status === 'active');

  return (
    <LandingShell
      health={health}
      projects={activeProjects}
      papers={papers}
      posts={posts}
    />
  );
}
