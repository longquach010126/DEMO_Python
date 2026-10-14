import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix dash
text = text.replace(
    'self.dash_self.set_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)\n        canvas = self.set_canvas',
    'self.dash_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)\n        canvas = self.dash_canvas'
)

# Fix acc
text = text.replace(
    'self.acc_self.set_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)\n        canvas = self.set_canvas',
    'self.acc_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)\n        canvas = self.acc_canvas'
)

# Fix cat
text = text.replace(
    'self.cat_self.set_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)\n        canvas = self.set_canvas',
    'self.cat_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)'
)

# Fix budg
text = text.replace(
    'self.budg_self.set_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)\n        canvas = self.set_canvas',
    'self.budg_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)'
)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
