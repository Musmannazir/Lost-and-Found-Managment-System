import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import psycopg2
from configparser import ConfigParser

# -------- Database Configuration Reader -------- #
def config(filename='db.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db_params = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_params[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return db_params

# ------------- Main Window ------------- #
root = tk.Tk()
root.title("Lost and Found Management - Login")
root.geometry("800x500")
root.configure(bg='#3b1d5e')
root.resizable(False, False)

# ------------- Left Frame ------------- #
left_frame = tk.Frame(root, width=400, height=500)
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

# ------------- Right Frame ------------- #
right_frame = tk.Frame(root, bg='white', width=400, height=500)
right_frame.pack(side='right', fill='both')

# Logo
try:
    logo_img = Image.open("logo.png").resize((80, 80))
    logo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(right_frame, image=logo, bg='white')
    logo_label.image = logo
    logo_label.place(x=160, y=15)
except Exception as e:
    print("Error loading logo:", e)

# Title
login_title = tk.Label(right_frame, text="Login", font=("Segoe UI", 20, "bold"), bg='white')
login_title.place(x=160, y=100)

# Email
email_label = tk.Label(right_frame, text="Email", font=("Segoe UI", 10, "bold"), bg='white')
email_label.place(x=70, y=150)
email_entry = tk.Entry(right_frame, font=("Segoe UI", 11), bd=1, relief="solid", width=30)
email_entry.place(x=70, y=175)

# Password
password_label = tk.Label(right_frame, text="Password", font=("Segoe UI", 10, "bold"), bg='white')
password_label.place(x=70, y=220)
password_entry = tk.Entry(right_frame, font=("Segoe UI", 11), bd=1, relief="solid", show="*", width=30)
password_entry.place(x=70, y=245)

# ------------- Login Function ------------- #
def login():
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if email == "" or password == "":
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # First, check if it's an admin
        admin_query = "SELECT admin_id, name FROM admins WHERE email = %s AND password = %s"
        cur.execute(admin_query, (email, password))
        admin_result = cur.fetchone()

        if admin_result:
            messagebox.showinfo("Admin Login", f"Welcome Admin {admin_result[1]}!")
            # Store admin_id as current user (optional, depending on admin flow)
            with open("current_user.txt", "w") as f:
                f.write(str(admin_result[0]))
            root.destroy()
            subprocess.Popen(["python", "admin.py"])
        else:
            # Check regular users
            user_query = "SELECT user_id, name FROM users WHERE email = %s AND password = %s"
            cur.execute(user_query, (email, password))
            user_result = cur.fetchone()

            if user_result:
                # Store user_id in a file
                with open("current_user.txt", "w") as f:
                    f.write(str(user_result[0]))
                messagebox.showinfo("Login Success", f"Welcome back {user_result[1]}!")
                root.destroy()
                subprocess.Popen(["python", "dashboard.py"])
            else:
                messagebox.showerror("Login Failed", "Invalid email or password.")

        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ------------- Other Navigation ------------- #
def signup():
    root.destroy()
    subprocess.Popen(["python", "signup.py"])

def forgot_password():
    subprocess.Popen(["python", "forget.py"])

# ------------- Buttons ------------- #
style = {
    "font": ("Segoe UI", 12, "bold"),
    "width": 24,
    "height": 1,
    "bd": 0,
    "cursor": "hand2"
}

login_btn = tk.Button(right_frame, text="Login", command=login, bg='#6a1b9a', fg='white', **style)
login_btn.place(x=70, y=300)

signup_btn = tk.Button(right_frame, text="Sign Up", command=signup, bg='white', fg='#6a1b9a',
                       activebackground='#eee', activeforeground='#6a1b9a',
                       highlightbackground='#6a1b9a', relief="solid", borderwidth=1, **style)
signup_btn.place(x=70, y=350)

forgot_pass = tk.Label(right_frame, text="Forgot your password?", fg='#3b1d5e', bg='white',
                       font=("Segoe UI", 10, "underline"), cursor="hand2")
forgot_pass.place(x=130, y=400)
forgot_pass.bind("<Button-1>", lambda e: forgot_password())

footer = tk.Label(right_frame, text="Lost something? We're here to help!",
                  font=("Segoe UI", 9), fg='gray', bg='white')
footer.place(x=90, y=460)

# ------------- Run GUI ------------- #
root.mainloop()