import subprocess
import tkinter as tk
from tkinter import Image, messagebox
import psycopg2 # type: ignore
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

# ------------- Forgot Password Window ------------- #
root = tk.Tk()
root.title("Forgot Password")
root.geometry("800x500")
root.configure(bg='#3b1d5e')
root.resizable(False, False)

# ------------- Left Frame ------------- #
left_frame = tk.Frame(root, width=400, height=500)
left_frame.pack(side='left', fill='y')

try:
    bg_img = Image.open("pic.jpg").resize((400, 500))
    bg_img = Image.PhotoImage(bg_img)
    bg_label = tk.Label(left_frame, image=bg_img)
    bg_label.image = bg_img
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print("Error loading side image:", e)
    left_frame.configure(bg='#3b1d5e')

# ------------- Right Frame ------------- #
right_frame = tk.Frame(root, bg='white', width=400, height=500)
right_frame.pack(side='right', fill='both')

# Title
forgot_title = tk.Label(right_frame, text="Reset Password", font=("Segoe UI", 20, "bold"), bg='white')
forgot_title.place(x=130, y=100)

# Email
email_label = tk.Label(right_frame, text="Email", font=("Segoe UI", 10, "bold"), bg='white')
email_label.place(x=70, y=150)
email_entry = tk.Entry(right_frame, font=("Segoe UI", 11), bd=1, relief="solid", width=30)
email_entry.place(x=70, y=175)

# New Password
new_password_label = tk.Label(right_frame, text="New Password", font=("Segoe UI", 10, "bold"), bg='white')
new_password_label.place(x=70, y=220)
new_password_entry = tk.Entry(right_frame, font=("Segoe UI", 11), bd=1, relief="solid", show="*", width=30)
new_password_entry.place(x=70, y=245)

# Confirm New Password
confirm_password_label = tk.Label(right_frame, text="Confirm Password", font=("Segoe UI", 10, "bold"), bg='white')
confirm_password_label.place(x=70, y=290)
confirm_password_entry = tk.Entry(right_frame, font=("Segoe UI", 11), bd=1, relief="solid", show="*", width=30)
confirm_password_entry.place(x=70, y=315)

# ------------- Reset Password Function ------------- #
def reset_password():
    email = email_entry.get().strip()
    new_password = new_password_entry.get().strip()
    confirm_password = confirm_password_entry.get().strip()

    if not email or not new_password or not confirm_password:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    if new_password != confirm_password:
        messagebox.showwarning("Password Mismatch", "Passwords do not match.")
        return

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # Check if the email exists in the database
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user = cur.fetchone()

        if user:
            # Update the password
            update_query = "UPDATE users SET password = %s WHERE email = %s"
            cur.execute(update_query, (new_password, email))
            conn.commit()

            messagebox.showinfo("Success", "Password updated successfully.")
            root.destroy()
            subprocess.Popen(["python", "login.py"])  # Redirect to login page after password reset
        else:
            messagebox.showerror("User Not Found", "No user found with this email address.")

        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ------------- Buttons ------------- #
style = {
    "font": ("Segoe UI", 12, "bold"),
    "width": 24,
    "height": 1,
    "bd": 0,
    "cursor": "hand2"
}

reset_btn = tk.Button(right_frame, text="Reset Password", command=reset_password, bg='#6a1b9a', fg='white', **style)
reset_btn.place(x=70, y=360)

back_btn = tk.Button(right_frame, text="Back to Login", command=lambda: root.destroy() or subprocess.Popen(["python", "login.py"]), bg='white', fg='#6a1b9a',
                     activebackground='#eee', activeforeground='#6a1b9a', highlightbackground='#6a1b9a', relief="solid", borderwidth=1, **style)
back_btn.place(x=70, y=410)

# ------------- Run GUI ------------- #
root.mainloop()
