import codecs
with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('Transaction.get_daily_expenses(self.cal_year, self.cal_month)', 'Transaction.get_daily_expenses(f"{self.cal_year:04d}-{self.cal_month:02d}")')

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
