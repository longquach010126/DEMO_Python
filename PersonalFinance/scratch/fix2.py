import codecs
import re

with codecs.open('models.py', 'r', 'utf-8') as f:
    text = f.read()

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

# Regex substitute the entire Category class until 'class Setting:'
text = re.sub(r'class Category:.*?class Setting:', new_cat + '\n\nclass Setting:', text, flags=re.DOTALL)

with codecs.open('models.py', 'w', 'utf-8') as f:
    f.write(text)
