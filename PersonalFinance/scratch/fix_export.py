import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

old_func = """    def export_report(self):
        messagebox.showinfo("Export", "Đã xuất báo cáo ra file Excel/CSV thành công! (Demo)")"""

new_func = """    def export_report(self):
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
            
        conn = sqlite3.connect('data/finance.db')
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
                
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo thành công ra file:\\n{filepath}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
        finally:
            conn.close()"""

text = text.replace(old_func, new_func)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
