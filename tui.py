#!/usr/bin/env python3
"""
Dialogue Generator TUI - Terminal User Interface using Rich
Run: python tui.py
Requires: pip install rich
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    from rich.align import Align
    from rich.rule import Rule
    from rich import box
    from rich.style import Style
    from rich.padding import Padding
except ImportError:
    print("Rich not installed. Run: pip install rich")
    sys.exit(1)

# Theme colors
THEME = {
    "accent": "#c678dd",
    "accent2": "#e06c75",
    "success": "#98c379",
    "warning": "#e5c07b",
    "info": "#61afef",
    "dim": "#5c6370",
    "text": "#abb2bf",
    "bg": "#282c34",
}

console = Console()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_header():
    """Display app header."""
    title = Text()
    title.append("DIALOGUE ", style=f"bold {THEME['accent']}")
    title.append("TEXTBOX ", style=f"bold {THEME['accent2']}")
    title.append("GENERATOR", style=f"bold {THEME['accent']}")
    
    subtitle = Text("Pixel-perfect typing animations", style=THEME['dim'])
    
    header = Panel(
        Align.center(Group(title, subtitle)),
        border_style=THEME['accent'],
        box=box.DOUBLE,
        padding=(0, 2),
    )
    console.print(header)
    console.print()


def show_status_bar():
    """Show current directory status."""
    cwd = Path.cwd()
    txt_count = len(list(cwd.glob("*.txt")))
    font_count = len(list(cwd.glob("*.ttf"))) + len(list(cwd.glob("*.otf")))
    
    status = Text()
    status.append(f" {cwd.name} ", style=f"bold {THEME['info']}")
    status.append(" | ", style=THEME['dim'])
    status.append(f"{txt_count} txt ", style=THEME['success'] if txt_count else THEME['warning'])
    status.append(f"{font_count} fonts", style=THEME['success'] if font_count else THEME['warning'])
    
    console.print(Panel(status, border_style=THEME['dim'], box=box.ROUNDED, padding=(0, 1)))
    console.print()


def find_files(extensions):
    """Find files with given extensions in current directory."""
    files = []
    for ext in extensions:
        files.extend(Path.cwd().glob(f"*{ext}"))
    return sorted([f.name for f in files])


def create_file_table(files, title, show_size=True):
    """Create a table showing files."""
    table = Table(
        title=title,
        box=box.ROUNDED,
        border_style=THEME['dim'],
        title_style=f"bold {THEME['accent']}",
        header_style=f"bold {THEME['info']}",
        show_edge=True,
        padding=(0, 1),
    )
    
    table.add_column("#", style=THEME['dim'], width=3, justify="right")
    table.add_column("File", style=THEME['text'])
    if show_size:
        table.add_column("Size", style=THEME['dim'], justify="right")
    
    for i, f in enumerate(files, 1):
        size = ""
        if show_size:
            try:
                sz = Path(f).stat().st_size
                size = f"{sz:,}B" if sz < 1024 else f"{sz/1024:.1f}K"
            except:
                size = "?"
        
        row = [str(i), f]
        if show_size:
            row.append(size)
        table.add_row(*row)
    
    return table


def select_file_interactive(files, prompt_text, allow_none=False, show_table=True):
    """Interactive file selection with table display."""
    if not files:
        console.print(f"  [{THEME['warning']}]No files found[/{THEME['warning']}]")
        return None
    
    if show_table:
        table = create_file_table(files, "", show_size=True)
        console.print(table)
    
    if allow_none:
        console.print(f"  [{THEME['dim']}]0. Skip / None[/{THEME['dim']}]")
    
    while True:
        choice = Prompt.ask(f"  [{THEME['accent']}]{prompt_text}[/{THEME['accent']}]", default="1")
        try:
            idx = int(choice)
            if allow_none and idx == 0:
                return None
            if 1 <= idx <= len(files):
                selected = files[idx - 1]
                console.print(f"  [{THEME['success']}]Selected: {selected}[/{THEME['success']}]")
                return selected
        except ValueError:
            if choice in files:
                console.print(f"  [{THEME['success']}]Selected: {choice}[/{THEME['success']}]")
                return choice
        console.print(f"  [{THEME['accent2']}]Invalid choice. Enter 1-{len(files)}{' or 0' if allow_none else ''}[/{THEME['accent2']}]")


def get_color_input(prompt_text, default, with_alpha=False):
    """Get RGBA color input."""
    default_str = ",".join(map(str, default))
    hint = "R,G,B,A" if with_alpha else "R,G,B"
    
    while True:
        value = Prompt.ask(
            f"  [{THEME['accent']}]{prompt_text}[/{THEME['accent']}] [{THEME['dim']}]({hint})[/{THEME['dim']}]",
            default=default_str
        )
        try:
            parts = [int(x.strip()) for x in value.split(",")]
            if len(parts) >= 3:
                if with_alpha:
                    color = parts[:4] if len(parts) >= 4 else parts[:3] + [255]
                else:
                    color = parts[:3]
                r, g, b = color[:3]
                console.print(f"  [on rgb({r},{g},{b})]     [/] [{THEME['dim']}]Preview[/{THEME['dim']}]")
                return color
        except ValueError:
            pass
        console.print(f"  [{THEME['accent2']}]Enter as {hint}[/{THEME['accent2']}]")


def create_menu(title, options, show_keys=True):
    """Create a styled menu panel."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style=f"bold {THEME['accent']}", width=4)
    table.add_column("Option", style=THEME['text'])
    
    for key, label in options:
        if key == "-":
            table.add_row("", "")
        else:
            table.add_row(f"[{key}]" if show_keys else key, label)
    
    return Panel(
        table,
        title=f"[bold {THEME['accent']}]{title}[/]",
        border_style=THEME['dim'],
        box=box.ROUNDED,
        padding=(1, 2),
    )


