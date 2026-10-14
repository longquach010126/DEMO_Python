import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# First, undo the bad replacement by removing all \n\s*import database
text = re.sub(r'\n\s*import database', '', text)

# Now, only insert 'import database' once at the top of the file!
# Let's insert it right after 'import sqlite3' at the top of the file.
# We can just put it at the very beginning of the file (or after imports).
imports = "import tkinter as tk\nfrom tkinter import ttk, messagebox, filedialog, colorchooser\nfrom datetime import datetime, date\nimport sqlite3\nimport csv\nimport matplotlib.pyplot as plt\nfrom matplotlib.backends.backend_tkagg import FigureCanvasTkAgg\nimport theme\nimport database\n"

# replace the imports block at the top if it doesn't have database
if 'import database' not in text[:1000]:
    # find import theme
    text = text.replace('import theme', 'import theme\nimport database')

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
