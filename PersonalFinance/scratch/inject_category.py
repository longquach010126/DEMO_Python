import codecs

with codecs.open('models.py', 'r', 'utf-8') as f:
    text = f.read()

old_str = "class Category:\\n    @staticmethod\\n    def get_by_type(t_type):"
if old_str not in text:
    old_str = "class Category:\\r\\n    @staticmethod\\r\\n    def get_by_type(t_type):"

new_str = """class Category:
    @staticmethod
    def get_all():
        return fetch_query("SELECT id, name, type, icon, color FROM categories")

    @staticmethod
    def update(c_id, name, t_type, icon, color):
        execute_query("UPDATE categories SET name=?, type=?, icon=?, color=? WHERE id=?", (name, t_type, icon, color, c_id))

    @staticmethod
    def delete(c_id):
        execute_query("DELETE FROM categories WHERE id=?", (c_id,))

    @staticmethod
    def get_by_type(t_type):"""

new_str = new_str.replace("\\n", "\\r\\n") if "\\r\\n" in old_str else new_str

text = text.replace(old_str, new_str)

with codecs.open('models.py', 'w', 'utf-8') as f:
    f.write(text)
