'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';
import { NAV_ITEMS } from '@/lib/nav-items';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

interface ForgeSidebarProps {
  userName: string;
  signOut: () => Promise<void>;
}

export function ForgeSidebar({ userName, signOut }: ForgeSidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="flex w-52 shrink-0 flex-col border-r border-border bg-card">
      {/* Header */}
      <div className="px-4 py-4">
        <Link href="/forge/dashboard" className="text-xs font-semibold uppercase tracking-[0.2em] text-foreground hover:no-underline">
          Forge
        </Link>
        <p className="mt-1 truncate text-[11px] text-muted-foreground">{userName}</p>
      </div>

      <Separator />

      {/* Navigation */}
      <nav className="flex-1 space-y-0.5 px-2 py-3">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-xs transition-colors hover:no-underline',
                isActive
                  ? 'bg-accent text-foreground'
                  : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground',
              )}
            >
              <item.icon className="h-3.5 w-3.5 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <Separator />

      {/* Footer */}
      <div className="flex items-center justify-between px-4 py-3">
        <Link
          href="/"
          className="text-[11px] text-muted-foreground transition-colors hover:text-foreground hover:no-underline"
        >
          serre.ai
        </Link>
        <form action={signOut}>
          <Button type="submit" variant="ghost" size="sm" className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground">
            <LogOut className="h-3 w-3" />
          </Button>
        </form>
      </div>
    </aside>
  );
}