def main_menu():
    """Display main menu and get choice."""
    options = [
        ("1", "Generate Pixel-Perfect Video"),
        ("2", "Generate Gradient Video"),
        ("-", ""),
        ("3", "Batch Process Multiple Files"),
        ("4", "Preview Settings (Dry Run)"),
        ("-", ""),
        ("5", "Create Default Config Files"),
        ("6", "View Current Directory"),
        ("-", ""),
        ("q", "Quit"),
    ]
    
    menu = create_menu("Main Menu", options)
    console.print(menu)
    
    return Prompt.ask(
        f"  [{THEME['accent']}]Select[/{THEME['accent']}]",
        choices=["1", "2", "3", "4", "5", "6", "q"],
        default="1"
    )


def section_header(text):
    """Print a section header."""
    console.print()
    console.print(Rule(text, style=THEME['accent']))
    console.print()


def configure_generate():
    """Configure pixel-perfect generator settings."""
    section_header("Pixel-Perfect Generator")
    
    config = {}
    
    console.print(f"  [{THEME['info']}]Step 1: Select Input File[/{THEME['info']}]")
    txt_files = find_files((".txt",))
    config["input"] = select_file_interactive(txt_files, "Text file") or "dialogue.txt"
    
    console.print()
    console.print(f"  [{THEME['info']}]Step 2: Select Font[/{THEME['info']}]")
    font_files = find_files((".ttf", ".otf"))
    config["font"] = select_file_interactive(font_files, "Font file", allow_none=True)
    
    console.print()
    console.print(f"  [{THEME['info']}]Step 3: Portrait Image (Optional)[/{THEME['info']}]")
    image_files = find_files((".png", ".jpg", ".jpeg", ".bmp"))
    config["portrait"] = select_file_interactive(image_files, "Portrait", allow_none=True)
    
    section_header("Video Settings")
    
    settings_panel = Panel(
        Text.from_markup(
            f"  Font Size: pixels for text rendering\n"
            f"  Max Width: wrap text at this width\n"
            f"  Padding: space around content\n"
            f"  FPS: frames per second\n"
            f"  Dwell: pause after text completes"
        ),
        title=f"[{THEME['dim']}]Setting Guide[/{THEME['dim']}]",
        border_style=THEME['dim'],
        box=box.ROUNDED,
    )
    console.print(settings_panel)
    console.print()
    
    config["font_size"] = IntPrompt.ask(f"  [{THEME['accent']}]Font size[/{THEME['accent']}]", default=20)
    config["max_width"] = IntPrompt.ask(f"  [{THEME['accent']}]Max width[/{THEME['accent']}]", default=1000)
    config["padding"] = IntPrompt.ask(f"  [{THEME['accent']}]Padding[/{THEME['accent']}]", default=10)
    config["fps"] = IntPrompt.ask(f"  [{THEME['accent']}]FPS[/{THEME['accent']}]", default=30)
    config["dwell"] = IntPrompt.ask(f"  [{THEME['accent']}]Dwell seconds[/{THEME['accent']}]", default=2)
    
    section_header("Colors")
    config["text_color"] = get_color_input("Text color", [255, 255, 255])
    config["bg_color"] = get_color_input("Background color", [0, 0, 0])
    
    section_header("Export Options")
    config["output"] = Prompt.ask(f"  [{THEME['accent']}]Output filename[/{THEME['accent']}]", default="dialogue.mp4")
    config["gif"] = Confirm.ask(f"  [{THEME['accent']}]Also export GIF?[/{THEME['accent']}]", default=False)
    config["auto_open"] = Confirm.ask(f"  [{THEME['accent']}]Open when done?[/{THEME['accent']}]", default=True)
    
    sound_files = find_files((".wav", ".ogg", ".mp3"))
    if sound_files:
        console.print()
        console.print(f"  [{THEME['info']}]Typing Sound (Optional)[/{THEME['info']}]")
        config["sound"] = select_file_interactive(sound_files, "Sound file", allow_none=True)
    
    return config


