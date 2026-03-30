import {
  LayoutDashboard,
  FolderOpen,
  Users,
  Brain,
  FileOutput,
  ScrollText,
  Settings,
  ClipboardList,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: readonly NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Projects', href: '/projects', icon: FolderOpen },
  { label: 'Collective', href: '/collective', icon: Users },
  { label: 'Knowledge', href: '/knowledge', icon: Brain },
  { label: 'Paper', href: '/paper', icon: FileOutput },
  { label: 'Backlog', href: '/backlog', icon: ClipboardList },
  { label: 'Logs', href: '/logs', icon: ScrollText },
  { label: 'Settings', href: '/settings', icon: Settings },
] as const;
