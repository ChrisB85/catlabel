import { useEffect, useState } from 'react';
import Konva from 'konva';
import bwipjs from 'bwip-js';
import QRCode from 'qrcode';

const loadInjectedImage = (src) => new Promise((resolve) => {
  const image = document.createElement('img');
  image.onload = () => resolve(image);
  image.onerror = () => resolve(null);
  image.src = src;
});

export const processHtmlDynamicElements = async (container, width, height, isCancelled) => {
  // 1. Process codes (QR/Barcode)
  const codeEls = Array.from(container.querySelectorAll('.catlabel-code'));

  for (const el of codeEls) {
    if (isCancelled && isCancelled()) return;

    const type = el.getAttribute('data-type');
    const format = el.getAttribute('data-format') || 'code128';
    const value = el.getAttribute('data-value') || '';

    if (!value) {
      el.innerHTML = '';
      continue;
    }

    try {
      let dataUrl = null;

      if (type === 'barcode') {
        const canvas = document.createElement('canvas');
        bwipjs.toCanvas(canvas, {
          bcid: format,
          text: value,
          scale: 3,
          includetext: false,
          backgroundcolor: 'FFFFFF'
        });
        dataUrl = canvas.toDataURL('image/png');
      } else if (type === 'qrcode') {
        dataUrl = await QRCode.toDataURL(value, {
          margin: 1,
          scale: 4,
          color: { dark: '#000000', light: '#FFFFFF' }
        });
      }

      if (dataUrl) {
        const image = await loadInjectedImage(dataUrl);
        if (isCancelled && isCancelled()) return;

        if (image) {
          image.style.maxWidth = '100%';
          image.style.maxHeight = '100%';
          image.style.width = '100%';
          image.style.height = '100%';
          image.style.objectFit = 'contain';
          el.replaceChildren(image);
        }
      }
    } catch (error) {
      console.error('Failed to generate dynamic code element', error);
    }
  }

  if (isCancelled && isCancelled()) return;

  // 2. Wait for all injected images to load
  const imgEls = Array.from(container.querySelectorAll('img'));
  await Promise.all(imgEls.map((img) => {
    if (img.complete) return Promise.resolve();
    return new Promise((resolve) => {
      img.onload = resolve;
      img.onerror = resolve;
    });
  }));

  if (isCancelled && isCancelled()) return;

  // =========================================================================
  // THREE-PASS AUTO-SCALING PIPELINE
  // =========================================================================

  // Force a complete DOM reflow so the browser calculates flex layouts perfectly
  // before we attempt to read any bounding boxes.
  container.offsetHeight;

  const boxes = Array.from(container.querySelectorAll('.bound-box'));

  // PASS 1: READ
  const boxMetrics = boxes.map((box) => {
    const rect = box.getBoundingClientRect();
    const style = window.getComputedStyle(box);

    return {
      outerW: Math.max(1, rect.width),
      outerH: Math.max(1, rect.height),
      innerW: Math.max(1, rect.width - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight)),
      innerH: Math.max(1, rect.height - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom))
    };
  });

  // PASS 2: LOCK (WRITE)
  boxes.forEach((box, i) => {
    box.style.width = `${boxMetrics[i].outerW}px`;
    box.style.height = `${boxMetrics[i].outerH}px`;
    box.style.flex = 'none';
    box.style.minWidth = 'unset';
    box.style.minHeight = 'unset';
    box.style.maxWidth = 'unset';
    box.style.maxHeight = 'unset';
  });

  if (isCancelled && isCancelled()) return;

  // PASS 3: BINARY SCALE
  const autoTexts = Array.from(container.querySelectorAll('.auto-text'));

  autoTexts.forEach((el) => {
    const parentBox = el.closest('.bound-box');
    if (!parentBox) return;

    const pIndex = boxes.indexOf(parentBox);
    const targetW = boxMetrics[pIndex].innerW;
    const targetH = boxMetrics[pIndex].innerH;

    el.style.width = '100%';
    el.style.height = 'auto';

    let low = 1;
    let high = 500;
    let best = 1;

    while (high - low >= 0.5) {
      const mid = (low + high) / 2;
      el.style.fontSize = `${mid}px`;

      const rect = el.getBoundingClientRect();

      // Use Math.ceil to prevent fractional pixel differences from causing premature shrinking
      const overflowsH = Math.ceil(el.scrollWidth) > targetW + 1;
      const overflowsV = Math.ceil(rect.height) > targetH + 1;

      if (overflowsH || overflowsV) {
        high = mid - 0.5;
      } else {
        best = mid;
        low = mid + 0.5;
      }
    }

    el.style.fontSize = `${Math.floor(best * 10) / 10}px`;
  });
};