def configure_gradient():
    """Configure gradient generator settings."""
    section_header("Gradient Generator")
    
    config = {}
    
    console.print(f"  [{THEME['info']}]Step 1: Select Input File[/{THEME['info']}]")
    txt_files = find_files((".txt",))
    config["input"] = select_file_interactive(txt_files, "Text file") or "dialogue.txt"
    
    console.print()
    console.print(f"  [{THEME['info']}]Step 2: Select Font[/{THEME['info']}]")
    font_files = find_files((".ttf", ".otf"))
    config["font"] = select_file_interactive(font_files, "Font file", allow_none=True)
    
    section_header("Box Dimensions")
    config["width"] = IntPrompt.ask(f"  [{THEME['accent']}]Box width[/{THEME['accent']}]", default=1000)
    config["height"] = IntPrompt.ask(f"  [{THEME['accent']}]Box height[/{THEME['accent']}]", default=209)
    config["padding"] = IntPrompt.ask(f"  [{THEME['accent']}]Padding[/{THEME['accent']}]", default=20)
    config["font_size"] = IntPrompt.ask(f"  [{THEME['accent']}]Font size[/{THEME['accent']}]", default=35)
    config["fps"] = IntPrompt.ask(f"  [{THEME['accent']}]FPS[/{THEME['accent']}]", default=30)
    config["dwell"] = IntPrompt.ask(f"  [{THEME['accent']}]Dwell seconds[/{THEME['accent']}]", default=3)
    
    section_header("Gradient Settings")
    
    gradient_options = Panel(
        Text.from_markup(
            f"  [{THEME['info']}]vertical[/{THEME['info']}]   - Top to bottom gradient\n"
            f"  [{THEME['info']}]horizontal[/{THEME['info']}] - Left to right gradient\n"
            f"  [{THEME['info']}]none[/{THEME['info']}]       - Solid color background"
        ),
        border_style=THEME['dim'],
        box=box.ROUNDED,
    )
    console.print(gradient_options)
    
    config["gradient"] = Prompt.ask(
        f"  [{THEME['accent']}]Gradient direction[/{THEME['accent']}]",
        choices=["vertical", "horizontal", "none"],
        default="vertical"
    )
    
    if config["gradient"] == "vertical":
        console.print()
        config["top_color"] = get_color_input("Top color", [255, 255, 255, 255], with_alpha=True)
        config["bottom_color"] = get_color_input("Bottom color", [121, 121, 121, 255], with_alpha=True)
    elif config["gradient"] == "horizontal":
        console.print()
        config["left_color"] = get_color_input("Left color", [255, 255, 255, 255], with_alpha=True)
        config["right_color"] = get_color_input("Right color", [121, 121, 121, 255], with_alpha=True)
    
    console.print()
    config["text_color"] = get_color_input("Text color", [0, 0, 0, 255], with_alpha=True)
    
    console.print()
    console.print(f"  [{THEME['info']}]Background Image (Optional - overrides gradient)[/{THEME['info']}]")
    image_files = find_files((".png", ".jpg", ".jpeg", ".bmp"))
    if image_files:
        config["bg_image"] = select_file_interactive(image_files, "Background", allow_none=True)
    
    section_header("Export Options")
    
    format_panel = Panel(
        Text.from_markup(
            f"  [{THEME['info']}]webm[/{THEME['info']}] - Best quality, transparency support\n"
            f"  [{THEME['info']}]mp4[/{THEME['info']}]  - Universal compatibility\n"
            f"  [{THEME['info']}]gif[/{THEME['info']}]  - Animated image, larger size"
        ),
        border_style=THEME['dim'],
        box=box.ROUNDED,
    )
    console.print(format_panel)
    
    config["format"] = Prompt.ask(
        f"  [{THEME['accent']}]Output format[/{THEME['accent']}]",
        choices=["webm", "mp4", "gif"],
        default="webm"
    )
    config["output"] = Prompt.ask(f"  [{THEME['accent']}]Output name (no extension)[/{THEME['accent']}]", default="")
    config["auto_open"] = Confirm.ask(f"  [{THEME['accent']}]Open when done?[/{THEME['accent']}]", default=True)
    
    return config


