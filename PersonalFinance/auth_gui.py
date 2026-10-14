import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os
import theme
import database

USERS_DB = os.path.join(database.DB_DIR, "users.db")

def init_users_db():
    os.makedirs(database.DB_DIR, exist_ok=True)
    with sqlite3.connect(USERS_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT
            )
        """)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class LoginGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MoneyManager - Đăng nhập")
        self.geometry("480x750")
        self.configure(bg=theme.BG)
        self.resizable(False, False)
        
        # Center the window
        theme.center_window(self, 480, 750)
        
        init_users_db()
        self.create_widgets()
        
    def create_widgets(self):
        for w in self.winfo_children(): w.destroy()
        
        tk.Label(self, text="💰", font=theme.F(50), bg=theme.BG).pack(pady=(20, 5))
        tk.Label(self, text="MoneyManager", font=theme.F(24, "bold"), fg=theme.TEXT, bg=theme.BG).pack()
        tk.Label(self, text="Quản lý tài chính cá nhân", font=theme.F(12), fg=theme.TEXT_2, bg=theme.BG).pack(pady=(0, 10))
        
        form = tk.Frame(self, bg=theme.CARD, padx=30, pady=20)
        form.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        form.config(highlightbackground=theme.BORDER, highlightthickness=1)
        
        tk.Label(form, text="Tài khoản", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(0, 5))
        self.ent_user = tk.Entry(form, font=theme.F(12), bg=theme.CARD_ALT, fg=theme.TEXT, relief="flat", insertbackground=theme.PRIMARY)
        self.ent_user.pack(fill="x", ipady=8, pady=(0, 10))
        
        tk.Label(form, text="Mật khẩu", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(0, 5))
        self.ent_pass = tk.Entry(form, font=theme.F(12), bg=theme.CARD_ALT, fg=theme.TEXT, relief="flat", insertbackground=theme.PRIMARY, show="•")
        self.ent_pass.pack(fill="x", ipady=8, pady=(0, 10))
        
        btn_frame = tk.Frame(form, bg=theme.CARD)
        btn_frame.pack(fill="x", pady=(10, 0))
        btn_frame.columnconfigure(0, weight=1, uniform="auth_btn")
        btn_frame.columnconfigure(1, weight=1, uniform="auth_btn")
        theme.RoundedButton(btn_frame, text="Đăng nhập", font=theme.F(12, "bold"), bg=theme.PRIMARY, fg="white", cursor="hand2", pady=12, command=self.do_login).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        theme.RoundedButton(btn_frame, text="Đăng ký", font=theme.F(12, "bold"), bg=theme.BALANCE, fg="white", cursor="hand2", pady=12, command=self.show_register).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def show_register(self):
        for w in self.winfo_children(): w.destroy()
        
        tk.Label(self, text="📝", font=theme.F(50), bg=theme.BG).pack(pady=(20, 5))
        tk.Label(self, text="Đăng ký tài khoản", font=theme.F(24, "bold"), fg=theme.TEXT, bg=theme.BG).pack(pady=(0, 10))
        
        form = tk.Frame(self, bg=theme.CARD, padx=30, pady=20)
        form.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        form.config(highlightbackground=theme.BORDER, highlightthickness=1)
        
        tk.Label(form, text="Tài khoản mới", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(0, 5))
        self.ent_user = tk.Entry(form, font=theme.F(12), bg=theme.CARD_ALT, fg=theme.TEXT, relief="flat", insertbackground=theme.PRIMARY)
        self.ent_user.pack(fill="x", ipady=8, pady=(0, 10))
        
        tk.Label(form, text="Mật khẩu", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(0, 5))
        self.ent_pass = tk.Entry(form, font=theme.F(12), bg=theme.CARD_ALT, fg=theme.TEXT, relief="flat", insertbackground=theme.PRIMARY, show="•")
        self.ent_pass.pack(fill="x", ipady=8, pady=(0, 10))
        
        tk.Label(form, text="Nhập lại mật khẩu", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(0, 5))
        self.ent_pass2 = tk.Entry(form, font=theme.F(12), bg=theme.CARD_ALT, fg=theme.TEXT, relief="flat", insertbackground=theme.PRIMARY, show="•")
        self.ent_pass2.pack(fill="x", ipady=8, pady=(0, 25))
        
        theme.RoundedButton(form, text="Tạo tài khoản", font=theme.F(12, "bold"), bg=theme.BALANCE, fg="white", cursor="hand2", pady=12, command=self.do_register).pack(fill="x", pady=(0, 10))
        
        btn_back = theme.RoundedButton(form, text="← Quay lại Đăng nhập", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.BORDER, cursor="hand2", pady=12, command=self.create_widgets)
        btn_back.pack(fill="x")

    def do_login(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get()
        if not user or not pwd:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
            
        with sqlite3.connect(USERS_DB) as conn:
            row = conn.execute("SELECT id FROM users WHERE username=? AND password_hash=?", 
                               (user, hash_password(pwd))).fetchone()
            if row:
                self.start_app(user)
            else:
                messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!")

    def do_register(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get()
        pwd2 = self.ent_pass2.get()
        
        if not user or not pwd:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
            
        if pwd != pwd2:
            messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp!")
            return
            
        try:
            with sqlite3.connect(USERS_DB) as conn:
                conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                             (user, hash_password(pwd)))
            messagebox.showinfo("Thành công", "Đăng ký thành công! Hãy đăng nhập.")
            self.create_widgets()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Tên tài khoản đã tồn tại!")

    def start_app(self, username):
        # Change DB dynamically
        database.DB_FILE = os.path.join(database.DB_DIR, f"finance_{username}.db")
        database.init_db()
        self.destroy()
        from gui import AppGUI
        app = AppGUI(username=username)
        app.mainloop()

if __name__ == "__main__":
    LoginGUI().mainloop()
