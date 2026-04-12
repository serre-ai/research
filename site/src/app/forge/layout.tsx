import { redirect } from 'next/navigation';
import { auth, signOut } from '@/lib/auth';
import { ForgeSidebar } from '@/components/forge/sidebar';
import { AppProviders } from '@/providers/app-providers';

export default async function ForgeLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();

  if (!session?.user) {
    redirect('/sign-in');
  }

  return (
    <AppProviders>
      <div className="flex h-dvh overflow-hidden">
        <ForgeSidebar
          userName={session.user.name ?? session.user.email ?? 'User'}
          signOut={async () => {
            'use server';
            await signOut({ redirectTo: '/' });
          }}
        />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </AppProviders>
  );
}
