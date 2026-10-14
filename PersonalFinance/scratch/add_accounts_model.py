import sqlite3
import codecs

# 1. DB
conn = sqlite3.connect('data/finance.db')
conn.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    icon TEXT
)
''')
c = conn.execute('SELECT COUNT(*) FROM accounts')
if c.fetchone()[0] == 0:
    defaults = [
        ('Tiền mặt', 'Tiền mặt', '💵'),
        ('Vietcombank', 'Ngân hàng', '🏦'),
        ('Momo', 'Ví điện tử', '📱')
    ]
    conn.executemany('INSERT INTO accounts (name, type, icon) VALUES (?, ?, ?)', defaults)
    conn.execute('UPDATE transactions SET account="Tiền mặt" WHERE account="Ví tiền mặt"')
conn.commit()
conn.close()

# 2. Add to models.py
with codecs.open('models.py', 'r', 'utf-8') as f:
    models_text = f.read()

account_model = """
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
"""
if "class Account:" not in models_text:
    models_text += account_model
    with codecs.open('models.py', 'w', 'utf-8') as f:
        f.write(models_text)
