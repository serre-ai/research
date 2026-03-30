import { mapStatusToKey, formatCurrency, formatDate } from '../dashboard-helpers';

describe('mapStatusToKey', () => {
  it('maps active and running to ok', () => {
    expect(mapStatusToKey('active')).toBe('ok');
    expect(mapStatusToKey('running')).toBe('ok');
  });

  it('maps paused and pending to warn', () => {
    expect(mapStatusToKey('paused')).toBe('warn');
    expect(mapStatusToKey('pending')).toBe('warn');
  });

  it('maps error and failed to error', () => {
    expect(mapStatusToKey('error')).toBe('error');
    expect(mapStatusToKey('failed')).toBe('error');
  });

  it('maps session statuses correctly', () => {
    expect(mapStatusToKey('completed')).toBe('ok');
    expect(mapStatusToKey('success')).toBe('ok');
    expect(mapStatusToKey('in_progress')).toBe('warn');
  });

  it('maps unknown statuses to idle', () => {
    expect(mapStatusToKey('unknown')).toBe('idle');
    expect(mapStatusToKey('')).toBe('idle');
  });
});

describe('formatCurrency', () => {
  it('formats with dollar sign and no decimals', () => {
    expect(formatCurrency(0)).toBe('$0');
    expect(formatCurrency(100)).toBe('$100');
    expect(formatCurrency(999.99)).toBe('$1000');
    expect(formatCurrency(42.3)).toBe('$42');
  });
});

describe('formatDate', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-03-20T12:00:00Z'));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns "today" for same day', () => {
    expect(formatDate('2026-03-20T08:00:00Z')).toBe('today');
  });

  it('returns "yesterday" for one day ago', () => {
    expect(formatDate('2026-03-19T08:00:00Z')).toBe('yesterday');
  });

  it('returns "Nd ago" for 2-6 days', () => {
    expect(formatDate('2026-03-18T12:00:00Z')).toBe('2d ago');
    expect(formatDate('2026-03-14T12:00:00Z')).toBe('6d ago');
  });

  it('returns formatted date for 7+ days', () => {
    const result = formatDate('2026-03-01T12:00:00Z');
    expect(result).toMatch(/Mar\s+1/);
  });
});
