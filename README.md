![pixel_perfect_video](https://github.com/user-attachments/assets/36d34cea-eeb7-4df0-a8c2-a77a26b37d8b)
![welcome_to_my_desktop_feel_gradient](https://github.com/user-attachments/assets/76d2b362-d89e-4a47-b75d-277fc78b0abf)

# Dialogue Textbox Generator

Generate pixel-perfect dialogue videos with typing animation, like Undertale/Deltarune.

## Features

- **Pixel-Perfect Rendering** - Crisp text without anti-aliasing
- **Gradient Backgrounds** - Vertical/horizontal gradients or custom images
- **Typing Animation** - Character-by-character with punctuation pauses
- **Sound Effects** - Optional typing sounds
- **Multiple Export Formats** - MP4, WebM, GIF
- **GUI & TUI** - Graphical and terminal interfaces
- **CLI** - Full command-line control
- **Config Files** - Save/load settings as JSON
- **Batch Processing** - Process multiple files at once
- **Auto-open** - Automatically open output when done

## Installation

```bash
pip install pygame opencv-python numpy

# Optional dependencies
pip install tqdm      # Progress bars
pip install Pillow    # GIF export
pip install rich      # TUI interface
```

## Quick Start

### GUI (Recommended)
```bash
python gui.py
```

### TUI (Terminal)
```bash
python tui.py
```

### CLI
```bash
# Basic usage
python generate.py

# With options
python generate.py -i dialogue.txt -o output.mp4 --font-size 24

# Gradient version
python gradient.py --format webm --gradient vertical
```

## File Structure

```
.
├── generate.py      # Pixel-perfect generator (CLI)
├── gradient.py      # Gradient background generator (CLI)
├── gui.py           # Graphical interface
├── tui.py           # Terminal interface
├── dialogue.txt     # Your text
├── your_font.ttf    # Font file
└── portrait.png     # Optional character portrait
```

## CLI Reference

### generate.py (Pixel-Perfect)

```bash
python generate.py [options]

Files:
  -i, --input FILE       Input text file (default: dialogue.txt)
  -o, --output FILE      Output video file (default: dialogue_from_txt.mp4)
  -f, --font FILE        Font file path
  -p, --portrait FILE    Portrait image path
  --sound FILE           Typing sound effect

Settings:
  --font-size N          Font size in pixels (default: 20)
  --max-width N          Max text width before wrap (default: 1000)
  --padding N            Padding around content (default: 10)
  --fps N                Frames per second (default: 30)
  --char-speed N         Frames per character (default: 1)
  --dwell N              Seconds after text completes (default: 2)

Colors:
  --text-color R,G,B     Text color (default: 255,255,255)
  --bg-color R,G,B       Background color (default: 0,0,0)

Export:
  --gif                  Also export as GIF
  --gif-only             Export only GIF (no video)
  --auto-open            Open output when done

Utilities:
  --dry-run              Preview without rendering
  --batch PATTERN        Process multiple files (e.g., "*.txt")
  --init-config          Create default config.json
```

### gradient.py (Gradient Background)

```bash
python gradient.py [options]

Files:
  -i, --input FILE       Input text file (default: dialogue.txt)
  -o, --output NAME      Output name without extension
  -f, --font FILE        Font file path
  --bg-image FILE        Background image (overrides gradient)

Box Settings:
  --width N              Box width (default: 1000)
  --height N             Box height (default: 209)
  --padding N            Padding inside box (default: 20)
  --font-size N          Font size (default: 35)
  --fps N                Frames per second (default: 30)
  --dwell N              Seconds after text (default: 3)

Gradient:
  --gradient TYPE        vertical, horizontal, or none
  --top-color R,G,B,A    Top/left gradient color
  --bottom-color R,G,B,A Bottom/right gradient color
  --text-color R,G,B,A   Text color (default: 0,0,0,255)

Export:
  --format FORMAT        webm, mp4, or gif (default: webm)
  --auto-open            Open output when done

Utilities:
  --dry-run              Preview without rendering
  --batch PATTERN        Process multiple files
  --init-config          Create default gradient_config.json
```

## Config Files

Create default configs:
```bash
python generate.py --init-config
python gradient.py --init-config
```

### config.json (generate.py)
```json
{
  "max_text_width": 1000,
  "padding": 10,
  "font_size": 20,
  "fps": 30,
  "char_speed": 1,
  "video_duration_sec_after_text": 2,
  "text_color": [255, 255, 255],
  "bg_color": [0, 0, 0],
  "auto_open": false,
  "export_gif": false
}
```

### gradient_config.json (gradient.py)
```json
{
  "box_size": [1000, 209],
  "padding": 20,
  "font_size": 35,
  "fps": 30,
  "dwell_time": 3,
  "gradient_direction": "vertical",
  "top_color": [255, 255, 255, 255],
  "bottom_color": [121, 121, 121, 255],
  "text_color": [0, 0, 0, 255],
  "output_format": "webm",
  "auto_open": false
}
```

## Examples

### Custom colors with GIF export
```bash
python generate.py --text-color 0,255,0 --bg-color 20,20,40 --gif
```

### Horizontal gradient
```bash
python gradient.py --gradient horizontal --top-color 255,200,200,255 --bottom-color 200,200,255,255
```

### Batch process all text files
```bash
python generate.py --batch "dialogues/*.txt"
python gradient.py --batch "*.txt" --format gif
```

### Preview without rendering
```bash
python generate.py --dry-run
```

### With typing sound
```bash
python generate.py --sound typing.wav
```

## GUI Features

- **Pixel-Perfect Tab** - Full control over generate.py
- **Gradient Tab** - Full control over gradient.py
- **Batch Tab** - Process multiple files
- **Color Pickers** - Visual color selection
- **Auto-detect** - Find fonts/images automatically
- **Save/Load Config** - Persist your settings

## TUI Features

- **Interactive Menus** - Arrow key navigation
- **File Browser** - See available files
- **Guided Setup** - Step-by-step configuration
- **Progress Display** - Real-time rendering status

## Notes

- ffmpeg required for WebM export (falls back to MP4/OpenCV if missing)
- PIL/Pillow required for GIF export
- Rich library required for TUI
- Font file (.ttf/.otf) required in current directory

## License

Public domain. Use freely.
