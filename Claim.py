import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from configparser import ConfigParser
import psycopg2
import subprocess
from PIL import Image, ImageTk
import os

# ----------------- DB CONFIG ----------------- #
def config(filename='db.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in {filename}')
    return db

# ----------------- DB OPERATIONS ----------------- #
def fetch_items():
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""
            SELECT i.item_id, i.title, i.image_path, l.location_name
            FROM items i
            JOIN locations l ON i.location_id = l.location_id
            WHERE i.status != 'Returned'
        """)
        items = cur.fetchall()
        cur.close()
        conn.close()
        return items
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []

def insert_claim(item_id, claimed_by, date, location):
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO claims (item_id, claimed_by, claim_date, status, loss_location, loss_date)
            VALUES (%s, %s, %s, 'Pending', %s, %s)
        """, (item_id, claimed_by, date, location, date))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Insert Error", str(e))
        return False

def get_user_name(user_id):
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user[0] if user else None
    except Exception as e:
        messagebox.showerror("Database Error", f"Error fetching user: {e}")
        return None

# ----------------- Read Current User ----------------- #
current_user_id = None
if os.path.exists("current_user.txt"):
    with open("current_user.txt", "r") as f:
        current_user_id = f.read().strip()

if not current_user_id:
    messagebox.showerror("Error", "No user is logged in. Please log in again.")
    subprocess.Popen(["python", "login.py"])
    exit()

# ----------------- GUI SETUP ----------------- #
root = tk.Tk()
root.title("Claim Lost Items")
root.geometry("900x550")
root.configure(bg="#3b1d5e")
root.resizable(False, False)

# ----------------- Header and Back Button ----------------- #
header = tk.Label(root, text="Lost Items - Click 'Claim' to Request", font=("Helvetica", 22, "bold"),
                  bg="#3b1d5e", fg="white")
header.pack(pady=10)

def go_back():
    root.destroy()
    subprocess.Popen(["python", "dashboard.py"])

tk.Button(root, text="← Back", command=go_back, bg="white", fg="#5e3aca", font=("Helvetica", 12, "bold"),
          bd=0, cursor="hand2").place(x=10, y=10)

# ----------------- Scrollable Frame ----------------- #
container = tk.Frame(root, bg="white")
container.place(x=50, y=60, width=800, height=470)

canvas = tk.Canvas(container, bg="white")
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="white")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ----------------- Claim Form Popup ----------------- #
def open_claim_form(item):
    user_name = get_user_name(current_user_id)
    if not user_name:
        messagebox.showerror("Error", "User not found. Please log in again.")
        root.destroy()
        subprocess.Popen(["python", "login.py"])
        return

    top = tk.Toplevel(root)
    top.title("Submit Claim")
    top.geometry("400x400")
    top.configure(bg="white")

    tk.Label(top, text="Submit Claim", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)
    tk.Label(top, text=f"Claiming as: {user_name}", font=("Helvetica", 12), bg="white").pack(pady=5)

    tk.Label(top, text="Date of Loss:", bg="white").pack(pady=5)
    date_entry = DateEntry(top, width=27)
    date_entry.pack()

    tk.Label(top, text="Location of Loss:", bg="white").pack()
    location_entry = tk.Entry(top, width=30)
    location_entry.pack()

    def submit():
        date = date_entry.get()
        location = location_entry.get()

        if not date or not location:
            messagebox.showwarning("Missing Info", "Please fill all fields.")
            return

        if insert_claim(item[0], current_user_id, date, location):
            messagebox.showinfo("Success", "Claim submitted successfully.")
            top.destroy()

    tk.Button(top, text="Submit Claim", command=submit, bg="#5e3aca", fg="white", font=("Helvetica", 11, "bold")).pack(pady=20)

# ----------------- Display Items ----------------- #
items = fetch_items()
for idx, item in enumerate(items):
    item_id, title, image_path, location = item

    card = tk.Frame(scrollable_frame, bg="#f8f8f8", bd=1, relief="solid", padx=10, pady=10)
    card.pack(pady=10, fill="x", padx=20)

    photo = None
    try:
        image_path = os.path.normpath(image_path) if image_path else None  # Normalize path separators
        if image_path and os.path.exists(image_path):
            print(f"Loading image: {image_path}")  # Debug
            # Verify the image before resizing
            with Image.open(image_path) as img:
                img.verify()  # Check if the image is valid
                img = img.convert("RGB")  # Ensure compatibility
            # Reopen the image for resizing (verify closes the file)
            img = Image.open(image_path)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)
        else:
            print(f"Image path not found or invalid: {image_path}")  # Debug
            raise FileNotFoundError
    except FileNotFoundError:
        print(f"Image file does not exist: {image_path}")
        img = Image.new("RGB", (100, 100), color="gray")
        photo = ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")  # Debug
        img = Image.new("RGB", (100, 100), color="gray")
        photo = ImageTk.PhotoImage(img)

    img_label = tk.Label(card, image=photo)
    img_label.image = photo
    img_label.grid(row=0, column=0, rowspan=4, padx=10)

    tk.Label(card, text=title, font=("Helvetica", 14, "bold"), bg="#f8f8f8").grid(row=0, column=1, sticky="w")
    tk.Label(card, text=f"Location: {location}", bg="#f8f8f8").grid(row=2, column=1, sticky="w")

    tk.Button(card, text="Claim", command=lambda item=item: open_claim_form(item),
              bg="#5e3aca", fg="white", font=("Helvetica", 10, "bold")).grid(row=0, column=2, rowspan=4, padx=10)

# ----------------- Mainloop ----------------- #
root.mainloop()