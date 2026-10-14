import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Ensure Settings canvas is assigned to self.set_canvas
text = text.replace(
    'canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)',
    'self.set_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)\n        canvas = self.set_canvas'
)

# 2. Add Settings and Reports (if it has canvas, wait reports doesn't have scroll canvas, just figure canvas, but I should add settings) to _on_mousewheel
scroll_update = '''    def _on_mousewheel(self, event):
        if self.current_btn == self.nav_buttons.get("Dashboard") and hasattr(self, "dash_canvas"):
            self.dash_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Accounts") and hasattr(self, "acc_canvas"):
            self.acc_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Categories") and hasattr(self, "cat_canvas"):
            self.cat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Budgets") and hasattr(self, "budg_canvas"):
            self.budg_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Settings") and hasattr(self, "set_canvas"):
            self.set_canvas.yview_scroll(int(-1*(event.delta/120)), "units")'''

text = re.sub(
    r'    def _on_mousewheel\(self, event\):.*?elif self\.current_btn == self\.nav_buttons\.get\("Budgets"\) and hasattr\(self, "budg_canvas"\):\n\s*self\.budg_canvas\.yview_scroll\(int\(-1\*\(event\.delta/120\)\), "units"\)', 
    scroll_update.strip('\n'), 
    text, 
    flags=re.DOTALL
)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
