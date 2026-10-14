"""Bảng màu, font chữ, danh mục và các hàm định dạng dùng chung cho giao diện."""
import re
import tkinter as tk
import unicodedata
from datetime import date, datetime

# ----------------------------------------------------------------- Màu sắc
BG = "#E0F2FE"        # xanh da trời nhạt (sky-100)
CARD = "#F0F9FF"      # trắng pha xanh (sky-50)
CARD_ALT = "#BAE6FD"  # sky-200
BORDER = "#38BDF8"    # sky-400 (Dùng làm bóng đổ nổi)
DIVIDER = "#BAE6FD"   # sky-200
TEXT = "#0C4A6E"      # sky-900
TEXT_2 = "#075985"    # sky-800
MUTED = "#0EA5E9"     # sky-500

SIDEBAR = "#0C4A6E"   # sky-900
SIDEBAR_HOVER = "#075985" # sky-800
SIDEBAR_CARD = "#082F49"  # sky-950
SIDEBAR_TEXT = "#BAE6FD"  # sky-200
SIDEBAR_MUTED = "#7DD3FC" # sky-300

PRIMARY = "#0EA5E9"       # sky-500
PRIMARY_HOVER = "#0284C7" # sky-600
PRIMARY_SOFT = "#E0F2FE"  # sky-100

INCOME = "#16A34A"
INCOME_SOFT = "#F0FDF4"
INCOME_BORDER = "#BBF7D0"
EXPENSE = "#EF4444"
EXPENSE_SOFT = "#FEF2F2"
EXPENSE_BORDER = "#FECACA"
BALANCE = "#2563EB"
BALANCE_SOFT = "#EFF6FF"
BALANCE_BORDER = "#BFDBFE"
WARNING = "#F59E0B"
WARNING_SOFT = "#FFFBEB"
WARNING_BORDER = "#FDE68A"

# ----------------------------------------------------------------- Font
FONT = "Segoe UI"
EMOJI_FONT = "Segoe UI Emoji"
ICON_FONT = "Segoe MDL2 Assets"


def F(size=10, weight="normal"):
    """Font chữ chính của ứng dụng."""
    return (FONT, size, weight)


# ----------------------------------------------------------------- Danh mục
EXPENSE_CATEGORIES = {
    "Ăn uống": ("🍔", "#F97316"),
    "Đi lại": ("🚗", "#3B82F6"),
    "Nhà ở": ("🏠", "#8B5CF6"),
    "Mua sắm": ("🛒", "#06B6D4"),
    "Học tập": ("📚", "#EC4899"),
    "Giải trí": ("🎮", "#F59E0B"),
    "Sức khỏe": ("💊", "#EF4444"),
    "Khác": ("📦", "#64748B"),
}

INCOME_CATEGORIES = {
    "Lương": ("💰", "#16A34A"),
    "Thưởng": ("🎁", "#10B981"),
    "Làm thêm": ("💼", "#0EA5E9"),
    "Gia đình": ("🏡", "#A855F7"),
    "Thu khác": ("💵", "#64748B"),
}


def cat_info(name):
    """Trả về (icon, màu) của danh mục."""
    if name in EXPENSE_CATEGORIES:
        return EXPENSE_CATEGORIES[name]
    if name in INCOME_CATEGORIES:
        return INCOME_CATEGORIES[name]
    return ("•", "#64748B")


def categories_for(t_type):
    return list((INCOME_CATEGORIES if t_type == "Thu" else EXPENSE_CATEGORIES).keys())


def all_categories():
    return list(EXPENSE_CATEGORIES) + list(INCOME_CATEGORIES)


# ----------------------------------------------------------------- Màu
def mix(color, other="#FFFFFF", ratio=0.85):
    """Trộn `color` với `other` (ratio = tỉ lệ của `other`). Dùng để tạo màu nền nhạt."""
    c1 = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    c2 = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a * (1 - ratio) + b * ratio):02X}" for a, b in zip(c1, c2))


