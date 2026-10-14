import codecs
import re

with codecs.open('auth_gui.py', 'r', 'utf-8') as f:
    text = f.read()

old_btn = 'btn_back = tk.Button(form, text="Quay lại Đăng nhập", font=theme.F(11), fg=theme.PRIMARY, bg=theme.CARD, relief="flat", cursor="hand2", command=self.create_widgets)\n        btn_back.pack(pady=(20, 0))'
new_btn = 'btn_back = tk.Button(form, text="← Quay lại Đăng nhập", font=theme.F(12, "bold"), fg=theme.TEXT, bg=theme.BORDER, relief="flat", cursor="hand2", command=self.create_widgets)\n        btn_back.pack(fill="x", pady=(15, 0), ipady=10)'

text = text.replace(old_btn, new_btn)

with codecs.open('auth_gui.py', 'w', 'utf-8') as f:
    f.write(text)
