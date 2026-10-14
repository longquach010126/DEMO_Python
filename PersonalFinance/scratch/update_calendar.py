import codecs
import re

with codecs.open('models.py', 'r', 'utf-8') as f:
    models_code = f.read()

# Add get_daily_stats to Transaction
stats_code = """    @staticmethod
    def get_daily_stats(month_str):
        query = "SELECT strftime('%d', date), type, SUM(amount) FROM transactions WHERE strftime('%Y-%m', date) = ? GROUP BY date, type"
        rows = fetch_query(query, (month_str,))
        stats = {}
        for r in rows:
            d = int(r[0])
            t_type = r[1]
            amt = r[2]
            if d not in stats: stats[d] = {"Thu": 0, "Chi": 0}
            stats[d][t_type] = amt
        return stats
        
    @staticmethod
    def get_by_date(date_str):
        return fetch_query("SELECT id, date, type, category, amount, description, note, account FROM transactions WHERE date = ? ORDER BY id DESC", (date_str,))"""

models_code = models_code.replace("    @staticmethod\n    def get_daily_expenses(month_str):", stats_code + "\n\n    @staticmethod\n    def get_daily_expenses(month_str):")

with codecs.open('models.py', 'w', 'utf-8') as f:
    f.write(models_code)


with codecs.open('gui.py', 'r', 'utf-8') as f:
    gui_code = f.read()

# Make sure update_calendar is called when saving transactions if Calendar is active
gui_code = gui_code.replace(
    'if self.current_btn == self.nav_buttons.get("Dashboard"):\n                    self.update_dashboard()',
    'if self.current_btn == self.nav_buttons.get("Dashboard"):\n                    self.update_dashboard()\n                elif self.current_btn == self.nav_buttons.get("Calendar"):\n                    self.update_calendar()'
)

# And similarly for delete transaction:
# "if self.current_btn == self.nav_buttons.get("Dashboard"): self.update_dashboard()" (might need to do it)
# I'll just rely on update_calendar being called from the modal.

