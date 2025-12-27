#!/usr/bin/env python3
"""
Dialogue Generator TUI - Terminal User Interface using Rich
Run: python tui.py
Requires: pip install rich
"""

import os
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich import box
except ImportError:
    print("Rich not installed. Run: pip install rich")
    sys.exit(1)

console = Console()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║       ██████╗ ██╗ █████╗ ██╗      ██████╗  ██████╗ ██╗   ██╗███████╗║
║       ██╔══██╗██║██╔══██╗██║     ██╔═══██╗██╔════╝ ██║   ██║██╔════╝║
║       ██║  ██║██║███████║██║     ██║   ██║██║  ███╗██║   ██║█████╗  ║
║       ██║  ██║██║██╔══██║██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ║
║       ██████╔╝██║██║  ██║███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗║
║       ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝║
║                     TEXTBOX GENERATOR                              ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")


def find_files(extensions):
    files = []
    for f in os.listdir("."):
        if f.lower().endswith(extensions):
            files.append(f)
    return files


def show_files_table(title, files, empty_msg):
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("#", style="dim", width=4)
    table.add_column("Filename", style="cyan")
    table.add_column("Size", justify="right", style="green")
    
    if not files:
        console.print(f"[yellow]{empty_msg}[/yellow]")
        return []
    
    for i, f in enumerate(files, 1):
        size = os.path.getsize(f)
        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
        table.add_row(str(i), f, size_str)
    
    console.print(table)
    return files


def select_file(files, prompt_text, allow_none=False):
    if not files:
        return None
    
    if allow_none:
        console.print("[dim]0. None[/dim]")
    
    while True:
        choice = Prompt.ask(prompt_text, default="1")
        try:
            idx = int(choice)
            if allow_none and idx == 0:
                return None
            if 1 <= idx <= len(files):
                return files[idx - 1]
        except ValueError:
            pass
        console.print("[red]Invalid choice[/red]")


def get_color_input(prompt_text, default):
    while True:
        value = Prompt.ask(prompt_text, default=",".join(map(str, default)))
        try:
            parts = [int(x.strip()) for x in value.split(",")]
            if len(parts) >= 3:
                return parts[:4] if len(parts) >= 4 else parts[:3] + [255]
        except ValueError:
            pass
        console.print("[red]Enter as R,G,B or R,G,B,A (e.g., 255,255,255)[/red]")


def main_menu():
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Description")
    
    table.add_row("1", "Generate Pixel-Perfect Video (generate.py)")
    table.add_row("2", "Generate Gradient Video (gradient.py)")
    table.add_row("3", "Batch Process Multiple Files")
    table.add_row("4", "Preview Settings (Dry Run)")
    table.add_row("5", "Create Default Config Files")
    table.add_row("6", "View Current Files")
    table.add_row("q", "Quit")
    
    console.print(Panel(table, title="[bold]Main Menu[/bold]", border_style="green"))
    return Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6", "q"])


def configure_generate():
    console.print("\n[bold cyan]═══ Pixel-Perfect Generator Configuration ═══[/bold cyan]\n")
    
    config = {}
    
    txt_files = find_files((".txt",))
    show_files_table("Text Files", txt_files, "No .txt files found")
    config["input"] = select_file(txt_files, "Select text file") or "dialogue.txt"
    
    console.print()
    font_files = find_files((".ttf", ".otf"))
    show_files_table("Font Files", font_files, "No font files found")
    config["font"] = select_file(font_files, "Select font")
    
    console.print()
    image_files = find_files((".png", ".jpg", ".jpeg", ".bmp"))
    show_files_table("Portrait Images", image_files, "No images found")
    config["portrait"] = select_file(image_files, "Select portrait (0 for none)", allow_none=True)
    
    console.print("\n[bold]Video Settings[/bold]")
    config["font_size"] = IntPrompt.ask("Font size", default=20)
    config["max_width"] = IntPrompt.ask("Max text width", default=1000)
    config["padding"] = IntPrompt.ask("Padding", default=10)
    config["fps"] = IntPrompt.ask("FPS", default=30)
    config["dwell"] = IntPrompt.ask("Dwell time (seconds after text)", default=2)
    
    console.print("\n[bold]Colors[/bold]")
    config["text_color"] = get_color_input("Text color (R,G,B)", [255, 255, 255])
    config["bg_color"] = get_color_input("Background color (R,G,B)", [0, 0, 0])
    
    console.print("\n[bold]Export Options[/bold]")
    config["output"] = Prompt.ask("Output filename", default="dialogue.mp4")
    config["gif"] = Confirm.ask("Also export as GIF?", default=False)
    config["auto_open"] = Confirm.ask("Open when done?", default=False)
    
    sound_files = find_files((".wav", ".ogg", ".mp3"))
    if sound_files:
        show_files_table("Sound Files", sound_files, "")
        config["sound"] = select_file(sound_files, "Select typing sound (0 for none)", allow_none=True)
    
    return config


