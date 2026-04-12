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
  { label: 'Dashboard', href: '/forge/dashboard', icon: LayoutDashboard },
  { label: 'Projects', href: '/forge/projects', icon: FolderOpen },
  { label: 'Collective', href: '/forge/collective', icon: Users },
  { label: 'Knowledge', href: '/forge/knowledge', icon: Brain },
  { label: 'Paper', href: '/forge/paper', icon: FileOutput },
  { label: 'Backlog', href: '/forge/backlog', icon: ClipboardList },
  { label: 'Logs', href: '/forge/logs', icon: ScrollText },
  { label: 'Settings', href: '/forge/settings', icon: Settings },
] as const;
