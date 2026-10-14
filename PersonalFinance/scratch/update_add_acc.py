import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

old_ent = '        ent_name = add_field("Tên tài khoản", tk.Entry, insertbackground=theme.PRIMARY)'
new_cb = '''        cb_name = add_field("Tên tài khoản (Có thể chọn hoặc tự gõ)", ttk.Combobox, values=[
            "Vietcombank", "Techcombank", "MB Bank", "ACB", "BIDV", "VietinBank", "TPBank", 
            "Momo", "ZaloPay", "VNPay", "Viettel Money", "ShopeePay", "Tiền mặt", "Agribank", "Sacombank"
        ])'''

text = text.replace(old_ent, new_cb)
text = text.replace('ent_name.insert(0, name)', 'cb_name.set(name)')
text = text.replace('name = ent_name.get().strip()', 'name = cb_name.get().strip()')

# Also wait, when add_field encounters ttk.Combobox, it sets state="readonly".
# If state="readonly", users cannot type custom names!
# I need to modify `add_field` inside `open_add_account_modal` to NOT enforce state="readonly" if it's the name.
# Or just modify `add_field` to accept state as a kwarg.

# Look at add_field inside open_add_account_modal:
'''
        def add_field(label_text, widget_class, **kwargs):
            tk.Label(form, text=label_text, font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(10, 5))
            if widget_class == ttk.Combobox:
                w = ttk.Combobox(form, font=theme.F(12), state="readonly", **kwargs)
'''

old_add_field = '''        def add_field(label_text, widget_class, **kwargs):
            tk.Label(form, text=label_text, font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(10, 5))
            if widget_class == ttk.Combobox:
                w = ttk.Combobox(form, font=theme.F(12), state="readonly", **kwargs)
                w.pack(fill="x", ipady=4)'''

new_add_field = '''        def add_field(label_text, widget_class, **kwargs):
            tk.Label(form, text=label_text, font=theme.F(11, "bold"), fg=theme.TEXT_2, bg=theme.CARD).pack(anchor="w", pady=(10, 5))
            if widget_class == ttk.Combobox:
                state = kwargs.pop("state", "readonly")
                w = ttk.Combobox(form, font=theme.F(12), state=state, **kwargs)
                w.pack(fill="x", ipady=4)'''

text = text.replace(old_add_field, new_add_field)
text = text.replace('cb_type = add_field("Loại", ttk.Combobox, values=["Tiền mặt", "Ngân hàng", "Thẻ", "Ví điện tử", "Tiết kiệm"])',
                    'cb_type = add_field("Loại", ttk.Combobox, values=["Tiền mặt", "Ngân hàng", "Thẻ", "Ví điện tử", "Tiết kiệm"], state="readonly")')
text = text.replace('cb_name = add_field("Tên tài khoản (Có thể chọn hoặc tự gõ)", ttk.Combobox, values=',
                    'cb_name = add_field("Tên tài khoản (Có thể chọn hoặc tự gõ)", ttk.Combobox, state="normal", values=')

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
