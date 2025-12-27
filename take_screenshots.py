#!/usr/bin/env python3
import os
import sys
import time
import tkinter as tk

sys.path.insert(0, os.path.dirname(__file__))

try:
    from PIL import ImageGrab
except ImportError:
    print("Pillow required: pip install Pillow")
    sys.exit(1)

from gui import App

os.makedirs("screenshots", exist_ok=True)

def capture_window(root, filename):
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    root.update()
    
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img.save(filename)
    print(f"Saved: {filename}")

def main():
    root = tk.Tk()
    app = App(root)
    
    def take_all():
        app.bg_type_var.set("solid")
        app.switch_bg_type()
        capture_window(root, "screenshots/gui_solid.png")
        
        app.bg_type_var.set("gradient")
        app.switch_bg_type()
        capture_window(root, "screenshots/gui_gradient.png")
        
        app.bg_type_var.set("image")
        app.switch_bg_type()
        capture_window(root, "screenshots/gui_image.png")
        
        try:
            app.notebook.select(1)
            capture_window(root, "screenshots/gui_batch.png")
        except:
            pass
        
        root.quit()
    
    root.after(500, take_all)
    root.mainloop()

if __name__ == "__main__":
    main()
