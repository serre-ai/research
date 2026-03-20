import { render, screen, fireEvent } from '@testing-library/react';
import { CommandPalette } from '../command-palette';

const mockPush = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}));

vi.mock('@/hooks', () => ({
  useProjects: () => ({
    data: [{ id: '1', name: 'reasoning-gaps' }],
    isLoading: false,
  }),
}));

// Mock cmdk — the real cmdk component pulls in @radix-ui which has
// the same React version conflict. Provide a minimal stub.
vi.mock('cmdk', () => {
  const { forwardRef, createElement } = require('react');

  function CommandRoot({ children, label, ...props }: Record<string, unknown>) {
    return createElement('div', { ...props, 'aria-label': label, role: 'dialog' }, children);
  }

  function CommandInput(props: Record<string, unknown>) {
    return createElement('input', props);
  }

  function CommandList({ children }: Record<string, unknown>) {
    return createElement('div', { role: 'listbox' }, children);
  }

  function CommandEmpty({ children }: Record<string, unknown>) {
    return createElement('div', null, children);
  }

  function CommandGroup({ heading, children }: Record<string, unknown>) {
    return createElement('div', { role: 'group', 'aria-label': heading }, children);
  }

  function CommandItem({ children, onSelect, value, ...props }: Record<string, unknown>) {
    return createElement(
      'div',
      {
        ...props,
        role: 'option',
        onClick: onSelect,
        'data-value': value,
      },
      children,
    );
  }

  // cmdk exports Command as default with subcomponents as properties
  const Command = Object.assign(CommandRoot, {
    Input: CommandInput,
    List: CommandList,
    Empty: CommandEmpty,
    Group: CommandGroup,
    Item: CommandItem,
  });

  return { Command };
});

describe('CommandPalette', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders nothing when closed', () => {
    const { container } = render(<CommandPalette />);
    expect(container.innerHTML).toBe('');
  });

  it('opens on Cmd+K', () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: 'k', metaKey: true });
    expect(screen.getByPlaceholderText('Type a command...')).toBeInTheDocument();
  });

  it('toggles closed on Cmd+K', () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: 'k', metaKey: true });
    expect(screen.getByPlaceholderText('Type a command...')).toBeInTheDocument();
    // Cmd+K toggles open state
    fireEvent.keyDown(document, { key: 'k', metaKey: true });
    expect(screen.queryByPlaceholderText('Type a command...')).not.toBeInTheDocument();
  });

  it('renders Navigation group with nav items', () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: 'k', metaKey: true });
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Projects')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders Projects group with project data', () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: 'k', metaKey: true });
    expect(screen.getByText('reasoning-gaps')).toBeInTheDocument();
  });

  it('renders Agents group', () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: 'k', metaKey: true });
    expect(screen.getByText('Sol')).toBeInTheDocument();
    expect(screen.getByText('Noor')).toBeInTheDocument();
  });

  it('closes when overlay is clicked', () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: 'k', metaKey: true });
    // Structure: overlay div > inner container div > Command (role=dialog)
    // The overlay is 2 levels up from the dialog
    const overlay = screen.getByRole('dialog').parentElement!.parentElement!;
    fireEvent.click(overlay);
    expect(screen.queryByPlaceholderText('Type a command...')).not.toBeInTheDocument();
  });
});
