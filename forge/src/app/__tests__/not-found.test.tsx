import { render, screen } from '@testing-library/react';
import RootNotFoundPage from '../not-found';

describe('RootNotFoundPage', () => {
  it('shows "Page not found"', () => {
    render(<RootNotFoundPage />);
    expect(screen.getByText('Page not found')).toBeInTheDocument();
  });

  it('"Back to home" links to /', () => {
    render(<RootNotFoundPage />);
    const link = screen.getByText('Back to home');
    expect(link).toHaveAttribute('href', '/');
  });

  it('shows descriptive text', () => {
    render(<RootNotFoundPage />);
    expect(screen.getByText(/doesn't exist/)).toBeInTheDocument();
  });
});
