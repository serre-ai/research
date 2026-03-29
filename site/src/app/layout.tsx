import type { Metadata } from 'next';
import { IBM_Plex_Mono } from 'next/font/google';
import Link from 'next/link';
import '@/styles/globals.css';

const mono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-mono',
  display: 'block',
});

export const metadata: Metadata = {
  title: {
    default: 'Serre AI',
    template: '%s — Serre AI',
  },
  description: 'Independent research lab. Formal foundations of AI reasoning.',
  metadataBase: new URL('https://serre.ai'),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${mono.variable}`}>
      <body className="bg-bg text-text font-mono antialiased">
        {/* Navigation */}
        <nav className="max-w-2xl mx-auto px-6 pt-10 pb-6 flex items-baseline justify-between">
          <Link href="/" className="text-text-bright font-semibold tracking-widest text-xs uppercase hover:no-underline">
            Serre AI
          </Link>
          <div className="flex gap-8">
            <Link href="/papers" className="text-xs text-text-muted hover:text-text-bright transition-colors">
              Papers
            </Link>
            <Link href="/about" className="text-xs text-text-muted hover:text-text-bright transition-colors">
              About
            </Link>
          </div>
        </nav>

        {/* Content */}
        <main className="max-w-2xl mx-auto px-6 pb-20">
          {children}
        </main>

        {/* Footer */}
        <footer className="max-w-2xl mx-auto px-6 pb-12">
          <hr />
          <p className="text-xs text-text-muted">
            Reykjavik{'  '}·{'  '}serre.ai{'  '}·{'  '}oddur@serre.ai
          </p>
        </footer>
      </body>
    </html>
  );
}
