import customtkinter as ctk
from desktop.theme import COLORS, FONTS


class SidebarButton(ctk.CTkButton):
    def __init__(self, parent, text, command=None, state="normal"):
        super().__init__(
            parent,
            text=text,
            command=command,
            state=state,
            anchor="w",
            height=42,
            font=FONTS["button"],
            fg_color=COLORS["button"],
            hover_color=COLORS["button_hover"],
            text_color=COLORS["text"],
            corner_radius=8,
        )