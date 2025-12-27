import os
import re
import sys
import argparse
import json
import platform
import subprocess
import shutil
from pathlib import Path

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

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
    "box_size": [1000, 209],
    "padding": 20,
    "font_size": 35,
    "fps": 30,
    "dwell_time": 3,
    "text_color": [0, 0, 0, 255],
    "top_color": [255, 255, 255, 255],
    "bottom_color": [121, 121, 121, 255],
    "gradient_direction": "vertical",
    "background_image": None,
    "output_format": "webm",
    "auto_open": False,
}

CONFIG_FILE = "gradient_config.json"


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
        description="Generate dialogue video with gradient background"
    )
    parser.add_argument("-i", "--input", default="dialogue.txt", help="Input text file")
    parser.add_argument("-o", "--output", help="Output filename (without extension)")
    parser.add_argument("-f", "--font", help="Font file path")
    parser.add_argument("--font-size", type=int, help="Font size in pixels")
    parser.add_argument("--width", type=int, help="Box width")
    parser.add_argument("--height", type=int, help="Box height")
    parser.add_argument("--padding", type=int, help="Padding inside the box")
    parser.add_argument("--fps", type=int, help="Frames per second")
    parser.add_argument("--dwell", type=float, help="Seconds after text completes")
    parser.add_argument("--top-color", help="Top gradient color as R,G,B,A")
    parser.add_argument("--bottom-color", help="Bottom gradient color as R,G,B,A")
    parser.add_argument("--left-color", help="Left gradient color (horizontal mode)")
    parser.add_argument("--right-color", help="Right gradient color (horizontal mode)")
    parser.add_argument("--gradient", choices=["vertical", "horizontal", "none"], 
                        help="Gradient direction")
    parser.add_argument("--bg-image", help="Background image path")
    parser.add_argument("--text-color", help="Text color as R,G,B,A")
    parser.add_argument("--format", choices=["webm", "mp4", "gif"], help="Output format")
    parser.add_argument("--auto-open", action="store_true", help="Open when done")
    parser.add_argument("--dry-run", action="store_true", help="Preview without rendering")
    parser.add_argument("--batch", help="Process multiple files (glob pattern)")
    parser.add_argument("--init-config", action="store_true", help="Create default config")
    return parser.parse_args()


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def sanitize_filename(text):
    words = re.findall(r'\w+', text)[:5]
    name = "_".join(words).lower() if words else "dialogue"
    return re.sub(r'[^\w-]', '', name)


def load_font(font_override=None, font_size=35):
    if font_override and os.path.exists(font_override):
        return pygame.font.Font(font_override, font_size)
    for f in os.listdir("."):
        if f.lower().endswith((".ttf", ".otf")):
            return pygame.font.Font(f, font_size)
    print("ERROR: No .ttf/.otf font file found")
    sys.exit(1)


def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append(" ")
            continue
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
    return lines if lines else [" "]


def draw_gradient(surface, color1, color2, direction="vertical"):
    width, height = surface.get_size()
    
    if direction == "vertical":
        for y in range(height):
            t = y / (height - 1) if height > 1 else 0
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            a = int(color1[3] * (1 - t) + color2[3] * t)
            pygame.draw.line(surface, (r, g, b, a), (0, y), (width - 1, y))
    else:
        for x in range(width):
            t = x / (width - 1) if width > 1 else 0
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            a = int(color1[3] * (1 - t) + color2[3] * t)
            pygame.draw.line(surface, (r, g, b, a), (x, 0), (x, height - 1))


def draw_background(surface, config, bg_image=None):
    if bg_image:
        scaled = pygame.transform.scale(bg_image, surface.get_size())
        surface.blit(scaled, (0, 0))
    elif config["gradient_direction"] == "none":
        surface.fill(tuple(config["top_color"]))
    else:
        draw_gradient(
            surface,
            tuple(config["top_color"]),
            tuple(config["bottom_color"]),
            config["gradient_direction"]
        )


def open_file(filepath):
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":
        subprocess.run(["open", filepath])
    else:
        subprocess.run(["xdg-open", filepath])


