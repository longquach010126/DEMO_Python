import codecs
with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace any occurrence of self.create_stats()
text = text.replace('self.create_stats()\n', '')
text = text.replace('        self.create_stats()\r\n', '')
text = text.replace('        self.create_stats()\n', '')

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
