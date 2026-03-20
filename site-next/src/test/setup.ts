import * as matchers from '@testing-library/jest-dom/matchers';
import { expect, vi } from 'vitest';
import { forwardRef, createElement } from 'react';

expect.extend(matchers);

// Stub icon factory — returns a span with data-icon for test queries.
// Needed because lucide-react's CJS uses root workspace's React 18
// while react-dom in tests is React 19, causing version mismatch.
function stubIcon(name: string) {
  const Icon = forwardRef((props: Record<string, unknown>, ref) =>
    createElement('span', { ...props, ref, 'data-icon': name }),
  );
  Icon.displayName = name;
  return Icon;
}

vi.mock('lucide-react', () => ({
  AlertTriangle: stubIcon('AlertTriangle'),
  FileQuestion: stubIcon('FileQuestion'),
  ChevronRight: stubIcon('ChevronRight'),
  LayoutDashboard: stubIcon('LayoutDashboard'),
  FolderOpen: stubIcon('FolderOpen'),
  Users: stubIcon('Users'),
  Brain: stubIcon('Brain'),
  FileOutput: stubIcon('FileOutput'),
  ScrollText: stubIcon('ScrollText'),
  Settings: stubIcon('Settings'),
  ClipboardList: stubIcon('ClipboardList'),
}));

// Mock next/link — same React version conflict as lucide-react.
vi.mock('next/link', () => ({
  __esModule: true,
  default: forwardRef(
    ({ children, href, ...props }: Record<string, unknown>, ref: unknown) =>
      createElement('a', { ...props, href, ref }, children as string),
  ),
}));