def generate_frames(text_lines, font, temp_dir, config, bg_image=None):
    screen_width, screen_height = config["box_size"]
    screen = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    line_height = font.get_height()
    padding = config["padding"]
    max_lines = (screen_height - 2 * padding) // line_height
    text_lines = text_lines[:max_lines]
    text_color = tuple(config["text_color"][:3])
    
    current_line = 0
    current_char = 0
    frame_number = 0

    total_chars = sum(len(line) for line in text_lines)
    dwell_frames = int(config["dwell_time"] * config["fps"])
    total_frames = total_chars + dwell_frames
    
    progress = None
    if HAS_TQDM:
        progress = tqdm(total=total_frames, desc="Rendering", unit="frame")

    while current_line < len(text_lines):
        draw_background(screen, config, bg_image)
        y = padding
        
        for i in range(current_line):
            text_surf = font.render(text_lines[i], True, text_color)
            screen.blit(text_surf, (padding, y))
            y += line_height
        
        if current_line < len(text_lines):
            partial_text = text_lines[current_line][:current_char]
            text_surf = font.render(partial_text, True, text_color)
            screen.blit(text_surf, (padding, y))
            current_char += 1
            if current_char > len(text_lines[current_line]):
                current_line += 1
                current_char = 0
        
        pygame.image.save(screen, os.path.join(temp_dir, f"frame_{frame_number:04d}.png"))
        frame_number += 1
        if progress:
            progress.update(1)

    for _ in range(dwell_frames):
        draw_background(screen, config, bg_image)
        y = padding
        for line in text_lines:
            text_surf = font.render(line, True, text_color)
            screen.blit(text_surf, (padding, y))
            y += line_height
        pygame.image.save(screen, os.path.join(temp_dir, f"frame_{frame_number:04d}.png"))
        frame_number += 1
        if progress:
            progress.update(1)

    if progress:
        progress.close()

    return frame_number, (screen_width, screen_height)


def export_webm(base_name, temp_dir, size, fps):
    output_file = f"{base_name}_gradient.webm"
    width, height = size
    input_pattern = os.path.join(temp_dir, "frame_%04d.png")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", input_pattern,
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuv420p",
        "-b:v", "5M",
        "-vf", f"scale={width}:{height}",
        output_file
    ]
    print("Exporting WebM...")
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"WebM export failed: {e}")
        return None


def export_mp4_cv2(base_name, temp_dir, size, fps):
    if not HAS_CV2:
        print("OpenCV not installed. Run: pip install opencv-python")
        return None
    
    output_file = f"{base_name}_gradient.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, size)
    
    frame_files = sorted([f for f in os.listdir(temp_dir) if f.endswith(".png")])
    for frame_file in frame_files:
        frame = cv2.imread(os.path.join(temp_dir, frame_file))
        video_writer.write(frame)
    
    video_writer.release()
    print(f"MP4 saved as '{output_file}'")
    return output_file


def export_mp4_ffmpeg(base_name, temp_dir, size, fps):
    output_file = f"{base_name}_gradient.mp4"
    width, height = size
    input_pattern = os.path.join(temp_dir, "frame_%04d.png")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", input_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", f"scale={width}:{height}",
        output_file
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        return output_file
    except subprocess.CalledProcessError:
        return None


def export_gif(base_name, temp_dir, fps):
    if not HAS_PIL:
        print("PIL not installed. Run: pip install Pillow")
        return None
    
    output_file = f"{base_name}_gradient.gif"
    frame_files = sorted([f for f in os.listdir(temp_dir) if f.endswith(".png")])
    
    images = [Image.open(os.path.join(temp_dir, f)) for f in frame_files]
    duration = int(1000 / fps)
    images[0].save(
        output_file,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0
    )
    print(f"GIF saved as '{output_file}'")
    return output_file


