import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

new_settings = """    # ============================== SETTINGS ==============================
    def create_settings(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Settings"] = frame
        self._create_header(frame, "Cài đặt & Dữ liệu", "Tùy chỉnh hệ thống và Quản lý cơ sở dữ liệu")

        canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        
        container = tk.Frame(canvas, bg=theme.BG, padx=40)
        
        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        def on_canvas_configure(event):
            canvas.itemconfig("set_scroll_frame", width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.create_window((0, 0), window=container, anchor="nw", tags="set_scroll_frame")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Profile
        prof_b, prof_c = self._create_card(container, padding=20, accent_color=theme.PRIMARY)
        prof_b.pack(fill="x", pady=(0, 20))
        tk.Label(prof_c, text="👤", font=theme.F(30), bg=theme.CARD).pack(side="left", padx=(0, 20))
        info = tk.Frame(prof_c, bg=theme.CARD)
        info.pack(side="left")
        tk.Label(info, text="Quách Bảo Long", font=theme.F(16, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x")
        tk.Label(info, text="Personal Finance v2.0", font=theme.F(11), fg=theme.TEXT_2, bg=theme.CARD, anchor="w").pack(fill="x")

        def create_section(title, icon="⚙️"):
            sec_b, sec_c = self._create_card(container, padding=20)
            sec_b.pack(fill="x", pady=(0, 20))
            tk.Label(sec_c, text=f"{icon} {title}", font=theme.F(14, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x", pady=(0, 15))
            return sec_c

        def add_row(parent, label_text, widget_class=None, **kwargs):
            row = tk.Frame(parent, bg=theme.CARD)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label_text, font=theme.F(11), fg=theme.TEXT, bg=theme.CARD).pack(side="left")
            if widget_class:
                w = widget_class(row, font=theme.F(11), **kwargs)
                w.pack(side="right")
                return w
            return row

        def add_btn_row(parent, label_text, btn_text, cmd, btn_color=theme.PRIMARY):
            row = tk.Frame(parent, bg=theme.CARD)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label_text, font=theme.F(11), fg=theme.TEXT, bg=theme.CARD).pack(side="left")
            tk.Button(row, text=btn_text, font=theme.F(10, "bold"), bg=btn_color, fg="white", relief="flat", cursor="hand2", command=cmd, padx=15).pack(side="right")

        # 1. Appearance
        sec_app = create_section("Giao diện & Khu vực (Appearance)", "🎨")
        cb_theme = add_row(sec_app, "Giao diện (Theme)", ttk.Combobox, values=["Light mode", "Dark mode"], state="readonly", width=15)
        cb_theme.current(0)
        cb_curr = add_row(sec_app, "Tiền tệ (Currency)", ttk.Combobox, values=["VND"], state="readonly", width=15)
        cb_curr.current(0)

        # 2. Database
        sec_db = create_section("Cơ sở dữ liệu (Database)", "🗄️")
        import os
        db_path = os.path.abspath('data/finance.db')
        
        row_path = tk.Frame(sec_db, bg=theme.CARD)
        row_path.pack(fill="x", pady=5)
        tk.Label(row_path, text="Vị trí file DB:", font=theme.F(11), fg=theme.TEXT, bg=theme.CARD).pack(side="left")
        tk.Entry(row_path, font=theme.F(10), fg=theme.TEXT_2, bg=theme.BORDER, relief="flat").pack(side="right", fill="x", expand=True, padx=(20, 0))
        row_path.winfo_children()[1].insert(0, db_path)
        row_path.winfo_children()[1].config(state="readonly")
        
        add_btn_row(sec_db, "Sao lưu an toàn (Backup)", "Backup Database", self.db_backup, theme.SUCCESS)

        # 3. Data
        sec_data = create_section("Dữ liệu (Data)", "💾")
        add_btn_row(sec_data, "Xuất giao dịch ra file CSV", "Export Data", self.data_export)
        add_btn_row(sec_data, "Nhập giao dịch từ file CSV", "Import Data", self.data_import, theme.WARNING)

        # 4. Application
        sec_app = create_section("Ứng dụng (Application)", "📱")
        add_btn_row(sec_app, "Thông tin phần mềm", "About", self.app_about, theme.TEXT_2)
        add_btn_row(sec_app, "Khôi phục cài đặt gốc", "Reset Settings", self.reset_settings, theme.EXPENSE)

    def db_backup(self):
        import shutil, os
        from tkinter import filedialog, messagebox
        db_path = os.path.abspath('data/finance.db')
        if not os.path.exists(db_path):
            messagebox.showerror("Lỗi", "Không tìm thấy file Database!")
            return
            
        dst = filedialog.asksaveasfilename(defaultextension=".sqlite", filetypes=[("SQLite DB", "*.sqlite *.db"), ("All Files", "*.*")], title="Lưu bản sao Database", initialfile="finance_backup.db")
        if dst:
            try:
                shutil.copy2(db_path, dst)
                messagebox.showinfo("Thành công", f"Đã sao chép database an toàn đến:\\n{dst}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể copy file:\\n{e}")

    def data_export(self):
        from tkinter import filedialog, messagebox
        import sqlite3, csv
        dst = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Export Transactions")
        if not dst: return
        try:
            conn = sqlite3.connect('data/finance.db')
            rows = conn.execute("SELECT * FROM transactions").fetchall()
            header = ["ID", "Ngày", "Loại", "Danh mục", "Số tiền", "Mô tả", "Ghi chú", "Tài khoản"]
            with open(dst, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(header)
                w.writerows(rows)
            messagebox.showinfo("Thành công", f"Đã xuất {len(rows)} giao dịch ra CSV.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            
    def data_import(self):
        messagebox.showinfo("Import", "Tính năng Import sẽ được cập nhật trong phiên bản sau để đảm bảo an toàn toàn vẹn dữ liệu (Data Integrity).")

    def app_about(self):
        from tkinter import messagebox
        messagebox.showinfo("Về ứng dụng", "Personal Finance v2.0\\nPhát triển bởi: Quách Bảo Long\\nỨng dụng quản lý tài chính cá nhân với Tkinter & SQLite.")

    def reset_settings(self):
        from tkinter import messagebox
        import sqlite3
        if messagebox.askyesno("Cảnh báo nguy hiểm", "Bạn có chắc chắn muốn Reset ứng dụng?\\nĐiều này sẽ không xóa giao dịch, nhưng sẽ đưa tất cả Cài đặt (Settings) về mặc định.", icon="warning"):
            conn = sqlite3.connect('data/finance.db')
            conn.execute("DELETE FROM settings")
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã khôi phục cài đặt gốc. Vui lòng khởi động lại phần mềm.")

    def update_settings(self):
        pass"""

# Thay thế từ "    # ============================== SETTINGS ==============================" đến hết file
text = re.sub(r'    # ============================== SETTINGS ==============================.*', new_settings, text, flags=re.DOTALL)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
