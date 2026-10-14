import re
import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    content = f.read()

dashboard_start = content.find("    # ============================== DASHBOARD ==============================")
trans_start = content.find("    # ============================== TRANSACTIONS ==============================")

new_dash_code = """    # ============================== DASHBOARD ==============================
    def create_dashboard(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Dashboard"] = frame
        
        self._create_header(frame, "Xin chào, Long 👋", "Tổng quan tài chính của bạn")

        # Scrollable area
        canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        
        self.dash_scroll_frame = tk.Frame(canvas, bg=theme.BG)
        
        self.dash_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        def on_canvas_configure(event):
            canvas.itemconfig("scroll_frame", width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.create_window((0, 0), window=self.dash_scroll_frame, anchor="nw", tags="scroll_frame")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            if self.frames.get("Dashboard") and self.frames["Dashboard"].winfo_ismapped():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.bind_all("<MouseWheel>", _on_mousewheel)

        # ---------------- KPI Row (1-4)
        kpi_frame = tk.Frame(self.dash_scroll_frame, bg=theme.BG, padx=40)
        kpi_frame.pack(fill="x", pady=(0, 20))
        
        for i in range(4): kpi_frame.grid_columnconfigure(i*2, weight=1, uniform="kpi")
        for i in range(3): kpi_frame.grid_columnconfigure(i*2+1, minsize=15)
        
        self.kpi_labels = {}
        kpis = [
            ("Tổng số dư", theme.BALANCE), 
            ("Thu nhập tháng", theme.INCOME), 
            ("Chi tiêu tháng", theme.EXPENSE), 
            ("Số tiền còn lại", theme.PRIMARY)
        ]
        for i, (title, color) in enumerate(kpis):
            b, c = self._create_card(kpi_frame, padding=20)
            b.grid(row=0, column=i*2, sticky="nsew")
            tk.Label(c, text=title, font=theme.F(11), fg=theme.TEXT_2, bg=theme.CARD, anchor="w").pack(fill="x")
            lbl = tk.Label(c, text="0đ", font=theme.F(18, "bold"), fg=color, bg=theme.CARD, anchor="w")
            lbl.pack(fill="x", pady=(5, 0))
            self.kpi_labels[title] = lbl

        # ---------------- Charts Row 1 (5, 6)
        cr1 = tk.Frame(self.dash_scroll_frame, bg=theme.BG, padx=40)
        cr1.pack(fill="both", expand=True, pady=(0, 20))
        cr1.grid_columnconfigure(0, weight=1, uniform="cr1")
        cr1.grid_columnconfigure(1, minsize=20)
        cr1.grid_columnconfigure(2, weight=1, uniform="cr1")

        b_pie, self.pie_card = self._create_card(cr1, padding=20)
        b_pie.grid(row=0, column=0, sticky="nsew")
        tk.Label(self.pie_card, text="Chi tiêu theo danh mục", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x")
        self.pie_container = tk.Frame(self.pie_card, bg=theme.CARD)
        self.pie_container.pack(fill="both", expand=True, pady=(10, 0))

        b_bar, self.bar_card = self._create_card(cr1, padding=20)
        b_bar.grid(row=0, column=2, sticky="nsew")
        tk.Label(self.bar_card, text="Thu nhập vs Chi tiêu", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x")
        self.bar_container = tk.Frame(self.bar_card, bg=theme.CARD)
        self.bar_container.pack(fill="both", expand=True, pady=(10, 0))

        # ---------------- Charts Row 2 (7, 10)
        cr2 = tk.Frame(self.dash_scroll_frame, bg=theme.BG, padx=40)
        cr2.pack(fill="both", expand=True, pady=(0, 20))
        cr2.grid_columnconfigure(0, weight=1, uniform="cr2")
        cr2.grid_columnconfigure(1, minsize=20)
        cr2.grid_columnconfigure(2, weight=1, uniform="cr2")

        b_line, self.line_card = self._create_card(cr2, padding=20)
        b_line.grid(row=0, column=0, sticky="nsew")
        tk.Label(self.line_card, text="Chi tiêu theo ngày (Tháng này)", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x")
        self.line_container = tk.Frame(self.line_card, bg=theme.CARD)
        self.line_container.pack(fill="both", expand=True, pady=(10, 0))

        b_prog, self.prog_card = self._create_card(cr2, padding=20)
        b_prog.grid(row=0, column=2, sticky="nsew")
        tk.Label(self.prog_card, text="Tiến độ ngân sách", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x")
        self.prog_container = tk.Frame(self.prog_card, bg=theme.CARD)
        self.prog_container.pack(fill="both", expand=True, pady=(10, 0))

        # ---------------- List Row (8, 9)
        lr = tk.Frame(self.dash_scroll_frame, bg=theme.BG, padx=40)
        lr.pack(fill="both", expand=True, pady=(0, 40))
        lr.grid_columnconfigure(0, weight=1, uniform="lr")
        lr.grid_columnconfigure(1, minsize=20)
        lr.grid_columnconfigure(2, weight=1, uniform="lr")

        b_recent, self.recent_card = self._create_card(lr, padding=20)
        b_recent.grid(row=0, column=0, sticky="nsew")
        tk.Label(self.recent_card, text="Giao dịch gần đây", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x")
        self.recent_container = tk.Frame(self.recent_card, bg=theme.CARD)
        self.recent_container.pack(fill="both", expand=True, pady=(10, 0))

        b_top, self.top_card = self._create_card(lr, padding=20)
        b_top.grid(row=0, column=2, sticky="nsew")
        tk.Label(self.top_card, text="Top 5 khoản chi lớn nhất", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w").pack(fill="x")
        self.top_container = tk.Frame(self.top_card, bg=theme.CARD)
        self.top_container.pack(fill="both", expand=True, pady=(10, 0))

    def update_dashboard(self):
        from models import Transaction, Budget
        from datetime import datetime
        
        current_month = datetime.now().strftime("%Y-%m")
        
        # 1-4: KPIs
        total_balance = Transaction.get_total_balance()
        monthly = Transaction.get_monthly_summary(current_month)
        thu = monthly.get('Thu', 0)
        chi = monthly.get('Chi', 0)
        remain = thu - chi
        
        self.kpi_labels["Tổng số dư"].config(text=theme.money(total_balance, sign=True))
        self.kpi_labels["Thu nhập tháng"].config(text=theme.money(thu, sign=True))
        self.kpi_labels["Chi tiêu tháng"].config(text=theme.money(chi))
        self.kpi_labels["Số tiền còn lại"].config(text=theme.money(remain, sign=True))
        
        if not HAS_MATPLOTLIB:
            return
            
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        # 5: Pie chart
        for w in self.pie_container.winfo_children(): w.destroy()
        pie_data = Transaction.get_expenses_by_category(current_month)
        if pie_data:
            fig1 = Figure(figsize=(4, 3), facecolor=theme.CARD)
            ax1 = fig1.add_subplot(111)
            ax1.pie([r[1] for r in pie_data], labels=[r[0] for r in pie_data], 
                   colors=[theme.cat_info(r[0])[1] for r in pie_data], autopct='%1.1f%%', textprops={'fontsize': 9, 'color': theme.TEXT})
            fig1.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
            c1 = FigureCanvasTkAgg(fig1, master=self.pie_container)
            c1.draw()
            c1.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(self.pie_container, text="Chưa có dữ liệu", bg=theme.CARD, fg=theme.TEXT_2).pack(pady=30)
            
        # 6: Bar chart
        for w in self.bar_container.winfo_children(): w.destroy()
        fig2 = Figure(figsize=(4, 3), facecolor=theme.CARD)
        ax2 = fig2.add_subplot(111)
        ax2.bar(['Thu nhập', 'Chi tiêu'], [thu, chi], color=[theme.INCOME, theme.EXPENSE])
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color(theme.MUTED)
        ax2.spines['bottom'].set_color(theme.MUTED)
        ax2.tick_params(colors=theme.TEXT_2)
        fig2.subplots_adjust(left=0.2, bottom=0.15, right=0.95, top=0.95)
        c2 = FigureCanvasTkAgg(fig2, master=self.bar_container)
        c2.draw()
        c2.get_tk_widget().pack(fill="both", expand=True)
        
        # 7: Line chart
        for w in self.line_container.winfo_children(): w.destroy()
        daily = Transaction.get_daily_expenses(current_month)
        if daily:
            days = list(range(1, 32))
            amounts = [daily.get(d, 0) for d in days]
            
            fig3 = Figure(figsize=(4, 3), facecolor=theme.CARD)
            ax3 = fig3.add_subplot(111)
            ax3.plot(days, amounts, color=theme.EXPENSE, marker='o', markersize=4)
            ax3.fill_between(days, amounts, color=theme.EXPENSE, alpha=0.1)
            ax3.spines['top'].set_visible(False)
            ax3.spines['right'].set_visible(False)
            ax3.spines['left'].set_color(theme.MUTED)
            ax3.spines['bottom'].set_color(theme.MUTED)
            ax3.tick_params(colors=theme.TEXT_2)
            fig3.subplots_adjust(left=0.2, bottom=0.15, right=0.95, top=0.95)
            c3 = FigureCanvasTkAgg(fig3, master=self.line_container)
            c3.draw()
            c3.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(self.line_container, text="Chưa có dữ liệu", bg=theme.CARD, fg=theme.TEXT_2).pack(pady=30)
            
        # 10: Budget Progress
        for w in self.prog_container.winfo_children(): w.destroy()
        budgets = Budget.get_all(current_month)
        if budgets:
            for cat, limit in budgets:
                spent = next((r[1] for r in pie_data if r[0] == cat), 0)
                pct = min(100, (spent/limit*100) if limit > 0 else 100)
                f = tk.Frame(self.prog_container, bg=theme.CARD)
                f.pack(fill="x", pady=5)
                tk.Label(f, text=f"{cat} ({theme.money(spent)} / {theme.money(limit)})", font=theme.F(10), bg=theme.CARD, fg=theme.TEXT).pack(anchor="w")
                
                bar_bg = tk.Frame(f, bg=theme.BORDER, height=8)
                bar_bg.pack(fill="x", pady=(2,0))
                fill_color = theme.EXPENSE if pct >= 90 else theme.WARNING if pct >= 70 else theme.PRIMARY
                if pct > 0:
                    bar_fill = tk.Frame(bar_bg, bg=fill_color, height=8)
                    bar_fill.place(relwidth=pct/100.0, relheight=1.0)
        else:
            tk.Label(self.prog_container, text="Chưa có ngân sách nào", bg=theme.CARD, fg=theme.TEXT_2).pack(pady=30)

        # 8: Recent Transactions
        for w in self.recent_container.winfo_children(): w.destroy()
        recent = Transaction.get_recent_transactions(5)
        if recent:
            for t in recent:
                f = tk.Frame(self.recent_container, bg=theme.CARD)
                f.pack(fill="x", pady=4)
                lbl_color = theme.INCOME if t[2] == 'Thu' else theme.EXPENSE
                sign = "+" if t[2] == 'Thu' else "-"
                tk.Label(f, text=t[1][5:], font=theme.F(9), bg=theme.CARD, fg=theme.TEXT_2).pack(side="left")
                tk.Label(f, text=theme.truncate(t[5], 20), font=theme.F(10, "bold"), bg=theme.CARD, fg=theme.TEXT).pack(side="left", padx=10)
                tk.Label(f, text=f"{sign}{theme.money(t[4])}", font=theme.F(10, "bold"), bg=theme.CARD, fg=lbl_color).pack(side="right")
        else:
            tk.Label(self.recent_container, text="Chưa có giao dịch", bg=theme.CARD, fg=theme.TEXT_2).pack(pady=20)

        # 9: Top 5 Largest Expenses
        for w in self.top_container.winfo_children(): w.destroy()
        top = Transaction.get_top_expenses(current_month, 5)
        if top:
            for cat, amt, desc, date in top:
                f = tk.Frame(self.top_container, bg=theme.CARD)
                f.pack(fill="x", pady=4)
                icon, _ = theme.cat_info(cat)
                tk.Label(f, text=icon, font=theme.F(12), bg=theme.CARD).pack(side="left")
                tk.Label(f, text=theme.truncate(desc, 20), font=theme.F(10), bg=theme.CARD, fg=theme.TEXT).pack(side="left", padx=10)
                tk.Label(f, text=theme.money(amt), font=theme.F(10, "bold"), bg=theme.CARD, fg=theme.EXPENSE).pack(side="right")
        else:
            tk.Label(self.top_container, text="Chưa có dữ liệu", bg=theme.CARD, fg=theme.TEXT_2).pack(pady=20)

"""

new_content = content[:dashboard_start] + new_dash_code + content[trans_start:]

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(new_content)

print("Dashboard rewrite complete.")
