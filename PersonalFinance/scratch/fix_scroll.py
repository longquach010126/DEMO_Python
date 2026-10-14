import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix Dashboard canvas
old_dash_canvas = '''        # Scrollable area
        canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)'''
new_dash_canvas = '''        # Scrollable area
        self.dash_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        canvas = self.dash_canvas
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)'''
text = text.replace(old_dash_canvas, new_dash_canvas)

# Remove Dashboard mousewheel binding
old_dash_mw = '''        def _on_mousewheel(event):
            if self.frames.get("Dashboard") and self.frames["Dashboard"].winfo_ismapped():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.bind_all("<MouseWheel>", _on_mousewheel)'''
text = text.replace(old_dash_mw, '')

# Fix Accounts canvas
old_acc_canvas = '''        # We need a canvas if there are many accounts, but a frame is fine for now, let's use canvas
        canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)'''
new_acc_canvas = '''        # We need a canvas if there are many accounts, but a frame is fine for now, let's use canvas
        self.acc_canvas = tk.Canvas(frame, bg=theme.BG, highlightthickness=0)
        canvas = self.acc_canvas
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)'''
text = text.replace(old_acc_canvas, new_acc_canvas)

# Let's also check if Settings has a canvas? No, settings currently doesn't use canvas, but if it does later...

# Add global scroll handler in __init__
global_mw = '''
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.current_btn == self.nav_buttons.get("Dashboard") and hasattr(self, "dash_canvas"):
            self.dash_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif self.current_btn == self.nav_buttons.get("Accounts") and hasattr(self, "acc_canvas"):
            self.acc_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
    def build_sidebar(self):'''

text = text.replace('\n    def build_sidebar(self):', global_mw)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
