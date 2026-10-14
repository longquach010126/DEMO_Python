import tkinter as tk
import database
from tkinter import ttk, messagebox, simpledialog
from models import Transaction, Budget, Category, Setting
from datetime import datetime, date
import calendar
import theme

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class AppGUI(tk.Tk):
    def __init__(self, username="User"):
        super().__init__()
        self.title("MoneyManager")
        self.geometry("1280x800")
        self.configure(bg=theme.BG)
        self.minsize(1024, 768)
        theme.center_window(self, 1280, 800)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", rowheight=50, font=theme.F(11), borderwidth=0, background=theme.CARD, fieldbackground=theme.CARD, foreground=theme.TEXT)
        self.style.configure("Treeview.Heading", font=theme.F(11, "bold"), background=theme.BG, foreground=theme.TEXT_2, borderwidth=0)
        self.style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) 
        self.style.map('Treeview', background=[('selected', theme.mix(theme.PRIMARY, theme.CARD, 0.9))], foreground=[('selected', theme.PRIMARY)])

        # Sidebar
        self.sidebar = tk.Frame(self, bg=theme.SIDEBAR, width=260)
        self.sidebar.pack(side="left", fill="y")
        
        from models import Category
        for t_type in ("Thu", "Chi"):
            for row in Category.get_by_type(t_type):
                name, icon, color = row
                if t_type == "Chi":
                    theme.EXPENSE_CATEGORIES[name] = (icon, color)
                else:
                    theme.INCOME_CATEGORIES[name] = (icon, color)

        
        # Main Content area
        self.main_content = tk.Frame(self, bg=theme.BG)
        self.main_content.pack(side="left", fill="both", expand=True)
        
        self.frames = {}
        self.current_btn = None
        self.username = username
        self.nav_buttons = {}
        
        self.build_sidebar()
        
        self.create_dashboard()
        self.create_transactions()
        self.create_calendar()
        self.create_budgets()
        self.create_categories()
        self.create_accounts()
        self.create_reports()
        self.create_settings()
        
        self.show_frame("Dashboard", self.nav_buttons["Dashboard"])

        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.current_btn == self.nav_buttons.get("Dashboard") and hasattr(self, "dash_canvas"):
            self.dash_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Accounts") and hasattr(self, "acc_canvas"):
            self.acc_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Categories") and hasattr(self, "cat_canvas"):
            self.cat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Budgets") and hasattr(self, "budg_canvas"):
            self.budg_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Settings") and hasattr(self, "set_canvas"):
            self.set_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
    def build_sidebar(self):
        logo_frame = tk.Frame(self.sidebar, bg=theme.SIDEBAR)
        logo_frame.pack(pady=40, fill="x", padx=30)
        tk.Label(logo_frame, text="MoneyManager", font=theme.F(18, "bold"), fg="#FFFFFF", bg=theme.SIDEBAR, anchor="w").pack(fill="x")
        tk.Label(logo_frame, text="Quản lý chi tiêu", font=theme.F(10), fg=theme.SIDEBAR_TEXT, bg=theme.SIDEBAR, anchor="w").pack(fill="x")

        menus = [
            ("Tổng quan", "Dashboard"),
            ("Giao dịch", "Transactions"),
            ("Lịch", "Calendar"),
            ("Danh mục", "Categories"),
            ("Ngân sách", "Budgets"),
            ("Báo cáo", "Reports"),
            ("Tài khoản", "Accounts"),
            ("Cài đặt", "Settings"),
        ]
        
        for text, frame_name in menus:
            btn = theme.RoundedButton(self.sidebar, text=f"   {text}", font=theme.F(12, "bold"), fg=theme.SIDEBAR_TEXT, bg=theme.SIDEBAR,
                            anchor="w", padx=30, cursor="hand2", activebackground=theme.SIDEBAR_HOVER,
                            parent_bg=theme.SIDEBAR, command=lambda n=frame_name: self.nav_click(n))
            btn.pack(fill="x", pady=8, padx=10)
            self.nav_buttons[frame_name] = btn
            
        btn_logout = theme.RoundedButton(self.sidebar, text="   Đăng xuất", font=theme.F(12, "bold"), fg=theme.SIDEBAR_TEXT, bg=theme.SIDEBAR,
                            anchor="w", padx=30, cursor="hand2", activebackground=theme.SIDEBAR_HOVER,
                            parent_bg=theme.SIDEBAR, command=self.do_logout)
        btn_logout.pack(side="bottom", fill="x", pady=40, padx=10)

    def do_logout(self):
        self.destroy()
        from auth_gui import LoginGUI
        app = LoginGUI()
        app.mainloop()

    def nav_click(self, frame_name):
        self.show_frame(frame_name, self.nav_buttons[frame_name])

    def show_frame(self, name, btn):
        if self.current_btn:
            self.current_btn.config(fg=theme.SIDEBAR_TEXT, bg=theme.SIDEBAR)
        btn.config(fg="#FFFFFF", bg=theme.SIDEBAR_HOVER)
        self.current_btn = btn

        for f in self.frames.values():
            f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
        
        update_func = getattr(self, f"update_{name.lower()}", None)
        if update_func:
            update_func()

    def _create_header(self, parent, title, subtitle="", right_action=None):
        header = tk.Frame(parent, bg=theme.BG, pady=30, padx=40)
        header.pack(fill="x")
        
        left_box = tk.Frame(header, bg=theme.BG)
        left_box.pack(side="left")
        lbl_title = tk.Label(left_box, text=title, font=theme.F(24, "bold"), fg=theme.TEXT, bg=theme.BG, anchor="w")
        lbl_title.pack(fill="x")
        if subtitle:
            tk.Label(left_box, text=subtitle, font=theme.F(11), fg=theme.TEXT_2, bg=theme.BG, anchor="w").pack(fill="x")
            
        if right_action:
            right_action(header).pack(side="right")
        return lbl_title

    def _create_card(self, parent, padding=25, accent_color=None):
        canvas = tk.Canvas(parent, bg=theme.BG, highlightthickness=0)
        
        r = 12
        # Force offset to at least r so inner frame never covers rounded corners
        offset = max(r, padding)
        frame_pad = max(0, padding - r)
        
        card = tk.Frame(canvas, bg=theme.CARD, padx=frame_pad, pady=frame_pad)
        
        def on_resize(event):
            canvas.delete("bg")
            w = event.width
            h = event.height
            
            def draw_round_rect(x1, y1, x2, y2, rad, color, tag):
                if x2 < x1 + 2*rad or y2 < y1 + 2*rad: return
                canvas.create_arc(x1, y1, x1+2*rad, y1+2*rad, start=90, extent=90, fill=color, outline="", tags=tag)
                canvas.create_arc(x2-2*rad, y1, x2, y1+2*rad, start=0, extent=90, fill=color, outline="", tags=tag)
                canvas.create_arc(x1, y2-2*rad, x1+2*rad, y2, start=180, extent=90, fill=color, outline="", tags=tag)
                canvas.create_arc(x2-2*rad, y2-2*rad, x2, y2, start=270, extent=90, fill=color, outline="", tags=tag)
                canvas.create_rectangle(x1+rad, y1, x2-rad, y2, fill=color, outline="", tags=tag)
                canvas.create_rectangle(x1, y1+rad, x2, y2-rad, fill=color, outline="", tags=tag)
            
            # Draw main card background
            draw_round_rect(2, 2, w-2, h-2, r, theme.CARD, "bg")
            
            canvas.coords("content", offset, offset)
            canvas.itemconfig("content", width=max(1, w - 2*offset), height=max(1, h - 2*offset))
            canvas.tag_lower("bg")

        canvas.bind("<Configure>", on_resize)
        canvas.create_window(offset, offset, window=card, anchor="nw", tags="content")
        
        return canvas, card

    # ============================== DASHBOARD ==============================
    def create_dashboard(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Dashboard"] = frame
        
        from models import Setting
        display_name = Setting.get("display_name", self.username)
        self.lbl_dashboard_greeting = self._create_header(frame, f"Xin chào, {display_name} 👋", "Tổng quan tài chính của bạn")

        # Scrollable area
        self.dash_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        canvas = self.dash_canvas
        canvas = self.dash_canvas
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
        from models import Transaction, Budget, Setting
        from datetime import datetime
        
        display_name = Setting.get("display_name", self.username)
        if hasattr(self, 'lbl_dashboard_greeting'):
            self.lbl_dashboard_greeting.config(text=f"Xin chào, {display_name} 👋")
        
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
            for b_id, cat, limit in budgets:
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

    # ============================== TRANSACTIONS ==============================
    def create_transactions(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Transactions"] = frame
        
        def right_action(p):
            return theme.RoundedButton(p, text="+ Thêm giao dịch", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), padx=20, pady=10, cursor="hand2", command=self.open_add_modal)
            
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
        self.cb_filter_acc = ttk.Combobox(row2, textvariable=self.filter_acc_var, state="readonly", width=20)
        self.cb_filter_acc.pack(side="left")
        
        tk.Label(row2, text="Từ ngày:", font=theme.F(11), bg=theme.BG, fg=theme.TEXT_2).pack(side="left", padx=(20, 5))
        self.filter_start_var = tk.StringVar()
        ent_start = tk.Entry(row2, textvariable=self.filter_start_var, width=12, font=theme.F(10), bg=theme.CARD, relief="flat")
        ent_start.pack(side="left", ipady=3)
        
        tk.Label(row2, text="Đến:", font=theme.F(11), bg=theme.BG, fg=theme.TEXT_2).pack(side="left", padx=(10, 5))
        self.filter_end_var = tk.StringVar()
        ent_end = tk.Entry(row2, textvariable=self.filter_end_var, width=12, font=theme.F(10), bg=theme.CARD, relief="flat")
        ent_end.pack(side="left", ipady=3)
        
        btn_filter = theme.RoundedButton(row2, text="Lọc", bg=theme.CARD_ALT, fg=theme.TEXT, font=theme.F(10, "bold"), cursor="hand2", padx=15, pady=6, command=self.update_transactions)
        btn_filter.pack(side="left", padx=20)

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
        
        btn_del = theme.RoundedButton(action_frame, text="Xóa", bg=theme.EXPENSE, fg="white", font=theme.F(10, "bold"), padx=20, pady=8, cursor="hand2", command=self.delete_transaction)
        btn_del.pack(side="right", padx=(10, 0))
        
        btn_edit = theme.RoundedButton(action_frame, text="Sửa", bg=theme.WARNING, fg="white", font=theme.F(10, "bold"), padx=20, pady=8, cursor="hand2", command=lambda: self.open_add_modal(edit=True))
        btn_edit.pack(side="right", padx=10)

        btn_view = theme.RoundedButton(action_frame, text="Chi tiết", bg=theme.PRIMARY, fg="white", font=theme.F(10, "bold"), padx=20, pady=8, cursor="hand2", command=self.view_detail_modal)
        btn_view.pack(side="right")

    def update_transactions(self):
        cats = ["Tất cả"] + theme.categories_for("Chi") + theme.categories_for("Thu")
        cats = list(dict.fromkeys(cats))
        self.cb_filter_cat['values'] = cats
        from models import Account
        accs = ["Tất cả"] + [a[1] for a in Account.get_all()]
        self.cb_filter_acc['values'] = accs
        
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
        theme.center_window(modal, 400, 500, parent=self)
        
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
        
        theme.RoundedButton(modal, text="Đóng", bg=theme.CARD_ALT, fg=theme.TEXT, font=theme.F(11), padx=25, pady=10, command=modal.destroy).pack(pady=20)

    def delete_transaction(self):
        selected = self.tree.selection()
        if not selected: return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa?"):
            t_id = self.tree.item(selected[0])['values'][0]
            Transaction.delete(t_id)
            self.update_transactions()

    def open_add_modal(self, edit=False, edit_data=None, prefill_date=None, is_tree_edit=False):
        from models import Transaction
        t_id = None
        orig_data = None
        if is_tree_edit or edit:
            if not edit_data:
                selected = getattr(self, 'tree', None) and self.tree.selection()
                if not selected: return
                t_id = self.tree.item(selected[0])['values'][0]
                orig_data = next((r for r in Transaction.get_all() if r[0] == t_id), None)
                if not orig_data: return
            else:
                orig_data = edit_data
                t_id = orig_data[0]
            
        modal = tk.Toplevel(self)
        modal.title("Sửa giao dịch" if edit else "Thêm giao dịch")
        modal.geometry("500x750")
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()
        theme.center_window(modal, 500, 750, parent=self)
        
        tk.Label(modal, text="Sửa giao dịch" if edit else "Thêm giao dịch mới", font=theme.F(18, "bold"), bg=theme.CARD, fg=theme.TEXT).pack(pady=20)
        
        form = tk.Frame(modal, bg=theme.CARD, padx=40)
        form.pack(fill="both", expand=True)
        
        # Tabs
        type_frame = tk.Frame(form, bg=theme.CARD)
        type_frame.pack(fill="x", pady=(0, 20))
        type_frame.columnconfigure(0, weight=1, uniform="type_btn")
        type_frame.columnconfigure(1, weight=1, uniform="type_btn")
        self.t_type_var = tk.StringVar(value="Chi")
        
        btn_chi = theme.RoundedButton(type_frame, text="Chi tiêu", font=theme.F(11, "bold"), padx=20, pady=12)
        btn_thu = theme.RoundedButton(type_frame, text="Thu nhập", font=theme.F(11, "bold"), padx=20, pady=12)
        
        def update_cats():
            cats = theme.categories_for(self.t_type_var.get())
            cb_cat['values'] = cats
            if cats:
                cb_cat.current(0)
            
        def set_type(t):
            self.t_type_var.set(t)
            if t == "Chi":
                btn_chi.configure(bg=theme.EXPENSE, fg="white")
                btn_thu.configure(bg=theme.BORDER, fg=theme.TEXT_2)
            else:
                btn_thu.configure(bg=theme.INCOME, fg="white")
                btn_chi.configure(bg=theme.BORDER, fg=theme.TEXT_2)
            update_cats()
            
        btn_chi.configure(command=lambda: set_type("Chi"))
        btn_thu.configure(command=lambda: set_type("Thu"))
        
        btn_chi.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        btn_thu.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
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
        ent_date.insert(0, prefill_date if prefill_date else datetime.now().strftime("%Y-%m-%d"))
        
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
                
        theme.RoundedButton(form, text="Lưu giao dịch", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), cursor="hand2", padx=20, pady=14, command=save).pack(fill="x", pady=20)

    # ============================== CALENDAR ==============================
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
            theme.RoundedButton(nav, text="< Trước", bg=theme.CARD, fg=theme.TEXT, font=theme.F(11), padx=15, pady=8, cursor="hand2", command=self.cal_prev).pack(side="left", padx=5)
            theme.RoundedButton(nav, text="Hôm nay", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), padx=15, pady=8, cursor="hand2", command=self.cal_today).pack(side="left", padx=5)
            theme.RoundedButton(nav, text="Sau >", bg=theme.CARD, fg=theme.TEXT, font=theme.F(11), padx=15, pady=8, cursor="hand2", command=self.cal_next).pack(side="left", padx=5)
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
        theme.center_window(modal, 700, 500, parent=self)
        
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
            
        theme.RoundedButton(header, text="+ Thêm giao dịch", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), cursor="hand2", padx=15, pady=8, command=add_new).pack(side="right")
        
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
                
                theme.RoundedButton(right, text="Sửa", bg=theme.BORDER, fg=theme.TEXT, font=theme.F(10), cursor="hand2", padx=10, pady=5, command=edit).pack(side="right")

        render_txs()

    # ============================== BUDGETS ==============================
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
            theme.RoundedButton(nav, text="< Trước", bg=theme.CARD, fg=theme.TEXT, font=theme.F(11), padx=15, pady=8, cursor="hand2", command=b_prev).pack(side="left", padx=5)
            self.lbl_budget_month = tk.Label(nav, text="", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.BG, width=12)
            self.lbl_budget_month.pack(side="left", padx=5)
            theme.RoundedButton(nav, text="Sau >", bg=theme.CARD, fg=theme.TEXT, font=theme.F(11), padx=15, pady=8, cursor="hand2", command=b_next).pack(side="left", padx=5)
            theme.RoundedButton(nav, text="+ Thêm ngân sách", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), padx=15, pady=8, cursor="hand2", command=self.open_add_budget_modal).pack(side="left", padx=(20,0))
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
        h = 420 if edit_row else 350
        modal.geometry(f"400x{h}")
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()
        theme.center_window(modal, 400, h, parent=self)

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
            import re
            raw = ent_amt.get()
            amt_str = re.sub(r'[^\d]', '', raw)
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
                elif self.current_btn == self.nav_buttons.get("Calendar"):
                    self.update_calendar()
                modal.destroy()
            except ValueError as e:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ", parent=modal)
                
        def delete():
            if messagebox.askyesno("Xóa", "Xóa ngân sách này?", parent=modal):
                from models import Budget
                Budget.delete(edit_row[0])
                self.update_budgets()
                modal.destroy()

        btn_frame = tk.Frame(form, bg=theme.CARD)
        btn_frame.pack(fill="x", pady=(30, 0))
        btn_frame.columnconfigure(0, weight=1, uniform="budg_btn")
        btn_frame.columnconfigure(1, weight=1, uniform="budg_btn")
        
        if edit_row:
            theme.RoundedButton(btn_frame, text="Xóa", bg=theme.EXPENSE, fg="white", font=theme.F(12, "bold"), cursor="hand2", padx=20, pady=12, command=delete).grid(row=0, column=0, sticky="ew", padx=(0, 5))
            theme.RoundedButton(btn_frame, text="Lưu", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), cursor="hand2", padx=20, pady=12, command=save).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        else:
            theme.RoundedButton(btn_frame, text="Lưu ngân sách", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), cursor="hand2", padx=20, pady=14, command=save).grid(row=0, column=0, columnspan=2, sticky="ew")

    # ============================== CATEGORIES ==============================
    def create_categories(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Categories"] = frame
        
        def right_action(p):
            return theme.RoundedButton(p, text="+ Thêm danh mục", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), padx=20, pady=10, cursor="hand2", command=self.open_add_category_modal)
            
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
        import theme
        theme.EXPENSE_CATEGORIES.clear()
        theme.INCOME_CATEGORIES.clear()
        for r in cats:
            if r[2] == 'Chi': theme.EXPENSE_CATEGORIES[r[1]] = (r[3], r[4])
            else: theme.INCOME_CATEGORIES[r[1]] = (r[3], r[4])

        
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
        modal.geometry("400x550")
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()
        theme.center_window(modal, 400, 550, parent=self)

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
                    theme.center_window(rep_modal, 350, 250, parent=modal)
                    
                    tk.Label(rep_modal, text=f"Danh mục đang có {len(txs)} giao dịch.", font=theme.F(11), fg=theme.TEXT, bg=theme.CARD).pack(pady=(20, 5))
                    tk.Label(rep_modal, text="Vui lòng chọn danh mục thay thế:", font=theme.F(11), fg=theme.TEXT_2, bg=theme.CARD).pack(pady=5)
                    
                    cats = [c[1] for c in Category.get_all() if c[1] != name and c[2] == t_type]
                    cb_rep = ttk.Combobox(rep_modal, values=cats, state="readonly", font=theme.F(11))
                    cb_rep.pack(pady=10, fill="x", padx=30)
                    if cats: cb_rep.current(0)
                    
                    def do_replace():
                        new_cat = cb_rep.get()
                        if not new_cat: return
                        
                        conn = database.connect()
                        conn.execute("UPDATE transactions SET category=? WHERE category=?", (new_cat, name))
                        conn.commit()
                        conn.close()
                        
                        Category.delete(c_id)
                        self.update_categories()
                        self.update_transactions()
                        rep_modal.destroy()
                        modal.destroy()
                        messagebox.showinfo("Thành công", "Đã xóa và chuyển giao dịch!", parent=self)
                        
                    theme.RoundedButton(rep_modal, text="Xác nhận", bg=theme.WARNING, fg="white", font=theme.F(11, "bold"), padx=15, pady=8, command=do_replace).pack(pady=10)

            theme.RoundedButton(header_frame, text="Xóa", bg=theme.EXPENSE, fg="white", font=theme.F(10, "bold"), padx=15, pady=6, cursor="hand2", command=check_and_delete).pack(side="right")

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
                    conn = database.connect()
                    conn.execute("UPDATE transactions SET category=? WHERE category=?", (new_name, old_name))
                    conn.commit()
                    conn.close()
            else:
                Category.add(new_name, new_t_type, new_icon, new_color)
                
            self.update_categories()
            modal.destroy()
            
        theme.RoundedButton(form, text="Lưu", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), cursor="hand2", padx=20, pady=14, command=save).pack(fill="x", pady=30)

    # ============================== ACCOUNTS ==============================
    def create_accounts(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Accounts"] = frame
        
        def right_action(p):
            return theme.RoundedButton(p, text="+ Thêm tài khoản", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), padx=20, pady=10, cursor="hand2", command=self.open_add_account_modal)
            
        self._create_header(frame, "Tài khoản", "Quản lý dòng tiền của bạn", right_action)

        self.acc_total_lbl = tk.Label(frame, text="Tổng: 0đ", font=theme.F(18, "bold"), fg=theme.TEXT, bg=theme.BG, anchor="e")
        self.acc_total_lbl.pack(fill="x", padx=40, pady=(0, 20))

        # We need a canvas if there are many accounts, but a frame is fine for now, let's use canvas
        self.acc_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        canvas = self.acc_canvas
        canvas = self.acc_canvas
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
        modal.configure(bg=theme.BG)
        modal.transient(self)
        modal.grab_set()
        theme.center_window(modal, 800, 600, parent=self)
        
        header = tk.Frame(modal, bg=theme.BG, padx=40, pady=20)
        header.pack(fill="x")
        
        tk.Label(header, text=f"{icon} {name}", font=theme.F(20, "bold"), fg=theme.TEXT, bg=theme.BG).pack(side="left")
        
        def del_acc():
            from models import Transaction, Account
            # Check if used
            txs = [t for t in Transaction.get_all() if t[7] == name]
            if txs:
                messagebox.showerror("Lỗi", f"Tài khoản đang có {len(txs)} giao dịch.\nVui lòng xóa hoặc chuyển các giao dịch này trước khi xóa tài khoản.", parent=modal)
                return
            if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tài khoản này?", parent=modal):
                Account.delete(a_id)
                self.update_accounts()
                modal.destroy()
                
        theme.RoundedButton(header, text="Xóa", bg=theme.EXPENSE, fg="white", font=theme.F(10, "bold"), padx=15, pady=6, cursor="hand2", command=del_acc).pack(side="right", padx=(10,0))
        theme.RoundedButton(header, text="Sửa", bg=theme.WARNING, fg="white", font=theme.F(10, "bold"), padx=15, pady=6, cursor="hand2", command=lambda: [modal.destroy(), self.open_add_account_modal(acc_row)]).pack(side="right")
        
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
        modal.configure(bg=theme.CARD)
        modal.transient(self)
        modal.grab_set()
        theme.center_window(modal, 400, 500, parent=self)
        
        tk.Label(modal, text="Sửa tài khoản" if edit_row else "Thêm tài khoản mới", font=theme.F(16, "bold"), bg=theme.CARD, fg=theme.TEXT).pack(pady=20)
        form = tk.Frame(modal, bg=theme.CARD, padx=40)
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

        cb_name = add_field("Tên tài khoản (Có thể chọn hoặc tự gõ)", ttk.Combobox, state="normal", values=[
            "Vietcombank", "Techcombank", "MB Bank", "ACB", "BIDV", "VietinBank", "TPBank", 
            "Momo", "ZaloPay", "VNPay", "Viettel Money", "ShopeePay", "Tiền mặt", "Agribank", "Sacombank"
        ])
        cb_type = add_field("Loại", ttk.Combobox, values=["Tiền mặt", "Ngân hàng", "Thẻ", "Ví điện tử", "Tiết kiệm"], state="readonly")
        cb_type.current(0)
        ent_icon = add_field("Biểu tượng (Emoji)", tk.Entry, insertbackground=theme.PRIMARY)
        ent_icon.insert(0, "💵")
        
        if edit_row:
            a_id, name, a_type, icon = edit_row
            cb_name.set(name)
            cb_type.set(a_type)
            ent_icon.delete(0, tk.END)
            ent_icon.insert(0, icon)
            
        def save():
            name = cb_name.get().strip()
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
                        conn = database.connect()
                        conn.execute("UPDATE transactions SET account=? WHERE account=?", (name, old_name))
                        conn.commit()
                        conn.close()
                else:
                    Account.add(name, a_type, icon)
                self.update_accounts()
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e), parent=modal)
                
        theme.RoundedButton(form, text="Lưu", bg=theme.PRIMARY, fg="white", font=theme.F(12, "bold"), cursor="hand2", padx=20, pady=14, command=save).pack(fill="x", pady=30)


    # ============================== REPORTS ==============================
    def create_reports(self):
        from datetime import datetime
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Reports"] = frame
        
        # Header
        self._create_header(frame, "Báo cáo", "Phân tích và thống kê nâng cao")
        
        # Filters
        filter_frame = tk.Frame(frame, bg=theme.CARD, padx=20, pady=15)
        filter_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        tk.Label(filter_frame, text="Loại báo cáo:", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(side="left", padx=(0, 10))
        
        self.rep_type = ttk.Combobox(filter_frame, values=[
            "1. Chi tiêu theo danh mục", 
            "2. Thu nhập theo danh mục", 
            "3. Chi tiêu theo tháng", 
            "4. Chi tiêu theo ngày", 
            "5. Thu nhập vs Chi tiêu", 
            "6. Top danh mục chi tiêu", 
            "7. Giao dịch lớn nhất"
        ], state="readonly", font=theme.F(11), width=25)
        self.rep_type.current(0)
        self.rep_type.pack(side="left", padx=(0, 20))
        
        tk.Label(filter_frame, text="Tháng/Năm:", font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(side="left", padx=(0, 10))
        self.rep_month = ttk.Combobox(filter_frame, values=["Tất cả", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], state="readonly", font=theme.F(11), width=8)
        self.rep_month.current(0)
        self.rep_month.pack(side="left", padx=(0, 10))
        
        cur_year = datetime.now().year
        self.rep_year = ttk.Combobox(filter_frame, values=[str(cur_year-1), str(cur_year), str(cur_year+1)], state="readonly", font=theme.F(11), width=8)
        self.rep_year.set(str(cur_year))
        self.rep_year.pack(side="left", padx=(0, 20))
        
        theme.RoundedButton(filter_frame, text="Lọc / Refresh", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), cursor="hand2", padx=15, pady=8, command=self.update_reports).pack(side="left", padx=(0, 10))
        theme.RoundedButton(filter_frame, text="Export CSV", bg=theme.BALANCE, fg="white", font=theme.F(11, "bold"), cursor="hand2", padx=15, pady=8, command=self.export_report).pack(side="left")
        
        # Content Canvas
        self.rep_canvas = tk.Frame(frame, bg=theme.BG, padx=40, pady=20)
        self.rep_canvas.pack(fill="both", expand=True)

    def export_report(self):
        rep = self.rep_type.get()
        m = self.rep_month.get()
        y = self.rep_year.get()
        
        month_filter = None if m == "Tất cả" else f"{y}-{m}"
        
        import sqlite3
        import csv
        from tkinter import filedialog, messagebox
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Lưu báo cáo"
        )
        
        if not filepath:
            return
            
        conn = database.connect()
        c = conn.cursor()
        
        try:
            if "1." in rep or "2." in rep:
                t_type = "Chi" if "1." in rep else "Thu"
                if month_filter:
                    c.execute("SELECT category, SUM(amount) FROM transactions WHERE type=? AND strftime('%Y-%m', date)=? GROUP BY category", (t_type, month_filter))
                else:
                    c.execute("SELECT category, SUM(amount) FROM transactions WHERE type=? GROUP BY category", (t_type,))
                rows = c.fetchall()
                header = ["Danh mục", "Tổng số tiền (VND)"]
                
            elif "3." in rep:
                c.execute("SELECT strftime('%Y-%m', date) as m, SUM(amount) FROM transactions WHERE type='Chi' GROUP BY m ORDER BY m")
                rows = c.fetchall()
                header = ["Tháng", "Tổng chi tiêu (VND)"]
                
            elif "4." in rep:
                from datetime import datetime
                if not month_filter: month_filter = f"{datetime.now().year}-{datetime.now().month:02d}"
                c.execute("SELECT date, SUM(amount) FROM transactions WHERE type='Chi' AND strftime('%Y-%m', date)=? GROUP BY date ORDER BY date", (month_filter,))
                rows = c.fetchall()
                header = ["Ngày", "Chi tiêu (VND)"]
                
            elif "5." in rep:
                q = "SELECT type, SUM(amount) FROM transactions"
                p = ()
                if month_filter:
                    q += " WHERE strftime('%Y-%m', date)=?"
                    p = (month_filter,)
                q += " GROUP BY type"
                c.execute(q, p)
                rows = c.fetchall()
                header = ["Loại", "Tổng số tiền (VND)"]
                
            elif "6." in rep:
                q = "SELECT category, SUM(amount) as s FROM transactions WHERE type='Chi'"
                p = ()
                if month_filter:
                    q += " AND strftime('%Y-%m', date)=?"
                    p = (month_filter,)
                q += " GROUP BY category ORDER BY s DESC LIMIT 5"
                c.execute(q, p)
                rows = c.fetchall()
                header = ["Danh mục", "Chi tiêu (VND)"]
                
            elif "7." in rep:
                q = "SELECT description, amount, date FROM transactions WHERE type='Chi'"
                p = ()
                if month_filter:
                    q += " AND strftime('%Y-%m', date)=?"
                    p = (month_filter,)
                q += " ORDER BY amount DESC LIMIT 5"
                c.execute(q, p)
                rows = c.fetchall()
                header = ["Mô tả giao dịch", "Số tiền (VND)", "Ngày"]
                
            # Use utf-8-sig so Excel can open it with correct Vietnamese accents
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
                
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo thành công ra file:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
        finally:
            conn.close()

    def update_reports(self):
        for w in self.rep_canvas.winfo_children(): w.destroy()
        
        rep = self.rep_type.get()
        m = self.rep_month.get()
        y = self.rep_year.get()
        
        month_filter = None if m == "Tất cả" else f"{y}-{m}"
        
        import sqlite3
        from datetime import datetime
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import theme
        
        conn = database.connect()
        c = conn.cursor()
        
        fig = Figure(figsize=(8, 5), dpi=100)
        fig.patch.set_facecolor(theme.CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(theme.CARD)
        ax.tick_params(colors=theme.TEXT)
        for spine in ax.spines.values(): spine.set_color(theme.BORDER)
        
        has_data = False
        
        if "1." in rep or "2." in rep:
            t_type = "Chi" if "1." in rep else "Thu"
            if month_filter:
                c.execute("SELECT category, SUM(amount) FROM transactions WHERE type=? AND strftime('%Y-%m', date)=? GROUP BY category", (t_type, month_filter))
            else:
                c.execute("SELECT category, SUM(amount) FROM transactions WHERE type=? GROUP BY category", (t_type,))
            rows = c.fetchall()
            if rows:
                has_data = True
                labels = [r[0] for r in rows]
                sizes = [r[1] for r in rows]
                colors = [theme.cat_info(lbl)[1] for lbl in labels]
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, textprops={'color': theme.TEXT})
                ax.set_title(f"{'Chi tiêu' if t_type=='Chi' else 'Thu nhập'} theo danh mục", color=theme.TEXT)
                
        elif "3." in rep:
            c.execute("SELECT strftime('%Y-%m', date) as m, SUM(amount) FROM transactions WHERE type='Chi' GROUP BY m ORDER BY m")
            rows = c.fetchall()
            if rows:
                has_data = True
                labels = [r[0] for r in rows]
                vals = [r[1] for r in rows]
                ax.bar(labels, vals, color=theme.EXPENSE)
                ax.set_title("Chi tiêu theo tháng", color=theme.TEXT)
                
        elif "4." in rep:
            if not month_filter: month_filter = f"{datetime.now().year}-{datetime.now().month:02d}"
            c.execute("SELECT strftime('%d', date) as d, SUM(amount) FROM transactions WHERE type='Chi' AND strftime('%Y-%m', date)=? GROUP BY d ORDER BY d", (month_filter,))
            rows = c.fetchall()
            if rows:
                has_data = True
                labels = [r[0] for r in rows]
                vals = [r[1] for r in rows]
                ax.plot(labels, vals, marker='o', color=theme.EXPENSE, linewidth=2)
                ax.set_title(f"Chi tiêu theo ngày trong tháng {month_filter}", color=theme.TEXT)
                
        elif "5." in rep:
            q = "SELECT type, SUM(amount) FROM transactions"
            p = ()
            if month_filter:
                q += " WHERE strftime('%Y-%m', date)=?"
                p = (month_filter,)
            q += " GROUP BY type"
            c.execute(q, p)
            rows = c.fetchall()
            if rows:
                has_data = True
                labels = [r[0] for r in rows]
                vals = [r[1] for r in rows]
                cols = [theme.INCOME if l == 'Thu' else theme.EXPENSE for l in labels]
                ax.bar(labels, vals, color=cols)
                ax.set_title("Thu nhập vs Chi tiêu", color=theme.TEXT)
                
        elif "6." in rep:
            q = "SELECT category, SUM(amount) as s FROM transactions WHERE type='Chi'"
            p = ()
            if month_filter:
                q += " AND strftime('%Y-%m', date)=?"
                p = (month_filter,)
            q += " GROUP BY category ORDER BY s DESC LIMIT 5"
            c.execute(q, p)
            rows = c.fetchall()
            if rows:
                has_data = True
                tk.Label(self.rep_canvas, text="Top 5 Danh mục chi tiêu", font=theme.F(16, "bold"), fg=theme.TEXT, bg=theme.BG).pack(pady=20)
                for r in rows:
                    cat, amt = r[0], r[1]
                    f = tk.Frame(self.rep_canvas, bg=theme.CARD, padx=20, pady=15)
                    f.pack(fill="x", pady=5)
                    tk.Label(f, text=theme.cat_info(cat)[0] + " " + cat, font=theme.F(14, "bold"), fg=theme.TEXT, bg=theme.CARD).pack(side="left")
                    tk.Label(f, text=theme.money(amt), font=theme.F(14, "bold"), fg=theme.EXPENSE, bg=theme.CARD).pack(side="right")
                    
        elif "7." in rep:
            q = "SELECT description, amount, date FROM transactions WHERE type='Chi'"
            p = ()
            if month_filter:
                q += " AND strftime('%Y-%m', date)=?"
                p = (month_filter,)
            q += " ORDER BY amount DESC LIMIT 5"
            c.execute(q, p)
            rows = c.fetchall()
            if rows:
                has_data = True
                tk.Label(self.rep_canvas, text="Top 5 Giao dịch chi tiêu lớn nhất", font=theme.F(16, "bold"), fg=theme.TEXT, bg=theme.BG).pack(pady=20)
                for r in rows:
                    desc, amt, date = r[0], r[1], r[2]
                    f = tk.Frame(self.rep_canvas, bg=theme.CARD, padx=20, pady=15)
                    f.pack(fill="x", pady=5)
                    tk.Label(f, text=desc, font=theme.F(14, "bold"), fg=theme.TEXT, bg=theme.CARD).pack(side="left")
                    tk.Label(f, text=date, font=theme.F(11), fg=theme.TEXT_2, bg=theme.CARD).pack(side="left", padx=20)
                    tk.Label(f, text=theme.money(amt), font=theme.F(14, "bold"), fg=theme.EXPENSE, bg=theme.CARD).pack(side="right")
                    
        conn.close()
        
        if not has_data:
            empty = tk.Frame(self.rep_canvas, bg=theme.BG)
            empty.pack(expand=True)
            tk.Label(empty, text="📭", font=theme.F(50), bg=theme.BG).pack()
            tk.Label(empty, text="Không có dữ liệu cho báo cáo này", font=theme.F(14, "bold"), fg=theme.TEXT_2, bg=theme.BG).pack(pady=10)
        elif "6." not in rep and "7." not in rep:
            canvas = FigureCanvasTkAgg(fig, master=self.rep_canvas)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    # ============================== SETTINGS ==============================
    def create_settings(self):
        frame = tk.Frame(self.main_content, bg=theme.BG)
        self.frames["Settings"] = frame
        self._create_header(frame, "Cài đặt & Dữ liệu", "Tùy chỉnh hệ thống và Quản lý cơ sở dữ liệu")

        self.set_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        canvas = self.set_canvas
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
        from models import Setting
        display_name = Setting.get("display_name", self.username)
        self.lbl_settings_name = tk.Label(info, text=f"Hi, {display_name}", font=theme.F(16, "bold"), fg=theme.TEXT, bg=theme.CARD, anchor="w")
        self.lbl_settings_name.pack(fill="x")
        tk.Label(info, text="Personal Finance v2.0", font=theme.F(11), fg=theme.TEXT_2, bg=theme.CARD, anchor="w").pack(fill="x")
        
        def edit_profile():
            from tkinter import simpledialog
            current = Setting.get("display_name", self.username)
            new_name = simpledialog.askstring("Chỉnh sửa thông tin", "Nhập tên hiển thị mới:", initialvalue=current)
            if new_name and new_name.strip():
                Setting.set("display_name", new_name.strip())
                self.lbl_settings_name.config(text=f"Hi, {new_name.strip()}")
                self.update_dashboard()
                
        theme.RoundedButton(prof_c, text="Chỉnh sửa", font=theme.F(10, "bold"), bg=theme.PRIMARY, fg="white", cursor="hand2", command=edit_profile, padx=15, pady=6).pack(side="right")

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
            theme.RoundedButton(row, text=btn_text, font=theme.F(10, "bold"), bg=btn_color, fg="white", cursor="hand2", command=cmd, padx=15, pady=6).pack(side="right")

        # 1. Data
        sec_data = create_section("Dữ liệu (Data)", "💾")
        add_btn_row(sec_data, "Xuất giao dịch ra file CSV", "Export Data", self.data_export)
        add_btn_row(sec_data, "Nhập giao dịch từ file CSV", "Import Data", self.data_import, theme.WARNING)

        # 2. Application
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
                messagebox.showinfo("Thành công", f"Đã sao chép database an toàn đến:\n{dst}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể copy file:\n{e}")

    def data_export(self):
        from tkinter import filedialog, messagebox
        import sqlite3, csv
        dst = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Export Transactions")
        if not dst: return
        try:
            conn = database.connect()
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
        messagebox.showinfo("Về ứng dụng", "Personal Finance v2.0\nPhát triển bởi: Quách Bảo Long\nỨng dụng quản lý tài chính cá nhân với Tkinter & SQLite.")

    def reset_settings(self):
        from tkinter import messagebox
        import sqlite3
        if messagebox.askyesno("Cảnh báo nguy hiểm", "Bạn có chắc chắn muốn Reset ứng dụng?\nĐiều này sẽ không xóa giao dịch, nhưng sẽ đưa tất cả Cài đặt (Settings) về mặc định.", icon="warning"):
            conn = database.connect()
            conn.execute("DELETE FROM settings")
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã khôi phục cài đặt gốc. Vui lòng khởi động lại phần mềm.")

    def update_settings(self):
        pass
    