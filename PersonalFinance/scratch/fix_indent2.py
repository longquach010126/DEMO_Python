import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# Undo all wrong import databases
text = re.sub(r'\n\s*import database', '', text)

# Put it exactly once at the top
# Find the first 'import tkinter as tk'
if 'import database' not in text[:1000]:
    text = text.replace('import tkinter as tk', 'import tkinter as tk\nimport database', 1)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
