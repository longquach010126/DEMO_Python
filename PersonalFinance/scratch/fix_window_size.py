import codecs

with codecs.open('auth_gui.py', 'r', 'utf-8') as f:
    text = f.read()

# Reduce paddings in show_register
text = text.replace('pady=(40, 10)', 'pady=(20, 5)')
text = text.replace('pady=(0, 30)', 'pady=(0, 15)')
text = text.replace('padx=40, pady=40', 'padx=30, pady=20')
text = text.replace('pady=(0, 15)', 'pady=(0, 10)')

# Let's set the geometry to larger just in case
text = text.replace('450x700', '480x750')
text = text.replace('700) // 2', '750) // 2')
text = text.replace('450) // 2', '480) // 2')

with codecs.open('auth_gui.py', 'w', 'utf-8') as f:
    f.write(text)
