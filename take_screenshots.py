#!/usr/bin/env python3
import tkinter as tk
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gui import App

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
    app = App(root)
    
    def capture():
        root.update_idletasks()
        root.update()
        
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save("screenshots/gui_solid.png")
        print("Saved: screenshots/gui_solid.png")
        
        app.bg_type_var.set("gradient")
        app.switch_bg_type()
        root.update_idletasks()
        root.update()
        root.after(200)
        root.update()
        
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save("screenshots/gui_gradient.png")
        print("Saved: screenshots/gui_gradient.png")
        
        root.quit()
    
    root.after(500, capture)
    root.mainloop()

if __name__ == "__main__":
    take_screenshots()
