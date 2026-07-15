import { describe, expect, test } from 'vitest';
import { getPageIndices, getPageItems, getPageLayout, normalizePageIndex } from './canvasPages';

describe('canvas page model', () => {
  test('normalizes invalid page indices and returns a sorted union', () => {
    expect(normalizePageIndex(-4)).toBe(0);
    expect(normalizePageIndex('3')).toBe(3);
    expect(getPageIndices({
      currentPage: 2,
      items: [{ pageIndex: 4 }, { pageIndex: 0 }],
      pageLayouts: [{ pageIndex: 3 }]
    })).toEqual([0, 2, 3, 4]);
  });

  test('never copies the last page items into an HTML-only page', () => {
    const items = [{ id: 'p0', pageIndex: 0 }];
    expect(getPageItems(items, 1)).toEqual([]);
    expect(getPageItems(items, 0)).toEqual(items);
  });

  test('uses legacy top-level HTML only for page zero', () => {
    const state = { htmlContent: '<b>legacy</b>', activeTemplate: { id: 'legacy' } };
    expect(getPageLayout(state, 0).htmlContent).toBe('<b>legacy</b>');
    expect(getPageLayout(state, 1).htmlContent).toBe('');
  });
});