new_calendar_code = """    # ============================== CALENDAR ==============================
    def create_calendar(self):
        import calendar
        from datetime import datetime
        now = datetime.now()
        self.cal_month, self.cal_year = now.month, now.year
        
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Calendar"] = frame
        
        self.header_frame = tk.Frame(frame, bg=theme.BG)
        self.header_frame.pack(fill="x")
        
        self.cal_stats_frame = tk.Frame(frame, bg=theme.BG)
        self.cal_stats_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        b, self.cal_container = self._create_card(frame, padding=20, accent_color=theme.PRIMARY)
        b.pack(fill="both", expand=True, padx=40, pady=(0, 40))

    def cal_prev(self):
        self.cal_month -= 1
        if self.cal_month == 0: self.cal_month, self.cal_year = 12, self.cal_year - 1
        self.update_calendar()
        
    def cal_next(self):
        self.cal_month += 1
        if self.cal_month == 13: self.cal_month, self.cal_year = 1, self.cal_year + 1
        self.update_calendar()
        
    def cal_today(self):
        from datetime import datetime
        now = datetime.now()
        self.cal_month, self.cal_year = now.month, now.year
        self.update_calendar()

    def update_calendar(self):
        from datetime import date
        import calendar
        from models import Transaction
        
        for w in self.header_frame.winfo_children(): w.destroy()
        
        def right_action(p):
            nav = tk.Frame(p, bg=theme.BG)
            tk.Button(nav, text="< Trước", bg=theme.CARD, fg=theme.TEXT, relief="flat", font=theme.F(11), padx=15, pady=8, cursor="hand2", command=self.cal_prev).pack(side="left", padx=5)
            tk.Button(nav, text="Hôm nay", bg=theme.PRIMARY, fg="white", relief="flat", font=theme.F(11, "bold"), padx=15, pady=8, cursor="hand2", command=self.cal_today).pack(side="left", padx=5)
            tk.Button(nav, text="Sau >", bg=theme.CARD, fg=theme.TEXT, relief="flat", font=theme.F(11), padx=15, pady=8, cursor="hand2", command=self.cal_next).pack(side="left", padx=5)
            return nav
            
        self._create_header(self.header_frame, f"Tháng {self.cal_month:02d}/{self.cal_year}", "Theo dõi thu chi theo ngày", right_action)

        month_str = f"{self.cal_year:04d}-{self.cal_month:02d}"
        stats = Transaction.get_daily_stats(month_str)
        
        # Calculate monthly stats
        total_thu = sum([s["Thu"] for s in stats.values()])
        total_chi = sum([s["Chi"] for s in stats.values()])
        max_chi_day = max(stats.keys(), key=lambda d: stats[d]["Chi"], default=0)
        max_chi_val = stats[max_chi_day]["Chi"] if max_chi_day else 0
        
        for w in self.cal_stats_frame.winfo_children(): w.destroy()
        
        def create_stat(parent, title, val, color):
            f = tk.Frame(parent, bg=theme.CARD, padx=20, pady=15)
            f.pack(side="left", expand=True, fill="x", padx=5)
            tk.Label(f, text=title, font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w")
            tk.Label(f, text=val, font=theme.F(14, "bold"), fg=color, bg=theme.CARD).pack(anchor="w", pady=(5, 0))
            
        create_stat(self.cal_stats_frame, "Tổng thu", theme.money(total_thu), theme.INCOME)
        create_stat(self.cal_stats_frame, "Tổng chi", theme.money(total_chi), theme.EXPENSE)
        create_stat(self.cal_stats_frame, "Cân đối", theme.money(total_thu - total_chi), theme.TEXT)
        create_stat(self.cal_stats_frame, "Chi nhiều nhất", f"Ngày {max_chi_day:02d}: {theme.money_short(max_chi_val)}" if max_chi_val > 0 else "Không có", theme.EXPENSE)

        for w in self.cal_container.winfo_children(): w.destroy()
        
        for i, d in enumerate(["T2", "T3", "T4", "T5", "T6", "T7", "CN"]):
            tk.Label(self.cal_container, text=d, font=theme.F(12, "bold"), fg=theme.TEXT_2, bg=theme.CARD).grid(row=0, column=i, pady=(0, 10))
            
        cal_days = calendar.monthcalendar(self.cal_year, self.cal_month)
        today = date.today()
        
        for r, week in enumerate(cal_days):
            self.cal_container.rowconfigure(r+1, weight=1, uniform="row")
            for c, day in enumerate(week):
                cell_bg = theme.CARD
                if day == today.day and self.cal_month == today.month and self.cal_year == today.year:
                    cell_bg = theme.PRIMARY_SOFT
                    
                cell = tk.Frame(self.cal_container, bg=cell_bg, width=120, height=100)
                cell.grid(row=r+1, column=c, padx=5, pady=5, sticky="nsew")
                cell.grid_propagate(False)
                cell.config(highlightbackground=theme.BORDER, highlightthickness=1)
                
                if day != 0:
                    lbl_day = tk.Label(cell, text=str(day), font=theme.F(12, "bold"), fg=theme.TEXT if cell_bg == theme.CARD else theme.PRIMARY, bg=cell_bg)
                    lbl_day.pack(anchor="ne", padx=10, pady=5)
                    
                    if day in stats:
                        if stats[day]["Thu"] > 0:
                            lbl_thu = tk.Label(cell, text=f"+{theme.money_short(stats[day]['Thu'])}", font=theme.F(11, "bold"), fg=theme.INCOME, bg=cell_bg)
                            lbl_thu.pack(anchor="e", padx=10)
                        if stats[day]["Chi"] > 0:
                            lbl_chi = tk.Label(cell, text=f"-{theme.money_short(stats[day]['Chi'])}", font=theme.F(11, "bold"), fg=theme.EXPENSE, bg=cell_bg)
                            lbl_chi.pack(anchor="e", padx=10)
                            
                    # Bind click to open day details
                    def on_click(e, d=day):
                        self.open_day_modal(d)
                        
                    cell.bind("<Button-1>", on_click)
                    lbl_day.bind("<Button-1>", on_click)
                    for child in cell.winfo_children(): child.bind("<Button-1>", on_click)
                    cell.bind("<Enter>", lambda e, c=cell: c.config(cursor="hand2"))
        
        for i in range(7):
            self.cal_container.columnconfigure(i, weight=1, uniform="col")

    def open_day_modal(self, day):
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
        
        def add_new():
            # Create a proxy for open_add_transaction_modal that also updates this modal when done
            self.open_add_transaction_modal()
            # Unfortunately open_add_transaction_modal doesn't block, so we'll just bind FocusIn to refresh this modal.
            
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
                    self.open_add_transaction_modal(t)
                
                tk.Button(right, text="Sửa", bg=theme.BORDER, fg=theme.TEXT, font=theme.F(10), relief="flat", cursor="hand2", padx=10, command=edit).pack(side="right")

        render_txs()
        
        # When returning from add/edit modal, we want to refresh this list and calendar
        def on_focus(e):
            render_txs()
            self.update_calendar()
            
        modal.bind("<FocusIn>", on_focus)
"""

gui_code = re.sub(r'    # ============================== CALENDAR ==============================.*?    # ============================== BUDGETS ==============================', new_calendar_code + '\n    # ============================== BUDGETS ==============================', gui_code, flags=re.DOTALL)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(gui_code)
