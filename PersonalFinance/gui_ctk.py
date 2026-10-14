import customtkinter as ctk
from models import Transaction, Budget
from datetime import datetime

# Cấu hình giao diện
ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue") 

# Màu sắc
BG_COLOR = "#F4F7FE"
SIDEBAR_COLOR = "#111C44"
CARD_BG = "#FFFFFF"
TEXT_MAIN = "#2B3674"
TEXT_SUB = "#A0AEC0"

COLOR_THU = "#05CD99"
COLOR_CHI = "#EE5D50"
COLOR_DU = "#4318FF"

class AppCTK(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MoneyManager (Modern Edition)")
        self.geometry("1200x750")
        self.configure(fg_color=BG_COLOR)
        
        # Grid layout chính
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        # Logo
        self.logo = ctk.CTkLabel(self.sidebar, text="MoneyManager", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FFFFFF")
        self.logo.grid(row=0, column=0, padx=20, pady=(40, 5))
        self.subtitle = ctk.CTkLabel(self.sidebar, text="Quản lý chi tiêu thông minh", font=ctk.CTkFont(size=12), text_color=TEXT_SUB)
        self.subtitle.grid(row=1, column=0, padx=20, pady=(0, 40))
        
        self.frames = {}
        self.nav_buttons = {}
        self.current_btn = None
        
        # Main content
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color=BG_COLOR)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        self.build_sidebar()
        self.create_dashboard()
        
        self.show_frame("Dashboard", self.nav_buttons["Dashboard"])

    def build_sidebar(self):
        menus = [
            ("Tổng quan", "Dashboard"),
            ("Giao dịch", "Transactions"),
            ("Danh mục", "Categories"),
            ("Ngân sách", "Budgets"),
            ("Thống kê", "Stats"),
            ("Cài đặt", "Settings"),
        ]
        for i, (text, name) in enumerate(menus):
            btn = ctk.CTkButton(self.sidebar, text=f"   {text}", fg_color="transparent", text_color=TEXT_SUB, 
                                hover_color="#2B3674", anchor="w", font=ctk.CTkFont(size=15, weight="bold"),
                                corner_radius=8, height=40,
                                command=lambda n=name: self.nav_click(n))
            btn.grid(row=i+2, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[name] = btn

    def nav_click(self, name):
        if name in self.frames:
            self.show_frame(name, self.nav_buttons[name])
        else:
            # Tạo frame tạm nếu chưa làm
            for f in self.frames.values(): f.grid_forget()
            frame = ctk.CTkFrame(self.main_content, fg_color=BG_COLOR)
            frame.grid(row=0, column=0, sticky="nsew")
            ctk.CTkLabel(frame, text=f"Màn hình {name} đang được cập nhật giao diện mới...", font=ctk.CTkFont(size=20), text_color=TEXT_SUB).pack(pady=100)
            self.frames[name] = frame
            self.show_frame(name, self.nav_buttons[name])

    def show_frame(self, name, btn):
        if self.current_btn:
            self.current_btn.configure(fg_color="transparent", text_color=TEXT_SUB)
        btn.configure(fg_color="#2B3674", text_color="#FFFFFF")
        self.current_btn = btn
        
        for f in self.frames.values(): f.grid_forget()
        self.frames[name].grid(row=0, column=0, sticky="nsew")
        
        if name == "Dashboard":
            self.update_dashboard()

    def create_dashboard(self):
        frame = ctk.CTkFrame(self.main_content, fg_color=BG_COLOR)
        self.frames["Dashboard"] = frame
        frame.grid_columnconfigure((0,1,2), weight=1)
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Xin chào, Long 👋", font=ctk.CTkFont(size=28, weight="bold"), text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Chúc bạn một ngày tốt lành!", font=ctk.CTkFont(size=14), text_color=TEXT_SUB).pack(anchor="w")
        
        user_info = ctk.CTkFrame(header, fg_color="transparent")
        user_info.pack(side="right")
        ctk.CTkLabel(user_info, text="🔔", font=ctk.CTkFont(size=24)).pack(side="left", padx=15)
        ctk.CTkLabel(user_info, text="Quách Bảo Long", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_MAIN).pack(side="left")
        
        # Cards
        self.lbl_thu = self.create_card(frame, 1, 0, "Tổng thu", COLOR_THU)
        self.lbl_chi = self.create_card(frame, 1, 1, "Tổng chi", COLOR_CHI)
        self.lbl_du = self.create_card(frame, 1, 2, "Số dư", COLOR_DU)
        
    def create_card(self, parent, row, col, title, color):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=20)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=15), text_color=TEXT_SUB).pack(anchor="w", padx=25, pady=(25, 5))
        val = ctk.CTkLabel(card, text="0 đ", font=ctk.CTkFont(size=32, weight="bold"), text_color=color)
        val.pack(anchor="w", padx=25, pady=(0, 25))
        return val

    def update_dashboard(self):
        summary = Transaction.get_summary()
        thu = summary.get('Thu', 0) or 0
        chi = summary.get('Chi', 0) or 0
        du = thu - chi
        self.lbl_thu.configure(text=f"{thu:,.0f} đ")
        self.lbl_chi.configure(text=f"{chi:,.0f} đ")
        self.lbl_du.configure(text=f"{du:,.0f} đ")

if __name__ == "__main__":
    app = AppCTK()
    app.mainloop()
