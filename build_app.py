import os

base_dir = "PersonalFinance"
os.makedirs(base_dir, exist_ok=True)
os.makedirs(os.path.join(base_dir, "data"), exist_ok=True)

with open(os.path.join(base_dir, "database.py"), "w", encoding="utf-8") as f:
    f.write('''import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_FILE = os.path.join(DB_DIR, 'finance.db')

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        note TEXT
    )
    """)
    conn.commit()
    conn.close()

def execute_query(query, params=()):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=()):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows
''')

with open(os.path.join(base_dir, "models.py"), "w", encoding="utf-8") as f:
    f.write('''from database import execute_query, fetch_query

class Transaction:
    @staticmethod
    def add(date, t_type, category, amount, description, note=""):
        query = "INSERT INTO transactions (date, type, category, amount, description, note) VALUES (?, ?, ?, ?, ?, ?)"
        execute_query(query, (date, t_type, category, amount, description, note))

    @staticmethod
    def get_all():
        return fetch_query("SELECT * FROM transactions ORDER BY date DESC")

    @staticmethod
    def get_summary():
        rows = fetch_query("SELECT type, SUM(amount) FROM transactions GROUP BY type")
        summary = {'Thu': 0, 'Chi': 0}
        for r in rows:
            if r[0] == 'Thu': summary['Thu'] = r[1]
            elif r[0] == 'Chi': summary['Chi'] = r[1]
        return summary

    @staticmethod
    def get_expenses_by_category():
        return fetch_query("SELECT category, SUM(amount) FROM transactions WHERE type='Chi' GROUP BY category")
        
    @staticmethod
    def delete(t_id):
        execute_query("DELETE FROM transactions WHERE id = ?", (t_id,))
''')

