# Dialogue Textbox Generator

Generate Undertale/Deltarune-style dialogue videos with typing animation.

## 🌟 **Web Version (Recommended)**

**Use the Web Version for the best experience!**  
The Python CLI/GUI tools are legacy and limited in features. The web version offers a modern interface, live preview, custom fonts, GIF/MP4 export, and much more.

### [Run the Web Version](https://micr.dev/dialogue)

<img width="1920" height="1080" alt="micr-dev-1920x1080desktop-b18983" src="https://github.com/user-attachments/assets/e1a35283-7f21-4c42-978c-bfcac15369a1" />


---

## Legacy Python Tools

> **Note:** These tools are considered deprecated. Please use the web version above.

![GUI](screenshots/gui.png)

### Features

- Typing animation with punctuation pauses
- Solid color, gradient, or image backgrounds
- Export to MP4, WebM, or GIF
- GUI, TUI, and CLI interfaces

### Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.8-3.12 (pygame doesn't support 3.14 yet).

### Usage

#### GUI

```bash
python gui.py
```

Type dialogue directly, choose background type, and generate.

#### TUI

```bash
python tui.py
```

Interactive terminal interface with the same features.

#### CLI

```bash
# Solid background
python generate.py -i dialogue.txt -o output.mp4

# Gradient background
python gradient.py -i dialogue.txt --gradient vertical --format webm
```

## License

Public domain.
