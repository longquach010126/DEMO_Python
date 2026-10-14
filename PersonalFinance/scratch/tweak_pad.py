import codecs

with codecs.open('auth_gui.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('self.ent_pass2.pack(fill="x", ipady=8, pady=(0, 10))', 'self.ent_pass2.pack(fill="x", ipady=8, pady=(0, 25))')
text = text.replace('command=self.do_register).pack(fill="x", ipady=10)', 'command=self.do_register).pack(fill="x", pady=(0, 10), ipady=10)')
text = text.replace('btn_back.pack(fill="x", pady=(15, 0)', 'btn_back.pack(fill="x", pady=(0, 0)')

with codecs.open('auth_gui.py', 'w', 'utf-8') as f:
    f.write(text)
