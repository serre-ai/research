import { UserMenu } from '@/components/user-menu';

interface AppHeaderProps {
  user: {
    name?: string | null;
    email?: string | null;
    image?: string | null;
  };
  signOutAction: () => Promise<void>;
}

export function AppHeader({ user, signOutAction }: AppHeaderProps) {
  return (
    <header className="flex h-[49px] items-center justify-between border-b border-border px-6">
      <div className="font-mono text-xs text-text-muted">Dashboard</div>
      <UserMenu user={user} signOutAction={signOutAction} />
    </header>
  );
}
