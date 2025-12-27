# Dialogue Textbox Generator - Web Version

This is the modern, web-based version of the Dialogue Textbox Generator, built with React, Vite, and HTML5 Canvas.

## Features

- **Live Preview**: See changes instantly as you type or adjust settings.
- **Rich Customization**:
  - Text content & typography (Google Fonts + Custom uploads)
  - Box dimensions and padding
  - Colors (Text, Background, Gradient)
  - Background Images
- **Animation Control**: Adjust FPS, character speed, and pause durations.
- **Export**: Record the animation to **WebM**, **MP4**, or **GIF**.
- **Modern UI**: Dark/Light mode, tooltips, and a clean interface.

## How to Run

1. Open a terminal in this directory (`web`).
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the URL shown in the terminal (usually `http://localhost:5173`) in your browser.

## Building for Production

To create a static build (HTML/CSS/JS) that can be hosted anywhere:

```bash
npm run build
```

The output will be in the `dist` folder.