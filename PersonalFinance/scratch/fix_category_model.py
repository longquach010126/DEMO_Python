import codecs

with codecs.open('models.py', 'r', 'utf-8') as f:
    text = f.read()

old_cat = """class Category:
    @staticmethod
    def get_by_type(t_type):
        return fetch_query("SELECT name, icon, color FROM categories WHERE type = ?", (t_type,))

    @staticmethod
    def add(name, t_type, icon, color):
        query = "INSERT INTO categories (name, type, icon, color) VALUES (?, ?, ?, ?)"
        execute_query(query, (name, t_type, icon, color))"""

new_cat = """class Category:
    @staticmethod
    def get_all():
        return fetch_query("SELECT id, name, type, icon, color FROM categories")
        
    @staticmethod
    def get_by_type(t_type):
        return fetch_query("SELECT name, icon, color FROM categories WHERE type = ?", (t_type,))

    @staticmethod
    def add(name, t_type, icon, color):
        query = "INSERT INTO categories (name, type, icon, color) VALUES (?, ?, ?, ?)"
        execute_query(query, (name, t_type, icon, color))

    @staticmethod
    def update(c_id, name, t_type, icon, color):
        execute_query("UPDATE categories SET name=?, type=?, icon=?, color=? WHERE id=?", (name, t_type, icon, color, c_id))

    @staticmethod
    def delete(c_id):
        execute_query("DELETE FROM categories WHERE id=?", (c_id,))"""

if "def get_all():" not in old_cat:
    text = text.replace(old_cat, new_cat)
    
with codecs.open('models.py', 'w', 'utf-8') as f:
    f.write(text)
