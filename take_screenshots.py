#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from gui import DialogueGeneratorGUI, ModernStyle

try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def take_screenshots():
    if not HAS_PIL:
        print("PIL required: pip install Pillow")
        return
    
    root = tk.Tk()
    app = DialogueGeneratorGUI(root)
    
    def capture():
        root.update_idletasks()
        root.update()
        
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save("screenshots/gui_pixel_perfect.png")
        print("Saved: screenshots/gui_pixel_perfect.png")
        
        app.notebook.select(1)
        root.update_idletasks()
        root.update()
        root.after(200)
        root.update()
        
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save("screenshots/gui_gradient.png")
        print("Saved: screenshots/gui_gradient.png")
        
        app.notebook.select(2)
        root.update_idletasks()
        root.update()
        root.after(200)
        root.update()
        
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save("screenshots/gui_batch.png")
        print("Saved: screenshots/gui_batch.png")
        
        root.quit()
    
    root.after(500, capture)
    root.mainloop()

if __name__ == "__main__":
    take_screenshots()
