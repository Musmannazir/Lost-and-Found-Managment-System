import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import os
import psycopg2
import configparser
import subprocess

# --------- Read DB config from database.ini --------- #
config = configparser.ConfigParser()
config.read('db.ini')
db_params = config['postgresql']

# --------- Connect to PostgreSQL --------- #
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# --------- Read Current User ----------------- #
current_user_id = None
if os.path.exists("current_user.txt"):
    with open("current_user.txt", "r") as f:
        current_user_id = f.read().strip()

if not current_user_id:
    messagebox.showerror("Error", "No user is logged in. Please log in again.")
    subprocess.Popen(["python", "login.py"])
    cursor.close()
    conn.close()
    exit()

# --------- Fetch Locations from DB --------- #
cursor.execute("SELECT location_id, location_name FROM locations")
locations = cursor.fetchall()
location_map = {name: lid for lid, name in locations}

# --------- Main Window --------- #
root = tk.Tk()
root.title("Post Lost Item")
root.geometry("900x550")
root.configure(bg='#3b1d5e')
root.resizable(False, False)

# --------- Left Frame --------- #
left_frame = tk.Frame(root, bg='#3b1d5e', width=400, height=550)
left_frame.pack(side='left', fill='y')

title = tk.Label(left_frame, text="Post Lost Item", font=("Segoe UI", 26, "bold"), fg='white', bg='#3b1d5e')
title.place(x=30, y=100)

desc = tk.Label(
    left_frame,
    text="Help others by posting items you found\nor report your lost items.",
    font=("Segoe UI", 13),
    fg='#d3cce3',
    bg='#3b1d5e',
    justify='left'
)
desc.place(x=30, y=160)

# --------- Right Frame --------- #
right_frame = tk.Frame(root, bg='white', width=500, height=550)
right_frame.pack(side='right', fill='both')

form_title = tk.Label(right_frame, text="Lost Item Form", font=("Segoe UI", 20, "bold"), bg='white', fg='#3b1d5e')
form_title.place(x=160, y=20)

def label_entry(text, y_pos):
    label = tk.Label(right_frame, text=text, font=("Segoe UI", 10, "bold"), bg='white', fg='#333')
    label.place(x=60, y=y_pos)

def entry_box(y_pos):
    entry = tk.Entry(right_frame, width=35, font=("Segoe UI", 10), bd=1, relief='solid')
    entry.place(x=60, y=y_pos)
    return entry

def go_back():
    root.destroy()
    subprocess.Popen(["python", "dashboard.py"])

back_btn = tk.Button(
    right_frame,
    text="← Back",
    command=go_back,
    bg="white",
    fg="#5e3aca",
    font=("Segoe UI", 11, "bold"),
    bd=0,
    cursor="hand2",
    activebackground="white",
    activeforeground="#431b8f"
)
back_btn.place(x=10, y=10)

# --------- Fields --------- #
label_entry("Item Title", 80)
title_entry = entry_box(100)

label_entry("Description", 140)
desc_entry = entry_box(160)

label_entry("Location", 200)
location_combo = ttk.Combobox(right_frame, values=list(location_map.keys()), state="readonly", width=32)
location_combo.place(x=60, y=220)

label_entry("Date", 260)
date_entry = DateEntry(right_frame, width=33, font=("Segoe UI", 10), background='#5e3aca',
                       foreground='white', date_pattern='yyyy-mm-dd')
date_entry.place(x=60, y=280)

# Status Dropdown (Lost or Found)
label_entry("Status", 320)
status_combo = ttk.Combobox(right_frame, values=["Lost", "Found"], state="readonly", width=32)
status_combo.place(x=60, y=340)
status_combo.set("Lost")

# Image Upload
image_path = [None]

def upload_image():
    file_path = filedialog.askopenfilename(title="Select Image",
                                           filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")])
    if file_path:
        image_path[0] = file_path
        img_label.config(text=os.path.basename(file_path), fg="green")

label_entry("Item Image", 380)
upload_btn = tk.Button(
    right_frame,
    text="Upload Image",
    command=upload_image,
    bg='#5e3aca',
    fg='white',
    font=("Segoe UI", 10, "bold"),
    bd=0,
    relief="flat",
    width=15,
    height=1,
    cursor="hand2",
    activebackground="#431b8f"
)
upload_btn.place(x=60, y=400)

img_label = tk.Label(right_frame, text="No image selected", font=("Segoe UI", 9), bg='white', fg='gray')
img_label.place(x=180, y=403)

# --------- Submit Item to DB --------- #
def post_item():
    title = title_entry.get()
    description = desc_entry.get()
    location_name = location_combo.get()
    date = date_entry.get()
    status = status_combo.get()

    if not (title and description and location_name and date and status and image_path[0]):
        messagebox.showwarning("Missing Info", "Please fill in all fields and upload an image.")
        return

    location_id = location_map.get(location_name)
    if not location_id:
        messagebox.showwarning("Invalid Location", "Selected location is not valid.")
        return

    image_store_path = os.path.join("images", os.path.basename(image_path[0]))

    # Save image to project folder
    if not os.path.exists("images"):
        os.makedirs("images")
    try:
        with open(image_path[0], 'rb') as src, open(image_store_path, 'wb') as dst:
            dst.write(src.read())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save image: {e}")
        return

    # Insert into items
    try:
        cursor.execute("""
            INSERT INTO items (title, description, date_reported, status, image_path, location_id, reported_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (title, description, date, status, image_store_path, location_id, current_user_id))
        conn.commit()
        messagebox.showinfo("Success", "Lost item posted successfully.")
        root.destroy()
        subprocess.Popen(["python", "dashboard.py"])
    except psycopg2.Error as e:
        conn.rollback()
        messagebox.showerror("Database Error", f"Failed to insert item: {e}")

submit_btn = tk.Button(
    right_frame,
    text="Post Item",
    command=post_item,
    bg='#5e3aca',
    fg='white',
    font=("Segoe UI", 11, "bold"),
    width=28,
    height=2,
    bd=0,
    relief='flat',
    cursor="hand2",
    activebackground="#431b8f"
)
submit_btn.place(x=60, y=460)

root.mainloop()
cursor.close()
conn.close()