import customtkinter as ctk
from desktop.theme import COLORS, FONTS


class StatusBadge(ctk.CTkLabel):
    STATUS = {
        "online": {"text": "● Online", "color": COLORS["success"]},
        "offline": {"text": "● Offline", "color": COLORS["danger"]},
        "starting": {"text": "● Starting", "color": COLORS["warning"]},
        "unknown": {"text": "● Unknown", "color": COLORS["text_muted"]},
    }

    def __init__(self, parent, status="unknown"):
        super().__init__(
            parent,
            corner_radius=14,
            padx=12,
            pady=6,
            font=FONTS["small"],
        )
        self.set_status(status)

    def set_status(self, status):
        status = status.lower()

        if status not in self.STATUS:
            status = "unknown"

        info = self.STATUS[status]

        self.configure(
            text=info["text"],
            fg_color=info["color"],
            text_color="white",
        )