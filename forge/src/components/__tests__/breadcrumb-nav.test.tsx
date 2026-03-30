import { render, screen } from '@testing-library/react';
import { BreadcrumbNav } from '../breadcrumb-nav';

const mockPathname = vi.fn(() => '/dashboard');

vi.mock('next/navigation', () => ({
  usePathname: () => mockPathname(),
}));

describe('BreadcrumbNav', () => {
  beforeEach(() => {
    mockPathname.mockReturnValue('/dashboard');
  });

  it('has aria-label "Breadcrumb"', () => {
    render(<BreadcrumbNav />);
    expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeInTheDocument();
  });

  it('renders single crumb with aria-current="page"', () => {
    render(<BreadcrumbNav />);
    const crumb = screen.getByText('Dashboard');
    expect(crumb).toHaveAttribute('aria-current', 'page');
    expect(crumb.tagName).toBe('SPAN');
  });

  it('renders intermediate crumbs as links', () => {
    mockPathname.mockReturnValue('/projects/reasoning-gaps/sessions');
    render(<BreadcrumbNav />);
    const projectsLink = screen.getByText('Projects');
    expect(projectsLink.closest('a')).toHaveAttribute('href', '/projects');
  });

  it('last crumb is not a link', () => {
    mockPathname.mockReturnValue('/projects/reasoning-gaps/sessions');
    render(<BreadcrumbNav />);
    const lastCrumb = screen.getByText('Sessions');
    expect(lastCrumb).toHaveAttribute('aria-current', 'page');
    expect(lastCrumb.closest('a')).toBeNull();
  });

  it('maps known segments to labels', () => {
    mockPathname.mockReturnValue('/collective/governance');
    render(<BreadcrumbNav />);
    expect(screen.getByText('Collective')).toBeInTheDocument();
    expect(screen.getByText('Governance')).toBeInTheDocument();
  });

  it('renders unknown segments as raw text', () => {
    mockPathname.mockReturnValue('/projects/my-custom-project');
    render(<BreadcrumbNav />);
    expect(screen.getByText('my-custom-project')).toBeInTheDocument();
  });

  it('returns null for empty pathname', () => {
    mockPathname.mockReturnValue('/');
    const { container } = render(<BreadcrumbNav />);
    expect(container.innerHTML).toBe('');
  });
});
