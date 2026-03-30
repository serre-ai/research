import { redirect } from 'next/navigation';
import { auth } from '@/lib/auth';
import { AppProviders } from '@/providers/app-providers';
import { CommandPalette } from '@/components/command-palette';
import { TuiScreen } from '@/components/tui/tui-screen';
import { TuiFrame } from '@/components/tui/tui-frame';
import { TuiAppShell } from '@/components/tui/tui-app-shell';

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
          title="FORGE"
          titleRight={session.user.name ?? session.user.email}
        >
          <TuiAppShell>
            {children}
          </TuiAppShell>
        </TuiFrame>
      </TuiScreen>
    </AppProviders>
  );
}
