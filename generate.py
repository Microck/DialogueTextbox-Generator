import pygame
import cv2
import numpy as np
import sys
import os
import argparse
import json
import webbrowser
import platform
import subprocess
from pathlib import Path

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DEFAULT_CONFIG = {
    "max_text_width": 1000,
    "padding": 10,
    "output_filename": "dialogue_from_txt.mp4",
    "font_size": 20,
    "video_duration_sec_after_text": 2,
    "char_speed": 1,
    "pause_comma": 4,
    "pause_punctuation": 10,
    "fps": 30,
    "text_color": [255, 255, 255],
    "bg_color": [0, 0, 0],
    "portrait_padding": 15,
    "auto_open": False,
    "sound_file": None,
    "export_gif": False,
    "gif_filename": "dialogue_from_txt.gif",
}

CONFIG_FILE = "config.json"
VIDEO_CODEC = "mp4v"


def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                config.update(user_config)
        except (json.JSONDecodeError, IOError):
            pass
    return config


def save_default_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    print(f"Default config saved to '{CONFIG_FILE}'")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate dialogue video with typing animation"
    )
    parser.add_argument("-i", "--input", default="dialogue.txt", help="Input text file")
    parser.add_argument("-o", "--output", help="Output video filename")
    parser.add_argument("-f", "--font", help="Font file path")
    parser.add_argument("-p", "--portrait", help="Portrait image path")
    parser.add_argument("--font-size", type=int, help="Font size in pixels")
    parser.add_argument("--max-width", type=int, help="Max text width before wrap")
    parser.add_argument("--padding", type=int, help="Padding around content")
    parser.add_argument("--fps", type=int, help="Frames per second")
    parser.add_argument("--char-speed", type=int, help="Frames per character")
    parser.add_argument("--dwell", type=float, help="Seconds after text completes")
    parser.add_argument("--auto-open", action="store_true", help="Open video when done")
    parser.add_argument("--sound", help="Sound file for typing effect")
    parser.add_argument("--gif", action="store_true", help="Also export as GIF")
    parser.add_argument("--gif-only", action="store_true", help="Export only GIF")
    parser.add_argument("--dry-run", action="store_true", help="Preview without rendering")
    parser.add_argument("--batch", help="Process multiple files (glob pattern)")
    parser.add_argument("--init-config", action="store_true", help="Create default config.json")
    parser.add_argument("--text-color", help="Text color as R,G,B (e.g., 255,255,255)")
    parser.add_argument("--bg-color", help="Background color as R,G,B (e.g., 0,0,0)")
    return parser.parse_args()


def find_assets(output_filename, font_override=None, portrait_override=None):
    font_path = font_override
    portrait_path = portrait_override
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


def find_portraits():
    image_ext = (".png", ".jpg", ".jpeg", ".bmp")
    portraits = []
    for filename in os.listdir("."):
        if filename.lower().endswith(image_ext):
            if "portrait" in filename.lower() or "char" in filename.lower():
                portraits.append(filename)
    if not portraits:
        for filename in os.listdir("."):
            if filename.lower().endswith(image_ext):
                portraits.append(filename)
                break
    return portraits


def wrap_text(text, font, max_width):
    lines = []
    manual_lines = text.split("\n")
    for manual_line in manual_lines:
        if not manual_line.strip():
            lines.append(" ")
            continue
        words = manual_line.split(" ")
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
    return lines if lines else [" "]


def open_file(filepath):
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":
        subprocess.run(["open", filepath])
    else:
        subprocess.run(["xdg-open", filepath])


def export_gif(frames, filename, fps):
    if not HAS_PIL:
        print("PIL not installed. Run: pip install Pillow")
        return False
    
    images = [Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)) for f in frames]
    duration = int(1000 / fps)
    images[0].save(
        filename,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0
    )
    print(f"GIF saved as '{filename}'")
    return True


def calculate_total_frames(lines, config):
    total_chars = sum(len(line) for line in lines)
    char_frames = total_chars * config["char_speed"]
    
    pause_frames = 0
    for line in lines:
        for char in line:
            if char == ",":
                pause_frames += config["pause_comma"]
            elif char in ".!?":
                pause_frames += config["pause_punctuation"]
    
    dwell_frames = int(config["video_duration_sec_after_text"] * config["fps"])
    return char_frames + pause_frames + dwell_frames


