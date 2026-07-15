import DOMPurify from 'dompurify';

const UNSAFE_STYLE_VALUE = /(?:expression\s*\(|url\s*\(|@import|-moz-binding|behavior\s*:)/i;

DOMPurify.addHook('uponSanitizeAttribute', (_node, data) => {
  if (data.attrName === 'style' && UNSAFE_STYLE_VALUE.test(data.attrValue || '')) {
    data.keepAttr = false;
  }
});

const SANITIZE_OPTIONS = {
  USE_PROFILES: { html: true, svg: true, svgFilters: false },
  FORBID_TAGS: [
    'script',
    'iframe',
    'object',
    'embed',
    'form',
    'input',
    'button',
    'textarea',
    'select',
    'option',
    'link',
    'meta',
    'base',
    'foreignObject'
  ],
  FORBID_ATTR: ['srcdoc', 'nonce'],
  ALLOW_DATA_ATTR: true
};

export const sanitizeLabelHtml = (html = '') => DOMPurify.sanitize(String(html), SANITIZE_OPTIONS).trim();
