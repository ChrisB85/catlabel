export const TEMPLATE_MAP = {
  default: { container: 'layout-default', text: 'text-standard', sub: null },
  center: { container: 'layout-center', text: 'text-standard', sub: null },
  maximize: { container: 'layout-center', text: 'text-maximized', sub: null },
  title_subtitle: { container: 'layout-flex-col', text: 'text-title', sub: 'text-subtitle' },
  warning_banner: { container: 'layout-banner', text: 'text-bold-inverted', sub: null },
  price_tag: { container: 'layout-price', text: 'text-huge-price', sub: 'text-product-name' },
  address: { container: 'layout-address', text: 'text-address', sub: null },
  jar_apothecary: { isCustom: true },
  jar_farmhouse: { isCustom: true },
  custom: { container: 'layout-default', text: null, sub: null }
};

export const LABEL_TEMPLATE_STYLES = `
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background: white;
}
body {
  overflow: hidden;
}
.label-canvas-container {
  container-type: size;
  container-name: label;
  width: 100%;
  height: 100%;
  background-color: white;
  box-sizing: border-box;
  overflow: hidden;
  padding: 4cqmin;
  display: flex;
}
.label-canvas-container * {
  box-sizing: border-box;
}
.label-copy {
  max-width: 100%;
  max-height: 100%;
  overflow-wrap: anywhere;
}
.layout-default {
  justify-content: flex-start;
  align-items: flex-start;
}
.layout-center {
  justify-content: center;
  align-items: center;
  text-align: center;
}
.layout-flex-col {
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 4cqh;
}
.layout-banner {
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 0 6cqw;
  background: #111827;
  color: white;
}
.layout-price {
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  text-align: center;
  padding: 10cqh 5cqw;
}
.layout-address {
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  text-align: left;
  padding: 8cqh 10cqw;
}
.text-standard {
  width: 100%;
  font-size: 22cqh;
  font-weight: 700;
  line-height: 1.05;
}
.text-maximized {
  width: 100%;
  font-size: 72cqh;
  font-weight: 900;
  line-height: 0.85;
  text-align: center;
}
.text-title {
  width: 100%;
  font-size: 32cqh;
  font-weight: 900;
  line-height: 0.95;
}
.text-subtitle {
  width: 100%;
  font-size: 16cqh;
  font-weight: 600;
  line-height: 1.1;
}
.text-bold-inverted {
  width: 100%;
  font-size: 30cqh;
  font-weight: 900;
  line-height: 0.95;
  text-transform: uppercase;
}
.text-huge-price {
  font-size: 45cqh;
  font-weight: 900;
  line-height: 1;
}
.text-product-name {
  font-size: 15cqh;
  font-weight: 700;
  line-height: 1.1;
  text-transform: uppercase;
  color: #333333;
}
.text-address {
  width: 100%;
  font-size: 18cqh;
  font-weight: 700;
  line-height: 1.4;
  white-space: pre-wrap;
}
.auto-text-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Apothecary Style */
.apothecary {
  padding: 4cqmin;
}
.apothecary .inner {
  border: 4px solid black;
  height: 100%;
  width: 100%;
  outline: 2px solid black;
  outline-offset: -8px;
  display: flex;
  flex-direction: column;
  padding: 8cqmin;
  text-align: center;
}

/* Farmhouse Style */
.farmhouse {
  display: flex;
  flex-direction: column;
  border: 6px solid black;
  padding: 0 !important;
}
.farmhouse .stripes {
  height: 15cqh;
  background: repeating-linear-gradient(45deg, transparent, transparent 4px, black 4px, black 8px);
  border-bottom: 4px solid black;
}
.farmhouse .stripes.bottom {
  border-bottom: none;
  border-top: 4px solid black;
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
  .replace(/<link[\s\S]*?>/gi, '')
  .replace(/@import\s+(?:url\()?['"]?([^'")]+)['"]?\)?;/gi, '')
  .trim();

export const buildLabelTemplateMarkup = (record = {}) => {
  const safeRecord = record && typeof record === 'object' ? record : {};
  const templateId = safeRecord.template_id || 'default';
  const activeTemplate = TEMPLATE_MAP[templateId] || TEMPLATE_MAP.default;

  if (templateId === 'custom') {
    return [
      '<div class="label-canvas-container">',
      `<div style="width:100%;height:100%;">${sanitizeLabelHtml(safeRecord.custom_html || '')}</div>`,
      '</div>'
    ].join('');
  }

  if (templateId === 'jar_apothecary') {
    return `
      <div class="label-canvas-container apothecary">
        <div class="inner">
          <div style="font-size: 16cqh; letter-spacing: 4px; font-weight: 700; margin-bottom: auto;">${formatText(safeRecord.text || 'PREMIUM')}</div>
          <div class="auto-text-wrapper" style="flex: 2; margin: 8cqmin 0;">
            <div class="auto-text" style="font-weight: 900; text-transform: uppercase; font-family: serif;">${formatText(safeRecord.title || '')}</div>
          </div>
          <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin: 8cqmin 0;">
            <div style="height: 2px; background: black; width: 40px;"></div>
            <span style="font-size: 16cqh;">✧</span>
            <div style="height: 2px; background: black; width: 40px;"></div>
          </div>
          <div class="auto-text-wrapper" style="flex: 1;">
            <div class="auto-text" style="font-style: italic; font-weight: bold; font-family: serif;">${formatText(safeRecord.subtitle || '')}</div>
          </div>
        </div>
      </div>
    `;
  }

  if (templateId === 'jar_farmhouse') {
    return `
      <div class="label-canvas-container farmhouse">
        <div class="stripes"></div>
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; padding: 6cqmin; text-align: center;">
          <div class="auto-text-wrapper" style="flex: 2; width: 100%;">
            <div class="auto-text" style="font-weight: 900; text-transform: uppercase; font-style: italic; font-family: serif;">${formatText(safeRecord.title || '')}</div>
          </div>
          <div style="width: 100%; height: 4px; background: black; margin: 12cqmin 0;"></div>
          <div class="auto-text-wrapper" style="width: 100%; flex: 1;">
            <div class="auto-text" style="font-weight: bold; letter-spacing: 4px; text-transform: uppercase;">${formatText(safeRecord.subtitle || '')}</div>
          </div>
        </div>
        <div class="stripes bottom"></div>
      </div>
    `;
  }

  if (templateId === 'title_subtitle' || templateId === 'price_tag') {
    return [
      `<div class="label-canvas-container ${activeTemplate.container}">`,
      `<div class="label-copy ${activeTemplate.text}">${formatText(safeRecord.title || '')}</div>`,
      `<div class="label-copy ${activeTemplate.sub}">${formatText(safeRecord.subtitle || '')}</div>`,
      '</div>'
    ].join('');
  }

  return [
    `<div class="label-canvas-container ${activeTemplate.container}">`,
    `<div class="label-copy ${activeTemplate.text}">${formatText(safeRecord.text || safeRecord.title || '')}</div>`,
    '</div>'
  ].join('');
};
