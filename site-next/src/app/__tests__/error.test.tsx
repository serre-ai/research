import { render, screen, fireEvent } from '@testing-library/react';
import RootErrorPage from '../error';

describe('RootErrorPage', () => {
  const defaultProps = {
    error: Object.assign(new Error('Test error message'), {}),
    reset: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows "Something went wrong"', () => {
    render(<RootErrorPage {...defaultProps} />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('shows the error message', () => {
    render(<RootErrorPage {...defaultProps} />);
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('shows digest when present', () => {
    const error = Object.assign(new Error('fail'), { digest: 'abc123' });
    render(<RootErrorPage error={error} reset={vi.fn()} />);
    expect(screen.getByText(/Digest: abc123/)).toBeInTheDocument();
  });

  it('hides digest when absent', () => {
    render(<RootErrorPage {...defaultProps} />);
    expect(screen.queryByText(/Digest:/)).not.toBeInTheDocument();
  });

  it('"Try again" calls reset', () => {
    const reset = vi.fn();
    render(<RootErrorPage error={defaultProps.error} reset={reset} />);
    fireEvent.click(screen.getByText('Try again'));
    expect(reset).toHaveBeenCalledOnce();
  });

  it('"Back to home" links to /', () => {
    render(<RootErrorPage {...defaultProps} />);
    const link = screen.getByText('Back to home');
    expect(link).toHaveAttribute('href', '/');
  });
});
