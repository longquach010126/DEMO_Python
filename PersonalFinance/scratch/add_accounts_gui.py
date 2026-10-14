import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Add to menus
if '("Tài khoản", "Accounts")' not in text:
    text = text.replace('            ("Cài đặt", "Settings"),', '            ("Tài khoản", "Accounts"),\r\n            ("Cài đặt", "Settings"),')
    if '("Tài khoản", "Accounts")' not in text:
        text = text.replace('            ("Cài đặt", "Settings"),', '            ("Tài khoản", "Accounts"),\n            ("Cài đặt", "Settings"),')

# 2. Add create_accounts call
if 'self.create_accounts()' not in text:
    text = text.replace('        self.create_settings()', '        self.create_accounts()\r\n        self.create_settings()')
    if 'self.create_accounts()' not in text:
        text = text.replace('        self.create_settings()', '        self.create_accounts()\n        self.create_settings()')

# 3. Add Accounts module code at the end (before Settings)
accounts_code = """    # ============================== ACCOUNTS ==============================
    def create_accounts(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Accounts"] = frame
        
        def right_action(p):
            return tk.Button(p, text="+ Thêm tài khoản", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), relief="flat", padx=20, pady=10, cursor="hand2", command=self.open_add_account_modal)
            
        self._create_header(frame, "Tài khoản", "Quản lý dòng tiền của bạn", right_action)

        self.acc_total_lbl = tk.Label(frame, text="Tổng: 0đ", font=theme.F(18, "bold"), fg=theme.TEXT, bg=theme.BG, anchor="e")
        self.acc_total_lbl.pack(fill="x", padx=40, pady=(0, 20))

        # We need a canvas if there are many accounts, but a frame is fine for now, let's use canvas
        canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        
        self.acc_container = tk.Frame(canvas, bg=theme.BG)
        
        self.acc_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        def on_acc_canvas_configure(event):
            canvas.itemconfig("acc_scroll_frame", width=event.width)
        canvas.bind("<Configure>", on_acc_canvas_configure)
        canvas.create_window((0, 0), window=self.acc_container, anchor="nw", tags="acc_scroll_frame")
        
        canvas.pack(side="left", fill="both", expand=True, padx=(40, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 40))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.acc_detail_view = tk.Frame(frame, bg=theme.BG) # For transaction history drill-down
        
    def update_accounts(self):
        self.acc_detail_view.pack_forget()
        
        for w in self.acc_container.winfo_children(): w.destroy()
        
        from models import Account, Transaction
        accounts = Account.get_all()
        balances = Account.get_balances()
        
        total = sum(balances.values())
        self.acc_total_lbl.config(text=f"Tổng: {theme.money(total)}")
        
        row_frame = None
        for i, row in enumerate(accounts):
            a_id, name, a_type, icon = row
            bal = balances.get(name, 0)
            
            if i % 3 == 0:
                row_frame = tk.Frame(self.acc_container, bg=theme.BG)
                row_frame.pack(fill="x", pady=(0, 20))
                for c in range(3): row_frame.grid_columnconfigure(c*2, weight=1, uniform="acc")
                for c in range(2): row_frame.grid_columnconfigure(c*2+1, minsize=20)
                
            card_b, card = self._create_card(row_frame, padding=20)
            card_b.grid(row=0, column=(i%3)*2, sticky="nsew")
            
            icon_lbl = tk.Label(card, text=icon, font=theme.F(28), fg=theme.PRIMARY, bg=theme.CARD)
            icon_lbl.pack(side="left", padx=(0, 15))
            
            info = tk.Frame(card, bg=theme.CARD)
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=name, font=theme.F(14, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x")
            tk.Label(info, text=a_type, font=theme.F(10), fg=theme.TEXT_2, bg=theme.CARD, anchor="w").pack(fill="x", pady=(2, 5))
            tk.Label(info, text=theme.money(bal), font=theme.F(14, "bold"), fg=theme.BALANCE if bal >= 0 else theme.EXPENSE, bg=theme.CARD, anchor="w").pack(fill="x")
            
            for w in (card_b, card, icon_lbl, info):
                w.bind("<Button-1>", lambda e, a=row: self.show_account_detail(a))
                w.bind("<Enter>", lambda e, cb=card_b: cb.config(cursor="hand2"))

    def show_account_detail(self, acc_row):
        a_id, name, a_type, icon = acc_row
        
        modal = tk.Toplevel(self)
        modal.title(f"Tài khoản: {name}")
        modal.geometry("800x600")
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 800) // 2
        y = self.winfo_y() + (self.winfo_height() - 600) // 2
        modal.geometry(f"+{x}+{y}")
        modal.configure(bg=theme.BG)
        modal.transient(self)
        modal.grab_set()
        
        header = tk.Frame(modal, bg=theme.BG, padx=40, pady=20)
        header.pack(fill="x")
        
        tk.Label(header, text=f"{icon} {name}", font=theme.F(20, "bold"), fg=theme.TEXT, bg=theme.BG).pack(side="left")
        
        def del_acc():
            from models import Transaction, Account
            # Check if used
            txs = [t for t in Transaction.get_all() if t[7] == name]
            if txs:
                messagebox.showerror("Lỗi", f"Tài khoản đang có {len(txs)} giao dịch.\\nVui lòng xóa hoặc chuyển các giao dịch này trước khi xóa tài khoản.", parent=modal)
                return
            if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tài khoản này?", parent=modal):
                Account.delete(a_id)
                self.update_accounts()
                modal.destroy()
                
        tk.Button(header, text="Xóa", bg=theme.EXPENSE, fg="white", font=theme.F(10, "bold"), relief="flat", padx=15, cursor="hand2", command=del_acc).pack(side="right", padx=(10,0))
        tk.Button(header, text="Sửa", bg=theme.WARNING, fg="white", font=theme.F(10, "bold"), relief="flat", padx=15, cursor="hand2", command=lambda: [modal.destroy(), self.open_add_account_modal(acc_row)]).pack(side="right")
        
        b, c = self._create_card(modal, padding=0)
        b.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        cols = ("Ngày", "Loại", "Danh mục", "Nội dung", "Số tiền")
        tree = ttk.Treeview(c, columns=cols, show="headings")
        for col in cols: tree.heading(col, text=col)
        tree.column("Ngày", width=100, anchor="center")
        tree.column("Loại", width=60, anchor="center")
        tree.column("Danh mục", width=150, anchor="w")
        tree.column("Nội dung", width=250, anchor="w")
        tree.column("Số tiền", width=120, anchor="e")
        tree.pack(fill="both", expand=True)
        
        from models import Transaction
        txs = [t for t in Transaction.get_all() if t[7] == name]
        for t in txs:
            t_id, d, r_type, cat, amt, desc, note, method = t[0:8]
            amt_display = f"+{theme.money(amt)}" if r_type == 'Thu' else f"-{theme.money(amt)}"
            tree.insert("", "end", values=(theme.fmt_date(d), r_type, cat, desc, amt_display))

    def open_add_account_modal(self, edit_row=None):
        modal = tk.Toplevel(self)
        modal.title("Sửa tài khoản" if edit_row else "Thêm tài khoản")
        modal.geometry("400x500")
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 500) // 2
        modal.geometry(f"+{x}+{y}")
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()
        
        tk.Label(modal, text="Sửa tài khoản" if edit_row else "Thêm tài khoản mới", font=theme.F(16, "bold"), bg=theme.CARD, fg=theme.TEXT).pack(pady=20)
        form = tk.Frame(modal, bg=theme.CARD, padx=40)
        form.pack(fill="both", expand=True)
        
        def add_field(label_text, widget_class, **kwargs):
            tk.Label(form, text=label_text, font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(10, 5))
            if widget_class == ttk.Combobox:
                w = ttk.Combobox(form, font=theme.F(12), state="readonly", **kwargs)
                w.pack(fill="x", ipady=4)
            else:
                f = tk.Frame(form, bg=theme.BORDER, padx=1, pady=1)
                f.pack(fill="x")
                w = widget_class(f, font=theme.F(12), bg=theme.CARD_ALT, fg=theme.TEXT, relief="flat", **kwargs)
                w.pack(fill="x", padx=1, pady=1, ipady=6)
            return w

        ent_name = add_field("Tên tài khoản", tk.Entry, insertbackground=theme.PRIMARY)
        cb_type = add_field("Loại", ttk.Combobox, values=["Tiền mặt", "Ngân hàng", "Thẻ", "Ví điện tử", "Tiết kiệm"])
        cb_type.current(0)
        ent_icon = add_field("Biểu tượng (Emoji)", tk.Entry, insertbackground=theme.PRIMARY)
        ent_icon.insert(0, "💵")
        
        if edit_row:
            a_id, name, a_type, icon = edit_row
            ent_name.insert(0, name)
            cb_type.set(a_type)
            ent_icon.delete(0, tk.END)
            ent_icon.insert(0, icon)
            
        def save():
            name = ent_name.get().strip()
            a_type = cb_type.get()
            icon = ent_icon.get().strip() or "💵"
            
            if not name:
                messagebox.showerror("Lỗi", "Vui lòng nhập tên tài khoản", parent=modal)
                return
                
            from models import Account, Transaction
            try:
                if edit_row:
                    old_name = edit_row[1]
                    Account.update(edit_row[0], name, a_type, icon)
                    if old_name != name:
                        import sqlite3
                        conn = sqlite3.connect('data/finance.db')
                        conn.execute("UPDATE transactions SET account=? WHERE account=?", (name, old_name))
                        conn.commit()
                        conn.close()
                else:
                    Account.add(name, a_type, icon)
                self.update_accounts()
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e), parent=modal)
                
        tk.Button(form, text="Lưu", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), relief="flat", cursor="hand2", command=save).pack(fill="x", pady=30, ipady=10)

"""

if "def create_accounts(" not in text:
    settings_idx = text.find("    # ============================== SETTINGS ==============================")
    text = text[:settings_idx] + accounts_code + text[settings_idx:]

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
