import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import psycopg2  # type: ignore
from configparser import ConfigParser

# ----------------- Database Connection ----------------- #
def config(filename='db.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return db

# ----------------- Sign Up Window ----------------- #
signup_root = tk.Tk()
signup_root.title("Lost and Found Management - Sign Up")
signup_root.geometry("800x500")
signup_root.configure(bg='#3b1d5e')
signup_root.resizable(False, False)

# ----------------- Left Side (Image Only) ----------------- #
left_frame = tk.Frame(signup_root, width=400, height=500)
left_frame.pack(side='left', fill='y')

try:
    bg_img = Image.open("pic.jpg").resize((400, 500))
    bg_img = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(left_frame, image=bg_img)
    bg_label.image = bg_img
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print("Error loading side image:", e)
    left_frame.configure(bg='#3b1d5e')

# ----------------- Right Side (Sign Up Box) ----------------- #
right_frame = tk.Frame(signup_root, bg='white', width=400, height=500)
right_frame.pack(side='right', fill='both')

signup_title = tk.Label(right_frame, text="Sign Up", font=("Helvetica", 20, "bold"), bg='white')
signup_title.place(x=150, y=20)

# Name Entry
name_label = tk.Label(right_frame, text="Full Name", font=("Helvetica", 10, "bold"), bg='white')
name_label.place(x=70, y=70)
name_entry = tk.Entry(right_frame, width=30, font=("Helvetica", 11))
name_entry.place(x=70, y=90)

# Email Entry
email_label = tk.Label(right_frame, text="Email", font=("Helvetica", 10, "bold"), bg='white')
email_label.place(x=70, y=120)
email_entry = tk.Entry(right_frame, width=30, font=("Helvetica", 11))
email_entry.place(x=70, y=140)

# Phone Number Entry
phone_label = tk.Label(right_frame, text="Phone Number", font=("Helvetica", 10, "bold"), bg='white')
phone_label.place(x=70, y=170)
phone_entry = tk.Entry(right_frame, width=30, font=("Helvetica", 11))
phone_entry.place(x=70, y=190)

# Role Dropdown
role_label = tk.Label(right_frame, text="Role", font=("Helvetica", 10, "bold"), bg='white')
role_label.place(x=70, y=220)
role_var = tk.StringVar(value="Select Role")
role_dropdown = tk.OptionMenu(right_frame, role_var, "Student", "Staff", "Guest")
role_dropdown.config(width=27, font=("Helvetica", 10), bg="white")
role_dropdown.place(x=70, y=240)

# Password Entry
password_label = tk.Label(right_frame, text="Password", font=("Helvetica", 10, "bold"), bg='white')
password_label.place(x=70, y=270)
password_entry = tk.Entry(right_frame, width=30, font=("Helvetica", 11), show="*")
password_entry.place(x=70, y=290)

# ----------------- Functions ----------------- #
def create_account():
    name = name_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    role = role_var.get()
    password = password_entry.get()

    if not name or not email or not phone or role == "Select Role" or not password:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # Check if user already exists
        cur.execute("SELECT * FROM users WHERE email=%s OR phone=%s", (email, phone))
        if cur.fetchone():
            messagebox.showerror("Error", "User with this email or phone already exists.")
        else:
            cur.execute("INSERT INTO users (name, email, phone, role, password) VALUES (%s, %s, %s, %s, %s)",
                        (name, email, phone, role, password))
            conn.commit()
            messagebox.showinfo("Success", f"Account created for {name} as {role}!")
            subprocess.Popen(["python", "dashboard.py"])
            signup_root.destroy()

        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

def go_back_to_login():
    signup_root.destroy()
    subprocess.Popen(["python", "login.py"])

# ----------------- Buttons ----------------- #
signup_btn = tk.Button(right_frame, text="Create Account", command=create_account, bg='#5e3aca', fg='white',
                       font=("Helvetica", 12, "bold"), width=24)
signup_btn.place(x=70, y=390)

back_btn = tk.Button(right_frame, text="Back to Login", command=go_back_to_login, bg='white', fg='#5e3aca',
                     font=("Helvetica", 12, "bold"), width=24, bd=2, highlightbackground="#5e3aca")
back_btn.place(x=70, y=430)

# ----------------- Start GUI ----------------- #
signup_root.mainloop()
