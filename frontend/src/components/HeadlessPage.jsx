import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Layer, Line, Rect, Stage } from 'react-konva';
import { toPng } from 'html-to-image';
import CanvasItemNode from './CanvasItemNode';
import HtmlLabel from './HtmlLabel';

const renderCanvasBorder = (canvasState) => {
  const width = Math.max(1, Number(canvasState?.width) || 384);
  const height = Math.max(1, Number(canvasState?.height) || 384);
  const thickness = canvasState?.canvasBorderThickness || 4;

  if (canvasState?.canvasBorder === 'box') {
    return <Rect width={width} height={height} stroke="black" strokeWidth={thickness} listening={false} />;
  }

  if (canvasState?.canvasBorder === 'top') {
    return <Line points={[0, 0, width, 0]} stroke="black" strokeWidth={thickness} listening={false} />;
  }

  if (canvasState?.canvasBorder === 'bottom') {
    return <Line points={[0, height, width, height]} stroke="black" strokeWidth={thickness} listening={false} />;
  }

  if (canvasState?.canvasBorder === 'cut_line') {
    return <Line points={[0, height, width, height]} stroke="black" strokeWidth={thickness} dash={[10, 10]} listening={false} />;
  }

  return null;
};

export default function HeadlessPage({ state, record, pageIndex, onReady }) {
  const stageRef = useRef(null);
  const containerRef = useRef(null);
  const items = state?.items || [];
  const pageLayouts = state?.pageLayouts || [];
  const width = Math.max(1, Number(state?.width) || 384);
  const height = Math.max(1, Number(state?.height) || 384);
  
  const activeLayout = pageLayouts.find(l => l.pageIndex === pageIndex) 
    || pageLayouts[pageLayouts.length - 1] 
    || { htmlContent: '' };

  const pageItems = useMemo(
    () => {
      const directItems = items.filter((item) => Number(item.pageIndex ?? 0) === pageIndex);
      if (directItems.length > 0) return directItems;
      const maxItemPage = items.reduce((max, item) => Math.max(max, Number(item.pageIndex ?? 0)), 0);
      if (pageIndex > maxItemPage) {
         return items.filter((item) => Number(item.pageIndex ?? 0) === maxItemPage);
      }
      return [];
    }, [items, pageIndex]
  );

  const [htmlReady, setHtmlReady] = useState(false);

  const captureBoth = useCallback(async () => {
    if (!containerRef.current) return;
    try {
      if (document.fonts?.ready) await document.fonts.ready;
      await new Promise(r => setTimeout(r, 100));
      const dataUrl = await toPng(containerRef.current, {
        pixelRatio: 1,
        backgroundColor: 'white',
        useCORS: true,
        cacheBust: true
      });
      onReady(dataUrl);
    } catch (error) {
      console.error('Headless capture failed', error);
    }
  }, [onReady]);

  useEffect(() => {
    if (htmlReady) {
      captureBoth();
    }
  }, [htmlReady, captureBoth, record, state, width, height]);

  return (
    <div ref={containerRef} style={{ width, height, position: 'absolute', backgroundColor: 'white' }}>
      <div style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
        <HtmlLabel
          html={activeLayout.htmlContent || ''}
          record={record}
          width={width}
          height={height}
          canvasBorder={state?.canvasBorder}
          canvasBorderThickness={state?.canvasBorderThickness}
          onRenderComplete={() => setHtmlReady(true)}
        />
      </div>
      <div style={{ position: 'absolute', inset: 0, zIndex: 2 }}>
        <Stage ref={stageRef} width={width} height={height}>
          <Layer>
            <Rect x={0} y={0} width={width} height={height} fill="transparent" listening={false} />
            {renderCanvasBorder(state)}
            {pageItems.map((item) => (
              <CanvasItemNode
                key={item.id}
                item={item}
                record={record}
                canvasWidth={width}
                canvasHeight={height}
              />
            ))}
          </Layer>
        </Stage>
      </div>
    </div>
  );
}