# ----------------------------------------------------------------- Tiền tệ
def money(value, sign=False):
    """1500000 -> '1.500.000đ'. sign=True thêm dấu +/-."""
    text = f"{abs(value):,.0f}".replace(",", ".") + "đ"
    if sign:
        return ("+" if value >= 0 else "-") + text
    return ("-" + text) if value < 0 else text


def money_short(value):
    """Dạng rút gọn cho ô lịch: 1250000 -> '1,25tr', 85000 -> '85k'."""
    v = abs(value)
    if v >= 1_000_000:
        return f"{v / 1_000_000:.2f}".rstrip("0").rstrip(".").replace(".", ",") + "tr"
    if v >= 1_000:
        return f"{v / 1_000:.0f}k"
    return f"{v:.0f}"


def parse_money(text):
    """Chấp nhận '80000', '80.000', '80k', '1,5tr', '2m'. Lỗi -> ValueError."""
    t = text.strip().lower().replace(" ", "").replace("đ", "").replace("vnd", "")
    mult = 1
    for suffix, m in (("tr", 1_000_000), ("m", 1_000_000), ("k", 1_000)):
        if t.endswith(suffix):
            t, mult = t[: -len(suffix)], m
            break
    if mult == 1:
        t = t.replace(".", "").replace(",", "")
    else:
        t = t.replace(",", ".")
    if not t:
        raise ValueError("empty")
    return float(t) * mult


def format_amount_input(value):
    return f"{value:,.0f}".replace(",", ".")


# ----------------------------------------------------------------- Ngày tháng
WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def fmt_date(iso):
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return str(iso)


def parse_date(text):
    text = text.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Ngày không hợp lệ: {text}")


def long_date(d: date):
    return f"{WEEKDAYS[d.weekday()]}, {d.strftime('%d/%m/%Y')}"


# ----------------------------------------------------------------- Tìm kiếm
def normalize(text):
    """Bỏ dấu tiếng Việt + chữ thường, để tìm 'an trua' vẫn ra 'Ăn trưa'."""
    text = (text or "").replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text).strip().casefold()


def truncate(text, n):
    return text if len(text) <= n else text[: n - 1] + "…"


# ----------------------------------------------------------------- Căn giữa màn hình
def center_window(win, width=None, height=None, parent=None):
    """Căn giữa cửa sổ (Tk hoặc Toplevel) vào giữa màn hình hoặc cửa sổ cha."""
    win.update_idletasks()
    w = width or win.winfo_width()
    h = height or win.winfo_height()
    
    if parent and parent.winfo_viewable():
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - w) // 2
        y = parent.winfo_y() + (parent.winfo_height() - h) // 2
    else:
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        
    x = max(0, x)
    y = max(0, y)
    win.geometry(f"{w}x{h}+{x}+{y}")