def generate_video(input_file, config, font_override=None, dry_run=False, output_name=None):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            dialogue = f.read().strip()
    except FileNotFoundError:
        print(f"ERROR: '{input_file}' not found")
        return None

    pygame.init()
    font = load_font(font_override, config["font_size"])
    lines = wrap_text(dialogue, font, config["box_size"][0] - 2 * config["padding"])
    base_name = output_name or sanitize_filename(dialogue)

    bg_image = None
    if config.get("background_image") and os.path.exists(config["background_image"]):
        bg_image = pygame.image.load(config["background_image"]).convert_alpha()
        print(f"Background: '{config['background_image']}'")

    print(f"Output size: {config['box_size'][0]}x{config['box_size'][1]}")
    print(f"Lines: {len(lines)}")
    
    if dry_run:
        total_chars = sum(len(line) for line in lines)
        duration = (total_chars + config["dwell_time"] * config["fps"]) / config["fps"]
        print(f"Duration: ~{duration:.1f}s")
        print("Dry run complete.")
        pygame.quit()
        return None

    temp_dir = f"{base_name}_frames"
    os.makedirs(temp_dir, exist_ok=True)

    print("Generating frames...")
    total_frames, screen_size = generate_frames(lines, font, temp_dir, config, bg_image)
    print(f"Frames: {total_frames}")

    output_format = config.get("output_format", "webm")
    has_ffmpeg = check_ffmpeg()
    output_file = None

    if output_format == "webm":
        if has_ffmpeg:
            output_file = export_webm(base_name, temp_dir, screen_size, config["fps"])
        else:
            print("ffmpeg not found, falling back to MP4 via OpenCV")
            output_file = export_mp4_cv2(base_name, temp_dir, screen_size, config["fps"])
    elif output_format == "mp4":
        if has_ffmpeg:
            output_file = export_mp4_ffmpeg(base_name, temp_dir, screen_size, config["fps"])
        if not output_file:
            output_file = export_mp4_cv2(base_name, temp_dir, screen_size, config["fps"])
    elif output_format == "gif":
        output_file = export_gif(base_name, temp_dir, config["fps"])

    shutil.rmtree(temp_dir)
    pygame.quit()

    if output_file:
        print(f"SUCCESS: {output_file}")
        if config.get("auto_open"):
            open_file(output_file)

    return output_file


def process_batch(pattern, config, font_override=None):
    from glob import glob
    files = glob(pattern)
    if not files:
        print(f"No files matching '{pattern}'")
        return
    
    print(f"Processing {len(files)} files...")
    for f in files:
        base = Path(f).stem
        print(f"\n--- {f} ---")
        generate_video(f, config, font_override, output_name=base)


def main():
    args = parse_args()
    
    if args.init_config:
        save_default_config()
        return
    
    config = load_config()
    
    if args.width:
        config["box_size"][0] = args.width
    if args.height:
        config["box_size"][1] = args.height
    if args.font_size:
        config["font_size"] = args.font_size
    if args.padding:
        config["padding"] = args.padding
    if args.fps:
        config["fps"] = args.fps
    if args.dwell:
        config["dwell_time"] = args.dwell
    if args.top_color:
        config["top_color"] = [int(x) for x in args.top_color.split(",")]
    if args.bottom_color:
        config["bottom_color"] = [int(x) for x in args.bottom_color.split(",")]
    if args.left_color:
        config["top_color"] = [int(x) for x in args.left_color.split(",")]
        config["gradient_direction"] = "horizontal"
    if args.right_color:
        config["bottom_color"] = [int(x) for x in args.right_color.split(",")]
        config["gradient_direction"] = "horizontal"
    if args.gradient:
        config["gradient_direction"] = args.gradient
    if args.bg_image:
        config["background_image"] = args.bg_image
    if args.text_color:
        config["text_color"] = [int(x) for x in args.text_color.split(",")]
    if args.format:
        config["output_format"] = args.format
    if args.auto_open:
        config["auto_open"] = True
    
    if args.batch:
        process_batch(args.batch, config, args.font)
        return
    
    generate_video(
        args.input,
        config,
        font_override=args.font,
        dry_run=args.dry_run,
        output_name=args.output
    )


if __name__ == "__main__":
    main()
