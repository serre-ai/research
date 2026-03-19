import Link from 'next/link';

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <nav className="border-b border-border px-6 py-4">
        <div className="mx-auto max-w-6xl flex items-center justify-between">
          <Link href="/" className="font-mono text-sm font-bold text-text-bright hover:no-underline">
            deepwork
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/papers" className="font-mono text-xs text-text-secondary hover:text-text">Papers</Link>
            <Link href="/blog" className="font-mono text-xs text-text-secondary hover:text-text">Blog</Link>
            <Link href="/about" className="font-mono text-xs text-text-secondary hover:text-text">About</Link>
            <Link href="/dashboard" className="font-mono text-xs text-text-muted hover:text-text">Dashboard</Link>
          </div>
        </div>
      </nav>
      {children}
    </div>
  );
}
