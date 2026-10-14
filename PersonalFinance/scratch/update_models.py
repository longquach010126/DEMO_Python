import codecs

with codecs.open('models.py', 'r', 'utf-8') as f:
    text = f.read()

# Update add method
old_add = """    @staticmethod
    def add(date, t_type, category, amount, description, note="", method="Tiền mặt"):
        query = "INSERT INTO transactions (date, type, category, amount, description, note, method) VALUES (?, ?, ?, ?, ?, ?, ?)"
        execute_query(query, (date, t_type, category, amount, description, note, method))"""
new_add = """    @staticmethod
    def add(date, t_type, category, amount, description, note="", method="Tiền mặt", account="Ví tiền mặt"):
        query = "INSERT INTO transactions (date, type, category, amount, description, note, method, account) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        execute_query(query, (date, t_type, category, amount, description, note, method, account))

    @staticmethod
    def update(t_id, date, t_type, category, amount, description, note, method, account):
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
        return fetch_query(query, tuple(params))"""

text = text.replace(old_add, new_add)
text = text.replace('def get_all():\r\n        return fetch_query("SELECT * FROM transactions ORDER BY date DESC")', 'def get_all():\r\n        return fetch_query("SELECT * FROM transactions ORDER BY date DESC")')

with codecs.open('models.py', 'w', 'utf-8') as f:
    f.write(text)
