import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess

# ------------- Main Window ------------- #
root = tk.Tk()
root.title("Lost and Found Management System")
root.geometry("800x500")
root.configure(bg='#3b1d5e')
root.resizable(False, False)

# ------------- Left Frame ------------- #
left_frame = tk.Frame(root, width=400, height=500, bg='#3b1d5e')
left_frame.pack(side='left', fill='y')

try:
    bg_img = Image.open("pic.jpg").resize((400, 500))
    bg_img = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(left_frame, image=bg_img, bg='#3b1d5e')
    bg_label.image = bg_img
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print("Error loading side image:", e)
    left_frame.configure(bg='#3b1d5e')

# ------------- Right Frame ------------- #
right_frame = tk.Frame(root, bg='white', width=400, height=500)
right_frame.pack(side='right', fill='both')

# Logo
try:
    logo_img = Image.open("logo.png").resize((80, 80))
    logo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(right_frame, image=logo, bg='white')
    logo_label.image = logo
    logo_label.place(x=160, y=50)
except Exception as e:
    print("Error loading logo:", e)

# Title
title_label = tk.Label(right_frame, text="Lost and Found Management", 
                      font=("Segoe UI", 18, "bold"), bg='white', fg='#3b1d5e', 
                      wraplength=340, justify='center')
title_label.place(x=30, y=140)

# Description
desc_label = tk.Label(right_frame, text="Reunite with your lost items or help others find theirs!", 
                      font=("Helvetica", 12), bg='white', fg='#333', 
                      wraplength=300, justify='center')
desc_label.place(x=50, y=200)

# ------------- Get Started Function ------------- #
def get_started():
    root.destroy()
    subprocess.Popen(["python", "login.py"])

# ------------- Get Started Button ------------- #
style = {
    "font": ("Segoe UI", 12, "bold"),
    "width": 24,
    "height": 2,
    "bd": 0,
    "cursor": "hand2",
    "bg": "#5e3aca",
    "fg": "white",
    "activebackground": "#431b8f",
    "activeforeground": "white"
}

get_started_btn = tk.Button(right_frame, text="Get Started", command=get_started, **style)
get_started_btn.place(x=70, y=300)

# Footer
footer = tk.Label(right_frame, text="Your belongings, our priority!", 
                  font=("Segoe UI", 9), fg='gray', bg='white')
footer.place(x=120, y=460)

# ------------- Run GUI ------------- #
root.mainloop()