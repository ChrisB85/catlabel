import { applyVars } from '../utils/rendering';

export const TEMPLATE_METADATA = [
  {
    id: 'centered_text',
    category: 'Layout',
    name: 'Centered Text',
    description: 'A single, perfectly auto-scaling text block.',
    fields: [{ name: 'text', label: 'Main Text', type: 'textarea', default: 'Centered Text' }],
  },
  {
    id: 'title_subtitle',
    category: 'Layout',
    name: 'Title & Subtitle',
    description: 'Stacked text with a large bold title.',
    fields: [
      { name: 'title', label: 'Title', type: 'text', default: 'MAIN TITLE' },
      { name: 'subtitle', label: 'Subtitle', type: 'text', default: 'Subheading text goes here' },
    ],
  },
  {
    id: 'price_tag',
    category: 'Dedicated',
    name: 'Price Tag with Barcode',
    description: 'Retail price tag.',
    fields: [
      { name: 'currency_symbol', label: 'Currency Symbol', type: 'text', default: '$' },
      { name: 'price_main', label: 'Main Price', type: 'text', default: '19' },
      { name: 'price_cents', label: 'Cents', type: 'text', default: '99' },
      { name: 'unit', label: 'Unit (e.g. /ea)', type: 'text', default: '' },
      { name: 'product_name', label: 'Product Name', type: 'text', default: 'Product Name' },
      { name: 'barcode', label: 'Barcode Data', type: 'text', default: '123456789' },
    ],
  },
  {
    id: 'inventory_tag',
    category: 'Dedicated',
    name: 'Modern Inventory Tag',
    description: 'Professional asset tag with inverted department header.',
    fields: [
      { name: 'department', label: 'Department / Category', type: 'text', default: 'WAREHOUSE' },
      { name: 'title', label: 'Item Name', type: 'text', default: 'Item Name' },
      { name: 'sku', label: 'SKU / Subtext', type: 'text', default: 'SKU-123' },
      { name: 'code_data', label: 'Code Data', type: 'text', default: 'INV-001' },
    ],
  },
  {
    id: 'shipping_address',
    category: 'Dedicated',
    name: 'Shipping Address',
    description: 'Professional shipping label with service banner.',
    fields: [
      { name: 'service', label: 'Service Type', type: 'text', default: 'PRIORITY' },
      { name: 'sender', label: 'Sender Address', type: 'textarea', default: 'John Doe\n123 Sender St.' },
      { name: 'recipient', label: 'Recipient Address', type: 'textarea', default: 'Jane Smith\n456 Recipient Ave.' },
    ],
  },
  {
    id: 'warning_banner',
    category: 'Dedicated',
    name: 'Warning Banner',
    description: 'Inverted black background with bold white text.',
    fields: [{ name: 'text', label: 'Warning Text', type: 'text', default: 'FRAGILE' }],
  },
  {
    id: 'expiration_date',
    category: 'Dedicated',
    name: 'Expiration / Batch Date',
    description: 'Prominent expiration date.',
    fields: [
      { name: 'product_name', label: 'Product Name (Optional)', type: 'text', default: '' },
      { name: 'exp_date', label: 'Expiration Date', type: 'text', default: '2025-12-31' },
      { name: 'made_date', label: 'Mfg / Made On (Optional)', type: 'text', default: '' },
    ],
  },
  {
    id: 'default',
    category: 'Legacy',
    name: 'Default',
    description: 'Legacy plain text layout.',
    fields: [{ name: 'text', label: 'Main Text', type: 'textarea', default: 'Label Text' }],
  },
  {
    id: 'center',
    category: 'Legacy',
    name: 'Center',
    description: 'Legacy centered text layout.',
    fields: [{ name: 'text', label: 'Main Text', type: 'textarea', default: 'Centered Text' }],
  },
  {
    id: 'maximize',
    category: 'Legacy',
    name: 'Maximize',
    description: 'Legacy maximized text layout.',
    fields: [{ name: 'text', label: 'Main Text', type: 'textarea', default: 'BIG TEXT' }],
  },
  {
    id: 'address',
    category: 'Legacy',
    name: 'Address',
    description: 'Legacy address block layout.',
    fields: [{ name: 'text', label: 'Address Text', type: 'textarea', default: '123 Example St.\nCity, ST 12345' }],
  },
  {
    id: 'jar_apothecary',
    category: 'Legacy',
    name: 'Jar: Apothecary',
    description: 'Classic apothecary pantry style.',
    fields: [
      { name: 'text', label: 'Top Text', type: 'text', default: 'PREMIUM' },
      { name: 'title', label: 'Title', type: 'text', default: 'BASIL' },
      { name: 'subtitle', label: 'Subtitle', type: 'text', default: 'Sweet & Aromatic' },
    ],
  },
  {
    id: 'jar_farmhouse',
    category: 'Legacy',
    name: 'Jar: Farmhouse',
    description: 'Farmhouse pantry label style.',
    fields: [
      { name: 'title', label: 'Title', type: 'text', default: 'BASIL' },
      { name: 'subtitle', label: 'Subtitle', type: 'text', default: 'Sweet & Aromatic' },
    ],
  },
  {
    id: 'custom',
    category: 'Layout',
    name: 'Custom HTML',
    description: 'Raw HTML entry.',
    fields: [{ name: 'custom_html', label: 'HTML Content', type: 'textarea', default: '<div>Hello</div>' }],
  },
];

