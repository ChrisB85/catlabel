import { describe, expect, it, vi } from 'vitest';
import { resolveUrl } from './ingress';

const withBase = (baseURI, run) => {
  vi.stubGlobal('document', { baseURI });
  try {
    return run();
  } finally {
    vi.unstubAllGlobals();
  }
};

describe('resolveUrl', () => {
  it('keeps root-absolute paths at the root when served from the root', () => {
    withBase('http://homeassistant.local:8000/', () => {
      expect(resolveUrl('/api/health')).toBe('http://homeassistant.local:8000/api/health');
    });
  });

  it('rebases root-absolute paths onto the ingress prefix', () => {
    withBase('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/', () => {
      expect(resolveUrl('/api/printers/scan'))
        .toBe('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/api/printers/scan');
    });
  });

  it('preserves the query string', () => {
    withBase('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/', () => {
      expect(resolveUrl('/api/fonts?refresh=1'))
        .toBe('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/api/fonts?refresh=1');
    });
  });

  it('leaves absolute and protocol-relative URLs alone', () => {
    withBase('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/', () => {
      expect(resolveUrl('https://example.com/a')).toBe('https://example.com/a');
      expect(resolveUrl('//example.com/a')).toBe('//example.com/a');
    });
  });

  it('leaves non-string inputs alone', () => {
    const request = new Request('http://example.com/a');
    withBase('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/', () => {
      expect(resolveUrl(request)).toBe(request);
    });
  });
});
