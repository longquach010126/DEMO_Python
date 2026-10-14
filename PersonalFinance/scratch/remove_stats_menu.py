import codecs
with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('            ("Thống kê", "Stats"),\n', '')
text = text.replace('            ("Thống kê", "Stats"),\r\n', '')

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
