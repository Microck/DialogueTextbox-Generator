#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.table import Table
    from rich.text import Text
    from rich.rule import Rule
    from rich import box
except ImportError:
    print("Rich not installed. Run: pip install rich")
    sys.exit(1)

THEME = {
    "accent": "#c678dd",
    "accent2": "#e06c75",
    "success": "#98c379",
    "warning": "#e5c07b",
    "info": "#61afef",
    "dim": "#5c6370",
    "text": "#abb2bf",
}

console = Console()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_header():
    title = Text()
    title.append("DIALOGUE ", style=f"bold {THEME['accent']}")
    title.append("GENERATOR", style=f"bold {THEME['accent2']}")
    console.print(Panel(title, border_style=THEME['accent'], box=box.DOUBLE, padding=(0, 2)))
    console.print()


def find_files(extensions):
    files = []
    for ext in extensions:
        files.extend(Path.cwd().glob(f"*{ext}"))
    return sorted([f.name for f in files])


def select_file(files, prompt_text, allow_none=False):
    if not files:
        console.print(f"  [{THEME['warning']}]No files found[/{THEME['warning']}]")
        return None
    
    for i, f in enumerate(files, 1):
        console.print(f"  [{THEME['dim']}]{i}.[/{THEME['dim']}] {f}")
    
    if allow_none:
        console.print(f"  [{THEME['dim']}]0. None[/{THEME['dim']}]")
    
    while True:
        choice = Prompt.ask(f"  [{THEME['accent']}]{prompt_text}[/{THEME['accent']}]", default="1")
        try:
            idx = int(choice)
            if allow_none and idx == 0:
                return None
            if 1 <= idx <= len(files):
                return files[idx - 1]
        except ValueError:
            if choice in files:
                return choice
        console.print(f"  [{THEME['accent2']}]Invalid[/{THEME['accent2']}]")


def get_color(prompt_text, default):
    default_str = ",".join(map(str, default))
    while True:
        value = Prompt.ask(f"  [{THEME['accent']}]{prompt_text}[/{THEME['accent']}] [{THEME['dim']}](R,G,B)[/{THEME['dim']}]", default=default_str)
        try:
            parts = [int(x.strip()) for x in value.split(",")]
            if len(parts) >= 3:
                r, g, b = parts[:3]
                console.print(f"  [on rgb({r},{g},{b})]     [/]")
                return parts[:3]
        except ValueError:
            pass
        console.print(f"  [{THEME['accent2']}]Enter as R,G,B[/{THEME['accent2']}]")


def get_dialogue():
    console.print(f"\n  [{THEME['info']}]Enter dialogue (empty line to finish):[/{THEME['info']}]")
    lines = []
    while True:
        line = Prompt.ask(f"  [{THEME['dim']}]>[/{THEME['dim']}]", default="")
        if not line and lines:
            break
        if line:
            lines.append(line)
    return "\n".join(lines)


def main_menu():
    options = [
        ("1", "Generate Video"),
        ("2", "Batch Process"),
        ("q", "Quit"),
    ]
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style=f"bold {THEME['accent']}", width=4)
    table.add_column("Option", style=THEME['text'])
    for key, label in options:
        table.add_row(f"[{key}]", label)
    
    console.print(Panel(table, title=f"[bold {THEME['accent']}]Menu[/]", border_style=THEME['dim'], box=box.ROUNDED))
    return Prompt.ask(f"  [{THEME['accent']}]Select[/{THEME['accent']}]", choices=["1", "2", "q"], default="1")


def configure_video():
    console.print(Rule("Generate Video", style=THEME['accent']))
    
    config = {}
    
    console.print(f"\n  [{THEME['info']}]Dialogue[/{THEME['info']}]")
    config["dialogue"] = get_dialogue()
    
    if not config["dialogue"]:
        console.print(f"  [{THEME['warning']}]No dialogue entered[/{THEME['warning']}]")
        return None
    
    console.print(f"\n  [{THEME['info']}]Background Type[/{THEME['info']}]")
    console.print(f"  [{THEME['dim']}]1.[/{THEME['dim']}] Solid")
    console.print(f"  [{THEME['dim']}]2.[/{THEME['dim']}] Gradient")
    console.print(f"  [{THEME['dim']}]3.[/{THEME['dim']}] Image")
    bg_choice = Prompt.ask(f"  [{THEME['accent']}]Select[/{THEME['accent']}]", choices=["1", "2", "3"], default="1")
    config["bg_type"] = {"1": "solid", "2": "gradient", "3": "image"}[bg_choice]
    
    console.print(f"\n  [{THEME['info']}]Font[/{THEME['info']}]")
    font_files = find_files((".ttf", ".otf"))
    config["font"] = select_file(font_files, "Font file", allow_none=True)
    
    console.print(f"\n  [{THEME['info']}]Size[/{THEME['info']}]")
    config["width"] = IntPrompt.ask(f"  [{THEME['accent']}]Width[/{THEME['accent']}]", default=800)
    config["height"] = IntPrompt.ask(f"  [{THEME['accent']}]Height[/{THEME['accent']}]", default=200)
    config["font_size"] = IntPrompt.ask(f"  [{THEME['accent']}]Font size[/{THEME['accent']}]", default=28)
    config["padding"] = IntPrompt.ask(f"  [{THEME['accent']}]Padding[/{THEME['accent']}]", default=20)
    config["speed"] = IntPrompt.ask(f"  [{THEME['accent']}]Speed (frames/char)[/{THEME['accent']}]", default=2)
    
    console.print(f"\n  [{THEME['info']}]Colors[/{THEME['info']}]")
    config["text_color"] = get_color("Text color", [255, 255, 255])
    
    if config["bg_type"] == "solid":
        config["bg_color"] = get_color("Background color", [0, 0, 0])
    elif config["bg_type"] == "gradient":
        config["grad_dir"] = Prompt.ask(f"  [{THEME['accent']}]Direction[/{THEME['accent']}]", choices=["vertical", "horizontal"], default="vertical")
        config["grad_top"] = get_color("Top/Left color", [255, 255, 255])
        config["grad_bottom"] = get_color("Bottom/Right color", [120, 120, 120])
    else:
        console.print(f"\n  [{THEME['info']}]Background Image[/{THEME['info']}]")
        image_files = find_files((".png", ".jpg", ".jpeg", ".bmp"))
        config["bg_image"] = select_file(image_files, "Image file", allow_none=True)
    
    console.print(f"\n  [{THEME['info']}]Output[/{THEME['info']}]")
    config["output"] = Prompt.ask(f"  [{THEME['accent']}]Filename[/{THEME['accent']}]", default="output.mp4")
    config["format"] = Prompt.ask(f"  [{THEME['accent']}]Format[/{THEME['accent']}]", choices=["mp4", "webm", "gif"], default="mp4")
    config["auto_open"] = Confirm.ask(f"  [{THEME['accent']}]Open when done?[/{THEME['accent']}]", default=True)
    
    return config


