#!/usr/bin/env python3
"""
Dialogue Generator GUI - Graphical User Interface using Tkinter
Run: python gui.py
"""

import os
import sys
import json
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser


class DialogueGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dialogue Textbox Generator")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.pixel_frame = ttk.Frame(self.notebook, padding=10)
        self.gradient_frame = ttk.Frame(self.notebook, padding=10)
        self.batch_frame = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.pixel_frame, text="Pixel-Perfect")
        self.notebook.add(self.gradient_frame, text="Gradient")
        self.notebook.add(self.batch_frame, text="Batch")
        
        self.setup_pixel_tab()
        self.setup_gradient_tab()
        self.setup_batch_tab()
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.load_defaults()
    
    def setup_pixel_tab(self):
        files_frame = ttk.LabelFrame(self.pixel_frame, text="Files", padding=10)
        files_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(files_frame, text="Text File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.px_input_var = tk.StringVar(value="dialogue.txt")
        ttk.Entry(files_frame, textvariable=self.px_input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=lambda: self.browse_file(self.px_input_var, [("Text", "*.txt")])).grid(row=0, column=2)
        
        ttk.Label(files_frame, text="Font File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.px_font_var = tk.StringVar()
        ttk.Entry(files_frame, textvariable=self.px_font_var, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=lambda: self.browse_file(self.px_font_var, [("Fonts", "*.ttf *.otf")])).grid(row=1, column=2)
        ttk.Button(files_frame, text="Auto", command=lambda: self.auto_find(self.px_font_var, (".ttf", ".otf"))).grid(row=1, column=3, padx=2)
        
        ttk.Label(files_frame, text="Portrait:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.px_portrait_var = tk.StringVar()
        ttk.Entry(files_frame, textvariable=self.px_portrait_var, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=lambda: self.browse_file(self.px_portrait_var, [("Images", "*.png *.jpg *.jpeg *.bmp")])).grid(row=2, column=2)
        ttk.Button(files_frame, text="Auto", command=lambda: self.auto_find(self.px_portrait_var, (".png", ".jpg", ".jpeg", ".bmp"))).grid(row=2, column=3, padx=2)
        
        ttk.Label(files_frame, text="Output:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.px_output_var = tk.StringVar(value="dialogue.mp4")
        ttk.Entry(files_frame, textvariable=self.px_output_var, width=50).grid(row=3, column=1, padx=5)
        
        ttk.Label(files_frame, text="Sound:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.px_sound_var = tk.StringVar()
        ttk.Entry(files_frame, textvariable=self.px_sound_var, width=50).grid(row=4, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=lambda: self.browse_file(self.px_sound_var, [("Audio", "*.wav *.ogg *.mp3")])).grid(row=4, column=2)
        
        settings_frame = ttk.LabelFrame(self.pixel_frame, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Font Size:").grid(row=0, column=0, sticky=tk.W)
        self.px_fontsize_var = tk.IntVar(value=20)
        ttk.Spinbox(settings_frame, from_=8, to=100, textvariable=self.px_fontsize_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Max Width:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.px_maxwidth_var = tk.IntVar(value=1000)
        ttk.Spinbox(settings_frame, from_=100, to=4000, textvariable=self.px_maxwidth_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(settings_frame, text="Padding:").grid(row=1, column=0, sticky=tk.W)
        self.px_padding_var = tk.IntVar(value=10)
        ttk.Spinbox(settings_frame, from_=0, to=100, textvariable=self.px_padding_var, width=10).grid(row=1, column=1, padx=5)
        
        ttk.Label(settings_frame, text="FPS:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0))
        self.px_fps_var = tk.IntVar(value=30)
        ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.px_fps_var, width=10).grid(row=1, column=3, padx=5)
        
        ttk.Label(settings_frame, text="Char Speed:").grid(row=2, column=0, sticky=tk.W)
        self.px_charspeed_var = tk.IntVar(value=1)
        ttk.Spinbox(settings_frame, from_=1, to=30, textvariable=self.px_charspeed_var, width=10).grid(row=2, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Dwell (sec):").grid(row=2, column=2, sticky=tk.W, padx=(20, 0))
        self.px_dwell_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(settings_frame, from_=0, to=30, increment=0.5, textvariable=self.px_dwell_var, width=10).grid(row=2, column=3, padx=5)
        
        colors_frame = ttk.LabelFrame(self.pixel_frame, text="Colors", padding=10)
        colors_frame.pack(fill=tk.X, pady=5)
        
        self.px_textcolor = [255, 255, 255]
        self.px_bgcolor = [0, 0, 0]
        
        ttk.Label(colors_frame, text="Text Color:").grid(row=0, column=0, sticky=tk.W)
        self.px_textcolor_btn = tk.Button(colors_frame, text="    ", bg="#ffffff", command=lambda: self.pick_color("px_text"))
        self.px_textcolor_btn.grid(row=0, column=1, padx=5)
        
        ttk.Label(colors_frame, text="Background:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.px_bgcolor_btn = tk.Button(colors_frame, text="    ", bg="#000000", command=lambda: self.pick_color("px_bg"))
        self.px_bgcolor_btn.grid(row=0, column=3, padx=5)
        
        options_frame = ttk.LabelFrame(self.pixel_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.px_gif_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Export GIF", variable=self.px_gif_var).grid(row=0, column=0, padx=10)
        
        self.px_gifonly_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="GIF Only", variable=self.px_gifonly_var).grid(row=0, column=1, padx=10)
        
        self.px_autoopen_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Auto Open", variable=self.px_autoopen_var).grid(row=0, column=2, padx=10)
        
        btn_frame = ttk.Frame(self.pixel_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Preview (Dry Run)", command=self.px_dry_run).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generate Video", command=self.px_generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Config", command=self.px_save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Load Config", command=self.px_load_config).pack(side=tk.RIGHT, padx=5)
    
    def setup_gradient_tab(self):
        files_frame = ttk.LabelFrame(self.gradient_frame, text="Files", padding=10)
        files_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(files_frame, text="Text File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.gr_input_var = tk.StringVar(value="dialogue.txt")
        ttk.Entry(files_frame, textvariable=self.gr_input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=lambda: self.browse_file(self.gr_input_var, [("Text", "*.txt")])).grid(row=0, column=2)
        
        ttk.Label(files_frame, text="Font File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.gr_font_var = tk.StringVar()
        ttk.Entry(files_frame, textvariable=self.gr_font_var, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=lambda: self.browse_file(self.gr_font_var, [("Fonts", "*.ttf *.otf")])).grid(row=1, column=2)
        ttk.Button(files_frame, text="Auto", command=lambda: self.auto_find(self.gr_font_var, (".ttf", ".otf"))).grid(row=1, column=3, padx=2)
        
        ttk.Label(files_frame, text="BG Image:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.gr_bgimage_var = tk.StringVar()
        ttk.Entry(files_frame, textvariable=self.gr_bgimage_var, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=lambda: self.browse_file(self.gr_bgimage_var, [("Images", "*.png *.jpg *.jpeg")])).grid(row=2, column=2)
        
        ttk.Label(files_frame, text="Output:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.gr_output_var = tk.StringVar()
        ttk.Entry(files_frame, textvariable=self.gr_output_var, width=50).grid(row=3, column=1, padx=5)
        
        settings_frame = ttk.LabelFrame(self.gradient_frame, text="Box Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Width:").grid(row=0, column=0, sticky=tk.W)
        self.gr_width_var = tk.IntVar(value=1000)
        ttk.Spinbox(settings_frame, from_=100, to=4000, textvariable=self.gr_width_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Height:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.gr_height_var = tk.IntVar(value=209)
        ttk.Spinbox(settings_frame, from_=50, to=2000, textvariable=self.gr_height_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(settings_frame, text="Padding:").grid(row=1, column=0, sticky=tk.W)
        self.gr_padding_var = tk.IntVar(value=20)
        ttk.Spinbox(settings_frame, from_=0, to=100, textvariable=self.gr_padding_var, width=10).grid(row=1, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Font Size:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0))
        self.gr_fontsize_var = tk.IntVar(value=35)
        ttk.Spinbox(settings_frame, from_=8, to=100, textvariable=self.gr_fontsize_var, width=10).grid(row=1, column=3, padx=5)
        
        ttk.Label(settings_frame, text="FPS:").grid(row=2, column=0, sticky=tk.W)
        self.gr_fps_var = tk.IntVar(value=30)
        ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.gr_fps_var, width=10).grid(row=2, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Dwell (sec):").grid(row=2, column=2, sticky=tk.W, padx=(20, 0))
        self.gr_dwell_var = tk.DoubleVar(value=3.0)
        ttk.Spinbox(settings_frame, from_=0, to=30, increment=0.5, textvariable=self.gr_dwell_var, width=10).grid(row=2, column=3, padx=5)
        
        gradient_frame = ttk.LabelFrame(self.gradient_frame, text="Gradient", padding=10)
        gradient_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(gradient_frame, text="Direction:").grid(row=0, column=0, sticky=tk.W)
        self.gr_direction_var = tk.StringVar(value="vertical")
        ttk.Combobox(gradient_frame, textvariable=self.gr_direction_var, values=["vertical", "horizontal", "none"], width=12).grid(row=0, column=1, padx=5)
        
        self.gr_topcolor = [255, 255, 255, 255]
        self.gr_bottomcolor = [121, 121, 121, 255]
        self.gr_textcolor = [0, 0, 0, 255]
        
        ttk.Label(gradient_frame, text="Top/Left:").grid(row=1, column=0, sticky=tk.W)
        self.gr_topcolor_btn = tk.Button(gradient_frame, text="    ", bg="#ffffff", command=lambda: self.pick_color("gr_top"))
        self.gr_topcolor_btn.grid(row=1, column=1, padx=5)
        
        ttk.Label(gradient_frame, text="Bottom/Right:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0))
        self.gr_bottomcolor_btn = tk.Button(gradient_frame, text="    ", bg="#797979", command=lambda: self.pick_color("gr_bottom"))
        self.gr_bottomcolor_btn.grid(row=1, column=3, padx=5)
        
        ttk.Label(gradient_frame, text="Text:").grid(row=1, column=4, sticky=tk.W, padx=(20, 0))
        self.gr_textcolor_btn = tk.Button(gradient_frame, text="    ", bg="#000000", command=lambda: self.pick_color("gr_text"))
        self.gr_textcolor_btn.grid(row=1, column=5, padx=5)
        
        options_frame = ttk.LabelFrame(self.gradient_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky=tk.W)
        self.gr_format_var = tk.StringVar(value="webm")
        ttk.Combobox(options_frame, textvariable=self.gr_format_var, values=["webm", "mp4", "gif"], width=10).grid(row=0, column=1, padx=5)
        
        self.gr_autoopen_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Auto Open", variable=self.gr_autoopen_var).grid(row=0, column=2, padx=20)
        
        btn_frame = ttk.Frame(self.gradient_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Preview (Dry Run)", command=self.gr_dry_run).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generate Video", command=self.gr_generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Config", command=self.gr_save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Load Config", command=self.gr_load_config).pack(side=tk.RIGHT, padx=5)
    
    def setup_batch_tab(self):
        ttk.Label(self.batch_frame, text="Process multiple dialogue files at once").pack(pady=10)
        
        pattern_frame = ttk.LabelFrame(self.batch_frame, text="File Pattern", padding=10)
        pattern_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pattern_frame, text="Pattern:").grid(row=0, column=0, sticky=tk.W)
        self.batch_pattern_var = tk.StringVar(value="*.txt")
        ttk.Entry(pattern_frame, textvariable=self.batch_pattern_var, width=40).grid(row=0, column=1, padx=5)
        
        ttk.Label(pattern_frame, text="Generator:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.batch_gen_var = tk.StringVar(value="generate")
        ttk.Combobox(pattern_frame, textvariable=self.batch_gen_var, values=["generate", "gradient"], width=15).grid(row=1, column=1, padx=5, sticky=tk.W)
        
        ttk.Button(self.batch_frame, text="Run Batch", command=self.run_batch).pack(pady=10)
        
        self.batch_output = tk.Text(self.batch_frame, height=15, width=80)
        self.batch_output.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def browse_file(self, var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            var.set(path)
    
    def auto_find(self, var, extensions):
        for f in os.listdir("."):
            if f.lower().endswith(extensions):
                var.set(f)
                return
        messagebox.showinfo("Not Found", f"No {extensions} file found in current directory")
    
    def pick_color(self, target):
        color = colorchooser.askcolor(title="Choose Color")
        if color[1]:
            rgb = [int(c) for c in color[0]]
            hex_color = color[1]
            
            if target == "px_text":
                self.px_textcolor = rgb
                self.px_textcolor_btn.config(bg=hex_color)
            elif target == "px_bg":
                self.px_bgcolor = rgb
                self.px_bgcolor_btn.config(bg=hex_color)
            elif target == "gr_top":
                self.gr_topcolor = rgb + [255]
                self.gr_topcolor_btn.config(bg=hex_color)
            elif target == "gr_bottom":
                self.gr_bottomcolor = rgb + [255]
                self.gr_bottomcolor_btn.config(bg=hex_color)
            elif target == "gr_text":
                self.gr_textcolor = rgb + [255]
                self.gr_textcolor_btn.config(bg=hex_color)
    
    def load_defaults(self):
        self.auto_find(self.px_font_var, (".ttf", ".otf"))
        self.auto_find(self.gr_font_var, (".ttf", ".otf"))
    
    def build_px_command(self, dry_run=False):
        cmd = ["python", "generate.py"]
        cmd.extend(["-i", self.px_input_var.get()])
        if self.px_font_var.get():
            cmd.extend(["-f", self.px_font_var.get()])
        if self.px_portrait_var.get():
            cmd.extend(["-p", self.px_portrait_var.get()])
        cmd.extend(["--font-size", str(self.px_fontsize_var.get())])
        cmd.extend(["--max-width", str(self.px_maxwidth_var.get())])
        cmd.extend(["--padding", str(self.px_padding_var.get())])
        cmd.extend(["--fps", str(self.px_fps_var.get())])
        cmd.extend(["--char-speed", str(self.px_charspeed_var.get())])
        cmd.extend(["--dwell", str(self.px_dwell_var.get())])
        cmd.extend(["--text-color", ",".join(map(str, self.px_textcolor))])
        cmd.extend(["--bg-color", ",".join(map(str, self.px_bgcolor))])
        cmd.extend(["-o", self.px_output_var.get()])
        if self.px_sound_var.get():
            cmd.extend(["--sound", self.px_sound_var.get()])
        if self.px_gif_var.get():
            cmd.append("--gif")
        if self.px_gifonly_var.get():
            cmd.append("--gif-only")
        if self.px_autoopen_var.get():
            cmd.append("--auto-open")
        if dry_run:
            cmd.append("--dry-run")
        return cmd
    
    def build_gr_command(self, dry_run=False):
        cmd = ["python", "gradient.py"]
        cmd.extend(["-i", self.gr_input_var.get()])
        if self.gr_font_var.get():
            cmd.extend(["-f", self.gr_font_var.get()])
        cmd.extend(["--width", str(self.gr_width_var.get())])
        cmd.extend(["--height", str(self.gr_height_var.get())])
        cmd.extend(["--padding", str(self.gr_padding_var.get())])
        cmd.extend(["--font-size", str(self.gr_fontsize_var.get())])
        cmd.extend(["--fps", str(self.gr_fps_var.get())])
        cmd.extend(["--dwell", str(self.gr_dwell_var.get())])
        cmd.extend(["--gradient", self.gr_direction_var.get()])
        cmd.extend(["--top-color", ",".join(map(str, self.gr_topcolor))])
        cmd.extend(["--bottom-color", ",".join(map(str, self.gr_bottomcolor))])
        cmd.extend(["--text-color", ",".join(map(str, self.gr_textcolor))])
        if self.gr_bgimage_var.get():
            cmd.extend(["--bg-image", self.gr_bgimage_var.get()])
        cmd.extend(["--format", self.gr_format_var.get()])
        if self.gr_output_var.get():
            cmd.extend(["-o", self.gr_output_var.get()])
        if self.gr_autoopen_var.get():
            cmd.append("--auto-open")
        if dry_run:
            cmd.append("--dry-run")
        return cmd
    
    def run_command(self, cmd, callback=None):
        def worker():
            self.status_var.set("Running...")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                output = result.stdout + result.stderr
                if callback:
                    self.root.after(0, lambda: callback(output, result.returncode == 0))
                else:
                    self.root.after(0, lambda: self.show_result(output, result.returncode == 0))
            except Exception as e:
                self.root.after(0, lambda: self.show_result(str(e), False))
        
        thread = threading.Thread(target=worker)
        thread.start()
    
    def show_result(self, output, success):
        self.status_var.set("Done" if success else "Error")
        if success:
            messagebox.showinfo("Complete", output or "Video generated successfully!")
        else:
            messagebox.showerror("Error", output or "Generation failed")
    
    def px_dry_run(self):
        cmd = self.build_px_command(dry_run=True)
        self.run_command(cmd)
    
    def px_generate(self):
        cmd = self.build_px_command()
        self.run_command(cmd)
    
    def gr_dry_run(self):
        cmd = self.build_gr_command(dry_run=True)
        self.run_command(cmd)
    
    def gr_generate(self):
        cmd = self.build_gr_command()
        self.run_command(cmd)
    
    def run_batch(self):
        gen = self.batch_gen_var.get()
        pattern = self.batch_pattern_var.get()
        cmd = ["python", f"{gen}.py", "--batch", pattern]
        
        def update_output(output, success):
            self.batch_output.delete(1.0, tk.END)
            self.batch_output.insert(tk.END, output)
            self.status_var.set("Batch complete" if success else "Batch failed")
        
        self.run_command(cmd, update_output)
    
    def px_save_config(self):
        config = {
            "max_text_width": self.px_maxwidth_var.get(),
            "padding": self.px_padding_var.get(),
            "font_size": self.px_fontsize_var.get(),
            "fps": self.px_fps_var.get(),
            "char_speed": self.px_charspeed_var.get(),
            "video_duration_sec_after_text": self.px_dwell_var.get(),
            "text_color": self.px_textcolor,
            "bg_color": self.px_bgcolor,
            "export_gif": self.px_gif_var.get(),
            "auto_open": self.px_autoopen_var.get(),
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        messagebox.showinfo("Saved", "Config saved to config.json")
    
    def px_load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)
            self.px_maxwidth_var.set(config.get("max_text_width", 1000))
            self.px_padding_var.set(config.get("padding", 10))
            self.px_fontsize_var.set(config.get("font_size", 20))
            self.px_fps_var.set(config.get("fps", 30))
            self.px_charspeed_var.set(config.get("char_speed", 1))
            self.px_dwell_var.set(config.get("video_duration_sec_after_text", 2))
            if "text_color" in config:
                self.px_textcolor = config["text_color"]
            if "bg_color" in config:
                self.px_bgcolor = config["bg_color"]
            self.px_gif_var.set(config.get("export_gif", False))
            self.px_autoopen_var.set(config.get("auto_open", False))
            messagebox.showinfo("Loaded", "Config loaded from config.json")
        else:
            messagebox.showwarning("Not Found", "config.json not found")
    
    def gr_save_config(self):
        config = {
            "box_size": [self.gr_width_var.get(), self.gr_height_var.get()],
            "padding": self.gr_padding_var.get(),
            "font_size": self.gr_fontsize_var.get(),
            "fps": self.gr_fps_var.get(),
            "dwell_time": self.gr_dwell_var.get(),
            "gradient_direction": self.gr_direction_var.get(),
            "top_color": self.gr_topcolor,
            "bottom_color": self.gr_bottomcolor,
            "text_color": self.gr_textcolor,
            "output_format": self.gr_format_var.get(),
            "auto_open": self.gr_autoopen_var.get(),
        }
        with open("gradient_config.json", "w") as f:
            json.dump(config, f, indent=2)
        messagebox.showinfo("Saved", "Config saved to gradient_config.json")
    
    def gr_load_config(self):
        if os.path.exists("gradient_config.json"):
            with open("gradient_config.json", "r") as f:
                config = json.load(f)
            if "box_size" in config:
                self.gr_width_var.set(config["box_size"][0])
                self.gr_height_var.set(config["box_size"][1])
            self.gr_padding_var.set(config.get("padding", 20))
            self.gr_fontsize_var.set(config.get("font_size", 35))
            self.gr_fps_var.set(config.get("fps", 30))
            self.gr_dwell_var.set(config.get("dwell_time", 3))
            self.gr_direction_var.set(config.get("gradient_direction", "vertical"))
            if "top_color" in config:
                self.gr_topcolor = config["top_color"]
            if "bottom_color" in config:
                self.gr_bottomcolor = config["bottom_color"]
            if "text_color" in config:
                self.gr_textcolor = config["text_color"]
            self.gr_format_var.set(config.get("output_format", "webm"))
            self.gr_autoopen_var.set(config.get("auto_open", False))
            messagebox.showinfo("Loaded", "Config loaded from gradient_config.json")
        else:
            messagebox.showwarning("Not Found", "gradient_config.json not found")


def main():
    root = tk.Tk()
    app = DialogueGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
