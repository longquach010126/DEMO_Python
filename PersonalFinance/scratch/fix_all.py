import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Update open_add_modal signature and logic
old_open_add = """    def open_add_modal(self, edit=False):
        t_id = None
        orig_data = None
        if edit:
            selected = self.tree.selection()
            if not selected: return
            t_id = self.tree.item(selected[0])['values'][0]
            orig_data = next((r for r in Transaction.get_all() if r[0] == t_id), None)
            if not orig_data: return
            
        modal = tk.Toplevel(self)"""

new_open_add = """    def open_add_modal(self, edit=False, edit_data=None, prefill_date=None, is_tree_edit=False):
        t_id = None
        orig_data = None
        if is_tree_edit or edit:
            if not edit_data:
                selected = getattr(self, 'tree', None) and self.tree.selection()
                if not selected: return
                t_id = self.tree.item(selected[0])['values'][0]
                from models import Transaction
                orig_data = next((r for r in Transaction.get_all() if r[0] == t_id), None)
                if not orig_data: return
            else:
                orig_data = edit_data
                t_id = orig_data[0]
            
        modal = tk.Toplevel(self)"""

text = text.replace(old_open_add, new_open_add)

# 2. Update Transactions tab to use open_add_modal(is_tree_edit=True)
# Wait, it currently has open_add_modal(edit=True). The new logic handles edit=True the same as is_tree_edit=True! So it's fine!

# 3. Update Calendar's open_day_modal to use open_add_modal properly and remove FocusIn
# We will replace the entire open_day_modal
match_day = re.search(r'    def open_day_modal.*?modal\.bind\("<FocusIn>", on_focus\)', text, flags=re.DOTALL)

if match_day:
    old_day = match_day.group(0)
    
    new_day = """    def open_day_modal(self, day):
        from models import Transaction
        date_str = f"{self.cal_year:04d}-{self.cal_month:02d}-{day:02d}"
        
        modal = tk.Toplevel(self)
        modal.title(f"Giao dịch ngày {date_str}")
        modal.geometry("700x500")
        modal.configure(bg=theme.BG)
        modal.transient(self)
        modal.grab_set()
        
        header = tk.Frame(modal, bg=theme.CARD, padx=30, pady=20)
        header.pack(fill="x")
        
        tk.Label(header, text=f"Chi tiết ngày {day:02d}/{self.cal_month:02d}/{self.cal_year}", font=theme.F(16, "bold"), fg=theme.TEXT, bg=theme.CARD).pack(side="left")
        
        def refresh_after_edit():
            render_txs()
            self.update_calendar()

        def add_new():
            self.open_add_modal(prefill_date=date_str)
            # Find the modal we just opened and wait for it
            for w in self.winfo_children():
                if isinstance(w, tk.Toplevel) and w != modal:
                    modal.wait_window(w)
                    refresh_after_edit()
                    break
            
        tk.Button(header, text="+ Thêm giao dịch", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), relief="flat", cursor="hand2", padx=15, pady=8, command=add_new).pack(side="right")
        
        list_frame = tk.Frame(modal, bg=theme.BG, padx=30, pady=20)
        list_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(list_frame, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=theme.BG)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas.find_withtag("all")[0], width=e.width))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def render_txs():
            for w in scroll_frame.winfo_children(): w.destroy()
            txs = Transaction.get_by_date(date_str)
            if not txs:
                tk.Label(scroll_frame, text="Không có giao dịch nào trong ngày này.", font=theme.F(12), fg=theme.TEXT_2, bg=theme.BG).pack(pady=40)
                return
                
            for tx in txs:
                t_id, d, r_type, cat, amt, desc, note, acc = tx
                f = tk.Frame(scroll_frame, bg=theme.CARD, padx=20, pady=15)
                f.pack(fill="x", pady=5)
                
                icon = theme.cat_info(cat)[0]
                
                left = tk.Frame(f, bg=theme.CARD)
                left.pack(side="left")
                tk.Label(left, text=f"{icon} {cat}", font=theme.F(13, "bold"), fg=theme.TEXT, bg=theme.CARD).pack(anchor="w")
                tk.Label(left, text=desc, font=theme.F(11), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w")
                
                right = tk.Frame(f, bg=theme.CARD)
                right.pack(side="right")
                
                color = theme.INCOME if r_type == 'Thu' else theme.EXPENSE
                sign = "+" if r_type == 'Thu' else "-"
                tk.Label(right, text=f"{sign}{theme.money(amt)}", font=theme.F(14, "bold"), fg=color, bg=theme.CARD).pack(side="right", padx=(20, 0))
                
                # Edit button
                def edit(t=tx):
                    self.open_add_modal(edit=True, edit_data=t)
                    for w in self.winfo_children():
                        if isinstance(w, tk.Toplevel) and w != modal:
                            modal.wait_window(w)
                            refresh_after_edit()
                            break
                
                tk.Button(right, text="Sửa", bg=theme.BORDER, fg=theme.TEXT, font=theme.F(10), relief="flat", cursor="hand2", padx=10, command=edit).pack(side="right")

        render_txs()"""
        
    text = text.replace(old_day, new_day)

# 4. In open_add_modal, prefill the date if prefill_date is provided
# ent_date.insert(0, datetime.now().strftime("%Y-%m-%d")) -> replace it to use prefill_date
old_date = """        ent_date = add_field("Ngày (YYYY-MM-DD)", tk.Entry, insertbackground=theme.PRIMARY)
        from datetime import datetime
        ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))"""

new_date = """        ent_date = add_field("Ngày (YYYY-MM-DD)", tk.Entry, insertbackground=theme.PRIMARY)
        from datetime import datetime
        ent_date.insert(0, prefill_date if prefill_date else datetime.now().strftime("%Y-%m-%d"))"""

text = text.replace(old_date, new_date)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
