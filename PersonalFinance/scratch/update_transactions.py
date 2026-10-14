import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

start_marker = "    # ============================== TRANSACTIONS =============================="
end_marker = "    # ============================== CALENDAR =============================="

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

new_code = """    # ============================== TRANSACTIONS ==============================
    def create_transactions(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Transactions"] = frame
        
        def right_action(p):
            return tk.Button(p, text="+ Thêm giao dịch", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), relief="flat", padx=20, pady=10, cursor="hand2", command=self.open_add_modal)
            
        self._create_header(frame, "Giao dịch", "Quản lý dòng tiền của bạn", right_action)

        # Filters
        filter_frame = tk.Frame(frame, bg=theme.BG, padx=40)
        filter_frame.pack(fill="x", pady=(0, 20))
        
        row1 = tk.Frame(filter_frame, bg=theme.BG)
        row1.pack(fill="x", pady=5)
        
        tk.Label(row1, text="🔍", font=theme.F(12), bg=theme.BG, fg=theme.TEXT_2).pack(side="left")
        self.search_var = tk.StringVar()
        ent_search = tk.Entry(row1, textvariable=self.search_var, font=theme.F(11), bg=theme.CARD, fg=theme.TEXT, relief="flat", width=30)
        ent_search.pack(side="left", padx=10, ipady=5)
        
        tk.Label(row1, text="Loại:", font=theme.F(11), bg=theme.BG, fg=theme.TEXT_2).pack(side="left", padx=(20, 5))
        self.filter_type_var = tk.StringVar(value="Tất cả")
        cb_type = ttk.Combobox(row1, textvariable=self.filter_type_var, values=["Tất cả", "Thu", "Chi"], state="readonly", width=10)
        cb_type.pack(side="left")

        row2 = tk.Frame(filter_frame, bg=theme.BG)
        row2.pack(fill="x", pady=5)
        
        tk.Label(row2, text="Danh mục:", font=theme.F(11), bg=theme.BG, fg=theme.TEXT_2).pack(side="left", padx=(0, 5))
        self.filter_cat_var = tk.StringVar(value="Tất cả")
        self.cb_filter_cat = ttk.Combobox(row2, textvariable=self.filter_cat_var, state="readonly", width=15)
        self.cb_filter_cat.pack(side="left")
        
        tk.Label(row2, text="Tài khoản:", font=theme.F(11), bg=theme.BG, fg=theme.TEXT_2).pack(side="left", padx=(20, 5))
        self.filter_acc_var = tk.StringVar(value="Tất cả")
        cb_acc = ttk.Combobox(row2, textvariable=self.filter_acc_var, values=["Tất cả", "Ví tiền mặt", "Tài khoản ngân hàng", "Thẻ tín dụng"], state="readonly", width=20)
        cb_acc.pack(side="left")
        
        tk.Label(row2, text="Từ ngày:", font=theme.F(11), bg=theme.BG, fg=theme.TEXT_2).pack(side="left", padx=(20, 5))
        self.filter_start_var = tk.StringVar()
        ent_start = tk.Entry(row2, textvariable=self.filter_start_var, width=12, font=theme.F(10), bg=theme.CARD, relief="flat")
        ent_start.pack(side="left", ipady=3)
        
        tk.Label(row2, text="Đến:", font=theme.F(11), bg=theme.BG, fg=theme.TEXT_2).pack(side="left", padx=(10, 5))
        self.filter_end_var = tk.StringVar()
        ent_end = tk.Entry(row2, textvariable=self.filter_end_var, width=12, font=theme.F(10), bg=theme.CARD, relief="flat")
        ent_end.pack(side="left", ipady=3)
        
        btn_filter = tk.Button(row2, text="Lọc", bg=theme.CARD_ALT, fg=theme.TEXT, font=theme.F(10, "bold"), relief="flat", cursor="hand2", command=self.update_transactions)
        btn_filter.pack(side="left", padx=20, ipady=2, ipadx=10)

        b, c = self._create_card(frame, padding=0, accent_color=theme.PRIMARY)
        b.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        cols = ("ID", "Ngày", "Loại", "Danh mục", "Nội dung", "Tài khoản", "Số tiền")
        self.tree = ttk.Treeview(c, columns=cols, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=0, stretch=tk.NO)
        
        self.tree.heading("Ngày", text="Ngày")
        self.tree.column("Ngày", width=100, anchor="center")

        self.tree.heading("Loại", text="Loại")
        self.tree.column("Loại", width=60, anchor="center")
        
        self.tree.heading("Danh mục", text="Danh mục")
        self.tree.column("Danh mục", width=150, anchor="w")
        
        self.tree.heading("Nội dung", text="Nội dung")
        self.tree.column("Nội dung", width=250, anchor="w")
        
        self.tree.heading("Tài khoản", text="Tài khoản")
        self.tree.column("Tài khoản", width=120, anchor="center")
        
        self.tree.heading("Số tiền", text="Số tiền")
        self.tree.column("Số tiền", width=120, anchor="e")
        
        self.tree.pack(fill="both", expand=True)
        
        action_frame = tk.Frame(frame, bg=theme.BG, padx=40)
        action_frame.pack(fill="x", pady=(0, 40))
        
        btn_del = tk.Button(action_frame, text="Xóa", bg=theme.EXPENSE, fg="white", font=theme.F(10, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", command=self.delete_transaction)
        btn_del.pack(side="right", padx=(10, 0))
        
        btn_edit = tk.Button(action_frame, text="Sửa", bg=theme.WARNING, fg="white", font=theme.F(10, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", command=lambda: self.open_add_modal(edit=True))
        btn_edit.pack(side="right", padx=10)

        btn_view = tk.Button(action_frame, text="Chi tiết", bg=theme.PRIMARY, fg="white", font=theme.F(10, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", command=self.view_detail_modal)
        btn_view.pack(side="right")

    def update_transactions(self):
        cats = ["Tất cả"] + theme.categories_for("Chi") + theme.categories_for("Thu")
        cats = list(dict.fromkeys(cats))
        self.cb_filter_cat['values'] = cats
        
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        keyword = self.search_var.get().strip()
        t_type = self.filter_type_var.get()
        start_date = self.filter_start_var.get().strip()
        end_date = self.filter_end_var.get().strip()
        category = self.filter_cat_var.get()
        account = self.filter_acc_var.get()
        
        for row in Transaction.search(keyword, t_type, start_date, end_date, category, account):
            if len(row) < 9:
                # Fallback if account missing in result
                t_id, d, r_type, cat, amt, desc, note, method = row[0:8]
                acc = method
            else:
                t_id, d, r_type, cat, amt, desc, note, method, acc = row[0:9]
            
            icon = theme.cat_info(cat)[0]
            cat_display = f"{icon}  {cat}"
            amt_display = theme.money(amt, sign=True)
            if r_type == "Chi":
                amt_display = f"-{theme.money(amt)}"
                
            self.tree.insert("", "end", values=(t_id, theme.fmt_date(d), r_type, cat_display, desc, acc, amt_display))

    def view_detail_modal(self):
        selected = self.tree.selection()
        if not selected: return
        t_id = self.tree.item(selected[0])['values'][0]
        
        # Find exact row
        row = next((r for r in Transaction.get_all() if r[0] == t_id), None)
        if not row: return
        
        if len(row) < 9:
            _, d, r_type, cat, amt, desc, note, method = row[0:8]
            acc = method
        else:
            _, d, r_type, cat, amt, desc, note, method, acc = row[0:9]
            
        modal = tk.Toplevel(self)
        modal.title("Chi tiết giao dịch")
        modal.geometry("400x500")
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()
        
        tk.Label(modal, text="Chi tiết giao dịch", font=theme.F(16, "bold"), bg=theme.CARD, fg=theme.TEXT).pack(pady=20)
        f = tk.Frame(modal, bg=theme.CARD, padx=30)
        f.pack(fill="both", expand=True)
        
        def add_row(lbl, val):
            r = tk.Frame(f, bg=theme.CARD)
            r.pack(fill="x", pady=8)
            tk.Label(r, text=lbl, font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD, width=15, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=theme.F(11), fg=theme.TEXT, bg=theme.CARD, anchor="w", wraplength=200).pack(side="left", fill="x")
            
        add_row("Ngày:", d)
        add_row("Loại:", r_type)
        add_row("Danh mục:", cat)
        add_row("Tài khoản:", acc)
        add_row("Số tiền:", theme.money(amt))
        add_row("Nội dung:", desc)
        add_row("Ghi chú:", note)
        
        tk.Button(modal, text="Đóng", bg=theme.CARD_ALT, fg=theme.TEXT, font=theme.F(11), relief="flat", command=modal.destroy).pack(pady=20, ipadx=20, ipady=5)

    def delete_transaction(self):
        selected = self.tree.selection()
        if not selected: return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa?"):
            t_id = self.tree.item(selected[0])['values'][0]
            Transaction.delete(t_id)
            self.update_transactions()

    def open_add_modal(self, edit=False):
        t_id = None
        orig_data = None
        if edit:
            selected = self.tree.selection()
            if not selected: return
            t_id = self.tree.item(selected[0])['values'][0]
            orig_data = next((r for r in Transaction.get_all() if r[0] == t_id), None)
            if not orig_data: return
            
        modal = tk.Toplevel(self)
        modal.title("Sửa giao dịch" if edit else "Thêm giao dịch")
        
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 750) // 2
        modal.geometry(f"500x750+{x}+{y}")
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()
        
        tk.Label(modal, text="Sửa giao dịch" if edit else "Thêm giao dịch mới", font=theme.F(18, "bold"), bg=theme.CARD, fg=theme.TEXT).pack(pady=20)
        
        form = tk.Frame(modal, bg=theme.CARD, padx=40)
        form.pack(fill="both", expand=True)
        
        # Tabs
        type_frame = tk.Frame(form, bg=theme.CARD)
        type_frame.pack(fill="x", pady=(0, 20))
        self.t_type_var = tk.StringVar(value="Chi")
        
        btn_chi = tk.Button(type_frame, text="Chi tiêu", font=theme.F(11, "bold"), relief="flat")
        btn_thu = tk.Button(type_frame, text="Thu nhập", font=theme.F(11, "bold"), relief="flat")
        
        def update_cats():
            cats = theme.categories_for(self.t_type_var.get())
            cb_cat['values'] = cats
            if cats:
                cb_cat.current(0)
            
        def set_type(t):
            self.t_type_var.set(t)
            if t == "Chi":
                btn_chi.config(bg=theme.EXPENSE, fg="white")
                btn_thu.config(bg=theme.BORDER, fg=theme.TEXT_2)
            else:
                btn_thu.config(bg=theme.INCOME, fg="white")
                btn_chi.config(bg=theme.BORDER, fg=theme.TEXT_2)
            update_cats()
            
        btn_chi.config(command=lambda: set_type("Chi"))
        btn_thu.config(command=lambda: set_type("Thu"))
        
        btn_chi.pack(side="left", expand=True, fill="x", padx=(0, 5), ipady=8)
        btn_thu.pack(side="left", expand=True, fill="x", padx=(5, 0), ipady=8)
        
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

        ent_date = add_field("Ngày (YYYY-MM-DD)", tk.Entry, insertbackground=theme.PRIMARY)
        from datetime import datetime
        ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        cb_cat = add_field("Danh mục", ttk.Combobox)
        ent_amount = add_field("Số tiền (đ)", tk.Entry, insertbackground=theme.PRIMARY)
        ent_desc = add_field("Nội dung", tk.Entry, insertbackground=theme.PRIMARY)
        cb_acc = add_field("Tài khoản", ttk.Combobox, values=["Ví tiền mặt", "Tài khoản ngân hàng", "Thẻ tín dụng"])
        cb_acc.current(0)
        ent_note = add_field("Ghi chú", tk.Entry, insertbackground=theme.PRIMARY)
        
        set_type("Chi")
        
        if edit and orig_data:
            if len(orig_data) < 9:
                _, d, r_type, cat, amt, desc, note, method = orig_data[0:8]
                acc = method
            else:
                _, d, r_type, cat, amt, desc, note, method, acc = orig_data[0:9]
                
            set_type(r_type)
            ent_date.delete(0, tk.END)
            ent_date.insert(0, d)
            cb_cat.set(cat)
            ent_amount.insert(0, str(int(amt)))
            ent_desc.insert(0, desc)
            cb_acc.set(acc)
            ent_note.insert(0, note)
        
        def save():
            try:
                # Validation
                date_str = ent_date.get().strip()
                datetime.strptime(date_str, "%Y-%m-%d") # validate date format
                
                amt_str = ent_amount.get().replace(",", "").replace(".", "")
                if not amt_str: raise ValueError("Thiếu số tiền")
                amt = float(amt_str)
                if amt <= 0: raise ValueError("Số tiền phải > 0")
                
                desc = ent_desc.get().strip()
                if not desc:
                    messagebox.showerror("Lỗi", "Vui lòng nhập nội dung!")
                    return
                    
                cat = cb_cat.get()
                acc = cb_acc.get()
                note = ent_note.get().strip()
                
                if edit:
                    Transaction.update(t_id, date_str, self.t_type_var.get(), cat, amt, desc, note, acc, acc)
                else:
                    Transaction.add(date_str, self.t_type_var.get(), cat, amt, desc, note, acc, acc)
                    
                self.update_transactions()
                if self.current_btn == self.nav_buttons.get("Dashboard"):
                    self.update_dashboard()
                modal.destroy()
            except ValueError as e:
                messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {e}")
                
        tk.Button(form, text="Lưu giao dịch", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), relief="flat", cursor="hand2", command=save).pack(fill="x", pady=20, ipady=10)

"""

new_text = text[:start_idx] + new_code + text[end_idx:]

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(new_text)
