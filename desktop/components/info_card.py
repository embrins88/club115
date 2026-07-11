import customtkinter as ctk
from desktop.theme import COLORS, FONTS


class InfoCard(ctk.CTkFrame):
    def __init__(self, parent, title, value):
        super().__init__(
            parent,
            fg_color=COLORS["panel"],
            corner_radius=12,
        )

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        )
        self.title_label.pack(anchor="w", padx=14, pady=(12, 0))

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=FONTS["heading"],
            text_color=COLORS["text"],
        )
        self.value_label.pack(anchor="w", padx=14, pady=(0, 12))

    def set_value(self, value):
        self.value_label.configure(text=value)