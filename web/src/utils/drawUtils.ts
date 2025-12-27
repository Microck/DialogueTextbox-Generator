export interface DrawConfig {
  text: string;
  boxWidth: number;
  boxHeight: number;
  padding: number;
  fontSize: number;
  fontFamily: string;
  textColor: string;
  bgColorTop: string;
  bgColorBottom: string;
  gradientDirection: 'vertical' | 'horizontal' | 'none';
  bgImage?: HTMLImageElement | null;
}

export function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number
): string[] {
  const lines: string[] = [];
  const paragraphs = text.split('\n');

  for (const paragraph of paragraphs) {
    if (!paragraph.trim()) {
      lines.push(' ');
      continue;
    }
    
    const words = paragraph.split(' ');
    let currentLine = '';

    for (const word of words) {
      const testLine = currentLine ? `${currentLine} ${word}` : word;
      const metrics = ctx.measureText(testLine);
      
      if (metrics.width > maxWidth) {
        if (currentLine) lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    }
    if (currentLine) lines.push(currentLine);
  }
  return lines.length ? lines : [' '];
}

export function drawFrame(
  ctx: CanvasRenderingContext2D,
  config: DrawConfig,
  progress: { lineIndex: number; charIndex: number } | 'full'
) {
  const {
    boxWidth,
    boxHeight,
    padding,
    fontSize,
    fontFamily,
    textColor,
    bgColorTop,
    bgColorBottom,
    gradientDirection,
    bgImage
  } = config;

  // Clear
  ctx.clearRect(0, 0, boxWidth, boxHeight);

  // Background
  if (bgImage) {
    ctx.drawImage(bgImage, 0, 0, boxWidth, boxHeight);
  } else {
    if (gradientDirection === 'none') {
      ctx.fillStyle = bgColorTop;
      ctx.fillRect(0, 0, boxWidth, boxHeight);
    } else {
      const gradient =
        gradientDirection === 'vertical'
          ? ctx.createLinearGradient(0, 0, 0, boxHeight)
          : ctx.createLinearGradient(0, 0, boxWidth, 0);
      gradient.addColorStop(0, bgColorTop);
      gradient.addColorStop(1, bgColorBottom);
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, boxWidth, boxHeight);
    }
  }

  // Text
  ctx.font = `${fontSize}px "${fontFamily}"`;
  ctx.fillStyle = textColor;
  ctx.textBaseline = 'top';

  const maxWidth = boxWidth - padding * 2;
  // We need to re-wrap text every frame to ensure consistency if font loads/changes
  // Optimization: wrapText could be memoized outside if perf issues arise, but for this scale it's fine.
  const lines = wrapText(ctx, config.text, maxWidth);
  const lineHeight = fontSize * 1.2; // slightly loose line height

  let y = padding;
  
  // If 'full', draw everything
  if (progress === 'full') {
    lines.forEach(line => {
      ctx.fillText(line, padding, y);
      y += lineHeight;
    });
    return;
  }

  // Draw completed lines
  for (let i = 0; i < progress.lineIndex; i++) {
    if (lines[i]) {
      ctx.fillText(lines[i], padding, y);
      y += lineHeight;
    }
  }

  // Draw current partial line
  if (lines[progress.lineIndex]) {
    const currentLineText = lines[progress.lineIndex];
    const partialText = currentLineText.substring(0, progress.charIndex);
    ctx.fillText(partialText, padding, y);
  }
}
