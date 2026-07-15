import { describe, expect, test } from 'vitest';
import {
  buildBatchMatrix,
  buildBatchSequence,
  extractTemplateVariables,
  getPrintJobCount,
  getRenderPixelCount,
  parseCsvRecords
} from './batchData';

describe('batch data safety and parsing', () => {
  test('builds matrix products and rejects them before exceeding the limit', () => {
    expect(buildBatchMatrix({ color: 'red,blue', size: 's,m' })).toEqual([
      { color: 'red', size: 's' },
      { color: 'red', size: 'm' },
      { color: 'blue', size: 's' },
      { color: 'blue', size: 'm' }
    ]);
    expect(() => buildBatchMatrix({ a: '1,2,3', b: '1,2,3' }, 8)).toThrow(/safety limit/i);
  });

  test('builds descending padded sequences and caps their length', () => {
    expect(buildBatchSequence({ varName: 'id', start: 3, end: 1, prefix: 'A-', padding: 2 })).toEqual([
      { id: 'A-03' }, { id: 'A-02' }, { id: 'A-01' }
    ]);
    expect(() => buildBatchSequence({ varName: 'id', start: 1, end: 20 }, 10)).toThrow(/safety limit/i);
  });

  test('parses quoted CSV fields, embedded newlines, escaped quotes, and BOMs', () => {
    const parsed = parseCsvRecords('\uFEFFname,note\r\n"Doe, Jane","Line 1\nLine 2"\r\nBob,"said ""hi"""');
    expect(parsed.headers).toEqual(['name', 'note']);
    expect(parsed.records).toEqual([
      { name: 'Doe, Jane', note: 'Line 1\nLine 2' },
      { name: 'Bob', note: 'said "hi"' }
    ]);
    expect(() => parseCsvRecords('name,name\nA,B')).toThrow(/unique/i);
    expect(() => parseCsvRecords('name\n"unfinished')).toThrow(/unterminated/i);
  });

  test('finds variables recursively across items, groups, and page templates', () => {
    const variables = extractTemplateVariables({
      items: [{ text: '{{ top }}', children: [{ params: { value: '{{ nested }}' } }] }],
      pageLayouts: [{ htmlContent: '<b>{{ html_value }}</b>', activeTemplate: { params: { code: '{{ code }}' } } }]
    });
    expect(new Set(variables)).toEqual(new Set(['top', 'nested', 'html_value', 'code']));
  });

  test('calculates job and decoded pixel budgets', () => {
    expect(getPrintJobCount({ records: 2, copies: 3, pages: 4 })).toBe(24);
    expect(getRenderPixelCount({ width: 100, height: 50, jobs: 10 })).toBe(50_000);
  });
});
