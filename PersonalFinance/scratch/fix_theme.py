import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

inject = """
        import theme
        theme.EXPENSE_CATEGORIES.clear()
        theme.INCOME_CATEGORIES.clear()
        for r in cats:
            if r[2] == 'Chi': theme.EXPENSE_CATEGORIES[r[1]] = (r[3], r[4])
            else: theme.INCOME_CATEGORIES[r[1]] = (r[3], r[4])
"""

text = text.replace("        thu = [c for c in cats if c[2] == 'Thu']", "        thu = [c for c in cats if c[2] == 'Thu']" + inject)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
