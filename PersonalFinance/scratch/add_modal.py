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
                state = kwargs.pop("state", "readonly")
                w = ttk.Combobox(form, font=theme.F(12), state=state, **kwargs)
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
        from models import Account
        accs = [a[1] for a in Account.get_all()]
        cb_acc = add_field("Tài khoản", ttk.Combobox, values=accs)
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
                elif self.current_btn == self.nav_buttons.get("Calendar"):
                    self.update_calendar()
                modal.destroy()
            except ValueError as e:
                messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {e}")
                
        tk.Button(form, text="Lưu giao dịch", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), relief="flat", cursor="hand2", command=save).pack(fill="x", pady=20, ipady=10)

    # ============================== CALENDAR ==============================
