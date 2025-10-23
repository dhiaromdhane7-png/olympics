import tkinter as tk
from tkinter import messagebox
import sqlite3

# --- Create local database if not exists ---
def setup_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Add test users (use INSERT OR IGNORE so reruns don't create duplicates)
    users = [
        ("farouk@esprit.tn", "1234"),
        ("fadi@esprit.tn", "1234"),
        ("rami@esprit.tn", "1234"),
        ("dhia@esprit.tn", "1234"),
    ]
    c.executemany("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", users)
    conn.commit()
    conn.close()

# --- Login verification ---
def connect_db(username, password):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("✅ Success", f"Welcome {username}!")
        else:
            messagebox.showerror("❌ Error", "Invalid username or password")

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# --- GUI Setup ---
root = tk.Tk()
root.title("User Login (SQLite)")
root.geometry("400x350")
root.config(bg="#1e1e2f")

# --- Title ---
title_label = tk.Label(root, text="🔐 User Login", font=("Arial", 20, "bold"), bg="#1e1e2f", fg="#00ffcc")
title_label.pack(pady=20)

# --- Username ---
username_label = tk.Label(root, text="Username (email)", font=("Arial", 12), bg="#1e1e2f", fg="#ffffff")
username_label.pack(pady=5)
username_entry = tk.Entry(root, font=("Arial", 12), width=30, relief="flat", bg="#2b2b40", fg="white", insertbackground="white")
username_entry.pack(pady=5)

# --- Password ---
password_label = tk.Label(root, text="Password", font=("Arial", 12), bg="#1e1e2f", fg="#ffffff")
password_label.pack(pady=5)
password_entry = tk.Entry(root, font=("Arial", 12), width=30, show="*", relief="flat", bg="#2b2b40", fg="white", insertbackground="white")
password_entry.pack(pady=5)

# --- Login Button ---
def on_login():
    user = username_entry.get().strip()
    pwd = password_entry.get().strip()
    if not user or not pwd:
        messagebox.showwarning("Input required", "Please enter both username and password.")
        return
    connect_db(user, pwd)

login_btn = tk.Button(root, text="Login", font=("Arial", 12, "bold"), bg="#00ffcc", fg="#000000", relief="flat", command=on_login)
login_btn.pack(pady=20, ipadx=20, ipady=5)

# --- Footer ---
footer_label = tk.Label(root, text="© 2025 Secure Login UI", font=("Arial", 9), bg="#1e1e2f", fg="#999999")
footer_label.pack(side="bottom", pady=10)

setup_db()
root.mainloop()
