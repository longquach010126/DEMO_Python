import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix in create_transactions
old_cb1 = 'cb_acc = ttk.Combobox(row2, textvariable=self.filter_acc_var, values=["Tất cả", "Ví tiền mặt", "Tài khoản ngân hàng", "Thẻ tín dụng"], state="readonly", width=20)'
new_cb1 = 'self.cb_filter_acc = ttk.Combobox(row2, textvariable=self.filter_acc_var, state="readonly", width=20)\n        self.cb_filter_acc.pack(side="left")'
text = text.replace(old_cb1 + '\n        cb_acc.pack(side="left")', new_cb1)

old_upd_tx = '        cats = ["Tất cả"] + theme.categories_for("Chi") + theme.categories_for("Thu")\n        cats = list(dict.fromkeys(cats))\n        self.cb_filter_cat[\'values\'] = cats'
new_upd_tx = old_upd_tx + '\n        from models import Account\n        accs = ["Tất cả"] + [a[1] for a in Account.get_all()]\n        self.cb_filter_acc[\'values\'] = accs'
text = text.replace(old_upd_tx, new_upd_tx)

# Fix in open_add_modal
old_cb2 = 'cb_acc = add_field("Tài khoản", ttk.Combobox, values=["Ví tiền mặt", "Tài khoản ngân hàng", "Thẻ tín dụng"])'
new_cb2 = 'from models import Account\n        accs = [a[1] for a in Account.get_all()]\n        cb_acc = add_field("Tài khoản", ttk.Combobox, values=accs)'
text = text.replace(old_cb2, new_cb2)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
