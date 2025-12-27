#!/usr/bin/env python3
"""
Dialogue Generator GUI - Modern Interface with Live Preview
Run: python gui.py
"""

import os
import sys
import json
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font as tkfont


class ModernStyle:
    BG_DARK = "#1a1a2e"
    BG_MEDIUM = "#16213e"
    BG_LIGHT = "#0f3460"
    ACCENT = "#e94560"
    ACCENT_HOVER = "#ff6b6b"
    TEXT = "#eaeaea"
    TEXT_DIM = "#a0a0a0"
    SUCCESS = "#4ecca3"
    WARNING = "#ffc93c"
    TOOLTIP_BG = "#2d2d44"
    TOOLTIP_FG = "#ffffff"


class Tooltip:
    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.after_id = None
        
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)
        widget.bind("<ButtonPress>", self._hide)
    
    def _schedule(self, event=None):
        self._hide()
        self.after_id = self.widget.after(self.delay, self._show)
    
    def _show(self):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        frame = tk.Frame(tw, bg=ModernStyle.TOOLTIP_BG, bd=1, relief=tk.SOLID)
        frame.pack()
        
        label = tk.Label(
            frame, text=self.text, justify=tk.LEFT,
            bg=ModernStyle.TOOLTIP_BG, fg=ModernStyle.TOOLTIP_FG,
            font=("Segoe UI", 9), padx=8, pady=4, wraplength=300
        )
        label.pack()
    
    def _hide(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class CollapsibleFrame(ttk.Frame):
    def __init__(self, parent, text, collapsed=True, style="Card.TFrame"):
        super().__init__(parent, style=style)
        
        self.collapsed = collapsed
        self._text = text
        
        self.header = ttk.Frame(self, style="Card.TFrame")
        self.header.pack(fill=tk.X)
        
        self.toggle_btn = ttk.Label(
            self.header, 
            text=f"{'▶' if collapsed else '▼'} {text}",
            style="Card.TLabel",
            cursor="hand2"
        )
        self.toggle_btn.pack(side=tk.LEFT, pady=5)
        self.toggle_btn.bind("<Button-1>", self._toggle)
        
        self.content = ttk.Frame(self, style="Card.TFrame", padding=(15, 10))
        if not collapsed:
            self.content.pack(fill=tk.X, padx=(15, 0))
    
    def _toggle(self, event=None):
        self.collapsed = not self.collapsed
        self.toggle_btn.config(text=f"{'▶' if self.collapsed else '▼'} {self._text}")
        if self.collapsed:
            self.content.pack_forget()
        else:
            self.content.pack(fill=tk.X, padx=(15, 0))


class DialogueGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dialogue Textbox Generator")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)
        self.root.configure(bg=ModernStyle.BG_DARK)
        
        self.setup_styles()
        self.setup_fonts()
        
        main_container = ttk.Frame(root, style="Dark.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.setup_header(main_container)
        
        content_frame = ttk.Frame(main_container, style="Dark.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        left_panel = ttk.Frame(content_frame, style="Dark.TFrame")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_panel = ttk.Frame(content_frame, style="Dark.TFrame", width=380)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_panel.pack_propagate(False)
        
        self.notebook = ttk.Notebook(left_panel, style="Dark.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.pixel_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.gradient_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.batch_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        
        self.notebook.add(self.pixel_frame, text="  Pixel-Perfect  ")
        self.notebook.add(self.gradient_frame, text="  Gradient  ")
        self.notebook.add(self.batch_frame, text="  Batch  ")
        
        self.setup_preview_panel(right_panel)
        self.setup_pixel_tab()
        self.setup_gradient_tab()
        self.setup_batch_tab()
        self.setup_status_bar(main_container)
        
        self.load_defaults()
        self.bind_preview_updates()
        self.root.after(100, self.update_preview)
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("Dark.TFrame", background=ModernStyle.BG_DARK)
        self.style.configure("Card.TFrame", background=ModernStyle.BG_MEDIUM)
        self.style.configure("Preview.TFrame", background=ModernStyle.BG_LIGHT)
        
        self.style.configure("Dark.TLabel", 
                           background=ModernStyle.BG_DARK, 
                           foreground=ModernStyle.TEXT)
        self.style.configure("Card.TLabel", 
                           background=ModernStyle.BG_MEDIUM, 
                           foreground=ModernStyle.TEXT)
        self.style.configure("Header.TLabel", 
                           background=ModernStyle.BG_DARK, 
                           foreground=ModernStyle.TEXT,
                           font=("Segoe UI", 16, "bold"))
        self.style.configure("SubHeader.TLabel", 
                           background=ModernStyle.BG_DARK, 
                           foreground=ModernStyle.TEXT_DIM,
                           font=("Segoe UI", 9))
        self.style.configure("Preview.TLabel", 
                           background=ModernStyle.BG_LIGHT, 
                           foreground=ModernStyle.TEXT,
                           font=("Segoe UI", 10, "bold"))
        
        self.style.configure("Dark.TNotebook", background=ModernStyle.BG_DARK)
        self.style.configure("Dark.TNotebook.Tab", 
                           background=ModernStyle.BG_MEDIUM,
                           foreground=ModernStyle.TEXT,
                           padding=[12, 6],
                           font=("Segoe UI", 9))
        self.style.map("Dark.TNotebook.Tab",
                      background=[("selected", ModernStyle.BG_LIGHT)],
                      foreground=[("selected", ModernStyle.TEXT)])
        
        self.style.configure("Card.TLabelframe", 
                           background=ModernStyle.BG_MEDIUM,
                           foreground=ModernStyle.TEXT)
        self.style.configure("Card.TLabelframe.Label", 
                           background=ModernStyle.BG_MEDIUM,
                           foreground=ModernStyle.ACCENT,
                           font=("Segoe UI", 9, "bold"))
        
        self.style.configure("TEntry",
                           fieldbackground=ModernStyle.BG_LIGHT,
                           foreground=ModernStyle.TEXT,
                           insertcolor=ModernStyle.TEXT)
        
        self.style.configure("TSpinbox",
                           fieldbackground=ModernStyle.BG_LIGHT,
                           foreground=ModernStyle.TEXT,
                           arrowcolor=ModernStyle.ACCENT)
        
        self.style.configure("TCombobox",
                           fieldbackground=ModernStyle.BG_LIGHT,
                           foreground=ModernStyle.TEXT,
                           arrowcolor=ModernStyle.ACCENT)
        
        self.style.configure("Accent.TButton",
                           background=ModernStyle.ACCENT,
                           foreground="white",
                           font=("Segoe UI", 10, "bold"),
                           padding=[15, 8])
        self.style.map("Accent.TButton",
                      background=[("active", ModernStyle.ACCENT_HOVER)])
        
        self.style.configure("Secondary.TButton",
                           background=ModernStyle.BG_LIGHT,
                           foreground=ModernStyle.TEXT,
                           padding=[8, 4])
        self.style.map("Secondary.TButton",
                      background=[("active", ModernStyle.BG_MEDIUM)])
        
        self.style.configure("TCheckbutton",
                           background=ModernStyle.BG_MEDIUM,
                           foreground=ModernStyle.TEXT)
        
        self.style.configure("Status.TLabel",
                           background=ModernStyle.BG_MEDIUM,
                           foreground=ModernStyle.TEXT_DIM,
                           font=("Segoe UI", 9))
    
    def setup_fonts(self):
        self.header_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = tkfont.Font(family="Segoe UI", size=9)
        self.mono_font = tkfont.Font(family="Consolas", size=10)
    
    def setup_header(self, parent):
        header_frame = ttk.Frame(parent, style="Dark.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_label = ttk.Label(header_frame, 
                               text="Dialogue Textbox Generator",
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame,
                                  text="Undertale-style dialogue animations",
                                  style="SubHeader.TLabel")
        subtitle_label.pack(side=tk.LEFT, padx=(12, 0), pady=(6, 0))
    
    def setup_preview_panel(self, parent):
        preview_label = ttk.Label(parent, text="LIVE PREVIEW", style="Preview.TLabel")
        preview_label.pack(fill=tk.X, pady=(0, 8))
        Tooltip(preview_label, "Real-time preview of your dialogue box")
        
        preview_container = ttk.Frame(parent, style="Preview.TFrame", padding=8)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview_canvas = tk.Canvas(
            preview_container,
            bg="#000000",
            highlightthickness=2,
            highlightbackground=ModernStyle.ACCENT
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        info_frame = ttk.Frame(parent, style="Dark.TFrame")
        info_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.preview_info_var = tk.StringVar(value="Edit text below to preview")
        info_label = ttk.Label(info_frame, 
                              textvariable=self.preview_info_var,
                              style="Status.TLabel")
        info_label.pack()
        
        text_frame = ttk.Frame(parent, style="Dark.TFrame")
        text_frame.pack(fill=tk.X, pady=(8, 0))
        
        text_label = ttk.Label(text_frame, text="Preview Text:", style="Dark.TLabel")
        text_label.pack(anchor=tk.W)
        Tooltip(text_label, "Type dialogue here to preview how it will look")
        
        self.preview_text_var = tk.StringVar(value="* Hello, world!\n* This is a preview.")
        self.preview_text = tk.Text(
            text_frame, 
            height=3, 
            bg=ModernStyle.BG_LIGHT,
            fg=ModernStyle.TEXT,
            insertbackground=ModernStyle.TEXT,
            font=self.mono_font,
            relief=tk.FLAT,
            padx=8,
            pady=8
        )
        self.preview_text.pack(fill=tk.X, pady=(4, 0))
        self.preview_text.insert("1.0", "* Hello, world!\n* This is a preview.")
        self.preview_text.bind("<KeyRelease>", lambda e: self.update_preview())
    
    def setup_pixel_tab(self):
        canvas = tk.Canvas(self.pixel_frame, bg=ModernStyle.BG_MEDIUM, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.pixel_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        files_frame = ttk.LabelFrame(scrollable_frame, text="Files", style="Card.TLabelframe", padding=12)
        files_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.px_input_var = tk.StringVar(value="dialogue.txt")
        self.px_font_var = tk.StringVar()
        self.px_portrait_var = tk.StringVar()
        self.px_output_var = tk.StringVar(value="dialogue.mp4")
        self.px_sound_var = tk.StringVar()
        
        self.create_file_row(files_frame, "Text File:", self.px_input_var, [("Text", "*.txt")], 0,
                            tooltip="Your dialogue text file")
        self.create_file_row(files_frame, "Output:", self.px_output_var, None, 1,
                            tooltip="Output video filename")
        
        quick_frame = ttk.LabelFrame(scrollable_frame, text="Quick Settings", style="Card.TLabelframe", padding=12)
        quick_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.px_fontsize_var = tk.IntVar(value=24)
        self.px_maxwidth_var = tk.IntVar(value=800)
        self.px_padding_var = tk.IntVar(value=15)
        self.px_fps_var = tk.IntVar(value=30)
        self.px_charspeed_var = tk.IntVar(value=2)
        self.px_dwell_var = tk.DoubleVar(value=2.0)
        
        quick_grid = ttk.Frame(quick_frame, style="Card.TFrame")
        quick_grid.pack(fill=tk.X)
        
        self.create_spinbox_row(quick_grid, "Font Size:", self.px_fontsize_var, 12, 72, 0, 0,
                               tooltip="Text size in pixels")
        self.create_spinbox_row(quick_grid, "Speed:", self.px_charspeed_var, 1, 10, 0, 2,
                               tooltip="Typing speed (1=fastest, 10=slowest)")
        
        colors_row = ttk.Frame(quick_frame, style="Card.TFrame")
        colors_row.pack(fill=tk.X, pady=(8, 0))
        
        self.px_textcolor = [255, 255, 255]
        self.px_bgcolor = [0, 0, 0]
        
        ttk.Label(colors_row, text="Text:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.px_textcolor_btn = tk.Button(
            colors_row, text="", bg="#ffffff", width=4, height=1,
            relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("px_text")
        )
        self.px_textcolor_btn.pack(side=tk.LEFT, padx=(0, 15))
        Tooltip(self.px_textcolor_btn, "Text color")
        
        ttk.Label(colors_row, text="Background:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.px_bgcolor_btn = tk.Button(
            colors_row, text="", bg="#000000", width=4, height=1,
            relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("px_bg")
        )
        self.px_bgcolor_btn.pack(side=tk.LEFT)
        Tooltip(self.px_bgcolor_btn, "Background color")
        
        advanced = CollapsibleFrame(scrollable_frame, "Advanced Options", collapsed=True)
        advanced.pack(fill=tk.X, pady=(0, 8))
        
        adv_files = ttk.Frame(advanced.content, style="Card.TFrame")
        adv_files.pack(fill=tk.X)
        
        self.create_file_row(adv_files, "Font:", self.px_font_var, [("Fonts", "*.ttf *.otf")], 0, 
                            auto_ext=(".ttf", ".otf"), tooltip="Custom font file (auto-detects if empty)")
        self.create_file_row(adv_files, "Portrait:", self.px_portrait_var, [("Images", "*.png *.jpg")], 1,
                            tooltip="Character portrait image")
        self.create_file_row(adv_files, "Sound:", self.px_sound_var, [("Audio", "*.wav *.ogg *.mp3")], 2,
                            tooltip="Typing sound effect")
        
        adv_settings = ttk.Frame(advanced.content, style="Card.TFrame")
        adv_settings.pack(fill=tk.X, pady=(8, 0))
        
        self.create_spinbox_row(adv_settings, "Max Width:", self.px_maxwidth_var, 200, 2000, 0, 0,
                               tooltip="Max text width before wrapping")
        self.create_spinbox_row(adv_settings, "Padding:", self.px_padding_var, 0, 50, 0, 2,
                               tooltip="Space around text")
        self.create_spinbox_row(adv_settings, "FPS:", self.px_fps_var, 15, 60, 1, 0,
                               tooltip="Video frame rate")
        self.create_spinbox_row(adv_settings, "Dwell:", self.px_dwell_var, 0, 10, 1, 2, increment=0.5,
                               tooltip="Pause after text finishes (seconds)")
        
        export = CollapsibleFrame(scrollable_frame, "Export Options", collapsed=True)
        export.pack(fill=tk.X, pady=(0, 8))
        
        self.px_gif_var = tk.BooleanVar(value=False)
        self.px_gifonly_var = tk.BooleanVar(value=False)
        self.px_autoopen_var = tk.BooleanVar(value=True)
        
        gif_cb = ttk.Checkbutton(export.content, text="Also export GIF", variable=self.px_gif_var, style="TCheckbutton")
        gif_cb.pack(anchor=tk.W)
        Tooltip(gif_cb, "Create a GIF alongside the video")
        
        gifonly_cb = ttk.Checkbutton(export.content, text="GIF only (no video)", variable=self.px_gifonly_var, style="TCheckbutton")
        gifonly_cb.pack(anchor=tk.W)
        Tooltip(gifonly_cb, "Only create GIF, skip video")
        
        auto_cb = ttk.Checkbutton(export.content, text="Open when done", variable=self.px_autoopen_var, style="TCheckbutton")
        auto_cb.pack(anchor=tk.W)
        Tooltip(auto_cb, "Automatically open the output file")
        
        btn_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        
        gen_btn = ttk.Button(btn_frame, text="Generate Video", command=self.px_generate, style="Accent.TButton")
        gen_btn.pack(side=tk.LEFT)
        Tooltip(gen_btn, "Create the dialogue video")
        
        preview_btn = ttk.Button(btn_frame, text="Preview Info", command=self.px_dry_run, style="Secondary.TButton")
        preview_btn.pack(side=tk.LEFT, padx=(8, 0))
        Tooltip(preview_btn, "Show estimated duration without rendering")
        
        save_btn = ttk.Button(btn_frame, text="Save Config", command=self.px_save_config, style="Secondary.TButton")
        save_btn.pack(side=tk.RIGHT)
        Tooltip(save_btn, "Save current settings to config.json")
        
        load_btn = ttk.Button(btn_frame, text="Load Config", command=self.px_load_config, style="Secondary.TButton")
        load_btn.pack(side=tk.RIGHT, padx=(0, 8))
        Tooltip(load_btn, "Load settings from config.json")
    
    def setup_gradient_tab(self):
        canvas = tk.Canvas(self.gradient_frame, bg=ModernStyle.BG_MEDIUM, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.gradient_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        files_frame = ttk.LabelFrame(scrollable_frame, text="Files", style="Card.TLabelframe", padding=12)
        files_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.gr_input_var = tk.StringVar(value="dialogue.txt")
        self.gr_font_var = tk.StringVar()
        self.gr_bgimage_var = tk.StringVar()
        self.gr_output_var = tk.StringVar()
        
        self.create_file_row(files_frame, "Text File:", self.gr_input_var, [("Text", "*.txt")], 0,
                            tooltip="Your dialogue text file")
        self.create_file_row(files_frame, "Output:", self.gr_output_var, None, 1,
                            tooltip="Output filename (leave empty for auto)")
        
        quick_frame = ttk.LabelFrame(scrollable_frame, text="Quick Settings", style="Card.TLabelframe", padding=12)
        quick_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.gr_width_var = tk.IntVar(value=800)
        self.gr_height_var = tk.IntVar(value=200)
        self.gr_padding_var = tk.IntVar(value=20)
        self.gr_fontsize_var = tk.IntVar(value=32)
        self.gr_fps_var = tk.IntVar(value=30)
        self.gr_dwell_var = tk.DoubleVar(value=2.0)
        
        quick_grid = ttk.Frame(quick_frame, style="Card.TFrame")
        quick_grid.pack(fill=tk.X)
        
        self.create_spinbox_row(quick_grid, "Font Size:", self.gr_fontsize_var, 16, 72, 0, 0,
                               tooltip="Text size in pixels")
        self.create_spinbox_row(quick_grid, "Box Height:", self.gr_height_var, 100, 500, 0, 2,
                               tooltip="Dialogue box height")
        
        gradient_row = ttk.Frame(quick_frame, style="Card.TFrame")
        gradient_row.pack(fill=tk.X, pady=(8, 0))
        
        self.gr_direction_var = tk.StringVar(value="vertical")
        self.gr_topcolor = [255, 255, 255, 255]
        self.gr_bottomcolor = [180, 180, 180, 255]
        self.gr_textcolor = [0, 0, 0, 255]
        
        ttk.Label(gradient_row, text="Direction:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        dir_combo = ttk.Combobox(gradient_row, textvariable=self.gr_direction_var, 
                                values=["vertical", "horizontal", "none"], width=10, state="readonly")
        dir_combo.pack(side=tk.LEFT, padx=(0, 15))
        dir_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        Tooltip(dir_combo, "Gradient direction (or solid color)")
        
        ttk.Label(gradient_row, text="Top:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.gr_topcolor_btn = tk.Button(gradient_row, text="", bg="#ffffff", width=3, height=1,
                                        relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("gr_top"))
        self.gr_topcolor_btn.pack(side=tk.LEFT, padx=(0, 10))
        Tooltip(self.gr_topcolor_btn, "Top/left gradient color")
        
        ttk.Label(gradient_row, text="Bottom:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.gr_bottomcolor_btn = tk.Button(gradient_row, text="", bg="#b4b4b4", width=3, height=1,
                                           relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("gr_bottom"))
        self.gr_bottomcolor_btn.pack(side=tk.LEFT, padx=(0, 10))
        Tooltip(self.gr_bottomcolor_btn, "Bottom/right gradient color")
        
        ttk.Label(gradient_row, text="Text:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.gr_textcolor_btn = tk.Button(gradient_row, text="", bg="#000000", width=3, height=1,
                                         relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("gr_text"))
        self.gr_textcolor_btn.pack(side=tk.LEFT)
        Tooltip(self.gr_textcolor_btn, "Text color")
        
        advanced = CollapsibleFrame(scrollable_frame, "Advanced Options", collapsed=True)
        advanced.pack(fill=tk.X, pady=(0, 8))
        
        adv_files = ttk.Frame(advanced.content, style="Card.TFrame")
        adv_files.pack(fill=tk.X)
        
        self.create_file_row(adv_files, "Font:", self.gr_font_var, [("Fonts", "*.ttf *.otf")], 0,
                            auto_ext=(".ttf", ".otf"), tooltip="Custom font file")
        self.create_file_row(adv_files, "BG Image:", self.gr_bgimage_var, [("Images", "*.png *.jpg")], 1,
                            tooltip="Background image (overrides gradient)")
        
        adv_settings = ttk.Frame(advanced.content, style="Card.TFrame")
        adv_settings.pack(fill=tk.X, pady=(8, 0))
        
        self.create_spinbox_row(adv_settings, "Width:", self.gr_width_var, 400, 1920, 0, 0,
                               tooltip="Box width in pixels")
        self.create_spinbox_row(adv_settings, "Padding:", self.gr_padding_var, 5, 50, 0, 2,
                               tooltip="Space inside box")
        self.create_spinbox_row(adv_settings, "FPS:", self.gr_fps_var, 15, 60, 1, 0,
                               tooltip="Video frame rate")
        self.create_spinbox_row(adv_settings, "Dwell:", self.gr_dwell_var, 0, 10, 1, 2, increment=0.5,
                               tooltip="Pause after text (seconds)")
        
        export = CollapsibleFrame(scrollable_frame, "Export Options", collapsed=True)
        export.pack(fill=tk.X, pady=(0, 8))
        
        self.gr_format_var = tk.StringVar(value="webm")
        self.gr_autoopen_var = tk.BooleanVar(value=True)
        
        format_row = ttk.Frame(export.content, style="Card.TFrame")
        format_row.pack(fill=tk.X)
        
        ttk.Label(format_row, text="Format:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        format_combo = ttk.Combobox(format_row, textvariable=self.gr_format_var, 
                                   values=["webm", "mp4", "gif"], width=8, state="readonly")
        format_combo.pack(side=tk.LEFT)
        Tooltip(format_combo, "Output video format")
        
        auto_cb = ttk.Checkbutton(export.content, text="Open when done", variable=self.gr_autoopen_var, style="TCheckbutton")
        auto_cb.pack(anchor=tk.W, pady=(5, 0))
        Tooltip(auto_cb, "Automatically open the output file")
        
        btn_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        
        gen_btn = ttk.Button(btn_frame, text="Generate Video", command=self.gr_generate, style="Accent.TButton")
        gen_btn.pack(side=tk.LEFT)
        Tooltip(gen_btn, "Create the dialogue video")
        
        preview_btn = ttk.Button(btn_frame, text="Preview Info", command=self.gr_dry_run, style="Secondary.TButton")
        preview_btn.pack(side=tk.LEFT, padx=(8, 0))
        Tooltip(preview_btn, "Show estimated duration")
        
        save_btn = ttk.Button(btn_frame, text="Save Config", command=self.gr_save_config, style="Secondary.TButton")
        save_btn.pack(side=tk.RIGHT)
        Tooltip(save_btn, "Save to gradient_config.json")
        
        load_btn = ttk.Button(btn_frame, text="Load Config", command=self.gr_load_config, style="Secondary.TButton")
        load_btn.pack(side=tk.RIGHT, padx=(0, 8))
        Tooltip(load_btn, "Load from gradient_config.json")
    
    def setup_batch_tab(self):
        header_label = ttk.Label(self.batch_frame, 
                                text="Process multiple dialogue files at once",
                                style="Card.TLabel",
                                font=("Segoe UI", 10))
        header_label.pack(pady=(0, 12))
        
        pattern_frame = ttk.LabelFrame(self.batch_frame, text="Batch Settings", style="Card.TLabelframe", padding=12)
        pattern_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.batch_pattern_var = tk.StringVar(value="*.txt")
        self.batch_gen_var = tk.StringVar(value="generate")
        
        pattern_row = ttk.Frame(pattern_frame, style="Card.TFrame")
        pattern_row.pack(fill=tk.X, pady=4)
        
        pattern_lbl = ttk.Label(pattern_row, text="File Pattern:", style="Card.TLabel")
        pattern_lbl.pack(side=tk.LEFT, padx=(0, 8))
        Tooltip(pattern_lbl, "Glob pattern to match files (e.g., *.txt, dialogues/*.txt)")
        
        ttk.Entry(pattern_row, textvariable=self.batch_pattern_var, width=30).pack(side=tk.LEFT)
        
        gen_row = ttk.Frame(pattern_frame, style="Card.TFrame")
        gen_row.pack(fill=tk.X, pady=4)
        
        gen_lbl = ttk.Label(gen_row, text="Generator:", style="Card.TLabel")
        gen_lbl.pack(side=tk.LEFT, padx=(0, 8))
        Tooltip(gen_lbl, "Which generator to use for batch processing")
        
        gen_combo = ttk.Combobox(gen_row, textvariable=self.batch_gen_var, 
                    values=["generate", "gradient"], width=27, state="readonly")
        gen_combo.pack(side=tk.LEFT)
        
        run_btn = ttk.Button(self.batch_frame, text="Run Batch Processing", 
                  command=self.run_batch, style="Accent.TButton")
        run_btn.pack(pady=12)
        Tooltip(run_btn, "Process all matching files")
        
        output_frame = ttk.LabelFrame(self.batch_frame, text="Output", style="Card.TLabelframe", padding=8)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.batch_output = tk.Text(
            output_frame, 
            height=10,
            bg=ModernStyle.BG_LIGHT,
            fg=ModernStyle.TEXT,
            font=self.mono_font,
            relief=tk.FLAT,
            padx=8,
            pady=8
        )
        self.batch_output.pack(fill=tk.BOTH, expand=True)
    
    def setup_status_bar(self, parent):
        status_frame = ttk.Frame(parent, style="Card.TFrame", padding=6)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
        status_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(status_frame, text="v2.1", style="Status.TLabel")
        version_label.pack(side=tk.RIGHT)
    
    def create_file_row(self, parent, label, var, filetypes, row, auto_ext=None, tooltip=None):
        lbl = ttk.Label(parent, text=label, style="Card.TLabel")
        lbl.grid(row=row, column=0, sticky=tk.W, pady=4)
        entry = ttk.Entry(parent, textvariable=var, width=35)
        entry.grid(row=row, column=1, padx=8, pady=4)
        
        if tooltip:
            Tooltip(lbl, tooltip)
            Tooltip(entry, tooltip)
        
        if filetypes:
            btn = ttk.Button(parent, text="...", style="Secondary.TButton", width=3,
                      command=lambda: self.browse_file(var, filetypes))
            btn.grid(row=row, column=2, padx=2)
            Tooltip(btn, "Browse")
        
        if auto_ext:
            auto_btn = ttk.Button(parent, text="Auto", style="Secondary.TButton",
                      command=lambda: self.auto_find(var, auto_ext))
            auto_btn.grid(row=row, column=3, padx=2)
            Tooltip(auto_btn, "Auto-detect file")
        
        return entry
    
    def create_spinbox_row(self, parent, label, var, from_, to, row, col, increment=1, tooltip=None):
        lbl = ttk.Label(parent, text=label, style="Card.TLabel")
        lbl.grid(row=row, column=col, sticky=tk.W, pady=6, padx=(0 if col == 0 else 20, 4))
        spinbox = ttk.Spinbox(parent, from_=from_, to=to, textvariable=var, width=8, increment=increment)
        spinbox.grid(row=row, column=col+1, pady=6)
        spinbox.bind("<KeyRelease>", lambda e: self.update_preview())
        spinbox.bind("<<Increment>>", lambda e: self.root.after(10, self.update_preview))
        spinbox.bind("<<Decrement>>", lambda e: self.root.after(10, self.update_preview))
        
        if tooltip:
            Tooltip(lbl, tooltip)
            Tooltip(spinbox, tooltip)
        
        return spinbox
    
    def bind_preview_updates(self):
        for var in [self.px_fontsize_var, self.px_padding_var, self.gr_width_var, 
                   self.gr_height_var, self.gr_padding_var, self.gr_fontsize_var]:
            var.trace_add("write", lambda *args: self.root.after(50, self.update_preview))
        
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.update_preview())
    
    def update_preview(self):
        self.preview_canvas.delete("all")
        
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            return
        
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:
            self.draw_pixel_preview(canvas_width, canvas_height)
        elif current_tab == 1:
            self.draw_gradient_preview(canvas_width, canvas_height)
        else:
            self.draw_batch_preview(canvas_width, canvas_height)
    
    def draw_pixel_preview(self, canvas_width, canvas_height):
        bg_hex = "#{:02x}{:02x}{:02x}".format(*self.px_bgcolor[:3])
        text_hex = "#{:02x}{:02x}{:02x}".format(*self.px_textcolor[:3])
        
        padding = 15
        box_width = canvas_width - padding * 2
        box_height = canvas_height - padding * 2
        
        self.preview_canvas.create_rectangle(
            padding, padding, 
            canvas_width - padding, canvas_height - padding,
            fill=bg_hex, outline=ModernStyle.ACCENT, width=2
        )
        
        preview_text = self.preview_text.get("1.0", "end-1c")
        lines = preview_text.split("\n")[:4]
        
        font_size = max(10, min(self.px_fontsize_var.get(), 28))
        text_padding = min(self.px_padding_var.get(), 20)
        
        y_pos = padding + text_padding + 8
        for line in lines:
            self.preview_canvas.create_text(
                padding + text_padding + 8, y_pos,
                text=line[:60],
                fill=text_hex,
                anchor=tk.NW,
                font=("Consolas", font_size)
            )
            y_pos += font_size + 6
        
        self.preview_info_var.set(f"Pixel-Perfect | {self.px_fontsize_var.get()}px | Speed: {self.px_charspeed_var.get()}")
    
    def draw_gradient_preview(self, canvas_width, canvas_height):
        padding = 15
        box_width = canvas_width - padding * 2
        box_height = canvas_height - padding * 2
        
        direction = self.gr_direction_var.get()
        top_color = self.gr_topcolor[:3]
        bottom_color = self.gr_bottomcolor[:3]
        
        if direction == "none":
            hex_color = "#{:02x}{:02x}{:02x}".format(*top_color)
            self.preview_canvas.create_rectangle(
                padding, padding,
                canvas_width - padding, canvas_height - padding,
                fill=hex_color, outline=ModernStyle.ACCENT, width=2
            )
        else:
            steps = 40
            if direction == "vertical":
                step_height = box_height / steps
                for i in range(steps):
                    t = i / steps
                    r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
                    g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
                    b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
                    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
                    
                    y1 = padding + i * step_height
                    y2 = padding + (i + 1) * step_height
                    self.preview_canvas.create_rectangle(
                        padding, y1, canvas_width - padding, y2,
                        fill=hex_color, outline=""
                    )
            else:
                step_width = box_width / steps
                for i in range(steps):
                    t = i / steps
                    r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
                    g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
                    b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
                    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
                    
                    x1 = padding + i * step_width
                    x2 = padding + (i + 1) * step_width
                    self.preview_canvas.create_rectangle(
                        x1, padding, x2, canvas_height - padding,
                        fill=hex_color, outline=""
                    )
        
        self.preview_canvas.create_rectangle(
            padding, padding,
            canvas_width - padding, canvas_height - padding,
            fill="", outline=ModernStyle.ACCENT, width=2
        )
        
        text_hex = "#{:02x}{:02x}{:02x}".format(*self.gr_textcolor[:3])
        preview_text = self.preview_text.get("1.0", "end-1c")
        lines = preview_text.split("\n")[:4]
        
        font_size = max(10, min(self.gr_fontsize_var.get(), 28))
        text_padding = min(self.gr_padding_var.get(), 20)
        
        y_pos = padding + text_padding + 8
        for line in lines:
            self.preview_canvas.create_text(
                padding + text_padding + 8, y_pos,
                text=line[:60],
                fill=text_hex,
                anchor=tk.NW,
                font=("Consolas", font_size)
            )
            y_pos += font_size + 6
        
        self.preview_info_var.set(f"Gradient ({direction}) | {self.gr_width_var.get()}x{self.gr_height_var.get()} | {self.gr_fontsize_var.get()}px")
    
    def draw_batch_preview(self, canvas_width, canvas_height):
        self.preview_canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text="Batch mode\nSelect files and run",
            fill=ModernStyle.TEXT_DIM,
            font=("Segoe UI", 12),
            justify=tk.CENTER
        )
        self.preview_info_var.set("Batch processing mode")
    
    def browse_file(self, var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            var.set(path)
            self.update_preview()
    
    def auto_find(self, var, extensions):
        for f in os.listdir("."):
            if f.lower().endswith(extensions):
                var.set(f)
                self.update_preview()
                return
        messagebox.showinfo("Not Found", f"No {extensions[0]} file found")
    
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
            
            self.update_preview()
    
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
            messagebox.showinfo("Complete", output or "Generated successfully!")
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
        self.status_var.set("Config saved")
        messagebox.showinfo("Saved", "Settings saved to config.json")
    
    def px_load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)
            self.px_maxwidth_var.set(config.get("max_text_width", 800))
            self.px_padding_var.set(config.get("padding", 15))
            self.px_fontsize_var.set(config.get("font_size", 24))
            self.px_fps_var.set(config.get("fps", 30))
            self.px_charspeed_var.set(config.get("char_speed", 2))
            self.px_dwell_var.set(config.get("video_duration_sec_after_text", 2))
            if "text_color" in config:
                self.px_textcolor = config["text_color"]
                self.px_textcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.px_textcolor[:3]))
            if "bg_color" in config:
                self.px_bgcolor = config["bg_color"]
                self.px_bgcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.px_bgcolor[:3]))
            self.px_gif_var.set(config.get("export_gif", False))
            self.px_autoopen_var.set(config.get("auto_open", True))
            self.update_preview()
            self.status_var.set("Config loaded")
            messagebox.showinfo("Loaded", "Settings loaded from config.json")
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
        self.status_var.set("Config saved")
        messagebox.showinfo("Saved", "Settings saved to gradient_config.json")
    
    def gr_load_config(self):
        if os.path.exists("gradient_config.json"):
            with open("gradient_config.json", "r") as f:
                config = json.load(f)
            if "box_size" in config:
                self.gr_width_var.set(config["box_size"][0])
                self.gr_height_var.set(config["box_size"][1])
            self.gr_padding_var.set(config.get("padding", 20))
            self.gr_fontsize_var.set(config.get("font_size", 32))
            self.gr_fps_var.set(config.get("fps", 30))
            self.gr_dwell_var.set(config.get("dwell_time", 2))
            self.gr_direction_var.set(config.get("gradient_direction", "vertical"))
            if "top_color" in config:
                self.gr_topcolor = config["top_color"]
                self.gr_topcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.gr_topcolor[:3]))
            if "bottom_color" in config:
                self.gr_bottomcolor = config["bottom_color"]
                self.gr_bottomcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.gr_bottomcolor[:3]))
            if "text_color" in config:
                self.gr_textcolor = config["text_color"]
                self.gr_textcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.gr_textcolor[:3]))
            self.gr_format_var.set(config.get("output_format", "webm"))
            self.gr_autoopen_var.set(config.get("auto_open", True))
            self.update_preview()
            self.status_var.set("Config loaded")
            messagebox.showinfo("Loaded", "Settings loaded from gradient_config.json")
        else:
            messagebox.showwarning("Not Found", "gradient_config.json not found")


def main():
    root = tk.Tk()
    app = DialogueGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
