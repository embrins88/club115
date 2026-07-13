from __future__ import annotations

import threading
import webbrowser
from tkinter import messagebox

import customtkinter as ctk

from desktop.components import InfoCard, StatusBadge
from desktop.theme import COLORS, FONTS

from servers.services.comparison_service import ComparisonService
from servers.services.server_config import get_server
from servers.services.server_config import get_server, get_servers
from servers.services.ssh_service import SSHService
from servers.services.sync_service import SyncService
from servers.services.server_control_service import ServerControlService


class MinecraftPage(ctk.CTkFrame):
    """Minecraft server management page."""


    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg"])

        self.app = app
        self.servers = get_servers()
        self.server_name_to_id = {
            server.name: server_id
                for server_id, server in self.servers.items()
}

        self.server_id = "homestead"
        self.server = self.servers[self.server_id]

        self.server_service = ServerControlService(self.server)
        self.sync_service = SyncService()
        self.ssh = SSHService(self.server)

        self.action_buttons: list[ctk.CTkButton] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.build_page()
        self.refresh_status()

    def build_page(self) -> None:
        self._build_header()
        self._build_info_cards()
        self._build_actions()
        self._build_activity_panel()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(
        self,
            fg_color=COLORS["panel"],
            corner_radius=12,
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=24,
            pady=(24, 12),
        )
        header.grid_columnconfigure(0, weight=1)

        title_area = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )
        title_area.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=14,
        )

        self.server_title = ctk.CTkLabel(
            title_area,
            text=f"🎮  {self.server.name}",
            font=FONTS["title"],
            text_color=COLORS["text"],
        )
        self.server_title.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.world_label = ctk.CTkLabel(
            title_area,
            text=f"World: {self.server.world_name}",
            font=FONTS.get("body", ("Segoe UI", 12)),
            text_color=COLORS.get("muted_text", "#9BA8B0"),
        )
        self.world_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(2, 0),
        )

        selector_area = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )
        selector_area.grid(
            row=0,
            column=1,
            sticky="e",
            padx=18,
            pady=14,
        )

        ctk.CTkLabel(
            selector_area,
            text="Server",
            font=FONTS.get("body", ("Segoe UI", 12)),
            text_color=COLORS.get("muted_text", "#9BA8B0"),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        self.server_selector = ctk.CTkOptionMenu(
            selector_area,
            values=list(self.server_name_to_id.keys()),
            command=self.change_server,
            width=180,
            height=36,
            font=FONTS["button"],
            fg_color=COLORS["button"],
            button_color=COLORS["button"],
            button_hover_color=COLORS["button_hover"],
            dropdown_fg_color=COLORS["panel"],
            dropdown_hover_color=COLORS["button_hover"],
            text_color=COLORS["text"],
        )
        self.server_selector.grid(
            row=1,
            column=0,
            sticky="e",
        )
        self.server_selector.set(self.server.name)

        self.status_badge = StatusBadge(header, "unknown")
        self.status_badge.grid(
            row=1,
            column=0,
            sticky="w",
            padx=18,
            pady=(0, 14),
        )

    def _build_info_cards(self) -> None:
        info = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg"],
        )
        info.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=24,
            pady=8,
        )
        info.grid_columnconfigure((0, 1, 2), weight=1)

        self.server_card = InfoCard(
            info,
            "Server Status",
            "Checking...",
        )
        self.server_card.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=12,
        )

        self.changes_card = InfoCard(
            info,
            "Pending Changes",
            "Checking...",
        )
        self.changes_card.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=8,
            pady=12,
        )

        self.checkpoint_card = InfoCard(
            info,
            "Last Checkpoint",
            "Checking...",
        )
        self.checkpoint_card.grid(
            row=0,
            column=2,
            sticky="ew",
            padx=8,
            pady=12,
        )

    def _build_actions(self) -> None:
        actions = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg"],
        )
        actions.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=24,
            pady=8,
        )
        actions.grid_columnconfigure((0, 1, 2, 3), weight=1)

        buttons = [
            ("Preview Sync", self.preview_sync),
            ("Run Sync", self.run_sync),
            ("Restart", self.restart_server),
            ("BlueMap", self.open_bluemap),
        ]

        for column, (text, command) in enumerate(buttons):
            button = ctk.CTkButton(
                actions,
                text=text,
                command=command,
                height=42,
                font=FONTS["button"],
                fg_color=COLORS["button"],
                hover_color=COLORS["button_hover"],
                text_color=COLORS["text"],
                corner_radius=8,
            )
            button.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=8,
                pady=12,
            )

            self.action_buttons.append(button)

    def _build_activity_panel(self) -> None:
        activity = ctk.CTkFrame(
            self,
            fg_color=COLORS["panel"],
            corner_radius=12,
        )
        activity.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=24,
            pady=(8, 24),
        )
        activity.grid_columnconfigure(0, weight=1)
        activity.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            activity,
            text="Activity",
            font=FONTS.get("heading", FONTS["button"]),
            text_color=COLORS["text"],
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(14, 6),
        )

        self.output = ctk.CTkTextbox(
            activity,
            fg_color=COLORS["panel"],
            border_width=0,
            font=("Consolas", 12),
            wrap="word",
        )
        self.output.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12),
        )

        self.log(
            f"{self.server.name} is ready.\n"
            "Use Preview Sync to check for client/server differences."
        )

    def log(self, text: str) -> None:
        """Append timestamped text to the activity log."""

        timestamp = datetime.now().strftime("%H:%M:%S")

        for line in text.rstrip().splitlines():
            self.output.insert(
                "end",
                f"{timestamp}  {line}\n"
            )

    self.output.see("end")

    def clear_log(self) -> None:
        """Clear the activity panel."""

        self.output.delete("1.0", "end")

    def set_busy(self, busy: bool) -> None:
        """Enable or disable page actions."""

        state = "disabled" if busy else "normal"

        for button in self.action_buttons:
            button.configure(state=state)

    def run_background(self, task) -> None:
        """Run a blocking backend operation outside the UI thread."""

        self.set_busy(True)

        def worker() -> None:
            try:
                task()
            except Exception as error:
                error_message = str(error)

                self.after(
                    0,
                    lambda message=error_message: self.log(
                        f"ERROR: {message}"
                    ),
                )
            finally:
                self.after(
                    0,
                    lambda: self.set_busy(False),
                )

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    def preview_sync(self) -> None:
        """Preview changes without modifying the server."""

        self.clear_log()
        self.log("> Previewing synchronization...")

        def task() -> None:
            result = self.sync_service.preview(self.SERVER_ID)

            self.after(
                0,
                lambda: self.display_sync_result(
                    result,
                    preview=True,
                ),
            )

        self.run_background(task)

    def run_sync(self) -> None:
        """Run the live synchronization workflow."""

        confirmed = messagebox.askyesno(
            "Synchronize Homestead",
            (
                "This will create a checkpoint, stop the server if needed, "
                "upload updated files, remove obsolete files, and restart it.\n\n"
                "Continue?"
            ),
        )

        if not confirmed:
            return

        self.clear_log()
        self.log("> Starting live synchronization...")

        def task() -> None:
            result = self.sync_service.sync(self.SERVER_ID)

            self.after(
                0,
                lambda: self.display_sync_result(
                    result,
                    preview=False,
                ),
            )

        self.run_background(task)

    def display_sync_result(
        self,
        result,
        *,
        preview: bool,
    ) -> None:
        """Display a workflow result in the activity panel."""

        self.clear_log()

        heading = "SYNC PREVIEW" if preview else "SYNC RESULT"

        self.log(heading)
        self.log("=" * len(heading))
        self.log(f"Server: {result.server_name}")
        self.log(f"Successful: {'Yes' if result.succeeded else 'No'}")
        self.log("")

        comparison = result.comparison

        if comparison:
            self.log("Changes")
            self.log(f"  Added:   {len(comparison.added)}")
            self.log(f"  Updated: {len(comparison.updated)}")
            self.log(f"  Removed: {len(comparison.removed)}")
            self.log("")

            if comparison.added:
                self.log("Added")
                for change in comparison.added:
                    self.log(f"  + {change.path}")
                self.log("")

            if comparison.updated:
                self.log("Updated")
                for change in comparison.updated:
                    self.log(f"  ~ {change.path}")
                self.log("")

            if comparison.removed:
                self.log("Removed")
                for change in comparison.removed:
                    self.log(f"  - {change.path}")
                self.log("")

        if result.checkpoint:
            self.log(
                f"Checkpoint: {result.checkpoint.checkpoint_id}"
            )
            self.log("")

        if result.completed_steps:
            self.log("Workflow")
            for step in result.completed_steps:
                self.log(f"  ✓ {step}")
            self.log("")

        for message in result.messages:
            self.log(message)

        for error in result.errors:
            self.log(f"ERROR: {error}")

        self.refresh_status(run_once=True)

    def restart_server(self) -> None:
        """Restart the Homestead systemd service."""

        confirmed = messagebox.askyesno(
            "Restart Homestead",
            "Restart the Homestead Minecraft server?",
        )

        if not confirmed:
            return

        self.clear_log()
        self.log("> Restarting Homestead...")

        def task() -> None:
            status = self.server_service.get_status()

            if status.is_running:
                self.server_service.stop()

            new_status = self.server_service.start()

            if not new_status.is_running:
                raise RuntimeError(
                    "Homestead did not return to a running state."
                )

            self.after(
                0,
                lambda: self.log("Homestead restarted successfully."),
            )
            self.after(
                0,
                lambda: self.refresh_status(run_once=True),
            )

        self.run_background(task)

    def open_bluemap(self) -> None:
        webbrowser.open(self.app.config["bluemap_url"])

    def refresh_status(self, run_once: bool = False) -> None:
        """Refresh status, pending changes, and checkpoint information."""

        def task() -> None:
            try:
                status = self.server_service.get_status()
                comparison = ComparisonService(self.server).run()
                checkpoint = self.get_latest_checkpoint()

                self.after(
                    0,
                    lambda: self.update_status_cards(
                        status,
                        comparison,
                        checkpoint,
                    ),
                )

            except Exception as error:
                self.after(
                    0,
                    lambda: self.show_status_error(str(error)),
                )

        threading.Thread(
            target=task,
            daemon=True,
        ).start()

        if not run_once:
            self.after(30000, self.refresh_status)

    def update_status_cards(
        self,
        status,
        comparison,
        checkpoint: str,
    ) -> None:
        """Apply refreshed values to the page."""

        if status.is_running:
            self.status_badge.set_status("online")
            self.server_card.set_value("Running")
        else:
            self.status_badge.set_status("offline")
            self.server_card.set_value("Stopped")

        if comparison.errors:
            self.changes_card.set_value("Error")
        elif comparison.total_changes == 0:
            self.changes_card.set_value("Synchronized")
        else:
            self.changes_card.set_value(
                f"{comparison.total_changes} change(s)"
            )

        self.checkpoint_card.set_value(
            checkpoint or "None"
        )

    def show_status_error(self, error: str) -> None:
        self.status_badge.set_status("unknown")
        self.server_card.set_value("Unknown")
        self.changes_card.set_value("Unknown")
        self.checkpoint_card.set_value("Unknown")
        self.log(f"Status refresh error: {error}")

    def get_latest_checkpoint(self) -> str:
        """Return the newest numbered checkpoint ID."""

        checkpoint_root = (
            f"/home/{self.server.ssh_user}/minecraft/checkpoints/"
            f"{self.server.server_id}"
        )

        command = (
            f"find '{checkpoint_root}' "
            "-maxdepth 1 -mindepth 1 -type d "
            "-name 'CP[0-9][0-9][0-9][0-9][0-9][0-9]' "
            "-printf '%f\n' "
            "| sort "
            "| tail -n 1"
        )

        result = self.ssh.run(
            command,
            check=False,
        )

        return result.stdout.strip()
    
    def change_server(self, selected_name: str) -> None:
        """Switch the page to another configured Minecraft server."""

        selected_id = self.server_name_to_id[selected_name]

        if selected_id == self.server_id:
            return

        self.server_id = selected_id
        self.server = self.servers[selected_id]

        self.server_service = ServerControlService(self.server)
        self.ssh = SSHService(self.server)

        self.server_title.configure(
            text=f"🎮  {self.server.name}"
        )
        self.world_label.configure(
            text=f"World: {self.server.world_name}"
        )

        self.status_badge.set_status("unknown")
        self.server_card.set_value("Checking...")
        self.changes_card.set_value("Checking...")
        self.checkpoint_card.set_value("Checking...")

        self.clear_log()
        self.log(f"Switched to {self.server.name}.")
        self.log(
            "Use Preview Sync to check for client/server differences."
        )

        self.refresh_status(run_once=True)