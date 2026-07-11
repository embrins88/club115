import customtkinter as ctk

from desktop.config_loader import load_config
from desktop.services.ssh_client import SSHClient
from desktop.services.minecraft import MinecraftServer

from desktop.pages.registry import PAGE_REGISTRY

from desktop.theme import COLORS, FONTS, SPACING
from desktop.components import SidebarButton, InfoCard, StatusBadge

CONFIG = load_config()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class Club115App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Club 115")
        self.geometry("1000x620")
        self.minsize(900, 560)
        self.configure(fg_color=COLORS["bg"])

        self.config = CONFIG

        self.ssh = SSHClient(CONFIG["server_host"], CONFIG["server_user"])
        self.minecraft = MinecraftServer(self.ssh)

        # Page management
        self.pages = {}
        self.current_page = None
        self.page_registry = PAGE_REGISTRY

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_main_panel()

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=COLORS["sidebar"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        title = ctk.CTkLabel(
            self.sidebar,
            text="Club 115",
            font=FONTS["title"],
            text_color=COLORS["text"]
        )
        title.pack(pady=(25, 5))

        subtitle = ctk.CTkLabel(
            self.sidebar,
                text="Mission Control",
                font=FONTS["small"],
                text_color=COLORS["text_muted"]
        )
        subtitle.pack(pady=(0, 25))

        SidebarButton(
            self.sidebar,
            text="🎮 Minecraft",
            command=lambda: self.show_page("minecraft")
        ).pack(fill="x", padx=18, pady=6)

        SidebarButton(
            self.sidebar,
            text="💾 Storage",
            state="disabled"
        ).pack(fill="x", padx=18, pady=6)

        SidebarButton(
            self.sidebar,
            text="🍓 Raspberry Pi",
            state="disabled"
        ).pack(fill="x", padx=18, pady=6)

        SidebarButton(
            self.sidebar,
            text="🌐 Network",
            state="disabled"
        ).pack(fill="x", padx=18, pady=6)

        SidebarButton(
            self.sidebar,
            text="⚙ Settings",
            state="disabled"
        ).pack(fill="x", padx=18, pady=6)

    def build_main_panel(self):
        self.main = ctk.CTkFrame(
        self,
            corner_radius=0,
            fg_color=COLORS["bg"]
        )
        self.main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(3, weight=1)

        self.show_page("minecraft")

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_page(self, name):
        if self.current_page:
            self.current_page.grid_forget()

        if name not in self.pages:
            page_class = self.page_registry[name]
            self.pages[name] = page_class(self.main, self)
            self.pages[name].grid(row=0, column=0, sticky="nsew")
        else:
            self.pages[name].grid(row=0, column=0, sticky="nsew")

        self.current_page = self.pages[name]