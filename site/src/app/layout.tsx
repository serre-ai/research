import type { Metadata } from 'next';
import { IBM_Plex_Mono } from 'next/font/google';
import { TooltipProvider } from '@/components/ui/tooltip';
import '@/styles/globals.css';

const mono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-mono',
  display: 'swap',
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
    <html lang="en" className={`dark ${mono.variable}`} suppressHydrationWarning>
      <body>
        <TooltipProvider>
          {children}
        </TooltipProvider>
      </body>
    </html>
  );
}
