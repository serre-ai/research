import { redirect } from 'next/navigation';
import { auth, signOut } from '@/lib/auth';
import { UserMenu } from '@/components/user-menu';
import { AppProviders } from '@/providers/app-providers';
import { AppSidebar } from '@/components/app-sidebar';

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
    <AppProviders>
      <div className="flex min-h-screen">
        <AppSidebar />
        <div className="flex flex-1 flex-col md:ml-0">
          <header className="flex h-[49px] items-center justify-between border-b border-border px-6">
            {/* Left spacer for mobile toggle button */}
            <div className="w-8 md:hidden" />
            <div className="font-mono text-xs text-text-muted">Dashboard</div>
            <UserMenu user={session.user} signOutAction={handleSignOut} />
          </header>
          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </AppProviders>
  );
}
