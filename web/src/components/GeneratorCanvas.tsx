import { useEffect, useRef, useImperativeHandle, forwardRef, useState } from 'react';
import { DrawConfig, drawFrame, wrapText } from '../utils/drawUtils';
import GIF from 'gif.js';

export interface GeneratorCanvasRef {
  play: () => void;
  record: (format: 'webm' | 'mp4' | 'gif') => Promise<void>;
  stop: () => void;
}

interface GeneratorCanvasProps {
  config: DrawConfig;
  charSpeed: number; // frames per char
  fps: number;
  pauseComma: number;
  pausePunctuation: number;
  dwellTime: number; // seconds
  onComplete?: () => void;
  fontLoaded?: boolean;
}

export const GeneratorCanvas = forwardRef<GeneratorCanvasRef, GeneratorCanvasProps>(
  ({ config, charSpeed, fps, pauseComma, pausePunctuation, dwellTime, onComplete, fontLoaded }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number>();
    const [isRecording, setIsRecording] = useState(false);
    
    // Internal state for animation
    const stateRef = useRef({
      lineIndex: 0,
      charIndex: 0,
      frameCounter: 0,
      pauseCounter: 0,
      lines: [] as string[],
      isFinished: false,
      dwellCounter: 0
    });

    const stopAnimation = () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      setIsRecording(false);
    };

    const resetState = (ctx: CanvasRenderingContext2D) => {
      const lines = wrapText(ctx, config.text, config.boxWidth - config.padding * 2);
      stateRef.current = {
        lineIndex: 0,
        charIndex: 0,
        frameCounter: 0,
        pauseCounter: 0,
        lines,
        isFinished: false,
        dwellCounter: 0
      };
      return lines;
    };

    // Main animation loop that respects target FPS for recording
    const startSequence = async (format: 'preview' | 'webm' | 'mp4' | 'gif' = 'preview') => {
      stopAnimation();
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return;

      resetState(ctx);

      const isRecordingVideo = format === 'webm' || format === 'mp4';
      const isRecordingGif = format === 'gif';
      
      let mediaRecorder: MediaRecorder | null = null;
      let chunks: Blob[] = [];
      let gifEncoder: GIF | null = null;

      if (isRecordingVideo || isRecordingGif) {
        setIsRecording(true);
      }

      if (isRecordingVideo) {
        const stream = canvas.captureStream(fps);
        // Try to respect the requested format if browser supports it
        let mimeType = 'video/webm';
        if (format === 'mp4') {
             if (MediaRecorder.isTypeSupported('video/mp4')) {
                 mimeType = 'video/mp4';
             } else {
                 console.warn("video/mp4 not supported by this browser, falling back to webm");
             }
        } else {
             if (MediaRecorder.isTypeSupported('video/webm;codecs=vp9')) {
                 mimeType = 'video/webm;codecs=vp9';
             }
        }

        mediaRecorder = new MediaRecorder(stream, { 
          mimeType,
          videoBitsPerSecond: 5000000 // 5Mbps
        });

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) chunks.push(e.data);
        };

        mediaRecorder.onstop = () => {
          const blob = new Blob(chunks, { type: mimeType });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `dialogue.${mimeType.includes('mp4') ? 'mp4' : 'webm'}`;
          a.click();
          URL.revokeObjectURL(url);
          setIsRecording(false);
        };

        mediaRecorder.start();
      }

      if (isRecordingGif) {
        gifEncoder = new GIF({
          workers: 2,
          quality: 10,
          width: config.boxWidth,
          height: config.boxHeight,
          workerScript: '/gif.worker.js'
        });
        
        gifEncoder.on('finished', (blob: Blob) => {
           const url = URL.createObjectURL(blob);
           const a = document.createElement('a');
           a.href = url;
           a.download = 'dialogue.gif';
           a.click();
           URL.revokeObjectURL(url);
           setIsRecording(false);
        });
      }

      const interval = 1000 / fps;
      let lastTime = performance.now();
      
      const loop = () => {
        const now = performance.now();
        const delta = now - lastTime;

        if (delta >= interval) {
          lastTime = now - (delta % interval);
          
          const state = stateRef.current;
          const { lines } = state;
          
          // Update Logic
          let shouldStop = false;

          if (state.isFinished) {
            state.dwellCounter++;
            drawFrame(ctx, config, 'full'); // Draw full frame during dwell
            if (state.dwellCounter >= dwellTime * fps) {
              shouldStop = true;
            }
          } else {
             // Drawing Logic
             drawFrame(ctx, config, { 
               lineIndex: state.lineIndex, 
               charIndex: state.charIndex 
             });

             // Step Logic
             if (state.pauseCounter > 0) {
               state.pauseCounter--;
             } else {
               state.frameCounter++;
               if (state.frameCounter >= charSpeed) {
                 state.frameCounter = 0;
                 const currentLine = lines[state.lineIndex];
                 if (currentLine && state.charIndex < currentLine.length) {
                   const char = currentLine[state.charIndex];
                   state.charIndex++;
                   if (char === ',') state.pauseCounter = pauseComma;
                   else if ('.!?'.includes(char)) state.pauseCounter = pausePunctuation;
                 } else {
                   state.lineIndex++;
                   state.charIndex = 0;
                   if (state.lineIndex >= lines.length) {
                     state.isFinished = true;
                   }
                 }
               }
             }
          }

          // Capture frame for GIF
          if (isRecordingGif && gifEncoder) {
            gifEncoder.addFrame(ctx, { copy: true, delay: interval });
          }

          if (shouldStop) {
              if (mediaRecorder && mediaRecorder.state === 'recording') {
                 mediaRecorder.stop();
              }
              if (isRecordingGif && gifEncoder) {
                 gifEncoder.render();
              } else {
                 setIsRecording(false);
              }

              stopAnimation();
              if (onComplete) onComplete();
              return;
          }
        }
        
        animationRef.current = requestAnimationFrame(loop);
      };

      loop();
    };

    useImperativeHandle(ref, () => ({
      play: () => startSequence('preview'),
      record: async (format) => startSequence(format),
      stop: stopAnimation
    }));

    // Initial Static Draw (Preview)
    useEffect(() => {
        if(isRecording) return; // Don't interfere with recording
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        drawFrame(ctx, config, 'full');
    }, [config, fontLoaded]);

    return (
      <div className="relative border border-gray-700 shadow-lg bg-black/50 backdrop-blur-sm rounded-lg overflow-hidden">
        <canvas
          ref={canvasRef}
          width={config.boxWidth}
          height={config.boxHeight}
          className="max-w-full h-auto"
        />
        {isRecording && (
          <div className="absolute top-2 right-2 flex items-center gap-2 bg-red-600 px-3 py-1 rounded-full text-xs font-bold animate-pulse z-50">
            <div className="w-2 h-2 bg-white rounded-full" />
            RECORDING
          </div>
        )}
      </div>
    );
  }
);