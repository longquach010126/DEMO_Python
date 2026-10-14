import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Add "Báo cáo" to sidebar
text = text.replace('("Ngân sách", "Budgets"),', '("Ngân sách", "Budgets"),\n            ("Báo cáo", "Reports"),')

# 2. Add self.create_reports() call
text = text.replace('self.create_settings()', 'self.create_reports()\n        self.create_settings()')

# 3. Add Reports logic at the end before SETTINGS
reports_code = """
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
        
        tk.Button(filter_frame, text="Lọc / Refresh", bg=theme.PRIMARY, fg="white", font=theme.F(11, "bold"), relief="flat", cursor="hand2", padx=15, command=self.update_reports).pack(side="left", padx=(0, 10))
        tk.Button(filter_frame, text="Export CSV", bg=theme.SUCCESS, fg="white", font=theme.F(11, "bold"), relief="flat", cursor="hand2", padx=15, command=self.export_report).pack(side="left")
        
        # Content Canvas
        self.rep_canvas = tk.Frame(frame, bg=theme.BG, padx=40, pady=20)
        self.rep_canvas.pack(fill="both", expand=True)

    def export_report(self):
        messagebox.showinfo("Export", "Đã xuất báo cáo ra file Excel/CSV thành công! (Demo)")

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
        
        conn = sqlite3.connect('data/finance.db')
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
"""

text = text.replace('    # ============================== SETTINGS ==============================', reports_code + '\n    # ============================== SETTINGS ==============================')

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
