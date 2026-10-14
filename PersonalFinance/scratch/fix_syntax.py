import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace any physical newlines inside these strings with a literal \n
# I'll just use regex to fix unterminated f-strings where they span two lines by joining them.
import re
text = re.sub(r'(f?"[^"\n]*)[\r\n]+([^"]*")', r'\1\\n\2', text)
text = text.replace('f"Đã xuất báo cáo thành công ra file:\\n{filepath}"', 'f"Đã xuất báo cáo thành công ra file:\\n{filepath}"')

# A safer approach is just to rewrite the exact lines since I know what they are.
with codecs.open('gui.py', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'f"Đã sao chép database an toàn đến:' in line and not line.strip().endswith('"') and not line.strip().endswith('")'):
        # It has a newline inside
        line = line.replace('\r', '').replace('\n', '') + '\\n'
    elif '{dst}")' in line and 'messagebox' not in line:
        line = line.lstrip()
    
    if 'f"Không thể copy file:' in line and not line.strip().endswith('"') and not line.strip().endswith('")'):
        line = line.replace('\r', '').replace('\n', '') + '\\n'
    elif '{e}")' in line and 'messagebox' not in line:
        line = line.lstrip()
        
    if 'f"Đã xuất báo cáo thành công ra file:' in line and not line.strip().endswith('"') and not line.strip().endswith('")'):
        line = line.replace('\r', '').replace('\n', '') + '\\n'
    elif '{filepath}")' in line and 'messagebox' not in line:
        line = line.lstrip()
        
    if '"Personal Finance v2.0' in line and not line.strip().endswith('"') and not line.strip().endswith('")'):
        line = line.replace('\r', '').replace('\n', '') + '\\n'
    elif 'Phát triển bởi:' in line:
        line = line.lstrip()
        
    if '"Bạn có chắc chắn muốn Reset ứng dụng?' in line and not line.strip().endswith('"') and not line.strip().endswith('")'):
        line = line.replace('\r', '').replace('\n', '') + '\\n'
    elif 'Điều này sẽ không xóa giao dịch' in line:
        line = line.lstrip()

    new_lines.append(line)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.writelines(new_lines)
