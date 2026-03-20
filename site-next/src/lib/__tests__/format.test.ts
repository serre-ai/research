import { formatDuration, formatTokens, formatCost, relativeTime } from '../format';

describe('formatDuration', () => {
  it('formats seconds under a minute', () => {
    expect(formatDuration(0)).toBe('0s');
    expect(formatDuration(1)).toBe('1s');
    expect(formatDuration(59)).toBe('59s');
  });

  it('formats minutes and seconds', () => {
    expect(formatDuration(60)).toBe('1m 0s');
    expect(formatDuration(90)).toBe('1m 30s');
    expect(formatDuration(3599)).toBe('59m 59s');
  });

  it('formats hours and minutes', () => {
    expect(formatDuration(3600)).toBe('1h 0m');
    expect(formatDuration(3661)).toBe('1h 1m');
    expect(formatDuration(7200)).toBe('2h 0m');
  });
});

describe('formatTokens', () => {
  it('formats tokens below 1K as plain numbers', () => {
    expect(formatTokens(0)).toBe('0');
    expect(formatTokens(999)).toBe('999');
  });

  it('formats thousands as K', () => {
    expect(formatTokens(1000)).toBe('1.0K');
    expect(formatTokens(1500)).toBe('1.5K');
    expect(formatTokens(999_999)).toBe('1000.0K');
  });

  it('formats millions as M', () => {
    expect(formatTokens(1_000_000)).toBe('1.0M');
    expect(formatTokens(2_500_000)).toBe('2.5M');
  });
});

describe('formatCost', () => {
  it('formats with dollar sign and 2 decimals', () => {
    expect(formatCost(0)).toBe('$0.00');
    expect(formatCost(1.5)).toBe('$1.50');
    expect(formatCost(100)).toBe('$100.00');
    expect(formatCost(0.1)).toBe('$0.10');
    expect(formatCost(99.999)).toBe('$100.00');
  });
});

describe('relativeTime', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-03-20T12:00:00Z'));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns "just now" for less than a minute ago', () => {
    expect(relativeTime('2026-03-20T12:00:00Z')).toBe('just now');
    expect(relativeTime('2026-03-20T11:59:30Z')).toBe('just now');
  });

  it('returns minutes ago', () => {
    expect(relativeTime('2026-03-20T11:55:00Z')).toBe('5m ago');
    expect(relativeTime('2026-03-20T11:01:00Z')).toBe('59m ago');
  });

  it('returns hours ago', () => {
    expect(relativeTime('2026-03-20T11:00:00Z')).toBe('1h ago');
    expect(relativeTime('2026-03-20T00:00:00Z')).toBe('12h ago');
  });

  it('returns days ago', () => {
    expect(relativeTime('2026-03-19T12:00:00Z')).toBe('1d ago');
    expect(relativeTime('2026-03-10T12:00:00Z')).toBe('10d ago');
  });
});
