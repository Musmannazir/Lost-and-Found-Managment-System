import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import os

# ----------------- Main Window ----------------- #
root = tk.Tk()
root.title("Lost and Found Management - Dashboard")
root.geometry("800x500")
root.configure(bg='#3b1d5e')
root.resizable(False, False)

# ----------------- Read Current User ----------------- #
current_user_id = None
if os.path.exists("current_user.txt"):
    with open("current_user.txt", "r") as f:
        current_user_id = f.read().strip()

# ----------------- Left Side (Illustration & Text) ----------------- #
left_frame = tk.Frame(root, bg='#3b1d5e', width=400, height=500)
left_frame.pack(side='left', fill='y')

title = tk.Label(left_frame, text="Lost and Found", font=("Helvetica", 24, "bold"), fg='white', bg='#3b1d5e')
title.place(x=20, y=120)

desc = tk.Label(left_frame, text="Efficiently manage and claim lost items.\nPost or claim items to help others.",
                font=("Helvetica", 12), fg='lightgray', bg='#3b1d5e', justify='left')
desc.place(x=20, y=170)

# ----------------- Right Side (Dashboard) ----------------- #
right_frame = tk.Frame(root, bg='white', width=400, height=500)
right_frame.pack(side='right', fill='both')

dashboard_title = tk.Label(right_frame, text="Dashboard", font=("Helvetica", 20, "bold"), bg='white')
dashboard_title.place(x=140, y=80)

# ----------------- Dashboard Functions ----------------- #
def claim_items():
    root.destroy()
    subprocess.Popen(["python", "claim.py"])

def post_items():
    root.destroy()
    subprocess.Popen(["python", "post.py"])

def logout():
    # Clean up current_user.txt
    if os.path.exists("current_user.txt"):
        os.remove("current_user.txt")
    root.destroy()
    subprocess.Popen(["python", "login.py"])

# ----------------- Styled Buttons ----------------- #
btn_style = {
    "font": ("Helvetica", 12, "bold"),
    "width": 24,
    "bd": 2
}

# Claim Items Button
claim_btn = tk.Button(right_frame, text="Claim Items", command=claim_items, bg='#5e3aca', fg='white', **btn_style)
claim_btn.place(x=70, y=150)

# Post Items Button
post_btn = tk.Button(right_frame, text="Post Items", command=post_items, bg='white', fg='#5e3aca',
                     highlightbackground="#5e3aca", **btn_style)
post_btn.place(x=70, y=210)

# Logout Button
logout_btn = tk.Button(right_frame, text="Logout", command=logout, bg='#e74c3c', fg='white', **btn_style)
logout_btn.place(x=70, y=270)

# ----------------- Start GUI ----------------- #
root.mainloop()