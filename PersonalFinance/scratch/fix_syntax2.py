import codecs
import re

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# The issue is that the python multi-line strings in update_settings.py used \\n, which were interpreted as literal backslash + n when running the script? No, they were interpreted as ACTUAL newlines because it was not a raw string!
# So in gui.py, we literally have physical newlines inside single-quoted string literals.

# Let's fix all the specific broken lines.
broken_strings = [
    ('f"Đã sao chép database an toàn đến:\\n', '{dst}")'),
    ('f"Không thể copy file:\\n', '{e}")'),
    ('"Personal Finance v2.0\\n', 'Phát triển bởi: Quách Bảo Long\\nỨng dụng quản lý tài chính cá nhân với Tkinter & SQLite.")'),
    ('"Bạn có chắc chắn muốn Reset ứng dụng?\\n', 'Điều này sẽ không xóa giao dịch, nhưng sẽ đưa tất cả Cài đặt (Settings) về mặc định.", icon="warning"):')
]

for s1, s2 in broken_strings:
    # We replace physical newline with literal "\n"
    s1_phys = s1.replace('\\n', '\n')
    s2_phys = s2.replace('\\n', '\n')
    
    # Actually, the file currently has:
    # "Personal Finance v2.0
    # Phát triển bởi...
    text = re.sub(r'f"Đã sao chép database an toàn đến:\r?\n\s*\{dst\}"\)', r'f"Đã sao chép database an toàn đến:\\n{dst}")', text)
    text = re.sub(r'f"Không thể copy file:\r?\n\s*\{e\}"\)', r'f"Không thể copy file:\\n{e}")', text)
    text = re.sub(r'"Personal Finance v2.0\r?\n\s*Phát triển bởi: Quách Bảo Long\r?\n\s*Ứng dụng quản lý tài chính cá nhân với Tkinter & SQLite."\)', r'"Personal Finance v2.0\\nPhát triển bởi: Quách Bảo Long\\nỨng dụng quản lý tài chính cá nhân với Tkinter & SQLite.")', text)
    text = re.sub(r'"Bạn có chắc chắn muốn Reset ứng dụng\?\r?\n\s*Điều này sẽ không xóa giao dịch, nhưng sẽ đưa tất cả Cài đặt \(Settings\) về mặc định.", icon="warning"\):', r'"Bạn có chắc chắn muốn Reset ứng dụng?\\nĐiều này sẽ không xóa giao dịch, nhưng sẽ đưa tất cả Cài đặt (Settings) về mặc định.", icon="warning"):', text)
    
    # And there's one in export_report
    text = re.sub(r'f"Đã xuất báo cáo thành công ra file:\r?\n\s*\{filepath\}"\)', r'f"Đã xuất báo cáo thành công ra file:\\n{filepath}")', text)

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
