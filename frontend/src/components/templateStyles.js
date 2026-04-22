import { applyVars } from '../utils/rendering';

const DEFAULT_ICON_SRC = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJibGFjayIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTIgMiAxNS4wOSA4LjI2IDIyIDkuMjcgMTcgMTQuMTQgMTguMTggMjEuMDIgMTIgMTcuNzcgNS44MiAyMS4wMiA3IDE0LjE0IDIgOS4yNyA4LjkxIDguMjYgMTIgMiI+PC9wb2x5Z29uPjwvc3ZnPg==';

const buildJarApothecaryMarkup = ({ text = '', title = '', subtitle = '' }) => `
  <div class="label-canvas-container apothecary">
    <div class="inner">
      <div class="bound-box" style="flex: 1;"><div class="auto-text" style="letter-spacing: 4px; font-weight: 700;">${text || 'PREMIUM'}</div></div>
      <div class="bound-box" style="flex: 2; margin: 8px 0;">
        <div class="auto-text" style="font-weight: 900; text-transform: uppercase; font-family: serif;">${title || ''}</div>
      </div>
      <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin: 8px 0; flex: 0.5;">
        <div style="height: 2px; background: black; width: 40px;"></div>
        <span style="font-size: 1.2em;">✧</span>
        <div style="height: 2px; background: black; width: 40px;"></div>
      </div>
      <div class="bound-box" style="flex: 1;">
        <div class="auto-text" style="font-style: italic; font-weight: bold; font-family: serif;">${subtitle || ''}</div>
      </div>
    </div>
  </div>
`;

const buildJarFarmhouseMarkup = ({ title = '', subtitle = '' }) => `
  <div class="label-canvas-container farmhouse">
    <div class="stripes"></div>
    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; padding: 4%; text-align: center;">
      <div class="bound-box" style="flex: 2; width: 100%;">
        <div class="auto-text" style="font-weight: 900; text-transform: uppercase; font-style: italic; font-family: serif;">${title || ''}</div>
      </div>
      <div style="width: 100%; height: 4px; background: black; margin: 4% 0; flex-shrink: 0;"></div>
      <div class="bound-box" style="width: 100%; flex: 1;">
        <div class="auto-text" style="font-weight: bold; letter-spacing: 4px; text-transform: uppercase;">${subtitle || ''}</div>
      </div>
    </div>
    <div class="stripes bottom"></div>
  </div>
`;