def generate_video(input_file, config, font_override=None, portrait_override=None, dry_run=False):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            dialogue_text = f.read()
        print(f"Loaded text from '{input_file}'")
    except FileNotFoundError:
        print(f"ERROR: File '{input_file}' not found.")
        return None

    output_filename = config["output_filename"]
    font_path, portrait_path = find_assets(output_filename, font_override, portrait_override)
    
    if not font_path:
        print("ERROR: No font file (.ttf or .otf) found.")
        return None
    print(f"Font: '{font_path}'")

    pygame.init()
    font = pygame.font.Font(font_path, config["font_size"])
    
    portrait = None
    if portrait_path:
        print(f"Portrait: '{portrait_path}'")
        portrait = pygame.image.load(portrait_path).convert_alpha()
    
    sound = None
    if config.get("sound_file") and os.path.exists(config["sound_file"]):
        pygame.mixer.init()
        sound = pygame.mixer.Sound(config["sound_file"])
        print(f"Sound: '{config['sound_file']}'")

    lines = wrap_text(dialogue_text, font, config["max_text_width"])
    text_block_height = len(lines) * font.get_height()

    actual_text_width = max(font.size(line)[0] for line in lines)
    content_width = actual_text_width
    portrait_width = 0
    
    if portrait:
        portrait_width = portrait.get_width()
        content_width += portrait_width + config["portrait_padding"]

    screen_width = content_width + (config["padding"] * 2)
    screen_height = (
        max(text_block_height, portrait.get_height() if portrait else 0)
        + (config["padding"] * 2)
    )
    screen_width = screen_width if screen_width % 2 == 0 else screen_width + 1
    screen_height = screen_height if screen_height % 2 == 0 else screen_height + 1
    
    total_frames = calculate_total_frames(lines, config)
    
    print(f"Resolution: {screen_width}x{screen_height}")
    print(f"Lines: {len(lines)}, Est. frames: {total_frames}")
    
    if dry_run:
        duration_sec = total_frames / config["fps"]
        print(f"Duration: ~{duration_sec:.1f}s")
        print("Dry run complete. No video generated.")
        pygame.quit()
        return None

    screen = pygame.Surface((screen_width, screen_height))
    bg_color = tuple(config["bg_color"])
    text_color = tuple(config["text_color"])
    
    video_writer = None
    gif_frames = []
    export_gif_flag = config.get("export_gif", False)
    gif_only = config.get("gif_only", False)
    
    if not gif_only:
        fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
        video_writer = cv2.VideoWriter(
            output_filename, fourcc, config["fps"], (screen_width, screen_height)
        )

    text_area_x = config["padding"]
    if portrait:
        text_area_x += portrait_width + config["portrait_padding"]

    current_line_index, char_index, frame_counter, pause_frames = 0, 0, 0, 0
    animation_done = False
    total_frames_rendered = 0
    start_of_padding_frame = float("inf")

    progress = None
    if HAS_TQDM:
        progress = tqdm(total=total_frames, desc="Rendering", unit="frame")

    while True:
        if not animation_done:
            if pause_frames > 0:
                pause_frames -= 1
            else:
                frame_counter += 1
                if frame_counter >= config["char_speed"]:
                    frame_counter = 0
                    line_text = lines[current_line_index]
                    if char_index < len(line_text):
                        current_char = line_text[char_index]
                        if sound:
                            sound.play()
                        if current_char == ",":
                            pause_frames = config["pause_comma"]
                        elif current_char in ".!?":
                            pause_frames = config["pause_punctuation"]
                    char_index += 1
                    if char_index >= len(line_text):
                        char_index = 0
                        current_line_index += 1
                        if current_line_index >= len(lines):
                            animation_done = True
                            start_of_padding_frame = total_frames_rendered
        else:
            padding_frames_total = config["video_duration_sec_after_text"] * config["fps"]
            if total_frames_rendered >= start_of_padding_frame + padding_frames_total:
                break

        screen.fill(bg_color)
        if portrait:
            screen.blit(portrait, (config["padding"], config["padding"]))

        y_offset = 0
        for i in range(current_line_index):
            text_surface = font.render(lines[i], False, text_color)
            screen.blit(text_surface, (text_area_x, config["padding"] + y_offset))
            y_offset += font.get_height()

        if current_line_index < len(lines):
            displayed_line = lines[current_line_index][:char_index]
            text_surface = font.render(displayed_line, False, text_color)
            screen.blit(text_surface, (text_area_x, config["padding"] + y_offset))

        frame_data = pygame.surfarray.pixels3d(screen)
        frame_bgr = cv2.cvtColor(frame_data.swapaxes(0, 1), cv2.COLOR_RGB2BGR)
        
        if video_writer:
            video_writer.write(frame_bgr)
        if export_gif_flag or gif_only:
            gif_frames.append(frame_bgr.copy())
        
        del frame_data
        total_frames_rendered += 1
        
        if progress:
            progress.update(1)
        elif total_frames_rendered % config["fps"] == 0:
            print(f"  ... {total_frames_rendered} frames ...")

    if progress:
        progress.close()

    if video_writer:
        video_writer.release()
        print(f"Video saved as '{output_filename}'")
    
    if (export_gif_flag or gif_only) and gif_frames:
        gif_name = config.get("gif_filename", output_filename.replace(".mp4", ".gif"))
        export_gif(gif_frames, gif_name, config["fps"])

    pygame.quit()
    
    if config.get("auto_open") and not gif_only:
        open_file(output_filename)
    
    return output_filename


def process_batch(pattern, config):
    from glob import glob
    files = glob(pattern)
    if not files:
        print(f"No files matching '{pattern}'")
        return
    
    print(f"Processing {len(files)} files...")
    for f in files:
        base = Path(f).stem
        cfg = config.copy()
        cfg["output_filename"] = f"{base}.mp4"
        cfg["gif_filename"] = f"{base}.gif"
        print(f"\n--- Processing: {f} ---")
        generate_video(f, cfg)


def main():
    args = parse_args()
    
    if args.init_config:
        save_default_config()
        return
    
    config = load_config()
    
    if args.output:
        config["output_filename"] = args.output
    if args.font_size:
        config["font_size"] = args.font_size
    if args.max_width:
        config["max_text_width"] = args.max_width
    if args.padding:
        config["padding"] = args.padding
    if args.fps:
        config["fps"] = args.fps
    if args.char_speed:
        config["char_speed"] = args.char_speed
    if args.dwell:
        config["video_duration_sec_after_text"] = args.dwell
    if args.auto_open:
        config["auto_open"] = True
    if args.sound:
        config["sound_file"] = args.sound
    if args.gif:
        config["export_gif"] = True
    if args.gif_only:
        config["gif_only"] = True
        config["export_gif"] = True
    if args.text_color:
        config["text_color"] = [int(x) for x in args.text_color.split(",")]
    if args.bg_color:
        config["bg_color"] = [int(x) for x in args.bg_color.split(",")]
    
    if args.batch:
        process_batch(args.batch, config)
        return
    
    generate_video(
        args.input,
        config,
        font_override=args.font,
        portrait_override=args.portrait,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
