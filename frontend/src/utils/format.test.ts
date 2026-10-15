import { describe, it, expect } from 'vitest';
import { formatCurrency, formatDate, monthLabel, pct } from './format';

describe('format utilities', () => {
  it('formats currency', () => {
    expect(formatCurrency('1234.5')).toBe('$1,234.50');
    expect(formatCurrency(0)).toBe('$0.00');
    expect(formatCurrency('not-a-number')).toBe('$0.00');
  });

  it('formats dates', () => {
    expect(formatDate('2026-01-15')).toMatch(/Jan/);
    expect(formatDate('')).toBe('');
  });

  it('formats month labels', () => {
    expect(monthLabel(2026, 1)).toBe('January 2026');
    expect(monthLabel(2026, 12)).toBe('December 2026');
  });

  it('formats percentages with sign', () => {
    expect(pct(5.2)).toBe('+5.2%');
    expect(pct(-3.1)).toBe('-3.1%');
  });
});
