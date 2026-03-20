import { FileQuestion } from 'lucide-react';

export default function RootNotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-bg px-4 text-center">
      <FileQuestion className="mb-4 h-12 w-12 text-text-muted" />
      <h2 className="font-mono text-xl font-semibold text-text-bright mb-2">Page not found</h2>
      <p className="font-mono text-sm text-text-secondary mb-6">
        The page you&apos;re looking for doesn&apos;t exist.
      </p>
      <a
        href="/"
        className="font-mono text-sm text-primary hover:text-primary-hover transition-colors"
      >
        Back to home
      </a>
    </div>
  );
}
