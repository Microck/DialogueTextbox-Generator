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
    

class DialogueGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✦ Dialogue Textbox Generator")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 700)
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
        
        right_panel = ttk.Frame(content_frame, style="Dark.TFrame", width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_panel.pack_propagate(False)
        
        self.notebook = ttk.Notebook(left_panel, style="Dark.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.pixel_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.gradient_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.batch_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        
        self.notebook.add(self.pixel_frame, text="  ⬛ Pixel-Perfect  ")
        self.notebook.add(self.gradient_frame, text="  🌈 Gradient  ")
        self.notebook.add(self.batch_frame, text="  📁 Batch  ")
        
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
                           font=("Segoe UI", 18, "bold"))
        self.style.configure("SubHeader.TLabel", 
                           background=ModernStyle.BG_DARK, 
                           foreground=ModernStyle.TEXT_DIM,
                           font=("Segoe UI", 10))
        self.style.configure("Preview.TLabel", 
                           background=ModernStyle.BG_LIGHT, 
                           foreground=ModernStyle.TEXT,
                           font=("Segoe UI", 11, "bold"))
        
        self.style.configure("Dark.TNotebook", background=ModernStyle.BG_DARK)
        self.style.configure("Dark.TNotebook.Tab", 
                           background=ModernStyle.BG_MEDIUM,
                           foreground=ModernStyle.TEXT,
                           padding=[15, 8],
                           font=("Segoe UI", 10))
        self.style.map("Dark.TNotebook.Tab",
                      background=[("selected", ModernStyle.BG_LIGHT)],
                      foreground=[("selected", ModernStyle.TEXT)])
        
        self.style.configure("Card.TLabelframe", 
                           background=ModernStyle.BG_MEDIUM,
                           foreground=ModernStyle.TEXT)
        self.style.configure("Card.TLabelframe.Label", 
                           background=ModernStyle.BG_MEDIUM,
                           foreground=ModernStyle.ACCENT,
                           font=("Segoe UI", 10, "bold"))
        
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
                           padding=[10, 5])
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
        self.header_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.label_font = tkfont.Font(family="Segoe UI", size=10)
        self.mono_font = tkfont.Font(family="Consolas", size=10)
    
    def setup_header(self, parent):
        header_frame = ttk.Frame(parent, style="Dark.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_label = ttk.Label(header_frame, 
                               text="Dialogue Textbox Generator",
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame,
                                  text="Create Undertale-style dialogue animations",
                                  style="SubHeader.TLabel")
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0), pady=(8, 0))
    
    def setup_preview_panel(self, parent):
        preview_label = ttk.Label(parent, text="👁 LIVE PREVIEW", style="Preview.TLabel")
        preview_label.pack(fill=tk.X, pady=(0, 10))
        
        preview_container = ttk.Frame(parent, style="Preview.TFrame", padding=10)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview_canvas = tk.Canvas(
            preview_container,
            bg="#000000",
            highlightthickness=2,
            highlightbackground=ModernStyle.ACCENT
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        info_frame = ttk.Frame(parent, style="Dark.TFrame")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.preview_info_var = tk.StringVar(value="Preview will update as you change settings")
        info_label = ttk.Label(info_frame, 
                              textvariable=self.preview_info_var,
                              style="Status.TLabel")
        info_label.pack()
        
        text_frame = ttk.Frame(parent, style="Dark.TFrame")
        text_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(text_frame, text="Preview Text:", style="Dark.TLabel").pack(anchor=tk.W)
        
        self.preview_text_var = tk.StringVar(value="* Hello, world!\n* This is a preview.")
        self.preview_text = tk.Text(
            text_frame, 
            height=4, 
            bg=ModernStyle.BG_LIGHT,
            fg=ModernStyle.TEXT,
            insertbackground=ModernStyle.TEXT,
            font=self.mono_font,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.preview_text.pack(fill=tk.X, pady=(5, 0))
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
        
        files_frame = ttk.LabelFrame(scrollable_frame, text="📂 Files", style="Card.TLabelframe", padding=15)
        files_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.px_input_var = tk.StringVar(value="dialogue.txt")
        self.px_font_var = tk.StringVar()
        self.px_portrait_var = tk.StringVar()
        self.px_output_var = tk.StringVar(value="dialogue.mp4")
        self.px_sound_var = tk.StringVar()
        
        self.create_file_row(files_frame, "Text File:", self.px_input_var, [("Text", "*.txt")], 0)
        self.create_file_row(files_frame, "Font:", self.px_font_var, [("Fonts", "*.ttf *.otf")], 1, auto_ext=(".ttf", ".otf"))
        self.create_file_row(files_frame, "Portrait:", self.px_portrait_var, [("Images", "*.png *.jpg *.jpeg *.bmp")], 2, auto_ext=(".png", ".jpg", ".jpeg", ".bmp"))
        self.create_file_row(files_frame, "Output:", self.px_output_var, None, 3)
        self.create_file_row(files_frame, "Sound:", self.px_sound_var, [("Audio", "*.wav *.ogg *.mp3")], 4)
        
        settings_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Settings", style="Card.TLabelframe", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.px_fontsize_var = tk.IntVar(value=20)
        self.px_maxwidth_var = tk.IntVar(value=1000)
        self.px_padding_var = tk.IntVar(value=10)
        self.px_fps_var = tk.IntVar(value=30)
        self.px_charspeed_var = tk.IntVar(value=1)
        self.px_dwell_var = tk.DoubleVar(value=2.0)
        
        settings_grid = ttk.Frame(settings_frame, style="Card.TFrame")
        settings_grid.pack(fill=tk.X)
        
        self.create_spinbox_row(settings_grid, "Font Size:", self.px_fontsize_var, 8, 100, 0, 0)
        self.create_spinbox_row(settings_grid, "Max Width:", self.px_maxwidth_var, 100, 4000, 0, 2)
        self.create_spinbox_row(settings_grid, "Padding:", self.px_padding_var, 0, 100, 1, 0)
        self.create_spinbox_row(settings_grid, "FPS:", self.px_fps_var, 1, 60, 1, 2)
        self.create_spinbox_row(settings_grid, "Char Speed:", self.px_charspeed_var, 1, 30, 2, 0)
        self.create_spinbox_row(settings_grid, "Dwell (sec):", self.px_dwell_var, 0, 30, 2, 2, increment=0.5)
        
        colors_frame = ttk.LabelFrame(scrollable_frame, text="🎨 Colors", style="Card.TLabelframe", padding=15)
        colors_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.px_textcolor = [255, 255, 255]
        self.px_bgcolor = [0, 0, 0]
        
        colors_grid = ttk.Frame(colors_frame, style="Card.TFrame")
        colors_grid.pack(fill=tk.X)
        
        ttk.Label(colors_grid, text="Text:", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.px_textcolor_btn = tk.Button(
            colors_grid, 
            text="", 
            bg="#ffffff",
            width=8,
            height=1,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.pick_color("px_text")
        )
        self.px_textcolor_btn.grid(row=0, column=1, padx=(0, 30))
        
        ttk.Label(colors_grid, text="Background:", style="Card.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.px_bgcolor_btn = tk.Button(
            colors_grid, 
            text="", 
            bg="#000000",
            width=8,
            height=1,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.pick_color("px_bg")
        )
        self.px_bgcolor_btn.grid(row=0, column=3)
        
        options_frame = ttk.LabelFrame(scrollable_frame, text="📦 Export Options", style="Card.TLabelframe", padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.px_gif_var = tk.BooleanVar(value=False)
        self.px_gifonly_var = tk.BooleanVar(value=False)
        self.px_autoopen_var = tk.BooleanVar(value=False)
        
        opts_grid = ttk.Frame(options_frame, style="Card.TFrame")
        opts_grid.pack(fill=tk.X)
        
        ttk.Checkbutton(opts_grid, text="Export GIF", variable=self.px_gif_var, style="TCheckbutton").grid(row=0, column=0, padx=(0, 20))
        ttk.Checkbutton(opts_grid, text="GIF Only", variable=self.px_gifonly_var, style="TCheckbutton").grid(row=0, column=1, padx=(0, 20))
        ttk.Checkbutton(opts_grid, text="Auto Open", variable=self.px_autoopen_var, style="TCheckbutton").grid(row=0, column=2)
        
        btn_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="🔍 Preview Info", command=self.px_dry_run, style="Secondary.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="🎬 Generate Video", command=self.px_generate, style="Accent.TButton").pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="💾 Save", command=self.px_save_config, style="Secondary.TButton").pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="📂 Load", command=self.px_load_config, style="Secondary.TButton").pack(side=tk.RIGHT)
    
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
        
        files_frame = ttk.LabelFrame(scrollable_frame, text="📂 Files", style="Card.TLabelframe", padding=15)
        files_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.gr_input_var = tk.StringVar(value="dialogue.txt")
        self.gr_font_var = tk.StringVar()
        self.gr_bgimage_var = tk.StringVar()
        self.gr_output_var = tk.StringVar()
        
        self.create_file_row(files_frame, "Text File:", self.gr_input_var, [("Text", "*.txt")], 0)
        self.create_file_row(files_frame, "Font:", self.gr_font_var, [("Fonts", "*.ttf *.otf")], 1, auto_ext=(".ttf", ".otf"))
        self.create_file_row(files_frame, "BG Image:", self.gr_bgimage_var, [("Images", "*.png *.jpg *.jpeg")], 2)
        self.create_file_row(files_frame, "Output:", self.gr_output_var, None, 3)
        
        settings_frame = ttk.LabelFrame(scrollable_frame, text="📐 Box Settings", style="Card.TLabelframe", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.gr_width_var = tk.IntVar(value=1000)
        self.gr_height_var = tk.IntVar(value=209)
        self.gr_padding_var = tk.IntVar(value=20)
        self.gr_fontsize_var = tk.IntVar(value=35)
        self.gr_fps_var = tk.IntVar(value=30)
        self.gr_dwell_var = tk.DoubleVar(value=3.0)
        
        settings_grid = ttk.Frame(settings_frame, style="Card.TFrame")
        settings_grid.pack(fill=tk.X)
        
        self.create_spinbox_row(settings_grid, "Width:", self.gr_width_var, 100, 4000, 0, 0)
        self.create_spinbox_row(settings_grid, "Height:", self.gr_height_var, 50, 2000, 0, 2)
        self.create_spinbox_row(settings_grid, "Padding:", self.gr_padding_var, 0, 100, 1, 0)
        self.create_spinbox_row(settings_grid, "Font Size:", self.gr_fontsize_var, 8, 100, 1, 2)
        self.create_spinbox_row(settings_grid, "FPS:", self.gr_fps_var, 1, 60, 2, 0)
        self.create_spinbox_row(settings_grid, "Dwell (sec):", self.gr_dwell_var, 0, 30, 2, 2, increment=0.5)
        
        gradient_frame = ttk.LabelFrame(scrollable_frame, text="🌈 Gradient", style="Card.TLabelframe", padding=15)
        gradient_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.gr_direction_var = tk.StringVar(value="vertical")
        self.gr_topcolor = [255, 255, 255, 255]
        self.gr_bottomcolor = [121, 121, 121, 255]
        self.gr_textcolor = [0, 0, 0, 255]
        
        dir_frame = ttk.Frame(gradient_frame, style="Card.TFrame")
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(dir_frame, text="Direction:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        dir_combo = ttk.Combobox(dir_frame, textvariable=self.gr_direction_var, 
                                values=["vertical", "horizontal", "none"], width=12, state="readonly")
        dir_combo.pack(side=tk.LEFT)
        dir_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        
        colors_grid = ttk.Frame(gradient_frame, style="Card.TFrame")
        colors_grid.pack(fill=tk.X)
        
        ttk.Label(colors_grid, text="Top/Left:", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.gr_topcolor_btn = tk.Button(colors_grid, text="", bg="#ffffff", width=6, height=1,
                                        relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("gr_top"))
        self.gr_topcolor_btn.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(colors_grid, text="Bottom/Right:", style="Card.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.gr_bottomcolor_btn = tk.Button(colors_grid, text="", bg="#797979", width=6, height=1,
                                           relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("gr_bottom"))
        self.gr_bottomcolor_btn.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(colors_grid, text="Text:", style="Card.TLabel").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.gr_textcolor_btn = tk.Button(colors_grid, text="", bg="#000000", width=6, height=1,
                                         relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("gr_text"))
        self.gr_textcolor_btn.grid(row=0, column=5)
        
        options_frame = ttk.LabelFrame(scrollable_frame, text="📦 Export Options", style="Card.TLabelframe", padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.gr_format_var = tk.StringVar(value="webm")
        self.gr_autoopen_var = tk.BooleanVar(value=False)
        
        opts_grid = ttk.Frame(options_frame, style="Card.TFrame")
        opts_grid.pack(fill=tk.X)
        
        ttk.Label(opts_grid, text="Format:", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        format_combo = ttk.Combobox(opts_grid, textvariable=self.gr_format_var, 
                                   values=["webm", "mp4", "gif"], width=10, state="readonly")
        format_combo.grid(row=0, column=1, padx=(0, 30))
        
        ttk.Checkbutton(opts_grid, text="Auto Open", variable=self.gr_autoopen_var, style="TCheckbutton").grid(row=0, column=2)
        
        btn_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="🔍 Preview Info", command=self.gr_dry_run, style="Secondary.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="🎬 Generate Video", command=self.gr_generate, style="Accent.TButton").pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="💾 Save", command=self.gr_save_config, style="Secondary.TButton").pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="📂 Load", command=self.gr_load_config, style="Secondary.TButton").pack(side=tk.RIGHT)
    
    def setup_batch_tab(self):
        header_label = ttk.Label(self.batch_frame, 
                                text="Process multiple dialogue files at once",
                                style="Card.TLabel",
                                font=("Segoe UI", 11))
        header_label.pack(pady=(0, 15))
        
        pattern_frame = ttk.LabelFrame(self.batch_frame, text="📁 Batch Settings", style="Card.TLabelframe", padding=15)
        pattern_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.batch_pattern_var = tk.StringVar(value="*.txt")
        self.batch_gen_var = tk.StringVar(value="generate")
        
        ttk.Label(pattern_frame, text="File Pattern:", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(pattern_frame, textvariable=self.batch_pattern_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(pattern_frame, text="Generator:", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(pattern_frame, textvariable=self.batch_gen_var, 
                    values=["generate", "gradient"], width=37, state="readonly").grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Button(self.batch_frame, text="🚀 Run Batch Processing", 
                  command=self.run_batch, style="Accent.TButton").pack(pady=15)
        
        output_frame = ttk.LabelFrame(self.batch_frame, text="📋 Output", style="Card.TLabelframe", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.batch_output = tk.Text(
            output_frame, 
            height=12,
            bg=ModernStyle.BG_LIGHT,
            fg=ModernStyle.TEXT,
            font=self.mono_font,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.batch_output.pack(fill=tk.BOTH, expand=True)
    
    def setup_status_bar(self, parent):
        status_frame = ttk.Frame(parent, style="Card.TFrame", padding=8)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="✓ Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
        status_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(status_frame, text="v2.0", style="Status.TLabel")
        version_label.pack(side=tk.RIGHT)
    
    def create_file_row(self, parent, label, var, filetypes, row, auto_ext=None):
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=var, width=45).grid(row=row, column=1, padx=10, pady=5)
        
        if filetypes:
            ttk.Button(parent, text="Browse", style="Secondary.TButton",
                      command=lambda: self.browse_file(var, filetypes)).grid(row=row, column=2, padx=2)
        
        if auto_ext:
            ttk.Button(parent, text="Auto", style="Secondary.TButton",
                      command=lambda: self.auto_find(var, auto_ext)).grid(row=row, column=3, padx=2)
    
    def create_spinbox_row(self, parent, label, var, from_, to, row, col, increment=1):
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row, column=col, sticky=tk.W, pady=8, padx=(0 if col == 0 else 30, 5))
        spinbox = ttk.Spinbox(parent, from_=from_, to=to, textvariable=var, width=10, increment=increment)
        spinbox.grid(row=row, column=col+1, pady=8)
        spinbox.bind("<KeyRelease>", lambda e: self.update_preview())
        spinbox.bind("<<Increment>>", lambda e: self.root.after(10, self.update_preview))
        spinbox.bind("<<Decrement>>", lambda e: self.root.after(10, self.update_preview))
    
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
        else:
            self.draw_gradient_preview(canvas_width, canvas_height)
    
    def draw_pixel_preview(self, canvas_width, canvas_height):
        bg_hex = "#{:02x}{:02x}{:02x}".format(*self.px_bgcolor[:3])
        text_hex = "#{:02x}{:02x}{:02x}".format(*self.px_textcolor[:3])
        
        padding = 20
        box_width = canvas_width - padding * 2
        box_height = canvas_height - padding * 2
        
        self.preview_canvas.create_rectangle(
            padding, padding, 
            canvas_width - padding, canvas_height - padding,
            fill=bg_hex, outline=ModernStyle.ACCENT, width=2
        )
        
        preview_text = self.preview_text.get("1.0", "end-1c")
        lines = preview_text.split("\n")[:4]
        
        font_size = max(8, min(self.px_fontsize_var.get(), 24))
        text_padding = self.px_padding_var.get()
        
        y_pos = padding + text_padding + 10
        for line in lines:
            self.preview_canvas.create_text(
                padding + text_padding + 10, y_pos,
                text=line[:50],
                fill=text_hex,
                anchor=tk.NW,
                font=("Consolas", font_size)
            )
            y_pos += font_size + 8
        
        self.preview_info_var.set(f"Pixel-Perfect Mode | Font: {self.px_fontsize_var.get()}px | Padding: {self.px_padding_var.get()}px")
    
    def draw_gradient_preview(self, canvas_width, canvas_height):
        padding = 20
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
            steps = 50
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
        
        font_size = max(8, min(self.gr_fontsize_var.get(), 24))
        text_padding = self.gr_padding_var.get()
        
        y_pos = padding + text_padding + 10
        for line in lines:
            self.preview_canvas.create_text(
                padding + text_padding + 10, y_pos,
                text=line[:50],
                fill=text_hex,
                anchor=tk.NW,
                font=("Consolas", font_size)
            )
            y_pos += font_size + 8
        
        self.preview_info_var.set(f"Gradient Mode ({direction}) | {self.gr_width_var.get()}x{self.gr_height_var.get()} | Font: {self.gr_fontsize_var.get()}px")
    
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
            self.status_var.set("⏳ Running...")
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
        self.status_var.set("✓ Done" if success else "✗ Error")
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
            self.status_var.set("✓ Batch complete" if success else "✗ Batch failed")
        
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
        self.status_var.set("✓ Config saved")
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
                self.px_textcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.px_textcolor[:3]))
            if "bg_color" in config:
                self.px_bgcolor = config["bg_color"]
                self.px_bgcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.px_bgcolor[:3]))
            self.px_gif_var.set(config.get("export_gif", False))
            self.px_autoopen_var.set(config.get("auto_open", False))
            self.update_preview()
            self.status_var.set("✓ Config loaded")
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
        self.status_var.set("✓ Config saved")
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
                self.gr_topcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.gr_topcolor[:3]))
            if "bottom_color" in config:
                self.gr_bottomcolor = config["bottom_color"]
                self.gr_bottomcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.gr_bottomcolor[:3]))
            if "text_color" in config:
                self.gr_textcolor = config["text_color"]
                self.gr_textcolor_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.gr_textcolor[:3]))
            self.gr_format_var.set(config.get("output_format", "webm"))
            self.gr_autoopen_var.set(config.get("auto_open", False))
            self.update_preview()
            self.status_var.set("✓ Config loaded")
            messagebox.showinfo("Loaded", "Config loaded from gradient_config.json")
        else:
            messagebox.showwarning("Not Found", "gradient_config.json not found")


def main():
    root = tk.Tk()
    app = DialogueGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