export const applyVars = (str, record) => {
  if (!str) return str;

  let result = String(str);

  if (record) {
    Object.keys(record).forEach((key) => {
      const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`{{\\s*${escapedKey}\\s*}}`, 'g');
      result = result.replace(regex, String(record[key] ?? ''));
    });
  }

  const now = new Date();
  const formatYMD = (dateObj) => {
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  result = result.replace(/{{\s*\$date\s*}}/g, formatYMD(now));
  result = result.replace(/{{\s*\$time\s*}}/g, now.toTimeString().substring(0, 5));
  result = result.replace(/{{\s*\$date([+-])(\d+)\s*}}/g, (match, op, daysStr) => {
    const days = parseInt(daysStr, 10);
    const nextDate = new Date(now);
    nextDate.setDate(nextDate.getDate() + (op === '+' ? days : -days));
    return formatYMD(nextDate);
  });

  return result;
};

export const useCodeGenerator = (type, data, barcodeType) => {
  const [src, setSrc] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const generate = async () => {
      if (!data || (type !== 'barcode' && type !== 'qrcode')) {
        if (!cancelled) setSrc(null);
        return;
      }

      if (type === 'barcode') {
        const canvas = document.createElement('canvas');

        try {
          let bcid = 'code128';
          if (barcodeType === 'code39') bcid = 'code39';
          if (barcodeType === 'ean13') bcid = 'ean13';

          bwipjs.toCanvas(canvas, {
            bcid,
            text: String(data),
            scale: 6,
            includetext: false,
            backgroundcolor: 'FFFFFF'
          });

          if (!cancelled) {
            setSrc(canvas.toDataURL('image/png'));
          }
        } catch (error) {
          console.error('Failed to generate barcode', error);
          if (!cancelled) setSrc(null);
        }

        return;
      }

      try {
        const dataUrl = await QRCode.toDataURL(String(data), {
          margin: 1,
          scale: 12,
          color: { dark: '#000000', light: '#FFFFFF' }
        });

        if (!cancelled) {
          setSrc(dataUrl);
        }
      } catch (error) {
        console.error('Failed to generate QR code', error);
        if (!cancelled) setSrc(null);
      }
    };

    generate();

    return () => {
      cancelled = true;
    };
  }, [barcodeType, data, type]);

  return src;
};

export const resolveDim = (dim, maxDim) => {
  if (typeof dim === 'string' && dim.endsWith('%')) {
    return (parseFloat(dim) / 100) * maxDim;
  }
  return Number(dim) || 0;
};

