import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    gui_text = f.read()

start_marker = "    # ============================== CATEGORIES =============================="
end_marker = "    # ============================== ACCOUNTS =============================="

start_idx = gui_text.find(start_marker)
end_idx = gui_text.find(end_marker)

new_gui_cat = """    # ============================== CATEGORIES ==============================
    def create_categories(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Categories"] = frame
        
        def right_action(p):
            return tk.Button(p, text="+ Thêm danh mục", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), relief="flat", padx=20, pady=10, cursor="hand2", command=self.open_add_category_modal)
            
        self._create_header(frame, "Danh mục", "Quản lý các nhóm thu chi", right_action)
        
        self.cat_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.cat_canvas.yview)
        
        self.cat_container = tk.Frame(self.cat_canvas, bg=theme.BG)
        
        self.cat_container.bind("<Configure>", lambda e: self.cat_canvas.configure(scrollregion=self.cat_canvas.bbox("all")))
        def on_cat_canvas_configure(event):
            self.cat_canvas.itemconfig("cat_scroll_frame", width=event.width)
        self.cat_canvas.bind("<Configure>", on_cat_canvas_configure)
        self.cat_canvas.create_window((0, 0), window=self.cat_container, anchor="nw", tags="cat_scroll_frame")
        
        self.cat_canvas.pack(side="left", fill="both", expand=True, padx=(40, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 40))
        self.cat_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.cat_content_frame = tk.Frame(self.cat_container, bg=theme.BG)
        self.cat_content_frame.pack(fill="both", expand=True)

    def update_categories(self):
        for w in self.cat_content_frame.winfo_children(): w.destroy()
        
        from models import Category
        cats = Category.get_all()
        
        # Split by type
        chi = [c for c in cats if c[2] == 'Chi']
        thu = [c for c in cats if c[2] == 'Thu']
        
        def render_section(title, data):
            tk.Label(self.cat_content_frame, text=title, font=theme.F(16, "bold"), fg=theme.TEXT, bg=theme.BG, anchor="w").pack(fill="x", pady=(20, 10))
            
            row_frame = None
            for i, row in enumerate(data):
                if i % 4 == 0:
                    row_frame = tk.Frame(self.cat_content_frame, bg=theme.BG)
                    row_frame.pack(fill="x", pady=10)
                    for c in range(4): row_frame.grid_columnconfigure(c*2, weight=1, uniform="cat")
                    for c in range(3): row_frame.grid_columnconfigure(c*2+1, minsize=15)
                    
                c_id, name, t_type, icon, color = row
                
                card_b, card = self._create_card(row_frame, padding=15)
                card_b.grid(row=0, column=(i%4)*2, sticky="nsew")
                
                tk.Label(card, text=icon, font=theme.F(24), fg=color, bg=theme.CARD).pack(side="left", padx=(0, 10))
                tk.Label(card, text=name, font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.CARD).pack(side="left")
                
                for w in (card_b, card, card.winfo_children()[0], card.winfo_children()[1]):
                    w.bind("<Button-1>", lambda e, r=row: self.open_add_category_modal(r))
                    w.bind("<Enter>", lambda e, cb=card_b: cb.config(cursor="hand2"))

        if chi: render_section("Chi tiêu", chi)
        if thu: render_section("Thu nhập", thu)

    def open_add_category_modal(self, edit_row=None):
        import tkinter as tk
        from tkinter import ttk, messagebox
        modal = tk.Toplevel(self)
        modal.title("Sửa Danh Mục" if edit_row else "Thêm Danh Mục Mới")
        
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 550) // 2
        modal.geometry(f"400x550+{x}+{y}")
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()

        header_frame = tk.Frame(modal, bg=theme.CARD)
        header_frame.pack(fill="x", pady=20, padx=30)
        
        tk.Label(header_frame, text="Sửa Danh Mục" if edit_row else "Tạo Danh Mục", font=theme.F(18, "bold"), fg=theme.TEXT, bg=theme.CARD).pack(side="left")

        form = tk.Frame(modal, bg=theme.CARD, padx=30)
        form.pack(fill="both", expand=True)

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

        ent_name = add_field("Tên danh mục", tk.Entry, insertbackground=theme.PRIMARY)
        cb_type = add_field("Loại (Thu/Chi)", ttk.Combobox, values=["Chi", "Thu"], state="readonly")
        cb_type.current(0)
        ent_icon = add_field("Biểu tượng (Emoji)", tk.Entry, insertbackground=theme.PRIMARY)
        ent_icon.insert(0, "📦")
        ent_color = add_field("Mã màu (Hex)", tk.Entry, insertbackground=theme.PRIMARY)
        ent_color.insert(0, theme.PRIMARY)

        if edit_row:
            c_id, name, t_type, icon, color = edit_row
            ent_name.insert(0, name)
            cb_type.set(t_type)
            ent_icon.delete(0, tk.END)
            ent_icon.insert(0, icon)
            ent_color.delete(0, tk.END)
            ent_color.insert(0, color)
            
            def check_and_delete():
                from models import Transaction, Category
                import sqlite3
                
                txs = [t for t in Transaction.get_all() if t[3] == name]
                if not txs:
                    if messagebox.askyesno("Xóa", "Bạn có chắc chắn muốn xóa danh mục này?", parent=modal):
                        Category.delete(c_id)
                        self.update_categories()
                        modal.destroy()
                else:
                    # Request replacement
                    rep_modal = tk.Toplevel(modal)
                    rep_modal.title("Chọn danh mục thay thế")
                    rep_modal.geometry("350x250")
                    rep_modal.configure(bg=theme.CARD)
                    rep_modal.transient(modal)
                    rep_modal.grab_set()
                    
                    tk.Label(rep_modal, text=f"Danh mục đang có {len(txs)} giao dịch.", font=theme.F(11), fg=theme.TEXT, bg=theme.CARD).pack(pady=(20, 5))
                    tk.Label(rep_modal, text="Vui lòng chọn danh mục thay thế:", font=theme.F(11), fg=theme.TEXT_2, bg=theme.CARD).pack(pady=5)
                    
                    cats = [c[1] for c in Category.get_all() if c[1] != name and c[2] == t_type]
                    cb_rep = ttk.Combobox(rep_modal, values=cats, state="readonly", font=theme.F(11))
                    cb_rep.pack(pady=10, fill="x", padx=30)
                    if cats: cb_rep.current(0)
                    
                    def do_replace():
                        new_cat = cb_rep.get()
                        if not new_cat: return
                        
                        conn = sqlite3.connect('data/finance.db')
                        conn.execute("UPDATE transactions SET category=? WHERE category=?", (new_cat, name))
                        conn.commit()
                        conn.close()
                        
                        Category.delete(c_id)
                        self.update_categories()
                        self.update_transactions()
                        rep_modal.destroy()
                        modal.destroy()
                        messagebox.showinfo("Thành công", "Đã xóa và chuyển giao dịch!", parent=self)
                        
                    tk.Button(rep_modal, text="Xác nhận", bg=theme.WARNING, fg="white", font=theme.F(11, "bold"), relief="flat", command=do_replace).pack(pady=10, ipadx=10)

            tk.Button(header_frame, text="Xóa", bg=theme.EXPENSE, fg="white", font=theme.F(10, "bold"), relief="flat", padx=15, cursor="hand2", command=check_and_delete).pack(side="right")

        def save():
            new_name = ent_name.get().strip()
            new_t_type = cb_type.get()
            new_icon = ent_icon.get().strip() or "📦"
            new_color = ent_color.get().strip() or theme.PRIMARY
            
            if not new_name:
                messagebox.showerror("Lỗi", "Vui lòng nhập tên danh mục!", parent=modal)
                return
                
            from models import Category
            import sqlite3
            
            if edit_row:
                old_name = edit_row[1]
                Category.update(edit_row[0], new_name, new_t_type, new_icon, new_color)
                if old_name != new_name:
                    conn = sqlite3.connect('data/finance.db')
                    conn.execute("UPDATE transactions SET category=? WHERE category=?", (new_name, old_name))
                    conn.commit()
                    conn.close()
            else:
                Category.add(new_name, new_t_type, new_icon, new_color)
                
            self.update_categories()
            modal.destroy()
            
        tk.Button(form, text="Lưu", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), relief="flat", cursor="hand2", command=save).pack(fill="x", pady=30, ipady=10)

"""

if start_idx != -1 and end_idx != -1:
    gui_text = gui_text[:start_idx] + new_gui_cat + gui_text[end_idx:]
    with codecs.open('gui.py', 'w', 'utf-8') as f:
        f.write(gui_text)
    print("Done writing to gui.py")
