from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shlex
from xmlrpc import client

from contextlib import contextmanager
from collections.abc import Iterator

import paramiko

from servers.models.server import Server


@dataclass(frozen=True)
class CommandResult:
    """Result returned by a remote SSH command."""

    command: str
    exit_code: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0


class SSHSession:
    """An open SSH and SFTP session."""

    def __init__(
        self,
        client: paramiko.SSHClient,
        sftp: paramiko.SFTPClient,
    ) -> None:
        self.client = client
        self.sftp = sftp

    def run(
        self,
        command: str,
        *,
        check: bool = True,
        timeout: int | None = None,
    ) -> CommandResult:
        """Run a command through the existing SSH connection."""

        _, stdout, stderr = self.client.exec_command(
            command,
            timeout=timeout,
        )

        exit_code = stdout.channel.recv_exit_status()

        result = CommandResult(
            command=command,
            exit_code=exit_code,
            stdout=stdout.read()
            .decode("utf-8", errors="replace")
            .strip(),
            stderr=stderr.read()
            .decode("utf-8", errors="replace")
            .strip(),
        )

        if check and not result.succeeded:
            raise RuntimeError(
                f"Remote command failed with exit code "
                f"{result.exit_code}: "
                f"{result.stderr or result.command}"
            )

        return result

    def upload(
        self,
        local_path: Path,
        remote_path: str,
    ) -> None:
        """Upload one file through the existing SFTP session."""

        if not local_path.is_file():
            raise FileNotFoundError(
                f"Local upload file does not exist: {local_path}"
            )

        self.sftp.put(str(local_path), remote_path)

    def write_text(
        self,
        remote_path: str,
        content: str,
    ) -> None:
        """Write a UTF-8 text file through the existing SFTP session."""

        with self.sftp.file(remote_path, "w") as remote_file:
            remote_file.write(content)

class SSHService:
    """Provide shared SSH and SFTP operations for one server."""
    
    def __init__(self, server: Server) -> None:
        self.server = server

    def connect(self) -> paramiko.SSHClient:
        """Open and return an SSH connection."""

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            hostname=self.server.ssh_host,
            username=self.server.ssh_user,
            key_filename=str(self.server.ssh_key),
            timeout=15,
        )

        return client

    def run(
        self,
        command: str,
        *,
        check: bool = True,
        timeout: int | None = None,
    ) -> CommandResult:
        """Run one remote command."""

        client = self.connect()

        try:
            _, stdout, stderr = client.exec_command(
                command,
                timeout=timeout,
            )

            exit_code = stdout.channel.recv_exit_status()

            result = CommandResult(
                command=command,
                exit_code=exit_code,
                stdout=stdout.read()
                .decode("utf-8", errors="replace")
                .strip(),
                stderr=stderr.read()
                .decode("utf-8", errors="replace")
                .strip(),
            )

            if check and not result.succeeded:
                raise RuntimeError(
                    f"Remote command failed with exit code "
                    f"{result.exit_code}: "
                    f"{result.stderr or result.command}"
                )

            return result
        finally:
            client.close()
        
    @contextmanager
    def session(self) -> Iterator[SSHSession]:
        """Open one reusable SSH/SFTP session."""

        client = self.connect()
        sftp = client.open_sftp()

        try:
            yield SSHSession(client, sftp)
        finally:
                sftp.close()
                client.close()

    def upload(
        self,
        local_path: Path,
        remote_path: str,
    ) -> None:
        """Upload one local file through SFTP."""

        if not local_path.is_file():
            raise FileNotFoundError(
                f"Local upload file does not exist: {local_path}"
            )

        client = self.connect()

        try:
            sftp = client.open_sftp()

            try:
                sftp.put(
                    str(local_path),
                    remote_path,
                )
            finally:
                sftp.close()

        finally:
            client.close()

    def write_text(
        self,
        remote_path: str,
        content: str,
    ) -> None:
        """Write a UTF-8 text file remotely through SFTP."""

        client = self.connect()

        try:
            sftp = client.open_sftp()

            try:
                with sftp.file(remote_path, "w") as remote_file:
                    remote_file.write(content)
            finally:
                sftp.close()

        finally:
            client.close()

    def open_sftp(self) -> tuple[paramiko.SSHClient, paramiko.SFTPClient]:
        """Open an SSH connection and an SFTP session."""

        client = self.connect()
        sftp = client.open_sftp()
        return client, sftp
    
    def mkdir(self, remote_path: str) -> None:
        """Create a remote directory if it does not already exist."""

        self.run(f"mkdir -p {shlex.quote(remote_path)}")