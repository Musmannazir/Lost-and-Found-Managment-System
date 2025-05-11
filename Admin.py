import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import psycopg2
import configparser
import os
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# Initialize Firebase
cred = credentials.Certificate("fb.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Read DB config from database.ini
config = configparser.ConfigParser()
config.read('db.ini')
db_params = config['postgresql']

# Connect to PostgreSQL
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# Main Admin Dashboard Window
root = tk.Tk()
root.title("Admin Dashboard")
root.geometry("800x500")
root.configure(bg='#3b1d5e')
root.resizable(False, False)

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'))

item_images = {}

# Function to log admin action
def log_admin_action(admin_id, action_type, description):
    try:
        cursor.execute('''
            INSERT INTO admin_actions (admin_id, action_type, action_description)
            VALUES (%s, %s, %s)
        ''', (admin_id, action_type, description))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error logging admin action: {e}")

# Function to upload all data to Firebase
def upload_to_firebase():
    try:
        # Upload items
        cursor.execute('''
            SELECT i.item_id, i.title, i.description, i.date_reported, i.status, u.name, l.location_name, i.image_path
            FROM items i
            LEFT JOIN users u ON i.reported_by = u.user_id
            LEFT JOIN locations l ON i.location_id = l.location_id
        ''')
        for row in cursor.fetchall():
            item_id, title, description, date_reported, status, user, location, image_path = row
            date_reported_str = date_reported.isoformat() if isinstance(date_reported, datetime.date) else str(date_reported)
            item_data = {
                'item_id': str(item_id),
                'title': title,
                'description': description,
                'date_reported': date_reported_str,
                'status': status,
                'reported_by': user if user else 'Unknown',
                'location': location if location else 'Unknown',
                'image_path': image_path if image_path else ''
            }
            db.collection('items').document(str(item_id)).set(item_data)

        # Upload users
        cursor.execute("SELECT user_id, name, email, phone, role FROM users")
        for row in cursor.fetchall():
            user_id, name, email, phone, role = row
            user_data = {
                'user_id': str(user_id),
                'name': name,
                'email': email,
                'phone': phone if phone else '',
                'role': role if role else ''
            }
            db.collection('users').document(str(user_id)).set(user_data)

        # Upload claims
        cursor.execute('''
            SELECT c.claim_id, i.title, u.name, c.claim_date, c.status, c.loss_location, c.loss_date
            FROM claims c
            JOIN items i ON c.item_id = i.item_id
            LEFT JOIN users u ON c.claimed_by = u.user_id
        ''')
        for row in cursor.fetchall():
            claim_id, item_title, user_name, claim_date, status, loss_location, loss_date = row
            claim_date_str = claim_date.isoformat() if isinstance(claim_date, datetime.date) else str(claim_date)
            loss_date_str = loss_date.isoformat() if isinstance(loss_date, datetime.date) else str(loss_date) if loss_date else ''
            claim_data = {
                'claim_id': str(claim_id),
                'item_title': item_title,
                'claimed_by': user_name if user_name else 'Unknown',
                'claim_date': claim_date_str,
                'status': status,
                'loss_location': loss_location if loss_location else '',
                'loss_date': loss_date_str
            }
            db.collection('claims').document(str(claim_id)).set(claim_data)

        # Upload deleted items
        cursor.execute('''
            SELECT di.deleted_item_id, di.item_id, di.title, u.name, di.date_reported, di.deleted_at
            FROM deleted_items di
            LEFT JOIN users u ON di.reported_by = u.user_id
        ''')
        for row in cursor.fetchall():
            deleted_item_id, item_id, title, reported_by, date_reported, deleted_at = row
            date_reported_str = date_reported.isoformat() if isinstance(date_reported, datetime.date) else str(date_reported)
            deleted_at_str = deleted_at.isoformat() if isinstance(deleted_at, datetime.datetime) else str(deleted_at)
            deleted_item_data = {
                'deleted_item_id': str(deleted_item_id),
                'item_id': str(item_id),
                'title': title,
                'reported_by': reported_by if reported_by else 'Unknown',
                'date_reported': date_reported_str,
                'deleted_at': deleted_at_str
            }
            db.collection('deleted_items').document(str(deleted_item_id)).set(deleted_item_data)

        # Upload deleted users
        cursor.execute("SELECT user_id, name, email, phone, role FROM deleted_users")
        for row in cursor.fetchall():
            user_id, name, email, phone, role = row
            deleted_user_data = {
                'user_id': str(user_id),
                'name': name,
                'email': email,
                'phone': phone if phone else '',
                'role': role if role else ''
            }
            db.collection('deleted_users').document(str(user_id)).set(deleted_user_data)

        # Upload deleted claims
        cursor.execute('''
            SELECT dc.claim_id, dc.item_id, u.name, dc.claim_date, dc.status, dc.loss_location, dc.loss_date
            FROM deleted_claims dc
            LEFT JOIN users u ON dc.claimed_by = u.user_id
        ''')
        for row in cursor.fetchall():
            claim_id, item_id, user_name, claim_date, status, loss_location, loss_date = row
            claim_date_str = claim_date.isoformat() if isinstance(claim_date, datetime.date) else str(claim_date)
            loss_date_str = loss_date.isoformat() if isinstance(loss_date, datetime.date) else str(loss_date) if loss_date else ''
            deleted_claim_data = {
                'claim_id': str(claim_id),
                'item_id': str(item_id),
                'claimed_by': user_name if user_name else 'Unknown',
                'claim_date': claim_date_str,
                'status': status,
                'loss_location': loss_location if loss_location else '',
                'loss_date': loss_date_str
            }
            db.collection('deleted_claims').document(str(claim_id)).set(deleted_claim_data)

        # Upload admin actions
        cursor.execute('''
            SELECT aa.action_id, aa.admin_id, aa.action_type, aa.action_description, aa.action_timestamp, a.username
            FROM admin_actions aa
            JOIN admins a ON aa.admin_id = a.admin_id
        ''')
        for row in cursor.fetchall():
            action_id, admin_id, action_type, action_description, action_timestamp, admin_username = row
            action_timestamp_str = action_timestamp.isoformat() if isinstance(action_timestamp, datetime.datetime) else str(action_timestamp)
            action_data = {
                'action_id': str(action_id),
                'admin_id': str(admin_id),
                'action_type': action_type,
                'action_description': action_description,
                'action_timestamp': action_timestamp_str,
                'admin_username': admin_username
            }
            db.collection('admin_actions').document(str(action_id)).set(action_data)

        messagebox.showinfo("Success", "All data successfully uploaded to Firebase Firestore.")
        log_admin_action(1, "Update", "Uploaded all data to Firebase Firestore")
        show_recent_actions()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload to Firebase: {str(e)}")

# Add Upload to Firebase and Recent Actions buttons at the top
button_frame = tk.Frame(root, bg='#3b1d5e')
button_frame.pack(pady=10)

firebase_btn = tk.Button(button_frame, text="Upload to Firebase", command=upload_to_firebase, bg='#28a745', fg='white')
firebase_btn.pack(side='left', padx=10)

recent_actions_btn = tk.Button(button_frame, text="Recent Actions", command=lambda: [notebook.select(actions_tab), show_recent_actions()], bg='#007bff', fg='white')
recent_actions_btn.pack(side='left', padx=10)

# --------- Tab 1: Manage Posted Items ---------
items_tab = ttk.Frame(notebook)
notebook.add(items_tab, text='Posted Items')

items_tree = ttk.Treeview(items_tab, columns=("ID", "Title", "Description", "Date", "Status", "User", "Location"), show='headings')
for col in items_tree["columns"]:
    items_tree.heading(col, text=col)
    items_tree.column(col, width=130)
items_tree.pack(fill='both', expand=True)

def show_posted_items():
    items_tree.delete(*items_tree.get_children())
    cursor.execute('''
        SELECT i.item_id, i.title, i.description, i.date_reported, i.status, COALESCE(u.name, 'Unknown') AS user_name, l.location_name, i.image_path
        FROM items i
        LEFT JOIN users u ON i.reported_by = u.user_id
        LEFT JOIN locations l ON i.location_id = l.location_id
    ''')
    for row in cursor.fetchall():
        item_id, title, description, date_reported, status, user_name, location, image_path = row
        image = None
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail((50, 50))
                image = ImageTk.PhotoImage(img)
                item_images[item_id] = image
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
        items_tree.insert('', 'end', values=(item_id, title, description, date_reported, status, user_name, location))

show_posted_items()

def delete_selected_item():
    selected = items_tree.focus()
    if not selected:
        messagebox.showwarning("No selection", "Please select an item to delete.")
        return
    item_id = items_tree.item(selected)['values'][0]
    try:
        cursor.execute('''
            SELECT item_id, title, description, date_reported, status, image_path, location_id, reported_by
            FROM items
            WHERE item_id = %s
        ''', (item_id,))
        item = cursor.fetchone()
        if item:
            cursor.execute('''
                INSERT INTO deleted_items (item_id, title, description, date_reported, status, image_path, location_id, reported_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', item)
            cursor.execute("DELETE FROM items WHERE item_id = %s", (item_id,))
            conn.commit()
            items_tree.delete(selected)
            messagebox.showinfo("Deleted", "Item moved to Deleted Items tab.")
            show_all_claims()
            load_deleted_items()
            load_deleted_claims()
            show_recent_actions()
    except psycopg2.Error as e:
        conn.rollback()
        messagebox.showerror("Error", f"Failed to delete item: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")

delete_button = ttk.Button(items_tab, text="Delete Item", command=delete_selected_item)
delete_button.pack(pady=10)

# --------- Tab 2: Claim Requests ---------
claims_tab = ttk.Frame(notebook)
notebook.add(claims_tab, text='Claim Requests')

claims_tree = ttk.Treeview(claims_tab, columns=("Claim ID", "Item", "User", "Date", "Status"), show='headings')
for col in claims_tree["columns"]:
    claims_tree.heading(col, text=col)
    claims_tree.column(col, width=150)
claims_tree.pack(fill='both', expand=True)

def show_all_claims():
    claims_tree.delete(*claims_tree.get_children())
    cursor.execute('''
        SELECT c.claim_id, i.title, COALESCE(u.name, 'Unknown') AS user_name, c.claim_date, c.status
        FROM claims c
        JOIN items i ON c.item_id = i.item_id
        LEFT JOIN users u ON c.claimed_by = u.user_id
    ''')
    for row in cursor.fetchall():
        claims_tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4]))

show_all_claims()

def approve_claim():
    selected = claims_tree.focus()
    if not selected:
        messagebox.showwarning("No selection", "Please select a claim to approve.")
        return
    claim_id = claims_tree.item(selected)['values'][0]
    try:
        cursor.execute('''
            SELECT claim_id, item_id, claimed_by, claim_date, status, approved_by, loss_location, loss_date
            FROM claims
            WHERE claim_id = %s
        ''', (claim_id,))
        claim = cursor.fetchone()
        if claim:
            cursor.execute('''
                UPDATE items
                SET status = 'Returned'
                WHERE item_id = %s
            ''', (claim[1],))
            updated_claim = (claim[0], claim[1], claim[2], claim[3], 'Approved', claim[5], claim[6], claim[7])
            cursor.execute('''
                INSERT INTO deleted_claims (claim_id, item_id, claimed_by, claim_date, status, approved_by, loss_location, loss_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', updated_claim)
            cursor.execute("DELETE FROM claims WHERE claim_id = %s", (claim_id,))
            conn.commit()
            log_admin_action(1, "Update", f"Approved claim ID {claim_id} for item ID {claim[1]}")
            show_all_claims()
            show_posted_items()
            load_deleted_claims()
            show_recent_actions()
            messagebox.showinfo("Approved", "Claim approved, item marked as Returned, and claim moved to Deleted Claims tab.")
    except psycopg2.Error as e:
        conn.rollback()
        messagebox.showerror("Error", f"Failed to approve claim: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")

def delete_claim():
    selected = claims_tree.focus()
    if not selected:
        messagebox.showwarning("No selection", "Please select a claim to delete.")
        return
    claim_id = claims_tree.item(selected)['values'][0]
    try:
        cursor.execute('''
            SELECT claim_id, item_id, claimed_by, claim_date, status, approved_by, loss_location, loss_date
            FROM claims
            WHERE claim_id = %s
        ''', (claim_id,))
        claim = cursor.fetchone()
        if claim:
            cursor.execute('''
                INSERT INTO deleted_claims (claim_id, item_id, claimed_by, claim_date, status, approved_by, loss_location, loss_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', claim)
            cursor.execute("DELETE FROM claims WHERE claim_id = %s", (claim_id,))
            conn.commit()
            show_all_claims()
            load_deleted_claims()
            show_recent_actions()
            messagebox.showinfo("Deleted", "Claim moved to Deleted Claims tab.")
    except psycopg2.Error as e:
        conn.rollback()
        messagebox.showerror("Error", f"Failed to delete claim: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")

claim_btns = tk.Frame(claims_tab)
claim_btns.pack(pady=10)

approve_btn = tk.Button(claim_btns, text="Approve Claim", command=approve_claim, bg='#5e3aca', fg='white')
approve_btn.pack(side='left', padx=10)

delete_claim_btn = tk.Button(claim_btns, text="Delete Claim", command=delete_claim, bg='#c0392b', fg='white')
delete_claim_btn.pack(side='left', padx=10)

# --------- Tab 3: User Management ---------
users_tab = ttk.Frame(notebook)
notebook.add(users_tab, text='Users')

users_tree = ttk.Treeview(users_tab, columns=("User ID", "Name", "Email"), show='headings')
for col in users_tree["columns"]:
    users_tree.heading(col, text=col)
    users_tree.column(col, width=180)
users_tree.pack(fill='both', expand=True)

def show_users():
    users_tree.delete(*users_tree.get_children())
    cursor.execute("SELECT user_id, name, email FROM users")
    for row in cursor.fetchall():
        users_tree.insert('', 'end', values=row)

show_users()

def remove_user():
    selected = users_tree.focus()
    if not selected:
        messagebox.showwarning("No selection", "Please select a user to delete.")
        return
    user_id = users_tree.item(selected)['values'][0]
    try:
        cursor.execute('''
            SELECT user_id, name, email, phone, role, password
            FROM users
            WHERE user_id = %s
        ''', (user_id,))
        user = cursor.fetchone()
        if not user:
            messagebox.showerror("Error", f"User with ID {user_id} not found.")
            show_users()
            return
        cursor.execute("SELECT user_id FROM deleted_users WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            messagebox.showerror("Error", f"User with ID {user_id} already exists in deleted_users.")
            show_users()
            return
        cursor.execute('''
            INSERT INTO deleted_users (user_id, name, email, phone, role, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', user)
        if cursor.rowcount == 0:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to insert user {user_id} into deleted_users.")
            show_users()
            return
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        if cursor.rowcount == 0:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to delete user {user_id} from users table.")
            show_users()
            return
        conn.commit()
        users_tree.delete(selected)
        show_posted_items()
        show_all_claims()
        load_deleted_users()
        load_deleted_items()
        load_deleted_claims()
        show_recent_actions()
        messagebox.showinfo("Removed", f"User {user_id} deleted and moved to Deleted Users tab.")
    except psycopg2.Error as e:
        conn.rollback()
        messagebox.showerror("Error", f"Failed to remove user: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")
        show_users()

delete_user_btn = ttk.Button(users_tab, text="Delete User", command=remove_user)
delete_user_btn.pack(pady=10)

# --------- Tab 4: Deleted Records ---------
deleted_tab = ttk.Frame(notebook)
notebook.add(deleted_tab, text='Deleted Records')

deleted_notebook = ttk.Notebook(deleted_tab)
deleted_notebook.pack(expand=True, fill='both')

# Deleted Items
deleted_items_tab = ttk.Frame(deleted_notebook)
deleted_notebook.add(deleted_items_tab, text='Items')

deleted_tree = ttk.Treeview(deleted_items_tab, columns=("Deleted ID", "Item ID", "Title", "Reported By", "Date", "Deleted At"), show='headings')
for col in deleted_tree["columns"]:
    deleted_tree.heading(col, text=col)
    deleted_tree.column(col, width=130)
deleted_tree.pack(fill='both', expand=True)

undo_item_btn = ttk.Button(deleted_items_tab, text="Undo Delete", command=lambda: undo_deleted_item())
undo_item_btn.pack(pady=10)

def load_deleted_items():
    deleted_tree.delete(*deleted_tree.get_children())
    cursor.execute('''
        SELECT di.deleted_item_id, di.item_id, di.title, COALESCE(u.name, 'Unknown') AS user_name, di.date_reported, di.deleted_at
        FROM deleted_items di
        LEFT JOIN users u ON di.reported_by = u.user_id
    ''')
    for row in cursor.fetchall():
        deleted_tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4], row[5]))

def undo_deleted_item():
    selected = deleted_tree.focus()
    if not selected:
        messagebox.showwarning("No selection", "Please select an item to undo.")
        return
    deleted_item_id = deleted_tree.item(selected)['values'][0]
    try:
        cursor.execute("SELECT item_id FROM deleted_items WHERE deleted_item_id