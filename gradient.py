import os
import re
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import sys
import subprocess
import shutil

# --- USER CONFIGURATION ---
BOX_SIZE = (1000, 209)         # (width, height) of the output video/image
PADDING = 20                  # Padding inside the box
FONT_SIZE = 35                # Font size in pixels
FPS = 30                      # Frames per second
DWELL_TIME = 3                # Seconds after text completes

# --- COLORS ---
TEXT_COLOR = (0, 0, 0, 255)        # RGBA color (black)
TOP_COLOR = (0xFF, 0xFF, 0xFF, 255)    # #FFFFFF (white)
BOTTOM_COLOR = (0x79, 0x79, 0x79, 255) # #797979 (gray)

def sanitize_filename(text):
    words = re.findall(r'\w+', text)[:5]
    name = "_".join(words).lower() if words else "dialogue"
    return re.sub(r'[^\w-]', '', name)

def load_font():
    for f in os.listdir("."):
        if f.lower().endswith((".ttf", ".otf")):
            return pygame.font.Font(f, FONT_SIZE)
    print("ERROR: Place a .ttf/.otf font file in this folder")
    sys.exit(1)

def wrap_text(text, font, max_width):
    lines = []
    space = font.size(" ")[0]
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
    return lines

def draw_vertical_gradient(surface, top_color, bottom_color):
    width, height = surface.get_size()
    for y in range(height):
        t = y / (height - 1) if height > 1 else 0
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        a = int(top_color[3] * (1 - t) + bottom_color[3] * t)
        pygame.draw.line(surface, (r, g, b, a), (0, y), (width - 1, y))

def generate_frames(text_lines, font, temp_dir, box_size, padding):
    screen_width, screen_height = box_size
    screen = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    line_height = font.get_height()
    max_lines = (screen_height - 2 * padding) // line_height
    # If too many lines, cut off
    text_lines = text_lines[:max_lines]
    current_line = 0
    current_char = 0
    frame_number = 0

    while current_line < len(text_lines):
        draw_vertical_gradient(screen, TOP_COLOR, BOTTOM_COLOR)
        y = padding
        for i in range(current_line):
            text_surf = font.render(text_lines[i], True, TEXT_COLOR)
            screen.blit(text_surf, (padding, y))
            y += line_height
        if current_line < len(text_lines):
            partial_text = text_lines[current_line][:current_char]
            text_surf = font.render(partial_text, True, TEXT_COLOR)
            screen.blit(text_surf, (padding, y))
            current_char += 1
            if current_char > len(text_lines[current_line]):
                current_line += 1
                current_char = 0
        pygame.image.save(screen, os.path.join(temp_dir, f"frame_{frame_number:04d}.png"))
        frame_number += 1

    # Add final still frames
    for _ in range(int(DWELL_TIME * FPS)):
        draw_vertical_gradient(screen, TOP_COLOR, BOTTOM_COLOR)
        y = padding
        for i, line in enumerate(text_lines):
            text_surf = font.render(line, True, TEXT_COLOR)
            screen.blit(text_surf, (padding, y))
            y += line_height
        pygame.image.save(screen, os.path.join(temp_dir, f"frame_{frame_number:04d}.png"))
        frame_number += 1

    return frame_number, (screen_width, screen_height)

def export_webm(base_name, temp_dir, size):
    output_file = f"{base_name}_gradient.webm"
    width, height = size
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", f"{temp_dir}/frame_%04d.png",
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuv420p",
        "-b:v", "5M",
        "-vf", f"scale={width}:{height}",
        output_file
    ]
    print("Exporting WebM...")
    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"WebM export failed: {e}")
        sys.exit(1)
    return output_file

def main():
    try:
        with open("dialogue.txt", "r", encoding="utf-8") as f:
            dialogue = f.read().strip()
    except FileNotFoundError:
        print("Create 'dialogue.txt' first")
        sys.exit(1)

    pygame.init()
    font = load_font()
    # Wrap text to fit inside the box with padding
    lines = wrap_text(dialogue, font, BOX_SIZE[0] - 2 * PADDING)
    base_name = sanitize_filename(dialogue)

    print(f"Output frame size: {BOX_SIZE[0]}x{BOX_SIZE[1]}")

    temp_dir = f"{base_name}_frames"
    os.makedirs(temp_dir, exist_ok=True)

    print("Generating PNG sequence with vertical gradient background...")
    total_frames, screen_size = generate_frames(lines, font, temp_dir, BOX_SIZE, PADDING)
    print(f"PNG sequence saved to: {temp_dir}/ ({total_frames} frames)")

    # Export WebM
    output = export_webm(base_name, temp_dir, screen_size)
    print(f"\nSUCCESS: {output} created with vertical gradient background!")

    # Cleanup
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()