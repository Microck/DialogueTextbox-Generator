import { useState, useRef, ChangeEvent, useEffect } from 'react';
import { GeneratorCanvas, GeneratorCanvasRef } from './components/GeneratorCanvas';
import { DrawConfig } from './utils/drawUtils';
import { Play, Download, Settings, Type, Palette, Layout, Image as ImageIcon, Type as FontIcon, HelpCircle, ChevronDown, Github } from 'lucide-react';
import { ModeToggle } from './components/mode-toggle';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './components/ui/tooltip';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './components/ui/dropdown-menu';

const PRESET_FONTS = [
  { name: 'Outfit', value: 'Outfit' },
  { name: 'Roboto', value: 'Roboto' },
  { name: 'Open Sans', value: 'Open Sans' },
  { name: 'Pixelify Sans', value: 'Pixelify Sans' },
];

function App() {
  const canvasRef = useRef<GeneratorCanvasRef>(null);

  // --- State ---
  const [text, setText] = useState(`This is a sample text for the Dialogue Generator.
You can type anything here and customize the look!`);
  
  // Dimensions & Layout
  const [boxWidth, setBoxWidth] = useState(600);
  const [boxHeight, setBoxHeight] = useState(150);
  const [padding, setPadding] = useState(20);
  const [fontSize, setFontSize] = useState(21);
  const [selectedFont, setSelectedFont] = useState<string>('Outfit');
  const [customFontName, setCustomFontName] = useState<string | null>(null);
  const [fontLoaded, setFontLoaded] = useState(false);
  
  // Colors
  const [textColor, setTextColor] = useState('#ffffff');
  const [bgColorTop, setBgColorTop] = useState('#000000');
  const [bgColorBottom, setBgColorBottom] = useState('#000000');
  // Extended background type including 'image' for UI state
  const [backgroundType, setBackgroundType] = useState<'solid' | 'vertical' | 'horizontal' | 'image'>('solid');
  
  // Animation
  const [fps, setFps] = useState(30);
  const [charSpeed, setCharSpeed] = useState(1);
  const [dwellTime, setDwellTime] = useState(2);
  const [pauseComma, setPauseComma] = useState(4);
  const [pausePunctuation, setPausePunctuation] = useState(10);

  // Background Image
  const [bgImage, setBgImage] = useState<HTMLImageElement | null>(null);

  // Ensure fonts are loaded before initial draw
  useEffect(() => {
    document.fonts.ready.then(() => {
      setFontLoaded(true);
    });
  }, []);

  const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const img = new Image();
        img.onload = () => setBgImage(img);
        img.src = event.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFontUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        const arrayBuffer = await file.arrayBuffer();
        // Clean name for CSS
        const fontName = file.name.split('.')[0].replace(/[^a-zA-Z0-9]/g, '');
        const fontFace = new FontFace(fontName, arrayBuffer);
        
        await fontFace.load();
        document.fonts.add(fontFace);
        setCustomFontName(fontName);
        setSelectedFont('custom'); // Switch dropdown to 'custom'
        setFontLoaded(prev => !prev); // Trigger re-render
      } catch (err) {
        console.error("Failed to load font:", err);
        alert("Failed to load font file. Please try a valid TTF/OTF/WOFF file.");
      }
    }
  };

  const currentFontFamily = selectedFont === 'custom' && customFontName ? customFontName : selectedFont;

  // Map UI state to config
  const gradientDirection = backgroundType === 'image' || backgroundType === 'solid' ? 'none' : backgroundType;
  
  // If backgroundType is 'image', we must ensure bgImage is used. 
  // If it's NOT 'image', we pass null for bgImage so it doesn't render even if one is loaded in state.
  const activeBgImage = backgroundType === 'image' ? bgImage : null;

  const config: DrawConfig = {
    text,
    boxWidth,
    boxHeight,
    padding,
    fontSize,
    fontFamily: currentFontFamily,
    textColor,
    bgColorTop,
    bgColorBottom,
    gradientDirection: gradientDirection as 'none' | 'vertical' | 'horizontal',
    bgImage: activeBgImage
  };

  return (
    <TooltipProvider delayDuration={300}>
      <div className="h-screen flex flex-col md:flex-row font-sans bg-background text-foreground transition-colors duration-300 overflow-hidden">
        
        {/* Sidebar Controls - Scrollable */}
        <div className="w-full md:w-96 border-r bg-card flex flex-col h-full z-20 shadow-xl">
          <div className="flex items-center justify-between p-6 border-b shrink-0 bg-card">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight">
                Dialogue Gen
              </h1>
              <a 
                href="https://github.com/Microck/DialogueTextbox-Generator" 
                target="_blank" 
                rel="noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github size={20} />
              </a>
            </div>
            <ModeToggle />
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
            
            {/* Text Input */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Type size={16} /> Content
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  className="font-mono text-sm min-h-[120px]"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Enter your dialogue here..."
                />
              </CardContent>
            </Card>

            {/* Typography */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <FontIcon size={16} /> Typography
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="fontSize">Font Size</Label>
                    <Input id="fontSize" type="number" value={fontSize} onChange={e => setFontSize(Number(e.target.value))} />
                </div>
                
                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="fontSelect">Font Family</Label>
                    <Select value={selectedFont} onValueChange={setSelectedFont}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select font" />
                      </SelectTrigger>
                      <SelectContent>
                        {PRESET_FONTS.map(font => (
                          <SelectItem key={font.value} value={font.value} style={{ fontFamily: font.value }}>
                            {font.name}
                          </SelectItem>
                        ))}
                        <SelectItem value="custom">
                          Custom {customFontName ? `(${customFontName})` : ''}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                </div>

                {selectedFont === 'custom' && (
                  <div className="grid w-full items-center gap-1.5 pt-2 border-t border-border animate-in fade-in slide-in-from-top-1 duration-200">
                      <Label htmlFor="fontUpload" className="text-xs text-muted-foreground">Upload Custom Font</Label>
                      <Input 
                        id="fontUpload"
                        type="file" 
                        accept=".ttf,.otf,.woff,.woff2" 
                        onChange={handleFontUpload}
                        className="cursor-pointer text-xs h-9"
                      />
                      {!customFontName && (
                        <p className="text-[10px] text-amber-500 italic">Please upload a font file to use this mode.</p>
                      )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Layout */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Layout size={16} /> Dimensions
                </CardTitle>
              </CardHeader>
              <CardContent>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="grid gap-1.5">
                        <Label htmlFor="width">Width</Label>
                        <Input id="width" type="number" value={boxWidth} onChange={e => setBoxWidth(Number(e.target.value))} />
                    </div>
                    <div className="grid gap-1.5">
                        <Label htmlFor="height">Height</Label>
                        <Input id="height" type="number" value={boxHeight} onChange={e => setBoxHeight(Number(e.target.value))} />
                    </div>
                    <div className="grid gap-1.5">
                        <Label htmlFor="padding">Padding</Label>
                        <Input id="padding" type="number" value={padding} onChange={e => setPadding(Number(e.target.value))} />
                    </div>
                  </div>
              </CardContent>
            </Card>

            {/* Colors & Appearance */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Palette size={16} /> Appearance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="textColor">Text Color</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground font-mono">{textColor}</span>
                    <Input id="textColor" type="color" value={textColor} onChange={e => setTextColor(e.target.value)} className="w-8 h-8 p-0 border-0 rounded-full overflow-hidden cursor-pointer" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Background Type</Label>
                  <Select value={backgroundType} onValueChange={(val: any) => setBackgroundType(val)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="solid">Solid Color</SelectItem>
                        <SelectItem value="vertical">Vertical Gradient</SelectItem>
                        <SelectItem value="horizontal">Horizontal Gradient</SelectItem>
                        <SelectItem value="image">Background Image</SelectItem>
                      </SelectContent>
                  </Select>
                </div>

                {backgroundType !== 'image' && (
                  <>
                    <div className="flex items-center justify-between animate-in fade-in slide-in-from-top-1 duration-200">
                      <Label htmlFor="bgColorTop">{backgroundType === 'solid' ? 'Background' : 'Start Color'}</Label>
                      <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground font-mono">{bgColorTop}</span>
                          <Input id="bgColorTop" type="color" value={bgColorTop} onChange={e => setBgColorTop(e.target.value)} className="w-8 h-8 p-0 border-0 rounded-full overflow-hidden cursor-pointer" />
                      </div>
                    </div>

                    {(backgroundType === 'vertical' || backgroundType === 'horizontal') && (
                      <div className="flex items-center justify-between animate-in fade-in slide-in-from-top-1 duration-200">
                        <Label htmlFor="bgColorBottom">End Color</Label>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground font-mono">{bgColorBottom}</span>
                          <Input id="bgColorBottom" type="color" value={bgColorBottom} onChange={e => setBgColorBottom(e.target.value)} className="w-8 h-8 p-0 border-0 rounded-full overflow-hidden cursor-pointer" />
                        </div>
                      </div>
                    )}
                  </>
                )}

                {backgroundType === 'image' && (
                  <div className="pt-3 border-t border-border animate-in fade-in slide-in-from-top-1 duration-200">
                      <div className="flex items-center justify-between mb-2">
                        <Label className="flex items-center gap-2 text-xs text-muted-foreground">
                            <ImageIcon size={14} /> Upload Image
                        </Label>
                        {bgImage && (
                            <Button variant="destructive" size="sm" onClick={() => setBgImage(null)} className="h-6 px-2 text-xs">Clear</Button>
                        )}
                      </div>
                      <Input 
                        type="file" 
                        accept="image/*" 
                        onChange={handleImageUpload}
                        className="cursor-pointer text-xs"
                      />
                      {!bgImage && (
                        <p className="text-[10px] text-amber-500 italic mt-1">Select an image file to display.</p>
                      )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Animation Settings */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Settings size={16} /> Animation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-1.5">
                      <Label htmlFor="fps">FPS</Label>
                      <Input id="fps" type="number" value={fps} onChange={e => setFps(Number(e.target.value))} />
                    </div>
                    <div className="grid gap-1.5">
                      <div className="flex items-center gap-1">
                        <Label htmlFor="charSpeed">Char Speed</Label>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <HelpCircle size={12} className="text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent side="top">
                            <p>How many frames it takes to type one character.</p>
                            <p>Lower = Faster typing.</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                      <Input id="charSpeed" type="number" value={charSpeed} onChange={e => setCharSpeed(Number(e.target.value))} />
                    </div>
                    <div className="grid gap-1.5">
                      <div className="flex items-center gap-1">
                        <Label htmlFor="pauseComma">Comma Pause</Label>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <HelpCircle size={12} className="text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent side="top">
                            <p>Extra frames to wait when a comma is typed.</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                      <Input id="pauseComma" type="number" value={pauseComma} onChange={e => setPauseComma(Number(e.target.value))} />
                    </div>
                    <div className="grid gap-1.5">
                      <div className="flex items-center gap-1">
                        <Label htmlFor="pausePunctuation">Punctuation</Label>
                         <Tooltip>
                          <TooltipTrigger asChild>
                            <HelpCircle size={12} className="text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent side="top">
                            <p>Extra frames to wait for . ! or ?</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                      <Input id="pausePunctuation" type="number" value={pausePunctuation} onChange={e => setPausePunctuation(Number(e.target.value))} />
                    </div>
                    <div className="col-span-2 grid gap-1.5">
                       <div className="flex items-center gap-1">
                        <Label htmlFor="dwellTime">End Dwell (sec)</Label>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <HelpCircle size={12} className="text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent side="top">
                            <p>How long the video stays still after typing finishes.</p>
                          </TooltipContent>
                        </Tooltip>
                       </div>
                       <Input id="dwellTime" type="number" value={dwellTime} onChange={e => setDwellTime(Number(e.target.value))} />
                    </div>
                </div>
              </CardContent>
            </Card>

          </div>
        </div>

        {/* Main Preview Area - Fixed, Non-Scrollable */}
        <div className="flex-1 bg-background flex flex-col items-center justify-center p-10 relative overflow-hidden h-full">
          <div className="absolute top-6 right-6 flex gap-3 z-20">
              <Button 
                variant="outline"
                onClick={() => canvasRef.current?.play()}
                className="gap-2"
              >
                <Play size={16} />
                Preview
              </Button>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button className="gap-2">
                    <Download size={16} />
                    Export
                    <ChevronDown size={14} className="opacity-70" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => canvasRef.current?.record('webm')}>
                    Export as WebM
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => canvasRef.current?.record('mp4')}>
                    Export as MP4 (Experimental)
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => canvasRef.current?.record('gif')}>
                    Export as GIF
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
          </div>

          {/* Grid Pattern */}
          <div className="absolute inset-0 opacity-10 pointer-events-none" 
                style={{ backgroundImage: 'radial-gradient(circle, currentColor 1px, transparent 1px)', backgroundSize: '24px 24px' }} 
          />

          <div className="z-10 shadow-2xl ring-1 ring-border rounded-sm overflow-hidden bg-card max-h-full max-w-full">
              <GeneratorCanvas 
                  ref={canvasRef}
                  config={config}
                  fps={fps}
                  charSpeed={charSpeed}
                  pauseComma={pauseComma}
                  pausePunctuation={pausePunctuation}
                  dwellTime={dwellTime}
                  fontLoaded={fontLoaded}
              />
          </div>
          
        </div>
      </div>
    </TooltipProvider>
  );
}

export default App;