with open(os.path.join(base_dir, "gui.py"), "w", encoding="utf-8") as f:
    f.write('''import tkinter as tk
from tkinter import ttk, messagebox
from models import Transaction
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MoneyManager - Quản lý Tài chính Cá nhân")
        self.geometry("1000x600")
        self.configure(bg="#f4f6f9")
        
        # Sidebar
        self.sidebar = tk.Frame(self, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")
        
        self.content_frame = tk.Frame(self, bg="#f4f6f9")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        self.frames = {}
        
        self.create_sidebar_buttons()
        self.create_dashboard_frame()
        self.create_transaction_frame()
        self.create_stats_frame()
        
        self.show_frame("Dashboard")

    def create_sidebar_buttons(self):
        title = tk.Label(self.sidebar, text="MoneyManager", fg="white", bg="#2c3e50", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        buttons = ["Tổng quan", "Giao dịch", "Thống kê"]
        frame_names = ["Dashboard", "Transactions", "Stats"]
        for btn_text, f_name in zip(buttons, frame_names):
            btn = tk.Button(self.sidebar, text=btn_text, bg="#34495e", fg="white", font=("Arial", 12), 
                            relief="flat", command=lambda n=f_name: self.show_frame(n))
            btn.pack(fill="x", pady=5, padx=10)

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
        if name == "Dashboard":
            self.update_dashboard()
        elif name == "Transactions":
            self.update_transaction_list()
        elif name == "Stats":
            self.update_stats()

    def create_dashboard_frame(self):
        frame = tk.Frame(self.content_frame, bg="#f4f6f9")
        self.frames["Dashboard"] = frame
        
        tk.Label(frame, text="Tổng quan Tài chính", font=("Arial", 20, "bold"), bg="#f4f6f9").pack(pady=20)
        
        self.summary_frame = tk.Frame(frame, bg="#f4f6f9")
        self.summary_frame.pack(fill="x", padx=20)
        
        self.lbl_thu = tk.Label(self.summary_frame, text="Tổng thu: 0đ", font=("Arial", 16), fg="green", bg="white", width=20, pady=20, relief="solid", bd=1)
        self.lbl_thu.grid(row=0, column=0, padx=10)
        
        self.lbl_chi = tk.Label(self.summary_frame, text="Tổng chi: 0đ", font=("Arial", 16), fg="red", bg="white", width=20, pady=20, relief="solid", bd=1)
        self.lbl_chi.grid(row=0, column=1, padx=10)
        
        self.lbl_du = tk.Label(self.summary_frame, text="Số dư: 0đ", font=("Arial", 16, "bold"), fg="blue", bg="white", width=20, pady=20, relief="solid", bd=1)
        self.lbl_du.grid(row=0, column=2, padx=10)

    def update_dashboard(self):
        summary = Transaction.get_summary()
        thu = summary.get('Thu', 0) or 0
        chi = summary.get('Chi', 0) or 0
        du = thu - chi
        
        self.lbl_thu.config(text=f"Tổng thu:\\n{thu:,.0f}đ")
        self.lbl_chi.config(text=f"Tổng chi:\\n{chi:,.0f}đ")
        self.lbl_du.config(text=f"Số dư:\\n{du:,.0f}đ")

    def create_transaction_frame(self):
        frame = tk.Frame(self.content_frame, bg="#f4f6f9")
        self.frames["Transactions"] = frame
        
        tk.Label(frame, text="Quản lý Giao dịch", font=("Arial", 20, "bold"), bg="#f4f6f9").pack(pady=10)
        
        # Add form
        form = tk.Frame(frame, bg="white", relief="solid", bd=1, padx=10, pady=10)
        form.pack(fill="x", padx=20, pady=10)
        
        tk.Label(form, text="Loại:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.cb_type = ttk.Combobox(form, values=["Thu", "Chi"], state="readonly")
        self.cb_type.current(1)
        self.cb_type.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form, text="Số tiền:", bg="white").grid(row=0, column=2, padx=5, pady=5)
        self.ent_amount = tk.Entry(form)
        self.ent_amount.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form, text="Danh mục:", bg="white").grid(row=0, column=4, padx=5, pady=5)
        self.cb_cat = ttk.Combobox(form, values=["Ăn uống", "Đi lại", "Mua sắm", "Học tập", "Lương", "Khác"])
        self.cb_cat.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Label(form, text="Nội dung:", bg="white").grid(row=1, column=0, padx=5, pady=5)
        self.ent_desc = tk.Entry(form, width=40)
        self.ent_desc.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        tk.Button(form, text="Thêm giao dịch", bg="#27ae60", fg="white", command=self.add_transaction).grid(row=1, column=4, columnspan=2, pady=5)
        
        # Table
        cols = ("ID", "Ngày", "Loại", "Danh mục", "Số tiền", "Nội dung")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Button(frame, text="Xóa giao dịch chọn", bg="#c0392b", fg="white", command=self.delete_transaction).pack(pady=5)

    def add_transaction(self):
        t_type = self.cb_type.get()
        amount_str = self.ent_amount.get()
        category = self.cb_cat.get()
        desc = self.ent_desc.get()
        date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            amount = float(amount_str)
            Transaction.add(date, t_type, category, amount, desc)
            messagebox.showinfo("Thành công", "Đã thêm giao dịch")
            self.update_transaction_list()
            self.ent_amount.delete(0, tk.END)
            self.ent_desc.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền không hợp lệ")

    def update_transaction_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in Transaction.get_all():
            formatted_row = list(row)
            formatted_row[4] = f"{row[4]:,.0f}đ"
            self.tree.insert("", "end", values=formatted_row)

    def delete_transaction(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        t_id = item['values'][0]
        Transaction.delete(t_id)
        self.update_transaction_list()

    def create_stats_frame(self):
        self.frames["Stats"] = tk.Frame(self.content_frame, bg="#f4f6f9")
        tk.Label(self.frames["Stats"], text="Thống kê chi tiêu", font=("Arial", 20, "bold"), bg="#f4f6f9").pack(pady=10)
        self.chart_frame = tk.Frame(self.frames["Stats"])
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
    def update_stats(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        data = Transaction.get_expenses_by_category()
        if not data:
            tk.Label(self.chart_frame, text="Chưa có dữ liệu chi tiêu").pack()
            return
            
        labels = [row[0] for row in data]
        sizes = [row[1] for row in data]
        
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()
''')

with open(os.path.join(base_dir, "main.py"), "w", encoding="utf-8") as f:
    f.write('''from database import init_db
from gui import AppGUI

if __name__ == "__main__":
    init_db()
    app = AppGUI()
    app.mainloop()
''')