def show_config_summary(config, title):
    """Display configuration summary."""
    section_header(f"{title} - Summary")
    
    table = Table(box=box.ROUNDED, border_style=THEME['dim'], show_header=False)
    table.add_column("Setting", style=f"bold {THEME['info']}")
    table.add_column("Value", style=THEME['text'])
    
    for key, value in config.items():
        display_value = str(value)
        if isinstance(value, list):
            display_value = ",".join(map(str, value))
        elif value is None:
            display_value = f"[{THEME['dim']}]None[/{THEME['dim']}]"
        elif value is True:
            display_value = f"[{THEME['success']}]Yes[/{THEME['success']}]"
        elif value is False:
            display_value = f"[{THEME['dim']}]No[/{THEME['dim']}]"
        
        table.add_row(key.replace("_", " ").title(), display_value)
    
    console.print(table)
    console.print()


def build_generate_command(config):
    """Build CLI command for generate.py."""
    cmd = [sys.executable, "generate.py"]
    cmd.extend(["-i", config["input"]])
    if config.get("font"):
        cmd.extend(["-f", config["font"]])
    if config.get("portrait"):
        cmd.extend(["-p", config["portrait"]])
    cmd.extend(["--font-size", str(config["font_size"])])
    cmd.extend(["--max-width", str(config["max_width"])])
    cmd.extend(["--padding", str(config["padding"])])
    cmd.extend(["--fps", str(config["fps"])])
    cmd.extend(["--dwell", str(config["dwell"])])
    cmd.extend(["--text-color", ",".join(map(str, config["text_color"][:3]))])
    cmd.extend(["--bg-color", ",".join(map(str, config["bg_color"][:3]))])
    cmd.extend(["-o", config["output"]])
    if config.get("gif"):
        cmd.append("--gif")
    if config.get("auto_open"):
        cmd.append("--auto-open")
    if config.get("sound"):
        cmd.extend(["--sound", config["sound"]])
    return cmd


def build_gradient_command(config):
    """Build CLI command for gradient.py."""
    cmd = [sys.executable, "gradient.py"]
    cmd.extend(["-i", config["input"]])
    if config.get("font"):
        cmd.extend(["-f", config["font"]])
    cmd.extend(["--width", str(config["width"])])
    cmd.extend(["--height", str(config["height"])])
    cmd.extend(["--padding", str(config["padding"])])
    cmd.extend(["--font-size", str(config["font_size"])])
    cmd.extend(["--fps", str(config["fps"])])
    cmd.extend(["--dwell", str(config["dwell"])])
    cmd.extend(["--gradient", config["gradient"]])
    
    if config.get("top_color"):
        cmd.extend(["--top-color", ",".join(map(str, config["top_color"]))])
    if config.get("bottom_color"):
        cmd.extend(["--bottom-color", ",".join(map(str, config["bottom_color"]))])
    if config.get("left_color"):
        cmd.extend(["--left-color", ",".join(map(str, config["left_color"]))])
    if config.get("right_color"):
        cmd.extend(["--right-color", ",".join(map(str, config["right_color"]))])
    
    cmd.extend(["--text-color", ",".join(map(str, config["text_color"]))])
    
    if config.get("bg_image"):
        cmd.extend(["--bg-image", config["bg_image"]])
    
    cmd.extend(["--format", config["format"]])
    if config.get("output"):
        cmd.extend(["-o", config["output"]])
    if config.get("auto_open"):
        cmd.append("--auto-open")
    
    return cmd


def run_command(cmd, show_cmd=True):
    """Execute a command and return success status."""
    if show_cmd:
        cmd_str = " ".join(cmd)
        console.print()
        console.print(Panel(
            f"[{THEME['dim']}]{cmd_str}[/{THEME['dim']}]",
            title=f"[{THEME['info']}]Running[/{THEME['info']}]",
            border_style=THEME['info'],
            box=box.ROUNDED,
        ))
        console.print()
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        console.print(f"\n  [{THEME['success']}]Done![/{THEME['success']}]")
        return True
    else:
        console.print(f"\n  [{THEME['accent2']}]Command failed (exit code {result.returncode})[/{THEME['accent2']}]")
        return False


