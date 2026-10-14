import codecs

with codecs.open('database.py', 'r', 'utf-8') as f:
    text = f.read()

# Add account to schema definition just in case
text = text.replace('    note TEXT\n);', '    note TEXT,\n    account TEXT DEFAULT \'Ví tiền mặt\'\n);')
text = text.replace('    note TEXT\r\n);', '    note TEXT,\r\n    account TEXT DEFAULT \'Ví tiền mặt\'\r\n);')

# Add ALTER TABLE block
alter_block = '''
        # Nâng cấp CSDL cũ: thêm cột tài khoản nếu chưa có.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(transactions)")}
        if "account" not in columns:
            conn.execute("ALTER TABLE transactions ADD COLUMN account TEXT DEFAULT 'Ví tiền mặt'")
'''
text = text.replace('        if "method" not in columns:', alter_block + '\n        if "method" not in columns:')

with codecs.open('database.py', 'w', 'utf-8') as f:
    f.write(text)
