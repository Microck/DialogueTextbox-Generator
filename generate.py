import pygame
import cv2
import numpy as np
import sys
import os

# --- CONFIGURATION ---

# --- LAYOUT & VIDEO SETTINGS ---
# The maximum width for the text block before it wraps.
MAX_TEXT_WIDTH = 1000
# The padding (in pixels) around all the content.
PADDING = 10

# General settings
OUTPUT_FILENAME = "dialogue_from_txt.mp4"
FONT_SIZE = 20
VIDEO_DURATION_SEC_AFTER_TEXT = 2

# --- SCRIPT ---

# Constants
VIDEO_CODEC = "mp4v"
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PORTRAIT_PADDING = 15

# Timing rules (in frames)
CHAR_SPEED = 1
PAUSE_COMMA = 4
PAUSE_PUNCTUATION = 10


def find_assets(output_filename):
    """Automatically find font and portrait files in the current directory."""
    font_path, portrait_path = None, None
    font_ext = (".ttf", ".otf")
    image_ext = (".png", ".jpg", ".jpeg", ".bmp")
    for filename in os.listdir("."):
        if not font_path and filename.lower().endswith(font_ext):
            font_path = filename
        if (
            not portrait_path
            and filename.lower().endswith(image_ext)
            and filename != output_filename
        ):
            portrait_path = filename
    return font_path, portrait_path


def wrap_text(text, font, max_width):
    """Wraps text to fit within a maximum width, respecting \n."""
    lines = []
    manual_lines = text.split("\n")
    for manual_line in manual_lines:
        words = manual_line.split(" ")
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
    return lines


def main():
    # --- 1. Load Text from File and Find Assets ---
    print("Loading assets...")
    try:
        with open("dialogue.txt", "r") as f:
            dialogue_text = f.read()
        print("Successfully loaded text from 'dialogue.txt'")
    except FileNotFoundError:
        print("\n--- ERROR ---")
        print("File 'dialogue.txt' not found. Please create it.")
        sys.exit()

    font_path, portrait_path = find_assets(OUTPUT_FILENAME)
    if not font_path:
        print("\n--- ERROR ---")
        print("No font file (.ttf or .otf) found in this directory.")
        sys.exit()
    print(f"Found font: '{font_path}'")

    pygame.init()
    font = pygame.font.Font(font_path, FONT_SIZE)
    portrait = None
    if portrait_path:
        print(f"Found portrait: '{portrait_path}'")
        portrait = pygame.image.load(portrait_path).convert_alpha()
    else:
        print("No portrait image found. Continuing without one.")

    # --- 2. Dynamic Resolution Calculation ---
    print("\nCalculating video dimensions...")
    lines = wrap_text(dialogue_text, font, MAX_TEXT_WIDTH)
    text_block_height = len(lines) * font.get_height()

    actual_text_width = 0
    for line in lines:
        actual_text_width = max(actual_text_width, font.size(line)[0])

    content_width = actual_text_width
    portrait_width = 0
    if portrait:
        portrait_width = portrait.get_width()
        content_width += portrait_width + PORTRAIT_PADDING

    screen_width = content_width + (PADDING * 2)
    screen_height = (
        max(text_block_height, portrait.get_height() if portrait else 0)
        + (PADDING * 2)
    )
    screen_width = screen_width if screen_width % 2 == 0 else screen_width + 1
    screen_height = screen_height if screen_height % 2 == 0 else screen_height + 1
    print(f"Calculated Resolution: {screen_width}x{screen_height}")

    # --- 3. Setup Screen and Video Writer ---
    screen = pygame.Surface((screen_width, screen_height))
    fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
    video_writer = cv2.VideoWriter(
        OUTPUT_FILENAME, fourcc, FPS, (screen_width, screen_height)
    )

    # --- 4. Layout and Rendering Loop ---
    text_area_x = PADDING
    if portrait:
        text_area_x += portrait_width + PORTRAIT_PADDING

    print("\nGenerating frames...")
    current_line_index, char_index, frame_counter, pause_frames = 0, 0, 0, 0
    animation_done = False
    total_frames_rendered = 0
    start_of_padding_frame = float("inf")

    while True:
        if not animation_done:
            if pause_frames > 0:
                pause_frames -= 1
            else:
                frame_counter += 1
                if frame_counter >= CHAR_SPEED:
                    frame_counter = 0
                    current_char = lines[current_line_index][char_index]
                    if current_char == ",":
                        pause_frames = PAUSE_COMMA
                    elif current_char in ".!?":
                        pause_frames = PAUSE_PUNCTUATION
                    char_index += 1
                    if char_index >= len(lines[current_line_index]):
                        char_index = 0
                        current_line_index += 1
                        if current_line_index >= len(lines):
                            animation_done = True
                            start_of_padding_frame = total_frames_rendered
                            print("Text animation complete. Adding final duration...")
        else:
            padding_frames = VIDEO_DURATION_SEC_AFTER_TEXT * FPS
            if total_frames_rendered >= start_of_padding_frame + padding_frames:
                break

        # --- Drawing ---
        screen.fill(BLACK)
        if portrait:
            screen.blit(portrait, (PADDING, PADDING))

        y_offset = 0
        for i in range(current_line_index):
            # Render with anti-aliasing FALSE for sharp, pixelated text
            text_surface = font.render(lines[i], False, WHITE)
            screen.blit(text_surface, (text_area_x, PADDING + y_offset))
            y_offset += font.get_height()

        if current_line_index < len(lines):
            displayed_line = lines[current_line_index][:char_index]
            # Render with anti-aliasing FALSE for sharp, pixelated text
            text_surface = font.render(displayed_line, False, WHITE)
            screen.blit(text_surface, (text_area_x, PADDING + y_offset))

        # --- Frame Conversion and Writing ---
        frame_data = pygame.surfarray.pixels3d(screen)
        frame_bgr = cv2.cvtColor(frame_data.swapaxes(0, 1), cv2.COLOR_RGB2BGR)
        video_writer.write(frame_bgr)
        del frame_data

        total_frames_rendered += 1
        if total_frames_rendered % FPS == 0:
            print(f"  ... {total_frames_rendered} frames rendered ...")

    # --- Cleanup ---
    print("Finalizing video...")
    video_writer.release()
    pygame.quit()
    print(f"\nSuccess! Video saved as '{OUTPUT_FILENAME}'")


if __name__ == "__main__":
    main()