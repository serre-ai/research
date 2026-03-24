import Link from 'next/link';

export function LandingFooter() {
  return (
    <div className="py-8 font-mono text-xs text-text-muted">
      <div className="flex flex-wrap gap-4">
        <Link href="https://github.com/oddurs/deepwork" className="hover:text-text-secondary">
          github
        </Link>
        <Link href="/about" className="hover:text-text-secondary">about</Link>
        <Link href="/dashboard" className="hover:text-text-secondary">dashboard</Link>
      </div>
      <p className="mt-3">
        Oddur Sigurdsson &middot; Reykjavik, Iceland &middot; 2026
      </p>
    </div>
  );
}
