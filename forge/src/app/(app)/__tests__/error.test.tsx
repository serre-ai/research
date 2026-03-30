import { render, screen, fireEvent } from '@testing-library/react';
import AppErrorPage from '../error';

describe('AppErrorPage', () => {
  const defaultProps = {
    error: Object.assign(new Error('App error'), {}),
    reset: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows "Something went wrong"', () => {
    render(<AppErrorPage {...defaultProps} />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('shows the error message', () => {
    render(<AppErrorPage {...defaultProps} />);
    expect(screen.getByText('App error')).toBeInTheDocument();
  });

  it('shows digest when present', () => {
    const error = Object.assign(new Error('fail'), { digest: 'def456' });
    render(<AppErrorPage error={error} reset={vi.fn()} />);
    expect(screen.getByText(/Digest: def456/)).toBeInTheDocument();
  });

  it('hides digest when absent', () => {
    render(<AppErrorPage {...defaultProps} />);
    expect(screen.queryByText(/Digest:/)).not.toBeInTheDocument();
  });

  it('"Try again" calls reset', () => {
    const reset = vi.fn();
    render(<AppErrorPage error={defaultProps.error} reset={reset} />);
    fireEvent.click(screen.getByText('Try again'));
    expect(reset).toHaveBeenCalledOnce();
  });
});
