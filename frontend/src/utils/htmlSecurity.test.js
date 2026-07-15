import { describe, expect, test } from 'vitest';
import { sanitizeLabelHtml } from './htmlSecurity';

describe('label HTML sanitization', () => {
  test('removes active content and unsafe attribute/style URLs', () => {
    const clean = sanitizeLabelHtml(`
      <script>alert(1)</script>
      <img src="x" onerror="alert(2)">
      <a href="javascript:alert(3)">bad</a>
      <div style="background:url(https://tracker.invalid/pixel)">tracked</div>
      <strong class="ok">safe</strong>
    `);
    expect(clean).not.toMatch(/script|onerror|javascript:|background/i);
    expect(clean).toContain('<strong class="ok">safe</strong>');
  });

  test('forbids interactive and embedding elements', () => {
    const clean = sanitizeLabelHtml('<form><input value="x"></form><iframe src="https://example.com"></iframe>');
    expect(clean).not.toMatch(/form|input|iframe/i);
  });
});
