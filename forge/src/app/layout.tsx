import type { Metadata } from 'next';
import { IBM_Plex_Mono, IBM_Plex_Sans } from 'next/font/google';
import '@/styles/globals.css';
import { QueryProvider } from '@/providers/query-provider';

const plexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-mono',
  display: 'block',
});

const plexSans = IBM_Plex_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-sans',
  display: 'block',
});

export const metadata: Metadata = {
  title: 'Forge',
  description: 'Serre AI research operations',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${plexMono.variable} ${plexSans.variable} dark`}>
      <body className="bg-bg text-text antialiased">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
