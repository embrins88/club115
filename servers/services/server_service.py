from __future__ import annotations

import shlex
from dataclasses import dataclass
from unittest import result

from matplotlib import lines
from servers.models import server
from servers.services.ssh_service import SSHService

from servers.models.server import Server


@dataclass(frozen=True)
class ServiceStatus:
    """Current systemd state for one managed server."""

    active_state: str
    sub_state: str

    @property
    def is_running(self) -> bool:
        return (
            self.active_state == "active"
            and self.sub_state == "running"
        )


class ServerControlService:
    """Control the systemd service for one managed server."""

    def __init__(self, server: Server) -> None:
        self.server = server
        self.ssh = SSHService(server)

    def get_status(self) -> ServiceStatus:
        """Return the current systemd service state."""

        service = shlex.quote(self.server.service)

        command = (
            "systemctl show "
            f"{service} "
            "--property=LoadState "
            "--property=ActiveState "
            "--property=SubState "
            "--value"
        )

        output = self._run_command(command)
        lines = output.splitlines()

        if len(lines) < 3:
            raise RuntimeError(
                f"Unexpected status response for "
                f"{self.server.service}: {output!r}"
            )

        load_state = lines[0].strip()

        if load_state != "loaded":
            raise RuntimeError(
                f"Service '{self.server.service}' is not loaded."
            )

        return ServiceStatus(
            active_state=lines[1].strip(),
            sub_state=lines[2].strip(),
        )

    def stop(self) -> ServiceStatus:
        """Stop the configured server service."""

        service = shlex.quote(self.server.service)

        self._run_command(
            f"sudo -n systemctl stop {service}"
        )

        status = self.get_status()

        if status.active_state != "inactive":
            raise RuntimeError(
                f"{self.server.service} did not stop cleanly. "
                f"State: {status.active_state}/{status.sub_state}"
            )

        return status

    def start(self) -> ServiceStatus:
        """Start the configured server service."""

        service = shlex.quote(self.server.service)

        self._run_command(
            f"sudo -n systemctl start {service}"
        )

        status = self.get_status()

        if not status.is_running:
            raise RuntimeError(
                f"{self.server.service} did not start cleanly. "
                f"State: {status.active_state}/{status.sub_state}"
            )

        return status

    def _run_command(self, command: str) -> str:
        """Run one remote command and return standard output."""

        result = self.ssh.run(command)
        return result.stdout