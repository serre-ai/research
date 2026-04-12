import Link from 'next/link';

const navLinks = [
  { href: '/papers', label: 'Papers' },
  { href: '/about', label: 'About' },
];

export function SiteHeader() {
  return (
    <header className="border-b border-border">
      <nav className="mx-auto flex max-w-3xl items-baseline justify-between px-6 py-4">
        <Link
          href="/"
          className="text-xs font-semibold uppercase tracking-[0.2em] text-foreground hover:no-underline"
        >
          Serre AI
        </Link>
        <div className="flex gap-6">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-xs text-muted-foreground transition-colors hover:text-foreground hover:no-underline"
            >
              {link.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