# ----------------------------------------------------------------- Nút bo tròn góc
class RoundedButton(tk.Canvas):
    """Nút bấm bo tròn góc dùng Canvas, cân bằng kích thước và căn giữa chuẩn xác."""

    def __init__(self, parent, text="", command=None, bg="#0EA5E9", fg="white",
                 font=None, radius=12, padx=20, pady=10, cursor="hand2",
                 anchor="center", activebackground=None, min_width=None, min_height=None, **kw):
        self._bg_color = bg
        self._fg_color = fg
        self._active_bg = activebackground or self._darken(bg, 0.15)
        self._radius = radius
        self._text = text
        self._command = command
        self._font = font or F(11, "bold")
        self._padx = padx
        self._pady = pady
        self._anchor = anchor
        self._pressed = False
        self._min_width = min_width
        self._min_height = min_height

        # Tính toán kích cỡ cơ sở theo nội dung chữ
        _tmp = tk.Label(parent, text=text, font=self._font)
        _tmp.update_idletasks()
        tw = _tmp.winfo_reqwidth()
        th = _tmp.winfo_reqheight()
        _tmp.destroy()

        init_w = max(tw + padx * 2, min_width or 0)
        init_h = max(th + pady * 2, min_height or 0)

        # Lấy màu nền cha để viền canvas hoàn toàn tệp màu
        parent_bg = kw.pop("parent_bg", None)
        if not parent_bg:
            try:
                parent_bg = parent.cget("bg")
            except Exception:
                parent_bg = BG

        super().__init__(parent, width=init_w, height=init_h, bg=parent_bg,
                         highlightthickness=0, bd=0, cursor=cursor, **kw)

        self._current_w = init_w
        self._current_h = init_h

        self._draw(self._bg_color)

        # Lắng nghe sự kiện co giãn để vẽ lại hình khối cân đối theo kích thước thực
        self.bind("<Configure>", self._on_configure)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_configure(self, event):
        if event.width > 1 and event.height > 1:
            if event.width != self._current_w or event.height != self._current_h:
                self._current_w = event.width
                self._current_h = event.height
                current_color = self._active_bg if self._pressed else self._bg_color
                self._draw(current_color)

    # ---- Vẽ hình chữ nhật bo tròn cân bằng 4 góc ----
    def _draw(self, color):
        self.delete("all")
        w = max(self._current_w, 4)
        h = max(self._current_h, 4)
        r = min(self._radius, w // 2, h // 2)

        # Tập điểm polygon chuẩn cho góc bo cong đều và đối xứng
        points = [
            r, 0,
            r, 0,
            w - r, 0,
            w - r, 0,
            w, 0,
            w, r,
            w, r,
            w, h - r,
            w, h - r,
            w, h,
            w - r, h,
            w - r, h,
            r, h,
            r, h,
            0, h,
            0, h - r,
            0, h - r,
            0, r,
            0, r,
            0, 0
        ]
        self.create_polygon(points, fill=color, outline=color, smooth=True, tags="bg")

        # Căn chỉnh vị trí chữ chính xác
        if self._anchor == "w":
            tx = self._padx
            anch = "w"
        elif self._anchor == "e":
            tx = w - self._padx
            anch = "e"
        else:
            tx = w / 2
            anch = "center"

        ty = h / 2
        self.create_text(tx, ty, text=self._text, fill=self._fg_color,
                         font=self._font, anchor=anch, tags="txt")

    def _darken(self, color, amount=0.15):
        """Làm tối màu đi một chút cho hover effect."""
        try:
            c = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
            return "#" + "".join(f"{max(0, int(v * (1 - amount))):02X}" for v in c)
        except Exception:
            return color

    def _on_enter(self, e):
        self._draw(self._active_bg)

    def _on_leave(self, e):
        self._pressed = False
        self._draw(self._bg_color)

    def _on_press(self, e):
        self._pressed = True
        darker = self._darken(self._bg_color, 0.25)
        self._draw(darker)

    def _on_release(self, e):
        if self._pressed and self._command:
            self._pressed = False
            self._draw(self._active_bg)
            self._command()

    # ---- Public API tương thích tk.Button ----
    def config(self, **kw):
        self.configure(**kw)

    def configure(self, **kw):
        if "text" in kw:
            self._text = kw.pop("text")
        if "bg" in kw:
            self._bg_color = kw.pop("bg")
            self._active_bg = self._darken(self._bg_color, 0.15)
        if "fg" in kw:
            self._fg_color = kw.pop("fg")
        if "command" in kw:
            self._command = kw.pop("command")
        if "state" in kw:
            state = kw.pop("state")
            if state == "disabled":
                self._command = None
                self._bg_color = "#CCCCCC"
                self._fg_color = "#888888"
            # Bỏ qua các state khác
        if "font" in kw:
            self._font = kw.pop("font")
        self._draw(self._bg_color)
        if kw:
            super().configure(**kw)

    def cget(self, key):
        if key == "text":
            return self._text
        if key == "bg" or key == "background":
            return self._bg_color
        return super().cget(key)
