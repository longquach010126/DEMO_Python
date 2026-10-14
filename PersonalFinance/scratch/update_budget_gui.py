import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

start_marker = "    # ============================== BUDGETS =============================="
end_marker = "    # ============================== CATEGORIES =============================="

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

new_code = """    # ============================== BUDGETS ==============================
    def create_budgets(self):
        from datetime import datetime
        now = datetime.now()
        self.budget_month = now.month
        self.budget_year = now.year
        
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Budgets"] = frame
        
        def b_prev():
            self.budget_month -= 1
            if self.budget_month == 0: self.budget_month, self.budget_year = 12, self.budget_year - 1
            self.update_budgets()
            
        def b_next():
            self.budget_month += 1
            if self.budget_month == 13: self.budget_month, self.budget_year = 1, self.budget_year + 1
            self.update_budgets()
            
        def right_action(p):
            nav = tk.Frame(p, bg=theme.BG)
            tk.Button(nav, text="< Trước", bg=theme.CARD, fg=theme.TEXT, relief="flat", font=theme.F(11), padx=15, pady=8, cursor="hand2", command=b_prev).pack(side="left", padx=5)
            self.lbl_budget_month = tk.Label(nav, text="", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.BG, width=12)
            self.lbl_budget_month.pack(side="left", padx=5)
            tk.Button(nav, text="Sau >", bg=theme.CARD, fg=theme.TEXT, relief="flat", font=theme.F(11), padx=15, pady=8, cursor="hand2", command=b_next).pack(side="left", padx=5)
            tk.Button(nav, text="+ Thêm ngân sách", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), relief="flat", padx=15, pady=8, cursor="hand2", command=self.open_add_budget_modal).pack(side="left", padx=(20,0))
            return nav
            
        self._create_header(frame, "Ngân sách", "Lên kế hoạch chi tiêu", right_action)

        self.budg_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.budg_canvas.yview)
        
        self.budg_container = tk.Frame(self.budg_canvas, bg=theme.BG)
        
        self.budg_container.bind("<Configure>", lambda e: self.budg_canvas.configure(scrollregion=self.budg_canvas.bbox("all")))
        def on_canvas_configure(event):
            self.budg_canvas.itemconfig("budg_scroll_frame", width=event.width)
        self.budg_canvas.bind("<Configure>", on_canvas_configure)
        self.budg_canvas.create_window((0, 0), window=self.budg_container, anchor="nw", tags="budg_scroll_frame")
        
        self.budg_canvas.pack(side="left", fill="both", expand=True, padx=(40, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 40))
        self.budg_canvas.configure(yscrollcommand=scrollbar.set)

    def update_budgets(self):
        self.lbl_budget_month.config(text=f"Tháng {self.budget_month}/{self.budget_year}")
        for w in self.budg_container.winfo_children(): w.destroy()
        
        month_str = f"{self.budget_year:04d}-{self.budget_month:02d}"
        
        from models import Budget, Transaction
        budgets = Budget.get_all(month_str)
        expenses = Transaction.get_expenses_by_category(month_str)
        spent_map = {r[0]: r[1] for r in expenses}
        
        if not budgets:
            tk.Label(self.budg_container, text="Chưa có ngân sách nào cho tháng này.", font=theme.F(12), fg=theme.TEXT_2, bg=theme.BG).pack(pady=40)
            return
            
        row_frame = None
        for i, row in enumerate(budgets):
            if i % 3 == 0:
                row_frame = tk.Frame(self.budg_container, bg=theme.BG)
                row_frame.pack(fill="x", pady=(0, 20))
                for c in range(3): row_frame.grid_columnconfigure(c*2, weight=1, uniform="budg")
                for c in range(2): row_frame.grid_columnconfigure(c*2+1, minsize=20)
                
            b_id, cat, limit = row
            spent = spent_map.get(cat, 0)
            rem = limit - spent
            pct = min(100, (spent / limit * 100) if limit > 0 else 100)
            
            card_b, card = self._create_card(row_frame, padding=25)
            card_b.grid(row=0, column=(i%3)*2, sticky="nsew")
            
            icon = theme.cat_info(cat)[0]
            header = tk.Frame(card, bg=theme.CARD)
            header.pack(fill="x")
            tk.Label(header, text=f"{icon} {cat}", font=theme.F(16, "bold"), fg=theme.TEXT, bg=theme.CARD).pack(side="left")
            
            # Colors based on thresholds
            if pct < 80:
                status, color = "Normal", theme.BALANCE
            elif pct < 90:
                status, color = "Warning", theme.WARNING
            elif pct < 100:
                status, color = "Critical", theme.EXPENSE
            else:
                status, color = "Exceeded", theme.EXPENSE
                
            tk.Label(header, text=status, font=theme.F(10, "bold"), fg=color, bg=theme.CARD).pack(side="right")
            
            # Progress bar
            bar_bg = tk.Frame(card, bg=theme.BORDER, height=12)
            bar_bg.pack(fill="x", pady=20)
            if pct > 0:
                bar_fill = tk.Frame(bar_bg, bg=color, height=12)
                bar_fill.place(relwidth=pct/100.0, relheight=1.0)
                
            info = tk.Frame(card, bg=theme.CARD)
            info.pack(fill="x")
            
            def add_stat(label, val_str, v_color):
                col = tk.Frame(info, bg=theme.CARD)
                col.pack(side="left", expand=True, fill="x")
                tk.Label(col, text=label, font=theme.F(10), fg=theme.TEXT_2, bg=theme.CARD).pack()
                tk.Label(col, text=val_str, font=theme.F(11, "bold"), fg=v_color, bg=theme.CARD).pack()
                
            add_stat("Ngân sách", theme.money(limit), theme.TEXT)
            add_stat("Đã chi", theme.money(spent), theme.TEXT)
            add_stat("Còn lại", theme.money(rem), theme.BALANCE if rem >= 0 else theme.EXPENSE)
            add_stat("Tiến độ", f"{pct:.1f}%", color)
            
            for w in (card_b, card, header, info):
                w.bind("<Button-1>", lambda e, r=row: self.open_add_budget_modal(r))
                w.bind("<Enter>", lambda e, cb=card_b: cb.config(cursor="hand2"))

    def open_add_budget_modal(self, edit_row=None):
        modal = tk.Toplevel(self)
        modal.title("Sửa ngân sách" if edit_row else "Thêm ngân sách")
        modal.geometry("400x350" if not edit_row else "400x420")
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - (350 if not edit_row else 420)) // 2
        modal.geometry(f"+{x}+{y}")
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()

        tk.Label(modal, text="Sửa ngân sách" if edit_row else "Thêm ngân sách mới", font=theme.F(18, "bold"), fg=theme.TEXT, bg=theme.CARD).pack(pady=(20, 10))

        form = tk.Frame(modal, bg=theme.CARD, padx=40)
        form.pack(fill="both", expand=True)
        
        tk.Label(form, text=f"Tháng {self.budget_month}/{self.budget_year}", font=theme.F(12, "bold"), fg=theme.PRIMARY, bg=theme.CARD).pack(anchor="w", pady=(0, 10))

        tk.Label(form, text="Danh mục", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(5, 5))
        cats = theme.categories_for("Chi")
        cb_cat = ttk.Combobox(form, values=cats, state="readonly", font=theme.F(12))
        cb_cat.pack(fill="x", ipady=4)
        if cats: cb_cat.current(0)
        
        tk.Label(form, text="Số tiền giới hạn (đ)", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(15, 5))
        ent_amt = tk.Entry(form, font=theme.F(14, "bold"), bg=theme.CARD_ALT, fg=theme.TEXT, relief="flat")
        ent_amt.pack(fill="x", ipady=8, padx=2)

        if edit_row:
            b_id, cat, limit = edit_row
            cb_cat.set(cat)
            ent_amt.insert(0, str(int(limit)))
            
        def save():
            amt_str = ent_amt.get().replace(",", "").replace(".", "")
            if not amt_str:
                messagebox.showerror("Lỗi", "Vui lòng nhập số tiền", parent=modal)
                return
            try:
                amt = float(amt_str)
                if amt <= 0: raise ValueError
                
                from models import Budget
                month_str = f"{self.budget_year:04d}-{self.budget_month:02d}"
                Budget.set_budget(month_str, cb_cat.get(), amt)
                
                self.update_budgets()
                if self.current_btn == self.nav_buttons.get("Dashboard"):
                    self.update_dashboard()
                modal.destroy()
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ", parent=modal)
                
        def delete():
            if messagebox.askyesno("Xóa", "Xóa ngân sách này?", parent=modal):
                from models import Budget
                Budget.delete(edit_row[0])
                self.update_budgets()
                modal.destroy()

        btn_frame = tk.Frame(form, bg=theme.CARD)
        btn_frame.pack(fill="x", pady=(30, 0))
        
        if edit_row:
            tk.Button(btn_frame, text="Xóa", bg=theme.EXPENSE, fg="white", font=theme.F(12, "bold"), relief="flat", cursor="hand2", command=delete).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)
            tk.Button(btn_frame, text="Lưu", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), relief="flat", cursor="hand2", command=save).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)
        else:
            tk.Button(btn_frame, text="Lưu ngân sách", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), relief="flat", cursor="hand2", command=save).pack(fill="x", ipady=10)

"""

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + new_code + text[end_idx:]

# Ensure mousewheel mapping includes Budgets
scroll_update = '''
    def _on_mousewheel(self, event):
        if self.current_btn == self.nav_buttons.get("Dashboard") and hasattr(self, "dash_canvas"):
            self.dash_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Accounts") and hasattr(self, "acc_canvas"):
            self.acc_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Categories") and hasattr(self, "cat_canvas"):
            self.cat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Budgets") and hasattr(self, "budg_canvas"):
            self.budg_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
'''
import re
text = re.sub(
    r'    def _on_mousewheel\(self, event\):.*?elif self\.current_btn == self\.nav_buttons\.get\("Categories"\) and hasattr\(self, "cat_canvas"\):\n\s*self\.cat_canvas\.yview_scroll\(int\(-1\*\(event\.delta/120\)\), "units"\)', 
    scroll_update.strip(), 
    text, 
    flags=re.DOTALL
)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