export const LABEL_TEMPLATE_STYLES = `
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background: white;
  overflow: hidden;
}
.label-canvas-container {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  overflow: hidden;
}
.label-canvas-container * {
  box-sizing: border-box;
}
.auto-text {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
}
.auto-text * {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.05 !important;
}
.bound-box {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
`;

const escapeHtml = (value = '') => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;');

const formatText = (value = '') => escapeHtml(value).replace(/\n/g, '<br />');

export const sanitizeLabelHtml = (html = '') => String(html)
  .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
  .replace(/<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi, '')
  .replace(/<(object|embed|form)[\s\S]*?>[\s\S]*?<\/\1>/gi, '')
  .replace(/\son\w+\s*=\s*(".*?"|'.*?'|[^\s>]+)/gi, '')
  .replace(/javascript\s*:/gi, '')
  .trim();

const LEGACY_FIELD_NAMES = [
  'text',
  'title',
  'subtitle',
  'custom_html',
  'currency_symbol',
  'price_main',
  'price_cents',
  'unit',
  'product_name',
  'barcode',
  'department',
  'sku',
  'code_data',
  'service',
  'sender',
  'recipient',
  'exp_date',
  'made_date',
];

const getTemplateMetadata = (templateId) =>
  TEMPLATE_METADATA.find((template) => template.id === templateId) || TEMPLATE_METADATA[0];

const resolveTemplateParams = (item = {}, record = {}) => {
  const templateId = item.template_id || 'centered_text';
  const templateMetadata = getTemplateMetadata(templateId);
  const sourceParams = item.params && typeof item.params === 'object' ? item.params : {};
  const mergedParams = {};

  (templateMetadata.fields || []).forEach((field) => {
    mergedParams[field.name] = sourceParams[field.name] ?? item[field.name] ?? field.default ?? '';
  });

  LEGACY_FIELD_NAMES.forEach((fieldName) => {
    if (mergedParams[fieldName] === undefined) {
      mergedParams[fieldName] = sourceParams[fieldName] ?? item[fieldName] ?? '';
    }
  });

  const resolvedParams = {};
  Object.entries(mergedParams).forEach(([key, value]) => {
    const resolvedValue = applyVars(value ?? '', record);
    resolvedParams[key] = key === 'custom_html'
      ? sanitizeLabelHtml(resolvedValue)
      : formatText(resolvedValue);
  });

  return resolvedParams;
};

