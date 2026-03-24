import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  TuiBox,
  TuiTable,
  TuiBadge,
  TuiStatusDot,
  TuiProgress,
  TuiSparkline,
  TuiMetric,
  TuiSkeleton,
} from '../tui';

describe('TuiBox', () => {
  it('renders children', () => {
    render(<TuiBox>Hello terminal</TuiBox>);
    expect(screen.getByText('Hello terminal')).toBeInTheDocument();
  });

  it('renders title', () => {
    render(<TuiBox title="PROJECTS">content</TuiBox>);
    expect(screen.getByText('PROJECTS')).toBeInTheDocument();
  });

  it('renders box-drawing characters', () => {
    const { container } = render(<TuiBox>content</TuiBox>);
    expect(container.textContent).toContain('┌');
    expect(container.textContent).toContain('┐');
    expect(container.textContent).toContain('└');
    expect(container.textContent).toContain('┘');
    expect(container.textContent).toContain('│');
  });

  it('applies variant class', () => {
    const { container } = render(<TuiBox variant="accent">content</TuiBox>);
    expect(container.querySelector('.tui-box--accent')).toBeTruthy();
  });

  it('applies custom className', () => {
    const { container } = render(<TuiBox className="mt-4">content</TuiBox>);
    expect(container.querySelector('.mt-4')).toBeTruthy();
  });
});

describe('TuiTable', () => {
  const columns = [
    { key: 'name', header: 'NAME' },
    { key: 'status', header: 'STATUS' },
  ];
  const data = [
    { name: 'reasoning-gaps', status: 'active' },
    { name: 'verification', status: 'writing' },
  ];

  it('renders headers', () => {
    render(<TuiTable columns={columns} data={data} rowKey={(r) => r.name} />);
    expect(screen.getByText('NAME')).toBeInTheDocument();
    expect(screen.getByText('STATUS')).toBeInTheDocument();
  });

  it('renders rows', () => {
    render(<TuiTable columns={columns} data={data} rowKey={(r) => r.name} />);
    expect(screen.getByText('reasoning-gaps')).toBeInTheDocument();
    expect(screen.getByText('verification')).toBeInTheDocument();
  });

  it('renders empty table without crashing', () => {
    render(<TuiTable columns={columns} data={[]} rowKey={(r) => r.name} />);
    expect(screen.getByText('NAME')).toBeInTheDocument();
  });

  it('supports custom render function', () => {
    const cols = [
      { key: 'name', header: 'NAME', render: (row: typeof data[0]) => <strong>{row.name}</strong> },
    ];
    render(<TuiTable columns={cols} data={data} rowKey={(r) => r.name} />);
    expect(screen.getByText('reasoning-gaps').tagName).toBe('STRONG');
  });
});

describe('TuiBadge', () => {
  it('renders with brackets', () => {
    render(<TuiBadge>ACTIVE</TuiBadge>);
    expect(screen.getByText(/\[ACTIVE\]/)).toBeInTheDocument();
  });

  it('applies color class', () => {
    const { container } = render(<TuiBadge color="ok">OK</TuiBadge>);
    expect(container.querySelector('.tui-badge--ok')).toBeTruthy();
  });
});

describe('TuiStatusDot', () => {
  it('renders correct characters', () => {
    const { rerender, container } = render(<TuiStatusDot status="ok" />);
    expect(container.textContent).toBe('●');

    rerender(<TuiStatusDot status="idle" />);
    expect(container.textContent).toBe('○');

    rerender(<TuiStatusDot status="error" />);
    expect(container.textContent).toBe('✗');
  });

  it('has aria-label', () => {
    render(<TuiStatusDot status="ok" />);
    expect(screen.getByLabelText('ok')).toBeInTheDocument();
  });
});

describe('TuiProgress', () => {
  it('renders progress bar', () => {
    render(<TuiProgress value={50} width={10} />);
    // 50% of 10 = 5 filled, 5 empty
    const el = screen.getByText(/50%/);
    expect(el).toBeInTheDocument();
  });

  it('clamps values', () => {
    render(<TuiProgress value={150} width={10} />);
    expect(screen.getByText(/100%/)).toBeInTheDocument();
  });

  it('handles zero', () => {
    render(<TuiProgress value={0} width={10} />);
    expect(screen.getByText(/0%/)).toBeInTheDocument();
  });

  it('hides percent when showPercent=false', () => {
    const { container } = render(<TuiProgress value={50} width={10} showPercent={false} />);
    expect(container.textContent).not.toContain('%');
  });
});

describe('TuiSparkline', () => {
  it('renders sparkline characters', () => {
    const { container } = render(<TuiSparkline data={[1, 5, 3, 8, 2]} />);
    const text = container.textContent ?? '';
    // Should contain block characters
    expect(text.length).toBe(5);
    expect(text).toMatch(/[▁▂▃▄▅▆▇█]{5}/);
  });

  it('returns null for empty data', () => {
    const { container } = render(<TuiSparkline data={[]} />);
    expect(container.textContent).toBe('');
  });

  it('handles uniform data', () => {
    const { container } = render(<TuiSparkline data={[5, 5, 5]} />);
    const text = container.textContent ?? '';
    // All same value → all same block
    expect(new Set(text.split('')).size).toBe(1);
  });
});

describe('TuiMetric', () => {
  it('renders label and value', () => {
    render(<TuiMetric label="DAILY SPEND" value="$14.34" />);
    expect(screen.getByText('DAILY SPEND')).toBeInTheDocument();
    expect(screen.getByText('$14.34')).toBeInTheDocument();
  });

  it('renders unit', () => {
    render(<TuiMetric label="MEMORY" value="1.3" unit="GB" />);
    expect(screen.getByText(/GB/)).toBeInTheDocument();
  });
});

describe('TuiSkeleton', () => {
  it('renders loading characters', () => {
    const { container } = render(<TuiSkeleton width={8} />);
    expect(container.textContent).toBe('░'.repeat(8));
  });

  it('has aria-label', () => {
    render(<TuiSkeleton />);
    expect(screen.getByLabelText('loading')).toBeInTheDocument();
  });
});
