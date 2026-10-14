import codecs
import re

with codecs.open('auth_gui.py', 'r', 'utf-8') as f:
    text = f.read()

old_login_btns = """        tk.Button(form, text="Đăng nhập", font=theme.F(12, "bold"), bg=theme.PRIMARY, fg="white", relief="flat", cursor="hand2", command=self.do_login).pack(fill="x", ipady=10)
        
        btn_reg = tk.Button(form, text="Chưa có tài khoản? Đăng ký ngay", font=theme.F(11), fg=theme.PRIMARY, bg=theme.CARD, relief="flat", cursor="hand2", command=self.show_register)
        btn_reg.pack(pady=(20, 0))"""

new_login_btns = """        btn_frame = tk.Frame(form, bg=theme.CARD)
        btn_frame.pack(fill="x", pady=(10, 0))
        tk.Button(btn_frame, text="Đăng nhập", font=theme.F(12, "bold"), bg=theme.PRIMARY, fg="white", relief="flat", cursor="hand2", command=self.do_login).pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=10)
        tk.Button(btn_frame, text="Đăng ký", font=theme.F(12, "bold"), bg=theme.BALANCE, fg="white", relief="flat", cursor="hand2", command=self.show_register).pack(side="right", fill="x", expand=True, padx=(5, 0), ipady=10)"""

text = text.replace(old_login_btns, new_login_btns)

with codecs.open('auth_gui.py', 'w', 'utf-8') as f:
    f.write(text)
