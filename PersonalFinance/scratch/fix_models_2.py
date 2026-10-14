import codecs
import re

with codecs.open('models.py', 'r', 'utf-8') as f:
    text = f.read()

# Remove the wrongly injected code
text = re.sub(r'\s*@staticmethod\s*def get_daily_stats.*?ORDER BY id DESC", \(date_str,\)\)', '', text, flags=re.DOTALL)

stats_code = """
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
"""

# Inject right before class Budget
text = text.replace('class Budget:', stats_code + '\nclass Budget:')

with codecs.open('models.py', 'w', 'utf-8') as f:
    f.write(text)