def build_command(config):
    temp_file = "_temp_dialogue.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(config["dialogue"])
    
    if config["bg_type"] == "solid":
        cmd = [sys.executable, "generate.py"]
        cmd.extend(["-i", temp_file])
        cmd.extend(["-o", config["output"]])
        if config.get("font"):
            cmd.extend(["-f", config["font"]])
        cmd.extend(["--font-size", str(config["font_size"])])
        cmd.extend(["--max-width", str(config["width"])])
        cmd.extend(["--padding", str(config["padding"])])
        cmd.extend(["--char-speed", str(config["speed"])])
        cmd.extend(["--text-color", ",".join(map(str, config["text_color"]))])
        cmd.extend(["--bg-color", ",".join(map(str, config["bg_color"]))])
        if config["auto_open"]:
            cmd.append("--auto-open")
        if config["format"] == "gif":
            cmd.append("--gif-only")
    else:
        cmd = [sys.executable, "gradient.py"]
        cmd.extend(["-i", temp_file])
        base = Path(config["output"]).stem
        cmd.extend(["-o", base])
        if config.get("font"):
            cmd.extend(["-f", config["font"]])
        cmd.extend(["--font-size", str(config["font_size"])])
        cmd.extend(["--width", str(config["width"])])
        cmd.extend(["--height", str(config["height"])])
        cmd.extend(["--padding", str(config["padding"])])
        cmd.extend(["--text-color", ",".join(map(str, config["text_color"])) + ",255"])
        cmd.extend(["--format", config["format"]])
        
        if config["bg_type"] == "gradient":
            cmd.extend(["--gradient", config["grad_dir"]])
            cmd.extend(["--top-color", ",".join(map(str, config["grad_top"])) + ",255"])
            cmd.extend(["--bottom-color", ",".join(map(str, config["grad_bottom"])) + ",255"])
        else:
            if config.get("bg_image"):
                cmd.extend(["--bg-image", config["bg_image"]])
        
        if config["auto_open"]:
            cmd.append("--auto-open")
    
    return cmd, temp_file


def run_command(cmd, temp_file=None):
    console.print(f"\n  [{THEME['dim']}]{' '.join(cmd)}[/{THEME['dim']}]")
    console.print()
    try:
        result = subprocess.run(cmd)
        if result.returncode == 0:
            console.print(f"\n  [{THEME['success']}]Done![/{THEME['success']}]")
        else:
            console.print(f"\n  [{THEME['accent2']}]Failed[/{THEME['accent2']}]")
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


def batch_process():
    console.print(Rule("Batch Process", style=THEME['accent']))
    
    console.print(f"\n  [{THEME['dim']}]Example: *.txt[/{THEME['dim']}]")
    pattern = Prompt.ask(f"  [{THEME['accent']}]File pattern[/{THEME['accent']}]", default="*.txt")
    
    generator = Prompt.ask(f"  [{THEME['accent']}]Generator[/{THEME['accent']}]", choices=["generate", "gradient"], default="generate")
    
    cmd = [sys.executable, f"{generator}.py", "--batch", pattern]
    run_command(cmd)


def main():
    while True:
        clear_screen()
        show_header()
        
        choice = main_menu()
        
        if choice == "q":
            console.print(f"\n  [{THEME['accent']}]Goodbye![/{THEME['accent']}]\n")
            break
        elif choice == "1":
            config = configure_video()
            if config:
                if Confirm.ask(f"\n  [{THEME['accent']}]Generate?[/{THEME['accent']}]", default=True):
                    cmd, temp_file = build_command(config)
                    run_command(cmd, temp_file)
            Prompt.ask(f"\n  [{THEME['dim']}]Press Enter[/{THEME['dim']}]", default="")
        elif choice == "2":
            batch_process()
            Prompt.ask(f"\n  [{THEME['dim']}]Press Enter[/{THEME['dim']}]", default="")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(f"\n  [{THEME['accent']}]Interrupted[/{THEME['accent']}]\n")
        sys.exit(0)