def batch_process():
    """Batch process multiple files."""
    section_header("Batch Processing")
    
    options = Panel(
        Text.from_markup(
            f"  [{THEME['info']}]generate[/{THEME['info']}] - Pixel-perfect generator\n"
            f"  [{THEME['info']}]gradient[/{THEME['info']}] - Gradient background generator"
        ),
        border_style=THEME['dim'],
        box=box.ROUNDED,
    )
    console.print(options)
    
    generator = Prompt.ask(
        f"  [{THEME['accent']}]Which generator?[/{THEME['accent']}]",
        choices=["generate", "gradient"],
        default="generate"
    )
    
    console.print()
    console.print(f"  [{THEME['dim']}]Examples: *.txt, dialogues/*.txt, chapter_*.txt[/{THEME['dim']}]")
    pattern = Prompt.ask(f"  [{THEME['accent']}]File pattern[/{THEME['accent']}]", default="*.txt")
    
    cmd = [sys.executable, f"{generator}.py", "--batch", pattern]
    run_command(cmd)


def dry_run():
    """Preview configuration without generating."""
    section_header("Dry Run Preview")
    
    generator = Prompt.ask(
        f"  [{THEME['accent']}]Which generator?[/{THEME['accent']}]",
        choices=["generate", "gradient"],
        default="generate"
    )
    
    console.print()
    txt_files = find_files((".txt",))
    input_file = select_file_interactive(txt_files, "Text file") or "dialogue.txt"
    
    cmd = [sys.executable, f"{generator}.py", "-i", input_file, "--dry-run"]
    run_command(cmd)


def create_configs():
    """Create default configuration files."""
    section_header("Creating Config Files")
    
    console.print(f"  [{THEME['info']}]Creating config.json...[/{THEME['info']}]")
    subprocess.run([sys.executable, "generate.py", "--init-config"], capture_output=True)
    console.print(f"  [{THEME['success']}]Created config.json[/{THEME['success']}]")
    
    console.print(f"  [{THEME['info']}]Creating gradient_config.json...[/{THEME['info']}]")
    subprocess.run([sys.executable, "gradient.py", "--init-config"], capture_output=True)
    console.print(f"  [{THEME['success']}]Created gradient_config.json[/{THEME['success']}]")
    
    console.print()
    console.print(f"  [{THEME['success']}]Config files ready![/{THEME['success']}]")


def view_directory():
    """View files in current directory."""
    section_header("Current Directory")
    
    categories = [
        ("Text Files", (".txt",)),
        ("Font Files", (".ttf", ".otf")),
        ("Images", (".png", ".jpg", ".jpeg", ".bmp")),
        ("Config", (".json",)),
        ("Output", (".mp4", ".webm", ".gif")),
    ]
    
    for title, exts in categories:
        files = find_files(exts)
        if files:
            table = create_file_table(files, title)
            console.print(table)
            console.print()
        else:
            console.print(f"  [{THEME['dim']}]{title}: None found[/{THEME['dim']}]")
            console.print()


def wait_for_enter():
    """Wait for user to press enter."""
    console.print()
    Prompt.ask(f"  [{THEME['dim']}]Press Enter to continue[/{THEME['dim']}]", default="")


def main():
    """Main application loop."""
    while True:
        clear_screen()
        show_header()
        show_status_bar()
        
        choice = main_menu()
        
        if choice == "q":
            console.print()
            console.print(f"  [{THEME['accent']}]Goodbye![/{THEME['accent']}]")
            console.print()
            break
        
        elif choice == "1":
            config = configure_generate()
            show_config_summary(config, "Pixel-Perfect")
            
            if Confirm.ask(f"  [{THEME['accent']}]Proceed with generation?[/{THEME['accent']}]", default=True):
                cmd = build_generate_command(config)
                run_command(cmd)
            
            wait_for_enter()
        
        elif choice == "2":
            config = configure_gradient()
            show_config_summary(config, "Gradient")
            
            if Confirm.ask(f"  [{THEME['accent']}]Proceed with generation?[/{THEME['accent']}]", default=True):
                cmd = build_gradient_command(config)
                run_command(cmd)
            
            wait_for_enter()
        
        elif choice == "3":
            batch_process()
            wait_for_enter()
        
        elif choice == "4":
            dry_run()
            wait_for_enter()
        
        elif choice == "5":
            create_configs()
            wait_for_enter()
        
        elif choice == "6":
            view_directory()
            wait_for_enter()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(f"\n  [{THEME['accent']}]Interrupted. Goodbye![/{THEME['accent']}]\n")
        sys.exit(0)