export const computeOptimalTextSize = (baseItem, textToFit, targetWidth, targetHeight) => {
  const fontFamily = baseItem.font ? baseItem.font.split('.')[0] : 'Arial';
  const fontStyleAttr = [
    baseItem.italic ? 'italic' : '',
    baseItem.weight || 700
  ].filter(Boolean).join(' ');

  let low = 6;
  let high = 800;
  let bestSize = baseItem.size || 24;

  const textNode = new Konva.Text({
    text: textToFit,
    fontFamily,
    fontStyle: fontStyleAttr,
    wrap: baseItem.no_wrap ? 'none' : 'word',
    lineHeight: baseItem.lineHeight ?? (String(textToFit).includes('\n') ? 1.15 : 1),
    padding: baseItem.padding !== undefined ? Number(baseItem.padding) : 0,
  });

  const words = String(textToFit).split(/\s+/).filter(Boolean);
  const tempWordNode = new Konva.Text({
    fontFamily,
    fontStyle: fontStyleAttr,
  });

  while (high - low >= 0.5) {
    const mid = (low + high) / 2;
    textNode.fontSize(mid);

    if (!baseItem.no_wrap) {
      textNode.width(targetWidth);
    } else {
      textNode.width(undefined);
    }

    const metrics = textNode.getClientRect();
    const italicBleed = baseItem.italic ? (mid * 0.15) : 0;

    let wordOverflow = false;
    tempWordNode.fontSize(mid);
    for (const word of words) {
      tempWordNode.text(word);
      if (tempWordNode.width() + italicBleed > targetWidth) {
        wordOverflow = true;
        break;
      }
    }

    if (metrics.width + italicBleed <= targetWidth && metrics.height <= targetHeight && !wordOverflow) {
      bestSize = mid;
      low = mid + 0.5;
    } else {
      high = mid - 0.5;
    }
  }

  textNode.destroy();
  tempWordNode.destroy();
  return Math.floor(bestSize * 10) / 10;
};

export const calculateAutoFitItem = (item, batchRecords = [{}], canvasWidth = 384, canvasHeight = 384) => {
  if (!item?.fit_to_width) return item;
  if (item.batch_scale_mode === 'individual') return item;

  const records = Array.isArray(batchRecords) && batchRecords.length > 0 ? batchRecords : [{}];
  const strings = records.map((record) => applyVars(item.text, record) || '');
  const uniqueStrings = [...new Set(strings)].sort((a, b) => b.length - a.length);
  const stringsToTest = uniqueStrings.filter((value) => String(value).length > 0).slice(0, 10);

  const resolvedW = resolveDim(item.width || 100, canvasWidth);
  const resolvedH = resolveDim(item.height || 50, canvasHeight);

  if (item.type === 'text') {
    const pad = item.padding !== undefined ? Number(item.padding) : 0;
    const targetWidth = Math.max(10, resolvedW - (pad * 2));
    const targetHeight = Math.max(10, resolvedH - (pad * 2));

    let overallBestSize = null;
    for (const actualText of stringsToTest) {
      const bestSize = computeOptimalTextSize(item, actualText, targetWidth, targetHeight);
      if (overallBestSize === null || bestSize < overallBestSize) {
        overallBestSize = bestSize;
      }
    }

    return { ...item, size: overallBestSize || item.size };
  }

  if (item.type === 'icon_text') {
    let overallBestScale = null;

    for (const actualText of stringsToTest) {
      const textNode = new Konva.Text({
        text: actualText,
        fontFamily: item.font ? item.font.split('.')[0] : 'Arial',
        fontStyle: (item.weight || 700).toString(),
        fontSize: 100,
      });
      const tWidth = textNode.getClientRect().width;
      textNode.destroy();

      const baseRatio = item.icon_size / item.size;
      const testIconSize = 100 * baseRatio;
      const testGap = Math.max(4, 100 * 0.08);
      const totalW = testIconSize + testGap + tWidth;

      const scaleToFitWidth = resolvedW / totalW;
      const scaleToFitHeight = resolvedH / Math.max(testIconSize, 100);

      const bestScale = Math.min(scaleToFitWidth, scaleToFitHeight);
      if (overallBestScale === null || bestScale < overallBestScale) {
        overallBestScale = bestScale;
      }
    }

    if (overallBestScale) {
      const newSize = Math.floor(100 * overallBestScale * 10) / 10;
      const newIconSize = Math.floor(100 * (item.icon_size / item.size) * overallBestScale * 10) / 10;
      const GAP = Math.max(4, newSize * 0.08);
      const newH = Math.max(newIconSize, newSize);

      return {
        ...item,
        size: newSize,
        icon_size: newIconSize,
        icon_y: (newH - newIconSize) / 2,
        text_x: newIconSize + GAP,
        text_y: (newH / 2) - ((newSize * 0.71) / 2),
      };
    }
  }

  return item;
};
