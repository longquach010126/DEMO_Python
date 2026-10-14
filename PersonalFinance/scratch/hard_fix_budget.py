import codecs
import re

with codecs.open('models.py', 'r', 'utf-8') as f:
    text = f.read()

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

# Regex substitute the entire Budget class until 'class Category:'
text = re.sub(r'class Budget:.*?class Category:', new_budget + '\n\nclass Category:', text, flags=re.DOTALL)

with codecs.open('models.py', 'w', 'utf-8') as f:
    f.write(text)
