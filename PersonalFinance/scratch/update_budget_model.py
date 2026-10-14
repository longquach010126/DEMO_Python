import codecs

with codecs.open('models.py', 'r', 'utf-8') as f:
    text = f.read()

old_budget = """class Budget:
    @staticmethod
    def set_budget(month, category, amount):
        # Check if exists
        rows = fetch_query("SELECT id FROM budgets WHERE month=? AND category=?", (month, category))
        if rows:
            execute_query("UPDATE budgets SET amount=? WHERE id=?", (amount, rows[0][0]))
        else:
            execute_query("INSERT INTO budgets (month, category, amount) VALUES (?, ?, ?)", (month, category, amount))

    @staticmethod
    def get_all(month):
        return fetch_query("SELECT category, amount FROM budgets WHERE month=?", (month,))"""

new_budget = """class Budget:
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
        execute_query("DELETE FROM budgets WHERE id=?", (b_id,))"""

if "def delete(b_id):" not in text:
    text = text.replace(old_budget, new_budget)
    with codecs.open('models.py', 'w', 'utf-8') as f:
        f.write(text)
