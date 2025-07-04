![pixel_perfect_video](https://github.com/user-attachments/assets/36d34cea-eeb7-4df0-a8c2-a77a26b37d8b)
![welcome_to_my_desktop_feel_gradient](https://github.com/user-attachments/assets/76d2b362-d89e-4a47-b75d-277fc78b0abf)


## Features

*   **Text from File:** Reads all dialogue directly from a simple `dialogue.txt` file.
*   **Automatic Asset Detection:** Automatically finds and uses a font file (`.ttf`/`.otf`) and a portrait image (`.png`/`.jpg`) placed in the same folder.
*   **Adaptive Resolution:** Dynamically calculates the video resolution to perfectly fit your text and portrait, minimizing wasted space.
*   **Pixel-Perfect Rendering:** Creates crisp, pixel-perfect font rendering (no anti-aliasing) for an authentic retro feel, just like in games like Undertale or Deltarune.
*   **Easy to Customize:** Key settings like font size, typing speed, and padding are all at the top of the script for easy tweaking.

## How to Use

### 1. Prerequisites

You need Python and the following libraries installed. You can install them using pip:

```bash
pip install pygame opencv-python numpy
```

### 2. Folder Setup

Place your files in a single folder like this:

```
.
├── generate_dialogue.py  # The Python script
├── dialogue.txt          # Your dialogue text
├── your_font.ttf         # Your chosen font file
└── portrait.png          # (Optional) Your character portrait
```

*   **`dialogue.txt`**: Create this file and write your dialogue inside. Use the Enter key to create new lines.
*   **Font**: Add any `.ttf` or `.otf` font file to the folder. The script will find it automatically.
*   **Portrait**: (Optional) Add a single `.png` or `.jpg` image to act as the character portrait.

### 3. Configure the Script

Open the Python script and adjust the settings in the `--- CONFIGURATION ---` section to your liking.

**Layout and Video Settings:**
```python
# --- LAYOUT & VIDEO SETTINGS ---
MAX_TEXT_WIDTH = 1000
PADDING = 10

# General settings
OUTPUT_FILENAME = "dialogue_from_txt.mp4"
FONT_SIZE = 20
VIDEO_DURATION_SEC_AFTER_TEXT = 2
```

**Frame-Based Timing Rules:**
You can also adjust the core timing rules directly in the script. These values are measured in frames (the video runs at 30 frames per second). Only working in 'dialogue.py'

```python
# Timing rules (in frames)
CHAR_SPEED = 1
PAUSE_COMMA = 4
PAUSE_PUNCTUATION = 10
```

### 4. Run It!

Open a terminal or command prompt in your project folder and run the script:

```bash
python generate_dialogue.py
```

The script will print its progress and save the final video (e.g., `dialogue_from_txt.mp4`) in the same folder.

## Update

**20/06/2024 `gradient.py`**

- **Fixed-Size Output:** You can now set a fixed output size (e.g., `512x512` or `1024x1024`) for your video, making it easy to create perfectly square or custom-sized dialogue boxes for any project.
- **Vertical Gradient Background:** The background now supports a vertical gradient (e.g., white at the top, gray at the bottom) for a modern, stylish look—just like in Spline or visual novels.
- **True Left-Aligned Text:** Text is always left-aligned and never stretched or centered, ensuring a clean, readable layout.
- **Automatic Text Wrapping:** The script automatically wraps your text to fit inside the box, respecting your chosen padding and font size.
- **Easy Customization:** All key layout options (`BOX_SIZE`, `PADDING`, `FONT_SIZE`) are now at the top of the script for quick adjustments.

**How to use the new features:**  
Just set your desired `BOX_SIZE`, `PADDING`, and `FONT_SIZE` at the top of the script. The rest is automatic!

## License

This project is released into the public domain. Feel free to use, modify, and distribute it as you see fit.
