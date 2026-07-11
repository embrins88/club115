class MinecraftServer:
    def __init__(self, ssh_client):
        self.ssh = ssh_client

    def status(self):
        return self.ssh.run("mc-status")

    def backup(self):
        return self.ssh.run("mc-backup")

    def restart(self):
        return self.ssh.run("mc-restart")