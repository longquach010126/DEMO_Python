import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

text = re.sub(r"sqlite3\.connect\(['\"]data/finance\.db['\"]\)", 'database.connect()', text)
# Ensure import database exists
if 'import database' not in text:
    text = text.replace('import sqlite3', 'import sqlite3\n        import database')
    text = text.replace('import sqlite3, csv', 'import sqlite3, csv\n        import database')

# Also, pass username to AppGUI to show on Profile
text = text.replace('def __init__(self):', 'def __init__(self, username="User"):')
text = text.replace('tk.Label(info, text="Quách Bảo Long"', 'tk.Label(info, text=f"Hi, {self.username}"')
text = text.replace('self.current_btn = None', 'self.current_btn = None\n        self.username = username')
text = text.replace('Quách Bảo Long', 'Quách Bảo Long')

# Replace exact occurrences in Profile section:
text = text.replace('text="Quách Bảo Long"', 'text=f"Hi, {self.username}"')

# Also, how to Logout?
# In gui.py build_sidebar, we have btn_logout. 
# We need to add command to btn_logout
logout_cmd = """        def on_logout():
            self.destroy()
            from auth_gui import LoginGUI
            LoginGUI().mainloop()
            
        btn_logout = tk.Button(self.sidebar, text="   Đăng xuất", font=theme.F(12, "bold"), fg=theme.SIDEBAR_TEXT, bg=theme.SIDEBAR,
                            relief="flat", anchor="w", padx=30, cursor="hand2", activebackground=theme.EXPENSE, activeforeground="white",
                            bd=0, highlightthickness=0, command=on_logout)"""

text = text.replace(
    'btn_logout = tk.Button(self.sidebar, text="   Đăng xuất", font=theme.F(12, "bold"), fg=theme.SIDEBAR_TEXT, bg=theme.SIDEBAR,\n                            relief="flat", anchor="w", padx=30, cursor="hand2", activebackground=theme.EXPENSE, activeforeground="white",\n                            bd=0, highlightthickness=0)',
    logout_cmd
)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