def configure_gradient():
    console.print("\n[bold cyan]═══ Gradient Generator Configuration ═══[/bold cyan]\n")
    
    config = {}
    
    txt_files = find_files((".txt",))
    show_files_table("Text Files", txt_files, "No .txt files found")
    config["input"] = select_file(txt_files, "Select text file") or "dialogue.txt"
    
    console.print()
    font_files = find_files((".ttf", ".otf"))
    show_files_table("Font Files", font_files, "No font files found")
    config["font"] = select_file(font_files, "Select font")
    
    console.print("\n[bold]Box Settings[/bold]")
    config["width"] = IntPrompt.ask("Box width", default=1000)
    config["height"] = IntPrompt.ask("Box height", default=209)
    config["padding"] = IntPrompt.ask("Padding", default=20)
    config["font_size"] = IntPrompt.ask("Font size", default=35)
    config["fps"] = IntPrompt.ask("FPS", default=30)
    config["dwell"] = IntPrompt.ask("Dwell time (seconds)", default=3)
    
    console.print("\n[bold]Gradient Settings[/bold]")
    gradient_type = Prompt.ask(
        "Gradient direction",
        choices=["vertical", "horizontal", "none"],
        default="vertical"
    )
    config["gradient"] = gradient_type
    
    if gradient_type != "none":
        if gradient_type == "vertical":
            config["top_color"] = get_color_input("Top color (R,G,B,A)", [255, 255, 255, 255])
            config["bottom_color"] = get_color_input("Bottom color (R,G,B,A)", [121, 121, 121, 255])
        else:
            config["left_color"] = get_color_input("Left color (R,G,B,A)", [255, 255, 255, 255])
            config["right_color"] = get_color_input("Right color (R,G,B,A)", [121, 121, 121, 255])
    
    config["text_color"] = get_color_input("Text color (R,G,B,A)", [0, 0, 0, 255])
    
    console.print("\n[bold]Background Image (optional)[/bold]")
    image_files = find_files((".png", ".jpg", ".jpeg", ".bmp"))
    if image_files:
        show_files_table("Background Images", image_files, "")
        config["bg_image"] = select_file(image_files, "Select background (0 for gradient)", allow_none=True)
    
    console.print("\n[bold]Export Options[/bold]")
    config["format"] = Prompt.ask("Output format", choices=["webm", "mp4", "gif"], default="webm")
    config["output"] = Prompt.ask("Output name (without extension)", default="")
    config["auto_open"] = Confirm.ask("Open when done?", default=False)
    
    return config


def build_generate_command(config):
    cmd = ["python", "generate.py"]
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
    cmd = ["python", "gradient.py"]
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


def run_command(cmd):
    console.print(f"\n[dim]Running: {' '.join(cmd)}[/dim]\n")
    import subprocess
    result = subprocess.run(cmd)
    return result.returncode == 0


def batch_process():
    console.print("\n[bold cyan]═══ Batch Processing ═══[/bold cyan]\n")
    
    generator = Prompt.ask(
        "Which generator?",
        choices=["generate", "gradient"],
        default="generate"
    )
    
    pattern = Prompt.ask("File pattern (glob)", default="*.txt")
    
    cmd = ["python", f"{generator}.py", "--batch", pattern]
    run_command(cmd)


def dry_run():
    console.print("\n[bold cyan]═══ Dry Run (Preview) ═══[/bold cyan]\n")
    
    generator = Prompt.ask(
        "Which generator?",
        choices=["generate", "gradient"],
        default="generate"
    )
    
    txt_files = find_files((".txt",))
    show_files_table("Text Files", txt_files, "No .txt files found")
    input_file = select_file(txt_files, "Select text file") or "dialogue.txt"
    
    cmd = ["python", f"{generator}.py", "-i", input_file, "--dry-run"]
    run_command(cmd)


def create_configs():
    console.print("\n[bold cyan]═══ Creating Config Files ═══[/bold cyan]\n")
    
    import subprocess
    subprocess.run(["python", "generate.py", "--init-config"])
    subprocess.run(["python", "gradient.py", "--init-config"])
    
    console.print("\n[green]Config files created![/green]")


def view_files():
    console.print("\n[bold cyan]═══ Current Directory Files ═══[/bold cyan]\n")
    
    console.print("[bold]Text Files:[/bold]")
    show_files_table("", find_files((".txt",)), "None found")
    
    console.print("\n[bold]Font Files:[/bold]")
    show_files_table("", find_files((".ttf", ".otf")), "None found")
    
    console.print("\n[bold]Image Files:[/bold]")
    show_files_table("", find_files((".png", ".jpg", ".jpeg", ".bmp")), "None found")
    
    console.print("\n[bold]Config Files:[/bold]")
    show_files_table("", find_files((".json",)), "None found")
    
    console.print("\n[bold]Output Files:[/bold]")
    show_files_table("", find_files((".mp4", ".webm", ".gif")), "None found")


def main():
    while True:
        clear_screen()
        show_banner()
        
        choice = main_menu()
        
        if choice == "q":
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        elif choice == "1":
            config = configure_generate()
            console.print("\n[bold]Review Configuration:[/bold]")
            for k, v in config.items():
                console.print(f"  {k}: {v}")
            
            if Confirm.ask("\nProceed with generation?", default=True):
                cmd = build_generate_command(config)
                run_command(cmd)
            
            Prompt.ask("\nPress Enter to continue")
        elif choice == "2":
            config = configure_gradient()
            console.print("\n[bold]Review Configuration:[/bold]")
            for k, v in config.items():
                console.print(f"  {k}: {v}")
            
            if Confirm.ask("\nProceed with generation?", default=True):
                cmd = build_gradient_command(config)
                run_command(cmd)
            
            Prompt.ask("\nPress Enter to continue")
        elif choice == "3":
            batch_process()
            Prompt.ask("\nPress Enter to continue")
        elif choice == "4":
            dry_run()
            Prompt.ask("\nPress Enter to continue")
        elif choice == "5":
            create_configs()
            Prompt.ask("\nPress Enter to continue")
        elif choice == "6":
            view_files()
            Prompt.ask("\nPress Enter to continue")


if __name__ == "__main__":
    main()
