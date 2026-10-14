from database import execute_query, fetch_query

class Transaction:
    @staticmethod
    def add(date, t_type, category, amount, description, note="", method="Tiền mặt", account="Ví tiền mặt"):
        query = "INSERT INTO transactions (date, type, category, amount, description, note, method, account) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        execute_query(query, (date, t_type, category, amount, description, note, method, account))

    @staticmethod
    def update(t_id, date, t_type, category, amount, description, note="", method="Tiền mặt", account="Ví tiền mặt"):
        query = "UPDATE transactions SET date=?, type=?, category=?, amount=?, description=?, note=?, method=?, account=? WHERE id=?"
        execute_query(query, (date, t_type, category, amount, description, note, method, account, t_id))

    @staticmethod
    def search(keyword="", t_type="Tất cả", start_date="", end_date="", category="Tất cả", account="Tất cả"):
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        if keyword:
            query += " AND (description LIKE ? OR note LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if t_type != "Tất cả":
            query += " AND type = ?"
            params.append(t_type)
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category != "Tất cả":
            query += " AND category = ?"
            params.append(category)
        if account != "Tất cả":
            query += " AND account = ?"
            params.append(account)
        query += " ORDER BY date DESC, id DESC"
        return fetch_query(query, tuple(params))

    @staticmethod
    def get_all():
        return fetch_query("SELECT * FROM transactions ORDER BY date DESC")

    @staticmethod
    def get_summary():
        rows = fetch_query("SELECT type, SUM(amount) FROM transactions GROUP BY type")
        summary = {'Thu': 0, 'Chi': 0}
        for r in rows:
            if r[0] == 'Thu': summary['Thu'] = r[1]
            elif r[0] == 'Chi': summary['Chi'] = r[1]
        return summary

    @staticmethod
    def get_expenses_by_category(month_str=None):
        if month_str:
            return fetch_query("SELECT category, SUM(amount) FROM transactions WHERE type='Chi' AND strftime('%Y-%m', date) = ? GROUP BY category", (month_str,))
        return fetch_query("SELECT category, SUM(amount) FROM transactions WHERE type='Chi' GROUP BY category")
        
    @staticmethod
    def get_daily_expenses(month_str):
        query = "SELECT strftime('%d', date), SUM(amount) FROM transactions WHERE type='Chi' AND strftime('%Y-%m', date) = ? GROUP BY date"
        rows = fetch_query(query, (month_str,))
        return {int(r[0]): r[1] for r in rows}

    @staticmethod
    def get_total_balance():
        rows = fetch_query("SELECT type, SUM(amount) FROM transactions GROUP BY type")
        thu, chi = 0, 0
        for r in rows:
            if r[0] == 'Thu': thu = r[1]
            elif r[0] == 'Chi': chi = r[1]
        return thu - chi

    @staticmethod
    def get_monthly_summary(month_str):
        rows = fetch_query("SELECT type, SUM(amount) FROM transactions WHERE strftime('%Y-%m', date) = ? GROUP BY type", (month_str,))
        summary = {'Thu': 0, 'Chi': 0}
        for r in rows:
            if r[0] == 'Thu': summary['Thu'] = r[1]
            elif r[0] == 'Chi': summary['Chi'] = r[1]
        return summary

    @staticmethod
    def get_recent_transactions(limit=5):
        return fetch_query("SELECT id, date, type, category, amount, description, method FROM transactions ORDER BY date DESC, id DESC LIMIT ?", (limit,))

    @staticmethod
    def get_top_expenses(month_str, limit=5):
        return fetch_query("SELECT category, amount, description, date FROM transactions WHERE type='Chi' AND strftime('%Y-%m', date) = ? ORDER BY amount DESC LIMIT ?", (month_str, limit))

    @staticmethod
    def delete(t_id):
        execute_query("DELETE FROM transactions WHERE id = ?", (t_id,))


    @staticmethod
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
        return fetch_query("SELECT id, date, type, category, amount, description, note, account FROM transactions WHERE date = ? ORDER BY id DESC", (date_str,))

class Budget:
    @staticmethod
    def set_budget(month, category, amount):
        rows = fetch_query("SELECT id FROM budgets WHERE month=? AND category=?", (month, category))
        if rows:
            execute_query("UPDATE budgets SET amount=? WHERE id=?", (amount, rows[0][0]))
        else:
            execute_query("INSERT INTO budgets (month, category, amount) VALUES (?, ?, ?)", (month, category, amount))

    @staticmethod
    def get_all(month):
        return fetch_query("SELECT id, category, amount FROM budgets WHERE month=?", (month,))
        
    @staticmethod
    def delete(b_id):
        execute_query("DELETE FROM budgets WHERE id=?", (b_id,))

class Category:
    @staticmethod
    def get_all():
        return fetch_query("SELECT id, name, type, icon, color FROM categories")
        
    @staticmethod
    def get_by_type(t_type):
        return fetch_query("SELECT name, icon, color FROM categories WHERE type = ?", (t_type,))

    @staticmethod
    def add(name, t_type, icon, color):
        query = "INSERT INTO categories (name, type, icon, color) VALUES (?, ?, ?, ?)"
        execute_query(query, (name, t_type, icon, color))

    @staticmethod
    def update(c_id, name, t_type, icon, color):
        execute_query("UPDATE categories SET name=?, type=?, icon=?, color=? WHERE id=?", (name, t_type, icon, color, c_id))

    @staticmethod
    def delete(c_id):
        execute_query("DELETE FROM categories WHERE id=?", (c_id,))

class Setting:
    @staticmethod
    def get(key, default=None):
        rows = fetch_query("SELECT value FROM settings WHERE key = ?", (key,))
        return rows[0][0] if rows else default

    @staticmethod
    def set(key, value):
        execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

class Account:
    @staticmethod
    def get_all():
        return fetch_query("SELECT id, name, type, icon FROM accounts ORDER BY type, name")
        
    @staticmethod
    def add(name, a_type, icon):
        execute_query("INSERT INTO accounts (name, type, icon) VALUES (?, ?, ?)", (name, a_type, icon))
        
    @staticmethod
    def update(a_id, name, a_type, icon):
        execute_query("UPDATE accounts SET name=?, type=?, icon=? WHERE id=?", (name, a_type, icon, a_id))
        
    @staticmethod
    def delete(a_id):
        execute_query("DELETE FROM accounts WHERE id=?", (a_id,))

    @staticmethod
    def get_balances():
        # returns dict of account_name: balance
        rows = fetch_query("SELECT account, type, SUM(amount) FROM transactions GROUP BY account, type")
        balances = {}
        for acc, t_type, amt in rows:
            if acc not in balances: balances[acc] = 0
            if t_type == 'Thu': balances[acc] += amt
            elif t_type == 'Chi': balances[acc] -= amt
        return balances
