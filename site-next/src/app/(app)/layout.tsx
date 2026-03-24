import { redirect } from 'next/navigation';
import { auth, signOut } from '@/lib/auth';
import { AppProviders } from '@/providers/app-providers';
import { CommandPalette } from '@/components/command-palette';
import { TuiScreen } from '@/components/tui/tui-screen';
import { TuiFrame } from '@/components/tui/tui-frame';

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();

  if (!session?.user) {
    redirect('/sign-in');
  }

  return (
    <AppProviders>
      <CommandPalette />
      <TuiScreen>
        <TuiFrame
          title="DEEPWORK"
          titleRight={session.user.name ?? session.user.email}
        >
          {children}
        </TuiFrame>
      </TuiScreen>
    </AppProviders>
  );
}