export const TEMPLATE_METADATA = [
  {
    id: 'centered_text',
    category: 'Layout',
    name: 'Centered Text',
    description: 'A single, perfectly auto-scaling text block.',
    fields: [{ name: 'text', label: 'Main Text', type: 'textarea', default: 'Centered Text' }],
    html: (p) => `
      <div class="label-canvas-container" style="padding:12px;">
        <div class="bound-box">
          <div class="auto-text" style="font-weight:900;">${p.text || p.title || ''}</div>
        </div>
      </div>`,
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
    html: (p) => `
      <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:12px; gap:8px;">
        <div class="bound-box" style="flex:3;">
          <div class="auto-text" style="font-weight:900; text-transform:uppercase;">${p.title || ''}</div>
        </div>
        <div style="height:4px; background:black; width:80%; margin:0 auto; flex-shrink:0;"></div>
        <div class="bound-box" style="flex:2;">
          <div class="auto-text" style="font-weight:700;">${p.subtitle || ''}</div>
        </div>
      </div>`,
  },
  {
    id: 'icon_text',
    category: 'Layout',
    name: 'Icon + Text',
    description: 'A clean icon next to your text.',
    fields: [
      { name: 'icon_src', label: 'Icon', type: 'icon' },
      { name: 'text', label: 'Text', type: 'text', default: 'Label' },
      {
        name: 'direction',
        label: 'Layout',
        type: 'select',
        options: [
          { label: 'Row (Left to Right)', value: 'row' },
          { label: 'Column (Top to Bottom)', value: 'col' },
        ],
        default: 'row',
      },
    ],
    html: (p) => {
      const isRow = p.direction !== 'col';
      const iconSrc = p.icon_src || DEFAULT_ICON_SRC;

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:${isRow ? 'row' : 'column'}; padding:12px; gap:12px; align-items:center; justify-content:center;">
          <div style="${isRow ? 'width:40%; max-width:40%; height:100%;' : 'width:100%; height:40%; max-height:40%;'} min-width:0; min-height:0; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            <img src="${iconSrc}" style="${isRow ? 'height:100%; max-width:100%;' : 'width:100%; max-height:100%;'} object-fit:contain;" />
          </div>
          <div class="bound-box" style="align-items:${isRow ? 'flex-start' : 'center'}; justify-content:center;">
            <div class="auto-text" style="font-weight:900; text-align:${isRow ? 'left' : 'center'};">${p.text || ''}</div>
          </div>
        </div>`;
    },
  },
  {
    id: 'qr_text',
    category: 'Layout',
    name: 'QR Code + Text',
    description: 'A QR code with adjacent text.',
    fields: [
      { name: 'data', label: 'QR Data', type: 'text', default: 'https://google.com' },
      { name: 'text', label: 'Text', type: 'textarea', default: 'Scan Me' },
    ],
    html: (p, isLandscape) => {
      const qrHtml = p.data ? `<div class="catlabel-code" data-type="qrcode" data-value="${p.data}"></div>` : '';

      if (!qrHtml) {
        return `
          <div class="label-canvas-container" style="padding:12px;">
            <div class="bound-box">
              <div class="auto-text" style="font-weight:900;">${p.text || ''}</div>
            </div>
          </div>`;
      }

      if (isLandscape) {
        return `
          <div class="label-canvas-container" style="display:flex; flex-direction:row; padding:12px; gap:12px;">
            <div style="flex:4; min-width:0; min-height:0; display:flex; align-items:center; justify-content:center;">${qrHtml}</div>
            <div class="bound-box" style="flex:6;"><div class="auto-text" style="font-weight:900;">${p.text || ''}</div></div>
          </div>`;
      }

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:12px; gap:12px;">
          <div style="flex:6; min-width:0; min-height:0; display:flex; align-items:center; justify-content:center;">${qrHtml}</div>
          <div class="bound-box" style="flex:4;"><div class="auto-text" style="font-weight:900;">${p.text || ''}</div></div>
        </div>`;
    },
  },
  {
    id: 'price_tag',
    category: 'Dedicated',
    name: 'Price Tag with Barcode',
    description: 'Retail price tag. Automatically adapts to square or wide labels.',
    fields: [
      { name: 'currency_symbol', label: 'Currency Symbol', type: 'text', default: '$' },
      { name: 'price_main', label: 'Main Price', type: 'text', default: '19' },
      { name: 'price_cents', label: 'Cents', type: 'text', default: '99' },
      { name: 'unit', label: 'Unit (e.g. /ea)', type: 'text', default: '' },
      { name: 'product_name', label: 'Product Name', type: 'text', default: 'Product Name' },
      { name: 'barcode', label: 'Barcode (Leave blank to omit)', type: 'text', default: '123456789' },
    ],
    html: (p, isLandscape) => {
      const unitHtml = p.unit ? `<span style="font-size:0.4em; margin-left:4px;">${p.unit}</span>` : '';
      const barcodeHtml = p.barcode ? `<div class="catlabel-code" data-type="barcode" data-format="code128" data-value="${p.barcode}"></div>` : '';
      const layout = isLandscape && barcodeHtml ? 'row' : 'column';

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:${layout}; padding:12px; gap:${isLandscape ? '12px' : '8px'};">
          <div style="flex:${barcodeHtml ? 6.5 : 1}; display:flex; flex-direction:column; min-width:0; min-height:0;">
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
          </div>
          ${barcodeHtml ? `<div style="flex:3.5; min-width:0; min-height:0; display:flex; align-items:center; justify-content:center;">${barcodeHtml}</div>` : ''}
        </div>`;
    },
  },
  {
    id: 'inventory_tag',
    category: 'Dedicated',
    name: 'Modern Inventory Tag',
    description: 'Professional asset tag with inverted department header and QR/Barcode.',
    fields: [
      { name: 'department', label: 'Department / Category', type: 'text', default: 'WAREHOUSE' },
      { name: 'title', label: 'Item Name', type: 'text', default: 'Item Name' },
      { name: 'sku', label: 'SKU / Subtext', type: 'text', default: 'SKU-123' },
      {
        name: 'code_type',
        label: 'Code Type',
        type: 'select',
        options: [
          { label: 'QR Code', value: 'qrcode' },
          { label: 'Barcode', value: 'barcode' },
        ],
        default: 'qrcode',
      },
      { name: 'code_data', label: 'Code Data', type: 'text', default: 'INV-001' },
    ],
    html: (p, isLandscape) => {
      const codeType = p.code_type === 'barcode' ? 'barcode' : 'qrcode';
      const codeHtml = p.code_data ? `<div class="catlabel-code" data-type="${codeType}" data-format="code128" data-value="${p.code_data}"></div>` : '';

      if (isLandscape) {
        return `
          <div class="label-canvas-container" style="display:flex; flex-direction:${codeHtml ? 'row' : 'column'}; padding:12px; gap:${codeHtml ? '12px' : '6px'}; align-items:${codeHtml ? 'center' : 'stretch'};">
            ${codeHtml ? `<div style="flex:3.5; min-width:0; min-height:0; display:flex; align-items:center; justify-content:center; height:100%;">${codeHtml}</div>` : ''}
            <div style="flex:6.5; min-width:0; min-height:0; display:flex; flex-direction:column; height:100%; gap:6px;">
              <div class="bound-box" style="flex:1; background:black; color:white; border-radius:4px;">
                <div class="auto-text" style="font-weight:900; letter-spacing:2px;">${p.department || ''}</div>
              </div>
              <div class="bound-box" style="flex:2; justify-content:flex-start;">
                <div class="auto-text" style="font-weight:800; text-align:left;">${p.title || ''}</div>
              </div>
              <div class="bound-box" style="flex:1; justify-content:flex-start;">
                <div class="auto-text" style="font-weight:600; font-family:monospace; text-align:left;">${p.sku || ''}</div>
              </div>
            </div>
          </div>`;
      }

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:8px; text-align:center; gap:6px;">
          <div class="bound-box" style="flex:1.5; background:black; color:white; min-height:20%;">
            <div class="auto-text" style="font-weight:900; letter-spacing:2px;">${p.department || ''}</div>
          </div>
          ${codeHtml ? `<div style="flex:4; min-width:0; min-height:0; display:flex; align-items:center; justify-content:center; padding:4px;">${codeHtml}</div>` : ''}
          <div class="bound-box" style="flex:2;">
            <div class="auto-text" style="font-weight:800; line-height:1;">${p.title || ''}</div>
          </div>
          <div class="bound-box" style="flex:1;">
            <div class="auto-text" style="font-weight:600; font-family:monospace;">${p.sku || ''}</div>
          </div>
        </div>`;
    },
  },
  {
    id: 'cable_flag',
    category: 'Dedicated',
    name: 'Cable Flag',
    description: 'Fold-over tag with a dashed center line. Repeats text on both sides.',
    fields: [{ name: 'text', label: 'Cable ID / Text', type: 'text', default: 'CABLE-01' }],
    html: (p, isLandscape) => `
      <div class="label-canvas-container" style="position:relative; display:flex; flex-direction:${isLandscape ? 'row' : 'column'}; padding:0;">
        <div style="position:absolute; ${isLandscape ? 'top:0; bottom:0; left:50%; border-left:3px dashed black; transform:translateX(-50%);' : 'left:0; right:0; top:50%; border-top:3px dashed black; transform:translateY(-50%);'}"></div>
        <div style="flex:1; min-width:0; min-height:0; padding:12px; display:flex;"><div class="bound-box"><div class="auto-text" style="font-weight:900;">${p.text || ''}</div></div></div>
        <div style="flex:1; min-width:0; min-height:0; padding:12px; display:flex;"><div class="bound-box"><div class="auto-text" style="font-weight:900;">${p.text || ''}</div></div></div>
      </div>`,
  },
  {
    id: 'shipping_address',
    category: 'Dedicated',
    name: 'Shipping Address',
    description: 'Professional shipping label with service banner and sender/recipient blocks.',
    fields: [
      { name: 'service', label: 'Service Type', type: 'text', default: 'PRIORITY' },
      { name: 'sender', label: 'Sender Address', type: 'textarea', default: 'John Doe\n123 Sender St.' },
      { name: 'recipient', label: 'Recipient Address', type: 'textarea', default: 'Jane Smith\n456 Recipient Ave.' },
    ],
    html: (p, isLandscape) => {
      if (isLandscape) {
        return `
          <div class="label-canvas-container" style="display:flex; flex-direction:row; padding: 0;">
            <div style="width:15%; background:black; color:white; display:flex; align-items:center; justify-content:center; writing-mode:vertical-rl; transform:rotate(180deg);">
              <div class="bound-box" style="padding: 12px;"><div class="auto-text" style="font-weight:900; letter-spacing:4px;">${p.service || ''}</div></div>
            </div>
            <div style="flex:1; display:flex; flex-direction:column; padding:16px; gap:12px;">
              <div style="flex:1; display:flex; flex-direction:column; min-width:0; min-height:0;">
                <div class="bound-box" style="flex: 0.3; align-items:flex-end; justify-content:flex-start; margin-bottom:4px;">
                   <div class="auto-text" style="font-weight:800; text-align:left;">FROM:</div>
                </div>
                <div class="bound-box" style="flex: 1; align-items:flex-start; justify-content:flex-start;">
                  <div class="auto-text" style="font-weight:600; text-align:left;">${p.sender || ''}</div>
                </div>
              </div>
              <div style="height:3px; background:black; width:100%; flex-shrink:0;"></div>
              <div style="flex:2; display:flex; flex-direction:column; min-width:0; min-height:0;">
                <div class="bound-box" style="flex: 0.4; align-items:flex-end; justify-content:flex-start; background:black; color:white; padding:4px 8px; align-self:flex-start; margin-bottom:8px;">
                   <div class="auto-text" style="font-weight:900; text-align:left;">SHIP TO:</div>
                </div>
                <div class="bound-box" style="flex: 1.6; align-items:flex-start; justify-content:flex-start;">
                  <div class="auto-text" style="font-weight:900; text-align:left;">${p.recipient || ''}</div>
                </div>
              </div>
            </div>
          </div>`;
      }

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; padding: 0;">
          <div style="height:15%; background:black; color:white; display:flex; align-items:center; justify-content:center;">
            <div class="bound-box" style="padding: 6px;"><div class="auto-text" style="font-weight:900; letter-spacing:4px;">${p.service || ''}</div></div>
          </div>
          <div style="flex:1; display:flex; flex-direction:column; padding:12px; gap:8px; min-width:0; min-height:0;">
            <div style="flex:1; display:flex; flex-direction:column; min-width:0; min-height:0;">
              <div class="bound-box" style="flex: 0.3; align-items:flex-end; justify-content:flex-start; margin-bottom:4px;">
                 <div class="auto-text" style="font-weight:800; text-align:left;">FROM:</div>
              </div>
              <div class="bound-box" style="flex: 1; align-items:flex-start; justify-content:flex-start;">
                <div class="auto-text" style="font-weight:600; text-align:left;">${p.sender || ''}</div>
              </div>
            </div>
            <div style="height:3px; background:black; width:100%; flex-shrink:0;"></div>
            <div style="flex:2; display:flex; flex-direction:column; min-width:0; min-height:0;">
              <div class="bound-box" style="flex: 0.3; align-items:flex-end; justify-content:flex-start; background:black; color:white; padding:4px; align-self:flex-start; margin-bottom:4px;">
                 <div class="auto-text" style="font-weight:900; text-align:left;">SHIP TO:</div>
              </div>
              <div class="bound-box" style="flex: 1; align-items:flex-start; justify-content:flex-start;">
                <div class="auto-text" style="font-weight:900; text-align:left;">${p.recipient || ''}</div>
              </div>
            </div>
          </div>
        </div>`;
    },
  },
  {
    id: 'warning_banner',
    category: 'Dedicated',
    name: 'Warning Banner',
    description: 'Inverted black background with bold white text.',
    fields: [{ name: 'text', label: 'Warning Text', type: 'text', default: 'FRAGILE' }],
    html: (p) => `
      <div class="label-canvas-container" style="background:black; color:white; padding:16px;">
        <div class="bound-box" style="border:6px solid white; padding:8px;">
          <div class="auto-text" style="font-weight:900; text-transform:uppercase; letter-spacing:4px;">${p.text || ''}</div>
        </div>
      </div>`,
  },
  {
    id: 'sale_tag',
    category: 'Dedicated',
    name: 'Retail Sale Tag',
    description: 'High contrast inverted price box.',
    fields: [
      { name: 'product_name', label: 'Product', type: 'text', default: 'Sale Item' },
      { name: 'old_price', label: 'Old Price', type: 'text', default: '29.99' },
      { name: 'new_price', label: 'New Price', type: 'text', default: '19.99' },
      { name: 'currency', label: 'Currency', type: 'text', default: '$' },
    ],
    html: (p, isLandscape) => {
      if (isLandscape) {
        return `
          <div class="label-canvas-container" style="display:flex; flex-direction:row;">
            <div style="flex:1; padding:12px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;">
              <div class="bound-box" style="flex:1; align-items:flex-end; justify-content:flex-start;">
                <div class="auto-text" style="font-weight:700; text-align:left;">${p.product_name || ''}</div>
              </div>
              <div class="bound-box" style="flex:1; align-items:flex-start; justify-content:flex-start; margin-top:4px;">
                <div class="auto-text" style="font-weight:900; text-decoration:line-through; color:#666; text-align:left;">${p.currency || ''}${p.old_price || ''}</div>
              </div>
            </div>
            <div style="flex:1; background:black; color:white; display:flex; align-items:center; justify-content:center; padding:16px;">
              <div class="bound-box"><div class="auto-text" style="font-weight:900;">${p.currency || ''}${p.new_price || ''}</div></div>
            </div>
          </div>`;
      }

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column;">
          <div style="flex:1; padding:8px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
            <div class="bound-box" style="flex:1;"><div class="auto-text" style="font-weight:700;">${p.product_name || ''}</div></div>
            <div class="bound-box" style="flex:1; margin-top:4px;"><div class="auto-text" style="font-weight:900; text-decoration:line-through; color:#666;">${p.currency || ''}${p.old_price || ''}</div></div>
          </div>
          <div style="flex:1; background:black; color:white; display:flex; align-items:center; justify-content:center; padding:12px;">
            <div class="bound-box"><div class="auto-text" style="font-weight:900;">${p.currency || ''}${p.new_price || ''}</div></div>
          </div>
        </div>`;
    },
  },
  {
    id: 'asset_tag',
    category: 'Dedicated',
    name: 'IT Asset Tag',
    description: 'Header bar, QR code, and details.',
    fields: [
      { name: 'department', label: 'Department', type: 'text', default: 'IT DEPT' },
      { name: 'asset_id', label: 'Asset ID', type: 'text', default: 'AST-0001' },
      { name: 'description', label: 'Description', type: 'text', default: 'Laptop Computer' },
    ],
    html: (p, isLandscape) => {
      const codeHtml = p.asset_id ? `<div class="catlabel-code" data-type="qrcode" data-value="${p.asset_id}"></div>` : '';

      if (isLandscape && codeHtml) {
        return `
          <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:8px; gap:8px;">
            <div class="bound-box" style="flex:1.4; background:black; color:white;">
              <div class="auto-text" style="font-weight:900; letter-spacing:2px;">${p.department || ''}</div>
            </div>
            <div style="flex:4.6; min-width:0; min-height:0; display:flex; gap:8px;">
              <div style="flex:3.5; min-width:0; min-height:0; display:flex; align-items:center; justify-content:center;">${codeHtml}</div>
              <div style="flex:6.5; min-width:0; min-height:0; display:flex; flex-direction:column; gap:4px;">
                <div class="bound-box" style="flex:2; justify-content:flex-start;"><div class="auto-text" style="font-weight:900; text-align:left;">${p.asset_id || ''}</div></div>
                <div class="bound-box" style="flex:1; justify-content:flex-start;"><div class="auto-text" style="font-weight:500; font-style:italic; text-align:left;">${p.description || ''}</div></div>
              </div>
            </div>
          </div>`;
      }

      return `
        <div class="label-canvas-container" style="display:flex; flex-direction:column; padding:8px; gap:8px;">
          <div class="bound-box" style="flex:1.2; background:black; color:white;">
            <div class="auto-text" style="font-weight:900; letter-spacing:2px;">${p.department || ''}</div>
          </div>
          ${codeHtml ? `<div style="flex:4; min-width:0; min-height:0; display:flex; align-items:center; justify-content:center;">${codeHtml}</div>` : ''}
          <div class="bound-box" style="flex:2;"><div class="auto-text" style="font-weight:900;">${p.asset_id || ''}</div></div>
          <div class="bound-box" style="flex:1;"><div class="auto-text" style="font-weight:500; font-style:italic;">${p.description || ''}</div></div>
        </div>`;
    },
  },
  {
    id: 'spice_jar',
    category: 'Dedicated',
    name: 'Pantry / Spice Jar',
    description: 'Elegant typography for home organization.',
    fields: [
      {
        name: 'style',
        label: 'Design Style',
        type: 'select',
        options: [
          { label: 'Apothecary (Classic)', value: 'jar_apothecary' },
          { label: 'Farmhouse (Stripes & Clean)', value: 'jar_farmhouse' },
        ],
        default: 'jar_apothecary',
      },
      { name: 'title', label: 'Main Label', type: 'text', default: 'BASIL' },
      { name: 'subtitle', label: 'Subtitle / Details', type: 'text', default: 'Sweet & Aromatic' },
      { name: 'text', label: 'Top Text (e.g. Premium)', type: 'text', default: 'PREMIUM' },
    ],
    html: (p) => {
      const isFarmhouse = p.style === 'jar_farmhouse';
      return isFarmhouse ? buildJarFarmhouseMarkup(p) : buildJarApothecaryMarkup(p);
    },
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
    html: (p) => {
      let html = `<div class="label-canvas-container" style="display:flex; flex-direction:column; padding:12px;">`;
      if (p.product_name) html += `<div class="bound-box" style="flex:2;"><div class="auto-text" style="font-weight:800; text-transform:uppercase;">${p.product_name}</div></div>`;
      if (p.made_date) html += `<div class="bound-box" style="flex:1; margin-top:4px;"><div class="auto-text" style="font-weight:600;">MFG: ${p.made_date}</div></div>`;
      html += `<div class="bound-box" style="flex:3; margin-top:8px; border:4px solid black; padding:8px; border-radius:8px;"><div class="auto-text" style="font-weight:900;">EXP: ${p.exp_date || ''}</div></div></div>`;
      return html;
    },
  },
  {
    id: 'default',
    category: 'Legacy',
    name: 'Default',
    description: 'Legacy plain text layout.',
    fields: [{ name: 'text', label: 'Main Text', type: 'textarea', default: 'Label Text' }],
    html: (p) => `
      <div class="label-canvas-container" style="display:flex; align-items:flex-start; justify-content:flex-start; padding:12px;">
        <div class="bound-box" style="align-items:flex-start; justify-content:flex-start;">
          <div class="auto-text" style="font-weight:700; text-align:left;">${p.text || ''}</div>
        </div>
      </div>`,
  },
  {
    id: 'center',
    category: 'Legacy',
    name: 'Center',
    description: 'Legacy centered text layout.',
    fields: [{ name: 'text', label: 'Main Text', type: 'textarea', default: 'Centered Text' }],
    html: (p) => `
      <div class="label-canvas-container" style="display:flex; align-items:center; justify-content:center; padding:12px;">
        <div class="bound-box">
          <div class="auto-text" style="font-weight:700;">${p.text || ''}</div>
        </div>
      </div>`,
  },
  {
    id: 'maximize',
    category: 'Legacy',
    name: 'Maximize',
    description: 'Legacy maximized text layout.',
    fields: [{ name: 'text', label: 'Main Text', type: 'textarea', default: 'BIG TEXT' }],
    html: (p) => `
      <div class="label-canvas-container" style="display:flex; align-items:center; justify-content:center; padding:12px;">
        <div class="bound-box">
          <div class="auto-text" style="font-weight:900;">${p.text || ''}</div>
        </div>
      </div>`,
  },
  {
    id: 'address',
    category: 'Legacy',
    name: 'Address',
    description: 'Legacy address block layout.',
    fields: [{ name: 'text', label: 'Address Text', type: 'textarea', default: '123 Example St.\nCity, ST 12345' }],
    html: (p) => `
      <div class="label-canvas-container" style="display:flex; flex-direction:column; justify-content:center; align-items:flex-start; text-align:left; padding:12px;">
        <div class="bound-box" style="align-items:flex-start; justify-content:flex-start;">
          <div class="auto-text" style="font-weight:700; text-align:left;">${p.text || ''}</div>
        </div>
      </div>`,
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
    html: (p) => buildJarApothecaryMarkup(p),
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
    html: (p) => buildJarFarmhouseMarkup(p),
  },
  {
    id: 'custom',
    category: 'Layout',
    name: 'Custom HTML',
    description: 'Raw HTML entry.',
    fields: [{ name: 'custom_html', label: 'HTML Content', type: 'textarea', default: '<div>Hello</div>' }],
    html: (p) => `<div class="label-canvas-container">${p.custom_html || ''}</div>`,
  },
];

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
  'icon_src',
  'direction',
  'data',
  'currency_symbol',
  'price_main',
  'price_cents',
  'unit',
  'product_name',
  'barcode',
  'department',
  'sku',
  'code_type',
  'code_data',
  'service',
  'sender',
  'recipient',
  'old_price',
  'new_price',
  'currency',
  'asset_id',
  'description',
  'style',
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
  const templateMetadata = getTemplateMetadata(templateId);

  if (typeof templateMetadata.html === 'function') {
    return templateMetadata.html(p, isLandscape);
  }

  let rawHtml = templateMetadata.html || '<div class="label-canvas-container"><div class="bound-box"><div class="auto-text">{{ text }}</div></div></div>';
  Object.entries(p).forEach(([key, val]) => {
    const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
    rawHtml = rawHtml.replace(regex, val);
  });
  return rawHtml;
};
