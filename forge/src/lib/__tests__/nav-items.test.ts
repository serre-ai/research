import { NAV_ITEMS } from '../nav-items';

describe('NAV_ITEMS', () => {
  it('has 8 navigation items', () => {
    expect(NAV_ITEMS).toHaveLength(8);
  });

  it('every item has label, href, and icon', () => {
    for (const item of NAV_ITEMS) {
      expect(item).toHaveProperty('label');
      expect(item).toHaveProperty('href');
      expect(item).toHaveProperty('icon');
      expect(typeof item.label).toBe('string');
      expect(typeof item.href).toBe('string');
      expect(item.icon).toBeDefined();
    }
  });

  it('all hrefs start with /', () => {
    for (const item of NAV_ITEMS) {
      expect(item.href).toMatch(/^\//);
    }
  });

  it('has no duplicate hrefs', () => {
    const hrefs = NAV_ITEMS.map((item) => item.href);
    expect(new Set(hrefs).size).toBe(hrefs.length);
  });

  it('has no duplicate labels', () => {
    const labels = NAV_ITEMS.map((item) => item.label);
    expect(new Set(labels).size).toBe(labels.length);
  });
});
