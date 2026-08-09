import { afterEach, describe, expect, test, vi } from 'vitest';
import { settingsForPrinterWidth, useStore } from './store';

afterEach(() => {
  vi.useRealTimers();
  useStore.setState({
    items: [],
    pageLayouts: [{ pageIndex: 0, htmlContent: '', activeTemplate: null }],
    batchRecords: [{}],
    currentPage: 0,
    currentProjectId: null,
    history: [],
    historyIndex: -1,
    canUndo: false,
    canRedo: false
  });
});

describe('editor store correctness', () => {
  test('AI setters accept React-style functional updaters', () => {
    useStore.setState({ aiMessages: [], aiSessionUsage: { tokens: 1 } });
    useStore.getState().setAiMessages((messages) => [...messages, { role: 'user', content: 'hello' }]);
    useStore.getState().setAiSessionUsage((usage) => ({ ...usage, tokens: usage.tokens + 4 }));
    expect(useStore.getState().aiMessages).toEqual([{ role: 'user', content: 'hello' }]);
    expect(useStore.getState().aiSessionUsage.tokens).toBe(5);
  });

  test('selects a newly added item on its target page', () => {
    useStore.setState({ currentPage: 2 });
    useStore.getState().addItem({ id: 'created', type: 'text', text: 'New' });
    expect(useStore.getState()).toMatchObject({
      selectedId: 'created', selectedIds: ['created'], currentPage: 2
    });
    expect(useStore.getState().items[0].pageIndex).toBe(2);
  });

  test('hydrates rotation and geometry atomically without double-swapping', () => {
    useStore.getState().hydrateCanvasState({
      width: 200,
      height: 100,
      isRotated: true,
      items: [{ id: 'one', type: 'text', text: 'A', pageIndex: 0 }]
    });
    expect(useStore.getState()).toMatchObject({ canvasWidth: 200, canvasHeight: 100, isRotated: true });
  });

  test('loading a project clears the previous document history', async () => {
    vi.useFakeTimers();
    useStore.getState().setItems([{ id: 'old', type: 'text', text: 'Old', pageIndex: 0 }]);
    await vi.advanceTimersByTimeAsync(450);
    expect(useStore.getState().canUndo).toBe(true);

    useStore.getState().loadProject({
      id: 42,
      canvas_state: { width: 300, height: 150, items: [{ id: 'new', type: 'text', text: 'New', pageIndex: 0 }] }
    });
    expect(useStore.getState()).toMatchObject({ currentProjectId: 42, history: [], canUndo: false });

    useStore.getState().undo();
    expect(useStore.getState().items[0].id).toBe('new');
  });

  test('clamps persisted copies and batch records while normalizing pages', () => {
    const records = Array.from({ length: 1_100 }, (_, index) => ({ index }));
    useStore.getState().hydrateCanvasState({
      printCopies: 999,
      batchRecords: records,
      pageLayouts: [{ pageIndex: -10, htmlContent: 'first' }]
    });
    expect(useStore.getState().printCopies).toBe(100);
    expect(useStore.getState().batchRecords).toHaveLength(1_000);
    expect(useStore.getState().pageLayouts[0].pageIndex).toBe(0);
  });
});

describe('print width follows the selected printer', () => {
  const settings = { paper_width_mm: 58, print_width_mm: 48, default_dpi: 203 };

  test('adopts the head width of the selected printer', () => {
    expect(settingsForPrinterWidth(settings, { width_mm: 110 })).toEqual({ ...settings, print_width_mm: 110 });
  });

  test('leaves settings alone when the width already matches', () => {
    expect(settingsForPrinterWidth(settings, { width_mm: 48 })).toBeNull();
  });

  test('ignores printers that report no usable width', () => {
    expect(settingsForPrinterWidth(settings, null)).toBeNull();
    expect(settingsForPrinterWidth(settings, {})).toBeNull();
    expect(settingsForPrinterWidth(settings, { width_mm: 0 })).toBeNull();
    expect(settingsForPrinterWidth(settings, { width_mm: 'wide' })).toBeNull();
  });

  test('keeps every other setting untouched', () => {
    const result = settingsForPrinterWidth(settings, { width_mm: 48.8 });
    expect(result.paper_width_mm).toBe(58);
    expect(result.default_dpi).toBe(203);
  });
});
