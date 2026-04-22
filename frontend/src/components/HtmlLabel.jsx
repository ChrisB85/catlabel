import React, { useEffect, useRef } from 'react';
import { applyVars, processHtmlDynamicElements } from '../utils/rendering';
import { useStore } from '../store';
import { LABEL_TEMPLATE_STYLES } from './templateStyles';

const overlayBaseStyle = {
  position: 'absolute',
  pointerEvents: 'none',
  boxSizing: 'border-box'
};

export default function HtmlLabel({
  html,
  record,
  width,
  height,
  canvasBorder = 'none',
  canvasBorderThickness = 4,
  onRenderComplete
}) {
  const containerRef = useRef(null);
  const defaultFont = useStore((state) => state.settings?.default_font) || 'Arial';
  const fontFamily = defaultFont.split('.')[0];
  const processedHtml = applyVars(html || '', record);
  const borderThickness = Math.max(1, Number(canvasBorderThickness) || 4);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return undefined;

    let cancelled = false;

    const process = async () => {
      await processHtmlDynamicElements(container, width, height);
      if (cancelled) return;
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          if (!cancelled && onRenderComplete) {
            onRenderComplete();
          }
        });
      });
    };

    process();

    return () => {
      cancelled = true;
    };
  }, [processedHtml, width, height, onRenderComplete]);

  return (
    <div
      style={{
        width,
        height,
        overflow: 'hidden',
        position: 'relative',
        backgroundColor: 'white',
        color: 'black',
        fontFamily: `'${fontFamily}', sans-serif`
      }}
    >
      <div
        ref={containerRef}
        style={{ width: '100%', height: '100%' }}
        dangerouslySetInnerHTML={{ __html: `<style>${LABEL_TEMPLATE_STYLES}</style>${processedHtml}` }}
      />
      {canvasBorder === 'box' && (
        <div
          style={{
            ...overlayBaseStyle,
            inset: 0,
            border: `${borderThickness}px solid black`
          }}
        />
      )}
      {canvasBorder === 'top' && (
        <div
          style={{
            ...overlayBaseStyle,
            top: 0,
            left: 0,
            right: 0,
            height: borderThickness,
            backgroundColor: 'black'
          }}
        />
      )}
      {canvasBorder === 'bottom' && (
        <div
          style={{
            ...overlayBaseStyle,
            bottom: 0,
            left: 0,
            right: 0,
            height: borderThickness,
            backgroundColor: 'black'
          }}
        />
      )}
      {canvasBorder === 'cut_line' && (
        <div
          style={{
            ...overlayBaseStyle,
            bottom: 0,
            left: 0,
            right: 0,
            borderBottom: `${borderThickness}px dashed black`
          }}
        />
      )}
    </div>
  );
}
