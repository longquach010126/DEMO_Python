import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

old_save = """        def save():
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
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ", parent=modal)"""

new_save = """        def save():
            import re
            raw = ent_amt.get()
            amt_str = re.sub(r'[^\\d]', '', raw)
            if not amt_str:
                messagebox.showerror("Lỗi", "Vui lòng nhập số tiền hợp lệ (chỉ nhập số)", parent=modal)
                return
            try:
                amt = float(amt_str)
                if amt <= 0: raise ValueError("Số tiền phải lớn hơn 0")
                
                from models import Budget
                month_str = f"{self.budget_year:04d}-{self.budget_month:02d}"
                Budget.set_budget(month_str, cb_cat.get(), amt)
                
                self.update_budgets()
                if self.current_btn == self.nav_buttons.get("Dashboard"):
                    self.update_dashboard()
                modal.destroy()
            except ValueError as e:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ", parent=modal)"""

text = text.replace(old_save, new_save)
text = text.replace(old_save.replace('\n', '\r\n'), new_save.replace('\n', '\r\n'))

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
