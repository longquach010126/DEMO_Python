import codecs
with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove from menus
text = text.replace('("Thống kê", "Stats"),\n', '')

# 2. Remove the create_stats and update_stats block
# The block is under # ============================== STATS ==============================
import re
text = re.sub(r'    # ============================== STATS ==============================.*?    # ============================== SETTINGS ==============================', '    # ============================== SETTINGS ==============================', text, flags=re.DOTALL)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
