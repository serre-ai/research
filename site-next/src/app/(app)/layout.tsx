import { redirect } from 'next/navigation';
import { auth, signOut } from '@/lib/auth';
import { UserMenu } from '@/components/user-menu';
import { AppProviders } from '@/providers/app-providers';

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();

  if (!session?.user) {
    redirect('/sign-in');
  }

  async function handleSignOut() {
    'use server';
    await signOut({ redirectTo: '/' });
  }

  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between border-b border-border px-6 py-3">
        <div className="flex items-center gap-4">
          <a href="/" className="font-mono text-sm font-bold text-text-bright">
            deepwork
          </a>
          <span className="text-text-muted">/</span>
          <a href="/dashboard" className="font-mono text-xs text-text-secondary hover:text-text">
            dashboard
          </a>
        </div>
        <UserMenu user={session.user} signOutAction={handleSignOut} />
      </header>
      <AppProviders>
        <main>{children}</main>
      </AppProviders>
    </div>
  );
}
