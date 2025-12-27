#!/usr/bin/env python3
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import json
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser


class App:
    BG = "#1a1a2e"
    BG2 = "#16213e"
    BG3 = "#0f3460"
    FG = "#e8e8e8"
    FG2 = "#a0a0a0"
    ACCENT = "#e94560"
    
    def __init__(self, root):
        self.root = root
        self.root.title("Dialogue Generator")
        self.root.geometry("750x600")
        self.root.minsize(700, 550)
        self.root.configure(bg=self.BG)
        
        self.setup_styles()
        self.setup_vars()
        self.setup_ui()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.BG)
        style.configure("Card.TFrame", background=self.BG2)
        style.configure("TLabel", background=self.BG, foreground=self.FG)
        style.configure("Card.TLabel", background=self.BG2, foreground=self.FG)
        style.configure("TCheckbutton", background=self.BG2, foreground=self.FG)
        style.configure("TSpinbox", fieldbackground=self.BG3, foreground=self.FG)
        style.configure("TCombobox", fieldbackground=self.BG3, foreground=self.FG)
        style.configure("Accent.TButton", background=self.ACCENT, foreground="#fff")
        style.map("Accent.TButton", background=[("active", "#ff6b6b")])
    
    def setup_vars(self):
        self.input_var = tk.StringVar(value="dialogue.txt")
        self.output_var = tk.StringVar(value="output.mp4")
        self.font_var = tk.StringVar()
        
        self.width_var = tk.IntVar(value=800)
        self.height_var = tk.IntVar(value=200)
        self.fontsize_var = tk.IntVar(value=28)
        self.padding_var = tk.IntVar(value=20)
        self.speed_var = tk.IntVar(value=2)
        
        self.bg_type_var = tk.StringVar(value="solid")
        self.bg_color = [0, 0, 0]
        self.text_color = [255, 255, 255]
        self.grad_top = [255, 255, 255]
        self.grad_bottom = [120, 120, 120]
        self.grad_dir_var = tk.StringVar(value="vertical")
        self.bg_image_var = tk.StringVar()
        
        self.format_var = tk.StringVar(value="mp4")
        self.autoopen_var = tk.BooleanVar(value=True)
    
    def setup_ui(self):
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        title = ttk.Label(main, text="Dialogue Generator", font=("Segoe UI", 18, "bold"))
        title.pack(anchor=tk.W)
        
        settings = ttk.Frame(main, style="Card.TFrame", padding=15)
        settings.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        left = ttk.Frame(settings, style="Card.TFrame")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right = ttk.Frame(settings, style="Card.TFrame")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_left_panel(left)
        self.setup_right_panel(right)
        self.setup_preview(main)
        self.setup_buttons(main)
    
    def setup_left_panel(self, parent):
        ttk.Label(parent, text="OUTPUT", style="Card.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        
        f2 = ttk.Frame(parent, style="Card.TFrame")
        f2.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(f2, text="File:", style="Card.TLabel", width=8).pack(side=tk.LEFT)
        ttk.Entry(f2, textvariable=self.output_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        
        f3 = ttk.Frame(parent, style="Card.TFrame")
        f3.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(f3, text="Font:", style="Card.TLabel", width=8).pack(side=tk.LEFT)
        ttk.Entry(f3, textvariable=self.font_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(f3, text="...", width=3, command=lambda: self.browse(self.font_var, [("Fonts", "*.ttf *.otf")])).pack(side=tk.LEFT)
        
        ttk.Label(parent, text="SIZE", style="Card.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(15, 0))
        
        size_frame = ttk.Frame(parent, style="Card.TFrame")
        size_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(size_frame, text="Width:", style="Card.TLabel").pack(side=tk.LEFT)
        w_spin = ttk.Spinbox(size_frame, from_=200, to=1920, textvariable=self.width_var, width=6)
        w_spin.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(size_frame, text="Height:", style="Card.TLabel").pack(side=tk.LEFT)
        h_spin = ttk.Spinbox(size_frame, from_=50, to=600, textvariable=self.height_var, width=6)
        h_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        text_frame = ttk.Frame(parent, style="Card.TFrame")
        text_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(text_frame, text="Font Size:", style="Card.TLabel").pack(side=tk.LEFT)
        fs_spin = ttk.Spinbox(text_frame, from_=12, to=72, textvariable=self.fontsize_var, width=5)
        fs_spin.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(text_frame, text="Padding:", style="Card.TLabel").pack(side=tk.LEFT)
        p_spin = ttk.Spinbox(text_frame, from_=0, to=50, textvariable=self.padding_var, width=5)
        p_spin.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(text_frame, text="Speed:", style="Card.TLabel").pack(side=tk.LEFT)
        s_spin = ttk.Spinbox(text_frame, from_=1, to=10, textvariable=self.speed_var, width=5)
        s_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(parent, text="FORMAT", style="Card.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(15, 0))
        
        fmt_frame = ttk.Frame(parent, style="Card.TFrame")
        fmt_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(fmt_frame, text="Output:", style="Card.TLabel").pack(side=tk.LEFT)
        fmt_combo = ttk.Combobox(fmt_frame, textvariable=self.format_var, values=["mp4", "webm", "gif"], width=8, state="readonly")
        fmt_combo.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Checkbutton(fmt_frame, text="Open when done", variable=self.autoopen_var).pack(side=tk.LEFT)
    
    def setup_right_panel(self, parent):
        ttk.Label(parent, text="BACKGROUND", style="Card.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        
        type_frame = ttk.Frame(parent, style="Card.TFrame")
        type_frame.pack(fill=tk.X, pady=(5, 0))
        
        for val, txt in [("solid", "Solid"), ("gradient", "Gradient"), ("image", "Image")]:
            rb = ttk.Radiobutton(type_frame, text=txt, value=val, variable=self.bg_type_var)
            rb.pack(side=tk.LEFT, padx=(0, 10))
        
        self.solid_frame = ttk.Frame(parent, style="Card.TFrame")
        self.grad_frame = ttk.Frame(parent, style="Card.TFrame")
        self.image_frame = ttk.Frame(parent, style="Card.TFrame")
        
        sf = ttk.Frame(self.solid_frame, style="Card.TFrame")
        sf.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(sf, text="Background:", style="Card.TLabel").pack(side=tk.LEFT)
        self.bg_btn = tk.Button(sf, text="", bg="#000000", width=4, relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("bg"))
        self.bg_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        gf1 = ttk.Frame(self.grad_frame, style="Card.TFrame")
        gf1.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(gf1, text="Direction:", style="Card.TLabel").pack(side=tk.LEFT)
        ttk.Combobox(gf1, textvariable=self.grad_dir_var, values=["vertical", "horizontal"], width=10, state="readonly").pack(side=tk.LEFT, padx=(5, 0))
        
        gf2 = ttk.Frame(self.grad_frame, style="Card.TFrame")
        gf2.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(gf2, text="Top/Left:", style="Card.TLabel").pack(side=tk.LEFT)
        self.grad_top_btn = tk.Button(gf2, text="", bg="#ffffff", width=4, relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("grad_top"))
        self.grad_top_btn.pack(side=tk.LEFT, padx=(5, 15))
        ttk.Label(gf2, text="Bottom/Right:", style="Card.TLabel").pack(side=tk.LEFT)
        self.grad_bottom_btn = tk.Button(gf2, text="", bg="#787878", width=4, relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("grad_bottom"))
        self.grad_bottom_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        imf = ttk.Frame(self.image_frame, style="Card.TFrame")
        imf.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(imf, text="Image:", style="Card.TLabel").pack(side=tk.LEFT)
        ttk.Entry(imf, textvariable=self.bg_image_var, width=20).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(imf, text="...", width=3, command=lambda: self.browse(self.bg_image_var, [("Images", "*.png *.jpg")])).pack(side=tk.LEFT)
        
        self.solid_frame.pack(fill=tk.X)
        
        ttk.Label(parent, text="TEXT COLOR", style="Card.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(15, 0))
        
        tc_frame = ttk.Frame(parent, style="Card.TFrame")
        tc_frame.pack(fill=tk.X, pady=(5, 0))
        self.text_btn = tk.Button(tc_frame, text="", bg="#ffffff", width=4, relief=tk.FLAT, cursor="hand2", command=lambda: self.pick_color("text"))
        self.text_btn.pack(side=tk.LEFT)
        
        self.bg_type_var.trace_add("write", lambda *a: self.switch_bg_type())
    
    def switch_bg_type(self):
        self.solid_frame.pack_forget()
        self.grad_frame.pack_forget()
        self.image_frame.pack_forget()
        
        t = self.bg_type_var.get()
        if t == "solid":
            self.solid_frame.pack(fill=tk.X, after=self.solid_frame.master.winfo_children()[1])
        elif t == "gradient":
            self.grad_frame.pack(fill=tk.X, after=self.solid_frame.master.winfo_children()[1])
        else:
            self.image_frame.pack(fill=tk.X, after=self.solid_frame.master.winfo_children()[1])
    
    def setup_preview(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(frame, text="Dialogue:").pack(anchor=tk.W)
        self.preview_text = tk.Text(frame, width=80, height=6, bg=self.BG3, fg=self.FG, insertbackground=self.FG, relief=tk.FLAT, padx=8, pady=8)
        self.preview_text.pack(fill=tk.X, pady=(5, 0))
        self.preview_text.insert("1.0", "* Hello, world!\n* This is a preview.")
    
    def setup_buttons(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(frame, text="Generate", style="Accent.TButton", command=self.generate).pack(side=tk.LEFT)
        ttk.Button(frame, text="Save Config", command=self.save_config).pack(side=tk.RIGHT)
        ttk.Button(frame, text="Load Config", command=self.load_config).pack(side=tk.RIGHT, padx=(0, 5))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frame, textvariable=self.status_var, foreground=self.FG2).pack(side=tk.LEFT, padx=(15, 0))
    
    def browse(self, var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            var.set(path)
    
    def pick_color(self, target):
        color = colorchooser.askcolor(title="Choose Color")
        if color[1]:
            rgb = [int(c) for c in color[0]]
            hex_color = color[1]
            
            if target == "bg":
                self.bg_color = rgb
                self.bg_btn.config(bg=hex_color)
            elif target == "text":
                self.text_color = rgb
                self.text_btn.config(bg=hex_color)
            elif target == "grad_top":
                self.grad_top = rgb
                self.grad_top_btn.config(bg=hex_color)
            elif target == "grad_bottom":
                self.grad_bottom = rgb
                self.grad_bottom_btn.config(bg=hex_color)
    
    def build_command(self):
        bg_type = self.bg_type_var.get()
        
        if bg_type == "solid":
            cmd = ["python", "generate.py"]
            cmd.extend(["-i", self.input_var.get()])
            cmd.extend(["-o", self.output_var.get()])
            if self.font_var.get():
                cmd.extend(["-f", self.font_var.get()])
            cmd.extend(["--font-size", str(self.fontsize_var.get())])
            cmd.extend(["--max-width", str(self.width_var.get())])
            cmd.extend(["--padding", str(self.padding_var.get())])
            cmd.extend(["--char-speed", str(self.speed_var.get())])
            cmd.extend(["--text-color", ",".join(map(str, self.text_color))])
            cmd.extend(["--bg-color", ",".join(map(str, self.bg_color))])
            if self.autoopen_var.get():
                cmd.append("--auto-open")
            fmt = self.format_var.get()
            if fmt == "gif":
                cmd.append("--gif-only")
        else:
            cmd = ["python", "gradient.py"]
            cmd.extend(["-i", self.input_var.get()])
            out = self.output_var.get()
            if out:
                base = Path(out).stem
                cmd.extend(["-o", base])
            if self.font_var.get():
                cmd.extend(["-f", self.font_var.get()])
            cmd.extend(["--font-size", str(self.fontsize_var.get())])
            cmd.extend(["--width", str(self.width_var.get())])
            cmd.extend(["--height", str(self.height_var.get())])
            cmd.extend(["--padding", str(self.padding_var.get())])
            cmd.extend(["--text-color", ",".join(map(str, self.text_color)) + ",255"])
            cmd.extend(["--format", self.format_var.get()])
            
            if bg_type == "gradient":
                cmd.extend(["--gradient", self.grad_dir_var.get()])
                cmd.extend(["--top-color", ",".join(map(str, self.grad_top)) + ",255"])
                cmd.extend(["--bottom-color", ",".join(map(str, self.grad_bottom)) + ",255"])
            else:
                if self.bg_image_var.get():
                    cmd.extend(["--bg-image", self.bg_image_var.get()])
            
            if self.autoopen_var.get():
                cmd.append("--auto-open")
        
        return cmd
    
    def generate(self):
        text = self.preview_text.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Empty", "No text to generate")
            return
        
        temp_file = "_temp_dialogue.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        self.input_var.set(temp_file)
        cmd = self.build_command()
        self.status_var.set("Generating...")
        
        def run():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.root.after(0, lambda: self.status_var.set("Done!"))
                else:
                    self.root.after(0, lambda: self.status_var.set("Error"))
                    self.root.after(0, lambda: messagebox.showerror("Error", result.stderr or "Generation failed"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set("Error"))
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        threading.Thread(target=run, daemon=True).start()
    
    def save_config(self):
        config = {
            "width": self.width_var.get(),
            "height": self.height_var.get(),
            "font_size": self.fontsize_var.get(),
            "padding": self.padding_var.get(),
            "speed": self.speed_var.get(),
            "bg_type": self.bg_type_var.get(),
            "bg_color": self.bg_color,
            "text_color": self.text_color,
            "grad_top": self.grad_top,
            "grad_bottom": self.grad_bottom,
            "grad_dir": self.grad_dir_var.get(),
            "format": self.format_var.get(),
            "auto_open": self.autoopen_var.get(),
        }
        with open("gui_config.json", "w") as f:
            json.dump(config, f, indent=2)
        messagebox.showinfo("Saved", "Config saved to gui_config.json")
    
    def load_config(self):
        if not os.path.exists("gui_config.json"):
            messagebox.showwarning("Not Found", "No gui_config.json found")
            return
        
        with open("gui_config.json", "r") as f:
            config = json.load(f)
        
        self.width_var.set(config.get("width", 800))
        self.height_var.set(config.get("height", 200))
        self.fontsize_var.set(config.get("font_size", 28))
        self.padding_var.set(config.get("padding", 20))
        self.speed_var.set(config.get("speed", 2))
        self.bg_type_var.set(config.get("bg_type", "solid"))
        self.bg_color = config.get("bg_color", [0, 0, 0])
        self.text_color = config.get("text_color", [255, 255, 255])
        self.grad_top = config.get("grad_top", [255, 255, 255])
        self.grad_bottom = config.get("grad_bottom", [120, 120, 120])
        self.grad_dir_var.set(config.get("grad_dir", "vertical"))
        self.format_var.set(config.get("format", "mp4"))
        self.autoopen_var.set(config.get("auto_open", True))
        
        self.bg_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.bg_color))
        self.text_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.text_color))
        self.grad_top_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.grad_top))
        self.grad_bottom_btn.config(bg="#{:02x}{:02x}{:02x}".format(*self.grad_bottom))
        
        self.switch_bg_type()
        messagebox.showinfo("Loaded", "Config loaded")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
