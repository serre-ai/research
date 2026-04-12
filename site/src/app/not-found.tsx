import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-4">
      <h1 className="text-sm font-medium text-foreground">404</h1>
      <p className="text-xs text-muted-foreground">Page not found.</p>
      <Link href="/" className="text-xs text-muted-foreground hover:text-foreground">
        &larr; Home
      </Link>
    </div>
  );
}
