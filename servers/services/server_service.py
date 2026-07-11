from __future__ import annotations

import shlex
from dataclasses import dataclass
from unittest import result

from matplotlib import lines
from servers.models import server
from servers.services import status
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
        unit = shlex.quote(self._unit_name())

        command = (
            "systemctl show "
                f"{unit} "
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
                f"{self._unit_name()}: {output!r}"
            )

        load_state = lines[0].strip()

        if load_state != "loaded":
            raise RuntimeError(
                f"Service '{self._unit_name()}' is not loaded."
            )

        return ServiceStatus(
            active_state=lines[1].strip(),
            sub_state=lines[2].strip(),
        )

    def stop(self) -> ServiceStatus:
        unit = shlex.quote(self._unit_name())

        self._run_command(
            f"sudo -n systemctl stop {unit}"
        )

        status = self.get_status()

        if status.active_state != "inactive":
            raise RuntimeError(
                f"{self._unit_name()} did not stop cleanly. "
                f"State: {status.active_state}/{status.sub_state}"
            )

        return status

    def start(self) -> ServiceStatus:
        unit = shlex.quote(self._unit_name())

        self._run_command(
            f"sudo -n systemctl start {unit}"
        )

        status = self.get_status()

        if not status.is_running:
            raise RuntimeError(
                f"{self._unit_name()} did not start cleanly. "
                f"State: {status.active_state}/{status.sub_state}"
            )

        return status

    def _run_command(self, command: str) -> str:
        """Run one remote command and return standard output."""

        result = self.ssh.run(command)
        return result.stdout
    
    def _unit_name(self) -> str:
        return f"{self.server.service}.service"