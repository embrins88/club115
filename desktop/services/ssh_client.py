import paramiko

class SSHClient:
    def __init__(self, host, user):
        self.host = host
        self.user = user

    def run(self, command):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(
                hostname=self.host,
                username=self.user,
                timeout=10
            )

            stdin, stdout, stderr = client.exec_command(command)
            out = stdout.read().decode(errors="replace").strip()
            err = stderr.read().decode(errors="replace").strip()

            return out, err

        finally:
            client.close()