export const buildLabelTemplateMarkup = (item = {}, record = {}) => {
  const templateId = item.template_id || 'centered_text';
  const p = resolveTemplateParams(item, record);
  const isLandscape = Number(item.width || 384) > Number(item.height || 384);

  switch (templateId) {
    case 'custom':
      return `<div class="label-canvas-container">${p.custom_html || ''}</div>`;

    case 'title_subtitle':
      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:12px; gap:8px;">
          <div class="bound-box" style="flex:3;">
            <div class="auto-text" style="font-weight:900; text-transform:uppercase;">${p.title || ''}</div>
          </div>
          <div style="height:4px; background:black; width:80%; margin:0 auto; flex-shrink:0;"></div>
          <div class="bound-box" style="flex:2;">
            <div class="auto-text" style="font-weight:700;">${p.subtitle || ''}</div>
          </div>
        </div>`;

    case 'price_tag': {
      const unitHtml = p.unit ? `<span style="font-size:0.4em; margin-left:4px;">${p.unit}</span>` : '';
      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:12px;">
          <div class="bound-box" style="flex:4;">
            <div class="auto-text" style="font-weight:900; display:flex; flex-direction:row; align-items:baseline;">
              <span>${p.currency_symbol || ''}${p.price_main || ''}</span>
              <span style="font-size:0.5em; vertical-align:super;">${p.price_cents || ''}</span>
              ${unitHtml}
            </div>
          </div>
          <div class="bound-box" style="flex:2; border-top:4px solid black; padding-top:6px; margin-top:6px;">
            <div class="auto-text" style="font-weight:800; text-transform:uppercase;">${p.product_name || ''}</div>
          </div>
        </div>`;
    }

    case 'shipping_address':
      if (isLandscape) {
        return `
          <div class="label-canvas-container" style="display:flex; flex-direction:row;">
            <div style="width:15%; background:black; color:white; display:flex; align-items:center; justify-content:center; writing-mode:vertical-rl; transform:rotate(180deg);">
              <div class="auto-text" style="font-weight:900; letter-spacing:4px; padding:12px;">${p.service || ''}</div>
            </div>
            <div style="flex:1; display:flex; flex-direction:column; padding:16px; gap:12px;">
              <div style="flex:1; display:flex; flex-direction:column;">
                <div style="font-size:14px; font-weight:800; margin-bottom:4px;">FROM:</div>
                <div class="bound-box" style="align-items:flex-start; justify-content:flex-start;">
                  <div class="auto-text" style="font-weight:600; text-align:left;">${p.sender || ''}</div>
                </div>
              </div>
              <div style="height:3px; background:black; width:100%; flex-shrink:0;"></div>
              <div style="flex:2; display:flex; flex-direction:column;">
                <div style="display:inline-block; background:black; color:white; font-weight:900; padding:4px 8px; align-self:flex-start; margin-bottom:8px; font-size:16px;">SHIP TO:</div>
                <div class="bound-box" style="align-items:flex-start; justify-content:flex-start;">
                  <div class="auto-text" style="font-weight:900; text-align:left;">${p.recipient || ''}</div>
                </div>
              </div>
            </div>
          </div>`;
      }

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column;">
          <div style="height:15%; background:black; color:white; display:flex; align-items:center; justify-content:center;">
            <div class="auto-text" style="font-weight:900; letter-spacing:4px; padding:6px;">${p.service || ''}</div>
          </div>
          <div style="flex:1; display:flex; flex-direction:column; padding:12px; gap:8px;">
            <div style="flex:1; display:flex; flex-direction:column;">
              <div style="font-size:12px; font-weight:800; margin-bottom:4px;">FROM:</div>
              <div class="bound-box" style="align-items:flex-start; justify-content:flex-start;">
                <div class="auto-text" style="font-weight:600; text-align:left;">${p.sender || ''}</div>
              </div>
            </div>
            <div style="height:3px; background:black; width:100%; flex-shrink:0;"></div>
            <div style="flex:2; display:flex; flex-direction:column;">
              <div style="font-size:14px; font-weight:900; margin-bottom:4px; background:black; color:white; padding:4px; align-self:flex-start;">SHIP TO:</div>
              <div class="bound-box" style="align-items:flex-start; justify-content:flex-start;">
                <div class="auto-text" style="font-weight:900; text-align:left;">${p.recipient || ''}</div>
              </div>
            </div>
          </div>
        </div>`;

    case 'inventory_tag':
      if (isLandscape) {
        return `
          <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:12px; gap:6px;">
            <div class="bound-box" style="flex:1; background:black; color:white; border-radius:4px;">
              <div class="auto-text" style="font-weight:900; letter-spacing:2px;">${p.department || ''}</div>
            </div>
            <div class="bound-box" style="flex:2; justify-content:flex-start;">
              <div class="auto-text" style="font-weight:800; text-align:left;">${p.title || ''}</div>
            </div>
            <div class="bound-box" style="flex:1; justify-content:flex-start;">
              <div class="auto-text" style="font-weight:600; font-family:monospace; text-align:left;">${p.sku || ''}</div>
            </div>
          </div>`;
      }

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:8px; text-align:center; gap:8px;">
          <div class="bound-box" style="flex:1; background:black; color:white;">
            <div class="auto-text" style="font-weight:900; letter-spacing:2px;">${p.department || ''}</div>
          </div>
          <div class="bound-box" style="flex:2;">
            <div class="auto-text" style="font-weight:800;">${p.title || ''}</div>
          </div>
          <div class="bound-box" style="flex:1;">
            <div class="auto-text" style="font-weight:600; font-family:monospace;">${p.sku || ''}</div>
          </div>
        </div>`;

    case 'warning_banner':
      return `
        <div class="label-canvas-container" style="background:black; color:white; padding:16px;">
          <div class="bound-box" style="border:6px solid white; padding:8px;">
            <div class="auto-text" style="font-weight:900; text-transform:uppercase; letter-spacing:4px;">${p.text || ''}</div>
          </div>
        </div>`;

    case 'expiration_date': {
      const htmlParts = [];

      if (p.product_name) {
        htmlParts.push(`
          <div class="bound-box" style="flex:2;">
            <div class="auto-text" style="font-weight:800; text-transform:uppercase;">${p.product_name}</div>
          </div>`);
      }

      if (p.made_date) {
        htmlParts.push(`
          <div class="bound-box" style="flex:1; margin-top:4px;">
            <div class="auto-text" style="font-weight:600;">MFG: ${p.made_date}</div>
          </div>`);
      }

      htmlParts.push(`
        <div class="bound-box" style="flex:3; margin-top:8px; border:4px solid black; padding:8px; border-radius:8px;">
          <div class="auto-text" style="font-weight:900;">EXP: ${p.exp_date || ''}</div>
        </div>`);

      return `<div class="label-canvas-container" style="display:flex; flex-direction:column; padding:12px;">${htmlParts.join('')}</div>`;
    }

    case 'default':
      return `
        <div class="label-canvas-container" style="display:flex; align-items:flex-start; justify-content:flex-start; padding:12px;">
          <div class="bound-box" style="align-items:flex-start; justify-content:flex-start;">
            <div class="auto-text" style="font-weight:700; text-align:left;">${p.text || ''}</div>
          </div>
        </div>`;

    case 'center':
      return `
        <div class="label-canvas-container" style="display:flex; align-items:center; justify-content:center; padding:12px;">
          <div class="bound-box">
            <div class="auto-text" style="font-weight:700;">${p.text || ''}</div>
          </div>
        </div>`;

    case 'maximize':
      return `
        <div class="label-canvas-container" style="display:flex; align-items:center; justify-content:center; padding:12px;">
          <div class="bound-box">
            <div class="auto-text" style="font-weight:900;">${p.text || ''}</div>
          </div>
        </div>`;

    case 'address':
      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; justify-content:center; align-items:flex-start; text-align:left; padding:12px;">
          <div class="bound-box" style="align-items:flex-start; justify-content:flex-start;">
            <div class="auto-text" style="font-weight:700; text-align:left;">${p.text || ''}</div>
          </div>
        </div>`;

    case 'jar_apothecary':
      return `
        <div class="label-canvas-container" style="padding:12px;">
          <div style="border:4px solid black; outline:2px solid black; outline-offset:-8px; width:100%; height:100%; display:flex; flex-direction:column; padding:16px; text-align:center;">
            <div style="font-size:16px; letter-spacing:4px; font-weight:700; margin-bottom:auto;">${p.text || 'PREMIUM'}</div>
            <div class="bound-box" style="flex:2; margin:12px 0;">
              <div class="auto-text" style="font-weight:900; text-transform:uppercase; font-family:serif;">${p.title || ''}</div>
            </div>
            <div style="display:flex; align-items:center; justify-content:center; gap:8px; margin:12px 0;">
              <div style="height:2px; background:black; width:40px;"></div>
              <span style="font-size:16px;">✧</span>
              <div style="height:2px; background:black; width:40px;"></div>
            </div>
            <div class="bound-box" style="flex:1;">
              <div class="auto-text" style="font-style:italic; font-weight:bold; font-family:serif;">${p.subtitle || ''}</div>
            </div>
          </div>
        </div>`;

    case 'jar_farmhouse':
      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; border:6px solid black;">
          <div style="height:15%; background:repeating-linear-gradient(45deg, transparent, transparent 4px, black 4px, black 8px); border-bottom:4px solid black;"></div>
          <div style="flex:1; display:flex; flex-direction:column; align-items:center; padding:16px; text-align:center;">
            <div class="bound-box" style="flex:2; width:100%;">
              <div class="auto-text" style="font-weight:900; text-transform:uppercase; font-style:italic; font-family:serif;">${p.title || ''}</div>
            </div>
            <div style="width:100%; height:4px; background:black; margin:16px 0;"></div>
            <div class="bound-box" style="width:100%; flex:1;">
              <div class="auto-text" style="font-weight:bold; letter-spacing:4px; text-transform:uppercase;">${p.subtitle || ''}</div>
            </div>
          </div>
          <div style="height:15%; background:repeating-linear-gradient(45deg, transparent, transparent 4px, black 4px, black 8px); border-top:4px solid black;"></div>
        </div>`;

    case 'centered_text':
    default:
      return `
        <div class="label-canvas-container" style="padding:12px;">
          <div class="bound-box">
            <div class="auto-text" style="font-weight:900;">${p.text || p.title || ''}</div>
          </div>
        </div>`;
  }
};
